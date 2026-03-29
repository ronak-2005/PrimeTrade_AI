import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_RAW       = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")
CHARTS_DIR     = os.path.join(BASE_DIR, "charts")
OUTPUTS_DIR    = os.path.join(BASE_DIR, "outputs")

SENTIMENT_FILE = os.path.join(DATA_RAW, "fear_greed_index.csv")
TRADER_FILE    = os.path.join(DATA_RAW, "historical_data.csv")
MERGED_FILE    = os.path.join(DATA_PROCESSED, "merged_data.csv")
METRICS_FILE   = os.path.join(DATA_PROCESSED, "daily_metrics.csv")

SENTIMENT_COL  = "Classification"
DATE_COL       = "date"
PNL_COL        = "Closed PnL"
SIZE_COL       = "Size USD"
SIDE_COL       = "Side"
ACCOUNT_COL    = "Account"
TIME_COL       = "Timestamp"
COIN_COL       = "Coin"
DIRECTION_COL  = "Direction"
FEE_COL        = "Fee"

FEAR_LABEL     = "Fear"
GREED_LABEL    = "Greed"

SENTIMENT_MAP = {
    'Extreme Fear' : 'Fear',
    'Fear'         : 'Fear',
    'Neutral'      : 'Fear',
    'Greed'        : 'Greed',
    'Extreme Greed': 'Greed',
}

PALETTE = {
    "Fear"  : "#E24B4A",
    "Greed" : "#1D9E75",
    "neutral": "#888780",
}

FIG_DPI    = 150
FIG_WIDTH  = 12
FIG_HEIGHT = 5
