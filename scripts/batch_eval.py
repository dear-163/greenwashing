"""
AI-GWRI 學術研究專用：大規模 Panel Data 批次評估腳本
支援掃描指定資料夾內的大量 PDF 永續報告書，
平行或循序評估後輸出符合 Stata / R / Python 實證分析規格的 Panel Dataset。
"""

import os
import sys
import glob
import json
import argparse
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

# 將專案根目錄加入路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pdf_parser import PDFParser
from core.scorer import AIGWRIScorer, MockAIGWRIScorer
from models.schema import AssessmentReport


def run_batch_assessment(
    input_dir: str,
    output_csv: str = "ai_gwri_panel_dataset.csv",
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    use_mock: bool = False,
    max_files: Optional[int] = None
) -> pd.DataFrame:
    """
    批次處理指定目錄下的所有 PDF 報告書並匯出 Panel Data
    """
    pdf_files = glob.glob(os.path.join(input_dir, "**", "*.pdf"), recursive=True)
    if not pdf_files:
        print(f"⚠️ 在 {input_dir} 未搜尋到任何 PDF 檔案。")
        return pd.DataFrame()

    if max_files:
        pdf_files = pdf_files[:max_files]

    print(f"📊 找到 {len(pdf_files)} 本報告書待評估...")
    parser = PDFParser()
    scorer = None if use_mock else AIGWRIScorer(api_key=api_key, model=model, pdf_parser=parser)

    panel_rows: List[Dict[str, Any]] = []

    for idx, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        print(f"\n[{idx}/{len(pdf_files)}] 正在處理: {filename}")

        try:
            # 解析 PDF
            pages = parser.parse_pdf(pdf_path)
            if not pages:
                print(f"  ❌ 跳過：無法解析 PDF 文本 ({filename})")
                continue

            # 嘗試從檔名推估公司名與年份（例如 2330_台積電_2023.pdf）
            clean_name = filename.replace(".pdf", "")
            tokens = clean_name.split("_")
            comp_hint = tokens[1] if len(tokens) > 1 else tokens[0]
            year_hint = tokens[2] if len(tokens) > 2 else (tokens[1] if len(tokens) > 1 and tokens[1].isdigit() else None)

            if use_mock:
                report = MockAIGWRIScorer.generate_sample_report(
                    company_name=comp_hint,
                    report_year=year_hint or "2023"
                )
            else:
                report = scorer.run_full_assessment(
                    pages_data=pages,
                    company_name_override=comp_hint,
                    report_year_override=year_hint,
                    progress_callback=lambda r, m: print(f"  進度 {int(r*100)}%: {m}", end="\r")
                )

            # 組裝 Panel Data 列資料
            row = {
                "company_name": report.company_name,
                "report_year": report.report_year,
                "source_file": filename,
                "ai_gwri_score": report.ai_gwri_score,
                "risk_level": report.risk_level,
                "highest_risk_dim": report.highest_risk_dimension,
                "second_highest_risk_dim": report.second_highest_risk_dimension,
                # 七大構面原始平均分 (0-4)
                "CEG_raw": report.dimension_scores["CEG"].raw_average,
                "QEG_raw": report.dimension_scores["QEG"].raw_average,
                "TAG_raw": report.dimension_scores["TAG"].raw_average,
                "SDR_raw": report.dimension_scores["SDR"].raw_average,
                "VRG_raw": report.dimension_scores["VRG"].raw_average,
                "VAG_raw": report.dimension_scores["VAG"].raw_average,
                "LIR_raw": report.dimension_scores["LIR"].raw_average,
                # 七大構面加權得分 (貢獻度)
                "CEG_weighted": report.dimension_scores["CEG"].weighted_score,
                "QEG_weighted": report.dimension_scores["QEG"].weighted_score,
                "TAG_weighted": report.dimension_scores["TAG"].weighted_score,
                "SDR_weighted": report.dimension_scores["SDR"].weighted_score,
                "VRG_weighted": report.dimension_scores["VRG"].weighted_score,
                "VAG_weighted": report.dimension_scores["VAG"].weighted_score,
                "LIR_weighted": report.dimension_scores["LIR"].weighted_score,
                # 信效度與品質指標
                "valid_count": report.quality_metrics.valid_count,
                "na_count": report.quality_metrics.na_count,
                "na_ratio": report.quality_metrics.na_ratio,
                "evidence_coverage": report.quality_metrics.evidence_coverage_ratio,
                "high_confidence_count": report.quality_metrics.high_confidence_count,
                "counter_evidence_count": report.quality_metrics.counter_evidence_count,
                "overall_data_quality": report.quality_metrics.overall_data_quality,
                "evaluated_at": report.evaluation_date,
                "model_used": report.model_used
            }

            # 展開所有 28 題原始得分 (CEG1 ~ LIR4)
            for it in report.item_results:
                row[f"{it.item_code}_score"] = it.score
                row[f"{it.item_code}_conf"] = it.confidence

            panel_rows.append(row)
            print(f"  ✅ 完成！AI-GWRI 總分: {report.ai_gwri_score:.2f} ({report.risk_level})")

        except Exception as e:
            print(f"  ❌ 處理異常 ({filename}): {str(e)}")

    if panel_rows:
        df_panel = pd.DataFrame(panel_rows)
        df_panel.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"\n🎉 批次評估完成！Panel Data 已成功匯出至: {output_csv} (共 {len(df_panel)} 筆觀測值)")
        return df_panel
    return pd.DataFrame()


if __name__ == "__main__":
    parser_cli = argparse.ArgumentParser(description="AI-GWRI 大規模報告書批次評估工具")
    parser_cli.add_argument("--input_dir", type=str, default="data/reports", help="存放 PDF 報告書之目錄路徑")
    parser_cli.add_argument("--output", type=str, default="ai_gwri_panel_dataset.csv", help="匯出 CSV 檔名")
    parser_cli.add_argument("--model", type=str, default="gpt-4o-mini", help="使用的 OpenAI 模型名稱")
    parser_cli.add_argument("--mock", action="store_true", help="使用示範仿真引擎 (無需 API Key 測試用)")
    parser_cli.add_argument("--max", type=int, default=None, help="最大評估檔案數量上限")
    args = parser_cli.parse_args()

    api_key_env = os.getenv("OPENAI_API_KEY")
    run_batch_assessment(
        input_dir=args.input_dir,
        output_csv=args.output,
        api_key=api_key_env,
        model=args.model,
        use_mock=args.mock,
        max_files=args.max
    )
