"""
Clean and preprocess stock data.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def clean_ohlcv_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean OHLCV data by handling missing values and outliers.
    
    Args:
        data: Raw OHLCV DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    df = data.copy()
    
    # Remove duplicates
    df = df[~df.index.duplicated(keep='first')]
    
    # Handle missing values
    if df.isnull().sum().sum() > 0:
        logger.warning(f"Found {df.isnull().sum().sum()} missing values")
        df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Remove zero volume rows (non-trading days)
    if 'Volume' in df.columns:
        df = df[df['Volume'] > 0]
    
    # Check for price anomalies
    for col in ['Open', 'High', 'Low', 'Close']:
        if col in df.columns:
            q1 = df[col].quantile(0.01)
            q99 = df[col].quantile(0.99)
            df = df[(df[col] >= q1) & (df[col] <= q99)]
    
    logger.info(f"Cleaned data: {len(df)} rows remaining")
    return df


def resample_data(data: pd.DataFrame, timeframe: str = "1H") -> pd.DataFrame:
    """
    Resample data to different timeframe.
    
    Args:
        data: OHLCV DataFrame
        timeframe: Target timeframe (e.g., '5min', '1H', '1D')
    
    Returns:
        Resampled DataFrame
    """
    resampled = data.resample(timeframe).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    logger.info(f"Resampled to {timeframe}: {len(resampled)} rows")
    return resampled


if __name__ == "__main__":
    # Example usage
    data = pd.read_csv("data/raw/AAPL.csv", index_col=0, parse_dates=True)
    cleaned = clean_ohlcv_data(data)
    cleaned.to_csv("data/processed/AAPL_cleaned.csv")

