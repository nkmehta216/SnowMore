# 🚀 Algo Trading ML Project

A complete machine learning-based algorithmic trading system that combines ML predictions with technical scalping strategies.

## 📋 Features

- **Data Collection**: Download and update historical stock data using yfinance
- **Technical Indicators**: Calculate RSI, MACD, Bollinger Bands, moving averages, and more
- **Machine Learning**: Train Random Forest models for price prediction
- **Scalping Strategy**: Short-term trading signals based on technical analysis
- **Combined Strategy**: Weighted combination of ML predictions and scalping signals
- **Backtesting**: Test strategies on historical data with performance metrics
- **REST API**: FastAPI server for real-time predictions
- **Web Dashboard**: Interactive frontend for viewing signals and model status
- **Jupyter Notebooks**: Exploratory analysis and visualization

## 🏗️ Project Structure

```
algo-trading-project/
├── venv/                   # Virtual environment
├── data/                   # Data storage
│   ├── raw/               # Raw downloaded data
│   ├── processed/         # Cleaned data
│   ├── indicators/        # Data with technical indicators
│   └── signals/           # Trading signals
├── notebooks/             # Jupyter notebooks
│   ├── 01_eda.ipynb
│   ├── 02_indicators.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_scalping_rules.ipynb
│   └── 05_backtesting.ipynb
├── src/                   # Source code
│   ├── data_collection/   # Data download modules
│   ├── preprocessing/     # Data cleaning and feature engineering
│   ├── modeling/          # ML model training and evaluation
│   ├── strategy/          # Trading strategies
│   ├── api/              # FastAPI application
│   └── utils/            # Utilities (logger, config, helpers)
├── models/                # Trained models
├── webapp/                # Web interface
│   ├── frontend/         # HTML, CSS, JS
│   └── backend/          # Server
├── tests/                 # Unit tests
├── scripts/               # Batch scripts for Windows
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Virtual Environment

The virtual environment is already created and activated. To manually activate:

**Windows:**
```bash
.\venv\Scripts\activate
```

### 2. Install Dependencies

Dependencies are already installed. To reinstall:
```bash
pip install -r requirements.txt
```

### 3. Download Data

```python
from src.data_collection.download_data import download_stock_data, save_data

ticker = "AAPL"
data = download_stock_data(ticker, "2020-01-01", "2024-12-12")
save_data(data, ticker)
```

### 4. Process Data

```python
from src.preprocessing.clean_data import clean_ohlcv_data
from src.preprocessing.feature_engineering import add_technical_indicators, add_price_features

# Load and clean
import pandas as pd
data = pd.read_csv("data/raw/AAPL.csv", index_col=0, parse_dates=True)
data = clean_ohlcv_data(data)

# Add indicators
data = add_technical_indicators(data)
data = add_price_features(data)

data.to_csv("data/indicators/AAPL_features.csv")
```

### 5. Train Model

```python
from src.modeling.train_model import prepare_features, train_random_forest, save_model

data = pd.read_csv("data/indicators/AAPL_features.csv", index_col=0, parse_dates=True)
X_train, X_test, y_train, y_test, scaler, features = prepare_features(data)

model = train_random_forest(X_train, y_train)
save_model(model, scaler, features, "AAPL")
```

### 6. Generate Signals

```python
from src.strategy.combined_strategy import generate_combined_strategy

data = pd.read_csv("data/indicators/AAPL_features.csv", index_col=0, parse_dates=True)
data = generate_combined_strategy("AAPL", data, ml_weight=0.6)
data.to_csv("data/signals/AAPL_combined_signals.csv")
```

### 7. Backtest Strategy

```python
from src.strategy.backtest import SimpleBacktester

data = pd.read_csv("data/signals/AAPL_combined_signals.csv", index_col=0, parse_dates=True)

backtester = SimpleBacktester(initial_capital=100000, commission=0.001)
results = backtester.backtest(data)
backtester.plot_equity_curve()
```

## 🖥️ Using Batch Scripts (Windows)

### Start API Server
```bash
scripts\start_api.bat
```

### Run Model Training
```bash
scripts\run_training.bat
```

### Run Backtest
```bash
scripts\run_backtest.bat
```

## 🌐 API Usage

### Start the API Server

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Or use the batch script:
```bash
scripts\start_api.bat
```

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /tickers` - Get default tickers
- `GET /models` - List available models
- `POST /predict` - Get trading prediction
- `GET /indicators/{ticker}` - Get latest indicators

### Example Prediction Request

```python
import requests

response = requests.post("http://localhost:8000/predict", json={
    "ticker": "AAPL",
    "features": {
        "Close": 150.0,
        "Volume": 1000000,
        "RSI": 45.0,
        "SMA_20": 148.5
    }
})

print(response.json())
```

## 🎨 Web Dashboard

### Start the Frontend Server

```bash
cd webapp/backend
python server.py
```

Then open your browser to `http://localhost:8080`

The dashboard displays:
- API status
- Available models
- Real-time trading signals
- Prediction confidence

## 📊 Jupyter Notebooks

Launch Jupyter:
```bash
jupyter notebook
```

Then explore the notebooks:
1. **01_eda.ipynb** - Exploratory Data Analysis
2. **02_indicators.ipynb** - Technical Indicators
3. **03_model_training.ipynb** - Model Training
4. **04_scalping_rules.ipynb** - Scalping Strategy
5. **05_backtesting.ipynb** - Backtesting

## 🧪 Testing

Run all tests:
```bash
python -m pytest tests/
```

Run specific test:
```bash
python tests/test_data_pipeline.py
python tests/test_model.py
python tests/test_api.py
```

## ⚙️ Configuration

Edit `src/utils/config.py` to customize:

- Trading parameters (capital, commission, risk)
- Model hyperparameters
- Technical indicator periods
- Scalping thresholds
- API settings

### Environment Variables

Create a `.env` file in the project root:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

## 📈 Performance Metrics

The backtester provides:
- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Total Trades
- Equity Curve

## 🛠️ Technologies Used

- **Data**: pandas, numpy, yfinance
- **ML**: scikit-learn, joblib
- **Indicators**: pandas-ta, ta
- **Visualization**: matplotlib, seaborn, plotly
- **API**: FastAPI, uvicorn
- **Testing**: pytest, unittest
- **Backtesting**: Custom backtester
- **Notebooks**: Jupyter

## 📝 Workflow

1. **Data Collection** → Download stock data
2. **Preprocessing** → Clean and calculate indicators
3. **Model Training** → Train ML models
4. **Signal Generation** → Combine ML + scalping signals
5. **Backtesting** → Test on historical data
6. **Deployment** → Serve via API

## 🔮 Future Enhancements

- [ ] Real-time data streaming
- [ ] More ML models (LSTM, XGBoost)
- [ ] Portfolio optimization
- [ ] Risk management system
- [ ] Live trading integration with Alpaca
- [ ] Discord/Telegram notifications
- [ ] Database integration (PostgreSQL)
- [ ] Docker containerization

## 📄 License

This project is for educational purposes only. Not financial advice.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Do not use it for live trading without thorough testing and understanding of the risks involved. Past performance does not guarantee future results.

## 🤝 Contributing

Contributions welcome! Please test thoroughly before submitting PRs.

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Happy Trading! 📈🚀**

