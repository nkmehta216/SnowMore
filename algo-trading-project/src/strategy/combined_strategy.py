"""
Combine ML predictions with scalping signals.
"""
import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import (
    DEFAULT_TICKERS,
    INDICATORS_DIR,
    SIGNALS_DIR,
    RISK_PER_TRADE,
)
try:
    from src.utils import load_model, predict
except Exception:
    # Provide safe fallbacks so the module can be imported in notebook contexts
    def load_model(ticker: str):
        """Fallback loader: raise FileNotFoundError to indicate missing model."""
        raise FileNotFoundError(f"Model loader not available for {ticker}")

    def predict(model, scaler, features, df: pd.DataFrame):
        """Fallback predict: return zeros and None probabilities."""
        preds = np.zeros(len(df), dtype=int)
        probs = None
        return preds, probs
from src.strategy.scalping_logic import calculate_scalping_signals

logger = get_logger(__name__)


def combine_signals(
    ml_signal: int,
    scalp_signal: int,
    ml_weight: float,
    scalp_weight: float,
) -> int:
    """
    Combine ML and scalping signals using weighted voting.
    """
    score = (ml_signal * ml_weight) + (scalp_signal * scalp_weight)

    if score > 0.5:
        return 1   # BUY
    elif score < -0.5:
        return -1  # SELL
    else:
        return 0   # HOLD


def generate_combined_strategy(
    ticker: str,
    data: pd.DataFrame,
    ml_weight: float = 0.6,
) -> pd.DataFrame:
    """
    Generate combined ML + scalping trading signals.
    """
    df = data.copy()

    # ---------- ML SIGNAL ----------
    try:
        model, scaler, features = load_model(ticker)
        preds, probs = predict(model, scaler, features, df)

        # Convert {0,1} → {-1,1}
        df["ml_signal"] = np.where(preds == 1, 1, -1)

    except FileNotFoundError:
        logger.warning(f"No ML model for {ticker} → scalping only")
        df["ml_signal"] = 0
        ml_weight = 0.0

    # ---------- SCALPING SIGNAL ----------
    df = calculate_scalping_signals(df)

    if "scalp_signal" not in df.columns:
        df["scalp_signal"] = 0
    else:
        df["scalp_signal"] = df["scalp_signal"].clip(-1, 1)

    # ---------- COMBINE ----------
    scalp_weight = 1.0 - ml_weight

    df["combined_signal"] = df.apply(
        lambda r: combine_signals(
            r["ml_signal"],
            r["scalp_signal"],
            ml_weight,
            scalp_weight,
        ),
        axis=1,
    )

    logger.info(f"Generated combined signals for {ticker}")
    return df


def calculate_position_size(
    capital: float,
    entry_price: float,
    stop_loss_price: float,
    risk_per_trade: float = RISK_PER_TRADE,
) -> int:
    """
    Risk-based position sizing.
    """
    risk_amount = capital * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss_price)

    if risk_per_share <= 0:
        return 0

    return int(risk_amount / risk_per_share)


def generate_signals_for_all_tickers(
    ml_weight: float = 0.6,
):
    """
    Generate combined signals for all configured tickers.
    """
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in DEFAULT_TICKERS:
        logger.info(f"⚙️ Generating signals for {ticker}")

        input_path = INDICATORS_DIR / f"{ticker}_features.csv"
        if not input_path.exists():
            logger.warning(f"Missing features for {ticker}, skipping")
            continue

        data = pd.read_csv(
            input_path,
            index_col=0,
            parse_dates=True,
        )

        signals = generate_combined_strategy(
            ticker,
            data,
            ml_weight=ml_weight,
        )

        output_path = SIGNALS_DIR / f"{ticker}_combined_signals.csv"
        signals.to_csv(output_path)

        logger.info(f"Saved signals → {output_path}")


if __name__ == "__main__":
    generate_signals_for_all_tickers(ml_weight=0.6)
