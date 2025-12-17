"""
Download historical stock data using yfinance.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.config import DEFAULT_TICKERS

logger = get_logger(__name__)


def download_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Download stock data from Yahoo Finance.
    """
    try:
        logger.info(f"Downloading {ticker} data from {start_date} to {end_date}")
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False
        )
        logger.info(f"Downloaded {len(data)} rows for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {e}")
        raise


def save_data(data: pd.DataFrame, ticker: str, output_dir: str = "data/raw"):
    """
    Save downloaded data to CSV file.
    """
    # Ensure we save to the project's raw data folder (absolute path)
    if output_dir == "data/raw":
        output_dir = "C:/Users/Nihar/Documents/GitHub/oop/SnowMore/algo-trading-project/data/raw"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path(output_dir) / f"{ticker}.csv"
    data.to_csv(filepath)
    logger.info(f"Saved data to {filepath}")


def download_all_tickers(
    start_date: str = "2020-01-01",
    end_date: str = "2024-12-12"
):
    """
    Download and save data for all configured tickers.
    """
    for ticker in DEFAULT_TICKERS:
        logger.info(f"Starting download for {ticker}")
        data = download_stock_data(ticker, start_date, end_date)

        if not data.empty:
            save_data(data, ticker)
        else:
            logger.warning(f"No data returned for {ticker}")


if __name__ == "__main__":
    download_all_tickers()
