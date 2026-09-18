# AI-GWRI 企業永續報告書漂綠風險自動評分系統 (MVP)

> **AI-based Greenwashing Risk Index (AI-GWRI)** 是基於學術文獻（Walker & Wan, 2012; Marquis et al., 2016; Michelon et al., 2015; Lagasio, 2024 等）與實務審計準則所設計的企業永續報告書漂綠風險評估架構。本專案將手冊（`codebook.md`）中的 28 個題項轉化為端到端可執行的 Evidence-based LLM 自動評分系統。

---

## 🌟 核心特色與架構設計

1. **嚴格保留實體 PDF 頁碼（Auditable Evidence Trail）**：
   - 透過 `pdfplumber` 與 `pypdf` 引擎雙模備援解析，保證萃取出的每段證據均對應 PDF 實體頁碼（1-indexed Page Number）。
   - 提供關鍵字權重機制（重大性、溫室氣體、廢棄物、裁罰、第三方查證等），智慧篩選大型報告書（100+ 頁）最具代表性的重點章節，杜絕 Context Window 溢位。

2. **OpenAI 結構化輸出（Structured Outputs）**：
   - 採用 OpenAI 最新 SDK Client 與 Pydantic 模型（`beta.chat.completions.parse`），確保 LLM 輸出嚴格符合 `ItemScoreResult` 規格。
   - 完整注入手冊中 28 題之「操作型定義」、「0–4 分判定規則」、「正反範例」與「NA 判定規則」。
   - 遵循五大核心原則：每題具備原文證據＋頁碼；0 分代表充分證據顯示低風險而非沒寫；資訊不足或非重大議題標示為 `NA`。

3. **純 Python 數學公式計算（禁止 LLM 心算）**：
   - 依照手冊第七節官方公式精確運算：
     $$\text{AI-GWRI} = 25\left(\frac{\text{CEG}}{4}\right) + 15\left(\frac{\text{QEG}}{4}\right) + 15\left(\frac{\text{TAG}}{4}\right) + 20\left(\frac{\text{SDR}}{4}\right) + 10\left(\frac{\text{VRG}}{4}\right) + 10\left(\frac{\text{VAG}}{4}\right) + 5\left(\frac{\text{LIR}}{4}\right)$$
   - 各構面自動排除 NA 題項計算有效平均分；若有效題少於 2 題自動警示 `Low Reliability`。
   - 彙總計算 NA Ratio、Evidence Coverage Ratio、High-confidence 分佈與總體資料品質評等。

4. **互動式 Streamlit 前端與 Plotly 視覺化看板**：
   - **總結看板**：AI-GWRI 總分 (0-100)、風險色塊、最高/次高風險構面、數據品質指標。
   - **互動圖表**：七大構面漂綠風險雷達圖（含中度風險警戒線）、原始平均分 vs 加權得分貢獻長條圖、總分儀表盤、28 題評分分佈直方圖。
   - **審計明細抽屜**：7 大構面 Tab + 28 題可展開檢視卡片，一覽給分、判定理由、支持證據（原文+頁碼）、反向證據（原文+頁碼）、缺漏資訊。
   - **雙模匯出**：支援一鍵匯出完整結構化 `JSON` 報告，以及供計量實證分析使用的 28 題項 `CSV` 檔案。
   - **內建 Demo 體驗模式**：即便無 API Key 或無大檔，也能一鍵載入示範報告書完整數據快速預覽。

---

## 📁 專案檔案結構

```
ai-gwri/
├── app.py                     # Streamlit 前端互動應用程式主入口
├── codebook.md                # AI-GWRI 永續報告書漂綠風險評估手冊 (v1.0)
├── requirements.txt           # 專案必要依賴套件清單
├── .env.example               # 環境變數設定範本 (API Key, Model 設定)
├── models/
│   ├── __init__.py
│   └── schema.py              # Pydantic 結構化資料模型 (ItemScoreResult, AssessmentReport 等)
├── core/
│   ├── __init__.py
│   ├── codebook_data.py       # 28 題項定義、0-4 分 Rubrics、正反例與 Prompt 生成器
│   ├── pdf_parser.py          # PDF 實體頁碼解析、文字清洗與重大章節篩選器
│   ├── scorer.py              # LLM 評分流程 (Step 1 宣稱辨識 + Step 2 構面批次審核 + Mock 引擎)
│   └── calculator.py          # 純 Python 構面平均分、AI-GWRI 加權計算與信效度檢驗
├── utils/
│   ├── __init__.py
│   └── visualizer.py          # Plotly 雷達圖、長條圖、儀表盤產製模組
└── tests/
    ├── test_codebook_and_calculator.py
    └── test_calculator_and_report.py
```

---

## 🚀 快速開始

### 1. 安裝環境依賴

建議使用 Python 3.10+：

```bash
# 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 安裝所需套件
pip install -r requirements.txt
```

### 2. 設定 API 金鑰

複製 `.env.example` 為 `.env`，並填入你的 OpenAI API Key：

```bash
cp .env.example .env
```

`.env` 內容範例：
```env
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
```
*(亦可直接在 Streamlit 側邊欄輸入 API Key)*

### 3. 啟動 Streamlit 應用程式

```bash
streamlit run app.py
```

瀏覽器將自動開啟 `http://localhost:8501`。

### 4. 執行單元測試

專案已內建完整測試套件：

```bash
python -m unittest discover tests
```

---

## 📊 七大構面與權重對照表

| 構面代碼 | 構面名稱 (中文) | 英文全名 | 題數 | 權重 |
|:---:|:---|:---|:---:|:---:|
| **CEG** | 主張—證據落差 | Claim–Evidence Gap | 4 題 | **25%** |
| **QEG** | 量化與績效落差 | Quantification & Performance Evidence Gap | 4 題 | **15%** |
| **TAG** | 目標—達成落差 | Target–Achievement Gap | 4 題 | **15%** |
| **SDR** | 選擇性揭露風險 | Selective Disclosure Risk | 4 題 | **20%** |
| **VRG** | 驗證與可信度落差 | Verification & Reliability Gap | 4 題 | **10%** |
| **VAG** | 模糊性與空泛性落差 | Vagueness & Ambiguity Gap | 4 題 | **10%** |
| **LIR** | 語言印象管理風險 | Linguistic Impression-management Risk | 4 題 | **5%** |
| **總計**| **AI-GWRI 總評** | **7 大構面完整審計** | **28 題** | **100%** |
