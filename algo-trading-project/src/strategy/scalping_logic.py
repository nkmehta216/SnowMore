"""
Scalping strategy logic for short-term trading.
"""
import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import (
    DEFAULT_TICKERS,
    INDICATORS_DIR,
    SIGNALS_DIR,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
    BREAKOUT_LOOKBACK,
)

logger = get_logger(__name__)


def calculate_scalping_signals(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate scalping signals based on technical indicators.
    """
    df = data.copy()
    df["scalp_signal"] = 0

    # -------- RSI logic --------
    if "RSI" in df.columns:
        df.loc[df["RSI"] <= RSI_OVERSOLD, "scalp_signal"] = 1
        df.loc[df["RSI"] >= RSI_OVERBOUGHT, "scalp_signal"] = -1

    # -------- Bollinger Bands --------
    bb_cols = ["BBL_20_2.0", "BBU_20_2.0"]
    if all(col in df.columns for col in bb_cols):
        df.loc[df["Close"] <= df["BBL_20_2.0"], "scalp_signal"] = 1
        df.loc[df["Close"] >= df["BBU_20_2.0"], "scalp_signal"] = -1

    # -------- MACD crossover --------
    macd_cols = ["MACD_12_26_9", "MACDs_12_26_9"]
    if all(col in df.columns for col in macd_cols):
        bullish = (
            (df["MACD_12_26_9"] > df["MACDs_12_26_9"]) &
            (df["MACD_12_26_9"].shift(1) <= df["MACDs_12_26_9"].shift(1))
        )
        bearish = (
            (df["MACD_12_26_9"] < df["MACDs_12_26_9"]) &
            (df["MACD_12_26_9"].shift(1) >= df["MACDs_12_26_9"].shift(1))
        )

        df.loc[bullish, "scalp_signal"] += 1
        df.loc[bearish, "scalp_signal"] -= 1

    # -------- Volume confirmation --------
    if "Volume" in df.columns:
        vol_ma = df["Volume"].rolling(20).mean()
        vol_spike = df["Volume"] > 1.5 * vol_ma
        df.loc[vol_spike, "scalp_signal"] *= 1.5

    # Normalize signal
    df["scalp_signal"] = df["scalp_signal"].clip(-1, 1)

    logger.info(f"Generated scalping signals → {len(df)} rows")
    return df


def detect_breakout(
    data: pd.DataFrame,
    lookback: int = BREAKOUT_LOOKBACK,
) -> pd.DataFrame:
    """
    Detect price breakouts using rolling highs/lows.
    """
    df = data.copy()

    df["rolling_high"] = df["High"].rolling(lookback).max()
    df["rolling_low"] = df["Low"].rolling(lookback).min()

    df["breakout_signal"] = 0
    df.loc[df["Close"] > df["rolling_high"].shift(1), "breakout_signal"] = 1
    df.loc[df["Close"] < df["rolling_low"].shift(1), "breakout_signal"] = -1

    logger.info(
        f"Detected {df['breakout_signal'].abs().sum()} breakout events"
    )
    return df


def generate_scalping_signals_for_all_tickers():
    """
    Generate scalping signals for all configured tickers.
    """
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in DEFAULT_TICKERS:
        logger.info(f"⚡ Generating scalping signals for {ticker}")

        input_path = INDICATORS_DIR / f"{ticker}_features.csv"
        if not input_path.exists():
            logger.warning(f"Missing features for {ticker}, skipping")
            continue

        data = pd.read_csv(
            input_path,
            index_col=0,
            parse_dates=True,
        )

        data = calculate_scalping_signals(data)
        data = detect_breakout(data)

        output_path = SIGNALS_DIR / f"{ticker}_scalp_signals.csv"
        data.to_csv(output_path)

        logger.info(f"Saved scalping signals → {output_path}")


if __name__ == "__main__":
    generate_scalping_signals_for_all_tickers()
