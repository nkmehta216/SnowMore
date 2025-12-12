"""
Combine ML predictions with scalping signals.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from modeling.model_utils import load_model, predict
from strategy.scalping_logic import calculate_scalping_signals

logger = get_logger(__name__)


def combine_signals(ml_signal: int, scalp_signal: int, 
                    ml_weight: float = 0.6, scalp_weight: float = 0.4) -> int:
    """
    Combine ML and scalping signals with weights.
    
    Args:
        ml_signal: ML model signal (-1, 0, 1)
        scalp_signal: Scalping signal (-1, 0, 1)
        ml_weight: Weight for ML signal
        scalp_weight: Weight for scalping signal
    
    Returns:
        Combined signal
    """
    combined = (ml_signal * ml_weight) + (scalp_signal * scalp_weight)
    
    # Convert to discrete signal
    if combined > 0.5:
        return 1  # Buy
    elif combined < -0.5:
        return -1  # Sell
    else:
        return 0  # Hold


def generate_combined_strategy(ticker: str, data: pd.DataFrame, 
                               ml_weight: float = 0.6) -> pd.DataFrame:
    """
    Generate trading signals using combined ML + scalping strategy.
    
    Args:
        ticker: Stock ticker
        data: DataFrame with features
        ml_weight: Weight for ML predictions (scalping gets 1-ml_weight)
    
    Returns:
        DataFrame with combined signals
    """
    df = data.copy()
    
    # Get ML predictions
    try:
        model, scaler, features = load_model(ticker)
        ml_preds, ml_probs = predict(model, scaler, features, df)
        df['ml_signal'] = (ml_preds * 2) - 1  # Convert 0/1 to -1/1
    except FileNotFoundError:
        logger.warning(f"No model found for {ticker}, using scalping only")
        df['ml_signal'] = 0
        ml_weight = 0
    
    # Get scalping signals
    df = calculate_scalping_signals(df)
    
    # Normalize scalping signals to -1, 0, 1
    if 'scalp_signal' in df.columns:
        df['scalp_signal'] = np.clip(df['scalp_signal'], -1, 1)
    else:
        df['scalp_signal'] = 0
    
    # Combine signals
    scalp_weight = 1 - ml_weight
    df['combined_signal'] = df.apply(
        lambda row: combine_signals(row['ml_signal'], row['scalp_signal'], 
                                   ml_weight, scalp_weight),
        axis=1
    )
    
    logger.info(f"Generated combined strategy signals for {ticker}")
    return df


def calculate_position_size(capital: float, risk_per_trade: float, 
                            entry_price: float, stop_loss_price: float) -> int:
    """
    Calculate position size based on risk management.
    
    Args:
        capital: Available capital
        risk_per_trade: Risk percentage per trade (e.g., 0.02 for 2%)
        entry_price: Entry price
        stop_loss_price: Stop loss price
    
    Returns:
        Number of shares to trade
    """
    risk_amount = capital * risk_per_trade
    price_diff = abs(entry_price - stop_loss_price)
    
    if price_diff == 0:
        return 0
    
    shares = int(risk_amount / price_diff)
    return shares


if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    data = pd.read_csv("data/indicators/AAPL_features.csv", index_col=0, parse_dates=True)
    result = generate_combined_strategy(ticker, data, ml_weight=0.6)
    result.to_csv(f"data/signals/{ticker}_combined_signals.csv")

