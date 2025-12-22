# Kaggle Data Integration - Code Modifications

## Summary of Changes

Your algo trading bot has been updated to work with Kaggle data instead of yfinance. The training period is now **2015-2023** and testing is on **2024** data.

## Modified Files

### 1. **Configuration (`src/utils/config.py`)**
- ✅ Added `RAW_DATA_DIR` pointing to `data/raw`
- ✅ Added `PROCESSED_DATA_DIR` pointing to `data/processed`
- ✅ Updated `DEFAULT_TICKERS` to Indian indices from Kaggle:
  - `NIFTY BANK`
  - `NIFTY COMMODITIES`
  - `NIFTY CONSUMPTION`
  - `NIFTY FIN SERVICE`
  - `NIFTY INDIA MFG`
  - `INDIA VIX`
- ✅ Added date ranges:
  - `TRAIN_START = "2015-01-01"` → `TRAIN_END = "2023-12-31"`
  - `TEST_START = "2024-01-01"` → `TEST_END = "2024-12-31"`
- ✅ Added ML parameters: `TEST_SIZE`, `RANDOM_STATE`, `N_ESTIMATORS`

### 2. **Data Loading (`src/data_collection/load_kaggle_data.py`)**
- ✅ **NEW FILE**: Replaces yfinance with Kaggle CSV loader
- Loads data from `data/raw/{ticker}_minute.csv`
- Automatically standardizes column names (date → Date, open → Open, etc.)
- Handles minute-level data with datetime parsing

### 3. **Data Cleaning (`src/preprocessing/clean_data.py`)**
- ✅ Updated to use `load_kaggle_data()` function
- Removed yfinance-specific code
- Handles Kaggle's lowercase column names automatically
- Processes all tickers from raw folder

### 4. **Data Splitting (`src/utils/data_split.py`)**
- ✅ **NEW FILE**: `split_data_by_date()` function
  - Splits data by date range instead of random split
  - Maintains chronological order for time series
  - 2015-2023 for training, 2024 for testing

### 5. **Model Training (`src/modeling/train_model.py`)**
- ✅ Updated `prepare_features_with_date_split()`:
  - Uses date-based splitting instead of `train_test_split`
  - Preserves temporal order (no shuffling)
  - Trains on 2015-2023, tests on 2024
- ✅ Updated `train_all_tickers()`:
  - Loads raw Kaggle data
  - Cleans and adds features
  - Uses date-based split
  - Returns training accuracy for each ticker

### 6. **Backtesting (`src/strategy/backtest_2024.py`)**
- ✅ **NEW FILE**: Dedicated 2024 backtesting script
- Backtests trained models on 2024 data only
- Generates trading signals and runs backtest engine
- Returns detailed metrics (return, sharpe, win rate, etc.)

### 7. **Master Pipeline (`run_pipeline.py`)**
- ✅ **NEW FILE**: Orchestrates entire workflow:
  1. Clean Kaggle data
  2. Train models (2015-2023)
  3. Backtest (2024)
  4. Print comprehensive summary

## How to Run

### Run Everything (Recommended)
```bash
cd c:\Users\Sunay Bhattacharjee\Desktop\AlgoTrading bot project\SnowMore\algo-trading-project
python run_pipeline.py
```

### Run Individual Steps

**1. Clean Data**
```bash
python src/preprocessing/clean_data.py
```

**2. Train Models**
```bash
python src/modeling/train_model.py
```

**3. Backtest on 2024**
```bash
python src/strategy/backtest_2024.py
```

## Data Format

Your Kaggle CSV files should have this structure (already in your raw folder):
```csv
date,open,high,low,close,volume
2015-01-09 09:15:00,18845.9,18845.9,18801.7,18801.7,0
2015-01-09 09:16:00,18801.7,18806.05,18790.2,18794.65,0
...
```

The code automatically:
- Standardizes column names to capitalized (Date, Open, High, Low, Close, Volume)
- Parses datetime properly
- Handles missing values
- Removes outliers

## Key Features

✅ **Date-based splitting**: No lookahead bias, respects time series order
✅ **2015-2023 training**: 9 years of data for robust model training
✅ **2024 testing**: Real out-of-sample testing period
✅ **Minute-level data**: High-frequency scalping signals
✅ **Automatic ticker handling**: Works with all Kaggle index files
✅ **Comprehensive metrics**: Sharpe ratio, win rate, max drawdown, etc.

## Troubleshooting

**No data loaded?**
- Ensure CSV files are in `data/raw/` with correct names: `{TICKER}_minute.csv`
- Check that column names are lowercase: date, open, high, low, close, volume

**Import errors?**
- Make sure you're running from the project root directory
- Verify `src/` folder structure is correct

**Model training slow?**
- First run processes all data - this is normal
- Minute-level data means lots of rows
- Consider using a subset if needed

## Next Steps

1. ✅ All data is ready to use
2. Run the pipeline to train models
3. Evaluate 2024 backtest performance
4. Optimize strategy parameters if needed
5. Deploy to live trading (with caution!)

## Configuration Options

Edit `src/utils/config.py` to customize:
- `INITIAL_CAPITAL`: Starting capital for backtest
- `COMMISSION_RATE`: Trading commission percentage
- `RISK_PER_TRADE`: Risk percentage per trade
- `STOP_LOSS_PCT` / `TAKE_PROFIT_PCT`: Position management
- `TRAIN_START`, `TRAIN_END`: Training period
- `TEST_START`, `TEST_END`: Testing period
