# AI-GWRI Streamlit App
import os
import io
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from models.schema import AssessmentReport, ItemScoreResult
from core.pdf_parser import PDFParser
from core.scorer import AIGWRIScorer, MockAIGWRIScorer
from core.codebook_data import DIMENSIONS_META, CODEBOOK_ITEMS
from utils.visualizer import (
    create_radar_chart,
    create_dimension_bar_chart,
    create_gauge_meter,
    create_item_distribution_chart
)

st.set_page_config(
    page_title="AI-GWRI 永續報告書漂綠風險評估系統",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.0rem; color: #475569; margin-bottom: 1.2rem; }
    .score-badge-0 { background-color: #DCFCE7; color: #15803D; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .score-badge-1 { background-color: #E0F2FE; color: #0369A1; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .score-badge-2 { background-color: #FEF3C7; color: #B45309; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .score-badge-3 { background-color: #FFEDD5; color: #C2410C; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .score-badge-4 { background-color: #FEE2E2; color: #B91C1C; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .score-badge-na { background-color: #F1F5F9; color: #64748B; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .quote-box { background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 10px 14px; margin: 6px 0; font-size: 0.92rem; color: #1E293B; }
    .counter-quote-box { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 10px 14px; margin: 6px 0; font-size: 0.92rem; color: #991B1B; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ 系統設定")

default_api_key = os.getenv("OPENAI_API_KEY", "")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    value=default_api_key,
    type="password",
    help="若未設定可於根目錄 .env 檔案中指定 OPENAI_API_KEY"
)

base_url = st.sidebar.text_input(
    "OpenAI Base URL (選填)",
    value=os.getenv("OPENAI_BASE_URL", ""),
    help="自訂 OpenAI 相容代理端點，例如 Azure 或第三方相容代理"
)

model_choice = st.sidebar.selectbox(
    "選擇評估模型",
    options=["gpt-4o-mini", "gpt-4o"],
    index=0,
    help="gpt-4o-mini: 快速且經濟；gpt-4o: 深度推理與長文稽核能力更強"
)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 報告書上傳")
uploaded_file = st.sidebar.file_uploader(
    "上傳企業永續報告書 (PDF)",
    type=["pdf"],
    help="支援一般企業 ESG / CSR / 永續報告書 PDF 檔案"
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ 快速功能")
if st.sidebar.button("🧪 載入示範報告書評估數據 (Demo)", use_container_width=True):
    st.session_state["assessment_report"] = MockAIGWRIScorer.generate_sample_report()
    st.sidebar.success("已載入示範企業評估報告！")

if "parsed_pages" not in st.session_state:
    st.session_state["parsed_pages"] = None
if "assessment_report" not in st.session_state:
    st.session_state["assessment_report"] = None

st.markdown('<div class="main-header">🌱 AI-GWRI 企業永續報告書漂綠風險自動評估系統</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基於 <i>AI-based Greenwashing Risk Index</i> (Codebook v1.0) 規範實作之證據導向 (Evidence-based) 28 題項全自動稽核系統</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    if (st.session_state["parsed_pages"] is None or 
        st.session_state.get("current_filename") != uploaded_file.name):
        
        with st.spinner(f"正在解析 PDF 報告書: {uploaded_file.name} (保留真實實體頁碼中...)"):
            try:
                parser = PDFParser()
                pages = parser.parse_pdf(file_bytes)
                st.session_state["parsed_pages"] = pages
                st.session_state["current_filename"] = uploaded_file.name
                st.session_state["pdf_parser_instance"] = parser
                st.success(f"✅ 成功解析 {len(pages)} 頁 PDF 實體頁面，總字元數: {sum(p['char_count'] for p in pages):,}")
            except Exception as e:
                st.error(f"❌ PDF 解析失敗: {str(e)}")

col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
with col_info1:
    if st.session_state["parsed_pages"]:
        total_p = len(st.session_state["parsed_pages"])
        total_c = sum(p["char_count"] for p in st.session_state["parsed_pages"])
        cur_f = st.session_state.get("current_filename", "PDF文件")
        st.info(f"📂 **已載入報告**: `{cur_f}` | 實體總頁數: **{total_p} 頁** | 總文字量: **{total_c:,} 字**")
    else:
        st.info("💡 請在左側上傳 PDF 格式的企業永續報告書，或點擊左側「載入示範報告書評估數據 (Demo)」進行快速體驗。")

with col_info2:
    company_name_input = st.text_input("受評企業名稱 (選填)", placeholder="系統可自動辨識")
with col_info3:
    report_year_input = st.text_input("報告所屬年份 (選填)", placeholder="系統可自動辨識")

start_col1, start_col2 = st.columns([1, 4])
with start_col1:
    start_eval = st.button(
        "🚀 開始 AI-GWRI 評估",
        type="primary",
        disabled=(st.session_state["parsed_pages"] is None),
        use_container_width=True
    )

if start_eval:
    if not api_key:
        st.error("⚠️ 請在左側側邊欄輸入有效的 OpenAI API Key！")
    else:
        progress_bar = st.progress(0.0)
        status_box = st.status("正在啟動 AI-GWRI 評估流程...", expanded=True)

        def update_progress(ratio: float, msg: str):
            progress_bar.progress(ratio)
            status_box.write(f"[{int(ratio*100)}%] {msg}")

        try:
            scorer = AIGWRIScorer(
                api_key=api_key,
                base_url=base_url if base_url.strip() else None,
                model=model_choice,
                pdf_parser=st.session_state.get("pdf_parser_instance", PDFParser())
            )

            report = scorer.run_full_assessment(
                pages_data=st.session_state["parsed_pages"],
                company_name_override=company_name_input.strip() or None,
                report_year_override=report_year_input.strip() or None,
                progress_callback=update_progress
            )
            
            st.session_state["assessment_report"] = report
            status_box.update(label="🎉 AI-GWRI 評估圓滿完成！", state="complete", expanded=False)
            st.rerun()

        except Exception as e:
            status_box.update(label=f"❌ 評估過程中斷: {str(e)}", state="error", expanded=True)
            st.exception(e)

report: AssessmentReport = st.session_state.get("assessment_report")

if report:
    st.markdown("---")
    
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.subheader(f"📊 評估報告：{report.company_name} ({report.report_year} 年度)")
        st.caption(f"評估時間: {report.evaluation_date} | 評估核心模型: `{report.model_used}`")
    with h_col2:
        st.caption("法定免責聲明")
        st.caption(f"<small>{report.disclaimer}</small>", unsafe_allow_html=True)

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    with kpi_col1:
        st.metric(
            label="AI-GWRI 總分",
            value=f"{report.ai_gwri_score:.1f} / 100",
            help="依七大構面官方權重公式純 Python 計算之漂綠風險指數 (分數愈高風險愈高)"
        )
    with kpi_col2:
        r_level = report.risk_level
        st.metric(label="漂綠風險等級", value=r_level.split(" ")[0])
    with kpi_col3:
        st.metric(
            label="有效評分題數",
            value=f"{report.quality_metrics.valid_count} / 28",
            delta=f"NA: {report.quality_metrics.na_count} 題",
            delta_color="off"
        )
    with kpi_col4:
        cov_pct = report.quality_metrics.evidence_coverage_ratio * 100
        st.metric(
            label="證據覆蓋率",
            value=f"{cov_pct:.1f}%",
            help="有效題項中同時包含實體頁碼與原文引述之比例"
        )
    with kpi_col5:
        st.metric(
            label="最高風險構面",
            value=report.highest_risk_dimension.split(" ")[0],
            help=report.highest_risk_dimension
        )
    with kpi_col6:
        st.metric(
            label="總體資料品質",
            value=report.quality_metrics.overall_data_quality,
            help="綜合考量 NA 比率、證據覆蓋率與 High-confidence 評定"
        )

    st.markdown("### 📈 構面風險與圖表分析")
    v_tab1, v_tab2, v_tab3 = st.tabs([
        "🕸️ 七大構面風險雷達圖 (Radar Chart)",
        "📊 原始得分 vs 加權貢獻長條圖 (Dimension Scores)",
        "⏱️ 總分儀表盤與 28 題評分分佈 (Gauge & Distribution)"
    ])

    with v_tab1:
        col_r1, col_r2 = st.columns([3, 2])
        with col_r1:
            fig_radar = create_radar_chart(report.dimension_scores)
            st.plotly_chart(fig_radar, use_container_width=True)
        with col_r2:
            st.markdown("**七大構面評分摘要表 (0-4 分制)**")
            summary_data = []
            for d_code, ds in report.dimension_scores.items():
                summary_data.append({
                    "構面": d_code,
                    "名稱": ds.dimension_name.split(" ")[0],
                    "權重": f"{int(ds.weight*100)}%",
                    "原始平均": f"{ds.raw_average:.2f}" if ds.raw_average is not None else "NA",
                    "加權分": f"{ds.weighted_score:.1f}" if ds.weighted_score is not None else "-",
                    "可靠度": ds.reliability
                })
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            st.caption("註：依手冊規定，有效題數少於 2 題之構面自動標示為 Low Reliability。")

    with v_tab2:
        fig_bar = create_dimension_bar_chart(report.dimension_scores)
        st.plotly_chart(fig_bar, use_container_width=True)

    with v_tab3:
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            fig_gauge = create_gauge_meter(report.ai_gwri_score, report.risk_level)
            st.plotly_chart(fig_gauge, use_container_width=True)
        with g_col2:
            fig_dist = create_item_distribution_chart(report.item_results)
            st.plotly_chart(fig_dist, use_container_width=True)

    if report.materiality_summary:
        with st.expander("🔍 查看企業重大議題篩選與核心環境宣稱 (Materiality & Claims Summary)", expanded=False):
            m_s = report.materiality_summary
            st.markdown(f"**識別出之重大環境議題**: `{'、'.join(m_s.material_topics)}`")
            st.markdown(f"**環境揭露總體印象摘要**: {m_s.executive_summary}")
            st.markdown("**主要環境宣稱列表 (Claim Extraction)**:")
            claim_rows = []
            for c in m_s.main_claims:
                claim_rows.append({
                    "PDF 頁碼": f"p. {c.page}" if c.page else "未註記",
                    "議題範疇": c.topic,
                    "適用對象/邊界": c.scope or "全集團",
                    "主要環境宣稱原文 (Claim Text)": c.claim_text
                })
            if claim_rows:
                st.dataframe(pd.DataFrame(claim_rows), use_container_width=True, hide_index=True)

    st.markdown("### 📝 28 題項逐題審查明細 (Auditable Codebook Evidence Trail)")
    st.caption("依據手冊標準輸出格式，每題清楚保留給分依據、支持證據、反向證據、PDF 實體頁碼及缺失說明。")

    dim_tabs = st.tabs([
        f"{code} ({int(meta['weight']*100)}%)"
        for code, meta in DIMENSIONS_META.items()
    ])

    items_by_code = {it.item_code: it for it in report.item_results}

    for tab_idx, (dim_code, dim_meta) in enumerate(DIMENSIONS_META.items()):
        with dim_tabs[tab_idx]:
            st.markdown(f"#### {dim_meta['name']}")
            st.caption(f"核心概念: {dim_meta['description']} | 文獻基礎: {dim_meta['literature']}")
            
            dim_item_codes = [f"{dim_code}{i}" for i in range(1, 5)]
            for code in dim_item_codes:
                it = items_by_code.get(code)
                if not it:
                    continue

                if it.score is None:
                    badge_html = '<span class="score-badge-na">分數: NA (不可評)</span>'
                else:
                    badge_html = f'<span class="score-badge-{it.score}">風險得分: {it.score} 分</span>'

                conf_color = {"High": "green", "Medium": "orange", "Low": "red"}.get(it.confidence, "gray")
                expander_title = f"【{it.item_code}】 {it.item_name} —— 得分: {it.score if it.score is not None else 'NA'} | 信心: {it.confidence}"

                with st.expander(expander_title, expanded=False):
                    c_badge1, c_badge2, c_badge3, c_badge4 = st.columns([1.5, 1.2, 1.2, 1.5])
                    with c_badge1:
                        st.markdown(badge_html, unsafe_allow_html=True)
                    with c_badge2:
                        st.markdown(f"信心水準: **:{conf_color}[{it.confidence}]**")
                    with c_badge3:
                        st.markdown(f"重大性: **{it.materiality_status}**")
                    with c_badge4:
                        st.markdown(f"跨期趨勢: **{it.year_compare}**")

                    st.markdown("**📌 判定理由摘要 (Reasoning Summary)**:")
                    st.write(it.reasoning_summary)

                    ev_pages_str = ", ".join([f"第 {p} 頁" for p in it.evidence_page]) if it.evidence_page else "未標註"
                    st.markdown(f"**📄 支持證據 (PDF 實體頁碼: `{ev_pages_str}`)**: ")
                    st.markdown(f'<div class="quote-box">『{it.evidence_quote}』</div>', unsafe_allow_html=True)

                    if it.counter_evidence_quote and it.counter_evidence_quote.strip():
                        c_pages_str = ", ".join([f"第 {p} 頁" for p in (it.counter_evidence_page or [])]) if it.counter_evidence_page else "未標註"
                        st.markdown(f"**⚠️ 反向/矛盾證據 (PDF 實體頁碼: `{c_pages_str}`)**: ")
                        st.markdown(f'<div class="counter-quote-box">『{it.counter_evidence_quote}』</div>', unsafe_allow_html=True)

                    if it.missing_information and it.missing_information.strip():
                        st.markdown(f"**❓ 關鍵缺失資訊 (Missing Information)**: `{it.missing_information}`")

    st.markdown("---")
    st.markdown("### 💾 評估成果匯出與下載")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        report_json_str = report.model_dump_json(indent=2)
        st.download_button(
            label="📥 下載完整評估報告 (JSON 格式)",
            data=report_json_str,
            file_name=f"AI_GWRI_Report_{report.company_name}_{report.report_year}.json",
            mime="application/json",
            use_container_width=True
        )

    with exp_col2:
        csv_rows = []
        for it in report.item_results:
            csv_rows.append({
                "受評公司": report.company_name,
                "報告年度": report.report_year,
                "構面": it.dimension,
                "題項代碼": it.item_code,
                "題項名稱": it.item_name,
                "得分": it.score if it.score is not None else "NA",
                "信心水準": it.confidence,
                "重大性": it.materiality_status,
                "實體頁碼": ", ".join(map(str, it.evidence_page)),
                "支持引文": it.evidence_quote,
                "反向頁碼": ", ".join(map(str, it.counter_evidence_page or [])),
                "反向引文": it.counter_evidence_quote or "",
                "判定理由": it.reasoning_summary,
                "跨期趨勢": it.year_compare,
                "關鍵缺失資訊": it.missing_information or ""
            })
        df_csv = pd.DataFrame(csv_rows)
        csv_buffer = io.StringIO()
        df_csv.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 下載 28 題審查明細表 (CSV 格式 / Excel 可讀)",
            data=csv_buffer.getvalue(),
            file_name=f"AI_GWRI_Items_{report.company_name}_{report.report_year}.csv",
            mime="text/csv",
            use_container_width=True
        )
