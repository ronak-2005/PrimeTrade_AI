"""
run_pipeline.py

Headless end-to-end pipeline. Runs every analysis step without Jupyter.
Use this for Docker, CI/CD, or scheduled runs.

Usage:
    python run_pipeline.py
    python run_pipeline.py --skip-model
    python run_pipeline.py --only 01 03
"""

import argparse
import os
import sys
import time
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from src.config import (
    SENTIMENT_FILE, TRADER_FILE, MERGED_FILE, DATA_PROCESSED,
    OUTPUTS_DIR, CHARTS_DIR, SENTIMENT_MAP, PALETTE
)
from src.utils import setup_plotting, save_chart, print_section


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def step_01_ingest():
    log("Step 01 — Data ingestion")

    sentiment_df = pd.read_csv(SENTIMENT_FILE)
    trader_df    = pd.read_csv(TRADER_FILE)

    log(f"  Sentiment : {sentiment_df.shape[0]:,} rows x {sentiment_df.shape[1]} cols")
    log(f"  Trader    : {trader_df.shape[0]:,} rows x {trader_df.shape[1]} cols")

    sentiment_df['Classification'] = sentiment_df['classification'].map(SENTIMENT_MAP)
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date

    ts_sample = trader_df['Timestamp'].iloc[0]
    if ts_sample > 1e12:
        trader_df['date'] = pd.to_datetime(trader_df['Timestamp'], unit='ms').dt.date
    else:
        trader_df['date'] = pd.to_datetime(trader_df['Timestamp'], unit='s').dt.date

    merged_df = trader_df.merge(
        sentiment_df[['date', 'Classification']],
        on='date', how='inner'
    )

    os.makedirs(DATA_PROCESSED, exist_ok=True)
    merged_df.to_csv(MERGED_FILE, index=False)

    log(f"  Merged    : {merged_df.shape[0]:,} rows")
    log(f"  Fear      : {(merged_df['Classification']=='Fear').sum():,} trades")
    log(f"  Greed     : {(merged_df['Classification']=='Greed').sum():,} trades")
    log(f"  Saved     : {MERGED_FILE}")
    return merged_df


def step_02_eda(df):
    log("Step 02 — EDA charts")
    setup_plotting()
    os.makedirs(CHARTS_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    counts = df['Classification'].value_counts()
    axes[0].bar(counts.index, counts.values,
                color=[PALETTE['Fear'], PALETTE['Greed']], width=0.5)
    axes[0].set_title('Total trades by sentiment')
    axes[0].set_ylabel('Number of trades')
    day_counts = df.groupby('date')['Classification'].first().value_counts()
    axes[1].bar(day_counts.index, day_counts.values,
                color=[PALETTE['Fear'], PALETTE['Greed']], width=0.5)
    axes[1].set_title('Unique days by sentiment')
    axes[1].set_ylabel('Number of days')
    plt.suptitle('Fear vs Greed — dataset coverage', fontsize=14)
    plt.tight_layout()
    save_chart(fig, '01_sentiment_distribution.png')
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for label, color in [('Fear', PALETTE['Fear']), ('Greed', PALETTE['Greed'])]:
        subset = df[df['Classification'] == label]['Closed PnL'].clip(-5000, 5000)
        axes[0].hist(subset, bins=80, alpha=0.6, label=label, color=color, edgecolor='none')
    axes[0].axvline(0, color='black', linewidth=1, linestyle='--')
    axes[0].set_title('PnL distribution by sentiment')
    axes[0].set_xlabel('Closed PnL (USD)')
    axes[0].legend()
    df.boxplot(column='Closed PnL', by='Classification', ax=axes[1],
               showfliers=False, medianprops=dict(color='black', linewidth=2))
    axes[1].set_title('PnL boxplot by sentiment')
    axes[1].set_xlabel('')
    plt.suptitle('')
    plt.suptitle('PnL distributions — Fear vs Greed', fontsize=14)
    plt.tight_layout()
    save_chart(fig, '02_pnl_distribution.png')
    plt.close()

    log("  EDA charts saved")


def step_03_features(df):
    log("Step 03 — Feature engineering")

    df['is_buy']  = (df['Side'] == 'BUY').astype(int)
    df['is_sell'] = (df['Side'] == 'SELL').astype(int)
    df['is_win']  = (df['Closed PnL'] > 0).astype(int)

    daily_metrics = df.groupby(['date', 'Account', 'Classification']).agg(
        daily_pnl      = ('Closed PnL',  'sum'),
        num_trades     = ('Closed PnL',  'count'),
        win_rate       = ('is_win',       'mean'),
        avg_size_usd   = ('Size USD',     'mean'),
        total_size_usd = ('Size USD',     'sum'),
        avg_fee        = ('Fee',          'mean'),
        total_fee      = ('Fee',          'sum'),
        buy_trades     = ('is_buy',       'sum'),
        sell_trades    = ('is_sell',      'sum'),
    ).reset_index()

    daily_metrics['buy_sell_ratio'] = (
        daily_metrics['buy_trades'] / (daily_metrics['sell_trades'] + 1e-9)
    )
    daily_metrics['is_profitable']    = (daily_metrics['daily_pnl'] > 0).astype(int)
    daily_metrics['net_pnl_after_fee'] = daily_metrics['daily_pnl'] - daily_metrics['total_fee']

    def compute_max_drawdown(pnl):
        cum = pnl.cumsum()
        return (cum - cum.cummax()).min()

    drawdown_df = (
        daily_metrics.sort_values(['Account','date'])
        .groupby('Account')['daily_pnl']
        .apply(compute_max_drawdown)
        .reset_index()
        .rename(columns={'daily_pnl': 'max_drawdown'})
    )

    trader_summary = daily_metrics.groupby('Account').agg(
        total_pnl       = ('daily_pnl',     'sum'),
        avg_daily_pnl   = ('daily_pnl',     'mean'),
        overall_winrate = ('win_rate',       'mean'),
        avg_trades_day  = ('num_trades',     'mean'),
        total_trades    = ('num_trades',     'sum'),
        active_days     = ('date',           'nunique'),
        avg_size_usd    = ('avg_size_usd',   'mean'),
        avg_buy_sell    = ('buy_sell_ratio',  'mean'),
        total_fees_paid = ('total_fee',       'sum'),
    ).reset_index()

    trader_summary = trader_summary.merge(drawdown_df, on='Account', how='left')

    trader_summary['size_segment'] = pd.qcut(
        trader_summary['avg_size_usd'], q=3,
        labels=['Small','Mid','Large'], duplicates='drop'
    )
    trader_summary['frequency_segment'] = pd.qcut(
        trader_summary['avg_trades_day'], q=3,
        labels=['Infrequent','Moderate','Frequent'], duplicates='drop'
    )
    trader_summary['winner_segment'] = np.where(
        trader_summary['overall_winrate'] >= 0.55, 'Consistent Winner', 'Inconsistent'
    )

    daily_metrics.to_csv(f'{DATA_PROCESSED}/daily_metrics.csv',  index=False)
    trader_summary.to_csv(f'{DATA_PROCESSED}/trader_summary.csv', index=False)

    log(f"  daily_metrics  : {daily_metrics.shape}")
    log(f"  trader_summary : {trader_summary.shape}")
    return daily_metrics, trader_summary


def step_04_analysis(daily, traders):
    log("Step 04 — Analysis and visualization")
    setup_plotting()

    fear  = daily[daily['Classification'] == 'Fear']
    greed = daily[daily['Classification'] == 'Greed']

    t_stat, p_val = stats.ttest_ind(
        fear['daily_pnl'].dropna(), greed['daily_pnl'].dropna()
    )

    print_section('Q1 — PnL PERFORMANCE')
    q1 = daily.groupby('Classification').agg(
        mean_pnl  = ('daily_pnl','mean'),
        win_rate  = ('win_rate', 'mean'),
        std_pnl   = ('daily_pnl','std'),
    ).round(4)
    print(q1.T.to_string())
    print(f'\n  T-test p-value : {p_val:.4f}  Significant: {"Yes" if p_val < 0.05 else "No"}')

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    mean_pnl   = [fear['daily_pnl'].mean(), greed['daily_pnl'].mean()]
    win_rates  = [fear['win_rate'].mean(),  greed['win_rate'].mean()]
    labels     = ['Fear','Greed']
    colors     = [PALETTE['Fear'], PALETTE['Greed']]

    bars = axes[0].bar(labels, mean_pnl, color=colors, width=0.5)
    axes[0].set_title('Mean daily PnL')
    axes[0].set_ylabel('PnL (USD)')
    axes[0].axhline(0, color='black', linewidth=0.8, linestyle='--')
    for bar, val in zip(bars, mean_pnl):
        axes[0].text(bar.get_x() + bar.get_width()/2, val,
                     f'{val:.2f}', ha='center', va='bottom' if val >= 0 else 'top')

    bars2 = axes[1].bar(labels, [w*100 for w in win_rates], color=colors, width=0.5)
    axes[1].set_title('Mean win rate')
    axes[1].set_ylabel('Win rate (%)')
    axes[1].axhline(50, color='black', linewidth=0.8, linestyle='--')
    axes[1].set_ylim(0, 100)
    for bar, val in zip(bars2, win_rates):
        axes[1].text(bar.get_x() + bar.get_width()/2, val*100 + 1,
                     f'{val*100:.1f}%', ha='center')

    axes[2].boxplot(
        [fear['daily_pnl'].clip(-2000,2000), greed['daily_pnl'].clip(-2000,2000)],
        labels=labels, showfliers=False,
        medianprops=dict(color='black', linewidth=2)
    )
    axes[2].set_title('PnL spread')
    axes[2].axhline(0, color='black', linewidth=0.8, linestyle='--')

    plt.suptitle('Q1 — Performance: Fear vs Greed', fontsize=14)
    plt.tight_layout()
    save_chart(fig, '06_q1_performance.png')
    plt.close()

    daily_seg = daily.merge(
        traders[['Account','size_segment','frequency_segment','winner_segment']],
        on='Account', how='left'
    )

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, seg, title in zip(
        axes,
        ['size_segment','frequency_segment','winner_segment'],
        ['Trade size','Frequency','Winner type']
    ):
        seg_data = daily_seg.groupby([seg,'Classification'])['daily_pnl'].mean().unstack()
        seg_data.plot(kind='bar', ax=ax,
                      color=[PALETTE['Fear'], PALETTE['Greed']],
                      width=0.6, rot=30)
        ax.set_title(f'Mean PnL by {title}')
        ax.set_ylabel('Mean daily PnL (USD)')
        ax.set_xlabel('')
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax.legend(title='Sentiment')

    plt.suptitle('Q3 — Segment performance', fontsize=14)
    plt.tight_layout()
    save_chart(fig, '08_q3_segments.png')
    plt.close()

    log("  Analysis charts saved")


def step_05_model(daily, traders):
    log("Step 05 — Modelling")
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import roc_auc_score
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    daily = daily.sort_values(['Account','date'])
    daily['sentiment_enc'] = (daily['Classification'] == 'Greed').astype(int)
    daily['target'] = daily.groupby('Account')['is_profitable'].shift(-1)
    daily = daily.dropna(subset=['target'])
    daily['target'] = daily['target'].astype(int)

    feature_cols = ['sentiment_enc','daily_pnl','num_trades',
                    'win_rate','avg_size_usd','buy_sell_ratio','total_fee']
    model_df = daily[feature_cols + ['target']].dropna()
    X, y = model_df[feature_cols], model_df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    preds = rf.predict(X_test)
    proba = rf.predict_proba(X_test)[:,1]
    auc   = roc_auc_score(y_test, proba)
    acc   = (preds == y_test).mean()

    log(f"  Random Forest — Accuracy: {acc:.4f}  ROC-AUC: {auc:.4f}")

    importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9,5))
    ax.barh(importances.index, importances.values, color=PALETTE['neutral'], edgecolor='none')
    ax.set_title('Feature importance — Random Forest')
    ax.set_xlabel('Importance')
    plt.tight_layout()
    save_chart(fig, '12_feature_importance.png')
    plt.close()

    cluster_cols = ['avg_size_usd','avg_trades_day','overall_winrate','avg_buy_sell','total_fees_paid']
    cluster_data = traders[cluster_cols].dropna()
    sc = StandardScaler()
    cluster_sc = sc.fit_transform(cluster_data)
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    traders_c = traders.loc[cluster_data.index].copy()
    traders_c['cluster'] = km.fit_predict(cluster_sc)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    traders_c.to_csv(f'{OUTPUTS_DIR}/trader_archetypes.csv', index=False)
    pd.DataFrame([{'Model':'Random Forest','Accuracy':acc,'ROC_AUC':auc}]).to_csv(
        f'{OUTPUTS_DIR}/model_results.csv', index=False
    )
    log("  Model outputs saved")


def main():
    parser = argparse.ArgumentParser(description='Primetrade analysis pipeline')
    parser.add_argument('--skip-model', action='store_true', help='Skip modelling step')
    parser.add_argument('--only', nargs='+', help='Run only specific steps e.g. --only 01 03')
    args = parser.parse_args()

    only = set(args.only) if args.only else None

    start = time.time()
    log("Pipeline starting")
    log("-" * 50)

    try:
        if not only or '01' in only:
            merged = step_01_ingest()
        else:
            merged = pd.read_csv(MERGED_FILE)

        if not only or '02' in only:
            step_02_eda(merged)

        if not only or '03' in only:
            daily, traders = step_03_features(merged)
        else:
            daily   = pd.read_csv(f'{DATA_PROCESSED}/daily_metrics.csv')
            traders = pd.read_csv(f'{DATA_PROCESSED}/trader_summary.csv')

        if not only or '04' in only:
            step_04_analysis(daily, traders)

        if (not only or '05' in only) and not args.skip_model:
            step_05_model(daily, traders)

    except Exception as e:
        log(f"Pipeline FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)

    elapsed = time.time() - start
    log("-" * 50)
    log(f"Pipeline complete in {elapsed:.1f}s")
    log(f"Charts  -> {CHARTS_DIR}")
    log(f"Outputs -> {OUTPUTS_DIR}")


if __name__ == '__main__':
    main()
