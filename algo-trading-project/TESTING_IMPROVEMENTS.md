# Quick Start: Testing the Accuracy Improvements

## 🚀 How to Test the Changes

### Option 1: Run the Complete Strategy Notebook (Recommended)
```bash
# Navigate to the notebook directory
cd "c:\Users\Sunay Bhattacharjee\Desktop\AlgoTrading bot project\SnowMore\algo-trading-project"

# Open the notebook in VS Code
code notebooks/06_combined_strategy.ipynb
```

Then:
1. **Run all cells** to see the new accuracy metrics
2. Compare results with the baseline (0.5018)
3. Check the "Best Approach" accuracy at the end

---

### Option 2: Run Backtesting Script
```bash
# From the project root directory
python scripts/run_backtest_intervals.py

# Or run individual backtest
python -c "
from src.strategy.backtest import ProperBacktester
from src.strategy.combined_strategy import generate_combined_strategy
# Load your data and run backtest
"
```

---

## 📊 What to Expect

### Before Optimization
- **Accuracy**: 50.18%
- **Win Rate**: ~50%
- **Total Trades**: High (many false signals)

### After Optimization
- **Accuracy**: 52-55%+ (target improvement: +1.5-3%)
- **Win Rate**: 52-58%+
- **Total Trades**: 30-40% fewer (higher quality signals)
- **False Positives**: 20-25% reduction

---

## 🔍 Key Metrics to Monitor

When you run the notebook (cell 353-452), look for:

```
╔═══════════════════════════════════════════════════════════╗
║           COMPARISON: ML vs Strategy vs Combined          ║
╠═══════════════════════════════════════════════════════════╣
║ Approach                   Accuracy    AUC        F1      ║
║───────────────────────────────────────────────────────────║
║ ML (LSTM)                  [value]     [value]    [value] ║
║ Strategy (Technical)       [NEW]       [NEW]      [NEW]   ║
║ Combined (Voting 50/50)    [NEW]       [NEW]      [NEW]   ║
║ Combined (Weighted 70/30)  [NEW]       [NEW]      [NEW]   ║
║ Combined (Agreement)       [NEW]       [NEW]      [NEW]   ║
╚═══════════════════════════════════════════════════════════╝
```

**Target**: Strategy accuracy should increase from 0.5018 to 0.52+

---

## 💾 Files Changed

### 1. **src/utils/config.py**
- More stringent RSI thresholds
- Higher ML probability requirements
- New adaptive weighting parameters

### 2. **src/strategy/scalping_logic.py**
- Enhanced multi-tier indicator scoring
- Higher signal thresholds (3 vs 2)
- Better support for strong vs weak signals

### 3. **src/strategy/combined_strategy.py**
- Adaptive ML weighting based on confidence
- Stricter ensemble thresholds (0.6 vs 0.5)
- Weak signal filtering

---

## 🎯 Success Criteria

✅ **Minimum**: Accuracy increases to 51% (0.3% improvement)
✅ **Target**: Accuracy reaches 52-55%+ (1.5-3% improvement)
✅ **Bonus**: Win rate improves by 2-5%+

---

## 🔧 If Results Don't Meet Expectations

### Try these adjustments:
1. **Increase ML weight further**:
   ```python
   ML_DEFAULT_WEIGHT = 0.70  # Was 0.65
   ML_WEIGHT_MIN = 0.6       # Was 0.5
   ```

2. **Fine-tune probability thresholds**:
   ```python
   MIN_PROB_BUY = 0.62   # Was 0.60
   MAX_PROB_SELL = 0.38  # Was 0.40
   ```

3. **Adjust scalping thresholds**:
   ```python
   # In scalping_logic.py
   df["scalp_signal"] = np.where(
       df["scalp_score"] >= 4,  # Increase from 3 for stricter signals
       ...
   )
   ```

4. **Enable agreement-only mode**:
   ```python
   # Only trade when both ML and technical agree
   # Results in fewer trades but higher win rate
   ```

---

## 📈 Performance Optimization Checklist

- [x] Enhanced RSI signal strength
- [x] Improved Bollinger Bands logic
- [x] Better MACD crossover detection
- [x] Stricter technical signal thresholds
- [x] Higher ML probability requirements
- [x] Adaptive ML weighting system
- [x] Stricter ensemble thresholds
- [x] Weak signal filtering

---

## 🚨 Important Notes

1. **These changes are conservative** - They prioritize signal quality over signal quantity
2. **Fewer trades = Higher accuracy** - The goal is better signals, not more signals
3. **Backtest thoroughly** - Test on different date ranges and ticker symbols
4. **Monitor live** - Paper trade before deploying to real capital
5. **Keep the old code** - If needed, you can revert to the original thresholds

---

## 📞 Validation Checklist

Before deploying these changes:
- [ ] Accuracy in notebook shows improvement
- [ ] Win rate increased by 2%+
- [ ] Total number of trades decreased by 20-40%
- [ ] Backtest results are positive
- [ ] Tested on multiple ticker symbols
- [ ] Verified no lookahead bias

---

See **ACCURACY_IMPROVEMENTS.md** for detailed explanation of each change.
