"""
AI-GWRI 數學公式計算與指標彙整模組
嚴格依照 codebook.md 第七節與第十節規範實作純 Python 運算，禁止依賴 LLM 心算。
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime

from models.schema import (
    ItemScoreResult,
    DimensionScore,
    QualityMetrics,
    AssessmentReport,
    MaterialityScreeningOutput,
)
from core.codebook_data import DIMENSIONS_META, CODEBOOK_ITEMS


def calculate_dimension_scores(
    items: List[ItemScoreResult]
) -> Dict[str, DimensionScore]:
    """
    計算七大構面各自的有效題項平均值、加權分數與可靠度。
    
    規則：
    1. 每一構面包含 4 個題項。
    2. NA 題 (score is None) 不納入分母。
    3. 若有效題數少於 2 題，標示為 Low Reliability。
    4. 加權分數 = weight * (raw_average / 4) * 100
    """
    # 依構面分組
    grouped_items: Dict[str, List[ItemScoreResult]] = {
        dim: [] for dim in DIMENSIONS_META.keys()
    }
    
    for item in items:
        dim = item.item_code[:3]
        if dim in grouped_items:
            grouped_items[dim].append(item)

    dimension_scores: Dict[str, DimensionScore] = {}

    for dim_code, meta in DIMENSIONS_META.items():
        dim_items = grouped_items.get(dim_code, [])
        valid_scores = [it.score for it in dim_items if it.score is not None]
        valid_count = len(valid_scores)
        na_count = len(dim_items) - valid_count
        weight = meta["weight"]

        if valid_count > 0:
            raw_avg = sum(valid_scores) / valid_count
            # 加權分數: weight * (raw_avg / 4) * 100
            weighted = weight * (raw_avg / 4.0) * 100.0
        else:
            raw_avg = None
            weighted = None

        # 可靠度判定
        if valid_count >= 3:
            reliability = "High"
        elif valid_count == 2:
            reliability = "Medium"
        else:
            reliability = "Low"

        dimension_scores[dim_code] = DimensionScore(
            dimension_code=dim_code,
            dimension_name=meta["name"],
            weight=weight,
            valid_item_count=valid_count,
            na_item_count=na_count,
            raw_average=round(raw_avg, 3) if raw_avg is not None else None,
            weighted_score=round(weighted, 2) if weighted is not None else None,
            reliability=reliability
        )

    return dimension_scores


def calculate_ai_gwri_score(
    dimension_scores: Dict[str, DimensionScore]
) -> float:
    """
    依據 codebook.md 第七節官方加權公式計算 AI-GWRI 總分 (0-100)：
    AI-GWRI = 25*(CEG/4) + 15*(QEG/4) + 15*(TAG/4) + 20*(SDR/4) + 10*(VRG/4) + 10*(VAG/4) + 5*(LIR/4)
    
    若有構面全部題項為 NA，將其餘有效構面的權重重新歸一化至 100% 進行加權。
    """
    total_active_weight = 0.0
    accumulated_score = 0.0

    for dim_code, dim_score in dimension_scores.items():
        if dim_score.raw_average is not None:
            # 公式權重 * (raw_average / 4) * 100
            accumulated_score += dim_score.weight * (dim_score.raw_average / 4.0) * 100.0
            total_active_weight += dim_score.weight

    if total_active_weight == 0.0:
        return 0.0

    # 若所有構面都有有效題，total_active_weight == 1.0
    if abs(total_active_weight - 1.0) < 1e-4:
        return round(accumulated_score, 2)
    else:
        # 重新歸一化
        normalized_score = accumulated_score / total_active_weight
        return round(normalized_score, 2)


def determine_risk_level(ai_gwri_score: float) -> str:
    """
    根據 AI-GWRI 總分 (0-100) 判定企業永續報告書漂綠風險等級
    """
    if ai_gwri_score < 20.0:
        return "無明顯風險 (Minimal Risk)"
    elif ai_gwri_score < 40.0:
        return "低度風險 (Low Risk)"
    elif ai_gwri_score < 60.0:
        return "中度風險 (Moderate Risk)"
    elif ai_gwri_score < 80.0:
        return "高度風險 (High Risk)"
    else:
        return "極高風險 (Critical Risk)"


def calculate_quality_metrics(items: List[ItemScoreResult]) -> QualityMetrics:
    """
    依據 codebook.md 第十節「評分品質檢查」計算品質與覆蓋率指標
    """
    total_items = len(items) if items else 28
    valid_scores = [it for it in items if it.score is not None]
    valid_count = len(valid_scores)
    na_count = total_items - valid_count
    na_ratio = round(na_count / total_items, 4) if total_items > 0 else 0.0

    # 證據覆蓋率：有效評分題項中，具有具體引文 (非空白) 與頁碼之比例
    evidenced_items = [
        it for it in valid_scores
        if it.evidence_quote and it.evidence_quote.strip() and it.evidence_page
    ]
    evidence_coverage = round(len(evidenced_items) / valid_count, 4) if valid_count > 0 else 0.0

    high_confidence_count = sum(1 for it in items if it.confidence == "High")
    counter_evidence_count = sum(
        1 for it in items
        if it.counter_evidence_quote and it.counter_evidence_quote.strip()
    )
    year_compare_count = sum(1 for it in items if it.year_compare != "NA")

    # 總體資料品質判定
    if na_ratio <= 0.25 and evidence_coverage >= 0.85 and high_confidence_count >= 16:
        overall_quality = "High"
    elif na_ratio <= 0.45 and evidence_coverage >= 0.65:
        overall_quality = "Medium"
    else:
        overall_quality = "Low"

    return QualityMetrics(
        valid_count=valid_count,
        na_count=na_count,
        na_ratio=na_ratio,
        evidence_coverage_ratio=evidence_coverage,
        high_confidence_count=high_confidence_count,
        counter_evidence_count=counter_evidence_count,
        year_compare_count=year_compare_count,
        overall_data_quality=overall_quality
    )


def find_top_risk_dimensions(
    dimension_scores: Dict[str, DimensionScore]
) -> Tuple[str, str]:
    """找出原始平均分數最高與次高的構面"""
    scored = [
        (ds.dimension_name, ds.raw_average if ds.raw_average is not None else -1.0)
        for ds in dimension_scores.values()
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    top_1 = f"{scored[0][0]} ({scored[0][1]:.2f} / 4.0)" if scored and scored[0][1] >= 0 else "無"
    top_2 = f"{scored[1][0]} ({scored[1][1]:.2f} / 4.0)" if len(scored) > 1 and scored[1][1] >= 0 else "無"
    return top_1, top_2


def build_assessment_report(
    company_name: str,
    report_year: Optional[str],
    model_used: str,
    item_results: List[ItemScoreResult],
    materiality_summary: Optional[MaterialityScreeningOutput] = None
) -> AssessmentReport:
    """彙整計算並產生完整 AssessmentReport 模型物件"""
    # 補充題項名稱與構面
    for item in item_results:
        meta = CODEBOOK_ITEMS.get(item.item_code, {})
        if not item.item_name and meta:
            item.item_name = meta.get("title", "")
        if not item.dimension:
            item.dimension = item.item_code[:3]

    dim_scores = calculate_dimension_scores(item_results)
    ai_gwri_score = calculate_ai_gwri_score(dim_scores)
    risk_level = determine_risk_level(ai_gwri_score)
    top1, top2 = find_top_risk_dimensions(dim_scores)
    quality = calculate_quality_metrics(item_results)

    return AssessmentReport(
        company_name=company_name or "未指定公司",
        report_year=report_year or "未指定年份",
        evaluation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        model_used=model_used,
        materiality_summary=materiality_summary,
        item_results=item_results,
        dimension_scores=dim_scores,
        ai_gwri_score=ai_gwri_score,
        risk_level=risk_level,
        highest_risk_dimension=top1,
        second_highest_risk_dimension=top2,
        quality_metrics=quality
    )
