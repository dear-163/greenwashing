"""
AI-GWRI 視覺化圖表產製模組
使用 Plotly 產製符合專業 ESG 研報水準的互動式圖表：
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
            f"構面: {code} ({name_str})<br>"
            f"原始平均: {val:.2f} / 4.0<br>"
            f"權重: {int((ds.weight if ds else 0)*100)}%<br>"
            f"加權貢獻: {weighted_str} 分<br>"
            f"有效題數: {ds.valid_item_count if ds else 0}/4 (NA: {ds.na_item_count if ds else 0})"
        )

    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    hover_closed = hover_texts + [hover_texts[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        name="企業報告書評估值",
        fillcolor="rgba(239, 68, 68, 0.25)",
        line=dict(color="#DC2626", width=2.5),
        marker=dict(size=7, color="#991B1B"),
        hovertext=hover_closed,
        hoverinfo="text"
    ))

    warning_line = [2.0] * len(categories_closed)
    fig.add_trace(go.Scatterpolar(
        r=warning_line,
        theta=categories_closed,
        mode="lines",
        name="中度風險警戒線 (2.0)",
        line=dict(color="#F59E0B", width=1.5, dash="dash"),
        hoverinfo="none"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4.0],
                tickvals=[0, 1, 2, 3, 4],
                ticktext=["0 (極低)", "1 (低)", "2 (中)", "3 (高)", "4 (極高)"],
                gridcolor="#E5E7EB",
                linecolor="#9CA3AF"
            ),
            angularaxis=dict(
                gridcolor="#E5E7EB",
                linecolor="#9CA3AF"
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        height=380,
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
            names.append(f"{code} ({int(ds.weight*100)}%)")
            raw_scores.append(ds.raw_average or 0.0)
            weighted_scores.append(ds.weighted_score or 0.0)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=names,
        y=raw_scores,
        name="原始平均分 (0-4分)",
        marker_color="#3B82F6",
        text=[f"{s:.2f}" for s in raw_scores],
        textposition="outside",
        yaxis="y1"
    ))

    fig.add_trace(go.Bar(
        x=names,
        y=weighted_scores,
        name="加權總分貢獻 (滿分100)",
        marker_color="#10B981",
        text=[f"{ws:.1f}分" for ws in weighted_scores],
        textposition="outside",
        yaxis="y2"
    ))

    fig.update_layout(
        barmode="group",
        yaxis=dict(
            title=dict(text="原始平均分 (0-4)", font=dict(color="#1D4ED8")),
            range=[0, 4.8],
            side="left",
            showgrid=True,
            gridcolor="#F3F4F6"
        ),
        yaxis2=dict(
            title=dict(text="加權分貢獻", font=dict(color="#047857")),
            range=[0, 30],
            side="right",
            overlaying="y",
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=30, r=30, t=30, b=50),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_gauge_meter(score: float, risk_level: str) -> go.Figure:
    """
    繪製 AI-GWRI 總分儀表盤 (0-100)
    """
    bar_color = "#DC2626" if score >= 60 else ("#F59E0B" if score >= 40 else "#10B981")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"AI-GWRI 漂綠風險指數<br><span style='font-size:14px;color:gray;'>{risk_level}</span>", "font": {"size": 18}},
        number={"suffix": " 分", "font": {"size": 32, "color": "#1E293B"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
            "bar": {"color": bar_color, "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, 20], "color": "rgba(16, 185, 129, 0.25)"},
                {"range": [20, 40], "color": "rgba(59, 130, 246, 0.25)"},
                {"range": [40, 60], "color": "rgba(245, 158, 11, 0.25)"},
                {"range": [60, 80], "color": "rgba(249, 115, 22, 0.35)"},
                {"range": [80, 100], "color": "rgba(239, 68, 68, 0.45)"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    ))

    fig.update_layout(
        height=260,
        margin=dict(l=30, r=30, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_item_distribution_chart(items: List[ItemScoreResult]) -> go.Figure:
    """
    繪製 28 題評分分佈統計直方圖 (0, 1, 2, 3, 4, NA)
    """
    counts = {
        "0分 (無風險)": 0,
        "1分 (低風險)": 0,
        "2分 (中風險)": 0,
        "3分 (高風險)": 0,
        "4分 (極高)": 0,
        "NA (不可評)": 0
    }
    for it in items:
        if it.score is None:
            counts["NA (不可評)"] += 1
        elif it.score == 0:
            counts["0分 (無風險)"] += 1
        elif it.score == 1:
            counts["1分 (低風險)"] += 1
        elif it.score == 2:
            counts["2分 (中風險)"] += 1
        elif it.score == 3:
            counts["3分 (高風險)"] += 1
        elif it.score == 4:
            counts["4分 (極高)"] += 1

    colors = ["#10B981", "#34D399", "#FBBF24", "#F97316", "#EF4444", "#9CA3AF"]
    
    fig = go.Figure([go.Bar(
        x=list(counts.keys()),
        y=list(counts.values()),
        marker_color=colors,
        text=list(counts.values()),
        textposition="outside"
    )])

    fig.update_layout(
        title="28 題評分分佈 (題數統計)",
        title_font_size=15,
        yaxis=dict(title="題數", range=[0, max(counts.values()) + 3], showgrid=True, gridcolor="#F3F4F6"),
        xaxis=dict(title=""),
        margin=dict(l=20, r=20, t=40, b=20),
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
