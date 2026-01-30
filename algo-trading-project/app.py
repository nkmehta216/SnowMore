#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Streamlit Web Application for Algo Trading Bot - Combined Strategy
Dashboard for monitoring ensemble ML + scalping strategy backtesting and live trading
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import warnings
from datetime import datetime, timedelta
import yfinance as yf
import pytz

warnings.filterwarnings('ignore')

# --------------------------------------------------
# Setup
# --------------------------------------------------
st.set_page_config(
    page_title="Combined Strategy Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
INITIAL_CAPITAL = 1_000_000
TREND_STRENGTH_MIN = 0.5

# Add project to path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import project modules
try:
    from src.data_collection.load_kaggle_data import load_kaggle_data
    from src.preprocessing.clean_data import clean_ohlcv_data
    from src.utils.data_split import split_data_by_date
    from src.utils.config import DEFAULT_TICKERS, TRAIN_START, TRAIN_END, TEST_START, TEST_END
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, classification_report
    import joblib
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

# --------------------------------------------------
# Styling & Custom CSS
# --------------------------------------------------
st.markdown("""
<style>
    /* Main styling */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-weight: 500;
    }
    
    /* Headers */
    .header {
        color: #667eea;
        font-weight: bold;
        margin-bottom: 20px;
        font-size: 24px;
    }
    
    /* Success indicators */
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Warning indicators */
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-weight: 600;
        color: #667eea;
    }
    
    /* Divider */
    hr {
        margin: 20px 0;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

# --------------------------------------------------
# Helper Functions - Combined Strategy
# --------------------------------------------------

@st.cache_data
def load_data(ticker):
    """Load and cache data for a ticker"""
    try:
        data = load_kaggle_data(ticker)
        return clean_ohlcv_data(data)
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        return None

def fetch_today_realtime_data(ticker, days=1):
    """Fetch today's real-time intraday data from yfinance"""
    try:
        IST = pytz.timezone("Asia/Kolkata")
        
        # Map ticker names to yfinance symbols
        ticker_map = {
            "NIFTY BANK": "^NSEBANK",
            "NIFTY": "^NSEI",
            "NIFTY COMMODITIES": "NIFTYCOMMDX.NS",
            "NIFTY CONSUMPTION": "NIFTYCONSUMER.NS",
            "NIFTY FIN SERVICE": "NIFTYFINANCE.NS",
            "NIFTY INDIA MFG": "NIFTYMFG.NS",
            "INDIA VIX": "^INDIAVIX"
        }
        
        yf_ticker = ticker_map.get(ticker, ticker)
        
        # Fetch last N days of 1-minute data
        end_date = datetime.now(IST)
        start_date = end_date - timedelta(days=days)
        
        live_data = yf.download(
            yf_ticker,
            start=start_date,
            end=end_date,
            interval="1m",
            progress=False
        )
        
        if live_data.empty:
            return None
        
        # Convert timezone to IST if needed
        if live_data.index.tz is None:
            live_data.index = live_data.index.tz_localize("UTC").tz_convert(IST)
        else:
            live_data.index = live_data.index.tz_convert(IST)
        
        # Handle MultiIndex columns from yfinance
        if isinstance(live_data.columns, pd.MultiIndex):
            live_data.columns = [col[0] for col in live_data.columns]
        
        # Standardize column names
        live_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        live_data = live_data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        
        return live_data
        
    except Exception as e:
        st.warning(f"Could not fetch real-time data for {ticker}: {e}")
        return None

def add_scalping_signals(data):
    """Add rule-based scalping signals using RSI, SMA, and MACD"""
    df = data.copy()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-8)
    rsi = 100 - (100 / (1 + rs))

    # Trend
    sma_20 = df["Close"].rolling(20).mean()
    sma_50 = df["Close"].rolling(50).mean()

    # MACD
    ema_12 = df["Close"].ewm(span=12).mean()
    ema_26 = df["Close"].ewm(span=26).mean()
    macd = ema_12 - ema_26
    macd_signal = macd.ewm(span=9).mean()
    macd_hist = macd - macd_signal

    # Near-high strength
    close_20_high = df["Close"].rolling(20).max()
    buy_strength = df["Close"] > 0.95 * close_20_high

    # Buy signals
    buy_uptrend = (df["Close"] > sma_20) & (sma_20 > sma_50)
    buy_rsi = (rsi > 30) & (rsi < 50)
    buy_macd = (macd > 0) & (macd_hist > 0)
    buy_signal = (buy_uptrend & buy_rsi) | (buy_uptrend & buy_macd) | (buy_uptrend & buy_strength)

    # Sell signals
    sell_downtrend = (df["Close"] < sma_20) & (sma_20 < sma_50)
    sell_rsi = (rsi < 70) & (rsi > 50)
    sell_macd = (macd < 0) & (macd_hist < 0)
    sell_signal = (sell_downtrend & sell_rsi) | (sell_downtrend & sell_macd)

    signal = pd.Series(0, index=df.index)
    signal[buy_signal & ~sell_signal] = 1
    signal[sell_signal & ~buy_signal] = -1
    signal[~buy_signal & ~sell_signal] = 0

    df["strategy_signal"] = signal
    df["RSI"] = rsi
    df["SMA_20"] = sma_20
    df["SMA_50"] = sma_50
    df["MACD"] = macd
    df["MACD_Signal"] = macd_signal

    return df

def add_basic_features(data, horizon=3, cost=0.0003):
    """Add basic ML features"""
    df = data.copy()

    df["returns"] = df["Close"].pct_change()
    df["log_returns"] = np.log(df["Close"] / df["Close"].shift(1))

    sma_10 = df["Close"].rolling(10).mean()
    sma_20 = df["Close"].rolling(20).mean()

    df["trend_10"] = (df["Close"] - sma_10) / (sma_10 + 1e-8)
    df["trend_20"] = (df["Close"] - sma_20) / (sma_20 + 1e-8)
    df["trend_diff"] = (sma_10 - sma_20) / (sma_20 + 1e-8)

    df["range_pct"] = (df["High"] - df["Low"]) / (df["Close"] + 1e-8)
    df["body_pct"] = (df["Close"] - df["Open"]) / (df["Close"] + 1e-8)
    df["body_abs"] = df["body_pct"].abs()

    df["volatility_10"] = df["returns"].rolling(10).std()
    df["vol_ratio"] = df["volatility_10"] / (df["volatility_10"].rolling(50).mean() + 1e-8)
    df["high_vol"] = (df["vol_ratio"] > 1.0).astype(int)

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-8)
    df["RSI"] = (100 - (100 / (1 + rs))) / 100.0

    if "Volume" in df.columns and float(df["Volume"].sum()) > 0:
        vol_sma = df["Volume"].rolling(20).mean()
        df["Volume_norm"] = np.log1p(df["Volume"] / (vol_sma + 1e-8))
    else:
        df["Volume_norm"] = 0.0

    future_return = (df["Close"].shift(-horizon) - df["Close"]) / df["Close"]
    df["target"] = (future_return > cost).astype(int)

    df.dropna(inplace=True)
    return df

def add_advanced_features(df):
    """Add advanced features from your notebook"""
    d = df.copy()
    
    d['momentum_5'] = (d['Close'] - d['Close'].shift(5)) / d['Close'].shift(5)
    d['momentum_10'] = (d['Close'] - d['Close'].shift(10)) / d['Close'].shift(10)
    d['momentum_20'] = (d['Close'] - d['Close'].shift(20)) / d['Close'].shift(20)
    d['momentum_accel'] = d['momentum_5'] - d['momentum_10']
    
    d['tr'] = np.maximum(
        d['High'] - d['Low'],
        np.maximum(
            abs(d['High'] - d['Close'].shift(1)),
            abs(d['Low'] - d['Close'].shift(1))
        )
    )
    d['atr'] = d['tr'].rolling(14).mean()
    d['atr_pct'] = d['atr'] / d['Close']
    
    sma_10 = d['Close'].rolling(10).mean()
    sma_20 = d['Close'].rolling(20).mean()
    sma_50 = d['Close'].rolling(50).mean()
    
    d['trend_strength'] = (
        ((d['Close'] > sma_20).astype(int) * 0.4) +
        ((sma_20 > sma_50).astype(int) * 0.3) +
        ((d['momentum_5'] > 0).astype(int) * 0.3)
    )
    
    d['vol_20'] = d['Close'].pct_change().rolling(20).std()
    d['vol_regime'] = (d['vol_20'] > d['vol_20'].rolling(50).mean()).astype(int)
    
    d['high_20'] = d['High'].rolling(20).max()
    d['low_20'] = d['Low'].rolling(20).min()
    d['price_position'] = (d['Close'] - d['low_20']) / (d['high_20'] - d['low_20'] + 1e-8)
    
    d['momentum_trend_signal'] = d['momentum_5'] * d['trend_strength']
    d['price_momentum_align'] = d['price_position'] * d['momentum_10']
    
    return d

@st.cache_resource
def train_ensemble_model(X_train_scaled, y_train):
    """Train XGBoost + LightGBM ensemble"""
    xgb_model = XGBClassifier(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.025,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=8,
        gamma=0.05,
        reg_alpha=0.05,
        reg_lambda=0.5,
        objective="binary:logistic",
        eval_metric="auc",
        random_state=42,
        verbosity=0
    )
    xgb_model.fit(X_train_scaled, y_train)
    
    lgb_model = LGBMClassifier(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.02,
        subsample=0.75,
        colsample_bytree=0.75,
        num_leaves=31,
        min_child_samples=5,
        reg_alpha=0.1,
        reg_lambda=0.5,
        objective="binary",
        metric="auc",
        random_state=42,
        verbose=-1
    )
    lgb_model.fit(X_train_scaled, y_train)
    
    return xgb_model, lgb_model

def get_ensemble_probability(xgb_model, lgb_model, X_scaled):
    """Get ensemble ML probability"""
    xgb_proba = xgb_model.predict_proba(X_scaled)[:, 1]
    lgb_proba = lgb_model.predict_proba(X_scaled)[:, 1]
    return xgb_proba * 0.55 + lgb_proba * 0.45

# --------------------------------------------------
# Main App
# --------------------------------------------------

# --------------------------------------------------
# Main App Header
# --------------------------------------------------

st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0; font-size: 32px;">🎯 Combined ML + Scalping Strategy</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">XGBoost + LightGBM Ensemble with Advanced Risk Management</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #667eea; text-align: center;'>⚙️ Configuration</h2>", unsafe_allow_html=True)
    st.divider()
    
    selected_ticker = st.selectbox(
        "📊 Select Ticker",
        DEFAULT_TICKERS,
        help="Choose a stock ticker to analyze"
    )
    
    st.info("💡 Tip: Switch tickers to compare different market segments", icon="ℹ️")

# --------------------------------------------------
# Main Tabs with Enhanced Styling
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview", 
    "🤖 ML Predictions", 
    "📊 Live Trading", 
    "📅 Daily Simulation"
])

st.divider()

# --------------------------------------------------
# Data Loading & Model Training
# --------------------------------------------------

@st.cache_resource
def prepare_strategy_data(ticker):
    """Prepare all data and train model"""
    try:
        # Load data
        raw_data = load_data(ticker)
        if raw_data is None:
            return None
        
        cleaned_data = clean_ohlcv_data(raw_data)
        train_data, test_data = split_data_by_date(cleaned_data)
        
        # Add signals and features to training data
        train_with_signals = add_scalping_signals(train_data)
        train_with_basic = add_basic_features(train_with_signals)
        train_with_advanced = add_advanced_features(train_with_basic)
        train_with_advanced = train_with_advanced.dropna()
        
        # Add signals and features to test data
        test_with_signals = add_scalping_signals(test_data)
        test_with_basic = add_basic_features(test_with_signals)
        test_with_advanced = add_advanced_features(test_with_basic)
        test_with_advanced = test_with_advanced.dropna()
        
        # Get feature columns
        feature_cols = [
            c for c in train_with_advanced.columns
            if c not in ["target", "Open", "High", "Low", "Close", "Volume", "strategy_signal", "tr", "high_20", "low_20"]
        ]
        
        # Prepare training data
        X_train = train_with_advanced[feature_cols]
        y_train = train_with_advanced["target"]
        
        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train ensemble
        xgb_model, lgb_model = train_ensemble_model(X_train_scaled, y_train)
        
        # Prepare test data
        X_test = test_with_advanced[feature_cols]
        X_test_scaled = scaler.transform(X_test)
        
        return {
            'train_data': train_with_advanced,
            'test_data': test_with_advanced,
            'X_test': X_test,
            'X_test_scaled': X_test_scaled,
            'xgb_model': xgb_model,
            'lgb_model': lgb_model,
            'scaler': scaler,
            'feature_cols': feature_cols
        }
    except Exception as e:
        st.error(f"Error preparing data: {e}")
        return None

# Load data
with st.spinner(f"Loading data for {selected_ticker}..."):
    strategy_data = prepare_strategy_data(selected_ticker)

if strategy_data is None:
    st.error("Failed to load data")
    st.stop()

# Get ML probabilities
ml_proba = get_ensemble_probability(
    strategy_data['xgb_model'],
    strategy_data['lgb_model'],
    strategy_data['X_test_scaled']
)

test_df = strategy_data['test_data'].copy()
test_df['ml_prob'] = ml_proba
prices = test_df["Close"].values
atr_values = test_df["atr"].values

# --------------------------------------------------
# FETCH TODAY'S REAL-TIME DATA FOR OVERVIEW
# --------------------------------------------------
with st.spinner("Fetching today's real-time market data..."):
    today_realtime_data = fetch_today_realtime_data(selected_ticker, days=1)
    
    if today_realtime_data is not None and len(today_realtime_data) > 50:
        # Process real-time data with features
        today_with_signals = add_scalping_signals(today_realtime_data.copy())
        today_with_basic = add_basic_features(today_with_signals.copy())
        today_with_advanced = add_advanced_features(today_with_basic.copy())
        today_with_advanced = today_with_advanced.dropna()
        
        if len(today_with_advanced) > 0:
            # Get ML probabilities for today's data
            X_today = today_with_advanced[strategy_data['feature_cols']].copy()
            X_today_scaled = strategy_data['scaler'].transform(X_today)
            today_ml_proba = get_ensemble_probability(
                strategy_data['xgb_model'],
                strategy_data['lgb_model'],
                X_today_scaled
            )
            
            # Use today's data for Overview
            today_df = today_with_advanced.copy()
            today_df['ml_prob'] = today_ml_proba
            overview_prices = today_df["Close"].values
            overview_atr_values = today_df["atr"].values
            overview_df = today_df
            is_realtime = True
        else:
            # Fallback to backtest data if today's data is too small
            overview_prices = prices
            overview_atr_values = atr_values
            overview_df = test_df
            is_realtime = False
    else:
        # Fallback to backtest data if can't fetch real-time
        overview_prices = prices
        overview_atr_values = atr_values
        overview_df = test_df
        is_realtime = False

# --------------------------------------------------
# TAB 1: Overview
# --------------------------------------------------

with tab1:
    st.markdown("<h2 style='color: #667eea;'>📈 Market Overview & Strategy Status</h2>", unsafe_allow_html=True)
    
    if is_realtime:
        st.success("✅ Real-time Data Active (Today)")
    else:
        st.warning("⏱️ Using historical backtest data (2024)")
    
    st.header(f"Strategy Overview - {selected_ticker}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    latest_price = overview_prices[-1]
    latest_ml_prob = overview_df['ml_prob'].iloc[-1]
    latest_rsi = overview_df['RSI'].iloc[-1]
    latest_signal = overview_df['strategy_signal'].iloc[-1]
    latest_atr_pct = overview_df['atr_pct'].iloc[-1]
    
    st.subheader("📊 Real-Time Market Data")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        price_change = ((overview_prices[-1] - overview_prices[-20])/overview_prices[-20]*100) if len(overview_prices) > 20 else 0
        st.metric("💰 Price", f"₹{latest_price:,.2f}", f"{price_change:+.2f}%", delta_color="normal")
    
    with col2:
        st.metric("🤖 ML Conf", f"{latest_ml_prob*100:.1f}%", "Strong" if latest_ml_prob > 0.6 else "Weak")
    
    with col3:
        rsi_val = latest_rsi*100
        rsi_status = "Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Neutral"
        st.metric("📈 RSI", f"{rsi_val:.1f}", rsi_status)
    
    with col4:
        signal_text = "🟢 BUY" if latest_signal == 1 else "🔴 SELL" if latest_signal == -1 else "⚪ NEUTRAL"
        st.metric("📍 Signal", signal_text)
    
    with col5:
        st.metric("⚡ ATR %", f"{latest_atr_pct*100:.3f}%", "High Vol" if latest_atr_pct > 0.015 else "Low Vol")
    
    st.divider()
    
    # Strategy info
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Ensemble Model")
        st.info("""
        **XGBoost + LightGBM Hybrid (55% + 45%)**
        - 250 estimators each
        - Advanced feature engineering
        - AUC-optimized
        - 25+ features per candle
        """)
    
    with col_right:
        st.subheader("🎯 Trading Logic")
        st.info(f"""
        **Combined Strategy**
        - ML Probability entry threshold: {np.percentile(overview_df['ml_prob'].values, 75):.2%}
        - Dynamic ATR-based stops
        - Trailing stops with 3-tier profits
        - Multiple position management
        """)

# --------------------------------------------------
# TAB 2: ML Predictions
# --------------------------------------------------

with tab2:
    st.markdown("<h2 style='color: #667eea;'>🤖 ML Model Analysis & Insights</h2>", unsafe_allow_html=True)
    
    # ML Probability distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Probability Distribution")
        fig_prob_dist = px.histogram(
            x=overview_df['ml_prob'].values,
            nbins=50,
            title="Ensemble ML Probability Distribution",
            labels={'x': 'Probability', 'y': 'Frequency'},
            color_discrete_sequence=['#667eea']
        )
        fig_prob_dist.update_layout(showlegend=False, hovermode='x unified')
        st.plotly_chart(fig_prob_dist, use_container_width=True)
    
    with col2:
        st.subheader("📈 Key Statistics")
        ml_probs_array = overview_df['ml_prob'].values
        stats_data = {
            'Metric': ['Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean', 'Std Dev'],
            'Value': [
                f"{ml_probs_array.min():.4f}",
                f"{np.percentile(ml_probs_array, 25):.4f}",
                f"{np.median(ml_probs_array):.4f}",
                f"{np.percentile(ml_probs_array, 75):.4f}",
                f"{ml_probs_array.max():.4f}",
                f"{ml_probs_array.mean():.4f}",
                f"{ml_probs_array.std():.4f}"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Price vs ML Probability
    fig_corr = go.Figure()
    
    fig_corr.add_trace(go.Scatter(
        x=np.arange(len(prices)),
        y=prices / prices[0],
        mode='lines',
        name='Price (Normalized)',
        yaxis='y1',
        line=dict(color='black', width=2)
    ))
    
    fig_corr.add_trace(go.Scatter(
        x=np.arange(len(ml_proba)),
        y=ml_proba,
        mode='lines',
        name='ML Probability',
        yaxis='y2',
        line=dict(color='blue', width=2, dash='dash')
    ))
    
    fig_corr.update_layout(
        title='Price vs ML Probability Over Time',
        xaxis_title='Candle Index',
        yaxis=dict(title='Normalized Price', side='left'),
        yaxis2=dict(title='ML Probability', side='right', overlaying='y'),
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# --------------------------------------------------
# TAB 3: Live Trading
# --------------------------------------------------

with tab3:
    st.markdown("<h2 style='color: #667eea;'>📊 Live Paper Trading Dashboard</h2>", unsafe_allow_html=True)
    st.info("🔴 Real-time simulation with ML ensemble predictions and dynamic risk management", icon="ℹ️")
    
    # Recent signals
    st.subheader("📈 Recent Trading Signals (Last 20 Candles)")
    
    recent_df = pd.DataFrame({
        'Index': range(len(overview_prices[-20:]))[-20:],
        'Price': overview_prices[-20:],
        'ML Prob': overview_df['ml_prob'].iloc[-20:].values,
        'RSI': overview_df['RSI'].iloc[-20:].values * 100,
        'ATR %': overview_df['atr_pct'].iloc[-20:].values * 100,
        'Signal': overview_df['strategy_signal'].iloc[-20:].values
    })
    
    recent_df['Signal'] = recent_df['Signal'].map({1: '🟢 BUY', -1: '🔴 SELL', 0: '⚪ NEUTRAL'})
    recent_df = recent_df.round(4)
    
    st.dataframe(recent_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Current status with improved styling
    st.subheader("⚡ Real-Time Status Indicators")
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        confidence = overview_df['ml_prob'].iloc[-1] * 100
        strength = "💪 Strong" if overview_df['ml_prob'].iloc[-1] > 0.6 else "⚠️ Weak"
        st.metric("ML Confidence", f"{confidence:.1f}%", strength)
    
    with col_status2:
        signals_buy = (overview_df['strategy_signal'] == 1).sum()
        signals_sell = (overview_df['strategy_signal'] == -1).sum()
        st.metric("📊 BUY vs SELL", f"🟢 {signals_buy} | 🔴 {signals_sell}")
    
    with col_status3:
        st.metric("📉 Data Points", f"{len(overview_df):,} candles")

with tab4:
    st.markdown("<h2 style='color: #667eea;'>📅 Daily Live Simulation</h2>", unsafe_allow_html=True)
    
    st.info("🔴 Select a date to simulate live trading for that specific day using real yfinance data", icon="⏰")
    
    # Define trading cost
    COST_PER_TRADE = 0.000001
    
    IST = pytz.timezone("Asia/Kolkata")
    
    # Date selector
    col_date1, col_date2 = st.columns([2, 3])
    
    with col_date1:
        days_back = st.slider("Days back from today:", 0, 30, 0, key="daily_sim_days")
    
    with col_date2:
        selected_sim_date = datetime.now(IST).date() - timedelta(days=days_back)
        st.metric("Simulation Date", selected_sim_date.strftime("%A, %B %d, %Y"))
    
    # Fetch and simulate for selected date
    if st.button("📊 Run Daily Simulation", key="run_daily_sim"):
        
        with st.spinner("Fetching yfinance data..."):
            try:
                # Fetch data for the selected date
                start_time = IST.localize(datetime.combine(selected_sim_date, datetime.min.time()))
                end_time = IST.localize(datetime.combine(selected_sim_date, datetime.max.time()))
                
                try:
                    sim_data = yf.download(
                        "^NSEBANK",
                        start=start_time,
                        end=end_time,
                        interval="1m",
                        progress=False
                    )
                    ticker_used = "^NSEBANK"
                except:
                    sim_data = yf.download(
                        "NIFTYBANK.NS",
                        start=start_time,
                        end=end_time,
                        interval="1m",
                        progress=False
                    )
                    ticker_used = "NIFTYBANK.NS"
                
                # Convert timezone
                if sim_data.index.tz is None:
                    sim_data.index = sim_data.index.tz_localize("UTC").tz_convert(IST)
                else:
                    sim_data.index = sim_data.index.tz_convert(IST)
                
                # Fix columns
                if isinstance(sim_data.columns, pd.MultiIndex):
                    sim_data.columns = [col[0] for col in sim_data.columns]
                
                sim_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                sim_data = sim_data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                
                if len(sim_data) == 0:
                    st.warning("⚠️ No data available for this date. It might be a holiday or weekend.")
                    st.stop()
                
                st.success(f"✅ Fetched {len(sim_data)} candles from yfinance")
                
            except Exception as e:
                st.error(f"❌ Error fetching data: {e}")
                st.stop()
        
        # Apply feature engineering
        with st.spinner("Processing features..."):
            try:
                sim_with_signals = add_scalping_signals(sim_data.copy())
                sim_with_features = add_basic_features(sim_with_signals.copy())
                sim_features = add_advanced_features(sim_with_features.copy())
                sim_features = sim_features.dropna()
                
                X_sim = sim_features[strategy_data['feature_cols']].copy()
                X_sim_scaled = strategy_data['scaler'].transform(X_sim)
                ml_prob_sim = get_ensemble_probability(
                    strategy_data['xgb_model'],
                    strategy_data['lgb_model'],
                    X_sim_scaled
                )
                
                sim_prices = sim_features["Close"].values
                sim_atr = sim_features["atr"].values
                
                st.success(f"✅ Features applied: {len(strategy_data['feature_cols'])} features, {len(sim_features)} candles")
                
            except Exception as e:
                st.error(f"❌ Error in feature engineering: {e}")
                st.stop()
        
        # Run daily backtest simulation
        with st.spinner("Running daily trading simulation..."):
            
            SIM_ENTRY_THRESHOLD = np.percentile(ml_prob_sim, 55)
            SIM_STOP_LOSS = 0.010
            SIM_TAKE_PROFIT = 0.025
            SIM_TRAIL_STOP = 0.002
            SIM_HORIZON = 15
            SIM_MIN_POS = 0.05
            SIM_MAX_POS = 0.15
            
            sim_capital = INITIAL_CAPITAL
            sim_peak_capital = sim_capital
            sim_positions = []
            sim_trades = []
            sim_equity = [sim_capital]
            sim_logs = []
            
            # Header
            sim_logs.append("=" * 80)
            sim_logs.append(f" LIVE MARKET SIMULATION - {selected_sim_date.strftime('%Y-%m-%d').upper()}")
            sim_logs.append("=" * 80)
            sim_logs.append(f"\n Fetched {len(sim_data)} candles")
            sim_logs.append(f"   Time Range: {sim_data.index[0]} to {sim_data.index[-1]}")
            sim_logs.append(f"   Price Range: ₹{sim_data['Low'].min():.2f} - ₹{sim_data['High'].max():.2f}")
            sim_logs.append(f"\n Applying feature engineering to data...")
            sim_logs.append(f" Features applied successfully")
            sim_logs.append(f"   ML Probability range: {ml_prob_sim.min():.4f} to {ml_prob_sim.max():.4f}")
            sim_logs.append(f"   Mean confidence: {ml_prob_sim.mean():.4f}")
            sim_logs.append(f"   Data points: {len(sim_features)} candles")
            sim_logs.append("")
            
            # Daily simulation loop
            for i in range(len(sim_prices)):
                current_price = sim_prices[i]
                current_time = sim_features.index[i]
                current_ml_prob = ml_prob_sim[i]
                current_atr = sim_atr[i]
                
                if i < 20:
                    sim_equity.append(sim_capital)
                    continue
                
                # Close positions
                positions_to_close = []
                
                for pos_idx, pos in enumerate(sim_positions):
                    price_move = (current_price - pos['entry_price']) / pos['entry_price']
                    vol_adj_stop = SIM_STOP_LOSS * (1 + (current_atr / current_price) * 0.3)
                    vol_adj_stop = np.clip(vol_adj_stop, SIM_STOP_LOSS * 0.8, SIM_STOP_LOSS * 1.2)
                    
                    exit_hit = False
                    exit_reason = None
                    exit_price = current_price
                    
                    if price_move >= SIM_TAKE_PROFIT:
                        exit_hit = True
                        exit_reason = "PROFIT"
                        exit_price = pos['entry_price'] * (1 + SIM_TAKE_PROFIT)
                    elif price_move > SIM_TAKE_PROFIT * 0.5 and current_price < pos['max_price'] * (1 - SIM_TRAIL_STOP):
                        exit_hit = True
                        exit_reason = "TRAIL"
                        exit_price = pos['max_price'] * (1 - SIM_TRAIL_STOP)
                    elif price_move <= -vol_adj_stop:
                        exit_hit = True
                        exit_reason = "STOP"
                        exit_price = current_price
                    elif i - pos['entry_idx'] >= SIM_HORIZON:
                        exit_hit = True
                        exit_reason = "TIME"
                        exit_price = current_price
                    
                    if exit_hit:
                        ret = (exit_price - pos['entry_price']) / pos['entry_price']
                        net_ret = ret - (COST_PER_TRADE * 2)
                        pnl = pos['position_value'] * net_ret
                        sim_capital += pnl
                        sim_peak_capital = max(sim_peak_capital, sim_capital)
                        
                        emoji = "🎯" if pnl > 0 else "🛑"
                        pnl_str = f"+₹{pnl:,.0f}" if pnl > 0 else f"-₹{abs(pnl):,.0f}"
                        ret_str = f"+{net_ret*100:.2f}%" if net_ret > 0 else f"{net_ret*100:.2f}%"
                        
                        sim_logs.append(f"{emoji} EXIT | {current_time.strftime('%H:%M:%S')} | ₹{exit_price:,.2f} | P&L: {pnl_str} ({ret_str}) | [{exit_reason}] | Capital: ₹{sim_capital:,.0f}")
                        
                        sim_trades.append({
                            'entry': pos['entry_price'],
                            'exit': exit_price,
                            'prob': pos['ml_prob'],
                            'return': net_ret,
                            'pnl': pnl,
                            'reason': exit_reason
                        })
                        
                        positions_to_close.append(pos_idx)
                
                sim_positions = [pos for idx, pos in enumerate(sim_positions) if idx not in positions_to_close]
                
                # Entry logic
                if current_ml_prob >= SIM_ENTRY_THRESHOLD and i < len(sim_prices) - SIM_HORIZON:
                    momentum_5 = sim_features["momentum_5"].iloc[i] if 'momentum_5' in sim_features.columns else 0
                    
                    total_exposure = sum(p['position_fraction'] for p in sim_positions)
                    max_allowed = 1.5
                    
                    if total_exposure < max_allowed:
                        conf_edge = current_ml_prob - SIM_ENTRY_THRESHOLD
                        max_edge = 1.0 - SIM_ENTRY_THRESHOLD if SIM_ENTRY_THRESHOLD < 1.0 else 0.5
                        normalized = conf_edge / max_edge if max_edge > 0 else 0.4
                        
                        pos_frac = SIM_MIN_POS + (SIM_MAX_POS - SIM_MIN_POS) * (normalized ** 1.3)
                        pos_frac = np.clip(pos_frac, SIM_MIN_POS, SIM_MAX_POS)
                        pos_frac *= (1.0 - total_exposure / max_allowed * 0.3)
                        pos_frac = max(pos_frac, SIM_MIN_POS * 0.5)
                        
                        pos_value = sim_capital * pos_frac
                        
                        sim_positions.append({
                            'entry_idx': i,
                            'entry_price': current_price,
                            'position_value': pos_value,
                            'position_fraction': pos_frac,
                            'ml_prob': current_ml_prob,
                            'max_price': current_price
                        })
                        
                        prob_pct = current_ml_prob * 100
                        size_pct = pos_frac * 100
                        sim_logs.append(f"🟢 ENTRY #{len(sim_positions)} | {current_time.strftime('%H:%M:%S')} | ₹{current_price:,.2f} | Conf: {prob_pct:.1f}% | Size: {size_pct:.0f}% | Capital: ₹{sim_capital:,.0f}")
                
                for pos in sim_positions:
                    pos['max_price'] = max(pos['max_price'], current_price)
                
                sim_equity.append(sim_capital)
            
            # Close remaining positions
            for pos in sim_positions:
                exit_price = sim_prices[-1]
                ret = (exit_price - pos['entry_price']) / pos['entry_price']
                net_ret = ret - (COST_PER_TRADE * 2)
                pnl = pos['position_value'] * net_ret
                sim_capital += pnl
                sim_peak_capital = max(sim_peak_capital, sim_capital)
                
                sim_trades.append({
                    'entry': pos['entry_price'],
                    'exit': exit_price,
                    'prob': pos['ml_prob'],
                    'return': net_ret,
                    'pnl': pnl,
                    'reason': 'CLOSE'
                })
            
            # Display logs
            sim_logs.append("")
            sim_logs.append("=" * 80)
            sim_logs.append("")
            
            logs_text = "\n".join(sim_logs)
            st.markdown(f"```\n{logs_text}\n```")
            
            # Summary statistics
            sim_return = (sim_capital / INITIAL_CAPITAL) - 1
            sim_winning = sum(1 for t in sim_trades if t['pnl'] > 0)
            sim_losing = len(sim_trades) - sim_winning
            
            sim_logs_summary = []
            sim_logs_summary.append(" CAPITAL SUMMARY:")
            sim_logs_summary.append(f"   Starting Capital:   ₹{INITIAL_CAPITAL:,.0f}")
            sim_logs_summary.append(f"   Ending Capital:     ₹{sim_capital:,.0f}")
            sim_logs_summary.append(f"   Peak Capital:       ₹{sim_peak_capital:,.0f}")
            sim_logs_summary.append(f"   Net P&L:            ₹{sim_capital - INITIAL_CAPITAL:+,.0f}")
            sim_logs_summary.append("")
            sim_logs_summary.append(" PERFORMANCE METRICS:")
            sim_logs_summary.append(f"   Daily Return:       {sim_return*100:+.3f}%")
            
            sim_equity_arr = np.array(sim_equity)
            max_dd = ((sim_equity_arr / np.maximum.accumulate(sim_equity_arr)) - 1).min()
            sim_logs_summary.append(f"   Max Drawdown:       {max_dd*100:.2f}%")
            
            sim_logs_summary.append(f"   Trades:             {len(sim_trades)}")
            if len(sim_trades) > 0:
                sim_logs_summary.append(f"   Winning:            {sim_winning} ({sim_winning/len(sim_trades)*100:.1f}%)")
                sim_logs_summary.append(f"   Losing:             {sim_losing} ({sim_losing/len(sim_trades)*100:.1f}%)")
            
            sim_logs_summary.append("")
            sim_logs_summary.append(" EXIT DISTRIBUTION:")
            exit_reasons = {}
            for t in sim_trades:
                reason = t['reason']
                exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
            
            for reason in sorted(exit_reasons.keys()):
                count = exit_reasons[reason]
                pct = count / len(sim_trades) * 100 if sim_trades else 0
                sim_logs_summary.append(f"   {reason:15} : {count:3} trades ({pct:5.1f}%)")
            
            sim_logs_summary.append("=" * 80)
            
            if sim_return > 0.05:
                verdict = f" EXCELLENT DAY! +{sim_return*100:.3f}%"
            elif sim_return > 0:
                verdict = f" PROFITABLE DAY! +{sim_return*100:.3f}%"
            elif sim_return == 0:
                verdict = " BREAKEVEN TODAY"
            else:
                verdict = f"  LOSS TODAY: {sim_return*100:.3f}%"
            
            sim_logs_summary.append(verdict)
            sim_logs_summary.append("=" * 80)
            
            summary_text = "\n".join(sim_logs_summary)
            st.markdown(f"```\n{summary_text}\n```")

st.divider()
st.markdown("""
<center>
    <p style='color: #888; font-size: 12px;'>
        Combined ML + Scalping Strategy | Ensemble Model | © 2026
    </p>
</center>
""", unsafe_allow_html=True)
