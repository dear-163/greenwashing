"""
AI-GWRI 企業永續報告書漂綠風險自動評估系統 (Streamlit 前端主程式)
風格：Forensic ESG Greenwashing Audit (深色數位鑑識・反漂綠主題風格)
"""

import os
import sys
import io
import json
import base64
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

from PIL import Image

logo_path = os.path.join(current_dir, "assets", "logo.png")
logo_img = None
logo_b64 = ""
if os.path.exists(logo_path):
    try:
        logo_img = Image.open(logo_path)
    except Exception:
        pass
    with open(logo_path, "rb") as _f:
        logo_b64 = base64.b64encode(_f.read()).decode("utf-8")

# 自動修補 Streamlit 底層 static 目錄 (覆蓋預設 favicon/apple-touch-icon)
def _ensure_streamlit_static_patched():
    try:
        import shutil
        st_static_dir = os.path.join(os.path.dirname(st.__file__), "static")
        if os.path.exists(st_static_dir) and os.path.exists(logo_path):
            for fname in ["favicon.png", "favicon.ico", "apple-touch-icon.png", "apple-touch-icon-precomposed.png", "logo.png"]:
                dest = os.path.join(st_static_dir, fname)
                shutil.copyfile(logo_path, dest)
            index_path = os.path.join(st_static_dir, "index.html")
            if os.path.exists(index_path):
                with open(index_path, "r", encoding="utf-8") as _inf:
                    idx_html = _inf.read()
                if "apple-touch-icon.png" not in idx_html:
                    injection = '''<link rel="apple-touch-icon" sizes="180x180" href="./apple-touch-icon.png" />
    <link rel="apple-touch-icon-precomposed" sizes="180x180" href="./apple-touch-icon-precomposed.png" />
    <link rel="icon" type="image/png" sizes="192x192" href="./apple-touch-icon.png" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-title" content="AI-GWRI" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    <title>AI-GWRI 企業永續漂綠風險評估系統</title>'''
                    idx_html = idx_html.replace("<title>Streamlit</title>", injection)
                    with open(index_path, "w", encoding="utf-8") as _outf:
                        _outf.write(idx_html)
    except Exception:
        pass

_ensure_streamlit_static_patched()

# 頁面配置
st.set_page_config(
    page_title="AI-GWRI 漂綠風險數位鑑識系統",
    page_icon=logo_img if logo_img is not None else "🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 Apple Touch Icon、PWA 與瀏覽器快捷圖標支援（手機加到主畫面專用）
if logo_b64:
    # 注入靜態標籤與前端動態穿透指令
    st.markdown(f"""
    <link rel="apple-touch-icon" sizes="180x180" href="app/static/apple-touch-icon.png">
    <link rel="apple-touch-icon-precomposed" sizes="180x180" href="app/static/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="192x192" href="app/static/logo.png">
    <link rel="icon" type="image/png" sizes="32x32" href="app/static/favicon.png">
    <link rel="manifest" href="app/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="AI-GWRI">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <script>
        (function() {{
            function updateIcons(doc) {{
                if (!doc || !doc.head) return;
                
                // 移除任何舊的皇冠圖示
                const oldIcons = doc.querySelectorAll("link[rel*='icon'], link[rel*='apple-touch-icon']");
                oldIcons.forEach(el => el.remove());

                const iconUri = "data:image/png;base64,{logo_b64}";

                const appleIcon = doc.createElement('link');
                appleIcon.rel = 'apple-touch-icon';
                appleIcon.sizes = '180x180';
                appleIcon.href = iconUri;
                doc.head.appendChild(appleIcon);

                const appleIconPre = doc.createElement('link');
                appleIconPre.rel = 'apple-touch-icon-precomposed';
                appleIconPre.sizes = '180x180';
                appleIconPre.href = iconUri;
                doc.head.appendChild(appleIconPre);

                const favIcon = doc.createElement('link');
                favIcon.rel = 'shortcut icon';
                favIcon.type = 'image/png';
                favIcon.href = iconUri;
                doc.head.appendChild(favIcon);

                const metaTitle = doc.createElement('meta');
                metaTitle.name = 'apple-mobile-web-app-title';
                metaTitle.content = 'AI-GWRI';
                doc.head.appendChild(metaTitle);
            }}

            try {{
                // 針對當前文檔
                updateIcons(document);
                // 針對外層 Streamlit 宿主文檔 (穿透 iframe)
                if (window.parent && window.parent.document) {{
                    updateIcons(window.parent.document);
                }}
                if (window.top && window.top.document) {{
                    updateIcons(window.top.document);
                }}
            }} catch(e) {{
                console.log("Icon update:", e);
            }}
        }})();
    </script>
    """, unsafe_allow_html=True)

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

    /* Streamlit KPI Metric 數值精緻自適應防爆版 */
    div[data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
        white-space: pre-line !important;
        word-break: break-word !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #94A3B8 !important;
        white-space: nowrap !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(52, 211, 153, 0.25) !important;
        border-radius: 10px !important;
        padding: 8px 10px !important;
        min-height: 90px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 側邊欄設定 -----------------
if os.path.exists(logo_path):
    s_col1, s_col2 = st.sidebar.columns([1, 3.2])
    with s_col1:
        st.image(logo_path, width=54)
    with s_col2:
        st.markdown("<div style='padding-top: 6px; font-weight: 700; font-size: 1.15rem; color: #F8FAFC;'>AI-GWRI<br><span style='font-size: 0.75rem; color: #34D399; font-weight: 500;'>漂綠風險數位鑑識</span></div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("### 🌿 **AI-GWRI 系統控制台**")
st.sidebar.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

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

ALL_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gpt-4o-mini",
    "gpt-4o"
]
default_idx = 0 if is_gemini else 6

base_url = st.sidebar.text_input(
    "API Base URL (選填)",
    value="https://generativelanguage.googleapis.com/v1beta/openai/" if is_gemini else os.getenv("OPENAI_BASE_URL", ""),
    help="自訂相容代理端點（輸入 Gemini Key 時自動路由）"
)

model_choice = st.sidebar.selectbox(
    "選擇評估稽核模型",
    options=ALL_MODELS,
    index=default_idx,
    help="推薦：gemini-3.1-flash-lite (每日 500 次高額度、15 RPM)，亦可選 3.7-flash 或 OpenAI"
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
logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width: 52px; height: 52px; border-radius: 12px; margin-right: 14px; vertical-align: middle; box-shadow: 0 4px 16px rgba(0,0,0,0.4);">' if logo_b64 else '🌱 '

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-tag">FORENSIC ESG AUDITING • EVIDENCE-BASED ENGINE</div>
    <h1 class="hero-title" style="display: flex; align-items: center; flex-wrap: wrap;">
        {logo_img_tag}
        <span>AI-GWRI 企業永續報告書漂綠風險鑑識系統</span>
    </h1>
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
                effective_model = "gemini-3.1-flash-lite"

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

        # 1. 總結看板 (專業金融鑑識自適應卡片，徹底杜絕文字擠壓被截斷)
        v_cnt = getattr(report.quality_metrics, 'valid_count', getattr(report.quality_metrics, 'evaluated_items_count', 28))
        n_cnt = getattr(report.quality_metrics, 'na_count', getattr(report.quality_metrics, 'na_items_count', 0))
        cov_pct = report.quality_metrics.evidence_coverage_ratio * 100
        r_level = report.risk_level.split(" ")[0]
        q_val = report.quality_metrics.overall_data_quality

        # 解析最高風險構面之代碼、全稱與原始平均分數
        dim_raw = report.highest_risk_dimension or "無"
        top_dim_code = "無"
        top_dim_name = "各構面均衡"
        top_dim_score_str = ""

        # 從 dimension_scores 中找出真正的最高分構面
        if report.dimension_scores:
            scored_sorted = sorted(
                [(ds.dimension_code, ds.dimension_name, ds.raw_average or 0.0) for ds in report.dimension_scores.values()],
                key=lambda x: x[2],
                reverse=True
            )
            if scored_sorted and scored_sorted[0][2] > 0:
                top_dim_code = scored_sorted[0][0]
                top_dim_name = scored_sorted[0][1].split(" ")[0]
                top_dim_score_str = f"{scored_sorted[0][2]:.2f} / 4.0"

        # 風險等級顏色映射
        risk_color_map = {
            "無明顯風險": "#34D399",
            "低度風險": "#38BDF8",
            "中度風險": "#FBBF24",
            "高度風險": "#F97316",
            "極高風險": "#EF4444"
        }
        r_color = risk_color_map.get(r_level, "#34D399")

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin-bottom: 24px;">
            <div class="metric-card">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-bottom: 6px;">AI-GWRI 漂綠總分</div>
                <div style="font-size: 1.85rem; font-weight: 800; color: #F8FAFC; line-height: 1.1;">
                    {report.ai_gwri_score:.1f}
                    <span style="font-size: 0.85rem; color: #64748B; font-weight: 500;">/ 100</span>
                </div>
                <div style="font-size: 0.72rem; color: #10B981; margin-top: 5px;">純公式加權計算</div>
            </div>
            <div class="metric-card">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-bottom: 6px;">漂綠風險等級</div>
                <div style="font-size: 1.35rem; font-weight: 800; color: {r_color}; line-height: 1.2;">
                    {r_level}
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 5px;">五級風險矩陣評定</div>
            </div>
            <div class="metric-card">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-bottom: 6px;">最高風險構面</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #F87171; line-height: 1.2;">
                    {top_dim_code} {top_dim_name}
                </div>
                <div style="font-size: 0.75rem; color: #CBD5E1; margin-top: 4px; font-weight: 600;">
                    {top_dim_score_str}
                </div>
            </div>
            <div class="metric-card">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-bottom: 6px;">可評估題項覆蓋</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #38BDF8; line-height: 1.1;">
                    {v_cnt} <span style="font-size: 0.85rem; color: #64748B;">/ 28 題</span>
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 5px;">NA 缺漏題數: {n_cnt} 題</div>
            </div>
            <div class="metric-card">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-bottom: 6px;">實質證據覆蓋率</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #10B981; line-height: 1.1;">
                    {cov_pct:.1f}%
                </div>
                <div style="font-size: 0.72rem; color: #34D399; margin-top: 5px;">具頁碼與原文摘錄</div>
            </div>
            <div class="metric-card">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-bottom: 6px;">審計資料品質</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #A78BFA; line-height: 1.1;">
                    {q_val} 級
                </div>
                <div style="font-size: 0.72rem; color: #C4B5FD; margin-top: 5px;">信度品質綜合驗證</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
