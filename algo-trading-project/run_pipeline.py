"""
Master script to train models on Kaggle data (2015-2023) and backtest on 2024.
This is the main entry point for the entire workflow.
"""
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.logger import get_logger
from src.utils.config import (
    DEFAULT_TICKERS,
    TRAIN_START,
    TRAIN_END,
    TEST_START,
    TEST_END,
)
from src.preprocessing.clean_data import clean_all_tickers
from src.modeling.train_model import train_all_tickers
from src.strategy.backtest_2024 import backtest_all_tickers_on_2024

logger = get_logger(__name__)


def main():
    """
    Complete workflow:
    1. Clean Kaggle raw data
    2. Train models on 2015-2023 data
    3. Backtest on 2024 data
    """
    
    logger.info("="*70)
    logger.info("ALGO TRADING BOT - KAGGLE DATA TRAINING & BACKTESTING PIPELINE")
    logger.info("="*70)
    logger.info(f"\nConfiguration:")
    logger.info(f"  Tickers: {', '.join(DEFAULT_TICKERS)}")
    logger.info(f"  Train Period: {TRAIN_START} to {TRAIN_END}")
    logger.info(f"  Test Period: {TEST_START} to {TEST_END}")
    logger.info(f"\n{'='*70}\n")
    
    # Step 1: Clean data
    logger.info("STEP 1: Cleaning Kaggle data...")
    logger.info("-" * 70)
    try:
        clean_all_tickers()
        logger.info("✅ Data cleaning completed\n")
    except Exception as e:
        logger.error(f"❌ Data cleaning failed: {e}\n")
        return
    
    # Step 2: Train models
    logger.info("STEP 2: Training ML models (2015-2023)...")
    logger.info("-" * 70)
    try:
        training_results = train_all_tickers()
        
        logger.info("\nTraining Results Summary:")
        for ticker, result in training_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                logger.info(
                    f"  ✅ {ticker}: {result['train_samples']} train | "
                    f"{result['test_samples']} test | "
                    f"Accuracy: {result.get('test_accuracy', 'N/A')}"
                )
            else:
                logger.info(f"  ❌ {ticker}: {result.get('error', 'Unknown error')}")
        
        logger.info("\n")
    except Exception as e:
        logger.error(f"❌ Model training failed: {e}\n")
        return
    
    # Step 3: Backtest on 2024 data
    logger.info("STEP 3: Backtesting on 2024 data...")
    logger.info("-" * 70)
    try:
        backtest_results = backtest_all_tickers_on_2024()
        logger.info("\n✅ Backtesting completed")
    except Exception as e:
        logger.error(f"❌ Backtesting failed: {e}\n")
        return
    
    # Final Summary
    logger.info("\n" + "="*70)
    logger.info("FINAL SUMMARY")
    logger.info("="*70)
    
    # Prepare summary table
    summary_data = []
    for ticker in DEFAULT_TICKERS:
        train_result = training_results.get(ticker, {})
        backtest_result = backtest_results.get(ticker, {})
        
        summary_data.append({
            "Ticker": ticker,
            "Train Status": train_result.get("status", "N/A"),
            "Test Accuracy": f"{train_result.get('test_accuracy', 0)*100:.2f}%" if train_result.get("test_accuracy") else "N/A",
            "Backtest Status": backtest_result.get("status", "N/A"),
            "Return (2024)": f"{backtest_result.get('total_return', 0)*100:.2f}%" if backtest_result.get("total_return") else "N/A",
            "Sharpe Ratio": f"{backtest_result.get('sharpe', 0):.4f}" if backtest_result.get("sharpe") else "N/A",
            "Win Rate": f"{backtest_result.get('win_rate', 0)*100:.2f}%" if backtest_result.get("win_rate") else "N/A",
            "Trades": backtest_result.get("total_trades", 0),
        })
    
    summary_df = pd.DataFrame(summary_data)
    logger.info(f"\n{summary_df.to_string(index=False)}")
    
    logger.info("\n" + "="*70)
    logger.info("Pipeline execution completed!")
    logger.info("="*70)


if __name__ == "__main__":
    main()
