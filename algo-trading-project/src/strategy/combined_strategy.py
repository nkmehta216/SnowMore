"""
Combine ML predictions with scalping signals.
"""

import pandas as pd
import numpy as np

from src.utils.logger import get_logger
from src.strategy.scalping_logic import calculate_scalping_signals

logger = get_logger(__name__)


def combine_signals(
    ml_signal: int,
    scalp_signal: int,
    ml_weight: float,
    scalp_weight: float,
) -> int:
    score = (ml_signal * ml_weight) + (scalp_signal * scalp_weight)

    if score >= 0.3:
        return 1
    elif score <= -0.3:
        return -1
    else:
        return 0


def generate_combined_strategy(
    ticker: str,
    data: pd.DataFrame,
    base_ml_weight: float = 0.6,
) -> pd.DataFrame:
    """
    Generate combined ML + scalping trading signals.
    """
    df = data.copy()

    # -------- ML SIGNAL (disabled for now) --------
    df["ml_signal"] = 0

    # -------- SCALPING SIGNAL --------
    df = calculate_scalping_signals(df)

    if "scalp_signal" not in df.columns:
        df["scalp_signal"] = 0

    ml_weight = base_ml_weight
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

    logger.info(
        f"{ticker} | Combined signals generated "
        f"(ML={ml_weight}, Scalp={scalp_weight})"
    )

    return df
