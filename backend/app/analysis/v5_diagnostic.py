"""v5 Diagnostic: comprehensive test of all 3 detectors across 9 data regimes.

Each regime is engineered to trigger a specific detector.
Tests verify the detector logic works correctly on synthetic data
that matches each market structure pattern.
"""
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.analysis.market_structure import (
    detect_consolidation,
    detect_sweep,
    detect_breakout,
    analyze_volatility,
    analyze_momentum,
)
from app.analysis.indicators import add_all_indicators

# ── data generators ──────────────────────────────────────────────────────────

def flat_data(bars: int = 120, price: float = 100.0, noise: float = 0.05, seed: int = 42) -> pd.DataFrame:
    """Generate flat/noisy data — mean-reverting around a fixed price (keeps ADX low)."""
    rng = np.random.default_rng(seed)
    closes = [price]
    for _ in range(bars - 1):
        step = rng.normal(0, noise) - 0.1 * (closes[-1] - price)
        closes.append(closes[-1] + step)
    df = pd.DataFrame({"close": closes})
    df["high"] = df["close"] + abs(rng.normal(0, noise * 0.6, bars))
    df["low"] = df["close"] - abs(rng.normal(0, noise * 0.6, bars))
    df["open"] = df["close"].shift(1).fillna(price)
    df["volume"] = 1000
    return df


def uptrend_then_consolidation(
    bars_uptrend: int = 40,
    bars_consolidation: int = 20,
    noise: float = 0.3,
    seed: int = 101,
) -> pd.DataFrame:
    """Strong uptrend followed by tight consolidation range."""
    rng = np.random.default_rng(seed)
    prices = []
    # Uptrend
    p = 100.0
    for _ in range(bars_uptrend):
        p += rng.uniform(0.4, 0.8)
        prices.append(p)
    # Consolidation — tight range
    consol_center = prices[-1]
    for _ in range(bars_consolidation):
        p = consol_center + rng.uniform(-0.3, 0.3)
        prices.append(p)
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.02, 0.2, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.02, 0.2, len(df)))
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    return df


def prior_range_then_consolidation(
    bars_range: int = 60,
    bars_consolidation: int = 18,
    seed: int = 201,
) -> pd.DataFrame:
    """Prior range then tight consolidation — ADX already low from range."""
    rng = np.random.default_rng(seed)
    prices = [100.0]
    # Prior range
    for _ in range(bars_range):
        prices.append(prices[-1] + rng.normal(0, 0.8))
    # Consolidation — tight range
    consol_center = prices[-1]
    for _ in range(bars_consolidation):
        prices.append(consol_center + rng.uniform(-0.25, 0.25))
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.02, 0.2, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.02, 0.2, len(df)))
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    return df


def consolidation_then_sweep(
    bars_consol: int = 20,
    bars_sweep_approach: int = 5,
    sweep_depth: float = 1.8,
    seed: int = 301,
) -> pd.DataFrame:
    """Tight consolidation, then a sweep below support with close-back."""
    rng = np.random.default_rng(seed)
    prices = [100.0]
    # Prior range
    for _ in range(40):
        prices.append(prices[-1] + rng.normal(0, 0.8))
    # Consolidation tight range
    consol_center = prices[-1]
    for _ in range(bars_consol):
        prices.append(consol_center + rng.uniform(-0.2, 0.2))
    # Support level = min during consolidation
    support = min(prices[-bars_consol:])
    # Drift toward support
    for _ in range(bars_sweep_approach):
        direction = support - prices[-1]
        step = direction * 0.3 + rng.normal(0, 0.1)
        prices.append(prices[-1] + step)
    # Sweep bar: break below support, then close back
    last = prices[-1]
    sweep_low = support - sweep_depth
    sweep_close = support + 0.1  # close back inside range
    prices.append(sweep_close)
    low_sweep = sweep_low
    high_sweep = support + 0.4

    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.02, 0.3, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.02, 0.3, len(df)))
    # Override last bar for sweep
    df.loc[df.index[-1], "low"] = low_sweep
    df.loc[df.index[-1], "high"] = high_sweep
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    return df


def consolidation_then_breakout(
    bars_consol: int = 20,
    breakout_size: float = 2.0,
    seed: int = 401,
) -> pd.DataFrame:
    """Tight consolidation, then a breakout above range high."""
    rng = np.random.default_rng(seed)
    prices = [100.0]
    # Prior range
    for _ in range(40):
        prices.append(prices[-1] + rng.normal(0, 0.8))
    # Consolidation
    consol_center = prices[-1]
    for _ in range(bars_consol):
        prices.append(consol_center + rng.uniform(-0.2, 0.2))
    # Breakout bar
    range_high = max(prices[-bars_consol:])
    prices.append(range_high + breakout_size)
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.02, 0.4, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.02, 0.3, len(df)))
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    # Increase ATR on last bar
    last_idx = df.index[-1]
    df.loc[last_idx, "high"] = df.loc[last_idx, "close"] + breakout_size * 0.3
    df.loc[last_idx, "low"] = df.loc[last_idx, "close"] - 0.1
    return df


def strong_downtrend(bars: int = 80, seed: int = 501) -> pd.DataFrame:
    """Strong downtrend for momentum analysis."""
    rng = np.random.default_rng(seed)
    prices = [100.0]
    for _ in range(bars):
        prices.append(prices[-1] - rng.uniform(0.3, 0.7))
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.02, 0.3, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.02, 0.3, len(df)))
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    return df


def choppy_range(bars: int = 100, seed: int = 601) -> pd.DataFrame:
    """Choppy range with moderate ADX (< 25) for consolidation testing."""
    rng = np.random.default_rng(seed)
    prices = [100.0]
    for _ in range(bars):
        step = rng.normal(0, 0.5) - 0.08 * (prices[-1] - 100.0)
        prices.append(prices[-1] + step)
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.05, 0.4, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.05, 0.4, len(df)))
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    return df


def ultra_tight_range(bars: int = 80, seed: int = 701) -> pd.DataFrame:
    """Extremely tight range — pins within 0.5%."""
    rng = np.random.default_rng(seed)
    center = 100.0
    prices = [center]
    for _ in range(bars):
        prices.append(center + rng.uniform(-0.08, 0.08))
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.01, 0.05, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.01, 0.05, len(df)))
    df["open"] = df["close"].shift(1).fillna(center)
    df["volume"] = 1000
    return df


def sweep_above(bars_consol: int = 20, seed: int = 801) -> pd.DataFrame:
    """Consolidation then sweep above resistance with close-back."""
    rng = np.random.default_rng(seed)
    prices = [100.0]
    for _ in range(40):
        prices.append(prices[-1] + rng.normal(0, 0.8))
    consol_center = prices[-1]
    for _ in range(bars_consol):
        prices.append(consol_center + rng.uniform(-0.2, 0.2))
    resistance = max(prices[-bars_consol:])
    for _ in range(5):
        direction = prices[-1] - consol_center
        prices.append(prices[-1] + direction * 0.3 + rng.normal(0, 0.1))
    # Sweep bar: break above resistance, close back
    sweep_high = resistance + 1.5
    sweep_close = resistance - 0.1
    prices.append(sweep_close)
    df = pd.DataFrame({"close": prices})
    df["high"] = df["close"] + abs(rng.uniform(0.02, 0.3, len(df)))
    df["low"] = df["close"] - abs(rng.uniform(0.02, 0.3, len(df)))
    df.loc[df.index[-1], "high"] = sweep_high
    df.loc[df.index[-1], "low"] = consol_center - 0.3
    df["open"] = df["close"].shift(1).fillna(100.0)
    df["volume"] = 1000
    return df


# ── test harness ──────────────────────────────────────────────────────────────

def run_regime(name: str, df: pd.DataFrame, expect_consolidation: bool, expect_sweep: bool, expect_breakout: bool):
    """Run all detectors on a data regime and report results with detailed diagnostics."""
    df_enhanced = add_all_indicators(df.copy())
    last = df_enhanced.iloc[-1]

    consol = detect_consolidation(df_enhanced)
    sweep = detect_sweep(df_enhanced)
    breakout = detect_breakout(df_enhanced)
    vol = analyze_volatility(df_enhanced)
    mom = analyze_momentum(df_enhanced)

    status = "✅" if (consol == expect_consolidation and sweep == expect_sweep and breakout == expect_breakout) else "❌"

    # ── detailed metrics ──
    adx = last.get("adx", 0)
    atr_val = last.get("atr", 0)
    atr_mean = df_enhanced["atr"].rolling(20).mean().iloc[-1]
    atr_ratio = atr_val / atr_mean if atr_mean and atr_mean > 0 else 999

    h10 = df_enhanced["high"].tail(10).max()
    l10 = df_enhanced["low"].tail(10).min()
    h50 = df_enhanced["high"].tail(50).max()
    l50 = df_enhanced["low"].tail(50).min()
    recent_range = h10 - l10
    total_range = h50 - l50
    range_ratio = recent_range / total_range if total_range > 0 else 999

    rsi = last.get("rsi", 50)

    prim_ok = adx < 25 and atr_ratio < 0.9 and range_ratio < 0.3
    fb_ultra = range_ratio < 0.15
    fb_atr = adx < 25 and range_ratio < 0.35 and atr_ratio < 1.0

    # Sweep details
    recent_high = df_enhanced["high"].iloc[-11:-1].max()
    recent_low = df_enhanced["low"].iloc[-11:-1].min()
    last_high = last.get("high", 0)
    last_low = last.get("low", 0)
    last_close = last.get("close", 0)
    last_open = last.get("open", 0)
    wick_upper = last_high - max(last_open, last_close)
    wick_lower = min(last_open, last_close) - last_low
    range_sz = last_high - last_low
    long_wick_above = wick_upper > range_sz * 0.5 if range_sz > 0 else False
    long_wick_below = wick_lower > range_sz * 0.5 if range_sz > 0 else False
    broke_high = last_high > recent_high
    broke_low = last_low < recent_low
    closed_back = (last_close < recent_high) and (last_close > recent_low)
    directional_aligned = False
    if broke_low:
        directional_aligned = "bearish" in mom
    elif broke_high:
        directional_aligned = "bullish" in mom

    print(f"  {status} {name}")
    print(f"       consolidation={consol} (expect {expect_consolidation})")
    print(f"       sweep={sweep} (expect {expect_sweep})")
    print(f"       breakout={breakout} (expect {expect_breakout})")
    print(f"       vol={vol}  mom={mom}  ADX={adx:.1f}  RSI={rsi:.1f}")
    print(f"       atr_ratio={atr_ratio:.3f}  range_ratio={range_ratio:.3f}  recent_range={recent_range:.3f}  total_range={total_range:.3f}")
    print(f"       consol conditions — primary={prim_ok}  ultra_tight={fb_ultra}  low_adx_atr={fb_atr}")
    if "sweep" in name.lower() or name.startswith("6.") or name.startswith("7."):
        print(f"       sweep details — broke_high={broke_high} broke_low={broke_low} closed_back={closed_back}")
        print(f"                       long_wick_above={long_wick_above} long_wick_below={long_wick_below}")
        print(f"                       wick_upper={wick_upper:.3f} wick_lower={wick_lower:.3f} range={range_sz:.3f}")
        print(f"                       directional_aligned={directional_aligned} (mom={mom})")
    print()

    return consol == expect_consolidation and sweep == expect_sweep and breakout == expect_breakout


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 72)
    print("  v5 DIAGNOSTIC — 9 Data Regimes × 3 Detectors")
    print("=" * 72)
    print()

    regimes = [
        ("1. Prior range → tight consolidation", prior_range_then_consolidation(), True, False, False),
        ("2. Uptrend → consolidation (stress test)", uptrend_then_consolidation(), True, False, False),
        ("3. Flat data (random walk)", flat_data(), True, False, False),
        ("4. Choppy range", choppy_range(), True, False, False),
        ("5. Ultra-tight range (pinned)", ultra_tight_range(), True, False, False),
        ("6. Consolidation → sweep below", consolidation_then_sweep(), False, True, False),
        ("7. Consolidation → sweep above", sweep_above(), False, True, False),
        ("8. Consolidation → breakout", consolidation_then_breakout(), False, False, True),
        ("9. Strong downtrend (no patterns)", strong_downtrend(), False, False, False),
    ]

    passed = 0
    failed = 0

    for name, df, exp_c, exp_s, exp_b in regimes:
        ok = run_regime(name, df, exp_c, exp_s, exp_b)
        if ok:
            passed += 1
        else:
            failed += 1

    print("=" * 72)
    print(f"  RESULTS: {passed}/{passed + failed} regimes passed")
    if failed:
        print(f"  ❌ {failed} regime(s) FAILING — see details above")
    else:
        print("  ✅ ALL REGIMES PASSED")
    print("=" * 72)
