"""
Clean and preprocess OHLCV stock data.
"""
import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import (
    DEFAULT_TICKERS,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
)

logger = get_logger(__name__)


def clean_ohlcv_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean OHLCV data by handling duplicates, missing values, and anomalies.
    """
    df = data.copy()

    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # Remove duplicate timestamps
    df = df[~df.index.duplicated(keep="first")]

    # Force numeric columns
    price_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        logger.warning(f"Found {missing} missing values — applying ffill/bfill")
        df = df.ffill().bfill()

    # Remove non-trading rows
    if "Volume" in df.columns:
        df = df[df["Volume"] > 0]

    # Remove extreme price anomalies (robust quantile filter)
    for col in ["Open", "High", "Low", "Close"]:
        if col in df.columns:
            q_low, q_high = df[col].quantile([0.01, 0.99])
            df = df[(df[col] >= q_low) & (df[col] <= q_high)]

    logger.info(f"Cleaned OHLCV data → {len(df)} rows")
    return df


def resample_data(data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample OHLCV data to a higher timeframe.
    """
    resampled = (
        data.resample(timeframe)
        .agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        .dropna()
    )

    logger.info(f"Resampled to {timeframe} → {len(resampled)} rows")
    return resampled


def clean_all_tickers():
    """
    Clean raw OHLCV data for all configured tickers.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in DEFAULT_TICKERS:
        logger.info(f" Cleaning data for {ticker}")

        raw_path = RAW_DATA_DIR / f"{ticker}.csv"
        if not raw_path.exists():
            logger.warning(f"Raw data not found for {ticker}, skipping")
            continue

        data = pd.read_csv(
            raw_path,
            index_col=0,
            parse_dates=True,
        )

        cleaned = clean_ohlcv_data(data)

        output_path = PROCESSED_DATA_DIR / f"{ticker}_cleaned.csv"
        cleaned.to_csv(output_path)

        logger.info(f"Saved cleaned data → {output_path}")


if __name__ == "__main__":
    clean_all_tickers()
