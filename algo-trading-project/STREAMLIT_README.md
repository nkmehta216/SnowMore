# AlgoTrading Bot - Streamlit Dashboard

A professional web-based dashboard for your algorithmic trading bot, built with Streamlit. Monitor trading strategies, analyze backtesting results, and visualize technical indicators in real-time.

## Features

### 📊 Overview Tab
- **Live Metrics**: Current price, RSI, trading signals, moving averages
- **Strategy Information**: Details about the combined scalping strategy
- **Data Period**: Training and testing date ranges

### 📈 Charts & Signals Tab
- **Price Chart**: Interactive candlestick-style chart with trading signals
  - Green triangles for BUY signals
  - Red triangles for SELL signals
  - SMA 20 and SMA 50 trend lines
- **RSI Indicator**: Relative Strength Index with overbought/oversold zones
- **MACD Indicator**: Moving Average Convergence Divergence with signal line
- **Recent Signals Table**: Last 20 trading signals with details

### 💰 Backtest Results Tab
- **Performance Metrics**:
  - Total Return
  - Annual Return
  - Sharpe Ratio
  - Maximum Drawdown
  - Win Rate
- **Cumulative Returns Chart**: Strategy vs Buy & Hold comparison
- **Performance Over Time**: Visual comparison of strategy effectiveness

### 📉 Statistics Tab
- **Price Statistics**: Min, Max, Mean, Std Dev, Current Price
- **Signal Distribution**: Pie chart showing Buy/Sell/Neutral signal counts
- **RSI Distribution**: Histogram of RSI values across all data points

## Installation

### 1. Install Dependencies

```bash
# Install Streamlit and related packages
pip install -r requirements-streamlit.txt
```

Or manually:

```bash
pip install streamlit pandas numpy plotly scikit-learn xgboost joblib yfinance
```

### 2. Verify Project Structure

Ensure your project structure is correct:

```
algo-trading-project/
├── app.py                      # Main Streamlit application
├── requirements-streamlit.txt  # Streamlit dependencies
├── start_streamlit.bat         # Windows startup script
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── src/
│   ├── data_collection/
│   ├── preprocessing/
│   ├── modeling/
│   ├── strategy/
│   └── utils/
└── notebooks/
    └── combined_strategy.py    # Your converted notebook
```

## Running the App

### Windows (Recommended)
Simply double-click the batch file:
```
start_streamlit.bat
```

Or run from terminal:
```bash
streamlit run app.py
```

### Mac/Linux
```bash
streamlit run app.py
```

### Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8501
```

## Configuration

### Streamlit Settings
Edit `.streamlit/config.toml` to customize:
- Theme colors (primaryColor, backgroundColor, etc.)
- Port (default: 8501)
- Server settings
- Logger level

### App Settings
Use the sidebar to:
- **Select Ticker**: Choose which stock to analyze from DEFAULT_TICKERS
- **Analysis Mode**: Switch between Live Data, Backtest Analysis, or Strategy Signals

## Dashboard Sections

### Sidebar Controls
- **Ticker Selection**: Drop-down to select stock symbols
- **Analysis Mode**: Radio buttons for different view modes

### Metric Cards
Each tab displays key metrics in card format:
- Color-coded indicators
- Real-time updates
- Trend indicators

### Interactive Charts
All charts are powered by Plotly:
- Hover for details
- Zoom and pan capabilities
- Download chart as PNG
- Toggle data series on/off

## Strategy Details

### Combined Scalping Strategy
The dashboard displays signals from your combined strategy using:

1. **RSI (Relative Strength Index)**
   - Buy: RSI between 30-50 (momentum without overbought)
   - Sell: RSI between 50-70 (momentum without oversold)

2. **Trend Confirmation (SMAs)**
   - Buy: Price > SMA 20 > SMA 50 (uptrend)
   - Sell: Price < SMA 20 < SMA 50 (downtrend)

3. **MACD Validation**
   - Buy: MACD > 0 and histogram positive
   - Sell: MACD < 0 and histogram negative

### Signal Types
- 🟢 **BUY**: All three indicators align for buying
- 🔴 **SELL**: All three indicators align for selling
- ⚪ **NEUTRAL**: No strong consensus

## Performance Metrics Explained

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Total Return** | (Final - Initial) / Initial | Overall profit/loss percentage |
| **Annual Return** | Average daily return × 252 | Expected return per year |
| **Sharpe Ratio** | (Return - Risk-Free) / Std Dev | Risk-adjusted return |
| **Max Drawdown** | Largest peak-to-trough decline | Worst-case loss |
| **Win Rate** | Winning trades / Total trades | Percentage of profitable trades |

## Data Sources

- **Historical Data**: Kaggle datasets and Yahoo Finance
- **Real-time Data**: Yahoo Finance API
- **Training Period**: Configured in src/utils/config.py
- **Testing Period**: Configured in src/utils/config.py

## Customization

### Add Custom Indicators
Edit `app.py` and add new functions:

```python
def add_my_indicator(data):
    df = data.copy()
    # Your indicator logic here
    df['My_Indicator'] = ...
    return df
```

### Change Theme
Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#FF5733"
backgroundColor="#1a1a2e"
```

### Add New Tickers
Update `src/utils/config.py`:

```python
DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'YOUR_TICKER']
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Data Loading Errors
- Ensure all CSV files exist in `data/` folders
- Check that Kaggle API is configured (for live data)
- Verify file paths in config.py

### Import Errors
```bash
# Reinstall all dependencies
pip install -r requirements-streamlit.txt --force-reinstall
```

### Performance Issues
- Clear cache: Delete `.streamlit/cache` folder
- Use fewer data points or a smaller time range
- Adjust sidebar refresh settings

## Advanced Features

### Caching
Data is automatically cached to improve performance:
- Cache lifetime: Default (until notebook restart)
- Clear manually in sidebar menu

### Real-time Updates
Set `runOnSave = true` in config.toml for live updates while editing

### Session State
Streamlit manages state automatically:
- Sidebar selections persist during session
- Charts update based on selections

## API Integration

The dashboard can be extended with API endpoints from your `src/api/main.py`:

```python
import requests

@st.cache_data
def get_model_predictions(ticker):
    response = requests.get(f"http://localhost:8000/predict/{ticker}")
    return response.json()
```

## Performance Tips

1. **Use data caching**: `@st.cache_data` decorator speeds up repeated loads
2. **Filter date ranges**: Reduce data points for faster processing
3. **Run locally**: Use localhost for best performance
4. **Monitor resources**: Check system RAM and CPU usage

## Security Considerations

For production deployment:
- Use environment variables for sensitive data
- Implement authentication/authorization
- Validate all user inputs
- Use HTTPS for remote access
- Restrict data access by user role

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements-streamlit.txt .
RUN pip install -r requirements-streamlit.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Cloud Platforms
- **Streamlit Cloud**: Direct GitHub integration
- **AWS**: EC2 + ECS
- **Heroku**: Container deployment
- **Azure**: App Service

## Support & Documentation

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python
- **Project Docs**: See README.md in project root

## Version History

- **v1.0.0** (Jan 2026): Initial release
  - Dashboard with 4 main tabs
  - Support for multiple tickers
  - Interactive charts and metrics
  - Backtest analysis

## License

See LICENSE file in project root

## Author

AlgoTrading Bot Project Team

---

**Last Updated**: January 30, 2026  
**Streamlit Version**: 1.28.1+
