"""
Train machine learning models for price direction prediction.
"""
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - xgboost may not be installed in all environments
    XGBClassifier = None

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


def train_stacked_model(
    X_train,
    y_train,
    rf_estimators: int = N_ESTIMATORS,
    xgb_estimators: int = 100,
):
    """
    Train a stacked classifier combining RandomForest and XGBoost with a
    LogisticRegression meta-estimator. Falls back to RandomForest-only if
    XGBoost is not available.
    """
    logger.info("Training stacked model (RandomForest + XGBoost)...")

    rf = RandomForestClassifier(
        n_estimators=rf_estimators,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    estimators = [("rf", rf)]

    if XGBClassifier is not None:
        xgb = XGBClassifier(
            n_estimators=xgb_estimators,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0,
            n_jobs=1,
            random_state=RANDOM_STATE,
        )
        estimators.append(("xgb", xgb))
    else:
        logger.warning("XGBoost not available; falling back to RandomForest only in stacking.")

    final_est = LogisticRegression(max_iter=1000)

    stacker = StackingClassifier(
        estimators=estimators,
        final_estimator=final_est,
        passthrough=False,
        n_jobs=-1,
    )

    stacker.fit(X_train, y_train)

    logger.info("Stacked model training completed")
    return stacker


def save_model(model, scaler, feature_cols, ticker: str):
    """
    Save trained model artifacts.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODELS_DIR / f"{ticker}_model.pkl")
    joblib.dump(scaler, MODELS_DIR / f"{ticker}_scaler.pkl")
    joblib.dump(feature_cols, MODELS_DIR / f"{ticker}_features.pkl")

    logger.info(f"Saved model artifacts for {ticker}")


def train_improved_stacked_model(
    X_train,
    y_train,
    rf_estimators: int = 200,
    xgb_estimators: int = 200,
    gb_estimators: int = 100,
):
    """
    Train an improved stacked classifier combining RandomForest, XGBoost, and 
    GradientBoosting with optimized hyperparameters for better accuracy.
    """
    logger.info("Training improved stacked model (RF + XGB + GB)...")

    rf = RandomForestClassifier(
        n_estimators=rf_estimators,
        max_depth=15,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    estimators = [("rf", rf)]

    if XGBClassifier is not None:
        xgb = XGBClassifier(
            n_estimators=xgb_estimators,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0,
            n_jobs=1,
            random_state=RANDOM_STATE,
        )
        estimators.append(("xgb", xgb))
    else:
        logger.warning("XGBoost not available; using RF and GB only.")

    gb = GradientBoostingClassifier(
        n_estimators=gb_estimators,
        max_depth=5,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
    )
    estimators.append(("gb", gb))

    final_est = LogisticRegression(max_iter=1000)

    stacker = StackingClassifier(
        estimators=estimators,
        final_estimator=final_est,
        passthrough=False,
        n_jobs=-1,
    )

    stacker.fit(X_train, y_train)

    logger.info("Improved stacked model training completed")
    return stacker


def tune_xgboost_hyperparameters(X_train, y_train):
    """
    Use GridSearchCV to find optimal XGBoost hyperparameters.
    Returns the best estimator and its CV score.
    """
    if XGBClassifier is None:
        logger.error("XGBoost not installed, skipping hyperparameter tuning")
        return None, None

    logger.info("Starting XGBoost hyperparameter tuning...")

    param_grid = {
        'max_depth': [4, 5, 6],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [100, 150, 200],
        'subsample': [0.7, 0.8, 0.9],
    }

    xgb_grid = GridSearchCV(
        XGBClassifier(eval_metric='logloss', random_state=RANDOM_STATE, n_jobs=1),
        param_grid,
        cv=3,
        n_jobs=-1,
        verbose=1,
    )

    xgb_grid.fit(X_train, y_train)
    
    logger.info(f"Best XGBoost parameters: {xgb_grid.best_params_}")
    logger.info(f"Best CV score: {xgb_grid.best_score_:.4f}")

    return xgb_grid.best_estimator_, xgb_grid.best_score_


def train_tuned_stacked_model(X_train, y_train, X_test=None, y_test=None):
    """
    Train a stacked model using tuned XGBoost hyperparameters.
    Optionally returns accuracy comparison if test data is provided.
    """
    logger.info("Training stacked model with tuned hyperparameters...")

    # Get tuned XGBoost
    best_xgb, _ = tune_xgboost_hyperparameters(X_train, y_train)

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    estimators = [("rf", rf)]

    if best_xgb is not None:
        estimators.append(("xgb", best_xgb))

    gb = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
    )
    estimators.append(("gb", gb))

    final_est = LogisticRegression(max_iter=1000)

    stacker = StackingClassifier(
        estimators=estimators,
        final_estimator=final_est,
        passthrough=False,
        n_jobs=-1,
    )

    stacker.fit(X_train, y_train)

    logger.info("Tuned stacked model training completed")

    # Return accuracy metrics if test data provided
    if X_test is not None and y_test is not None:
        y_pred = stacker.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Tuned Model Test Accuracy: {accuracy:.4f}")
        return stacker, accuracy
    
    return stacker, None



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

        # Train stacked model (RandomForest + XGBoost when available)
        try:
            model = train_stacked_model(X_train, y_train)
        except Exception as e:
            logger.error(f"Stacked training failed, falling back to RandomForest: {e}")
            model = train_random_forest(X_train, y_train)

        save_model(model, scaler, features, ticker)


if __name__ == "__main__":
    train_all_tickers()
