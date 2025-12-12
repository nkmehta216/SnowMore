"""
Utility functions for model loading and prediction.
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def load_model(ticker: str, model_dir: str = "models"):
    """
    Load trained model, scaler, and feature list.
    
    Args:
        ticker: Stock ticker
        model_dir: Directory containing saved models
    
    Returns:
        model, scaler, feature_columns
    """
    model_path = Path(model_dir) / f"{ticker}_model.pkl"
    scaler_path = Path(model_dir) / f"{ticker}_scaler.pkl"
    features_path = Path(model_dir) / f"{ticker}_features.pkl"
    
    if not all([model_path.exists(), scaler_path.exists(), features_path.exists()]):
        raise FileNotFoundError(f"Model files not found for {ticker}")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    features = joblib.load(features_path)
    
    logger.info(f"Loaded model for {ticker}")
    return model, scaler, features


def predict(model, scaler, features, data: pd.DataFrame):
    """
    Make predictions using trained model.
    
    Args:
        model: Trained model
        scaler: Fitted scaler
        features: List of feature names
        data: DataFrame with features
    
    Returns:
        predictions, probabilities
    """
    # Ensure all required features are present
    missing_features = set(features) - set(data.columns)
    if missing_features:
        logger.warning(f"Missing features: {missing_features}")
        for feat in missing_features:
            data[feat] = 0
    
    # Select and order features
    X = data[features]
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Predict
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled) if hasattr(model, 'predict_proba') else None
    
    return predictions, probabilities


def get_trading_signal(probabilities, buy_threshold: float = 0.6, sell_threshold: float = 0.4):
    """
    Convert model probabilities to trading signals.
    
    Args:
        probabilities: Model probability predictions
        buy_threshold: Threshold for buy signal
        sell_threshold: Threshold for sell signal
    
    Returns:
        Trading signal: 1 (buy), -1 (sell), 0 (hold)
    """
    if probabilities is None:
        return 0
    
    prob_up = probabilities[:, 1] if len(probabilities.shape) > 1 else probabilities
    
    if prob_up > buy_threshold:
        return 1  # Buy
    elif prob_up < sell_threshold:
        return -1  # Sell
    else:
        return 0  # Hold


if __name__ == "__main__":
    # Example usage
    model, scaler, features = load_model("AAPL")
    data = pd.read_csv("data/indicators/AAPL_features.csv", index_col=0, parse_dates=True)
    preds, probs = predict(model, scaler, features, data.tail(1))
    signal = get_trading_signal(probs)
    print(f"Prediction: {preds[0]}, Probability: {probs[0]}, Signal: {signal}")

