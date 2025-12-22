## Quick Start Guide - Kaggle Data Training & Testing

### What Changed?
Your trading bot now:
- ✅ Loads data directly from Kaggle CSV files (no yfinance)
- ✅ Trains models on historical data 2015-2023
- ✅ Tests on 2024 data only
- ✅ Uses Indian stock indices (NIFTY BANK, NIFTY COMMODITIES, etc.)

### Files You Already Have ✅
- `data/raw/NIFTY BANK_minute.csv`
- `data/raw/NIFTY COMMODITIES_minute.csv`
- `data/raw/NIFTY CONSUMPTION_minute.csv`
- `data/raw/NIFTY FIN SERVICE_minute.csv`
- `data/raw/NIFTY INDIA MFG_minute.csv`
- `data/raw/INDIA VIX_minute.csv`

### Step-by-Step Instructions

#### 1️⃣ Validate Your Data
```bash
cd "c:\Users\Sunay Bhattacharjee\Desktop\AlgoTrading bot project\SnowMore\algo-trading-project"
python validate_data.py
```
This checks if all Kaggle files are readable and shows data coverage.

#### 2️⃣ Run Full Pipeline (Recommended)
```bash
python run_pipeline.py
```
This automatically:
- Cleans all Kaggle data
- Trains ML models (2015-2023)
- Backtests on 2024
- Prints comprehensive results

**Expected Output:**
```
STEP 1: Cleaning Kaggle data...
✅ Data cleaning completed

STEP 2: Training ML models (2015-2023)...
✅ NIFTY BANK: 100000 train | 15000 test | Accuracy: 0.5234
✅ NIFTY COMMODITIES: 95000 train | 14500 test | Accuracy: 0.5189
...

STEP 3: Backtesting on 2024 data...
📊 Backtesting NIFTY BANK on 2024 data
✅ NIFTY BANK Backtest Results:
   Final Equity: $105234.50
   Total Return: 5.23%
   Win Rate: 52.34%
```

---

### Or Run Individual Steps

**Just clean data:**
```bash
python src/preprocessing/clean_data.py
```

**Just train models:**
```bash
python src/modeling/train_model.py
```

**Just backtest 2024:**
```bash
python src/strategy/backtest_2024.py
```

---

### Customization

Edit `src/utils/config.py` to change:

```python
# Change initial capital for backtest
INITIAL_CAPITAL = 100000.0  # → change to your amount

# Change training/testing dates
TRAIN_START = "2015-01-01"  # → change to different start
TRAIN_END = "2023-12-31"    # → change to different end
TEST_START = "2024-01-01"   # → change to different test start
TEST_END = "2024-12-31"     # → change to different test end

# Change tickers
DEFAULT_TICKERS = [
    "NIFTY BANK",
    "NIFTY COMMODITIES",
    # Add/remove as needed
]
```

---

### Output Files Created

After running, you'll have:
- `data/processed/` - Cleaned OHLCV data
- `models/` - Trained ML models + scalers
  - `{TICKER}_model.pkl` - Trained model
  - `{TICKER}_scaler.pkl` - Feature scaler
  - `{TICKER}_features.pkl` - Feature names

---

### Troubleshooting

**Error: "No such file or directory: data/raw"**
- Make sure your CSV files are in `data/raw/` folder
- File names must be exactly: `{TICKER}_minute.csv`

**Error: "No training data for NIFTY BANK"**
- Check if your data has dates in 2015-2023 range
- Run `validate_data.py` to check date coverage

**Models not improving?**
- Make sure you have enough data (check `validate_data.py` output)
- Consider adjusting hyperparameters in `src/utils/config.py`
- Try different ML model combinations in `train_model.py`

---

### What Happens Internally

1. **Data Loading** (`load_kaggle_data.py`)
   - Reads CSV from `data/raw/`
   - Standardizes column names (date → Date, open → Open)
   - Parses datetime correctly

2. **Data Cleaning** (`clean_data.py`)
   - Removes duplicates
   - Handles missing values
   - Removes outliers
   - Saves cleaned data to `data/processed/`

3. **Feature Engineering**
   - Adds technical indicators (SMA, RSI, etc.)
   - Creates lag features
   - Prepares features for ML

4. **Model Training** (`train_model.py`)
   - **Date-based split**: 2015-2023 train, 2024 test
   - No lookahead bias
   - Preserves time series order
   - Trains Stacked Ensemble:
     - RandomForest
     - XGBoost (if available)
     - GradientBoosting
     - Meta-learner (LogisticRegression)

5. **Backtesting** (`backtest_2024.py`)
   - Generates trading signals
   - Combines ML + scalping signals
   - Runs backtest on 2024 data only
   - Calculates metrics:
     - Total return
     - Sharpe ratio
     - Win rate
     - Max drawdown

---

### Key Differences from Old Code

| Feature | Old (yfinance) | New (Kaggle) |
|---------|---|---|
| Data source | Yahoo Finance API | Local CSV files |
| Date range | Configurable | 2015-2023 (train), 2024 (test) |
| Train/Test split | Random (shuffle=False) | Date-based (chronological) |
| Tickers | US stocks (AAPL, MSFT) | Indian indices |
| Data frequency | Daily | **Minute-level** |

---

### Performance Notes

- **First run will be slow** (minute-level data = lots of rows)
- Processing 9 years of minute data takes 5-15 minutes
- Subsequent runs use cached cleaned data
- Training time depends on data size and CPU cores

---

### Need Help?

1. Check logs in terminal output
2. Run `validate_data.py` to diagnose data issues
3. Verify CSV files are in correct location
4. Check column names in raw CSV files

---

### Next Steps

1. ✅ Run `validate_data.py` to confirm setup
2. ✅ Run `python run_pipeline.py` to train & test
3. ✅ Review backtest results
4. ✅ Optimize strategy parameters if needed
5. ✅ Deploy to live trading (with risk management!)

**Good luck! 🚀**
