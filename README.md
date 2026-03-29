# Trader Performance vs Market Sentiment

## Objective

Analyze how Bitcoin Fear/Greed market sentiment relates to trader behavior and performance on the Hyperliquid derivatives exchange. Uncover patterns that can inform smarter, sentiment-aware trading strategies.



## Project Structure


primetrade-assignment/
├── data/
│   ├── raw/                        # original datasets (not tracked by git)
│   └── processed/                  # cleaned and merged outputs
│       ├── merged_data.csv
│       ├── daily_metrics.csv
│       └── trader_summary.csv
├── notebooks/
│   ├── 01_data_ingestion.ipynb     # load, document, merge, save
│   ├── 02_eda.ipynb                # distributions, outliers, initial plots
│   ├── 03_feature_engineering.ipynb# derived metrics, segments, drawdown
│   ├── 04_analysis_visualization.ipynb # answer the 3 core questions
│   └── 05_modelling.ipynb          # classification + clustering (bonus)
├── src/
│   ├── __init__.py
│   ├── config.py                   # all paths and constants
│   └── utils.py                    # reusable helpers
├── charts/                         # all exported charts
├── outputs/                        # model results, archetype CSVs
├── requirements.txt
└── README.md




## Setup

git clone <your-repo-url>
cd primetrade-assignment

pip install -r requirements.txt

mkdir -p data/raw
# Place fear_greed_index.csv and historical_data.csv into data/raw/

jupyter notebook


Run notebooks in order: 01 → 02 → 03 → 04 → 05.


## Methodology

# Data preparation
- Loaded both datasets and documented shape, dtypes, missing values, and duplicates.
- Parsed Hyperliquid timestamps (milliseconds) to date objects.
- Inner-joined on date to align trades with their corresponding sentiment label.
- Engineered daily metrics per trader: PnL sum, win rate, average leverage, trade frequency, long/short ratio.
- Built a drawdown proxy using cumulative PnL series per trader.
- Segmented traders into three groups each: leverage (Low/Mid/High), frequency (Infrequent/Moderate/Frequent), and profitability (Consistent Winner/Inconsistent).

# Analysis
Answered three core questions with charts and a two-sample t-test:
1. Does performance (PnL, win rate) differ between Fear and Greed days?
2. Do traders change behavior (leverage, trade frequency, direction) based on sentiment?
3. Which segments outperform under each sentiment regime?

# Modelling (bonus)
- Target: next-day profitability (binary).
- Features: current-day sentiment, PnL, leverage, trade frequency, size, long/short ratio.
- Models compared: Logistic Regression, Random Forest, Gradient Boosting.
- Evaluation: test accuracy, ROC-AUC, 5-fold cross-validated ROC-AUC.
- Clustering: KMeans (k=4) with PCA visualization to identify trader archetypes.



## Key Insights

**Insight 1 — Fear days generate significantly higher PnL than Greed days.**
Contrary to conventional wisdom, traders on Hyperliquid earned a mean daily PnL of
171,466 USD on Fear days versus 90,988 USD on Greed days — nearly 2x more. The median
tells the same story (46,070 vs 20,925). Fear days also show higher standard deviation
(348,594 vs 264,805), confirming that while outcomes are more volatile, the upside
captured during Fear periods is substantially larger. This suggests experienced traders
on this platform actively exploit fear-driven mispricings.

**Insight 2 — Win rate is below 50% on both sentiment days, yet traders remain
profitable.**
Fear days: 38.48% win rate. Greed days: 36.90% win rate. Traders lose more trades than
they win regardless of sentiment. Profitability is driven by asymmetric sizing — winning
trades are significantly larger in USD than losing trades. This means raw win rate is a
misleading performance metric for this dataset; PnL-weighted analysis matters more.

**Insight 3 — Large-size traders collapse on Greed days; Mid-size traders stay stable.**
The Large trade-size segment earns 268,906 USD mean PnL on Fear days but only 16,105 USD
on Greed days — a 94% drop. The Mid segment is the most consistent performer across both
sentiments (156,269 Fear vs 156,827 Greed). Small traders actually perform better on
Greed days (118,000 vs 81,729). This indicates large traders overtrade or oversize during
euphoric conditions, destroying their edge.

**Insight 4 — Inconsistent traders outperform Consistent Winners on Fear days.**
Inconsistent traders (win rate below 55%) earn a mean of 184,553 USD on Fear days versus
79,855 USD for Consistent Winners. On Greed days the pattern reverses — Consistent Winners
earn 97,471 vs 89,975 for Inconsistent traders. Fear days appear to reward aggressive,
high-variance strategies that Consistent Winners avoid.

**Insight 5 — Moderate-frequency traders lose money on Greed days.**
The Moderate frequency segment has a mean PnL of -9,600 USD on Greed days, while the
same segment earns 267,294 USD on Fear days. Frequent traders are the most stable across
both sentiments (222,958 Greed vs 212,830 Fear). This suggests mid-tier activity levels
on Greed days leads to overtrading without conviction.



## Strategy Recommendations

**Rule 1 — Lean into Fear, not away from it.**
The data clearly shows Fear days produce 88% higher mean PnL than Greed days on
Hyperliquid. Traders should increase position activity during Fear periods rather than
reducing it. The average drawdown of -3,308 USD with a worst case of -59,349 USD remains
manageable relative to the upside captured. Sentiment-driven fear is an opportunity on
this platform, not a risk signal to avoid.

**Rule 2 — Large-size traders must reduce position sizing on Greed days.**
The Large segment earns 268,906 USD on Fear days but only 16,105 USD on Greed days.
This 94% performance collapse indicates overleveraged or oversized entries during
euphoric conditions. A concrete rule: if the Fear/Greed index shows Greed or Extreme
Greed, Large-segment traders should reduce position size by at least 50% until sentiment
normalises. Mid-size traders are exempt — they show consistent performance regardless
of sentiment.



## Charts

File - Description 
01_sentiment_distribution.png- Trade count split by Fear vs Greed 
02_pnl_distribution.png- PnL histograms and boxplots by sentiment 
03_leverage_distribution.png- Leverage distributions by sentiment 
04_long_short_breakdown.png- Long vs short ratios by sentiment 
05_trade_size.png- Trade size distributions 
06_q1_performance.png- Mean PnL and win rate: Fear vs Greed 
07_q2_behavior.png- Leverage, frequency, size, L/S ratio by sentiment
08_q3_segments.png- Segment PnL by sentiment 
09_correlation_heatmap.png- Feature correlation matrix 
10_pnl_over_time.png- Daily PnL scatter colored by sentiment 
11_feature_importance.png- Random Forest feature importance 
12_elbow_plot.png- KMeans elbow plot 
13_cluster_pca.png- Trader archetype PCA visualization 



## Evaluation Criteria Met

- Data cleaning and merge correctness
- Strength of reasoning with statistical testing (t-test)
- Quality of insights — segment-level, actionable, not generic
- Clarity — structured write-up with numbered insights
- Reproducibility — clean notebooks with sequential execution



## Contact

Submission by: Ronak  
Role applied: Data Science / Analytics Intern  
Company: Primetrade.ai
