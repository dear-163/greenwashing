"""
AI-GWRI LLM 自動評分核心流程模組
嚴格落實 codebook.md 第五節九大步驟：
1. Materiality screening: 辨識重大議題
2. Claim extraction: 抽取主要環境宣稱
3. Evidence matching: 搜尋具體行動、數據與驗證
4. Negative evidence search: 主動搜尋負面資訊與惡化 KPI
5. Cross-year comparison: 前期對照與趨勢
6. Item scoring: 28 題 rubric 判定 (0-4 或 NA)
7. Evidence audit: 保留實體頁碼、原文摘錄與反證
8. Dimension aggregation & 9. Weighted AI-GWRI: 串接 calculator 運算
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Callable

from models.schema import (
    MaterialityScreeningOutput,
    DimensionBatchScoreOutput,
    ItemScoreResult,
    AssessmentReport,
    EnvironmentalClaim,
)
from core.codebook_data import (
    DIMENSIONS_META,
    CODEBOOK_ITEMS,
    get_dimension_items,
    build_dimension_scoring_prompt,
)
from core.pdf_parser import PDFParser
from core.calculator import build_assessment_report

logger = logging.getLogger(__name__)


class AIGWRIScorer:
    """AI-GWRI 評估引擎"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        pdf_parser: Optional[PDFParser] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or None
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.pdf_parser = pdf_parser or PDFParser()
        self._client = None

    @property
    def client(self):
        """延遲初始化 OpenAI Client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("未設定 OpenAI API Key，請在 .env 或介面中輸入。")
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def step1_screen_materiality_and_claims(
        self,
        pages_data: List[Dict[str, Any]],
        max_context_chars: int = 40000
    ) -> MaterialityScreeningOutput:
        """
        Step 1 & 2: 辨識企業重大環境議題，並抽取 3-8 項最具代表性的環境宣稱與承諾。
        避免對非重大議題機械扣分，並為後續 28 題評分奠定 Claim 基礎。
        """
        # 優先挑選前 5 頁（目錄、摘要）及重大性與氣候相關頁面
        relevant_pages = self.pdf_parser.filter_relevant_pages(
            pages_data=pages_data,
            max_pages=20,
            focus_group="materiality"
        )
        context_text = self.pdf_parser.get_compact_context(
            relevant_pages, max_total_chars=max_context_chars
        )

        system_prompt = """你是一位精通 GRI、TCFD、SASB 準則與綠色洗白（Greenwashing）審計的資深 ESG 分析師。
你的任務是通讀永續報告書內容（已標註實體頁碼 [PDF Page X]），客觀完成兩項前置分析：
1. 辨識受評企業名稱、報告所屬年度、以及報告書中明列或涉及的「重大環境議題 (Material Environmental Topics)」。
2. 抽取 3-8 項核心的「重大環境宣稱與減量承諾 (Major Environmental Claims)」，記錄其原文、所屬議題、範疇與出現的實體頁碼。
3. 撰寫 100-200 字的環境揭露總體印象摘要。
請務必精準客觀，頁碼必須為文本中真實標註的 [PDF Page X] 數字。"""

        user_prompt = f"""請分析以下報告書文字內容，輸出結構化重大性與環境宣稱摘要：

{context_text}"""

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=MaterialityScreeningOutput,
                temperature=0.0
            )
            return response.choices[0].message.parsed
        except Exception as e:
            logger.warning(f"Step 1 Structured Outputs 呼叫異常，嘗試備援解析: {str(e)}")
            # 備援：JSON Mode 解析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n請以符合 MaterialityScreeningOutput 結構的 JSON 格式輸出。"},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            data = json.loads(response.choices[0].message.content)
            return MaterialityScreeningOutput.model_validate(data)

    def step2_score_single_dimension(
        self,
        dimension_code: str,
        pages_data: List[Dict[str, Any]],
        materiality_summary: Optional[MaterialityScreeningOutput] = None,
        max_context_chars: int = 60000
    ) -> DimensionBatchScoreOutput:
        """
        對單一構面（包含 4 個題項）進行嚴格 Rubric 評分。
        注入 codebook.md 的 0-4 分詳細判定邏輯、正反範例與 NA 規則。
        """
        dim_meta = DIMENSIONS_META.get(dimension_code, {})
        scoring_guide = build_dimension_scoring_prompt(dimension_code)

        # 針對不同構面調整頁面篩選策略
        focus_grp = None
        if dimension_code in ["CEG", "QEG"]:
            focus_grp = "climate_energy"
        elif dimension_code == "TAG":
            focus_grp = "targets_assurance"
        elif dimension_code == "SDR":
            focus_grp = "compliance_negative"
        elif dimension_code == "VRG":
            focus_grp = "targets_assurance"

        relevant_pages = self.pdf_parser.filter_relevant_pages(
            pages_data=pages_data,
            max_pages=30,
            focus_group=focus_grp
        )
        context_text = self.pdf_parser.get_compact_context(
            relevant_pages, max_total_chars=max_context_chars
        )

        materiality_info = ""
        if materiality_summary:
            claims_desc = "\n".join([
                f"- [Page {c.page or 'N/A'}] ({c.topic}) {c.claim_text}"
                for c in materiality_summary.main_claims
            ])
            materiality_info = f"""
受評企業背景：
- 公司名稱: {materiality_summary.company_name}
- 報告年度: {materiality_summary.report_year}
- 重大環境議題: {', '.join(materiality_summary.material_topics)}
- 報告主要環境宣稱 (Claim):
{claims_desc}
"""

        system_prompt = f"""你是一位嚴謹公正的永續報告書漂綠風險（Greenwashing Risk）資深稽核審查員。
你必須完全依照以下提供的 AI-GWRI Codebook 評分標準對 4 個題項進行獨立審核。

{scoring_guide}

【特別強調】：
1. 每一題的 evidence_page 必須為報告書內容中真實標註的 [PDF Page X] 數字，不可胡亂臆測！
2. evidence_quote 請摘錄報告書原文，保留必要上下文以供審核。
3. 嚴格遵守 0-4 分與 NA 原則：0 分表示「有完整可信證據」，若缺乏資訊或非重大議題，請設為 null (NA)。
4. 請務必評審該構面下的所有 4 個題項。
"""

        user_prompt = f"""{materiality_info}

以下為該報告書篩選之重點章節頁面內容（已標註實體頁碼）：
{context_text}

請針對構面【{dimension_code}】完成 4 個題項的評分與證據擷取："""

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=DimensionBatchScoreOutput,
                temperature=0.0
            )
            result = response.choices[0].message.parsed
            return self._validate_and_sanitize_dimension_output(result, dimension_code)
        except Exception as e:
            logger.warning(f"構面 {dimension_code} Structured Outputs 異常: {str(e)}，切換備援解析")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n請以符合 DimensionBatchScoreOutput 的 JSON 結構回傳。"},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            data = json.loads(response.choices[0].message.content)
            result = DimensionBatchScoreOutput.model_validate(data)
            return self._validate_and_sanitize_dimension_output(result, dimension_code)

    def _validate_and_sanitize_dimension_output(
        self,
        output: DimensionBatchScoreOutput,
        dimension_code: str
    ) -> DimensionBatchScoreOutput:
        """驗證與補齊構面下可能缺失的題項"""
        expected_items = get_dimension_items(dimension_code)
        output_items_dict = {item.item_code: item for item in output.items}
        
        sanitized_items: List[ItemScoreResult] = []
        for exp in expected_items:
            code = exp["code"]
            if code in output_items_dict:
                item = output_items_dict[code]
                item.item_name = exp["title"]
                item.dimension = dimension_code
                sanitized_items.append(item)
            else:
                # 補上 NA 預設項
                sanitized_items.append(ItemScoreResult(
                    item_code=code,
                    item_name=exp["title"],
                    dimension=dimension_code,
                    score=None,
                    confidence="Low",
                    materiality_status="Unclear",
                    evidence_page=[],
                    evidence_quote="報告書中無充分資訊可供評估",
                    reasoning_summary="未檢索到足夠實質內容，依規範評為 NA",
                    year_compare="NA",
                    missing_information="未揭露相關資訊"
                ))
        
        output.items = sanitized_items
        return output

    def run_full_assessment(
        self,
        pages_data: List[Dict[str, Any]],
        company_name_override: Optional[str] = None,
        report_year_override: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> AssessmentReport:
        """
        執行完整的端到端 AI-GWRI 評估流程：
        - 步驟 0: 進度初使化 (5%)
        - 步驟 1: 重大議題與宣稱前置抽取 (15%)
        - 步驟 2-8: 七大構面循序評分 (各佔 10-12%，累計至 95%)
        - 步驟 9: 數學公式計算與指標彙總 (100%)
        """
        if not pages_data:
            raise ValueError("傳入的 PDF 頁面資料為空，無法進行評估。")

        if progress_callback:
            progress_callback(0.05, "開始解析報告書重大性議題與核心環境宣稱 (Step 1)...")

        # Step 1: Materiality & Claims
        materiality = self.step1_screen_materiality_and_claims(pages_data)
        comp_name = company_name_override or materiality.company_name or "受評企業"
        rep_year = report_year_override or materiality.report_year or "未揭露"

        all_item_results: List[ItemScoreResult] = []
        dim_keys = list(DIMENSIONS_META.keys())
        total_dims = len(dim_keys)

        for idx, dim_code in enumerate(dim_keys):
            dim_meta = DIMENSIONS_META[dim_code]
            dim_progress = 0.15 + (idx / total_dims) * 0.75
            
            if progress_callback:
                progress_callback(
                    dim_progress,
                    f"正在評估構面 [{dim_code}] {dim_meta['name']} (第 {idx+1}/{total_dims} 個構面)..."
                )

            dim_output = self.step2_score_single_dimension(
                dimension_code=dim_code,
                pages_data=pages_data,
                materiality_summary=materiality
            )
            all_item_results.extend(dim_output.items)

        if progress_callback:
            progress_callback(0.95, "正在執行純 Python 數學公式加權計算與信效度品質檢驗 (Step 9)...")

        # Step 9: 數學計算與總指標彙整
        report = build_assessment_report(
            company_name=comp_name,
            report_year=rep_year,
            model_used=self.model,
            item_results=all_item_results,
            materiality_summary=materiality
        )

        if progress_callback:
            progress_callback(1.0, "AI-GWRI 評估完成！正在呈現分析總結看板。")

        return report


class MockAIGWRIScorer:
    """
    示範與離線測試用 Mock 評分器
    可產生符合 codebook.md 標準規格之 28 題仿真數據與計算結果，
    供系統展示、無 API Key 測試或快速 UI 驗證使用。
    """

    @staticmethod
    def generate_sample_report(company_name: str = "創研永續科技股份有限公司", report_year: str = "2023") -> AssessmentReport:
        from models.schema import MaterialityScreeningOutput, EnvironmentalClaim
        
        materiality = MaterialityScreeningOutput(
            company_name=company_name,
            report_year=report_year,
            material_topics=["氣候變遷與溫室氣體減量", "能源轉型與綠能採購", "循環經濟與水資源管理"],
            main_claims=[
                EnvironmentalClaim(
                    claim_text="承諾於 2030 年達成全集團溫室氣體範疇一與範疇二減量 42%，2050 達成淨零碳排。",
                    topic="氣候變遷",
                    scope="全集團全球營運據點",
                    page=14
                ),
                EnvironmentalClaim(
                    claim_text="2025 年台灣廠區全面導入高效率冰水主機與空壓節能系統，節省電力 1,500 萬度。",
                    topic="節能改善",
                    scope="台灣 3 座主要廠區",
                    page=28
                ),
                EnvironmentalClaim(
                    claim_text="積極擴大再生能源採用，本年度綠電轉供佔比達 18.5%。",
                    topic="再生能源",
                    scope="台灣營運據點",
                    page=33
                ),
                EnvironmentalClaim(
                    claim_text="製程水回收率持續提升，目標達到 85% 之國際標竿水準。",
                    topic="水資源",
                    scope="核心生產據點",
                    page=47
                )
            ],
            executive_summary="受評企業在溫室氣體盤查與節能專案方面揭露較為詳盡，具備第三方有限確信查證；但在長期目標里程碑、範疇三碳排放母數以及部分質性宣稱上存在若干量化與因果說明落差。"
        )

        mock_raw_data = [
            # CEG
            ("CEG1", 1, "High", "Material", [28, 29], "2023年投資新台幣1.2億元完成3座廠區空壓與照明汰換，節電620萬度。", [32], "部分低碳研發宣稱僅提及進行中，無明確投資額。", "主要節能專案具備完整資本支出與專案名稱支持，少數研發宣稱較抽象，評為 1 分。", "Improved", "研發專案效益之預期完成時程"),
            ("CEG2", 2, "Medium", "Material", [30], "報告提及全廠能源效率提升4.2%，並列舉部分馬達更換。", [35], "電力總消耗仍上升1.8%，與效率提升之關係未充分分解。", "部分改善措施與總耗電數據存在抵消，因果分解不夠充分，評為 2 分。", "Stable", "產量變動對總能耗之影響因素分析"),
            ("CEG3", 1, "High", "Material", [12, 14, 28], "永續願景頁面雖有願景承諾，但在環境章節提供多項工程措施與資本支出清單。", None, None, "象徵性宣示與實質行動比例尚稱平衡，實質專案描述充分。", "Improved", None),
            ("CEG4", 2, "Medium", "Material", [33], "宣稱推動綠色辦公節能，但所附圖表為生產廠區電力強度下降。", [34], "辦公室獨立用電數據未單獨列出。", "成果數據之範疇與宣稱主體略有不對稱，評為 2 分。", "Stable", "綠色辦公之獨立節電成效數據"),
            # QEG
            ("QEG1", 0, "High", "Material", [22, 23], "完整列出 2021-2023 年範疇一、二排放量（公噸 CO2e）及營收碳強度。", None, None, "主要環境宣稱均附有完整絕對量與強度數據，無量化落差。", "Stable", None),
            ("QEG2", 1, "High", "Material", [14], "以 2020 年為基準年（排放量 184,200 tCO2e），目標減量 42%。", [15], "水資源目標未明確定義基準年。", "溫室氣體有明確基準年與基準量，水資源指標缺少基準數值，評為 1 分。", "Stable", "水資源基準年之絕對耗水量"),
            ("QEG3", 0, "High", "Material", [22, 45, 48], "連續 3 年 (2021-2023) 之用電、用水、溫室氣體與廢棄物數據可比表格。", None, None, "核心環境 KPI 均提供三年以上連續歷史數據，口徑一致。", "Stable", None),
            ("QEG4", 2, "Medium", "Material", [24], "註記溫室氣體範疇一二涵蓋母公司及主要子公司（營收佔比 91%）。", [25], "範疇三僅揭露類別 1 採購商品，且未明確計算方法與母數。", "範疇一二邊界清晰，但範疇三覆蓋率與計算分母嚴重模糊，評為 2 分。", "Stable", "範疇三完整類別盤查與邊界說明"),
            # TAG
            ("TAG1", 0, "High", "Material", [14], "設定 2030 年減碳 42%、2050 年淨零碳排，期限明確。", None, None, "重大環境目標均具備具體 Target Year。", "Stable", None),
            ("TAG2", 2, "Medium", "Material", [15], "2030 目標缺乏 2025、2027 年中間里程碑路徑規劃。", [16], "僅有一張總體路徑圖，無具體年段指標分攤。", "長期目標未有效拆解為短中期查核點，評為 2 分。", "Stable", "2025 年中期減量階段目標值"),
            ("TAG3", 1, "High", "Material", [16], "2022 年承諾之太陽能自發自用建置 2MW，2023 年進度已完成 1.4MW (70%)。", None, None, "當年度有主動追蹤前期承諾進度，落後部分亦有說明。", "Improved", None),
            ("TAG4", 1, "Medium", "Material", [48], "水回收率 82% 略低於年度目標 85%，說明係因擴建新產線調校延宕所致。", None, None, "未達標項目坦誠揭露並提供合理解釋與後續補強策略。", "Stable", None),
            # SDR
            ("SDR1", 2, "High", "Material", [8, 49], "報告書前言與各篇章大標題聚焦綠能與節水成就，製程廢棄物產量增加 6.8% 僅以小表格呈現。", [50], "廢棄物表格中有標註代碼與總量，但未做任何篇幅說明。", "正面成果在視覺與篇幅上明顯突出，負面變動弱化於附表，評為 2 分。", "Deteriorated", "廢棄物增加之深入檢討與對應方案"),
            ("SDR2", 3, "Medium", "Material", [50], "有害事業廢棄物較前一年度增加 14.5%，內文未見任何成因解釋與改善措施。", [51], "僅於統計總表出現數值變動。", "重大負面環境指標顯著惡化卻未提供原因分析，選擇性弱化，評為 3 分。", "Deteriorated", "有害廢棄物激增之製程成因與防制措施"),
            ("SDR3", 1, "High", "Material", [22, 23, 47, 50], "已揭露 Scope 1, Scope 2、水、能耗、廢棄物，但缺乏 Scope 3 與空污 SOx/NOx 具體數據。", None, None, "主要核心指標揭露尚齊全，僅次要空污指標存在小缺口，評為 1 分。", "Stable", "固定污染源 SOx / NOx 排放量"),
            ("SDR4", 1, "Medium", "Material", [29], "以竹科 A 廠榮獲綠建築標章宣示綠色製造，後續內文有標註全集團各廠之綠建築比例。", None, None, "雖有示範廠案例，但有標註母數與整體比例，未造成嚴重誤導。", "Stable", None),
            # VRG
            ("VRG1", 0, "High", "Material", [72], "溫室氣體盤查 (ISO 14064-1:2018) 由台灣檢驗科技 (SGS) 完成第三方查證並附聲明書。", None, None, "重大核心溫室氣體數據具備合格獨立第三方查證。", "Stable", None),
            ("VRG2", 1, "High", "Material", [73], "SGS 查證聲明書明確標註涵蓋範疇一與範疇二，保證等級為有限確信 (Limited Assurance)。", None, None, "查證範圍與確信等級清楚，但未包含範疇三與水資源數據。", "Stable", "其他環境 KPI 之確信範圍擴充"),
            ("VRG3", 1, "High", "Material", [25], "詳細註明溫室氣體 GWP 採用 IPCC 第六次評估報告，電力係數採用經濟部能源署最新公佈值。", None, None, "計算方法與排放係數來源透明完整。", "Stable", None),
            ("VRG4", 0, "High", "Material", [68, 70], "報告附錄附有 GRI 準則對照表與 SASB 指標索引，頁碼與項目對應清晰可追溯。", None, None, "環境數據具備極佳的索引可追溯性。", "Stable", None),
            # VAG
            ("VAG1", 1, "High", "Material", [11, 28], "雖使用『低碳供應鏈』等詞彙，但在供應商章節具體定義要求前 50 大供應商完成碳盤查。", None, None, "願景詞彙多有後續具體措施界定，空泛性較低。", "Improved", None),
            ("VAG2", 2, "Medium", "Material", [37], "『積極推動綠色產品研發、持續深化循環包材』等宣示，未設定明確 KPI 或研發佔比。", [38], "包材減塑成效未能量化說明。", "具有方向性之承諾缺乏量化衡量指標支持，評為 2 分。", "Stable", "綠色包材減量比重或定量指標"),
            ("VAG3", 1, "Medium", "Material", [42], "提及產品具備節能效益，並附有第三方能效標章認證證書。", None, None, "效益詞有標章認證支撐，可信度尚可。", "Stable", None),
            ("VAG4", 1, "High", "Material", [14, 28], "減碳目標與節能專案均清楚標示適用廠區（台灣營運中心）與實施年度。", None, None, "關鍵宣稱人事實地時間邊界清晰。", "Stable", None),
            # LIR
            ("LIR1", 1, "Medium", "Material", [6, 12], "董事長致詞偏向正向樂觀，但環境績效章節敘事客觀中立，未過度渲染。", None, None, "語氣與實際揭露績效大致匹配，無顯著浮誇宣傳。", "Stable", None),
            ("LIR2", 2, "Medium", "Material", [51], "在說明廢棄物增量時，使用『因應製程多元化調校致使衍生性暫存物質結構重組』等高度迂迴術語。", [52], "語句複雜度顯著提高，弱化廢棄物管理責任。", "負面議題附近出現顯著語言複雜化與被動語態，評為 2 分。", "Deteriorated", "以直白語言坦誠說明廢棄物激增真相"),
            ("LIR3", 1, "High", "Material", [18], "政策承諾沿用部分標準模板，但各章節專案與數據均為當年度最新資訊更新。", None, None, "模板套話比例正常，具備實質年報更新內容。", "Stable", None),
            ("LIR4", 1, "High", "Material", [8, 51], "正面報導雖豐富，但負面廢棄物資訊仍有獨立篇幅與表格揭露，未達嚴重轉移焦點程度。", None, None, "無故意透過過量正面行銷壓制重大環境爭議之情事。", "Stable", None),
        ]

        item_results = []
        for code, score, conf, mat, ev_p, ev_q, c_p, c_q, r_sum, y_c, m_i in mock_raw_data:
            item_results.append(ItemScoreResult(
                item_code=code,
                item_name=CODEBOOK_ITEMS[code]["title"],
                dimension=code[:3],
                score=score,
                confidence=conf,
                materiality_status=mat,
                evidence_page=ev_p,
                evidence_quote=ev_q,
                counter_evidence_page=c_p,
                counter_evidence_quote=c_q,
                reasoning_summary=r_sum,
                year_compare=y_c,
                missing_information=m_i
            ))

        return build_assessment_report(
            company_name=company_name,
            report_year=report_year,
            model_used="gpt-4o-mini (示範仿真引擎)",
            item_results=item_results,
            materiality_summary=materiality
        )
