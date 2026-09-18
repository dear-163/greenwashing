"""
PDF 解析與文字抽取模組
負責讀取 PDF 檔案（支援本機路徑或 Streamlit BytesIO 上傳），
嚴格保留實體 PDF 頁碼（1-indexed Page Number）作為 Metadata，
並提供針對企業永續報告書的章節關鍵字篩選與 Context Window 控管機制。
"""

import io
import re
from typing import List, Dict, Any, Union, Optional


class PDFParser:
    """永續報告書 PDF 專用解析器"""

    # 永續報告書核心關鍵字群組（用於重大性與環境章節篩選）
    KEYWORD_GROUPS = {
        "materiality": [
            "重大議題", "重大性", "實質性", "利害關係人", "矩陣", "GRI", "TCFD", "SASB", "報告邊界"
        ],
        "climate_energy": [
            "溫室氣體", "碳排放", "碳排", "減碳", "減量", "範疇一", "範疇二", "範疇三",
            "Scope 1", "Scope 2", "Scope 3", "淨零", "Net Zero", "碳中和", "SBTi",
            "能源", "節能", "再生能源", "綠電", "太陽能", "電力消耗", "用電強度"
        ],
        "environment_resources": [
            "水資源", "廢棄物", "循環經濟", "污染", "空氣污染", "廢水", "放流水",
            "化學品", "生物多樣性", "包材", "原物料"
        ],
        "compliance_negative": [
            "違規", "罰鍰", "裁罰", "事故", "訴訟", "申訴", "環境糾紛", "未達標", "落後"
        ],
        "targets_assurance": [
            "目標", "基準年", "里程碑", "查證", "驗證", "第三方", "確信", "保證",
            "查證聲明", "AA1000", "ISO 14064", "ISAE 3000", "有限確信", "合理確信"
        ]
    }

    def __init__(self):
        self.pages_data: List[Dict[str, Any]] = []

    def parse_pdf(
        self,
        file_source: Union[str, bytes, io.BytesIO],
        *args,
        progress_callback: Optional[Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        解析 PDF 檔案並回傳包含頁碼與文本的字典列表。
        優先採用高效能串流式 pypdf 引擎（速度快 20~50 倍，記憶體佔用極低），
        並支援即時進度回調，若遇到特殊編碼則自動 fallback 至 pdfplumber。
        
        Args:
            file_source: 檔案路徑 (str)、二進位數據 (bytes) 或 BytesIO 物件。
            progress_callback: 進度回調函式 callback(current_page, total_pages)
            
        Returns:
            List[Dict[str, Any]]: 格式為 [{"page": 1, "text": "...", "char_count": 120}, ...]
        """
        cb = progress_callback or kwargs.get("progress_callback")
        if cb is None and len(args) > 0:
            cb = args[0]
            
        self.pages_data = []
        
        if isinstance(file_source, bytes):
            file_obj = io.BytesIO(file_source)
        elif isinstance(file_source, io.BytesIO):
            file_obj = file_source
        else:
            file_obj = open(file_source, "rb")

        # 1. 優先使用高效能 pypdf 引擎（專為數百頁大型永續報告書優化，秒級完成）
        try:
            import pypdf
            file_obj.seek(0)
            reader = pypdf.PdfReader(file_obj)
            total_pages = len(reader.pages)
            
            for idx, page in enumerate(reader.pages):
                try:
                    raw_text = page.extract_text() or ""
                except Exception:
                    raw_text = ""
                cleaned_text = self._clean_text(raw_text)
                self.pages_data.append({
                    "page": idx + 1,  # 嚴格 1-indexed 實體頁碼
                    "text": cleaned_text,
                    "char_count": len(cleaned_text)
                })
                if cb and (idx % 3 == 0 or idx == total_pages - 1):
                    cb(idx + 1, total_pages)

            if any(p["char_count"] > 0 for p in self.pages_data):
                return self.pages_data
        except Exception:
            # 若 pypdf 失敗，自動嘗試 pdfplumber
            pass

        # 2. Fallback: 使用 pdfplumber
        try:
            import pdfplumber
            file_obj.seek(0)
            self.pages_data = []
            with pdfplumber.open(file_obj) as pdf:
                total_pages = len(pdf.pages)
                for idx, page in enumerate(pdf.pages):
                    raw_text = page.extract_text() or ""
                    cleaned_text = self._clean_text(raw_text)
                    self.pages_data.append({
                        "page": idx + 1,
                        "text": cleaned_text,
                        "char_count": len(cleaned_text)
                    })
                    if cb and (idx % 3 == 0 or idx == total_pages - 1):
                        cb(idx + 1, total_pages)
        except Exception as e:
            raise RuntimeError(f"PDF 解析失敗: {str(e)}")
        finally:
            if not isinstance(file_source, (bytes, io.BytesIO)):
                file_obj.close()

        return self.pages_data

    @staticmethod
    def _clean_text(text: str) -> str:
        """清洗提取文字中的冗餘空字符與異常符號，徹底移除 Unicode surrogates 避免 UTF-8 編碼失敗"""
        if not text:
            return ""
        # 1. 移除 Unicode surrogates (\ud800-\udfff)
        text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
        # 2. 移除非法控制字符但保留換行與空格
        cleaned = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f\ud800-\udfff]', '', text)
        # 3. 合併過度換行與空格
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        return cleaned.strip()

    def filter_relevant_pages(
        self,
        pages_data: Optional[List[Dict[str, Any]]] = None,
        max_pages: int = 40,
        focus_group: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        針對大型 PDF 報告進行關鍵頁面篩選與評分，優先保留最相關的環境揭露頁面。
        
        Args:
            pages_data: 待篩選頁面（若未傳入則使用 instance 內之 pages_data）
            max_pages: 最多保留頁數（預設 40 頁，避免超出 context window）
            focus_group: 特定聚焦關鍵字群組 (如 'materiality', 'climate_energy' 等)
            
        Returns:
            List[Dict[str, Any]]: 按頁碼排序之最相關頁面列表
        """
        source_pages = pages_data or self.pages_data
        if not source_pages:
            return []

        # 若總頁數本身不大於上限，全部保留
        if len(source_pages) <= max_pages:
            return source_pages

        scored_pages = []
        for p in source_pages:
            text = p["text"]
            score = 0
            if len(text.strip()) < 5:  # 忽略完全空白或僅有極少字符的頁面
                continue

            # 若在前 5 頁（通常為目錄、執行摘要、重大性矩陣），給予基礎保底權重
            if p["page"] <= 5:
                score += 3

            # 關鍵字加權計分
            if focus_group and focus_group in self.KEYWORD_GROUPS:
                target_kws = self.KEYWORD_GROUPS[focus_group]
                for kw in target_kws:
                    if kw in text:
                        score += 3
            else:
                for grp_name, kws in self.KEYWORD_GROUPS.items():
                    for kw in kws:
                        if kw in text:
                            # 負面事件與查證關鍵字權重更高
                            weight = 2 if grp_name in ["compliance_negative", "targets_assurance"] else 1
                            score += weight

            scored_pages.append((score, p))

        # 依分數排序，選取前 top N
        scored_pages.sort(key=lambda x: x[0], reverse=True)
        selected_pages = [p for score, p in scored_pages[:max_pages]]
        
        # 重新按照頁碼升序排列，確保語意連貫
        selected_pages.sort(key=lambda x: x["page"])
        return selected_pages

    @staticmethod
    def get_compact_context(
        pages: List[Dict[str, Any]],
        max_total_chars: int = 80000
    ) -> str:
        """
        將頁面陣列組合成附帶實體頁碼標註的 Context 字串供 LLM 使用。
        
        Format:
        === [PDF Page 12] ===
        文字內容...
        """
        context_parts = []
        total_chars = 0

        for p in pages:
            page_num = p["page"]
            text = p["text"]
            if not text.strip():
                continue
            
            section_header = f"\n=== [PDF Page {page_num}] ===\n"
            available = max_total_chars - total_chars - len(section_header)
            if available <= 200:
                break
            
            if len(text) > available:
                text = text[:available] + "\n...(本頁文字過長截斷)..."
                
            context_parts.append(section_header + text)
            total_chars += len(section_header) + len(text)

        return "".join(context_parts)
