from __future__ import annotations

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


class EnvironmentalClaim(BaseModel):
    """企業重大環境宣稱與主張"""
    claim_text: str = Field(description="環境宣稱原文或核心摘要")
    topic: str = Field(description="議題領域，如碳排放、再生能源、水資源、廢棄物等")
    scope: Optional[str] = Field(default=None, description="涵蓋範疇，如全集團、特定子公司、範疇一/二/三等")
    page: Optional[int] = Field(default=None, description="該宣稱所在的 PDF 實體頁碼")


class MaterialityScreeningOutput(BaseModel):
    """Step 1: 重大議題辨識與主要宣稱擷取結果"""
    company_name: str = Field(description="報告書揭露之企業名稱")
    report_year: Optional[str] = Field(default=None, description="報告所屬年度，如 2023 或 2024")
    material_topics: List[str] = Field(
        default_factory=list,
        description="該公司辨識出之重大環境議題清單（如溫室氣體減量、能源管理、水資源保護等）"
    )
    main_claims: List[EnvironmentalClaim] = Field(
        default_factory=list,
        description="報告書中 3-8 項最具代表性的主要環境宣稱、承諾或目標"
    )
    executive_summary: str = Field(
        default="",
        description="環境揭露總體印象與核心背景概述（100-200字）"
    )


class ItemScoreResult(BaseModel):
    """
    單一題項評分結果（依照 codebook.md 第二節與第六節標準輸出欄位）
    """
    item_code: str = Field(
        description="題項代碼，例如 CEG1, QEG2, TAG3, SDR4, VRG1, VAG2, LIR3 等"
    )
    item_name: Optional[str] = Field(
        default=None,
        description="題項名稱或簡要標題"
    )
    dimension: Optional[str] = Field(
        default=None,
        description="所屬構面代碼 (CEG, QEG, TAG, SDR, VRG, VAG, LIR)"
    )
    score: Optional[int] = Field(
        default=None,
        ge=0,
        le=4,
        description="評分 0-4 分；若無法合理判斷或資訊不足則填 null (代表 NA)"
    )
    confidence: Literal["High", "Medium", "Low"] = Field(
        default="Medium",
        description="評分信心水準：High (證據充足清晰) / Medium (有依據但有推論成分) / Low (證據微弱)"
    )
    materiality_status: Literal["Material", "Non-material", "Unclear"] = Field(
        default="Material",
        description="該題項涉及議題對公司之重大性狀態"
    )
    evidence_page: List[int] = Field(
        default_factory=list,
        description="支持評分的真實 PDF 實體頁碼列表（不可隨意編造，必須在 PDF 文本中可定位）"
    )
    evidence_quote: str = Field(
        description="支持評分的報告書原文摘錄（需包含足夠上下文以供人工審核驗證）"
    )
    counter_evidence_page: Optional[List[int]] = Field(
        default=None,
        description="與初步判斷相反的反向證據頁碼（如有）"
    )
    counter_evidence_quote: Optional[str] = Field(
        default=None,
        description="與初步判斷相反的反向證據原文摘錄（如有）"
    )
    reasoning_summary: str = Field(
        description="判定理由與評分依據說明（不超過 100-150 字）"
    )
    year_compare: Literal["Improved", "Stable", "Deteriorated", "NA"] = Field(
        default="NA",
        description="與前期或承諾比較趨勢：Improved (改善) / Stable (持平) / Deteriorated (惡化) / NA (無比較)"
    )
    missing_information: Optional[str] = Field(
        default=None,
        description="關鍵缺失資訊或未充分說明的缺口說明"
    )


class DimensionBatchScoreOutput(BaseModel):
    """
    單一構面批次評分輸出模型（用於 OpenAI Structured Outputs）
    """
    dimension_code: str = Field(description="構面代碼，例如 CEG, QEG, TAG, SDR, VRG, VAG, LIR")
    dimension_notes: Optional[str] = Field(default=None, description="該構面評估之整體備註或審核觀察")
    items: List[ItemScoreResult] = Field(description="該構面下 4 個題項的詳細評分結果")


class DimensionScore(BaseModel):
    """構面分數統計"""
    dimension_code: str = Field(description="構面代碼 (CEG, QEG, TAG, SDR, VRG, VAG, LIR)")
    dimension_name: str = Field(description="構面中文名稱")
    weight: float = Field(description="權重比例 (0.25, 0.15, 0.20 等)")
    valid_item_count: int = Field(description="有效計分題數 (0-4)")
    na_item_count: int = Field(description="NA 題數 (0-4)")
    raw_average: Optional[float] = Field(
        default=None,
        description="有效題項原始平均分 (0-4)，若全為 NA 則為 None"
    )
    weighted_score: Optional[float] = Field(
        default=None,
        description="加權得分，計算公式為 weight * (raw_average / 4) * 100"
    )
    reliability: Literal["High", "Medium", "Low"] = Field(
        default="High",
        description="依據手冊規定，有效題數少於 2 題標示為 Low Reliability"
    )


class QualityMetrics(BaseModel):
    """評分品質與覆蓋率統計指標"""
    valid_count: int = Field(description="有效評分題數 (滿分28)")
    na_count: int = Field(description="NA 題數 (滿分28)")
    na_ratio: float = Field(description="NA 佔比 (na_count / 28)")
    evidence_coverage_ratio: float = Field(
        description="證據覆蓋率：有引用原文與頁碼之有效題項比例 (0.0-1.0)"
    )
    high_confidence_count: int = Field(description="High 信心水準題數")
    counter_evidence_count: int = Field(description="具備反向證據之題數")
    year_compare_count: int = Field(description="具跨年度比較資訊之題數")
    overall_data_quality: Literal["High", "Medium", "Low"] = Field(
        description="總體資料品質等級"
    )


class AssessmentReport(BaseModel):
    """
    AI-GWRI 企業永續報告書漂綠風險總體評估報告
    """
    company_name: str = Field(description="受評企業名稱")
    report_year: Optional[str] = Field(default="未揭露", description="報告書所屬年份")
    evaluation_date: str = Field(description="評估執行時間")
    model_used: str = Field(description="執行評估之 LLM 模型名稱")
    materiality_summary: Optional[MaterialityScreeningOutput] = Field(
        default=None,
        description="重大議題與宣稱摘要"
    )
    item_results: List[ItemScoreResult] = Field(
        description="所有 28 題的詳細評估結果"
    )
    dimension_scores: Dict[str, DimensionScore] = Field(
        description="七大構面各自的分數與權重計算結果"
    )
    ai_gwri_score: float = Field(
        description="加權後 AI-GWRI 總體漂綠風險指數 (0-100)"
    )
    risk_level: str = Field(
        description="風險等級文字（如 無明顯風險、低度風險、中度風險、高度風險、極高風險）"
    )
    highest_risk_dimension: str = Field(
        description="風險最高的構面名稱與分數"
    )
    second_highest_risk_dimension: str = Field(
        description="風險次高的構面名稱與分數"
    )
    quality_metrics: QualityMetrics = Field(
        description="評分品質與數據指標"
    )
    disclaimer: str = Field(
        default="本分數代表永續報告書所呈現之漂綠風險（Greenwashing Risk），不等同於已確認之違法或欺瞞事件。",
        description="報告法定免責聲明"
    )
