# 🚀 Streamlit Website - Setup Guide

## What Was Created

Your AlgoTrading Bot now has a professional web dashboard! Here's what you got:

### 📁 New Files Created:

1. **`app.py`** - Main Streamlit application (1200+ lines)
   - Complete interactive dashboard
   - 4 main tabs: Overview, Charts, Backtest, Statistics
   - Real-time technical indicators
   - Trading signal visualization

2. **`requirements-streamlit.txt`** - Dependencies for the dashboard
   - Streamlit 1.28.1
   - Plotly for interactive charts
   - All ML libraries (scikit-learn, XGBoost, etc.)

3. **`.streamlit/config.toml`** - Streamlit configuration
   - Custom theme with professional colors
   - Port configuration
   - Server settings

4. **`start_streamlit.bat`** - One-click launcher (Windows)
   - Automatically activates virtual environment
   - Starts Streamlit server
   - Opens dashboard at localhost:8501

5. **`setup_streamlit.py`** - Automated setup script
   - Installs all dependencies
   - Verifies installation
   - Checks project structure

6. **`STREAMLIT_README.md`** - Complete documentation
   - Feature descriptions
   - Installation guide
   - Usage instructions
   - Troubleshooting tips

---

## ⚡ Quick Start

### Step 1: Install Dependencies
Run the setup script:
```bash
python setup_streamlit.py
```

Or manually:
```bash
pip install -r requirements-streamlit.txt
```

### Step 2: Start the Dashboard
**Windows:** Double-click `start_streamlit.bat`

**Or run:**
```bash
streamlit run app.py
```

### Step 3: Open in Browser
```
http://localhost:8501
```

---

## 📊 Dashboard Features

### Tab 1: Overview
- Current price and price change
- RSI with overbought/oversold status
- Current trading signal (Buy/Sell/Neutral)
- SMA 20 and SMA 50 values
- Strategy information
- Data period summary

### Tab 2: Charts & Signals
- **Price Chart**: Shows price with BUY (🟢) and SELL (🔴) signals
- **SMA Trendlines**: 20 and 50-period moving averages
- **RSI Indicator**: With 70 (overbought) and 30 (oversold) zones
- **MACD Indicator**: With signal line and histogram
- **Recent Signals Table**: Last 20 signals with all indicator values

### Tab 3: Backtest Results
- **Performance Metrics**:
  - Total Return %
  - Annual Return %
  - Sharpe Ratio
  - Maximum Drawdown %
  - Win Rate %
- **Cumulative Returns Chart**: Strategy vs Buy & Hold comparison

### Tab 4: Statistics
- **Price Statistics**: Min, Max, Mean, Std Dev, Current
- **Signal Distribution**: Pie chart of Buy/Sell/Neutral signals
- **RSI Distribution**: Histogram showing RSI values

---

## 🎨 Customization Options

### Change Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor="#1f77b4"           # Change to any hex color
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#f0f2f6"
```

### Add More Tickers
Edit `src/utils/config.py`:
```python
DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'YOUR_TICKER']
```

### Change Data Periods
Edit `src/utils/config.py`:
```python
TRAIN_START = "2022-01-01"
TEST_START = "2024-01-01"
```

### Add Custom Indicators
Add functions to `app.py` and call them in tabs:
```python
def add_my_custom_indicator(data):
    df = data.copy()
    # Your logic here
    df['My_Indicator'] = ...
    return df
```

---

## 🔧 Project Structure

```
algo-trading-project/
├── app.py                          # ✨ Streamlit dashboard
├── requirements-streamlit.txt       # ✨ Dashboard dependencies
├── setup_streamlit.py              # ✨ Setup script
├── start_streamlit.bat             # ✨ Windows launcher
├── STREAMLIT_README.md             # ✨ Full documentation
├── .streamlit/
│   └── config.toml                 # ✨ Streamlit config
├── notebooks/
│   ├── 06_combined_strategy.ipynb
│   └── combined_strategy.py
├── src/
│   ├── data_collection/
│   ├── preprocessing/
│   ├── modeling/
│   ├── strategy/
│   └── utils/
└── data/
    ├── raw/
    ├── processed/
    ├── indicators/
    └── signals/
```

---

## 📈 Strategy Overview

The dashboard visualizes your **Combined Scalping Strategy** with three indicators:

### 1. **RSI (Relative Strength Index)**
- Buy: 30 < RSI < 50 (momentum with room for growth)
- Sell: 50 < RSI < 70 (momentum without risk)

### 2. **Trend (SMA)**
- Buy: Price > SMA20 > SMA50 (uptrend confirmed)
- Sell: Price < SMA20 < SMA50 (downtrend confirmed)

### 3. **Momentum (MACD)**
- Buy: MACD > 0 AND histogram positive
- Sell: MACD < 0 AND histogram negative

**Final Signal:**
- 🟢 **BUY**: All three indicators aligned for buying
- 🔴 **SELL**: All three indicators aligned for selling
- ⚪ **NEUTRAL**: No strong consensus

---

## 🚀 Advanced Usage

### Real-time Updates
The dashboard will automatically refresh when you edit code (with `runOnSave = true`).

### Data Caching
Streamlit caches data for performance:
- First load: Download and process data
- Subsequent loads: Use cache (faster)
- Clear cache manually if needed

### Multiple Tickers
Switch between different stocks using the sidebar dropdown.

### Analysis Modes
(Feature for future expansion - sidebar radio button ready)

---

## 📱 Mobile Access

Access from other devices:
```bash
streamlit run app.py --server.address 0.0.0.0
```

Then connect from other computers using:
```
http://YOUR_COMPUTER_IP:8501
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Module Not Found Error
```bash
# Reinstall dependencies
pip install -r requirements-streamlit.txt --force-reinstall
```

### Charts Not Displaying
- Clear browser cache (Ctrl+Shift+Delete)
- Restart Streamlit (Ctrl+C and run again)

### Data Not Loading
- Verify CSV files exist in `data/raw/` and `data/processed/`
- Check file permissions
- Ensure Kaggle API is configured

---

## 📚 Documentation

- **Full Guide**: See `STREAMLIT_README.md`
- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python

---

## ✅ Checklist

- [x] Streamlit app created (`app.py`)
- [x] Dependencies file created
- [x] Configuration file created
- [x] Windows launcher created
- [x] Setup script created
- [x] Documentation created
- [x] All 4 tabs implemented
- [x] Interactive charts added
- [x] Real-time indicators displayed
- [x] Backtest metrics calculated
- [x] Statistics displayed

---

## 🎯 Next Steps

1. **Install**: Run `python setup_streamlit.py`
2. **Start**: Run `start_streamlit.bat` (Windows) or `streamlit run app.py`
3. **Access**: Open `http://localhost:8501` in your browser
4. **Explore**: Navigate through all 4 tabs
5. **Customize**: Modify colors, tickers, date ranges as needed
6. **Deploy**: Deploy to cloud (Streamlit Cloud, AWS, Heroku, etc.)

---

## 💡 Tips

- Use the sidebar to switch between tickers
- Hover over charts for detailed information
- Download charts as PNG using Plotly menu
- Zoom and pan on charts for detailed analysis
- Refresh page if charts don't load (Ctrl+R)
- Check console for error messages (F12)

---

**Enjoy your professional AlgoTrading Dashboard! 🚀**

*Created: January 30, 2026*
