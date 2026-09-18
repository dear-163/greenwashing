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
from utils.visualizer import create_radar_chart, create_dimension_bar_chart, create_gauge_meter

class TestAI_GWRI_Full(unittest.TestCase):
    def test_sample_report_generation(self):
        report = MockAIGWRIScorer.generate_sample_report('台塑石化', '2023')
        self.assertEqual(len(report.item_results), 28)
        self.assertEqual(len(report.dimension_scores), 7)
        self.assertGreater(report.ai_gwri_score, 0.0)
        self.assertLess(report.ai_gwri_score, 100.0)
        
        # Verify visualizers run without error
        fig_radar = create_radar_chart(report.dimension_scores)
        self.assertIsNotNone(fig_radar)
        
        fig_bar = create_dimension_bar_chart(report.dimension_scores)
        self.assertIsNotNone(fig_bar)
        
        fig_gauge = create_gauge_meter(report.ai_gwri_score, report.risk_level)
        self.assertIsNotNone(fig_gauge)

    def test_perfect_and_worst_scores(self):
        zeros = [ItemScoreResult(
            item_code=f'{d}{i}', score=0, confidence='High', materiality_status='Material',
            evidence_page=[1], evidence_quote='完整數據', reasoning_summary='無風險', year_compare='Stable'
        ) for d in ['CEG', 'QEG', 'TAG', 'SDR', 'VRG', 'VAG', 'LIR'] for i in range(1, 5)]
        
        dim_z = calculate_dimension_scores(zeros)
        score_z = calculate_ai_gwri_score(dim_z)
        self.assertEqual(score_z, 0.0)
        self.assertEqual(determine_risk_level(score_z), '無明顯風險 (Minimal Risk)')

        fours = [ItemScoreResult(
            item_code=f'{d}{i}', score=4, confidence='High', materiality_status='Material',
            evidence_page=[1], evidence_quote='口號', reasoning_summary='極高風險', year_compare='Deteriorated'
        ) for d in ['CEG', 'QEG', 'TAG', 'SDR', 'VRG', 'VAG', 'LIR'] for i in range(1, 5)]
        
        dim_f = calculate_dimension_scores(fours)
        score_f = calculate_ai_gwri_score(dim_f)
        self.assertEqual(score_f, 100.0)
        self.assertEqual(determine_risk_level(score_f), '極高風險 (Critical Risk)')

    def test_na_handling(self):
        items = []
        for d in ['CEG', 'QEG', 'TAG', 'SDR', 'VRG', 'VAG', 'LIR']:
            for i in range(1, 5):
                code = f'{d}{i}'
                score = 2 if code == 'CEG1' else (None if d == 'CEG' else 1)
                items.append(ItemScoreResult(
                    item_code=code, score=score, confidence='Medium', materiality_status='Material',
                    evidence_page=[1], evidence_quote='Q', reasoning_summary='R', year_compare='NA'
                ))
        dims = calculate_dimension_scores(items)
        self.assertEqual(dims['CEG'].valid_item_count, 1)
        self.assertEqual(dims['CEG'].raw_average, 2.0)
        self.assertEqual(dims['CEG'].reliability, 'Low')

if __name__ == '__main__':
    unittest.main()
