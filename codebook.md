AI-GWRI Codebook Version 1.0

AI-based Greenwashing Risk Index

永續報告書漂綠風險之 LLM／人工編碼操作手冊

適用對象：企業永續報告書、ESG 報告書、CSR 報告書

評分單位：公司 × 年度

核心原則：Claim → Evidence → Action → Outcome → Verification

一、Codebook 使用目的與基本原則

本 Codebook 將 AI-GWRI 的 28 個題項轉化為可重複執行的 evidence-based coding 規則，可同時支援大型語言模型（LLM）自動評分與人工 coder 進行內容分析。核心概念來自 greenwashing 的 decoupling、selective disclosure、symbolic–substantive actions、揭露品質與 NLP／impression-management 文獻（Walker & Wan, 2012; Marquis et al., 2016; Michelon et al., 2015; Lagasio, 2024; Gorovaia & Makrominas, 2025; Lublóy et al., 2025）。

評分時不得僅依語氣、單一句子或關鍵字判斷。LLM 必須先抽取環境宣稱，再搜尋相關數據、行動、目標、結果、負面資訊與第三方驗證，最後依規則評分。

原則一：每一題都必須有『原文證據＋頁碼』；若無法定位，應降低信心或標示 NA。

原則二：0 分代表『有充分證據顯示低風險』，不是『報告書沒寫』。資訊不足時使用 NA。

原則三：公司沒有某項重大環境議題時，不應因缺乏該議題資訊自動扣分；應先判斷 materiality。

原則四：評分應以公司年度為單位，但若題項涉及目標達成、跨年重複或揭露一致性，可使用前 1–3 年報告輔助判斷。

原則五：LLM 應輸出可審核的結構化資料，不可只回傳最終分數。

二、標準輸出欄位（LLM Evidence Schema）


| 欄位 | 說明 |

| --- | --- |

| company | 公司名稱 |

| report_year | 報告年度 |

| item_code | 題項代碼，例如 CEG1 |

| score | 0–4；若無法合理判斷則 NA |

| confidence | High / Medium / Low |

| materiality_status | Material / Non-material / Unclear |

| evidence_page | PDF 頁碼；可複數 |

| evidence_quote | 支持評分的原文摘錄；建議 1–3 段 |

| counter_evidence_page | 與初步判斷相反的證據頁碼 |

| counter_evidence_quote | 相反證據原文 |

| reasoning_summary | 不超過 100–150 字的判定理由 |

| year_compare | 與前期比較結果：Improved / Stable / Deteriorated / NA |

| missing_information | 關鍵缺失資訊 |

| source_scope | 報告書章節或附錄範圍 |



三、共通 0–4 分判定框架


| 分數 | 風險程度 | 一般判定邏輯 |

| --- | --- | --- |

| 0 | 無明顯風險 | 證據完整、可量化、可追蹤、可驗證；正反資訊揭露相對平衡。 |

| 1 | 低風險 | 大致完整，僅有次要資訊缺口，不影響對實際環境行動的判斷。 |

| 2 | 中度風險 | 存在明顯資訊缺口、證據不完整或揭露不平衡，但尚有部分實質支持。 |

| 3 | 高風險 | 多數重要宣稱缺乏充分實質證據，或負面資訊明顯弱化／缺失。 |

| 4 | 極高風險 | 宣稱與證據嚴重脫節、關鍵資訊明顯缺漏、重大負面資訊被選擇性弱化，或無法建立可信的行動—績效鏈。 |

| NA | 不可評分 | 資訊量不足、議題對該公司非重大且無合理評估基礎，或報告格式導致證據無法可靠擷取。 |



四、28 題詳細 Codebook

D1 Claim–Evidence Gap (CEG)

主要文獻基礎：Walker & Wan (2012); Lublóy et al. (2025)

CEG1　重要環境宣稱缺乏具體行動證據

操作型定義：

衡量公司提出重大環境主張後，是否能在同一報告年度找到直接對應的具體行動、專案、制度或執行措施。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 每個主要宣稱均能找到清楚且具體的行動證據。 |

| 1 | 大多數主要宣稱有行動支持，少數次要宣稱較抽象。 |

| 2 | 部分主要宣稱有行動支持，部分僅停留在承諾。 |

| 3 | 多數主要宣稱缺乏具體行動支持。 |

| 4 | 幾乎所有主要宣稱均只有口號或原則性描述。 |



正反例：

反例（低風險）：『2025 年完成 3 座廠房能源管理系統建置，投資新台幣 X 億元。』正例（高風險）：『本公司持續深化低碳營運，積極落實節能減碳。』但無任何專案或措施。

AI evidence fields：

claim_text, claim_topic, action_project, implementation_date, investment_amount, responsible_unit, project_scope

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若找不到主要環境宣稱，且報告整體環境資訊極少：不要直接給 0，應依 materiality 判斷；若無法判斷則 NA。

跨年度比較原則：

比較同一主題上一年度是否只有承諾、本年度是否新增具體行動。若新增行動，year_compare=Improved。

CEG2　宣稱之環境改善缺乏實際執行專案或措施

操作型定義：

衡量公司聲稱『改善、降低、提升』時，是否揭露造成該改善的具體執行機制，而非只報告結果或口號。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 改善結果與執行措施有直接對應。 |

| 1 | 多數改善有措施說明，細節略不足。 |

| 2 | 只有部分改善能對應措施。 |

| 3 | 多數改善聲稱無法找到對應措施。 |

| 4 | 大量改善性語句完全無執行內容。 |



正反例：

反例：『更換 1,200 台高效率馬達，使用電量下降 8.4%。』正例：『能源效率顯著提升。』但未說明任何措施。

AI evidence fields：

improvement_claim, before_after_metric, action_mechanism, project_name, scope, causal_link

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若僅有績效數據但無改善性宣稱，本題可 NA；不要因沒有『改善』字樣扣分。

跨年度比較原則：

跨年檢查改善措施是否持續存在，以及今年的績效是否與措施方向一致。

CEG3　Symbolic commitment 明顯多於 substantive action

操作型定義：

衡量報告中象徵性承諾、價值宣示與願景文字，相對於可驗證實質行動的比例與落差。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 承諾與實質行動大致平衡。 |

| 1 | 象徵性文字略多，但實質行動充分。 |

| 2 | 象徵性與實質內容約各半。 |

| 3 | 象徵性內容明顯多於實質行動。 |

| 4 | 主要環境篇章幾乎以願景、承諾、口號構成。 |



正反例：

反例：每項願景後均列專案、KPI、預算與成果。正例：大量『致力、持續、深化、領先、打造綠色未來』，但缺少行動與結果。

AI evidence fields：

symbolic_claim_count, substantive_action_count, symbolic_examples, substantive_examples, ratio_symbolic_substantive

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若報告內容過短、無法穩定計算 symbolic/substantive 比例，標示 NA。

跨年度比較原則：

比較 symbolic/substantive 比例是否逐年上升；若承諾增加但實質行動未同步增加，視為 Deteriorated。

CEG4　宣稱與提供之結果證據無法建立直接對應

操作型定義：

衡量公司提出環境宣稱後，報告中的成果數據是否能直接支持該宣稱，而非使用不同範圍、不同口徑或無關績效佐證。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 宣稱與結果一一對應，範圍與口徑一致。 |

| 1 | 少數範圍或口徑差異，但不影響結論。 |

| 2 | 部分宣稱只能由間接結果支持。 |

| 3 | 多數宣稱與成果數據對應弱。 |

| 4 | 宣稱與提供的結果幾乎無可辨識關聯。 |



正反例：

反例：宣稱『降低 Scope 2』，並提供同範圍 Scope 2 年度下降資料。正例：宣稱『整體碳排下降』，卻只提供單一廠區節電量。

AI evidence fields：

claim_scope, result_metric, result_scope, time_period, denominator, direct_match_flag

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若無結果性宣稱或無可比結果，依議題重要性判斷；無合理基礎時 NA。

跨年度比較原則：

檢查公司是否跨年改變範圍、口徑或母數，導致宣稱與結果不可比。

D2 Quantification & Performance Evidence Gap (QEG)

主要文獻基礎：Marquis et al. (2016); Michelon et al. (2015); Lublóy et al. (2025)

QEG1　重要環境宣稱缺乏量化數據

操作型定義：

衡量重大環境宣稱是否附有可量化數據，而非只以定性文字描述。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 主要宣稱均有量化數據。 |

| 1 | 少數次要宣稱缺乏數據。 |

| 2 | 約半數主要宣稱有數據。 |

| 3 | 多數主要宣稱只有定性描述。 |

| 4 | 幾乎沒有量化支持。 |



正反例：

反例：『用水強度下降 12.3%，至 0.45 m³/千元營收。』正例：『持續降低用水量』但無數值。

AI evidence fields：

claim_text, metric_name, absolute_value, unit, intensity_value, percentage_change

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若該宣稱本質上無法合理量化，則不應扣分，可 NA 或排除該 claim。

跨年度比較原則：

比較同一主題量化資訊是否增加；由定性轉為定量視為 Improved。

QEG2　缺乏基準年或基準值

操作型定義：

衡量績效與減量目標是否提供明確基準年或基準值，讓外部讀者能判斷改善幅度。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 主要目標與改善宣稱均有明確基準。 |

| 1 | 少數次要項目缺基準。 |

| 2 | 部分重要項目無基準。 |

| 3 | 多數改善性主張缺基準。 |

| 4 | 幾乎所有相對改善主張均無基準。 |



正反例：

反例：『以 2020 年為基準，2030 年 Scope 1+2 減量 42%。』正例：『2030 年大幅減碳』但無基準年。

AI evidence fields：

baseline_year, baseline_value, target_year, target_value, metric_name

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若該數據是絕對值揭露而非『改善／減量目標』，不必強制要求基準，可 NA。

跨年度比較原則：

檢查基準年是否跨年任意變更；如變更，必須揭露理由與重算。

QEG3　缺乏跨年度可比較資料

操作型定義：

衡量主要環境 KPI 是否至少提供兩期以上可比較數據，或清楚說明無法比較的原因。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 主要 KPI 有 3 年以上一致口徑資料。 |

| 1 | 大多數 KPI 有至少 2 年資料。 |

| 2 | 部分 KPI 可比較。 |

| 3 | 多數 KPI 僅單年值。 |

| 4 | 幾乎無跨年可比資料。 |



正反例：

反例：表列 2023–2025 排放、能源、水與廢棄物。正例：只提供 2025 單年數據，卻宣稱『持續改善』。

AI evidence fields：

year_series, metric_name, unit_consistency, scope_consistency, restatement_flag

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

新成立公司、新指標首次採用或法規首次要求揭露時，可 NA 或降低評分，但要記錄原因。

跨年度比較原則：

優先比較連續三年；若口徑變更，記錄是否有重編前期資料。

QEG4　數據範圍、coverage 或 denominator 不清楚

操作型定義：

衡量環境數據是否清楚說明涵蓋公司、子公司、廠區、地區、營運邊界，以及強度指標的母數。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 範圍、coverage 與 denominator 完整。 |

| 1 | 有少量邊界細節不清。 |

| 2 | 部分重要數據範圍或母數不清。 |

| 3 | 多數重要數據缺乏範圍說明。 |

| 4 | 數據無法判斷代表公司整體或局部。 |



正反例：

反例：『涵蓋全球 95% 營收之營運據點；強度以百萬元營收為母數。』正例：『碳排強度下降 15%』但不知母數或涵蓋哪些廠。

AI evidence fields：

organizational_boundary, geographic_scope, coverage_percent, denominator, denominator_unit, excluded_entities

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若該數據本身不需 denominator，則 denominator 可不適用；但 coverage 還是要判斷。

跨年度比較原則：

檢查 coverage 是否跨年擴大或縮小，以及公司是否說明對趨勢的影響。

D3 Target–Achievement Gap (TAG)

主要文獻基礎：Walker & Wan (2012); Lublóy et al. (2025)

TAG1　長期環境目標缺乏明確期限

操作型定義：

衡量環境承諾是否具有明確 target year 或完成期限。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 所有重大目標均有期限。 |

| 1 | 少數次要目標無期限。 |

| 2 | 部分重大目標只有模糊時間。 |

| 3 | 多數重大目標沒有明確期限。 |

| 4 | 目標幾乎都是無期限願景。 |



正反例：

反例：『2030 年再生能源使用比例達 60%。』正例：『持續提升再生能源使用比例。』

AI evidence fields：

target_text, target_year, interim_year, deadline_type

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若內容只是政策原則而非目標，不應強迫評分，可 NA。

跨年度比較原則：

比較過去無期限承諾是否轉為具體期限。

TAG2　目標缺乏短中期 milestones

操作型定義：

衡量長期目標是否拆解為可追蹤的中間里程碑。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 長期目標有清楚年度／階段性 milestones。 |

| 1 | 大多數目標有里程碑。 |

| 2 | 部分有、部分無。 |

| 3 | 長期目標多數沒有中期節點。 |

| 4 | 只存在遠期目標，完全沒有中間路徑。 |



正反例：

反例：2030 目標搭配 2026、2028 階段目標。正例：只寫『2050 淨零』。

AI evidence fields：

long_term_target, milestones, milestone_years, milestone_values

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若目標期限短於 2 年，可不要求 milestones，標示 NA。

跨年度比較原則：

跨年確認 milestones 是否按期更新，避免公司每年延後。

TAG3　過去承諾缺乏當年度進度追蹤

操作型定義：

衡量前期已提出的重要目標，在本年度是否揭露目前進度。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 重大前期目標均有進度與差距說明。 |

| 1 | 少數次要目標未更新。 |

| 2 | 約半數重要目標有進度。 |

| 3 | 多數前期承諾未追蹤。 |

| 4 | 過去目標在本年度幾乎消失。 |



正反例：

反例：『2030 減量 42%，截至 2025 已達 18%，進度符合路徑。』正例：2023 報告曾承諾目標，2025 報告完全不再提。

AI evidence fields：

prior_year_target, current_progress, progress_percent, status_on_track, explanation

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

首次報告或首次設定目標時 NA。

跨年度比較原則：

必須至少對照前一年度；重要長期目標建議回看 2–3 年。

TAG4　未達標目標未充分揭露或說明

操作型定義：

衡量公司在目標未達、落後或惡化時，是否坦誠揭露原因、差距與改善措施。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 未達標事項清楚揭露並解釋。 |

| 1 | 大致揭露，改善計畫略少。 |

| 2 | 有揭露但解釋有限。 |

| 3 | 未達標被弱化或只模糊帶過。 |

| 4 | 明顯存在未達標跡象但報告完全不說明。 |



正反例：

反例：『因新廠投產，排放較目標高 9%；已調整 2026 設備汰換計畫。』正例：指標惡化但正文只強調其他改善成果。

AI evidence fields：

target_value, actual_value, gap, missed_target_flag, cause, corrective_action

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若當年度無任何目標未達或無法辨識是否未達，NA。

跨年度比較原則：

跨年檢查未達標事項是否在次年被刪除或改寫目標。

D4 Selective Disclosure Risk (SDR)

主要文獻基礎：Marquis et al. (2016); de Freitas Netto et al. (2020); Lublóy et al. (2025)

SDR1　正面環境成果明顯比負面成果更突出

操作型定義：

衡量報告對正面與負面環境績效是否存在明顯呈現不對稱，包括篇幅、標題、圖表與敘述強度。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 正負資訊揭露平衡。 |

| 1 | 略偏正面但負面資訊仍清楚。 |

| 2 | 正面內容較突出，負面內容較簡略。 |

| 3 | 負面資訊明顯弱化。 |

| 4 | 整體呈現幾乎只剩正面成果。 |



正反例：

反例：同時揭露改善與惡化 KPI 並說明原因。正例：首頁大幅宣傳節能成果，排放增加僅藏於附表。

AI evidence fields：

positive_kpi_count, negative_kpi_count, positive_prominence, negative_prominence, negative_explanations

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若本年度所有重大指標確實均改善，不能因缺乏負面資訊扣分；需查核跨年數據後判斷。

跨年度比較原則：

比較各年負面資訊的篇幅與可見度是否異常下降。

SDR2　重大負面環境變動未充分說明

操作型定義：

衡量重要環境 KPI 惡化時，公司是否提供原因、影響與改善措施。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 所有重大惡化均有充分解釋。 |

| 1 | 少數惡化解釋不足。 |

| 2 | 約半數惡化有說明。 |

| 3 | 多數重大惡化未說明。 |

| 4 | 重大惡化被完全忽略或刻意弱化。 |



正反例：

反例：能源使用增加並解釋新廠投產與後續改善計畫。正例：用水增加 35% 但正文無解釋。

AI evidence fields：

negative_metric, year_on_year_change, materiality, cause, impact, corrective_action

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若無重大負面變動，NA。

跨年度比較原則：

至少比較前一年度；若公司跨年變更口徑，需排除口徑變動造成的假性惡化。

SDR3　重要排放、污染或資源指標存在揭露缺口

操作型定義：

衡量與公司重大環境議題相關的核心 KPI 是否缺漏，包括 Scope 1–3、能源、水、廢棄物、污染排放等。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 重大議題核心 KPI 完整。 |

| 1 | 僅少數次要 KPI 缺漏。 |

| 2 | 至少一項重要 KPI 缺漏或部分揭露。 |

| 3 | 多項重要 KPI 缺漏。 |

| 4 | 核心重大環境議題幾乎未量化揭露。 |



正反例：

反例：對公司重大議題提供完整 GHG、能源、水與廢棄物資料。正例：高碳排產業完全不揭露 Scope 1–2，卻大量強調公益植樹。

AI evidence fields：

material_topics, required_core_kpis, reported_kpis, missing_kpis, scope1, scope2, scope3, water, waste, pollutants

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若該 KPI 對該產業明確不具重大性，應標示 Non-material 並 NA，不可機械式扣分。

跨年度比較原則：

追蹤同一 KPI 是否突然消失；若前期有揭露、今年取消且無解釋，風險上升。

SDR4　使用局部改善形成整體環境改善印象

操作型定義：

衡量公司是否以單一廠區、單一專案或小範圍成果，暗示公司整體環境績效改善。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 局部與整體範圍標示清楚。 |

| 1 | 少數敘述略有泛化。 |

| 2 | 部分局部成果被放大。 |

| 3 | 多數正面敘述以局部資料代表整體。 |

| 4 | 高度依賴小範圍案例製造整體改善印象。 |



正反例：

反例：明確標示『僅適用台中廠，占總產量 12%』。正例：以單一示範廠減排 20% 宣稱『公司減碳成效卓越』。

AI evidence fields：

claim_scope, evidence_scope, company_total_scope, coverage_percent, generalization_flag

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若企業只有單一營運據點，局部／整體問題不適用，可 NA。

跨年度比較原則：

檢查正面案例 coverage 是否逐年下降但宣稱仍保持整體化。

D5 Verification & Reliability Gap (VRG)

主要文獻基礎：Michelon et al. (2015); Gorovaia & Makrominas (2025)

VRG1　重大環境 KPI 缺乏第三方驗證

操作型定義：

衡量重大環境數據是否經外部 assurance／verification，尤其是溫室氣體與關鍵 KPI。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 重大 KPI 多數經外部驗證。 |

| 1 | 主要 KPI 有驗證，少數未涵蓋。 |

| 2 | 僅部分重大 KPI 驗證。 |

| 3 | 大多數重大 KPI 未驗證。 |

| 4 | 完全無第三方驗證且公司仍高度依賴自我宣稱。 |



正反例：

反例：Scope 1–2 與主要水／能源數據經第三方查證。正例：報告大量強調減碳成果，但無任何 assurance／verification。

AI evidence fields：

assurance_provider, assurance_standard, verified_kpis, unverified_kpis, verification_statement

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若法規或產業慣例對某 KPI 尚無合理第三方驗證方式，可 NA 或降低重要性。

跨年度比較原則：

比較驗證範圍是否逐年擴大或縮小。

VRG2　Assurance coverage 不明或有限

操作型定義：

衡量 assurance 是否清楚說明涵蓋哪些章節、公司範圍、KPI 與 assurance level。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | coverage 與 assurance level 完整清楚。 |

| 1 | 少量細節不清。 |

| 2 | 僅列部分涵蓋範圍。 |

| 3 | coverage 非常有限或模糊。 |

| 4 | 只宣稱『經查證』但完全無法知道查證什麼。 |



正反例：

反例：附 assurance statement，明列 KPI、範圍與 limited/reasonable assurance。正例：只放查證機構 logo。

AI evidence fields：

assurance_scope, assurance_level, covered_entities, covered_kpis, exclusions

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若完全無 assurance，VRG1 可評分；VRG2 原則上 NA，避免重複處罰。

跨年度比較原則：

跨年檢查 assurance coverage 是否縮減而未說明。

VRG3　宣稱之資料來源或計算方法不透明

操作型定義：

衡量重要環境數據是否說明計算標準、方法、排放係數、資料來源或估計方式。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 方法與來源完整。 |

| 1 | 少量細節缺漏。 |

| 2 | 部分 KPI 方法不清。 |

| 3 | 多數 KPI 缺乏方法說明。 |

| 4 | 幾乎無法重現或理解數據如何計算。 |



正反例：

反例：說明 GHG Protocol、排放係數來源與估算方式。正例：只列『減碳 12%』，完全無方法。

AI evidence fields：

methodology, standard_used, emission_factor_source, data_source, estimation_method, restatement_method

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若數據為簡單直接量測且方法無重大歧義，可降低要求；仍應有來源。

跨年度比較原則：

檢查方法是否跨年變更及是否揭露重算。

VRG4　重要環境數據缺乏可追溯性

操作型定義：

衡量外部讀者是否能從報告附錄、索引、查證聲明或資料表追溯到環境 KPI 的來源與範圍。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 主要 KPI 可完整追溯。 |

| 1 | 少數 KPI 追溯較困難。 |

| 2 | 約半數 KPI 可追溯。 |

| 3 | 多數 KPI 無明確來源鏈。 |

| 4 | 幾乎所有重要數據都是孤立數字。 |



正反例：

反例：KPI 表列來源章節、查證範圍與計算註記。正例：圖表數字沒有來源、範圍或附註。

AI evidence fields：

kpi_table_reference, appendix_reference, assurance_reference, source_note, traceability_flag

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若報告本身結構嚴重損壞導致頁碼或表格不可辨識，NA。

跨年度比較原則：

跨年檢查同一 KPI 的定義與表格位置是否一致；不一致時需確認是否為定義變更。

D6 Vagueness & Ambiguity Gap (VAG)

主要文獻基礎：de Freitas Netto et al. (2020); Michelon et al. (2015)

VAG1　大量使用抽象環境承諾而無具體定義

操作型定義：

衡量企業是否大量使用願景式環境承諾，卻沒有界定其意義、範圍或可衡量結果。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 抽象承諾少，且均有具體化。 |

| 1 | 有少量抽象語言但不影響判斷。 |

| 2 | 抽象與具體內容約各半。 |

| 3 | 多數環境敘述偏抽象。 |

| 4 | 主要環境敘事幾乎都是不可驗證承諾。 |



正反例：

反例：『綠色製造』明確定義為能源、排放與廢棄物三項 KPI。正例：『打造世界級綠色企業』但無定義。

AI evidence fields：

vague_claims, defined_terms, scope_definition, measurable_link, vague_claim_count

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若報告環境章節很短、樣本不足，NA。

跨年度比較原則：

比較抽象語句比例是否逐年增加。

VAG2　「提升、積極、持續」等語句缺乏 KPI 支持

操作型定義：

衡量具有方向性但無量化支持的動詞或形容詞是否被頻繁用於重大環境主張。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 方向性語句幾乎都有 KPI 支持。 |

| 1 | 少數無 KPI。 |

| 2 | 約半數有 KPI 支持。 |

| 3 | 多數方向性語句無 KPI。 |

| 4 | 大量使用提升／積極／持續等詞但無績效資料。 |



正反例：

反例：『持續降低排放』後緊接三年排放趨勢。正例：『持續提升能源效率』無任何能源效率 KPI。

AI evidence fields：

directional_terms, supported_by_kpi, linked_metric, support_ratio

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若該語句僅是章節標題或一般政策用語，不納入計分。

跨年度比較原則：

比較 KPI support ratio 跨年變化。

VAG3　環境效益使用模糊或無法驗證的描述

操作型定義：

衡量公司是否使用『環保、低碳、綠色、友善、永續』等效益詞，但未說明衡量依據。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 效益詞均有定義或證據。 |

| 1 | 少數模糊效益詞。 |

| 2 | 部分重要效益描述不可驗證。 |

| 3 | 多數效益宣稱模糊。 |

| 4 | 主要環境優勢都建立在不可驗證描述上。 |



正反例：

反例：『低碳產品』定義為產品碳足跡較基準產品低 30%。正例：『綠色產品占比提升』但綠色產品定義不明。

AI evidence fields：

benefit_terms, definition, verification_basis, certification, threshold

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若相關名詞已有法定／國際標準且報告清楚引用，可不扣分。

跨年度比較原則：

檢查公司是否跨年改變『綠色產品』定義以維持成長。

VAG4　關鍵宣稱缺乏明確範圍、時間或對象

操作型定義：

衡量重大環境宣稱是否清楚回答 where / when / what / whom。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 主要宣稱的範圍、期間、對象清楚。 |

| 1 | 少數細節缺漏。 |

| 2 | 部分宣稱邊界模糊。 |

| 3 | 多數宣稱缺乏範圍或時間。 |

| 4 | 主要宣稱幾乎無法知道適用對象與期間。 |



正反例：

反例：『2025 年台灣三座晶圓廠用水強度下降 8%。』正例：『今年公司大幅降低水資源使用』但無範圍。

AI evidence fields：

time_scope, entity_scope, facility_scope, population_scope, product_scope

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若宣稱本身為公司政策總則，非績效主張，可 NA。

跨年度比較原則：

比較相同宣稱的範圍是否逐年縮小但文字仍維持整體性。

D7 Linguistic Impression-management Risk (LIR)

主要文獻基礎：Lagasio (2024); Gorovaia & Makrominas (2025)

LIR1　環境敘述呈現異常高度正向語氣

操作型定義：

衡量環境章節之正向語氣是否顯著高於其可觀察績效與負面資訊所支持的程度。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 語氣與績效大致一致。 |

| 1 | 略偏正向但有充分證據。 |

| 2 | 正向語氣明顯高於實際績效。 |

| 3 | 高度正向且負面績效存在。 |

| 4 | 極度宣傳性語氣與實際證據嚴重不一致。 |



正反例：

反例：正向敘述與持續改善 KPI 一致，並揭露惡化項目。正例：排放上升卻大量使用『卓越、領先、顯著成功』。

AI evidence fields：

sentiment_score, promotional_terms, performance_direction, negative_kpis, tone_performance_gap

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

沒有可比較績效資料時，不應單靠 tone 評分，原則上 NA。

跨年度比較原則：

比較 tone 與績效方向跨年是否分離。

LIR2　負面議題附近出現較高語言複雜度或模糊化

操作型定義：

衡量當公司說明環境惡化、事故、裁罰或未達標時，是否使用異常複雜、間接、被動或技術性敘述弱化責任。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 負面資訊直接清楚。 |

| 1 | 少量技術性語言但仍易理解。 |

| 2 | 部分負面段落明顯複雜。 |

| 3 | 多數負面資訊以高度間接方式表達。 |

| 4 | 負面事件幾乎被術語、被動語態或長句掩蓋。 |



正反例：

反例：『本年度因 X 事故遭裁罰 Y 元，原因為 Z，已完成改善。』正例：以數段複雜法規文字描述，卻不直接說明遭裁罰。

AI evidence fields：

negative_event, sentence_length, passive_voice, technical_density, directness, plain_language_summary

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若無負面事件或未達標事項，NA。

跨年度比較原則：

比較同類負面事件跨年的文字複雜度與直接性。

LIR3　大量 boilerplate 或重複性永續語言

操作型定義：

衡量本年度環境敘述是否大量沿用前期模板化文字，卻缺乏新增績效與具體更新。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 每年內容有實質更新。 |

| 1 | 少量模板文字。 |

| 2 | 重複內容明顯但仍有重要更新。 |

| 3 | 大部分文字與前期高度相似。 |

| 4 | 主要環境篇章幾乎複製前期，缺乏新資訊。 |



正反例：

反例：保留政策背景，但 KPI、專案與進度均更新。正例：連續三年同一段『致力於永續、積極減碳』幾乎逐字相同。

AI evidence fields：

text_similarity_prior_year, repeated_paragraphs, new_information_ratio, updated_kpis

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

沒有前期報告可比較時 NA。

跨年度比較原則：

建議至少比較前一年度；若有資料可計算 2–3 年文字相似度趨勢。

LIR4　大量正面環境內容可能造成 attention deflection

操作型定義：

衡量公司是否在存在重大負面環境事件或績效惡化時，大量增加其他正面環境敘事，轉移讀者注意。

0–4 分判定規則：


| 分數 | 判定規則 |

| --- | --- |

| 0 | 負面事件被直接且充分說明。 |

| 1 | 正面內容稍多但不影響負面資訊可見度。 |

| 2 | 存在一定程度注意力轉移。 |

| 3 | 負面事件附近大量插入無關正面案例。 |

| 4 | 重大負面議題被大量正面敘事淹沒。 |



正反例：

反例：先完整揭露事故，再另章節呈現其他成果。正例：裁罰事件僅一句，周圍數頁都是植樹、志工、綠色活動。

AI evidence fields：

negative_event_prominence, positive_content_volume, proximity_to_negative_event, topic_relevance, deflection_flag

頁碼與原文證據要求：

至少回傳 1 個支持目前分數的頁碼與原文摘錄；若存在相反證據，另回傳 counter_evidence_page 與 counter_evidence_quote。原文應保留足夠上下文，使人工 coder 可在 PDF 中重新定位並驗證判斷。

NA 規則：

若無重大負面事件／惡化績效，NA。

跨年度比較原則：

比較事件發生年度與前後年度正面內容量是否異常跳升。

五、LLM 自動評分標準流程


| 步驟 | LLM 任務 | 輸出 |

| --- | --- | --- |

| 1. Materiality screening | 辨識該公司之重大環境議題；避免對非重大議題機械扣分。 | material_topics |

| 2. Claim extraction | 抽取主要環境宣稱、目標、改善敘述與績效主張。 | claim_text / topic / scope |

| 3. Evidence matching | 搜尋與每個 claim 對應的行動、KPI、數據、結果、驗證。 | evidence fields |

| 4. Negative evidence search | 主動搜尋排放增加、目標未達、事故、裁罰、惡化 KPI。 | negative evidence |

| 5. Cross-year comparison | 對照前 1–3 年相同 KPI、目標與敘述。 | year_compare |

| 6. Item scoring | 依 28 題 rubric 分別評 0–4 或 NA。 | item scores |

| 7. Evidence audit | 每題附頁碼、原文、反證與 confidence。 | auditable output |

| 8. Dimension aggregation | 計算 7 構面平均分數。 | dimension scores |

| 9. Weighted AI-GWRI | 依權重轉為 0–100。 | AI-GWRI |



六、建議的結構化輸出格式

每一題建議輸出下列結構；正式實作時可轉為 JSON、CSV 或資料庫欄位：


| 欄位 | 範例 |

| --- | --- |

| item_code | CEG1 |

| score | 3 |

| confidence | High |

| materiality_status | Material |

| evidence_page | p. 46, p. 51 |

| evidence_quote | 『本公司持續推動低碳製造……』；未見對應專案或成果。 |

| counter_evidence_page | p. 63 |

| counter_evidence_quote | 『完成 A 廠空壓系統汰換……』 |

| reasoning_summary | 主要低碳宣稱多為原則性表述，僅少數單廠專案可直接支持，故評為 3。 |

| year_compare | Stable |

| missing_information | 缺少公司整體低碳製造專案清單與結果。 |



七、構面與總指標計算

每一構面先計算有效題項平均；NA 題不納入分母，但需另行計算 NA ratio。若某構面有效題少於 2 題，建議該構面標示為 Low Reliability，並避免直接計入總分，或於實證研究中進行敏感度分析。

AI-GWRI = 25(CEG/4) + 15(QEG/4) + 15(TAG/4) + 20(SDR/4) + 10(VRG/4) + 10(VAG/4) + 5(LIR/4)

建議同時保留：AI-GWRI、七構面分數、28 題原始分數、NA ratio、evidence coverage ratio、confidence distribution。這些欄位可用於後續信效度、穩健性與模型比較。

八、人工與 LLM 一致性檢驗建議

為建立 measurement reliability，建議抽取 10%–20% 報告由至少兩位人工 coder 與 LLM 分別評分。題項層級可使用 weighted kappa 或 Krippendorff's alpha；構面與總分可使用 ICC。若 LLM 與人工評分差異超過 1 分，應進行 adjudication 並修訂 codebook。

另外建議執行：不同 LLM、不同 temperature、不同 prompt、同一模型重複評分、不同報告年度的 robustness tests。若某題在多模型間一致性長期偏低，應考慮刪題、合併或改寫判準。

九、核心參考文獻

Delmas, M. A., & Burbano, V. C. (2011). The drivers of greenwashing. California Management Review, 54(1), 64–87. https://doi.org/10.1525/cmr.2011.54.1.64

de Freitas Netto, S. V., Sobral, M. F. F., Ribeiro, A. R. B., & Soares, G. R. L. (2020). Concepts and forms of greenwashing: A systematic review. Environmental Sciences Europe, 32, 19.

Walker, K., & Wan, F. (2012). The harm of symbolic actions and green-washing: Corporate actions and communications on environmental performance and their financial implications. Journal of Business Ethics, 109(2), 227–242. https://doi.org/10.1007/s10551-011-1122-4

Marquis, C., Toffel, M. W., & Zhou, Y. (2016). Scrutiny, norms, and selective disclosure: A global study of greenwashing. Organization Science, 27(2), 483–504. https://doi.org/10.1287/orsc.2015.1039

Michelon, G., Pilonato, S., & Ricceri, F. (2015). CSR reporting practices and the quality of disclosure: An empirical analysis. Critical Perspectives on Accounting, 33, 59–78.

Lagasio, V. (2024). ESG-washing detection in corporate sustainability reports. International Review of Financial Analysis, 96, 103742.

Gorovaia, N., & Makrominas, M. (2025). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31, 427–462. https://doi.org/10.1111/eufm.12509

Lublóy, Á., Keresztúri, J. L., & Berlinger, E. (2025). Quantifying firm-level greenwashing: A systematic literature review. Journal of Environmental Management, 373, 123399.

十、AI-GWRI 公司年度總評分表

本表用於彙整單一公司—年度之 28 題評分結果。每題填入 0–4 或 NA；各構面以有效題項平均計算，再依權重轉換為加權分數。建議同時保留 NA 數量與 evidence coverage，以避免總分掩蓋資料不足問題。


| 公司名稱 | ＿＿＿＿＿＿＿＿ | 報告年度 | ＿＿＿＿年 |

| --- | --- | --- | --- |

| 評分模型／版本 | ＿＿＿＿＿＿＿＿ | 評分日期 | ＿＿＿＿＿＿＿＿ |




| 構面 | 題項1 | 題項2 | 題項3 | 題項4 | 構面平均 0–4 | 權重 | 加權分數 0–權重 | NA數 |

| --- | --- | --- | --- | --- | --- | --- | --- | --- |

| CEG | CEG1 | CEG2 | CEG3 | CEG4 |  | 25% |  |  |

| QEG | QEG1 | QEG2 | QEG3 | QEG4 |  | 15% |  |  |

| TAG | TAG1 | TAG2 | TAG3 | TAG4 |  | 15% |  |  |

| SDR | SDR1 | SDR2 | SDR3 | SDR4 |  | 20% |  |  |

| VRG | VRG1 | VRG2 | VRG3 | VRG4 |  | 10% |  |  |

| VAG | VAG1 | VAG2 | VAG3 | VAG4 |  | 10% |  |  |

| LIR | LIR1 | LIR2 | LIR3 | LIR4 |  | 5% |  |  |

| 總計 |  |  |  |  |  | 100% | AI-GWRI = ____ / 100 | ____ |



總分計算

AI-GWRI = 25(CEG/4) + 15(QEG/4) + 15(TAG/4) + 20(SDR/4) + 10(VRG/4) + 10(VAG/4) + 5(LIR/4)

評分品質檢查


| 檢查項目 | 結果 |

| --- | --- |

| 有效評分題數 | ____ / 28 |

| NA 題數 | ____ / 28 |

| Evidence coverage ratio | ____ % |

| High-confidence 題數 | ____ / 28 |

| 具 counter-evidence 題數 | ____ / 28 |

| 跨年度可比較題數 | ____ / 28 |

| 總體資料品質 | □ High　□ Medium　□ Low |



總體判讀


| 項目 | 填寫內容 |

| --- | --- |

| AI-GWRI 總分 | ____ / 100 |

| 最高風險構面 | ________________________ |

| 次高風險構面 | ________________________ |

| 主要風險證據 | ____________________________________________________________ |

| 主要反向證據 | ____________________________________________________________ |

| 跨年度趨勢 | □ Improved　□ Stable　□ Deteriorated　□ NA |

| 最終判讀 | 本分數代表永續報告書所呈現之漂綠風險，不等同於已確認之漂綠事件。 |

