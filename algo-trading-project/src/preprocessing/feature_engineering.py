"""
Feature engineering: Add technical indicators and derived features.
"""
import pandas as pd
import numpy as np
import pandas_ta as ta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add common technical indicators to OHLCV data.
    
    Args:
        data: OHLCV DataFrame
    
    Returns:
        DataFrame with additional indicator columns
    """
    df = data.copy()
    
    # Moving averages
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    df['EMA_12'] = ta.ema(df['Close'], length=12)
    df['EMA_26'] = ta.ema(df['Close'], length=26)
    
    # RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # MACD
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    
    # Bollinger Bands
    bbands = ta.bbands(df['Close'], length=20)
    df = pd.concat([df, bbands], axis=1)
    
    # ATR (Average True Range)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    
    # Volume indicators
    df['Volume_SMA'] = ta.sma(df['Volume'], length=20)
    
    # Stochastic
    stoch = ta.stoch(df['High'], df['Low'], df['Close'])
    df = pd.concat([df, stoch], axis=1)
    
    logger.info(f"Added technical indicators. Total columns: {len(df.columns)}")
    return df


def add_price_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add price-based features.
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        DataFrame with additional price features
    """
    df = data.copy()
    
    # Returns
    df['returns'] = df['Close'].pct_change()
    df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Price range
    df['range'] = df['High'] - df['Low']
    df['range_pct'] = (df['High'] - df['Low']) / df['Close']
    
    # Gap
    df['gap'] = df['Open'] - df['Close'].shift(1)
    df['gap_pct'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)
    
    # Volatility
    df['volatility'] = df['returns'].rolling(window=20).std()
    
    logger.info(f"Added price features")
    return df


def create_lag_features(data: pd.DataFrame, columns: list, lags: int = 5) -> pd.DataFrame:
    """
    Create lagged features for specified columns.
    
    Args:
        data: Input DataFrame
        columns: List of column names to create lags for
        lags: Number of lag periods
    
    Returns:
        DataFrame with lagged features
    """
    df = data.copy()
    
    for col in columns:
        if col in df.columns:
            for lag in range(1, lags + 1):
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    logger.info(f"Created {lags} lag features for {len(columns)} columns")
    return df


if __name__ == "__main__":
    # Example usage
    data = pd.read_csv("data/processed/AAPL_cleaned.csv", index_col=0, parse_dates=True)
    data = add_technical_indicators(data)
    data = add_price_features(data)
    data = create_lag_features(data, ['Close', 'Volume', 'RSI'], lags=3)
    data.to_csv("data/indicators/AAPL_features.csv")

