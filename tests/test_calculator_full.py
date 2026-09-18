"""
AI-GWRI 數學公式與評分匯總完整單元測試
"""
import unittest

from models.schema import ItemScoreResult, MaterialityScreeningOutput, EnvironmentalClaim
from core.calculator import (
    calculate_dimension_scores,
    calculate_ai_gwri_score,
    determine_risk_level,
    calculate_quality_metrics,
    build_assessment_report
)
from core.scorer import MockAIGWRIScorer


class TestCalculatorFormulas(unittest.TestCase):
    def test_mock_sample_report(self):
        """驗證 Mock 評分器產出之報告數值與公式正確性"""
        report = MockAIGWRIScorer.generate_sample_report("測試科技股份有限公司", "2023")
        
        self.assertEqual(len(report.item_results), 28)
        self.assertEqual(len(report.dimension_scores), 7)
        self.assertGreaterEqual(report.ai_gwri_score, 0.0)
        self.assertLessEqual(report.ai_gwri_score, 100.0)
        
        # 驗證七大構面均存在
        for code in ["CEG", "QEG", "TAG", "SDR", "VRG", "VAG", "LIR"]:
            self.assertIn(code, report.dimension_scores)
            ds = report.dimension_scores[code]
            self.assertEqual(ds.valid_item_count + ds.na_item_count, 4)

        # 驗證品質指標
        self.assertEqual(report.quality_metrics.valid_count + report.quality_metrics.na_count, 28)
        self.assertGreater(report.quality_metrics.evidence_coverage_ratio, 0.0)

    def test_all_zeros_and_all_fours(self):
        """極端值驗證：全部 0 分應為 0.0，全部 4 分應為 100.0"""
        items_all_zero = []
        items_all_four = []
        for dim in ["CEG", "QEG", "TAG", "SDR", "VRG", "VAG", "LIR"]:
            for i in range(1, 5):
                code = f"{dim}{i}"
                items_all_zero.append(ItemScoreResult(
                    item_code=code,
                    score=0,
                    confidence="High",
                    materiality_status="Material",
                    evidence_page=[1],
                    evidence_quote="完美證據",
                    reasoning_summary="低風險",
                    year_compare="Stable"
                ))
                items_all_four.append(ItemScoreResult(
                    item_code=code,
                    score=4,
                    confidence="High",
                    materiality_status="Material",
                    evidence_page=[1],
                    evidence_quote="口號文字",
                    reasoning_summary="極高風險",
                    year_compare="Deteriorated"
                ))

        dim_scores_zero = calculate_dimension_scores(items_all_zero)
        score_zero = calculate_ai_gwri_score(dim_scores_zero)
        self.assertEqual(score_zero, 0.0)
        self.assertEqual(determine_risk_level(score_zero), "無明顯風險 (Minimal Risk)")

        dim_scores_four = calculate_dimension_scores(items_all_four)
        score_four = calculate_ai_gwri_score(dim_scores_four)
        self.assertEqual(score_four, 100.0)
        self.assertEqual(determine_risk_level(score_four), "極高風險 (Critical Risk)")

    def test_na_exclusion(self):
        """驗證 NA 題項不列入構面分母"""
        items = []
        for dim in ["CEG", "QEG", "TAG", "SDR", "VRG", "VAG", "LIR"]:
            for i in range(1, 5):
                code = f"{dim}{i}"
                # 假設 CEG1 為 2分，CEG2-4 為 NA
                if code == "CEG1":
                    score = 2
                elif dim == "CEG":
                    score = None  # NA
                else:
                    score = 0
                items.append(ItemScoreResult(
                    item_code=code,
                    score=score,
                    confidence="Medium",
                    materiality_status="Material",
                    evidence_page=[],
                    evidence_quote="",
                    reasoning_summary="test",
                    year_compare="NA"
                ))

        dim_scores = calculate_dimension_scores(items)
        # CEG 有效題數為 1，分數應為 2/1 = 2.0
        self.assertEqual(dim_scores["CEG"].valid_item_count, 1)
        self.assertEqual(dim_scores["CEG"].raw_average, 2.0)
        # 依手冊規定，有效題 < 2 標示為 Low Reliability
        self.assertEqual(dim_scores["CEG"].reliability, "Low")


if __name__ == "__main__":
    unittest.main()
