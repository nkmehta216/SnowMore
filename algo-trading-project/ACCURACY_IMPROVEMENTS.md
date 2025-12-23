# Trading Strategy Accuracy Improvements

## Current Baseline
- **Strategy Accuracy**: 0.5018 (50.18%)
- **Improvement over ML**: 0.30%
- **Target**: Increase accuracy to 55%+ and improve win rate

## Optimization Changes

### 1. **Enhanced RSI Thresholds** (scalping_logic.py)
**Problem**: Weak oversold/overbought signals were triggering on marginal conditions.

**Changes**:
- `RSI_OVERSOLD`: 30 → **25** (stricter oversold condition)
- `RSI_OVERBOUGHT`: 70 → **75** (stricter overbought condition)
- Added **multi-tier scoring**:
  - Extreme RSI (≤25 or ≥75): **+2 or -2 points** (strong signals)
  - Moderate RSI (26-35 or 65-74): **+1 or -1 points** (weak signals)

**Expected Impact**: Reduces false signals by ~15-20%, increases signal quality

---

### 2. **Improved Bollinger Bands Logic** (scalping_logic.py)
**Problem**: Simple band touches didn't account for proximity and strength.

**Changes**:
- Close **at band**: **±2 points** (strong bounce/reversal signal)
- Close **near band** (within 25% of band width): **±1 point** (weak signal)
- Added band width calculation for context-aware scoring

**Expected Impact**: More nuanced support/resistance signals, reduces whipsaws

---

### 3. **Enhanced MACD Crossover Detection** (scalping_logic.py)
**Problem**: All MACD crossovers treated equally regardless of strength.

**Changes**:
- Strong crossover (diff > 1σ): **±2 points** (high conviction)
- Weak crossover (diff ≤ 1σ): **±1 point** (low conviction)
- Better trend change detection using standard deviation

**Expected Impact**: Distinguishes strong from weak momentum shifts

---

### 4. **Stricter Signal Thresholds** (scalping_logic.py)
**Problem**: Signals generated at score ≥2, causing too many trades.

**Changes**:
- Old threshold: `scalp_score >= 2` → **New: `scalp_score >= 3`**
- Requires **3+ indicator confirmations** instead of 2
- Filters out single-indicator noise

**Expected Impact**: ~30% fewer trades, significantly higher win rate

---

### 5. **Stricter ML Probability Thresholds** (config.py)
**Problem**: ML model being too permissive with buy/sell signals.

**Changes**:
- `MIN_PROB_BUY`: 0.55 → **0.60** (require >60% confidence)
- `MAX_PROB_SELL`: 0.45 → **0.40** (require <40% confidence)
- `ML_DEFAULT_WEIGHT`: 0.60 → **0.65** (increase reliance on ML)

**Expected Impact**: Higher quality ML predictions, fewer false positives

---

### 6. **Adaptive ML Weighting** (combined_strategy.py)
**Problem**: Fixed 60% ML weight regardless of confidence level.

**Changes**:
- **Dynamic weighting** based on ML confidence:
  - High confidence (>0.65): ML weight = 80%
  - Medium confidence (0.55-0.65): ML weight = 65%
  - Low confidence (<0.55): ML weight = 50%
- New parameters:
  - `ML_WEIGHT_MIN`: 0.5 (minimum ML influence)
  - `ML_WEIGHT_MAX`: 0.8 (maximum ML influence)

**Expected Impact**: Better signal quality through confidence-based weighting

---

### 7. **Ensemble Signal Thresholds** (combined_strategy.py)
**Problem**: Combined signals accepted too easily (threshold = 0.5).

**Changes**:
- Old threshold: score ≥ 0.5 → **New: score ≥ 0.6**
- Old threshold: score ≤ -0.5 → **New: score ≤ -0.6**
- Requires **higher agreement** between ML and technical signals

**Expected Impact**: Fewer signals but higher accuracy per trade

---

### 8. **Weak Signal Filtering** (combined_strategy.py)
**Problem**: Weak technical signals combined with no ML signal still generated trades.

**Changes**:
- New filter: Suppress signals where:
  - `scalp_score < 3` (weak technical) AND
  - `ml_signal == 0` (no ML confirmation)
- Only strong technical signals alone are accepted

**Expected Impact**: Eliminates weak edge trades, improves win rate

---

## Summary of Configuration Changes

| Parameter | Before | After | Rationale |
|-----------|--------|-------|-----------|
| RSI_OVERSOLD | 30 | 25 | Stronger oversold condition |
| RSI_OVERBOUGHT | 70 | 75 | Stronger overbought condition |
| ML_DEFAULT_WEIGHT | 0.60 | 0.65 | Increase ML reliance |
| MIN_PROB_BUY | 0.55 | 0.60 | Higher ML confidence threshold |
| MAX_PROB_SELL | 0.45 | 0.40 | Higher ML confidence threshold |
| Scalp Signal Threshold | ≥2 | ≥3 | Higher conviction required |
| Ensemble Threshold | ≥0.5 | ≥0.6 | Better signal agreement |

---

## Expected Results

### Trade Quality Improvements
- **Signal Count**: ↓ 30-40% (fewer but better trades)
- **Win Rate**: ↑ 50-55% → **52-58%** (higher accuracy per trade)
- **False Signal Reduction**: ↓ 20-25%

### Accuracy Expected to Improve From
- **Current**: 0.5018 (50.18%)
- **Target**: 0.55+ (55%+)
- **Potential Improvement**: +0.5-2.0%

---

## How to Validate These Changes

1. **Run the notebook cell to recompute accuracy**:
   - Cell 353-452 in `06_combined_strategy.ipynb`
   - Compare new accuracy vs 0.5018 baseline

2. **Check trade statistics**:
   - Total trades should decrease
   - Win rate should increase
   - Average profit per trade should improve

3. **Run backtest for 2024 data**:
   ```bash
   python scripts/run_backtest_intervals.py
   ```

4. **Monitor the combined strategy metrics** in backtesting output

---

## Files Modified

1. **src/utils/config.py** - Updated RSI and ML thresholds
2. **src/strategy/scalping_logic.py** - Enhanced indicator scoring
3. **src/strategy/combined_strategy.py** - Improved signal combination logic

---

## Next Steps if Accuracy Needs Further Improvement

1. **Increase ML weight further** (0.70+) if ML accuracy > 51%
2. **Add ATR volatility filter** (suppress signals in low volatility)
3. **Implement stop-loss optimization** in backtest engine
4. **Try different ensemble methods**:
   - Agreement-based (only trade if both agree)
   - Voting-based (majority vote from 3+ indicators)
5. **Retrain ML models** with better feature engineering
