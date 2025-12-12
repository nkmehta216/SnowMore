"""
Scalping strategy logic for short-term trading.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def calculate_scalping_signals(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate scalping signals based on technical indicators.
    
    Args:
        data: DataFrame with OHLCV and indicators
    
    Returns:
        DataFrame with scalping signals
    """
    df = data.copy()
    
    # Initialize signal column
    df['scalp_signal'] = 0
    
    # RSI-based signals
    if 'RSI' in df.columns:
        df.loc[df['RSI'] < 30, 'scalp_signal'] = 1  # Oversold - Buy
        df.loc[df['RSI'] > 70, 'scalp_signal'] = -1  # Overbought - Sell
    
    # Bollinger Bands signals
    if all(col in df.columns for col in ['BBL_20_2.0', 'BBU_20_2.0']):
        df.loc[df['Close'] < df['BBL_20_2.0'], 'scalp_signal'] = 1  # Below lower band - Buy
        df.loc[df['Close'] > df['BBU_20_2.0'], 'scalp_signal'] = -1  # Above upper band - Sell
    
    # MACD crossover
    if all(col in df.columns for col in ['MACD_12_26_9', 'MACDs_12_26_9']):
        df['macd_cross'] = np.where(
            (df['MACD_12_26_9'] > df['MACDs_12_26_9']) & 
            (df['MACD_12_26_9'].shift(1) <= df['MACDs_12_26_9'].shift(1)), 
            1, 0
        )
        df['macd_cross_down'] = np.where(
            (df['MACD_12_26_9'] < df['MACDs_12_26_9']) & 
            (df['MACD_12_26_9'].shift(1) >= df['MACDs_12_26_9'].shift(1)), 
            -1, 0
        )
        df['scalp_signal'] += df['macd_cross'] + df['macd_cross_down']
    
    # Volume spike detection
    if 'Volume' in df.columns:
        df['vol_ma'] = df['Volume'].rolling(window=20).mean()
        df['vol_spike'] = df['Volume'] > (df['vol_ma'] * 1.5)
        # Amplify signals on high volume
        df.loc[df['vol_spike'], 'scalp_signal'] *= 1.5
    
    logger.info(f"Generated scalping signals for {len(df)} rows")
    return df


def apply_stop_loss_take_profit(entry_price: float, signal: int, 
                                 stop_loss_pct: float = 0.02, 
                                 take_profit_pct: float = 0.03) -> dict:
    """
    Calculate stop loss and take profit levels.
    
    Args:
        entry_price: Entry price
        signal: Trading signal (1 for buy, -1 for sell)
        stop_loss_pct: Stop loss percentage
        take_profit_pct: Take profit percentage
    
    Returns:
        Dictionary with stop_loss and take_profit prices
    """
    if signal == 1:  # Long position
        stop_loss = entry_price * (1 - stop_loss_pct)
        take_profit = entry_price * (1 + take_profit_pct)
    elif signal == -1:  # Short position
        stop_loss = entry_price * (1 + stop_loss_pct)
        take_profit = entry_price * (1 - take_profit_pct)
    else:
        stop_loss = take_profit = entry_price
    
    return {
        'stop_loss': stop_loss,
        'take_profit': take_profit
    }


def detect_breakout(data: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
    """
    Detect price breakouts.
    
    Args:
        data: DataFrame with OHLCV data
        lookback: Lookback period for high/low detection
    
    Returns:
        DataFrame with breakout signals
    """
    df = data.copy()
    
    df['high_roll'] = df['High'].rolling(window=lookback).max()
    df['low_roll'] = df['Low'].rolling(window=lookback).min()
    
    df['breakout_up'] = (df['Close'] > df['high_roll'].shift(1)).astype(int)
    df['breakout_down'] = (df['Close'] < df['low_roll'].shift(1)).astype(int) * -1
    
    df['breakout_signal'] = df['breakout_up'] + df['breakout_down']
    
    logger.info(f"Detected {df['breakout_signal'].abs().sum()} breakouts")
    return df


if __name__ == "__main__":
    # Example usage
    data = pd.read_csv("data/indicators/AAPL_features.csv", index_col=0, parse_dates=True)
    data = calculate_scalping_signals(data)
    data = detect_breakout(data)
    data.to_csv("data/signals/AAPL_scalp_signals.csv")

