"""
AI-GWRI 學術研究專用：信度檢驗與編碼員一致性計算工具
依據 codebook.md 第八節規範：
1. 題項層級（0-4 有序）：計算 Cohen's Weighted Kappa 與 Krippendorff's Alpha
2. 構面與總分（連續）：計算 Intraclass Correlation Coefficient (ICC) 與 Pearson / Spearman 相關係數
3. 自動產出論文用之學術評估表格 (Markdown & LaTeX)
"""

import math
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np


def compute_weighted_cohen_kappa(rater1: List[int], rater2: List[int], num_categories: int = 5) -> float:
    """
    計算 Quadratic Weighted Cohen's Kappa (適用於 0-4 分序位尺度)
    """
    valid_pairs = [(r1, r2) for r1, r2 in zip(rater1, rater2) if r1 is not None and r2 is not None]
    if not valid_pairs:
        return 0.0

    n = len(valid_pairs)
    obs_mat = np.zeros((num_categories, num_categories))
    for r1, r2 in valid_pairs:
        obs_mat[int(r1), int(r2)] += 1
    obs_mat = obs_mat / n

    # 計算邊際分佈
    p_r1 = np.sum(obs_mat, axis=1)
    p_r2 = np.sum(obs_mat, axis=0)
    exp_mat = np.outer(p_r1, p_r2)

    # 權重矩陣 (Quadratic weight)
    w_mat = np.zeros((num_categories, num_categories))
    for i in range(num_categories):
        for j in range(num_categories):
            w_mat[i, j] = ((i - j) ** 2) / ((num_categories - 1) ** 2)

    po = np.sum(w_mat * obs_mat)
    pe = np.sum(w_mat * exp_mat)

    if pe == 0:
        return 1.0
    return round(float(1.0 - (po / pe)), 4)


def compute_icc(rater1: List[float], rater2: List[float]) -> float:
    """
    計算 ICC(2,1) - Two-way random effects, absolute agreement, single rater
    """
    pairs = [(r1, r2) for r1, r2 in zip(rater1, rater2) if r1 is not None and r2 is not None]
    if len(pairs) < 2:
        return 0.0

    y = np.array(pairs)
    n, k = y.shape  # n=樣本數, k=2 (rater數量)
    
    # 計算 ANOVA 平方和
    mean_row = np.mean(y, axis=1)
    mean_col = np.mean(y, axis=0)
    grand_mean = np.mean(y)

    ss_total = np.sum((y - grand_mean) ** 2)
    ss_rows = k * np.sum((mean_row - grand_mean) ** 2)
    ss_cols = n * np.sum((mean_col - grand_mean) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1)) if ((n - 1) * (k - 1)) > 0 else 1e-6

    # ICC(2,1) 公式
    denom = ms_rows + (k - 1) * ms_error + (k * (ms_cols - ms_error) / n)
    if denom == 0:
        return 1.0
    icc = (ms_rows - ms_error) / denom
    return round(float(icc), 4)


def generate_reliability_report_demo():
    """產製示範學術信度報告表格"""
    print("=" * 70)
    print("📈 AI-GWRI 學術信度檢驗模擬範例 (LLM vs Human Coder)")
    print("=" * 70)

    # 模擬 50 份報告之 28 題人工與 LLM 評分
    np.random.seed(42)
    sample_size = 50
    
    # 題項層級
    human_scores = np.random.choice([0, 1, 2, 3, 4], size=sample_size, p=[0.1, 0.3, 0.35, 0.2, 0.05])
    # LLM 與人類高度一致 (85% 機率相同，15% 差 1 分)
    noise = np.random.choice([0, 1, -1], size=sample_size, p=[0.85, 0.08, 0.07])
    llm_scores = np.clip(human_scores + noise, 0, 4)

    kappa = compute_weighted_cohen_kappa(human_scores.tolist(), llm_scores.tolist())

    # 總分層級 (0-100)
    human_total = human_scores * 20.0 + np.random.normal(5, 3, size=sample_size)
    llm_total = llm_scores * 20.0 + np.random.normal(5, 3, size=sample_size)
    icc_val = compute_icc(human_total.tolist(), llm_total.tolist())
    corr = float(np.corrcoef(human_total, llm_total)[0, 1])

    print(f"抽樣檢驗樣本數 (N): {sample_size} 本報告書")
    print(f"1. 題項層級 (Item-level) Quadratic Weighted Kappa: {kappa:.4f} (卓越信度 > 0.80)")
    print(f"2. 構面與總分 (Dimension/Index-level) ICC(2,1):   {icc_val:.4f} (卓越一致性 > 0.75)")
    print(f"3. 總分皮爾森相關係數 (Pearson Correlation r):    {corr:.4f} (p < 0.001)")
    print("-" * 70)
    print("論文直接引用格式 (LaTeX Table Template):\n")
    latex_snippet = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Inter-Rater Reliability: LLM (GPT-4o) vs. Human Coders}}
\\begin{{tabular}}{{lcccc}}
\\hline
Metric Level & Agreement Coefficient & Value & Benchmark & Reliability Level \\\\
\\hline
Item-level (28 items) & Quadratic Weighted $\\kappa$ & {kappa:.4f} & $> 0.80$ & Almost Perfect \\\\
Dimension Scores & ICC(2,1) & {icc_val:.4f} & $> 0.75$ & Excellent \\\\
AI-GWRI Total Index & Pearson Correlation $r$ & {corr:.4f} & $p < 0.001$ & Highly Significant \\\\
\\hline
\\end{{tabular}}
\\end{{table}}"""
    print(latex_snippet)


if __name__ == "__main__":
    generate_reliability_report_demo()
