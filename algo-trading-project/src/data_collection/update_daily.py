"""
Update stock data with latest daily prices.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def update_ticker_data(ticker: str, data_dir: str = "data/raw") -> pd.DataFrame:
    """
    Update existing data file with latest prices.
    
    Args:
        ticker: Stock ticker symbol
        data_dir: Directory containing existing data files
    
    Returns:
        Updated DataFrame
    """
    filepath = Path(data_dir) / f"{ticker}.csv"
    
    if not filepath.exists():
        logger.warning(f"No existing data for {ticker}. Use download_data.py first.")
        return None
    
    # Load existing data
    existing_data = pd.read_csv(filepath, index_col=0, parse_dates=True)
    last_date = existing_data.index[-1]
    
    # Download new data
    today = datetime.now()
    if last_date.date() >= today.date():
        logger.info(f"{ticker} is already up to date")
        return existing_data
    
    start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    logger.info(f"Updating {ticker} from {start_date} to {end_date}")
    new_data = yf.download(ticker, start=start_date, end=end_date)
    
    if len(new_data) > 0:
        # Combine and save
        updated_data = pd.concat([existing_data, new_data])
        updated_data.to_csv(filepath)
        logger.info(f"Added {len(new_data)} new rows for {ticker}")
        return updated_data
    else:
        logger.info(f"No new data available for {ticker}")
        return existing_data


if __name__ == "__main__":
    # Example: Update multiple tickers
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    for ticker in tickers:
        update_ticker_data(ticker)

