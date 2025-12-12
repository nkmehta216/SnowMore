"""
Configuration settings for the project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INDICATORS_DIR = DATA_DIR / "indicators"
SIGNALS_DIR = DATA_DIR / "signals"
MODELS_DIR = PROJECT_ROOT / "models"

# API Keys (load from .env file)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Trading parameters
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
INITIAL_CAPITAL = 100000
COMMISSION_RATE = 0.001  # 0.1%
RISK_PER_TRADE = 0.02  # 2%

# Model parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42
N_ESTIMATORS = 100

# Technical indicator parameters
RSI_PERIOD = 14
SMA_PERIODS = [20, 50, 200]
EMA_PERIODS = [12, 26]
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2.0
ATR_PERIOD = 14

# Scalping parameters
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
STOP_LOSS_PCT = 0.02
TAKE_PROFIT_PCT = 0.03
BREAKOUT_LOOKBACK = 20

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000


def get_config():
    """
    Get configuration dictionary.
    
    Returns:
        Dictionary with all configuration settings
    """
    return {
        'paths': {
            'project_root': str(PROJECT_ROOT),
            'data_dir': str(DATA_DIR),
            'raw_data': str(RAW_DATA_DIR),
            'processed_data': str(PROCESSED_DATA_DIR),
            'indicators': str(INDICATORS_DIR),
            'signals': str(SIGNALS_DIR),
            'models': str(MODELS_DIR)
        },
        'trading': {
            'tickers': DEFAULT_TICKERS,
            'initial_capital': INITIAL_CAPITAL,
            'commission_rate': COMMISSION_RATE,
            'risk_per_trade': RISK_PER_TRADE
        },
        'model': {
            'test_size': TEST_SIZE,
            'random_state': RANDOM_STATE,
            'n_estimators': N_ESTIMATORS
        },
        'indicators': {
            'rsi_period': RSI_PERIOD,
            'sma_periods': SMA_PERIODS,
            'ema_periods': EMA_PERIODS,
            'macd': {'fast': MACD_FAST, 'slow': MACD_SLOW, 'signal': MACD_SIGNAL},
            'bollinger': {'period': BB_PERIOD, 'std': BB_STD},
            'atr_period': ATR_PERIOD
        },
        'scalping': {
            'rsi_oversold': RSI_OVERSOLD,
            'rsi_overbought': RSI_OVERBOUGHT,
            'stop_loss_pct': STOP_LOSS_PCT,
            'take_profit_pct': TAKE_PROFIT_PCT,
            'breakout_lookback': BREAKOUT_LOOKBACK
        }
    }

