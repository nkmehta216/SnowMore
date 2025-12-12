"""
Download historical stock data using yfinance.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def download_stock_data(ticker: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
    """
    Download stock data from Yahoo Finance.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (1m, 5m, 15m, 1h, 1d, etc.)
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        logger.info(f"Downloading {ticker} data from {start_date} to {end_date}")
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        logger.info(f"Downloaded {len(data)} rows for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {e}")
        raise


def save_data(data: pd.DataFrame, ticker: str, output_dir: str = "data/raw"):
    """
    Save downloaded data to CSV file.
    
    Args:
        data: DataFrame containing stock data
        ticker: Stock ticker symbol
        output_dir: Directory to save the data
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path(output_dir) / f"{ticker}.csv"
    data.to_csv(filepath)
    logger.info(f"Saved data to {filepath}")


if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    start = "2020-01-01"
    end = "2024-12-12"
    
    data = download_stock_data(ticker, start, end)
    save_data(data, ticker)

