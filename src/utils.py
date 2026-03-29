import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from src.config import CHARTS_DIR, FIG_DPI, PALETTE


def setup_plotting():
    plt.rcParams['figure.figsize']      = (12, 5)
    plt.rcParams['figure.dpi']          = FIG_DPI
    plt.rcParams['axes.spines.top']     = False
    plt.rcParams['axes.spines.right']   = False
    plt.rcParams['axes.grid']           = True
    plt.rcParams['grid.alpha']          = 0.3
    plt.rcParams['font.family']         = 'DejaVu Sans'
    sns.set_palette("Set2")


def save_chart(fig, filename):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches='tight')
    print(f"Chart saved: {path}")
    return path


def sentiment_colors(labels):
    return [PALETTE.get(l, PALETTE['neutral']) for l in labels]


def print_section(title):
    print()
    print("=" * 55)
    print(f"  {title}")
    print("=" * 55)


def print_subsection(title):
    print()
    print(f"--- {title} ---")


def describe_df(df, name="DataFrame"):
    print_section(name)
    print(f"  Shape      : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"  Columns    : {df.columns.tolist()}")
    print(f"  Dtypes     :")
    for col, dt in df.dtypes.items():
        print(f"             {col:30s} {str(dt)}")
    print(f"  Missing    :")
    for col, n in df.isnull().sum().items():
        flag = "  <-- check" if n > 0 else ""
        print(f"             {col:30s} {n}{flag}")
    print(f"  Duplicates : {df.duplicated().sum():,}")
