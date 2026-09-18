<p align="center">
  <img src="assets/logo.png" width="140" alt="AI-GWRI Logo" style="border-radius: 28px; box-shadow: 0 8px 24px rgba(10,25,47,0.4);" />
</p>

# AI-GWRI 企業永續報告書漂綠風險自動鑑識評分系統

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://greenwashing-ai-gwri.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)

> **AI-based Greenwashing Risk Index (AI-GWRI)** 是基於頂級學術文獻（Walker & Wan, 2012; Marquis et al., 2016; Michelon et al., 2015; Lagasio, 2024 等）與國際實務審計準則（GRI, TCFD, SASB, ISSB）所構建的企業永續報告書漂綠風險鑑識評估架構。本系統將完整評估手冊（`codebook.md`）中的 7 大構面、28 個題項轉化為端到端可執行的 Evidence-based 自動化鑑識引擎。

🌐 **線上展示雲端服務**: [https://greenwashing-ai-gwri.streamlit.app](https://greenwashing-ai-gwri.streamlit.app)

---

## 🌟 核心特色與架構優勢

1. **嚴格保留實體 PDF 頁碼（Auditable Evidence Trail）**：
   - 採用高效串流解析技術，百頁報告書秒級解析完成，百分之百鎖定 PDF 實體頁碼（1-indexed Page Number）。
   - 具備智慧主題章節過濾演算法，針對重大性、溫室氣體盤查、減碳目標、環保違規裁罰及第三方查證等重點頁面進行精準權重抽取。

2. **2 批次高併發打包架構（2-Batch Packaging Pipeline）**：
   - 突破傳統多輪 API 連線瓶頸，將 7 大構面審計精煉打包為 2 大獨立批次（實質作為構面 + 獨立驗證與修辭構面）。
   - 請求次數減少 65%，徹底杜絕 API 頻率限制（429）與伺服器壅塞（503），兼顧全面深度原文比對與秒級快速推論。

3. **雙主流模型引擎支援（Google Gemini & OpenAI）**：
   - **Google Gemini**: 原生支援 `gemini-3.1-flash-lite`（每日 500 次高額度推薦）、`gemini-3.5-flash-lite`、`gemini-3.7-flash`、`gemini-2.5-flash`、`gemini-2.5-pro`。
   - **OpenAI**: 支援 `gpt-4o-mini`、`gpt-4o`。
   - 輸入 `AIzaSy...` 金鑰自動路由至 Google Gemini 端點；輸入 `sk-...` 自動路由至 OpenAI 端點。

4. **純 Python 數學公式計算（嚴禁 LLM 心算）**：
   - 嚴格依照手冊官方公式進行正規化加權運算：
     $$\text{AI-GWRI} = 25\left(\frac{\text{CEG}}{4}\right) + 15\left(\frac{\text{QEG}}{4}\right) + 15\left(\frac{\text{TAG}}{4}\right) + 20\left(\frac{\text{SDR}}{4}\right) + 10\left(\frac{\text{VRG}}{4}\right) + 10\left(\frac{\text{VAG}}{4}\right) + 5\left(\frac{\text{LIR}}{4}\right)$$
   - 各構面自動排除 NA 題項進行動態權重歸一化，若有效題數少於 2 題自動標示為 `Low Reliability`。
   - 產出 NA 佔比、證據覆蓋率（Evidence Coverage）、信心水準分佈與總體資料品質評等。

5. **數位金融鑑識級互動可視化看板**：
   - **6 大 KPI 自適應摘要卡片**：AI-GWRI 總分、五級風險評定、最高風險構面中英全稱、題項覆蓋數、證據覆蓋率與審計品質。
   - **雙子圖長條圖 (Subplots)**：左右分離獨立呈現「0-4 原始風險分」與「滿分 100 加權分貢獻」，徹底杜絕標籤數字擠壓重疊。
   - **七大構面風險雷達圖**：附帶實質永續線 (1.0) 與中度風險警戒線 (2.0)。
   - **總分儀表盤與 28 題評分分佈**：快速掌握企業漂綠風險落點。
   - **結構化雙模匯出**：支援一鍵下載完整 `JSON` 鑑識審計報告與計量實證分析專用 `CSV` 資料。

---

## 📊 七大構面與權重對照表

| 構面代碼 | 構面名稱 (中文) | 英文全名 | 題數 | 權重 | 理論文獻基礎 |
|:---:|:---|:---|:---:|:---:|:---|
| **CEG** | 主張—證據落差 | Claim–Evidence Gap | 4 題 | **25%** | Walker & Wan (2012); Lublóy et al. (2025) |
| **QEG** | 量化與績效落差 | Quantification & Performance Evidence Gap | 4 題 | **15%** | Marquis et al. (2016); Michelon et al. (2015) |
| **TAG** | 目標—達成落差 | Target–Achievement Gap | 4 題 | **15%** | Walker & Wan (2012); Lublóy et al. (2025) |
| **SDR** | 選擇性揭露風險 | Selective Disclosure Risk | 4 題 | **20%** | Marquis et al. (2016); de Freitas Netto et al. (2020) |
| **VRG** | 驗證與可信度落差 | Verification & Reliability Gap | 4 題 | **10%** | Michelon et al. (2015); Gorovaia & Makrominas (2025) |
| **VAG** | 模糊性與空泛性落差 | Vagueness & Ambiguity Gap | 4 題 | **10%** | de Freitas Netto et al. (2020); Michelon et al. (2015) |
| **LIR** | 語言印象管理風險 | Linguistic Impression-management Risk | 4 題 | **5%** | Lagasio (2024); Gorovaia & Makrominas (2025) |
| **總計**| **AI-GWRI 總評** | **7 大構面完整審計** | **28 題** | **100%** | **五級漂綠風險矩陣評定** |

---

## 📁 專案檔案結構

```
ai-gwri/
├── app.py                     # Streamlit 前端鑑識應用主入口
├── codebook.md                # AI-GWRI 永續報告書漂綠風險評估手冊 (v1.0)
├── requirements.txt           # 專案必要依賴套件清單
├── models/
│   └── schema.py              # Pydantic 結構化資料模型 (ItemScoreResult, AssessmentReport 等)
├── core/
│   ├── codebook_data.py       # 28 題項定義、0-4 分 Rubrics、正反範例與 Prompt 生成器
│   ├── pdf_parser.py          # PDF 串流頁碼解析、文字清洗與重大章節篩選器
│   ├── scorer.py              # 2-Batch 打包審計引擎 (自帶 429/503 退避重試與容錯降級)
│   └── calculator.py          # 純 Python 構面加權、正規化公式計算與信效度檢驗
├── visualization/
│   └── visualizer.py          # Plotly 雙子圖長條圖、雷達圖、儀表盤產製模組
└── tests/
    └── test_codebook_and_calculator.py
```

---

## 🚀 本地快速啟動

### 1. 安裝環境依賴

建議使用 Python 3.10 以上版本：

```bash
# 建立並啟用虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 安裝所需套件
pip install -r requirements.txt
```

### 2. 設定 API 金鑰 (選填)

若需在本地預填 API Key，可建立 `.env` 檔案：

```env
OPENAI_API_KEY=sk-... 或 AIzaSy...
```

*(亦可直接於 Streamlit 側邊欄即時輸入金鑰)*

### 3. 啟動 Streamlit 鑑識系統

```bash
streamlit run app.py
```

系統啟動後，瀏覽器將自動開啟 `http://localhost:8501`。

---

## ⚖️ 學術免責聲明 (Academic Disclaimer)

本系統評定之 AI-GWRI 分數與風險等級，代表企業永續報告書在揭露結構、證據充份性與語意修辭上所呈現的「漂綠風險（Greenwashing Risk）」，不等同於已確認之法律違法、裁罰定讞或財務欺瞞事件。報告成果適用於學術研究、永續投資盡職調查（ESG Due Diligence）及企業自律檢視之輔助參考。
