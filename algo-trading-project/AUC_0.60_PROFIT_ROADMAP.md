# 🎯 AUC 0.6013 → -0.15% Return: Complete Diagnostic & Fix Roadmap

## Executive Summary
Your model has an AUC of **0.6013** (weak but technically above random 0.50), yet the backtest loses **-0.15%** on 50 trades with a **40% win rate**. This is a **calibration problem**, not a fundamental strategy flaw.

**The Real Issue:**
- Model outputs probabilities: **0.10 to 0.53** (should be 0.0 to 1.0)
- Average probability: **0.2948** (thinks most bars are 70% likely to be negative!)
- This is consistent with **2.6:1 class imbalance** (71% samples are target=0)
- Your model learned: "most of the time, price won't move" → outputs near 0.3

---

## Diagnostic Report (Current Status)

### Model Calibration Issues

| Metric | Your Value | Expected | Problem |
|--------|-----------|----------|---------|
| **Max Probability** | 0.533 | 0.95+ | Model is underfitted |
| **Mean Probability** | 0.295 | 0.45+ | Predicts mostly "no trade" |
| **Prob > 0.5** | 102 samples | 40K+ | Almost no strong signals |
| **Class Ratio** | 71% : 29% | <55% : >45% | Extreme imbalance in training |
| **Win Rate** | 40% | 55%+ | Predicting worse than random |
| **Profit Factor** | 0.50 | 1.30+ | Losses exceed wins |

### Why You're Losing Despite AUC 0.6013

```
AUC measures: Can the model RANK signals from best to worst?
             (ROC curve = true positive vs false positive rates)

But AUC ≠ Profitability because:
1. You're trading TOP 2% of signals (Q=0.98)
2. At top 2%, the model outputs: 0.45 - 0.53
3. At those probabilities, the model barely distinguishes up vs down
4. So you get 40% win rate = worse than your training set's class ratio
5. Plus costs (0.016% per round trip) kill thin margins
```

**Analogy:** Your model is like a doctor who rates everyone as "probably healthy" (0.3 confidence). When you only treat the "sickest" (top 2%), they're still only 40% likely to recover. You need a model that says "this person has 85% chance of disease."

---

## Three Remediation Paths (Pick ONE)

### 🟢 PATH 1: REDUCE REGULARIZATION (Fastest Fix)

**Hypothesis:** Heavy regularization (reg_alpha=0.5, reg_lambda=3.0) prevents the model from making confident predictions.

**What to change in Cell 8 (XGBoost Training):**

```python
xgb_model = XGBClassifier(
    # ... other params ...
    reg_alpha=0.1,      # REDUCED from 0.5
    reg_lambda=0.5,     # REDUCED from 3.0  
    min_child_weight=10, # REDUCED from 50
    # ... rest same ...
)
```

**Expected result:** Model will output probabilities 0.1 to 0.8+ (not 0.1 to 0.53)

**Time to test:** 5 minutes
**Risk:** May overfit on training data (but backtest will tell you)
**Success criteria:** 
- Max probability > 0.70
- Mean probability > 0.40
- Win rate > 52% (better than baseline)

**Go to:** [Run Cells 1-15] → Check AUC is still > 0.55 → Check win rate

---

### 🟡 PATH 2: RETRAIN WITH DIFFERENT TARGET (Medium Effort)

**Hypothesis:** Your target definition (0.3% profit in 3 bars) is impossible to predict with current features. Try different horizons.

**What to change in Cell 4 (add_basic_features):**

Current:
```python
future_return = (df["Close"].shift(-horizon) - df["Close"]) / df["Close"]
df["target"] = (future_return > cost).astype(int)  # horizon=3, cost=0.0003
```

Test these combinations (one at a time):

| Horizon | Cost Threshold | Why Try |
|---------|----------------|---------|
| 1 | 0.0001 | Too short? Model can't predict 1 bar ahead |
| 5 | 0.0005 | Medium-term move, higher cost |
| 10 | 0.001 | Longer trend, capture bigger moves |
| 20 | 0.002 | Half hour move, more stationary |
| 60 | 0.005 | Your exit horizon, natural target |

**For each, run:**
```python
# Cell 4: Change horizon/cost
# Cell 5-8: Retrain model
# Check: AUC, max probability, backtest results
```

**Time to test:** 20 minutes (test 4-5 combinations)
**Risk:** Low - you're just retraining, not changing strategy
**Success criteria:** AUC > 0.58 AND max probability > 0.65

---

### 🔴 PATH 3: INVERSE TRADING SIGNAL (Nuclear Option)

**Hypothesis:** Your model is BACKWARDS - it predicts which bars will GO DOWN, not up.

**Evidence:**
- Average probability: 0.29 (thinks price will fall 71% of the time)
- Current trades: 40% win rate (would be 60% if inverted!)
- Class distribution: 71% target=0 (no upside)

**What to change in Cell 13 (Backtest Loop):**

Instead of:
```python
if prob >= ENTRY_THRESHOLD:  # Trade when confidence HIGH
    # enter position
```

Try:
```python
if prob <= np.percentile(ml_prob, 1-ENTRY_Q):  # Trade when confidence LOW
    # enter position (inverted interpretation)
```

**Time to test:** 2 minutes (edit + run Cell 13)
**Risk:** Medium - might make losses worse
**Success criteria:** Win rate jumps to 60%+

**Expected result if this works:**
- 40% win rate → 60% win rate (inverted)
- -0.15% return → +0.15% return (approximation)

---

## Recommended Action Plan

### Step 1: Test in THIS order (takes 30 minutes):

1. **Run PATH 1 (Reduce Regularization)**
   - Change reg_alpha=0.1, reg_lambda=0.5 in Cell 8
   - Run Cells 8-15
   - **If AUC > 0.55 AND win rate > 52%:** ✅ DONE! This was the issue
   - **If AUC drops < 0.52 or win rate stays low:** Continue to PATH 2

2. **If PATH 1 fails, run PATH 2 (Different target)**
   - Try horizon=10, cost=0.001 in Cell 4
   - Run Cells 4-15
   - Check AUC and win rate
   - If better: try 2-3 more horizons
   - If not: go to PATH 3

3. **If PATH 2 fails, try PATH 3 (Inverse signals)**
   - Edit Cell 13 to trade when prob <= threshold
   - Run Cell 13-15
   - **Check:** Does win rate jump from 40% to 60%?
   - **If yes:** You've been using inverse logic - flip all signals
   - **If no:** Model has zero predictive power, need retraining

### Step 2: Once you find a profitable configuration

1. **Run on full backtest** (Cells 1-15)
2. **Check:**
   - Total return > 0%
   - Win rate > 50%
   - Profit factor > 1.0
3. **Then adjust parameters:**
   - If return > 2%: too profitable? Maybe reduce position sizes
   - If return 0-1%: acceptable, lock in, start with paper trading
   - If return < -0.5%: still losing, go back to PATH 1-3

---

## Quick Reference: Exact Changes

### PATH 1 - Cell 8, Lines 235-246 (Regularization):

**FROM:**
```python
xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.01,
    subsample=0.5,
    colsample_bytree=0.5,
    min_child_weight=50,
    gamma=0.5,
    reg_alpha=0.5,
    reg_lambda=3.0,
```

**TO:**
```python
xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=4,           # +1 (let model be more complex)
    learning_rate=0.02,    # +2x (learn faster)
    subsample=0.7,         # +0.2 (more data per tree)
    colsample_bytree=0.7,  # +0.2
    min_child_weight=10,   # ÷5 (allow smaller leaves)
    gamma=0.1,             # -80% (less split penalty)
    reg_alpha=0.1,         # ÷5 (L1 penalty)
    reg_lambda=0.5,        # ÷6 (L2 penalty)
```

### PATH 2 - Cell 4, Line 146 (Target):

**FROM:**
```python
horizon=3, cost=0.0003
```

**TO (try each one by one):**
```python
horizon=1, cost=0.0001  # Tomorrow's move
horizon=5, cost=0.0005  # 5-bar move
horizon=10, cost=0.001  # Half-hour move ← Start here
horizon=20, cost=0.002  # Hourly move
```

### PATH 3 - Cell 13, Line 674 (Inverse Logic):

**FROM:**
```python
if prob >= ENTRY_THRESHOLD:
```

**TO:**
```python
if prob <= np.percentile(ml_prob, 1-ENTRY_Q):  # Inverted!
```

---

## Success Metrics

| Metric | Bad | Acceptable | Good | Excellent |
|--------|-----|-----------|------|-----------|
| **AUC** | <0.52 | 0.52-0.55 | 0.55-0.60 | >0.60 |
| **Win Rate** | <45% | 45-50% | 50-55% | >55% |
| **Profit Factor** | <1.0 | 1.0-1.2 | 1.2-1.5 | >1.5 |
| **Total Return** | <-1% | -1% to 0% | 0-2% | >2% |
| **Max Prob** | <0.6 | 0.6-0.7 | 0.7-0.85 | >0.85 |

Your target: **Get AUC > 0.58, Win Rate > 52%, Max Prob > 0.70**

---

## Common Mistakes to Avoid

❌ **Don't:** Change all three PAths at once
✅ **Do:** Test PATH 1 → if fails, test PATH 2 → if fails, test PATH 3

❌ **Don't:** Ignore the AUC when making changes
✅ **Do:** Always check that AUC stays > 0.55

❌ **Don't:** Judge on single backtest run
✅ **Do:** Run full Cells 1-15 for each test

❌ **Don't:** Trade live until you see +1-2% backtest return
✅ **Do:** Paper trade first, confirm real-time performance

---

## Questions to Answer

**Q: Why is AUC 0.6013 but I still lose money?**
A: AUC measures ranking ability, not profitability. You need high AUC + confident predictions + proper position sizing. You have AUC ✓ but weak predictions ✗ and tiny positions ✗.

**Q: My model says prob=0.53 but I need it to say 0.85?**
A: That's what PATH 1 fixes - reduce regularization so model can be more confident. Or PATH 2 - change target so model finds clearer patterns.

**Q: What if all 3 paths fail?**
A: Your features or target are fundamentally broken. You'd need to:
1. Add new features (RSI, MACD, moving average crosses)
2. Try different targets (0.5% profit, 1% profit)
3. Check for data leakage in feature engineering

---

## Next Steps

1. **Now:** Pick PATH 1 and make the code change (5 min)
2. **Then:** Run Cells 8-15 and report: AUC, max prob, win rate
3. **If successful:** Run full Cells 1-15 and check total return
4. **If still losing:** Move to PATH 2 and repeat

**Once profitable (even +0.5%):** You can scale up position sizes and optimize exit strategy.

Good luck! You're closer than you think. This is a **calibration fix**, not a strategy redesign.
