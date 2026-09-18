"""
AI-GWRI 核心邏輯單元測試（包含 Codebook 結構與純數學公式驗證）
"""
import unittest

from core.codebook_data import DIMENSIONS_META, CODEBOOK_ITEMS, get_dimension_items, build_dimension_scoring_prompt
from core.pdf_parser import PDFParser


class TestCodebookData(unittest.TestCase):
    def test_dimensions_integrity(self):
        """驗證 7 大構面與權重總和為 100%"""
        self.assertEqual(len(DIMENSIONS_META), 7)
        expected_dims = ["CEG", "QEG", "TAG", "SDR", "VRG", "VAG", "LIR"]
        for d in expected_dims:
            self.assertIn(d, DIMENSIONS_META)

        total_weight = sum(d["weight"] for d in DIMENSIONS_META.values())
        self.assertAlmostEqual(total_weight, 1.0, places=4)
        
        # 驗證手冊指定權重
        self.assertEqual(DIMENSIONS_META["CEG"]["weight"], 0.25)
        self.assertEqual(DIMENSIONS_META["QEG"]["weight"], 0.15)
        self.assertEqual(DIMENSIONS_META["TAG"]["weight"], 0.15)
        self.assertEqual(DIMENSIONS_META["SDR"]["weight"], 0.20)
        self.assertEqual(DIMENSIONS_META["VRG"]["weight"], 0.10)
        self.assertEqual(DIMENSIONS_META["VAG"]["weight"], 0.10)
        self.assertEqual(DIMENSIONS_META["LIR"]["weight"], 0.05)

    def test_all_28_items_exist(self):
        """驗證 28 題項完整性與每個構面包含 4 題"""
        self.assertEqual(len(CODEBOOK_ITEMS), 28)
        for dim_code in DIMENSIONS_META:
            items = get_dimension_items(dim_code)
            self.assertEqual(len(items), 4, f"構面 {dim_code} 題數應為 4")
            for it in items:
                self.assertTrue(it["code"].startswith(dim_code))
                self.assertTrue(len(it["title"]) > 0)
                self.assertTrue(len(it["definition"]) > 0)
                self.assertEqual(len(it["rubric"]), 5, f"題項 {it['code']} 應有 0-4 分評分標準")

    def test_prompt_builder(self):
        """驗證 Prompt 建構器內容"""
        prompt = build_dimension_scoring_prompt("CEG")
        self.assertIn("CEG1", prompt)
        self.assertIn("CEG2", prompt)
        self.assertIn("CEG3", prompt)
        self.assertIn("CEG4", prompt)
        self.assertIn("0分 (無明顯風險)", prompt)
        self.assertIn("Strict Guidelines", prompt)


class TestPDFParser(unittest.TestCase):
    def test_clean_text(self):
        """驗證文本清洗與非法控制字元移除"""
        raw = "Hello\x00World\n\n\n\nTest   Spaces"
        cleaned = PDFParser._clean_text(raw)
        self.assertEqual(cleaned, "HelloWorld\n\nTest Spaces")

    def test_filter_relevant_pages(self):
        """驗證關鍵字頁面評分與篩選機制"""
        parser = PDFParser()
        sample_pages = [
            {"page": 1, "text": "目錄與企業簡介", "char_count": 50},
            {"page": 2, "text": "重大議題評估矩陣與 GRI 準則對照", "char_count": 200},
            {"page": 3, "text": "董事長致詞與企業願景", "char_count": 100},
            {"page": 4, "text": "溫室氣體盤查 Scope 1 Scope 2 碳排放量與減碳目標", "char_count": 300},
            {"page": 5, "text": "一般人事薪酬規範", "char_count": 80},
        ]
        filtered = parser.filter_relevant_pages(sample_pages, max_pages=3)
        self.assertEqual(len(filtered), 3)
        # 應包含頁碼 2 或 4 等高相關頁面
        filtered_pages = [p["page"] for p in filtered]
        self.assertIn(4, filtered_pages)

    def test_get_compact_context(self):
        """驗證實體頁碼標註上下文輸出"""
        sample_pages = [
            {"page": 12, "text": "再生能源建置 5MW", "char_count": 20},
            {"page": 15, "text": "有害廢棄物處理說明", "char_count": 20}
        ]
        ctx = PDFParser.get_compact_context(sample_pages)
        self.assertIn("=== [PDF Page 12] ===", ctx)
        self.assertIn("再生能源建置 5MW", ctx)
        self.assertIn("=== [PDF Page 15] ===", ctx)


if __name__ == "__main__":
    unittest.main()
