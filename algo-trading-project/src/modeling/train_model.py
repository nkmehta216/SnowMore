"""
Train machine learning models for price direction prediction.
"""
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

from src.utils.logger import get_logger
from src.utils.config import (
    DEFAULT_TICKERS,
    INDICATORS_DIR,
    MODELS_DIR,
    TEST_SIZE,
    RANDOM_STATE,
    N_ESTIMATORS,
)

logger = get_logger(__name__)


def prepare_features(
    data: pd.DataFrame,
    target_column: str = "target",
    test_size: float = TEST_SIZE,
):
    """
    Prepare features and target for time-series model training.
    """
    df = data.dropna().copy()

    # Create target if not present
    if target_column not in df.columns:
        df[target_column] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        df.dropna(inplace=True)

    # Numeric features only (exclude target)
    feature_cols = (
        df.select_dtypes(include=[np.number])
        .columns.difference([target_column])
        .tolist()
    )

    X = df[feature_cols]
    y = df[target_column]

    # Time-series split (NO SHUFFLE)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logger.info(
        f"Prepared data | Train: {X_train.shape} | Test: {X_test.shape}"
    )

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols


def train_random_forest(
    X_train,
    y_train,
    n_estimators: int = N_ESTIMATORS,
):
    """
    Train Random Forest classifier.
    """
    logger.info("Training Random Forest classifier...")

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    logger.info("Random Forest training completed")
    return model


def save_model(model, scaler, feature_cols, ticker: str):
    """
    Save trained model artifacts.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODELS_DIR / f"{ticker}_model.pkl")
    joblib.dump(scaler, MODELS_DIR / f"{ticker}_scaler.pkl")
    joblib.dump(feature_cols, MODELS_DIR / f"{ticker}_features.pkl")

    logger.info(f"Saved model artifacts for {ticker}")


def train_all_tickers():
    """
    Train models for all configured tickers.
    """
    for ticker in DEFAULT_TICKERS:
        logger.info(f"🚀 Training model for {ticker}")

        data_path = INDICATORS_DIR / f"{ticker}_features.csv"
        if not data_path.exists():
            logger.warning(f"Missing data for {ticker}, skipping")
            continue

        data = pd.read_csv(
            data_path,
            index_col=0,
            parse_dates=True,
        )

        X_train, X_test, y_train, y_test, scaler, features = prepare_features(data)

        model = train_random_forest(X_train, y_train)
        save_model(model, scaler, features, ticker)


if __name__ == "__main__":
    train_all_tickers()
