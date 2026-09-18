"""
AI-GWRI 評估手冊完整 28 題項與 7 大構面定義常數
依據 codebook.md (AI-GWRI Codebook Version 1.0) 建立
"""
from typing import Dict, List, Any

DIMENSIONS_META: Dict[str, Dict[str, Any]] = {
    "CEG": {
        "code": "CEG",
        "name": "Claim–Evidence Gap (主張—證據落差)",
        "weight": 0.25,
        "literature": "Walker & Wan (2012); Lublóy et al. (2025)",
        "description": "衡量重大環境主張是否有具體行動、執行機制、實質措施與直接結果數據支持。"
    },
    "QEG": {
        "code": "QEG",
        "name": "Quantification & Performance Evidence Gap (量化與績效落差)",
        "weight": 0.15,
        "literature": "Marquis et al. (2016); Michelon et al. (2015); Lublóy et al. (2025)",
        "description": "衡量重大環境主張是否具備量化數據、明確基準年/值、跨年度可比性與清晰的範疇/母數。"
    },
    "TAG": {
        "code": "TAG",
        "name": "Target–Achievement Gap (目標—達成落差)",
        "weight": 0.15,
        "literature": "Walker & Wan (2012); Lublóy et al. (2025)",
        "description": "衡量長期目標是否有具體期限、短中期里程碑、當年度進度追蹤及未達標檢討。"
    },
    "SDR": {
        "code": "SDR",
        "name": "Selective Disclosure Risk (選擇性揭露風險)",
        "weight": 0.2,
        "literature": "Marquis et al. (2016); de Freitas Netto et al. (2020); Lublóy et al. (2025)",
        "description": "衡量是否存在報喜不報憂、負面變動隱匿、關鍵排放污染缺口及以局部改善混淆整體。"
    },
    "VRG": {
        "code": "VRG",
        "name": "Verification & Reliability Gap (驗證與可信度落差)",
        "weight": 0.1,
        "literature": "Michelon et al. (2015); Gorovaia & Makrominas (2025)",
        "description": "衡量重大環境數據是否經過第三方獨立查證、查證涵蓋範疇、計算方法透明度與數據可追溯性。"
    },
    "VAG": {
        "code": "VAG",
        "name": "Vagueness & Ambiguity Gap (模糊性與空泛性落差)",
        "weight": 0.1,
        "literature": "de Freitas Netto et al. (2020); Michelon et al. (2015)",
        "description": "衡量是否濫用抽象願景詞、缺乏KPI支持的方向性動詞、無法驗證的效益詞與缺乏人事實地範圍之宣稱。"
    },
    "LIR": {
        "code": "LIR",
        "name": "Linguistic Impression-management Risk (語言印象管理風險)",
        "weight": 0.05,
        "literature": "Lagasio (2024); Gorovaia & Makrominas (2025)",
        "description": "衡量環境敘述是否存在異常誇飾正向語氣、負面議題語意複雜化/被動模糊化、大量公版套話及轉移焦點行為。"
    }
}

CODEBOOK_ITEMS: Dict[str, Dict[str, Any]] = {
    "CEG1": {
        "code": "CEG1",
        "dimension": "CEG",
        "title": "重要環境宣稱缺乏具體行動證據",
        "definition": "衡量公司提出重大環境主張後，是否能在同一報告年度找到直接對應的具體行動、專案、制度或執行措施。",
        "rubric": {
            "0": "每個主要宣稱均能找到清楚且具體的行動證據。",
            "1": "大多數主要宣稱有行動支持，少數次要宣稱較抽象。",
            "2": "部分主要宣稱有行動支持，部分僅停留在承諾。",
            "3": "多數主要宣稱缺乏具體行動支持。",
            "4": "幾乎所有主要宣稱均只有口號或原則性描述。"
        },
        "examples": "反例（低風險）：『2025 年完成 3 座廠房能源管理系統建置，投資新台幣 X 億元。』正例（高風險）：『本公司持續深化低碳營運，積極落實節能減碳。』但無任何專案或措施。",
        "na_rule": "若找不到主要環境宣稱，且報告整體環境資訊極少：不要直接給 0，應依 materiality 判斷；若無法判斷則 NA。",
        "cross_year_rule": "比較同一主題上一年度是否只有承諾、本年度是否新增具體行動。若新增行動，year_compare=Improved。"
    },
    "CEG2": {
        "code": "CEG2",
        "dimension": "CEG",
        "title": "宣稱之環境改善缺乏實際執行專案或措施",
        "definition": "衡量公司聲稱『改善、降低、提升』時，是否揭露造成該改善的具體執行機制，而非只報告結果或口號。",
        "rubric": {
            "0": "改善結果與執行措施有直接對應。",
            "1": "多數改善有措施說明，細節略不足。",
            "2": "只有部分改善能對應措施。",
            "3": "多數改善聲稱無法找到對應措施。",
            "4": "大量改善性語句完全無執行內容。"
        },
        "examples": "反例：『更換 1,200 台高效率馬達，使用電量下降 8.4%。』正例：『能源效率顯著提升。』但未說明任何措施。",
        "na_rule": "若僅有績效數據但無改善性宣稱，本題可 NA；不要因沒有『改善』字樣扣分。",
        "cross_year_rule": "跨年檢查改善措施是否持續存在，以及今年的績效是否與措施方向一致。"
    },
    "CEG3": {
        "code": "CEG3",
        "dimension": "CEG",
        "title": "Symbolic commitment 明顯多於 substantive action",
        "definition": "衡量報告中象徵性承諾、價值宣示與願景文字，相對於可驗證實質行動的比例與落差。",
        "rubric": {
            "0": "承諾與實質行動大致平衡。",
            "1": "象徵性文字略多，但實質行動充分。",
            "2": "象徵性與實質內容約各半。",
            "3": "象徵性內容明顯多於實質行動。",
            "4": "主要環境篇章幾乎以願景、承諾、口號構成。"
        },
        "examples": "反例：每項願景後均列專案、KPI、預算與成果。正例：大量『致力、持續、深化、領先、打造綠色未來』，但缺少行動與結果。",
        "na_rule": "若報告內容過短、無法穩定計算 symbolic/substantive 比例，標示 NA。",
        "cross_year_rule": "比較 symbolic/substantive 比例是否逐年上升；若承諾增加但實質行動未同步增加，視為 Deteriorated。"
    },
    "CEG4": {
        "code": "CEG4",
        "dimension": "CEG",
        "title": "宣稱與提供之結果證據無法建立直接對應",
        "definition": "衡量公司提出環境宣稱後，報告中的成果數據是否能直接支持該宣稱，而非使用不同範圍、不同口徑或無關績效佐證。",
        "rubric": {
            "0": "宣稱與結果一一對應，範圍與口徑一致。",
            "1": "少數範圍或口徑差異，但不影響結論。",
            "2": "部分宣稱只能由間接結果支持。",
            "3": "多數宣稱與成果數據對應弱。",
            "4": "宣稱與提供的結果幾乎無可辨識關聯。"
        },
        "examples": "反例：宣稱『降低 Scope 2』，並提供同範圍 Scope 2 年度下降資料。正例：宣稱『整體碳排下降』，卻只提供單一廠區節電量。",
        "na_rule": "若無結果性宣稱或無可比結果，依議題重要性判斷；無合理基礎時 NA。",
        "cross_year_rule": "檢查公司是否跨年改變範圍、口徑或母數，導致宣稱與結果不可比。"
    },
    "QEG1": {
        "code": "QEG1",
        "dimension": "QEG",
        "title": "重要環境宣稱缺乏量化數據",
        "definition": "衡量重大環境宣稱是否附有可量化數據，而非只以定性文字描述。",
        "rubric": {
            "0": "主要宣稱均有量化數據。",
            "1": "少數次要宣稱缺乏數據。",
            "2": "約半數主要宣稱有數據。",
            "3": "多數主要宣稱只有定性描述。",
            "4": "幾乎沒有量化支持。"
        },
        "examples": "反例：『用水強度下降 12.3%，至 0.45 m³/千元營收。』正例：『持續降低用水量』但無數值。",
        "na_rule": "若該宣稱本質上無法合理量化，則不應扣分，可 NA 或排除該 claim。",
        "cross_year_rule": "比較同一主題量化資訊是否增加；由定性轉為定量視為 Improved。"
    },
    "QEG2": {
        "code": "QEG2",
        "dimension": "QEG",
        "title": "缺乏基準年或基準值",
        "definition": "衡量績效與減量目標是否提供明確基準年或基準值，讓外部讀者能判斷改善幅度。",
        "rubric": {
            "0": "主要目標與改善宣稱均有明確基準。",
            "1": "少數次要項目缺基準。",
            "2": "部分重要項目無基準。",
            "3": "多數改善性主張缺基準。",
            "4": "幾乎所有相對改善主張均無基準。"
        },
        "examples": "反例：『以 2020 年為基準，2030 年 Scope 1+2 減量 42%。』正例：『2030 年大幅減碳』但無基準年。",
        "na_rule": "若該數據是絕對值揭露而非『改善／減量目標』，不必強制要求基準，可 NA。",
        "cross_year_rule": "檢查基準年是否跨年任意變更；如變更，必須揭露理由與重算。"
    },
    "QEG3": {
        "code": "QEG3",
        "dimension": "QEG",
        "title": "缺乏跨年度可比較資料",
        "definition": "衡量主要環境 KPI 是否至少提供兩期以上可比較數據，或清楚說明無法比較的原因。",
        "rubric": {
            "0": "主要 KPI 有 3 年以上一致口徑資料。",
            "1": "大多數 KPI 有至少 2 年資料。",
            "2": "部分 KPI 可比較。",
            "3": "多數 KPI 僅單年值。",
            "4": "幾乎無跨年可比資料。"
        },
        "examples": "反例：表列 2023–2025 排放、能源、水與廢棄物。正例：只提供 2025 單年數據，卻宣稱『持續改善』。",
        "na_rule": "新成立公司、新指標首次採用或法規首次要求揭露時，可 NA 或降低評分，但要記錄原因。",
        "cross_year_rule": "優先比較連續三年；若口徑變更，記錄是否有重編前期資料。"
    },
    "QEG4": {
        "code": "QEG4",
        "dimension": "QEG",
        "title": "數據範圍、coverage 或 denominator 不清楚",
        "definition": "衡量環境數據是否清楚說明涵蓋公司、子公司、廠區、地區、營運邊界，以及強度指標的母數。",
        "rubric": {
            "0": "範圍、coverage 與 denominator 完整。",
            "1": "有少量邊界細節不清。",
            "2": "部分重要數據範圍或母數不清。",
            "3": "多數重要數據缺乏範圍說明。",
            "4": "數據無法判斷代表公司整體或局部。"
        },
        "examples": "反例：『涵蓋全球 95% 營收之營運據點；強度以百萬元營收為母數。』正例：『碳排強度下降 15%』但不知母數或涵蓋哪些廠。",
        "na_rule": "若該數據本身不需 denominator，則 denominator 可不適用；但 coverage 還是要判斷。",
        "cross_year_rule": "檢查 coverage 是否跨年擴大或縮小，以及公司是否說明對趨勢的影響。"
    },
    "TAG1": {
        "code": "TAG1",
        "dimension": "TAG",
        "title": "長期環境目標缺乏明確期限",
        "definition": "衡量環境承諾是否具有明確 target year 或完成期限。",
        "rubric": {
            "0": "所有重大目標均有期限。",
            "1": "少數次要目標無期限。",
            "2": "部分重大目標只有模糊時間。",
            "3": "多數重大目標沒有明確期限。",
            "4": "目標幾乎都是無期限願景。"
        },
        "examples": "反例：『2030 年再生能源使用比例達 60%。』正例：『持續提升再生能源使用比例。』",
        "na_rule": "若內容只是政策原則而非目標，不應強迫評分，可 NA。",
        "cross_year_rule": "比較過去無期限承諾是否轉為具體期限。"
    },
    "TAG2": {
        "code": "TAG2",
        "dimension": "TAG",
        "title": "目標缺乏短中期 milestones",
        "definition": "衡量長期目標是否拆解為可追蹤的中間里程碑。",
        "rubric": {
            "0": "長期目標有清楚年度／階段性 milestones。",
            "1": "大多數目標有里程碑。",
            "2": "部分有、部分無。",
            "3": "長期目標多數沒有中期節點。",
            "4": "只存在遠期目標，完全沒有中間路徑。"
        },
        "examples": "反例：2030 目標搭配 2026、2028 階段目標。正例：只寫『2050 淨零』。",
        "na_rule": "若目標期限短於 2 年，可不要求 milestones，標示 NA。",
        "cross_year_rule": "跨年確認 milestones 是否按期更新，避免公司每年延後。"
    },
    "TAG3": {
        "code": "TAG3",
        "dimension": "TAG",
        "title": "過去承諾缺乏當年度進度追蹤",
        "definition": "衡量前期已提出的重要目標，在本年度是否揭露目前進度。",
        "rubric": {
            "0": "重大前期目標均有進度與差距說明。",
            "1": "少數次要目標未更新。",
            "2": "約半數重要目標有進度。",
            "3": "多數前期承諾未追蹤。",
            "4": "過去目標在本年度幾乎消失。"
        },
        "examples": "反例：『2030 減量 42%，截至 2025 已達 18%，進度符合路徑。』正例：2023 報告曾承諾目標，2025 報告完全不再提。",
        "na_rule": "首次報告或首次設定目標時 NA。",
        "cross_year_rule": "必須至少對照前一年度；重要長期目標建議回看 2–3 年。"
    },
    "TAG4": {
        "code": "TAG4",
        "dimension": "TAG",
        "title": "未達標目標未充分揭露或說明",
        "definition": "衡量公司在目標未達、落後或惡化時，是否坦誠揭露原因、差距與改善措施。",
        "rubric": {
            "0": "未達標事項清楚揭露並解釋。",
            "1": "大致揭露，改善計畫略少。",
            "2": "有揭露但解釋有限。",
            "3": "未達標被弱化或只模糊帶過。",
            "4": "明顯存在未達標跡象但報告完全不說明。"
        },
        "examples": "反例：『因新廠投產，排放較目標高 9%；已調整 2026 設備汰換計畫。』正例：指標惡化但正文只強調其他改善成果。",
        "na_rule": "若當年度無任何目標未達或無法辨識是否未達，NA。",
        "cross_year_rule": "跨年檢查未達標事項是否在次年被刪除或改寫目標。"
    },
    "SDR1": {
        "code": "SDR1",
        "dimension": "SDR",
        "title": "正面環境成果明顯比負面成果更突出",
        "definition": "衡量報告對正面與負面環境績效是否存在明顯呈現不對稱，包括篇幅、標題、圖表與敘述強度。",
        "rubric": {
            "0": "正負資訊揭露平衡。",
            "1": "略偏正面但負面資訊仍清楚。",
            "2": "正面內容較突出，負面內容較簡略。",
            "3": "負面資訊明顯弱化。",
            "4": "整體呈現幾乎只剩正面成果。"
        },
        "examples": "反例：同時揭露改善與惡化 KPI 並說明原因。正例：首頁大幅宣傳節能成果，排放增加僅藏於附表。",
        "na_rule": "若本年度所有重大指標確實均改善，不能因缺乏負面資訊扣分；需查核跨年數據後判斷。",
        "cross_year_rule": "比較各年負面資訊的篇幅與可見度是否異常下降。"
    },
    "SDR2": {
        "code": "SDR2",
        "dimension": "SDR",
        "title": "重大負面環境變動未充分說明",
        "definition": "衡量重要環境 KPI 惡化時，公司是否提供原因、影響與改善措施。",
        "rubric": {
            "0": "所有重大惡化均有充分解釋。",
            "1": "少數惡化解釋不足。",
            "2": "約半數惡化有說明。",
            "3": "多數重大惡化未說明。",
            "4": "重大惡化被完全忽略或刻意弱化。"
        },
        "examples": "反例：能源使用增加並解釋新廠投產與後續改善計畫。正例：用水增加 35% 但正文無解釋。",
        "na_rule": "若無重大負面變動，NA。",
        "cross_year_rule": "至少比較前一年度；若公司跨年變更口徑，需排除口徑變動造成的假性惡化。"
    },
    "SDR3": {
        "code": "SDR3",
        "dimension": "SDR",
        "title": "重要排放、污染或資源指標存在揭露缺口",
        "definition": "衡量與公司重大環境議題相關的核心 KPI 是否缺漏，包括 Scope 1–3、能源、水、廢棄物、污染排放等。",
        "rubric": {
            "0": "重大議題核心 KPI 完整。",
            "1": "僅少數次要 KPI 缺漏。",
            "2": "至少一項重要 KPI 缺漏或部分揭露。",
            "3": "多項重要 KPI 缺漏。",
            "4": "核心重大環境議題幾乎未量化揭露。"
        },
        "examples": "反例：對公司重大議題提供完整 GHG、能源、水與廢棄物資料。正例：高碳排產業完全不揭露 Scope 1–2，卻大量強調公益植樹。",
        "na_rule": "若該 KPI 對該產業明確不具重大性，應標示 Non-material 並 NA，不可機械式扣分。",
        "cross_year_rule": "追蹤同一 KPI 是否突然消失；若前期有揭露、今年取消且無解釋，風險上升。"
    },
    "SDR4": {
        "code": "SDR4",
        "dimension": "SDR",
        "title": "使用局部改善形成整體環境改善印象",
        "definition": "衡量公司是否以單一廠區、單一專案或小範圍成果，暗示公司整體環境績效改善。",
        "rubric": {
            "0": "局部與整體範圍標示清楚。",
            "1": "少數敘述略有泛化。",
            "2": "部分局部成果被放大。",
            "3": "多數正面敘述以局部資料代表整體。",
            "4": "高度依賴小範圍案例製造整體改善印象。"
        },
        "examples": "反例：明確標示『僅適用台中廠，占總產量 12%』。正例：以單一示範廠減排 20% 宣稱『公司減碳成效卓越』。",
        "na_rule": "若企業只有單一營運據點，局部／整體問題不適用，可 NA。",
        "cross_year_rule": "檢查正面案例 coverage 是否逐年下降但宣稱仍保持整體化。"
    },
    "VRG1": {
        "code": "VRG1",
        "dimension": "VRG",
        "title": "重大環境 KPI 缺乏第三方驗證",
        "definition": "衡量重大環境數據是否經外部 assurance／verification，尤其是溫室氣體與關鍵 KPI。",
        "rubric": {
            "0": "重大 KPI 多數經外部驗證。",
            "1": "主要 KPI 有驗證，少數未涵蓋。",
            "2": "僅部分重大 KPI 驗證。",
            "3": "大多數重大 KPI 未驗證。",
            "4": "完全無第三方驗證且公司仍高度依賴自我宣稱。"
        },
        "examples": "反例：Scope 1–2 與主要水／能源數據經第三方查證。正例：報告大量強調減碳成果，但無任何 assurance／verification。",
        "na_rule": "若法規或產業慣例對某 KPI 尚無合理第三方驗證方式，可 NA 或降低重要性。",
        "cross_year_rule": "比較驗證範圍是否逐年擴大或縮小。"
    },
    "VRG2": {
        "code": "VRG2",
        "dimension": "VRG",
        "title": "Assurance coverage 不明或有限",
        "definition": "衡量 assurance 是否清楚說明涵蓋哪些章節、公司範圍、KPI 與 assurance level。",
        "rubric": {
            "0": "coverage 與 assurance level 完整清楚。",
            "1": "少量細節不清。",
            "2": "僅列部分涵蓋範圍。",
            "3": "coverage 非常有限或模糊。",
            "4": "只宣稱『經查證』但完全無法知道查證什麼。"
        },
        "examples": "反例：附 assurance statement，明列 KPI、範圍與 limited/reasonable assurance。正例：只放查證機構 logo。",
        "na_rule": "若完全無 assurance，VRG1 可評分；VRG2 原則上 NA，避免重複處罰。",
        "cross_year_rule": "跨年檢查 assurance coverage 是否縮減而未說明。"
    },
    "VRG3": {
        "code": "VRG3",
        "dimension": "VRG",
        "title": "宣稱之資料來源或計算方法不透明",
        "definition": "衡量重要環境數據是否說明計算標準、方法、排放係數、資料來源或估計方式。",
        "rubric": {
            "0": "方法與來源完整。",
            "1": "少量細節缺漏。",
            "2": "部分 KPI 方法不清。",
            "3": "多數 KPI 缺乏方法說明。",
            "4": "幾乎無法重現或理解數據如何計算。"
        },
        "examples": "反例：說明 GHG Protocol、排放係數來源與估算方式。正例：只列『減碳 12%』，完全無方法。",
        "na_rule": "若數據為簡單直接量測且方法無重大歧義，可降低要求；仍應有來源。",
        "cross_year_rule": "檢查方法是否跨年變更及是否揭露重算。"
    },
    "VRG4": {
        "code": "VRG4",
        "dimension": "VRG",
        "title": "重要環境數據缺乏可追溯性",
        "definition": "衡量外部讀者是否能從報告附錄、索引、查證聲明或資料表追溯到環境 KPI 的來源與範圍。",
        "rubric": {
            "0": "主要 KPI 可完整追溯。",
            "1": "少數 KPI 追溯較困難。",
            "2": "約半數 KPI 可追溯。",
            "3": "多數 KPI 無明確來源鏈。",
            "4": "幾乎所有重要數據都是孤立數字。"
        },
        "examples": "反例：KPI 表列來源章節、查證範圍與計算註記。正例：圖表數字沒有來源、範圍或附註。",
        "na_rule": "若報告本身結構嚴重損壞導致頁碼或表格不可辨識，NA。",
        "cross_year_rule": "跨年檢查同一 KPI 的定義與表格位置是否一致；不一致時需確認是否為定義變更。"
    },
    "VAG1": {
        "code": "VAG1",
        "dimension": "VAG",
        "title": "大量使用抽象環境承諾而無具體定義",
        "definition": "衡量企業是否大量使用願景式環境承諾，卻沒有界定其意義、範圍或可衡量結果。",
        "rubric": {
            "0": "抽象承諾少，且均有具體化。",
            "1": "有少量抽象語言但不影響判斷。",
            "2": "抽象與具體內容約各半。",
            "3": "多數環境敘述偏抽象。",
            "4": "主要環境敘事幾乎都是不可驗證承諾。"
        },
        "examples": "反例：『綠色製造』明確定義為能源、排放與廢棄物三項 KPI。正例：『打造世界級綠色企業』但無定義。",
        "na_rule": "若報告環境章節很短、樣本不足，NA。",
        "cross_year_rule": "比較抽象語句比例是否逐年增加。"
    },
    "VAG2": {
        "code": "VAG2",
        "dimension": "VAG",
        "title": "「提升、積極、持續」等語句缺乏 KPI 支持",
        "definition": "衡量具有方向性但無量化支持的動詞或形容詞是否被頻繁用於重大環境主張。",
        "rubric": {
            "0": "方向性語句幾乎都有 KPI 支持。",
            "1": "少數無 KPI。",
            "2": "約半數有 KPI 支持。",
            "3": "多數方向性語句無 KPI。",
            "4": "大量使用提升／積極／持續等詞但無績效資料。"
        },
        "examples": "反例：『持續降低排放』後緊接三年排放趨勢。正例：『持續提升能源效率』無任何能源效率 KPI。",
        "na_rule": "若該語句僅是章節標題或一般政策用語，不納入計分。",
        "cross_year_rule": "比較 KPI support ratio 跨年變化。"
    },
    "VAG3": {
        "code": "VAG3",
        "dimension": "VAG",
        "title": "環境效益使用模糊或無法驗證的描述",
        "definition": "衡量公司是否使用『環保、低碳、綠色、友善、永續』等效益詞，但未說明衡量依據。",
        "rubric": {
            "0": "效益詞均有定義或證據。",
            "1": "少數模糊效益詞。",
            "2": "部分重要效益描述不可驗證。",
            "3": "多數效益宣稱模糊。",
            "4": "主要環境優勢都建立在不可驗證描述上。"
        },
        "examples": "反例：『低碳產品』定義為產品碳足跡較基準產品低 30%。正例：『綠色產品占比提升』但綠色產品定義不明。",
        "na_rule": "若相關名詞已有法定／國際標準且報告清楚引用，可不扣分。",
        "cross_year_rule": "檢查公司是否跨年改變『綠色產品』定義以維持成長。"
    },
    "VAG4": {
        "code": "VAG4",
        "dimension": "VAG",
        "title": "關鍵宣稱缺乏明確範圍、時間或對象",
        "definition": "衡量重大環境宣稱是否清楚回答 where / when / what / whom。",
        "rubric": {
            "0": "主要宣稱的範圍、期間、對象清楚。",
            "1": "少數細節缺漏。",
            "2": "部分宣稱邊界模糊。",
            "3": "多數宣稱缺乏範圍或時間。",
            "4": "主要宣稱幾乎無法知道適用對象與期間。"
        },
        "examples": "反例：『2025 年台灣三座晶圓廠用水強度下降 8%。』正例：『今年公司大幅降低水資源使用』但無範圍。",
        "na_rule": "若宣稱本身為公司政策總則，非績效主張，可 NA。",
        "cross_year_rule": "比較相同宣稱的範圍是否逐年縮小但文字仍維持整體性。"
    },
    "LIR1": {
        "code": "LIR1",
        "dimension": "LIR",
        "title": "環境敘述呈現異常高度正向語氣",
        "definition": "衡量環境章節之正向語氣是否顯著高於其可觀察績效與負面資訊所支持的程度。",
        "rubric": {
            "0": "語氣與績效大致一致。",
            "1": "略偏正向但有充分證據。",
            "2": "正向語氣明顯高於實際績效。",
            "3": "高度正向且負面績效存在。",
            "4": "極度宣傳性語氣與實際證據嚴重不一致。"
        },
        "examples": "反例：正向敘述與持續改善 KPI 一致，並揭露惡化項目。正例：排放上升卻大量使用『卓越、領先、顯著成功』。",
        "na_rule": "沒有可比較績效資料時，不應單靠 tone 評分，原則上 NA。",
        "cross_year_rule": "比較 tone 與績效方向跨年是否分離。"
    },
    "LIR2": {
        "code": "LIR2",
        "dimension": "LIR",
        "title": "負面議題附近出現較高語言複雜度或模糊化",
        "definition": "衡量當公司說明環境惡化、事故、裁罰或未達標時，是否使用異常複雜、間接、被動或技術性敘述弱化責任。",
        "rubric": {
            "0": "負面資訊直接清楚。",
            "1": "少量技術性語言但仍易理解。",
            "2": "部分負面段落明顯複雜。",
            "3": "多數負面資訊以高度間接方式表達。",
            "4": "負面事件幾乎被術語、被動語態或長句掩蓋。"
        },
        "examples": "反例：『本年度因 X 事故遭裁罰 Y 元，原因為 Z，已完成改善。』正例：以數段複雜法規文字描述，卻不直接說明遭裁罰。",
        "na_rule": "若無負面事件或未達標事項，NA。",
        "cross_year_rule": "比較同類負面事件跨年的文字複雜度與直接性。"
    },
    "LIR3": {
        "code": "LIR3",
        "dimension": "LIR",
        "title": "大量 boilerplate 或重複性永續語言",
        "definition": "衡量本年度環境敘述是否大量沿用前期模板化文字，卻缺乏新增績效與具體更新。",
        "rubric": {
            "0": "每年內容有實質更新。",
            "1": "少量模板文字。",
            "2": "重複內容明顯但仍有重要更新。",
            "3": "大部分文字與前期高度相似。",
            "4": "主要環境篇章幾乎複製前期，缺乏新資訊。"
        },
        "examples": "反例：保留政策背景，但 KPI、專案與進度均更新。正例：連續三年同一段『致力於永續、積極減碳』幾乎逐字相同。",
        "na_rule": "沒有前期報告可比較時 NA。",
        "cross_year_rule": "建議至少比較前一年度；若有資料可計算 2–3 年文字相似度趨勢。"
    },
    "LIR4": {
        "code": "LIR4",
        "dimension": "LIR",
        "title": "大量正面環境內容可能造成 attention deflection",
        "definition": "衡量公司是否在存在重大負面環境事件或績效惡化時，大量增加其他正面環境敘事，轉移讀者注意。",
        "rubric": {
            "0": "負面事件被直接且充分說明。",
            "1": "正面內容稍多但不影響負面資訊可見度。",
            "2": "存在一定程度注意力轉移。",
            "3": "負面事件附近大量插入無關正面案例。",
            "4": "重大負面議題被大量正面敘事淹沒。"
        },
        "examples": "反例：先完整揭露事故，再另章節呈現其他成果。正例：裁罰事件僅一句，周圍數頁都是植樹、志工、綠色活動。",
        "na_rule": "若無重大負面事件／惡化績效，NA。",
        "cross_year_rule": "比較事件發生年度與前後年度正面內容量是否異常跳升。"
    }
}


def get_dimension_items(dimension_code: str) -> List[Dict[str, Any]]:
    """取得特定構面下的所有 4 個題項"""
    return [it for it in CODEBOOK_ITEMS.values() if it["dimension"] == dimension_code]

def build_dimension_scoring_prompt(dimension_code: str) -> str:
    """為特定構面建構完整的 LLM 評分 Prompt 說明"""
    dim = DIMENSIONS_META.get(dimension_code, {})
    items = get_dimension_items(dimension_code)
    
    lines = [
        f"=== 構面評估任務: {dim.get('name', dimension_code)} (權重: {int(dim.get('weight', 0)*100)}%) ===",
        f"文獻依據: {dim.get('literature', '')}",
        f"構面核心概念: {dim.get('description', '')}",
        "",
        "請依據提供的 PDF 永續報告書內容（已標註實體頁碼 [PDF Page X]），對該構面下的 4 個題項逐一進行客觀、可審核的嚴謹評分：",
        ""
    ]
    for it in items:
        lines.append("-" * 75)
        lines.append(f"【題項代碼】: {it['code']} - {it['title']}")
        lines.append(f"【操作型定義】: {it['definition']}")
        lines.append("【0-4 分判定規則】:")
        lines.append(f"  - 0分 (無明顯風險): {it['rubric'].get('0', '證據完整可信')}")
        lines.append(f"  - 1分 (低風險): {it['rubric'].get('1', '大致完整，僅有次要資訊缺口')}")
        lines.append(f"  - 2分 (中度風險): {it['rubric'].get('2', '存在明顯資訊缺口或部分停留在口號')}")
        lines.append(f"  - 3分 (高風險): {it['rubric'].get('3', '多數重要宣稱缺乏充分實質證據')}")
        lines.append(f"  - 4分 (極高風險): {it['rubric'].get('4', '宣稱與證據嚴重脫節，幾乎完全缺乏實質支持')}")
        lines.append(f"【正反範例】: {it['examples']}")
        lines.append(f"【NA 規則】: {it['na_rule']} (注意：若資訊不足或非公司重大議題，請將 score 設為 null 代表 NA；切勿因為報告沒寫就給 0 分)")
        lines.append(f"【跨年度比較原則】: {it['cross_year_rule']}")
        lines.append("")
        
    lines.append("-" * 75)
    lines.append("【嚴格評分指引 (Strict Guidelines)】:")
    lines.append("1. 原則一：每一題的 evidence_page 必須為報告書中真實存在的 PDF 實體頁碼（整數清單），不可自行發明頁碼。")
    lines.append("2. 原則二：evidence_quote 必須為報告書中的真實文字摘錄（可供人工檢核原文）。")
    lines.append("3. 原則三：0分代表「有充分證據顯示低風險」，而非「報告沒寫」。若報告書根本未揭露或資訊不足以評估，請將 score 設為 null (NA)。")
    lines.append("4. 原則四：若存在與初步判斷相反的反向證據，必須填寫 counter_evidence_page 與 counter_evidence_quote。")
    lines.append("5. 原則五：reasoning_summary 須在 100-150 字內精準交代給分理由與證據落差。")
    
    return "\n".join(lines)
