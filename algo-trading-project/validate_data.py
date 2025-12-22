"""
Data validation and diagnostics script.
Check your Kaggle data setup before running training.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.logger import get_logger
from src.utils.config import DEFAULT_TICKERS, RAW_DATA_DIR
from src.data_collection.load_kaggle_data import load_kaggle_data
from src.utils.data_split import split_data_by_date, get_date_range

logger = get_logger(__name__)


def validate_data_setup():
    """
    Validate that all Kaggle data files are present and readable.
    """
    logger.info("="*70)
    logger.info("DATA VALIDATION & DIAGNOSTICS")
    logger.info("="*70)
    
    logger.info(f"\nExpected data directory: {RAW_DATA_DIR}")
    logger.info(f"Directory exists: {RAW_DATA_DIR.exists()}")
    
    if not RAW_DATA_DIR.exists():
        logger.error(f"❌ Data directory not found: {RAW_DATA_DIR}")
        return False
    
    # Check files
    logger.info(f"\n{'Ticker':<25} {'File Found':<12} {'Rows':<10} {'Date Range':<40}")
    logger.info("-" * 87)
    
    all_valid = True
    
    for ticker in DEFAULT_TICKERS:
        file_path = RAW_DATA_DIR / f"{ticker}_minute.csv"
        
        if file_path.exists():
            try:
                data = load_kaggle_data(ticker)
                rows = len(data)
                date_start, date_end = get_date_range(data)
                
                logger.info(
                    f"{ticker:<25} ✅ Yes          {rows:<10} "
                    f"{str(date_start):<20} to {str(date_end):<20}"
                )
            except Exception as e:
                logger.info(f"{ticker:<25} ⚠️  Error       - {str(e)[:40]}")
                all_valid = False
        else:
            logger.info(f"{ticker:<25} ❌ Missing      -")
            all_valid = False
    
    # Check date coverage
    logger.info(f"\n{'Date Coverage Analysis':<70}")
    logger.info("-" * 70)
    
    train_periods = []
    test_periods = []
    
    for ticker in DEFAULT_TICKERS:
        try:
            data = load_kaggle_data(ticker)
            train_data, test_data = split_data_by_date(data)
            
            if len(train_data) > 0:
                train_periods.append((
                    ticker,
                    train_data.index[0],
                    train_data.index[-1],
                    len(train_data)
                ))
            
            if len(test_data) > 0:
                test_periods.append((
                    ticker,
                    test_data.index[0],
                    test_data.index[-1],
                    len(test_data)
                ))
        except Exception as e:
            logger.warning(f"Could not split data for {ticker}: {e}")
    
    if train_periods:
        logger.info("\nTraining Data (2015-2023):")
        for ticker, start, end, count in train_periods:
            logger.info(f"  {ticker:<25} {count:>8} rows | {start.date()} to {end.date()}")
    
    if test_periods:
        logger.info("\nTest Data (2024):")
        for ticker, start, end, count in test_periods:
            logger.info(f"  {ticker:<25} {count:>8} rows | {start.date()} to {end.date()}")
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("SUMMARY")
    logger.info(f"{'='*70}")
    
    tickers_available = sum(1 for ticker in DEFAULT_TICKERS 
                           if (RAW_DATA_DIR / f"{ticker}_minute.csv").exists())
    
    logger.info(f"Total tickers configured: {len(DEFAULT_TICKERS)}")
    logger.info(f"Tickers with data files: {tickers_available}/{len(DEFAULT_TICKERS)}")
    logger.info(f"Training periods found: {len(train_periods)}")
    logger.info(f"Test periods found: {len(test_periods)}")
    
    if all_valid and tickers_available == len(DEFAULT_TICKERS):
        logger.info("\n✅ Data setup is valid! Ready to train models.")
        return True
    else:
        logger.warning(
            f"\n⚠️  Some data issues detected. "
            f"Please ensure all CSV files are in {RAW_DATA_DIR}"
        )
        return False


def sample_data_preview():
    """
    Preview sample data from first available ticker.
    """
    logger.info(f"\n{'='*70}")
    logger.info("DATA SAMPLE PREVIEW")
    logger.info(f"{'='*70}\n")
    
    for ticker in DEFAULT_TICKERS:
        try:
            data = load_kaggle_data(ticker)
            
            logger.info(f"Sample from {ticker}:")
            logger.info(f"\nFirst 5 rows:")
            logger.info(f"{data.head(5)}\n")
            
            logger.info(f"Data info:")
            logger.info(f"  Shape: {data.shape}")
            logger.info(f"  Columns: {list(data.columns)}")
            logger.info(f"  Data types:\n{data.dtypes}\n")
            
            break  # Show only first available
        except Exception as e:
            continue


if __name__ == "__main__":
    # Run validation
    is_valid = validate_data_setup()
    
    # Show sample
    sample_data_preview()
    
    # Final guidance
    if is_valid:
        logger.info("\n✅ You're ready to run: python run_pipeline.py")
    else:
        logger.info("\n❌ Please fix the data issues before training.")
