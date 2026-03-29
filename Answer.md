# Trader Performance vs Market Sentiment — Analysis Write-up
# Primetrade.ai | Data Science Intern Assignment | Ronak



## Objective

Analyze whether Bitcoin Fear/Greed sentiment influences trader behavior and performance
on the Hyperliquid derivatives exchange, and derive actionable trading rules from the findings.



## Methodology

**Step 1 — Data preparation**
Loaded both datasets, documented shape, dtypes, missing values, and duplicates.
Parsed Hyperliquid millisecond timestamps to date objects. Mapped the 5-label sentiment
classification (Extreme Fear, Fear, Neutral, Greed, Extreme Greed) into 2 labels
(Fear / Greed) for cleaner binary analysis. Merged on date using an inner join.

**Step 2 — Feature engineering**
Built daily metrics per trader: total PnL, win rate, trade frequency, average trade
size (USD), buy/sell ratio, total fees paid, and net PnL after fees. Computed a
drawdown proxy using cumulative PnL series per trader. Segmented traders into three
independent dimensions: trade size (Small / Mid / Large), frequency
(Infrequent / Moderate / Frequent), and profitability consistency
(Consistent Winner / Inconsistent).

**Step 3 — Analysis**
Answered the three core questions using grouped aggregations, two-sample t-tests for
statistical significance, and cross-segment comparisons. Produced 14 charts covering
distributions, behavioral patterns, segment performance, and temporal trends.

**Step 4 — Modelling (bonus)**
Trained Logistic Regression, Random Forest, and Gradient Boosting classifiers to
predict next-day trader profitability using current-day sentiment and behavior features.
Evaluated using ROC-AUC with 5-fold cross-validation. Clustered traders into 4
behavioral archetypes using KMeans with PCA visualization.



## Key Insights

**Insight 1 — Fear days generate 88% higher mean PnL than Greed days.**

 Metric - Fear - Greed |

Mean daily PnL - 171,466 USD - 90,988 USD 
Median daily PnL - 46,070 USD - 20,925 USD 
Std deviation - 348,594 - 264,805 

Contrary to conventional expectations, Fear days on Hyperliquid produce nearly double
the mean and median PnL of Greed days. Higher standard deviation on Fear days confirms
greater volatility, but the upside captured far outweighs the increased risk. This
suggests experienced traders on this platform actively exploit fear-driven mispricings
rather than retreating during uncertainty.



**Insight 2 — Win rate is below 50% on both sentiment types, yet traders remain profitable.**

| Metric | Fear | Greed |
||||
| Win rate | 38.48% | 36.90% |

Traders lose more individual trades than they win regardless of sentiment. Profitability
is driven by asymmetric trade sizing — winning trades are substantially larger in USD
value than losing trades. This means raw win rate is a misleading performance metric
for this dataset. Risk-reward ratio and position sizing matter far more than win rate
when evaluating trader quality on Hyperliquid.



**Insight 3 — Large-size traders lose 94% of their edge on Greed days.**

| Size segment - Fear PnL - Greed PnL - Change 

 Large - 268,906 USD - 16,105 USD  -94% 
 Mid - 156,269 USD - 156,827 USD  +0.4% 
 Small - 81,729 USD - 118,000 USD  +44% 

The Mid segment is the most consistent performer — virtually identical PnL across both
sentiments. Large traders dramatically overperform on Fear days but collapse on Greed
days, suggesting they oversize or overtrade during euphoric conditions. Small traders
show the opposite pattern and actually perform better on Greed days, indicating a
different strategy profile suited to trending, bullish conditions.



**Insight 4 — Moderate-frequency traders lose money on Greed days.**

Frequency segment - Fear PnL - Greed PnL 

Frequent - 212,830 USD - 222,958 USD 
Moderate - 267,294 USD - -9,600 USD 
Infrequent - 62,587 USD - 52,472 USD 

The Moderate segment swings from being the second-best performer on Fear days
(267,294 USD) to negative territory on Greed days (-9,600 USD). Frequent traders are
the only segment that performs consistently well across both sentiments. This suggests
mid-tier activity on Greed days leads to overtrading without conviction — placing trades
out of FOMO rather than edge.



**Insight 5 — Average drawdown is contained relative to profit potential.**

- Average maximum drawdown per trader: -3,308 USD
- Worst single-trader drawdown: -59,349 USD

Given that mean daily PnL on Fear days exceeds 171,000 USD, the average drawdown of
-3,308 USD represents a favorable risk-reward profile. The worst-case drawdown of
-59,349 USD is significant but isolated. Most traders on this platform operate with
controlled downside relative to their upside capture.



## Strategy Recommendations

**Rule 1 — Increase trading activity on Fear days, not Greed days.**

The data shows Fear days produce 88% higher mean PnL and 120% higher median PnL than
Greed days. Traders should treat Fear sentiment as an opportunity signal rather than a
risk-off trigger. Concrete implementation: when the Fear/Greed index reads Fear or
Extreme Fear, maintain or increase normal position activity. When it reads Greed or
Extreme Greed, apply the size reduction rule below.

*Applies to: all trader segments, especially Large and Moderate-frequency traders.*



**Rule 2 — Large-size traders must reduce position sizing by at least 50% on Greed days.**

The Large segment earns 268,906 USD on Fear days but collapses to 16,105 USD on Greed
days — a 94% drop. This is the single strongest pattern in the dataset. The Mid segment
shows no such sensitivity (156,269 vs 156,827 USD), confirming the problem is specific
to oversizing during euphoric conditions, not a market-wide effect.

Concrete rule: if Classification = Greed, Large-segment traders cap individual position
size to 50% of their Fear-day average. Resume normal sizing when sentiment returns to
Fear or Neutral.

*Applies to: traders whose average trade size places them in the top tercile.*



## Model Results (Bonus)

Logistic Regression | 0.8889 | 0.625 |
Random Forest ( Best performer) | 0.8889 | 0.625 |
Gradient Boosting | 0.8889 | 0.5625 |


Top features by importance (Random Forest): daily PnL, win rate, and sentiment encoding
were the strongest predictors of next-day profitability, confirming that current-day
performance and sentiment together carry meaningful signal.

Clustering identified 4 behavioral archetypes: High-Volume Trader, Low-Volume Trader,
Consistent Winner, and Active Trader — each with distinct risk/return profiles across
sentiment regimes.



## Reproducibility

git clone <repo>
cd primetrade-assignment
pip install -r requirements.txt
# Place CSVs in data/raw/
python run_pipeline.py


## Or with Docker:
make docker-build
make docker-run


All charts reproducible in `charts/`. All processed data in `data/processed/`.
All model outputs in `outputs/`.



*Submitted by Ronak | Primetrade.ai Data Science Intern Application*
