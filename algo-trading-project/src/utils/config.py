"""
Configuration settings for the project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INDICATORS_DIR = DATA_DIR / "indicators"
SIGNALS_DIR = DATA_DIR / "signals"
MODELS_DIR = PROJECT_ROOT / "models"

# Trading parameters (NIFTY 50 – free via yfinance)
DEFAULT_TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
]

INITIAL_CAPITAL = 100000
COMMISSION_RATE = 0.001
RISK_PER_TRADE = 0.02

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
