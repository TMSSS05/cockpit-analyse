## Goal
- Fix `range_low_break` scenario not triggering in `generate_scenarios()`

## Progress
### Done
- **Root cause found**: `get_closest_level()` at `levels.py:217` used `max()` instead of `min()` for `closest_below`, returning the **farthest** level below price instead of the nearest.
- **Fix applied**: `max(below, ...)` → `min(below, ...)`. Confirmed: `london_low@97.759` (dist=0.049) now correctly returned over `previous_day_low@97.711` (dist=0.097).
- **`range_low_break dir=short`** now fires with seed=42, noise=80 + tight=30 config.

### Remaining
- `breakout_bullish/bearish`, `sweep_bullish/bearish` test data generators may need separate tuning — these were failing before the fix too (data doesn't meet ADX/ATR/MM pivot thresholds).

## Key Debug
- `max(below, key=lambda l: price - l["price"])` → selects element with largest `price - l["price"]` (farthest below)
- `min(below, key=lambda l: price - l["price"])` → selects element with smallest `price - l["price"]` (nearest below)

## Relevant File
- `/home/tmsss/Documents/Trading/Cockpit-analyse/backend/app/analysis/levels.py:217` — the bug
