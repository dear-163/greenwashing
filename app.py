"""
AI-GWRI 企業永續報告書漂綠風險自動評估系統 (Streamlit 前端主程式)
風格：Forensic ESG Greenwashing Audit (深色數位鑑識・反漂綠主題風格)
"""

import os
import sys
import io
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 確保專案根目錄在 sys.path 首位，避免 Linux/Streamlit Cloud 套件命名衝突
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

load_dotenv()

from models.schema import AssessmentReport, ItemScoreResult
from core.pdf_parser import PDFParser
from core.scorer import AIGWRIScorer
from core.codebook_data import DIMENSIONS_META, CODEBOOK_ITEMS
from visualization.visualizer import (
    create_radar_chart,
    create_dimension_bar_chart,
    create_gauge_meter,
    create_item_distribution_chart
)

def render_plotly_chart(fig):
    """跨版本相容 Plotly 圖表渲染 (消除 Streamlit 1.64+ use_container_width 警示)"""
    import inspect
    sig = inspect.signature(st.plotly_chart).parameters
    if "width" in sig:
        st.plotly_chart(fig, width="stretch")
    else:
        st.plotly_chart(fig, use_container_width=True)

def full_width_kw():
    """跨版本相容元件寬度參數"""
    import inspect
    sig = inspect.signature(st.button).parameters
    if "width" in sig:
        return {"width": "stretch"}
    return {"use_container_width": True}

# 頁面配置
st.set_page_config(
    page_title="AI-GWRI 漂綠風險數位鑑識系統",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂高質感反漂綠 (Greenwashing Forensic) 深色主題樣式
st.markdown("""
<style>
    /* 全域字體與背景 */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Noto+Sans+TC:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    /* 頂部英雄區塊 Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #042014 0%, #0B3824 45%, #0F172A 100%);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(4, 32, 20, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        top: -50px;
        right: -50px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, rgba(0,0,0,0) 70%);
        pointer-events: none;
    }
    .hero-tag {
        display: inline-block;
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid rgba(52, 211, 153, 0.4);
        color: #34D399;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 1px;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-title span {
        background: linear-gradient(90deg, #34D399, #10B981, #6EE7B7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 6px;
    }
    
    /* 統計看板卡片 Metric Card */
    .metric-card {
        background: linear-gradient(145deg, #111E17 0%, #0C1510 100%);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(52, 211, 153, 0.5);
    }
    
    /* 分數專用發光徽章 */
    .badge-score-0 { background: #064E3B; color: #6EE7B7; border: 1px solid #10B981; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
    .badge-score-1 { background: #0C4A6E; color: #7DD3FC; border: 1px solid #38BDF8; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
    .badge-score-2 { background: #78350F; color: #FDE68A; border: 1px solid #F59E0B; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
    .badge-score-3 { background: #7C2D12; color: #FDBA74; border: 1px solid #F97316; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
    .badge-score-4 { background: #7F1D1D; color: #FCA5A5; border: 1px solid #EF4444; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }
    .badge-score-na { background: #1E293B; color: #94A3B8; border: 1px solid #475569; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }

    /* 鑑識引文區塊 */
    .evidence-box {
        background: rgba(6, 78, 59, 0.22);
        border-left: 4px solid #10B981;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        color: #D1FAE5;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .counter-box {
        background: rgba(127, 29, 29, 0.22);
        border-left: 4px solid #EF4444;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        color: #FEE2E2;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .missing-box {
        background: rgba(120, 53, 15, 0.22);
        border-left: 4px solid #F59E0B;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 8px 0;
        color: #FEF3C7;
        font-size: 0.9rem;
    }
    
    .page-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .page-pill-red {
        display: inline-block;
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 側邊欄設定 -----------------
st.sidebar.markdown("### 🌿 **AI-GWRI 系統控制台**")

default_api_key = os.getenv("OPENAI_API_KEY", "")
api_key = st.sidebar.text_input(
    "API Key (OpenAI / Google Gemini)",
    value=default_api_key,
    type="password",
    help="支援 OpenAI Key (以 sk- 開頭) 或 Google Gemini Key (以 AIzaSy 開頭)"
)

is_gemini = api_key.strip().startswith("AIzaSy")
if is_gemini:
    st.sidebar.success("✨ 已偵測為 Google Gemini Key，自動路由至 Gemini 端點！")

ALL_MODELS = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gpt-4o-mini", "gpt-4o"]
default_idx = 0 if is_gemini else 3

base_url = st.sidebar.text_input(
    "API Base URL (選填)",
    value="https://generativelanguage.googleapis.com/v1beta/openai/" if is_gemini else os.getenv("OPENAI_BASE_URL", ""),
    help="自訂相容代理端點（輸入 Gemini Key 時自動路由）"
)

model_choice = st.sidebar.selectbox(
    "選擇評估稽核模型",
    options=ALL_MODELS,
    index=default_idx,
    help="模型：Google (gemini-2.5-flash) 或 OpenAI (gpt-4o-mini, gpt-4o)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📂 **報告書上傳**")
uploaded_file = st.sidebar.file_uploader(
    "上傳企業永續報告書 (PDF)",
    type=["pdf"],
    help="支援企業 ESG / CSR / 永續報告書 PDF 檔案（最大支援 200MB）"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **系統指引**：上傳報告書並輸入 API Key 後，即可點擊主畫面綠色按鈕開始鑑識審查。")

# 狀態初始化
if "parsed_pages" not in st.session_state:
    st.session_state["parsed_pages"] = None
if "assessment_report" not in st.session_state:
    st.session_state["assessment_report"] = None

# ----------------- 主畫面 Hero Banner -----------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-tag">FORENSIC ESG AUDITING • EVIDENCE-BASED ENGINE</div>
    <h1 class="hero-title">🌱 AI-GWRI <span>企業永續報告書漂綠風險</span> 鑑識系統</h1>
    <p class="hero-subtitle">基於 <i>AI-based Greenwashing Risk Index</i> (Codebook v1.0) 規範實作之證據導向 28 題項全自動稽核引擎</p>
</div>
""", unsafe_allow_html=True)

# ----------------- PDF 解析區 -----------------
if uploaded_file is not None:
    if (st.session_state["parsed_pages"] is None or 
        st.session_state.get("current_filename") != uploaded_file.name):
        
        file_bytes = uploaded_file.getvalue()
        parse_status = st.status(f"⚡ 正在極速解析 PDF 報告書: {uploaded_file.name}...", expanded=True)
        parse_bar = parse_status.progress(0.0)

        def on_parse_progress(curr, total):
            ratio = min(curr / total, 1.0) if total else 1.0
            parse_bar.progress(ratio)
            parse_status.write(f"📄 正在抽取實體頁碼與內文: 第 {curr} / {total} 頁 ({int(ratio*100)}%)...")

        try:
            parser = PDFParser()
            try:
                pages = parser.parse_pdf(file_bytes, progress_callback=on_parse_progress)
            except TypeError:
                pages = parser.parse_pdf(file_bytes)
            st.session_state["parsed_pages"] = pages
            st.session_state["current_filename"] = uploaded_file.name
            st.session_state["pdf_parser_instance"] = parser
            total_chars = sum(p["char_count"] for p in pages)
            parse_status.update(
                label=f"✅ 成功完成 {len(pages)} 頁 PDF 實體頁面極速解析（總文字量: {total_chars:,} 字）！",
                state="complete",
                expanded=False
            )
        except Exception as e:
            parse_status.update(label=f"❌ PDF 解析失敗: {str(e)}", state="error", expanded=True)
            st.error(f"❌ PDF 解析失敗: {str(e)}")

col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
with col_info1:
    if st.session_state["parsed_pages"]:
        total_p = len(st.session_state["parsed_pages"])
        total_c = sum(p["char_count"] for p in st.session_state["parsed_pages"])
        cur_f = st.session_state.get("current_filename", "PDF文件")
        st.info(f"📂 **已載入報告**: `{cur_f}` | 實體總頁數: **{total_p} 頁** | 總文字量: **{total_c:,} 字**")
    else:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px dashed rgba(52, 211, 153, 0.4); border-radius: 10px; padding: 14px 18px; color: #94A3B8;">
            💡 <b>使用說明</b>：請於左側控制台輸入 API Key 並上傳企業永續報告書 (PDF)，確認載入後點擊下方 <b>「🚀 開始 AI-GWRI 評估」</b> 啟動鑑識稽核。
        </div>
        """, unsafe_allow_html=True)

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
        **full_width_kw()
    )

if start_eval:
    if not api_key:
        st.error("⚠️ 請在左側側邊欄輸入有效的 API Key（支援 OpenAI sk-... 或 Google Gemini AIzaSy...）！")
    else:
        progress_bar = st.progress(0.0)
        status_box = st.status("正在啟動 AI-GWRI 鑑識流程...", expanded=True)

        def update_progress(ratio: float, msg: str):
            progress_bar.progress(ratio)
            status_box.write(f"[{int(ratio*100)}%] {msg}")

        try:
            effective_model = model_choice
            if is_gemini and "gemini" not in model_choice.lower():
                effective_model = "gemini-2.5-flash"

            scorer = AIGWRIScorer(
                api_key=api_key,
                base_url=base_url.strip() if base_url.strip() else None,
                model=effective_model,
                pdf_parser=st.session_state.get("pdf_parser_instance", PDFParser())
            )

            report = scorer.run_full_assessment(
                pages_data=st.session_state["parsed_pages"],
                company_name_override=company_name_input.strip() or None,
                report_year_override=report_year_input.strip() or None,
                progress_callback=update_progress
            )
            
            st.session_state["assessment_report"] = report
            status_box.update(label="🎉 AI-GWRI 鑑識評估圓滿完成！", state="complete", expanded=False)
            st.rerun()

        except Exception as e:
            status_box.update(label=f"❌ 評估過程中斷: {str(e)}", state="error", expanded=True)
            st.exception(e)

# ----------------- 報告結果呈現區 -----------------
report: AssessmentReport = st.session_state.get("assessment_report")

if report:
    st.markdown("---")
    try:
        # 頂部報告標頭
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown(f"### 📊 漂綠鑑識報告：`{report.company_name}` ({report.report_year} 年度)")
            st.caption(f"評估時間: {report.evaluation_date} | 鑑識引擎: `{report.model_used}`")
        with h_col2:
            st.caption("學術免責聲明")
            st.caption(f"<small>{report.disclaimer}</small>", unsafe_allow_html=True)

        # 1. 總結看板 (KPI Cards)
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
                label="可評估題項",
                value=f"{report.quality_metrics.evaluated_items_count} / 28",
                delta=f"NA: {report.quality_metrics.na_items_count} 題",
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
                label="資料品質評等",
                value=report.quality_metrics.overall_data_quality,
                help="綜合考量 NA 比率、證據覆蓋率與 High-confidence 評定"
            )

        # 2. 視覺化分析區塊
        st.markdown("### 📈 構面風險與視覺化圖表")
        v_tab1, v_tab2, v_tab3 = st.tabs([
            "🕸️ 七大構面風險雷達圖 (Radar Chart)",
            "📊 原始得分 vs 加權貢獻長條圖 (Dimension Scores)",
            "⏱️ 總分儀表盤與 28 題評分分佈 (Gauge & Distribution)"
        ])

        with v_tab1:
            col_r1, col_r2 = st.columns([3, 2])
            with col_r1:
                fig_radar = create_radar_chart(report.dimension_scores)
                render_plotly_chart(fig_radar)
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
                st.dataframe(df_summary, hide_index=True, **full_width_kw())
                st.caption("註：依手冊規定，有效題數少於 2 題之構面自動標示為 Low Reliability。")

        with v_tab2:
            fig_bar = create_dimension_bar_chart(report.dimension_scores)
            render_plotly_chart(fig_bar)

        with v_tab3:
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_gauge = create_gauge_meter(report.ai_gwri_score, report.risk_level)
                render_plotly_chart(fig_gauge)
            with g_col2:
                fig_dist = create_item_distribution_chart(report.item_results)
                render_plotly_chart(fig_dist)

        # 3. 重大議題與宣稱前置矩陣 (Step 1 成果)
        if report.materiality_summary:
            with st.expander("🔍 查看企業重大議題篩選與核心環境宣稱 (Materiality & Claims Matrix)", expanded=False):
                m_s = report.materiality_summary
                st.markdown(f"**識別出之重大環境議題**: `{'`、`'.join(m_s.material_topics)}`")
                st.markdown(f"**環境揭露總體印象摘要**: {m_s.executive_summary}")
                st.markdown("**主要環境宣稱列表 (Claim Extraction)**:")
                claim_rows = []
                for c in m_s.main_claims:
                    claim_rows.append({
                        "PDF 實體頁碼": f"p. {c.page}" if c.page else "未註記",
                        "議題範疇": c.topic,
                        "涵蓋對象/邊界": c.scope or "全集團",
                        "主要環境宣稱原文 (Claim Text)": c.claim_text
                    })
                if claim_rows:
                    st.dataframe(pd.DataFrame(claim_rows), hide_index=True, **full_width_kw())

        # 4. 28 題詳細審核列表 (Auditable Item Trail)
        st.markdown("### 📝 28 題項逐題鑑識審查明細 (Auditable Codebook Evidence Trail)")
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
                        badge_html = '<span class="badge-score-na">判定: NA (不可評)</span>'
                    else:
                        badge_html = f'<span class="badge-score-{it.score}">漂綠風險分: {it.score} 分</span>'

                    conf_color = {"High": "#34D399", "Medium": "#FBBF24", "Low": "#F87171"}.get(it.confidence, "#94A3B8")
                    score_str = f"{it.score} 分" if it.score is not None else "NA"
                    expander_title = f"【{it.item_code}】 {it.item_name} —— 得分: {score_str} | 信心: {it.confidence}"

                    with st.expander(expander_title, expanded=False):
                        c_badge1, c_badge2, c_badge3, c_badge4 = st.columns([1.5, 1.2, 1.2, 1.5])
                        with c_badge1:
                            st.markdown(badge_html, unsafe_allow_html=True)
                        with c_badge2:
                            st.markdown(f"信心水準: <b style='color:{conf_color};'>{it.confidence}</b>", unsafe_allow_html=True)
                        with c_badge3:
                            st.markdown(f"重大性: <b>{it.materiality_status}</b>", unsafe_allow_html=True)
                        with c_badge4:
                            st.markdown(f"跨期趨勢: <b>{it.year_compare}</b>", unsafe_allow_html=True)

                        st.markdown("**📌 判定理由說明 (Reasoning Summary)**:")
                        st.write(it.reasoning_summary)

                        # 支持證據
                        ev_p = it.evidence_page or []
                        ev_pill = " ".join([f"<span class='page-pill'>第 {p} 頁</span>" for p in ev_p]) if ev_p else "<span class='page-pill'>未標註</span>"
                        st.markdown(f"**📄 支持證據 (PDF 實體頁碼: {ev_pill})**: ", unsafe_allow_html=True)
                        st.markdown(f'<div class="evidence-box">『{it.evidence_quote}』</div>', unsafe_allow_html=True)

                        # 反向證據
                        if it.counter_evidence_quote and it.counter_evidence_quote.strip():
                            c_p = it.counter_evidence_page or []
                            c_pill = " ".join([f"<span class='page-pill-red'>第 {p} 頁</span>" for p in c_p]) if c_p else "<span class='page-pill-red'>未標註</span>"
                            st.markdown(f"**⚠️ 矛盾/反向證據 (PDF 實體頁碼: {c_pill})**: ", unsafe_allow_html=True)
                            st.markdown(f'<div class="counter-box">『{it.counter_evidence_quote}』</div>', unsafe_allow_html=True)

                        # 缺失資訊
                        if it.missing_information and it.missing_information.strip():
                            st.markdown(f"**❓ 關鍵缺失資訊 (Missing Information)**: `{it.missing_information}`")

        # 5. 資料匯出區塊
        st.markdown("---")
        st.markdown("### 💾 鑑識成果匯出與下載")
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            report_json_str = report.model_dump_json(indent=2)
            st.download_button(
                label="📥 下載完整鑑識報告 (JSON 格式)",
                data=report_json_str,
                file_name=f"AI_GWRI_Report_{report.company_name}_{report.report_year}.json",
                mime="application/json",
                **full_width_kw()
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
                label="📥 下載 28 題審查明細表 (CSV 格式 / Stata/R/Excel 可讀)",
                data=csv_buffer.getvalue(),
                file_name=f"AI_GWRI_Items_{report.company_name}_{report.report_year}.csv",
                mime="text/csv",
                **full_width_kw()
            )
    except Exception as render_err:
        st.error(f"⚠️ 報告畫面渲染異常: {str(render_err)}")
