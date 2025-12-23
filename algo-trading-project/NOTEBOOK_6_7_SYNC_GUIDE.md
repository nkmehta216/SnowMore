# Notebook 6 & 7 Synchronization Guide

## Quick Summary

**Notebook 6**: Trains LightGBM models on scalping features  
**Notebook 7**: Backtests predictions from Notebook 6

### Feature Flow
```
Notebook 6 (06_combined_strategy.ipynb)
    ↓
add_scalping_features_fast()
    ↓
Train LightGBM (2 models)
    ↓
Output: y_test_prob_ml, y_test_pred_ml, y_test_ml
    ↓
Notebook 7 (07_combined_backtesting.ipynb)
    ↓
Use same features + predictions for backtesting
    ↓
SimpleBacktester runs with predictions
    ↓
Portfolio metrics (Sharpe, Return, Drawdown)
```

## Key Synchronization Points

### 1. Feature Engineering (MUST MATCH)
Both notebooks use `add_scalping_features_fast()`:
```python
# Ultra-fast indicators
RSI: 3, 5, 7 periods
MACD: (2,5) and (3,7)
Stochastic: 3, 5 periods
Volatility: 2, 3, 5 periods
EMA: 2, 3, 5 periods

# Price action
body_pct, close_position, hl_ratio, wick ratios

# Target (NOTEBOOK 6 ONLY)
0.2% profit within 5 bars
```

### 2. Model Architecture (NOTEBOOK 6)
```
LightGBM Model 1:
- n_estimators: 150
- learning_rate: 0.12
- max_depth: 7
- num_leaves: 31
- subsample: 0.8
- colsample_bytree: 0.8

LightGBM Model 2:
- n_estimators: 200
- learning_rate: 0.10
- max_depth: 6
- num_leaves: 27
- subsample: 0.85
- colsample_bytree: 0.85

Ensemble: 50/50 weighted average
Threshold: Optimized for F1 (range: 0.3-0.8, step: 0.02)
```

### 3. Strategy Signals (BOTH NOTEBOOKS)
```python
add_scalping_signals():
  RSI(5): Buy < 30, Sell > 70
  EMA(3) vs EMA(5): Buy > Sell
```

### 4. Backtesting (NOTEBOOK 7 ONLY)
```
ML Predictions: y_test_prob_ml from Notebook 6
Strategy Signals: Calculated in Notebook 7
Combined: 70% ML + 30% Strategy
SimpleBacktester: Run on combined predictions
```

## Validation Checklist

Before running Notebook 7:

✅ **Notebook 6 must complete**:
- Cell 1-5: Data loading ✓
- Cell 6: LightGBM training → outputs `y_test_prob_ml`, `y_test_pred_ml`, metrics ✓
- Cell 7-13: Not needed for Notebook 7 (optional)

✅ **Feature alignment**:
- Check feature count in Notebook 6 Cell 6
- Should match feature count in Notebook 7 Cell 6
- Both use `add_scalping_features_fast()`

✅ **Data alignment**:
- Test data shape must match
- Same date range (TEST_START to TEST_END)
- No NaN issues (both handle via `np.nan_to_num`)

✅ **Scaling**:
- Both use StandardScaler
- Notebook 6: `scaler.fit_transform(X_train_scaled)` 
- Notebook 7: `scaler.fit_transform(X_train_scaled)` → Fresh scaling per ticker

## Variable Passing

**Notebook 6 → Notebook 7** (via kernel memory):
- `test_with_features`: Feature matrix
- `y_test_ml`: Ground truth labels
- `y_test_prob_ml`: Model probabilities
- `y_test_pred_ml`: Binary predictions
- `lgb_1`, `lgb_2`: Trained models (optional, Notebook 7 trains fresh)

**Notebook 7** (independent training):
- Retrains models for each ticker independently
- Uses same hyperparameters as Notebook 6
- Generates fresh `y_test_prob_ml` for each ticker

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Feature count mismatch | Ensure both use `add_scalping_features_fast()` |
| NaN values in predictions | Use `np.nan_to_num()` before backtesting |
| Misaligned data | Check TEST_START/TEST_END in config |
| All zeros/ones predictions | Check class balance (print `y_train_ml.mean()`) |
| Threshold > 0.8 | Might indicate class imbalance; check target distribution |

## Performance Expectations

**Accuracy**: 
- Old (LSTM): ~52% with basic features
- New (LightGBM): Expected 60%+ with scalping features

**Backtest Returns**:
- Single ticker: Highly variable (+50% to -30% possible)
- Portfolio average: More stable, often 0-5% in sample
- Out-of-sample: Expect 30-50% of in-sample performance

**Sharpe Ratio**:
- Good: > 1.0
- Excellent: > 2.0 (rare in backtests)
- Poor: < 0.5 (might need adjustment)

## If Something Goes Wrong

1. **Check Notebook 6 execution**:
   ```python
   print(f"Features: {X_test_ml.shape[1]}")
   print(f"Positive rate: {y_test_ml.mean()*100:.2f}%")
   print(f"Predictions shape: {y_test_prob_ml.shape}")
   ```

2. **Check data alignment**:
   ```python
   print(f"Test data: {test_with_features.shape}")
   print(f"Predictions: {y_test_prob_ml.shape}")
   assert test_with_features.shape[0] == len(y_test_prob_ml)
   ```

3. **Check strategy signals**:
   ```python
   print(f"Strategy buys: {(strategy_signal == 1).sum()}")
   print(f"Strategy sells: {(strategy_signal == -1).sum()}")
   ```

4. **Check backtester**:
   ```python
   print(f"Total trades: {len(bt_ml.trades)}")
   print(f"Buy & hold comparison: {metrics_bh['total_return']*100:.2f}%")
   ```

## Run Order

1. **Notebook 6**: 
   - Run Cell 1-6 (stops at LightGBM results)
   - Note: `y_test_prob_ml` shape and accuracy

2. **Notebook 7**:
   - Run Cell 1-2 (load functions)
   - Run Cell 6 (single ticker backtest) → Validate 1 ticker works
   - Run Cell 9 (portfolio backtest) → Full validation
   - Run Cell 11 (conclusions) → Summary

3. **Iterate**:
   - Adjust weights (70/30) if needed
   - Modify threshold ranges if F1 optimization not working
   - Try different feature combinations (edit `add_scalping_features_fast()`)

## Success Criteria

✅ Notebook 7 runs without errors  
✅ Single ticker backtest completes  
✅ Portfolio backtest shows all tickers  
✅ Sharpe ratio > 0  
✅ Combined accuracy >= ML accuracy (ensemble benefit)  
✅ Visualization saved correctly  

---

**Last Updated**: After LightGBM integration  
**Status**: Ready for testing  
**Next**: Execute both notebooks and compare results
