"""
Train machine learning models for price prediction.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def prepare_features(data: pd.DataFrame, target_column: str = 'target', test_size: float = 0.2):
    """
    Prepare features and target for model training.
    
    Args:
        data: DataFrame with features
        target_column: Name of target column
        test_size: Proportion of data for testing
    
    Returns:
        X_train, X_test, y_train, y_test, scaler
    """
    # Drop NaN values
    df = data.dropna()
    
    # Separate features and target
    if target_column not in df.columns:
        # Create binary target: 1 if next day price goes up, 0 otherwise
        df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        df = df.dropna()
    
    # Remove non-numeric columns and target
    feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [col for col in feature_cols if col not in [target_column, 'target']]
    
    X = df[feature_cols]
    y = df[target_column] if target_column in df.columns else df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols


def train_random_forest(X_train, y_train, n_estimators: int = 100):
    """
    Train Random Forest classifier.
    
    Args:
        X_train: Training features
        y_train: Training target
        n_estimators: Number of trees
    
    Returns:
        Trained model
    """
    logger.info("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    logger.info(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    return model


def save_model(model, scaler, feature_cols, ticker: str, output_dir: str = "models"):
    """
    Save trained model and preprocessing objects.
    
    Args:
        model: Trained model
        scaler: Fitted scaler
        feature_cols: List of feature column names
        ticker: Stock ticker
        output_dir: Directory to save model
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    model_path = Path(output_dir) / f"{ticker}_model.pkl"
    scaler_path = Path(output_dir) / f"{ticker}_scaler.pkl"
    features_path = Path(output_dir) / f"{ticker}_features.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(feature_cols, features_path)
    
    logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    # Example usage
    data = pd.read_csv("data/indicators/AAPL_features.csv", index_col=0, parse_dates=True)
    X_train, X_test, y_train, y_test, scaler, features = prepare_features(data)
    model = train_random_forest(X_train, y_train)
    save_model(model, scaler, features, "AAPL")

