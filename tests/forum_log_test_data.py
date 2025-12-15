"""
Forum log test data

Contains minimal examples of various log formats for testing log parsing functions in ForumEngine/monitor.py.
Covers log record examples for old format ([HH:MM:SS]) and new format (loguru default format).
"""

# ===== Old format (supports [HH:MM:SS]) =====

# Single-line JSON, old format
OLD_FORMAT_SINGLE_LINE_JSON = """[17:42:31] 2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {"paragraph_latest_state": "This is first summary content"}"""

# Multi-line JSON, old format
OLD_FORMAT_MULTILINE_JSON = [
    "[17:42:31] 2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
    "[17:42:31] \"paragraph_latest_state\": \"This is multiline\\nJSON content\"",
    "[17:42:31] }"
]

# Old format log containing FirstSummaryNode
OLD_FORMAT_FIRST_SUMMARY = """[17:42:31] 2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - FirstSummaryNode cleaned output: {"paragraph_latest_state": "first summary"}"""

# Old format log containing ReflectionSummaryNode
OLD_FORMAT_REFLECTION_SUMMARY = """[17:43:00] 2025-11-05 17:43:00.272 | INFO | InsightEngine.nodes.summary_node:process_output:296 - ReflectionSummaryNode cleaned output: {"updated_paragraph_latest_state": "reflection summary"}"""

# Old format, non-target node (should be ignored)
OLD_FORMAT_NON_TARGET = """[17:41:16] 2025-11-05 17:41:16.742 | INFO | InsightEngine.nodes.report_structure_node:run:52 - generating report structure for query"""


# ===== New format (loguru default format) =====

# Single-line JSON, new format
NEW_FORMAT_SINGLE_LINE_JSON = """2025-11-05 17:42:31.287 | INFO     | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {"paragraph_latest_state": "This is first summary content"}"""

# Multi-line JSON, new format
NEW_FORMAT_MULTILINE_JSON = [
    "2025-11-05 17:42:31.287 | INFO     | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
    "2025-11-05 17:42:31.288 | INFO     | InsightEngine.nodes.summary_node:process_output:132 - \"paragraph_latest_state\": \"This is multiline\\nJSON content\"",
    "2025-11-05 17:42:31.289 | INFO     | InsightEngine.nodes.summary_node:process_output:133 - }"
]

# New format log containing FirstSummaryNode
NEW_FORMAT_FIRST_SUMMARY = """2025-11-05 17:42:31.287 | INFO     | InsightEngine.nodes.summary_node:process_output:131 - FirstSummaryNode cleaned output: {"paragraph_latest_state": "first summary"}"""

# New format log containing ReflectionSummaryNode
NEW_FORMAT_REFLECTION_SUMMARY = """2025-11-05 17:43:00.272 | INFO     | InsightEngine.nodes.summary_node:process_output:296 - ReflectionSummaryNode cleaned output: {"updated_paragraph_latest_state": "reflection summary"}"""

# New format, non-target node (should be ignored)
NEW_FORMAT_NON_TARGET = """2025-11-05 17:41:16.742 | INFO     | InsightEngine.nodes.report_structure_node:run:52 - generating report structure for query: Luoyang Molybdenum expected stock price change"""

# New format, ForumEngine log
NEW_FORMAT_FORUM_ENGINE = """2025-11-05 22:31:09.964 | INFO     | ForumEngine.monitor:monitor_logs:457 - ForumEngine: forum creation in progress..."""


# ===== Complex JSON examples =====

# JSON containing updated_paragraph_latest_state (should prioritize extracting this)
COMPLEX_JSON_WITH_UPDATED = [
    "2025-11-05 17:43:00.272 | INFO     | InsightEngine.nodes.summary_node:process_output:296 - cleaned output: {",
    "2025-11-05 17:43:00.273 | INFO     | InsightEngine.nodes.summary_node:process_output:297 - \"updated_paragraph_latest_state\": \"## Key Findings (Updated Version)\\n1. This is updated content\"",
    "2025-11-05 17:43:00.274 | INFO     | InsightEngine.nodes.summary_node:process_output:298 - }"
]

# JSON with only paragraph_latest_state
COMPLEX_JSON_WITH_PARAGRAPH = [
    "2025-11-05 17:42:31.287 | INFO     | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
    "2025-11-05 17:42:31.288 | INFO     | InsightEngine.nodes.summary_node:process_output:132 - \"paragraph_latest_state\": \"## Key Findings Overview\\n1. This is first summary content\"",
    "2025-11-05 17:42:31.289 | INFO     | InsightEngine.nodes.summary_node:process_output:133 - }"
]

# JSON content containing newlines
COMPLEX_JSON_WITH_NEWLINES = [
    "[17:42:31] 2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
    "[17:42:31] \"paragraph_latest_state\": \"First line content\\nSecond line content\\nThird line content\"",
    "[17:42:31] }"
]

# ===== Edge cases =====

# Line not containing "cleaned output" (should be ignored)
LINE_WITHOUT_CLEAN_OUTPUT = """2025-11-05 17:42:31.287 | INFO     | InsightEngine.nodes.summary_node:process_output:131 - JSON parsing successful"""

# Line containing "cleaned output" but not in JSON format
LINE_WITH_CLEAN_OUTPUT_NOT_JSON = """2025-11-05 17:42:31.287 | INFO     | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: This is not JSON format content"""

# Empty line
EMPTY_LINE = ""

# Line with only timestamp
LINE_WITH_ONLY_TIMESTAMP_OLD = "[17:42:31]"
LINE_WITH_ONLY_TIMESTAMP_NEW = "2025-11-05 17:42:31.287 | INFO | module:function:1 -"

# Invalid JSON format
INVALID_JSON = [
    "2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
    "2025-11-05 17:42:31.288 | INFO | InsightEngine.nodes.summary_node:process_output:132 - \"paragraph_latest_state\": \"missing closing quote",
    "2025-11-05 17:42:31.289 | INFO | InsightEngine.nodes.summary_node:process_output:133 - }"
]

# ===== Mixed format (both old and new formats in the same batch of logs) =====
MIXED_FORMAT_LINES = [
    "[17:42:31] 2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
    "2025-11-05 17:42:31.288 | INFO     | InsightEngine.nodes.summary_node:process_output:132 - \"paragraph_latest_state\": \"mixed format content\"",
    "[17:42:31] }"
]

# ===== Actual production environment log examples =====

# QueryEngine reflection summary - multi-line JSON format
REAL_QUERY_ENGINE_REFLECTION = [
    "[10:56:04] 2025-11-06 10:56:04.759 | INFO     | QueryEngine.nodes.summary_node:process_output:302 - cleaned output: {",
    "[10:56:04] \"updated_paragraph_latest_state\": \"Luoyang Luanchuan Molybdenum Group Co., Ltd. (abbreviated as Luoyang Molybdenum, CMOC) is a leading molybdenum production enterprise in mainland China and one of the world's top non-ferrous and rare metal producers. The company's predecessor can be traced back to the small-scale concentrator in Luanchuan County established in 1969 with the approval of the former Ministry of Metallurgy. In 1999, Luoyang Luanchuan Molybdenum Group was formally established and restructured into a joint-stock company in 2006. After two mixed-ownership reforms in 2004 and 2014, Luoyang Molybdenum is currently a privately held joint-stock company. The company was listed on the Hong Kong Stock Exchange in 2007 (stock code: 03993) and returned to A-share listing on the Shanghai Stock Exchange in 2012 (stock code: 603993).\\n\\nLuoyang Molybdenum's core business covers the mining, selection, smelting and processing of basic and rare metals, including molybdenum, tungsten, copper, cobalt, niobium, phosphorus, etc., while actively developing mineral trade business. The company's business footprint spans Asia, Africa, South America and Europe, making it a global leading producer of copper, cobalt, molybdenum, tungsten and niobium, as well as a leading phosphate fertilizer producer in Brazil. As of Q3 2025, the company achieved operating revenue of 145.485 billion yuan, net profit attributable to parent company of 8.671 billion yuan, and net cash flow from operating activities of 12.009 billion yuan, with the asset-liability ratio further optimized to 50.15%.\\n\\n### Strategy and Operations Upgrade\\nIn 2025, the company welcomed an important strategic turning point, introducing a management team with an international perspective. The new chairman Liu Jianfeng (former commercial director of CNOOC) and executive vice president Que Zhaoyang (former executive of Zijin Mining Group) led the promotion of organizational structure innovation. Through key acquisitions such as the Cangrejos gold mine in Ecuador (expected to start production in 2029), the company achieved a transformation of its asset portfolio towards multiple varieties (mainly copper and gold), multiple countries (covering Africa and South America), and multiple stages (combination of production and greenfield projects). The core mining area in the Democratic Republic of Congo continues to be optimized through 'small improvements and small reforms', with planned copper capacity reaching 800,000-1 million tons by 2028, and the construction of the Nzilo II hydropower station effectively alleviating energy constraints.\\n\\n### Industry Position and Financial Performance\\nAccording to the latest 2025 Fortune China 500 ranking, Luoyang Molybdenum ranked 138th with revenue of 213.029 billion yuan, with market value exceeding 250 billion yuan. The company's unique 'mine + trade' dual-wheel model controls 12% of global copper concentrate trade volume through the IXM trading platform, with TFM and KFM project costs ranking in the top 30% and top 10% globally respectively. The company maintains an absolute advantage in the new energy metals field, with cobalt production accounting for over 40% of global total. Recent export control policies in the Democratic Republic of Congo have prompted cobalt price rebounds, with average prices in the first half of 2025 increasing 26% compared to 2024.\\n\\n### Technology and Social Responsibility\\n5G smart mines achieve full-process unmanned operations from drilling, transportation to crushing, with mining costs 18-22% lower than international peers. In terms of ESG construction, MSCI rating was upgraded to BBB level, climate risks disclosed through TCFD framework, mine electrification rate reached 35%, and emission reduction intensity decreased by 19% year-on-year. In 2025, a cash dividend of 0.255 yuan per share was implemented, continuously rewarding shareholders.\\n\\n### Future Outlook\\nManagement expects to maintain high-intensity mergers and acquisitions from 2026-2028, focusing on copper and gold resources, with multiple potential projects already reserved. The Cangrejos gold mine in Ecuador (expected annual gold production of 11.5 tons) and KFM Phase II expansion constitute mid-term growth drivers, with Morgan Stanley predicting copper equivalent production capacity to exceed 1.5 million tons by 2027. The company's asset-liability ratio is controlled within the 50% safety line, with cash on hand exceeding 32 billion yuan, providing sufficient ammunition for strategic layout.\"",
    "[10:56:04] }"
]

# InsightEngine reflection summary - multi-line JSON format (containing "generating reflection summary" identifier)
REAL_INSIGHT_ENGINE_REFLECTION = [
    "[10:55:19] 2025-11-06 10:55:19.563 | INFO     | InsightEngine.nodes.summary_node:run:265 - generating reflection summary",
    "[10:56:41] 2025-11-06 10:56:41.626 | INFO     | InsightEngine.nodes.summary_node:process_output:296 - cleaned output: {",
    "[10:56:41] \"updated_paragraph_latest_state\": \"## Key Findings (Updated Version)\\nLuoyang Molybdenum's Q3 2025 market performance shows structural differentiation. Against the backdrop of global copper prices rising 18% year-on-year (LME three-month copper average price $8,927/ton), the company's stock price actually fell 12.3% cumulatively, forming a sharp contrast with the 7.8% increase in the Shenwan Non-ferrous Metals Index. In-depth analysis shows this disconnection mainly stems from three contradictions: the game between global energy transition dividends and regional operational risks, the conflict between resource endowment advantages and ESG shortcomings, and the misalignment between institutional valuation framework changes and retail investor cognitive lag. Latest public opinion monitoring shows that professional investors' discussion focus has shifted from production data to the judicial progress of community compensation cases in the Democratic Republic of Congo (estimated amount of $230 million), while retail investors are still hyping the 'new energy metals' concept.\\n\\n## Detailed Data Portrait\\n### Production and Costs\\n- Democratic Republic of Congo TFM copper-cobalt mine: Q3 copper production 128,000 tons (down 7% quarter-on-quarter), cobalt production 5,200 tons (down 9% quarter-on-quarter), unit cash cost rose to $1.52/lb (Q2 was $1.38), due to local strikes causing 14 days of production suspension (loss of output value about 320 million yuan)\\n- Brazil niobium-phosphate mine: ferro-niobium production 21,000 tons (up 4% year-on-year), phosphate fertilizer production 280,000 tons (record), shipping cost proportion rose to 23% (2024 average 17%), but saved 180 million yuan in local costs due to Brazilian real depreciation\\n- Australia NPM copper-gold mine: copper grade declined to 0.72% (same period last year 0.81%), but maintained stable production through improved recovery rate (recovery rate increased 2.3 percentage points to 89.7%)\\n\\n### Financial Indicators\\n- Revenue: Q3 achieved 28.7 billion yuan (up 9.2% year-on-year, down 5.3% quarter-on-quarter), 6% below Bloomberg consensus expectations, mainly due to decline in copper-cobalt sales\\n- Cash Flow: net cash flow from operating activities 4.2 billion yuan (down 18% year-on-year), capital expenditure reached 3.5 billion yuan (KFM project accounted for 72%)\\n- Debt: asset-liability ratio rose to 58.3% (end of 2024 54.1%), newly added 2 billion yuan corporate bonds with coupon rate 6.8% (120bp higher than peers)\\n\\n### Market Reaction\\n- Stock performance: Q3 cumulative turnover rate 287%, significantly higher than Zijin Mining (189%) and Jiangxi Copper (156%), amplitude reached 43%\\n- Institutional trends: northbound funds holdings reduced by 120 million shares, Norway's pension fund shareholding ratio decreased from 2.1% to 1.4% (ESG rebalancing)\\n- Public opinion heat: Baidu index 'Luoyang Molybdenum' average daily search volume 3,215 times (ranked 4th in industry), but professional platform Wind word frequency statistics show analyst attention ranking 2nd (including 327 research reports)\\n\\n## Diverse Voices Convergence\\nIndustry perspective:\\n1. [Fastmarkets analyst] 'After the implementation of new mining tax in the Democratic Republic of Congo, TFM project's effective tax rate increased from 31.5% to 35.8%, increasing the tax burden per pound of copper by $0.12' (report cited 87 times)\\n2. [Brazil Mining Association] 'Despite rising shipping costs, Luoyang Molybdenum's niobium-phosphate mine remains a high-quality asset in the top 20% of the global cost curve'\\n3. [DRC Mining Minister's statement] 'Requires foreign mining enterprises to reach 40% local procurement ratio by 2026' (current 25%)\\n4. [Australian Minerals Council] 'NPM mine's labor costs have exceeded affordable range and may affect 2026 expansion plans'\\n\\nInvestor voice:\\n5. [Xueqiu user @ValueMiner] 'DCF model shows that if DRC policy risk premium increases by 200bp, the company's reasonable valuation should be reduced by 15-20%' (with detailed calculation table, professionally certified)\\n6. [Stock forum hot post] 'After social security fund Q3 reduction, financing balance instead increased by 430 million yuan, fierce long-short game' (single-day clicks over 100,000)\\n7. [Twitter institutional account] 'MSCI lowered company governance (G) score from 6.2 to 5.4, mainly due to board independence issues'\\n8. [Institutional investor research summary] 'At least 7 funds questioned DRC subsidiary dividend policy (dividend payout ratio only 12% in past three years)'\\n9. [Reddit retail discussion] 'Call option holdings surged 300%, concentrated strike price 9 yuan'\\n\\nInternational perspective:\\n10. [Bloomberg report] 'Luoyang Molybdenum and Glencore's KFM project equity negotiations stalled, with $5/lb difference in cobalt price expectations after 2026'\\n11. [DRC local media] 'TFM surrounding community filed 3 new environmental lawsuits, requiring total compensation of $80 million'\\n12. [Australian mining workers forum] 'NPM mining area union is preparing new round of salary negotiations, existing contract premium has reached 125% of industry average'\\n13. [Reuters] 'China Exim Bank may provide $1.5 billion refinancing for KFM project'\\n14. [African Development Bank report] 'DRC mining community conflict incidents increased 47% year-on-year'\\n\\n## Deep Insight Upgrade\\n### Policy Risk Quantification\\nThrough Monte Carlo simulation calculations, under the following scenarios: (1) DRC royalty rate increased by 3 percentage points (2) shipping costs maintained at current levels (3) cobalt price hovers around $25/lb, the company's 2026 EBITDA may shrink by 2.3-2.8 billion yuan. Sensitivity analysis shows that the weight of DRC policy variables on valuation impact increased from 18% last year to 31%. Geopolitical experts point out that the approaching DRC election makes the mining policy uncertainty index reach 78 (warning line 70).\\n\\n### ESG Impact Decomposition\\n- Environment (E): Tailings pond management was flagged by MSCI, mainly because the water recycling rate of DRC projects is only 72% (international peer average 85%), and 2 small-scale leaks occurred in 2025\\n- Society (S): Community relationship score plummeted, due to Q3 local employment ratio dropping to 43% (committed target 60%), and medical investment decreased 15% year-on-year\\n- Governance (G): Independent directors on the board account for 33% (only 1 with international mining experience), lower than the international mining company average of 45%\\n\\n### Capital Behavior Analysis\\nDragon and tiger list data shows that Q3 institutional dedicated seats net sold 2.3 billion yuan (record quarterly high), but quantitative fund trading proportion increased from 12% to 19%, showing enhanced algorithmic trading effect on stock price volatility. Northbound funds holding cost analysis shows that foreign capital stop-loss lines are concentrated around 6.8 yuan (current price 7.2 yuan). Notably, the block trade premium rate narrowed from Q2's -3% to -1.2%, suggesting some long-term funds started buying at lows.\\n\\n## Trend and Pattern Recognition\\n1. Information layering intensified: Professional institutions predict supply and demand changes through LME inventory data (recent Asian warehouse copper inventory increased 35%), while retail investors still rely on optimistic predictions from brokerage research reports ('buy' rating ratio still 68% but down 11% from Q2)\\n2. ESG factor pricing power increased: Negative rating directly led to 3.2% gap down opening on November 3, creating the largest single-day gap in three months\\n3. New features of long-short game: Short selling balance broke 500 million yuan for the first time in history (average interest rate 8.6%), while over-the-counter option implied volatility rose to 52% (higher than industry average 38%)\\n4. Cost inflation transmission lag: Although auxiliary materials like sulfuric acid prices rose 23%, product prices only increased 9%, gross margin under significant pressure\\n\\n## Comparative Analysis\\n| Dimension                | Luoyang Molybdenum       | Zijin Mining             | Jiangxi Copper           | Industry Average         |\\n|-------------------------|--------------------------|--------------------------|--------------------------|--------------------------|\\n| Overseas revenue ratio  | 68%                      | 55%                      | 32%                      | 48%                      |\\n| Copper mine cash cost   | $1.52/lb                 | $1.35/lb                 | $1.48/lb                 | $1.45/lb                 |\\n| ESG rating              | BB-(MSCI)                | BBB(S&P)                 | BB+(MSCI)                | BBB-(S&P)                |\\n| Q3 institutional research visits | 87 times                | 126 times                | 53 times                 | 89 times                 |\\n| Retail shareholder ratio| 41%                      | 38%                      | 45%                      | 42%                      |\\n| Overseas project disputes| 4 cases                  | 2 cases                  | 1 case                   | 2.3 cases                |\\n| R&D investment ratio    | 0.8%                     | 1.2%                     | 0.9%                     | 1.1%                     |\\n\\n*Data period: Q3 2025, Sources: Company announcements, rating agencies, Shanghai and Shenzhen Stock Exchanges, Bloomberg Terminal*\"",
    "[10:56:41] }"
]

# MediaEngine reflection summary - single-line JSON format
REAL_MEDIA_ENGINE_REFLECTION = """[10:56:15] 2025-11-06 10:56:15.779 | INFO     | MediaEngine.nodes.summary_node:run:268 - generating reflection summary
[10:56:42] 2025-11-06 10:56:42.337 | INFO     | MediaEngine.nodes.summary_node:process_output:302 - cleaned output: {"updated_paragraph_latest_state": "## Comprehensive Information Overview\\r\\nAccording to current query requirements, this section will analyze Luoyang Molybdenum's basic situation, focusing on its company establishment time, headquarters location, main business and position in the global mining field. Although the search results provided this time are empty, based on mastery of public authoritative information and industry common sense, combined with corporate official websites, annual reports and historical reports from mainstream financial media, we can systematically restore Luoyang Molybdenum's core profile. As a global leading diversified mining group, Luoyang Molybdenum occupies an important position in China's and even the world's non-ferrous metals industry, with its development history, strategic layout and resource control capabilities all demonstrating significant international characteristics.\\r\\n\\r\\n## In-depth Text Content Analysis\\r\\nLuoyang Molybdenum's full name is Luoyang Luanchuan Molybdenum Group Co., Ltd., established in 2003, with its predecessor tracing back to the Luanchuan Molybdenum Mine established in 1969, marking the company's deep historical accumulation in the field of molybdenum-tungsten resource development. The company was listed on the main board of the Hong Kong Stock Exchange in 2007 (stock code: 03993.HK) and listed on the main board of the Shanghai Stock Exchange in 2012 (stock code: 603993), forming an A+H share dual capital platform structure, enhancing financing capabilities and international influence. Headquarters located in Luanchuan County, Luoyang City, Henan Province, situated in an important mineral resource-rich area in central China, relying on local abundant strategic metal reserves such as molybdenum and tungsten, it has built an integrated industrial chain from mining, beneficiation to deep processing. The company's main business focuses on the exploration, mining, processing and sales of basic and rare metals, with core products including molybdenum, tungsten, copper, cobalt, niobium, phosphorus and gold, forming a diversified mineral product combination that effectively enhances anti-cyclical fluctuation capabilities. Especially in molybdenum resources, Luoyang Molybdenum's Luanchuan mining area is known as 'one of the world's three largest molybdenum mines', with its molybdenum metal reserves ranking among the top globally; while in tungsten resources it also possesses world-class scale, making it one of China's and even the world's most important tungsten producers. In recent years, through a series of cross-border mergers and acquisitions, the company has successfully expanded into African and South American markets, especially operating the Tenke Fungurume copper-cobalt mine in the Democratic Republic of Congo, making it the world's second-largest cobalt producer, occupying a key position in the new energy battery raw material supply chain. Additionally, the company's niobium mines in Brazil (Catalão and Boa Vista projects) are also important sources of high-grade niobium resources globally, with niobium widely used in high-strength alloy steel manufacturing, serving the aerospace and high-end equipment manufacturing fields.\\r\\n\\r\\n## Visual Information Interpretation\\r\\nAlthough no relevant image materials were provided this time, from previously published company promotional materials, annual report covers and mine实景图中可以推断出，洛阳钼业的品牌视觉通常以深蓝、灰色为主色调，象征着工业稳重与科技感，配以矿山开采场景、现代化选矿厂或地球仪元素，突出其'全球化矿业巨头'的定位。例如，在年度报告中常见大型露天矿坑航拍图，展现宏大的开采规模；也有员工在智能化控制中心监控生产流程的画面，体现数字化转型成果。这些视觉符号共同塑造了一个传统资源型企业向高科技、绿色化、国际化综合矿业集团转型的形象。若能获取近期官方发布的图片，预计将看到更多关于绿色矿山建设、生态修复工程以及海外项目本地社区合作的内容，反映ESG（环境、社会与治理）理念的深入实践。\\r\\n\\r\\n## Comprehensive Data Analysis\\r\\nFrom financial and operational data perspectives, Luoyang Molybdenum has maintained steady growth in recent years. According to the 2023 annual report, the company achieved annual operating revenue of approximately 144.5 billion RMB, net profit attributable to parent company exceeding 8 billion RMB, and total assets exceeding 200 billion RMB, demonstrating strong profitability and asset strength. In terms of resource reserves, according to JORC standard disclosure, the company controls over 2 million tons of molybdenum metal reserves, about 800,000 tons of tungsten reserves, tens of millions of tons of copper resources, and hundreds of thousands of tons of cobalt resources, showing extremely superior resource endowments. In production, in 2023 the company's annual molybdenum production was about 17,000 tons, tungsten concentrate equivalent WO₃ about 25,000 tons, copper metal about 220,000 tons, cobalt metal about 25,000 tons, with copper-cobalt production mainly from Democratic Republic of Congo and Australia Northparkes projects. In global mining rankings, Luoyang Molybdenum has been selected for Forbes Global 2000 for many consecutive years and ranked among the top in Fortune China 500. According to SNL Metals & Mining and other institutions, its cobalt production market share accounts for about 15-18% of global total production, second only to Glencore, ranking second in the world; while molybdenum product market share also ranks among the top three globally. Additionally, the company's R&D investment continues to increase, with 2023 R&D expenses exceeding 1.5 billion yuan, mainly used for smart mine construction, low-grade ore comprehensive utilization technology and carbon emission reduction process optimization, reflecting determination to transform towards high-quality development models.\\r\\n\\r\\n## Multi-dimensional Insights\\r\\nIn summary, Luoyang Molybdenum is not only a local mining enterprise rooted in Henan, China, but has developed into a transnational mining group with global resource allocation capabilities. Its success path demonstrates a 'local advantage resources + strategic overseas expansion' dual-wheel drive model. Domestically, it has established a solid foundation based on the Luanchuan world-class molybdenum-tungsten deposits; overseas, through precise mergers and acquisitions, it has achieved effective control of key strategic minerals - especially copper-cobalt resources needed for new energy - aligning with global energy transition trends. At the same time, the company actively promotes digitalization, intelligence and green mine construction, such as using unmanned transportation systems and remote monitoring platforms at the Kisanfu copper-cobalt mine in northern Peru, enhancing safety and efficiency. In the future, as demand for metals such as copper, cobalt, and niobium continues to rise due to electric vehicles, energy storage systems and renewable energy infrastructure, Luoyang Molybdenum's strategic value will be further highlighted. However, its overseas operations also face geopolitical risks, environmental compliance pressures and community relationship management challenges, especially in resource-rich but relatively weakly governed countries like the Democratic Republic of Congo. Therefore, how to balance economic benefits with social responsibility and strengthen sustainable development capabilities will be key to determining its long-term competitiveness."}"""

# ===== SearchNode output examples (should be filtered, should not enter forum) =====

# SearchNode first search query - multi-line JSON format
SEARCH_NODE_FIRST_SEARCH = [
    "[11:16:35] 2025-11-06 11:16:35.567 | INFO     | InsightEngine.nodes.search_node:process_output:97 - cleaned output: {",
    "[11:16:35] \"search_query\": \"what does everyone think\"",
    "[11:16:35] \"search_tool\": \"search_topic_globally\"",
    "[11:16:35] \"reasoning\": \"This is the reasoning for the search query\"",
    "[11:16:35] \"enable_sentiment\": true",
    "[11:16:35] }"
]

# SearchNode reflection search query - single-line JSON format
SEARCH_NODE_REFLECTION_SEARCH = """[11:17:05] 2025-11-06 11:17:05.547 | INFO     | InsightEngine.nodes.search_node:process_output:232 - cleaned output: {"search_query": "AI education data leak unfair", "search_tool": "search_hot_content", "reasoning": "Need to understand recent hot controversies about AI education, especially data security and fairness issues most concerned by the public, to supplement specific cases and real public opinion data", "time_period": "week", "enable_sentiment": true}"""

# ===== Error log examples (should be filtered, should not enter forum) =====

# SummaryNode JSON parsing failed error log
SUMMARY_NODE_JSON_ERROR = "[11:55:31] 2025-11-06 11:55:31.763 | ERROR    | MediaEngine.nodes.summary_node:process_output:141 - JSON parsing failed: Unterminated string starting at: line 1 column 28 (char 27)"

# SummaryNode JSON repair failed error log
SUMMARY_NODE_JSON_FIX_ERROR = "[11:55:31] 2025-11-06 11:55:31.799 | ERROR    | MediaEngine.nodes.summary_node:process_output:149 - JSON repair failed, directly using cleaned text"

# SummaryNode ERROR level log (contains nodes.summary_node but should not be captured)
SUMMARY_NODE_ERROR_LOG = "[11:55:31] 2025-11-06 11:55:31.763 | ERROR    | MediaEngine.nodes.summary_node:process_output:141 - error occurred: unable to process output"

# SummaryNode Traceback error log (although contains nodes.summary_node, should not be captured)
SUMMARY_NODE_TRACEBACK = """[11:55:31] File "D:\\Programing\\BettaFish\\SingleEngineApp\\..\\MediaEngine\\nodes\\summary_node.py", line 138, in process_output
[11:55:31] result = json.loads(cleaned_output)"""

