"""
AI-GWRI 視覺化圖表產製模組 (Greenwashing Forensic Aesthetic)
使用 Plotly 產製符合頂級 ESG 數位鑑識與反漂綠審計視覺質感的暗色互動圖表：
1. 七大構面漂綠風險雷達圖 (Radar Chart with Risk Tiers)
2. 七大構面原始分與加權分對比長條圖 (Dimension Bar Chart)
3. AI-GWRI 總分儀表盤 (Gauge Meter)
4. 28 題評分分佈直方圖 (Score Distribution)
"""

from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from models.schema import DimensionScore, ItemScoreResult


def create_radar_chart(dimension_scores: Dict[str, DimensionScore]) -> go.Figure:
    """
    繪製七大構面 0-4 分風險雷達圖。
    注意：在 AI-GWRI 中，分數愈高代表漂綠風險愈高（0 代表低風險，4 代表極高風險）。
    """
    categories = [
        "CEG<br>(主張證據)",
        "QEG<br>(量化績效)",
        "TAG<br>(目標達成)",
        "SDR<br>(選擇揭露)",
        "VRG<br>(驗證可靠)",
        "VAG<br>(模糊空泛)",
        "LIR<br>(語言印象)"
    ]
    dim_codes = ["CEG", "QEG", "TAG", "SDR", "VRG", "VAG", "LIR"]
    
    values = []
    hover_texts = []
    for code in dim_codes:
        ds = dimension_scores.get(code)
        val = ds.raw_average if (ds and ds.raw_average is not None) else 0.0
        values.append(val)
        name_str = ds.dimension_name if ds else ""
        weighted_str = f"{ds.weighted_score:.1f}" if (ds and ds.weighted_score is not None) else "0.0"
        hover_texts.append(
            f"<b>構面: {code}</b> ({name_str})<br>"
            f"原始平均: <span style='color:#F87171;'>{val:.2f}</span> / 4.0<br>"
            f"權重: {int((ds.weight if ds else 0)*100)}%<br>"
            f"加權貢獻: {weighted_str} 分<br>"
            f"有效題數: {ds.valid_item_count if ds else 0}/4 (NA: {ds.na_item_count if ds else 0})"
        )

    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    hover_closed = hover_texts + [hover_texts[0]]

    fig = go.Figure()

    # 企業實際得分（以亮紅半透明漸層呈現風險面貌）
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        name="企業報告書漂綠風險",
        fillcolor="rgba(239, 68, 68, 0.35)",
        line=dict(color="#EF4444", width=3),
        marker=dict(size=8, color="#F87171", symbol="diamond"),
        hovertext=hover_closed,
        hoverinfo="text"
    ))

    # 風險警戒線（中度風險基準線 2.0）
    warning_line = [2.0] * len(categories_closed)
    fig.add_trace(go.Scatterpolar(
        r=warning_line,
        theta=categories_closed,
        mode="lines",
        name="中度風險警戒線 (2.0)",
        line=dict(color="#FBBF24", width=2, dash="dash"),
        hoverinfo="none"
    ))

    # 安全基準線（低度風險基準線 1.0）
    safe_line = [1.0] * len(categories_closed)
    fig.add_trace(go.Scatterpolar(
        r=safe_line,
        theta=categories_closed,
        mode="lines",
        name="實質永續基準線 (1.0)",
        line=dict(color="#34D399", width=1.5, dash="dot"),
        hoverinfo="none"
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(10, 20, 15, 0.6)",
            radialaxis=dict(
                visible=True,
                range=[0, 4.0],
                tickvals=[0, 1, 2, 3, 4],
                ticktext=["0 (實質)", "1 (微瑕)", "2 (中度)", "3 (高度)", "4 (極高)"],
                gridcolor="#1E3A2B",
                linecolor="#34D399",
                tickfont=dict(color="#94A3B8", size=10)
            ),
            angularaxis=dict(
                gridcolor="#1E3A2B",
                linecolor="#34D399",
                tickfont=dict(color="#F1F5F9", size=11, family="sans-serif")
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=11)
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_dimension_bar_chart(dimension_scores: Dict[str, DimensionScore]) -> go.Figure:
    """
    繪製七大構面原始平均分 (0-4) 與權重貢獻對比長條圖
    """
    dim_codes = ["CEG", "QEG", "TAG", "SDR", "VRG", "VAG", "LIR"]
    names = []
    raw_scores = []
    weighted_scores = []

    for code in dim_codes:
        ds = dimension_scores.get(code)
        if ds:
            names.append(f"{code}<br>({int(ds.weight*100)}%)")
            raw_scores.append(ds.raw_average or 0.0)
            weighted_scores.append(ds.weighted_score or 0.0)

    fig = go.Figure()

    # 原始得分
    fig.add_trace(go.Bar(
        x=names,
        y=raw_scores,
        name="原始平均分 (0-4分)",
        marker_color="#38BDF8",
        marker_line=dict(color="#0284C7", width=1.5),
        text=[f"{s:.2f}" for s in raw_scores],
        textposition="outside",
        textfont=dict(color="#E2E8F0"),
        yaxis="y1"
    ))

    # 加權得分貢獻
    fig.add_trace(go.Bar(
        x=names,
        y=weighted_scores,
        name="加權總分貢獻 (滿分100)",
        marker_color="#10B981",
        marker_line=dict(color="#059669", width=1.5),
        text=[f"{ws:.1f}分" for ws in weighted_scores],
        textposition="outside",
        textfont=dict(color="#E2E8F0"),
        yaxis="y2"
    ))

    fig.update_layout(
        barmode="group",
        yaxis=dict(
            title=dict(text="原始平均分 (0-4)", font=dict(color="#38BDF8")),
            range=[0, 4.8],
            side="left",
            showgrid=True,
            gridcolor="#1E293B",
            tickfont=dict(color="#94A3B8")
        ),
        yaxis2=dict(
            title=dict(text="加權分貢獻", font=dict(color="#34D399")),
            range=[0, 30],
            side="right",
            overlaying="y",
            showgrid=False,
            tickfont=dict(color="#94A3B8")
        ),
        xaxis=dict(
            tickfont=dict(color="#E2E8F0", size=11)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=11)
        ),
        margin=dict(l=30, r=30, t=30, b=50),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_gauge_meter(score: float, risk_level: str) -> go.Figure:
    """
    繪製 AI-GWRI 總分儀表盤 (0-100)
    """
    bar_color = "#EF4444" if score >= 60 else ("#F59E0B" if score >= 40 else "#10B981")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={
            "text": f"<span style='font-size:16px;color:#94A3B8;'>AI-GWRI 漂綠風險指數</span><br><span style='font-size:18px;font-weight:700;color:{bar_color};'>{risk_level}</span>",
            "font": {"family": "sans-serif"}
        },
        number={"suffix": " 分", "font": {"size": 36, "color": "#F8FAFC", "family": "sans-serif"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#64748B", "tickfont": {"color": "#94A3B8"}},
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": "#0B1510",
            "borderwidth": 1.5,
            "bordercolor": "#1E3A2B",
            "steps": [
                {"range": [0, 20], "color": "rgba(16, 185, 129, 0.25)"},
                {"range": [20, 40], "color": "rgba(56, 189, 248, 0.25)"},
                {"range": [40, 60], "color": "rgba(245, 158, 11, 0.25)"},
                {"range": [60, 80], "color": "rgba(249, 115, 22, 0.35)"},
                {"range": [80, 100], "color": "rgba(239, 68, 68, 0.45)"}
            ],
            "threshold": {
                "line": {"color": "#EF4444", "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_item_distribution_chart(items: List[ItemScoreResult]) -> go.Figure:
    """
    繪製 28 題評分分佈統計直方圖 (0, 1, 2, 3, 4, NA)
    """
    counts = {
        "0分 (實質)": 0,
        "1分 (微瑕)": 0,
        "2分 (中度)": 0,
        "3分 (高度)": 0,
        "4分 (極高)": 0,
        "NA (不可評)": 0
    }
    for it in items:
        if it.score is None:
            counts["NA (不可評)"] += 1
        elif it.score == 0:
            counts["0分 (實質)"] += 1
        elif it.score == 1:
            counts["1分 (微瑕)"] += 1
        elif it.score == 2:
            counts["2分 (中度)"] += 1
        elif it.score == 3:
            counts["3分 (高度)"] += 1
        elif it.score == 4:
            counts["4分 (極高)"] += 1

    colors = ["#10B981", "#34D399", "#FBBF24", "#F97316", "#EF4444", "#64748B"]
    
    fig = go.Figure([go.Bar(
        x=list(counts.keys()),
        y=list(counts.values()),
        marker_color=colors,
        marker_line=dict(color="#0F172A", width=1),
        text=list(counts.values()),
        textposition="outside",
        textfont=dict(color="#F1F5F9", size=13)
    )])

    fig.update_layout(
        title=dict(text="28 題評分分佈 (題數統計)", font=dict(color="#F1F5F9", size=15)),
        yaxis=dict(title="題數", range=[0, max(counts.values()) + 3], showgrid=True, gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
        xaxis=dict(tickfont=dict(color="#CBD5E1", size=11)),
        margin=dict(l=20, r=20, t=40, b=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
