"""
signals.py — pure logic for buy/sell decisions. No I/O, easy to unit-test.
"""
import json
import os
from config import (
    ALERT_MODE, DROP_THRESHOLD_PCT, PROFIT_THRESHOLD_PCT, STATE_FILE
)


# ---------- state file (only used in FROM_PEAK mode) ----------------------- #
def _load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------- buy signal ----------------------------------------------------- #
def check_buy_signal(symbol: str, current: float, prev_close: float,
                     state: dict) -> dict | None:
    """
    Returns a dict describing the alert if triggered, else None.

    DAILY_DROP : compare today vs yesterday's close.
    FROM_PEAK  : compare today vs highest price ever observed (state["peak"]).
    """
    if ALERT_MODE == "DAILY_DROP":
        reference = prev_close
        ref_label = "prev close"
    elif ALERT_MODE == "FROM_PEAK":
        peak = state.get(symbol, {}).get("peak", current)
        peak = max(peak, current)        # update watermark
        state.setdefault(symbol, {})["peak"] = peak
        reference = peak
        ref_label = "observed peak"
    else:
        raise ValueError(f"Unknown ALERT_MODE: {ALERT_MODE}")

    drop_pct = ((reference - current) / reference) * 100
    if drop_pct >= DROP_THRESHOLD_PCT:
        return {
            "symbol": symbol,
            "current": current,
            "reference": reference,
            "ref_label": ref_label,
            "drop_pct": drop_pct,
        }
    return None


# ---------- sell signal ---------------------------------------------------- #
def check_sell_signal(symbol: str, current: float, avg_cost: float,
                      qty: int) -> dict | None:
    profit_pct = ((current - avg_cost) / avg_cost) * 100
    if profit_pct >= PROFIT_THRESHOLD_PCT:
        return {
            "symbol": symbol,
            "current": current,
            "avg_cost": avg_cost,
            "qty": qty,
            "profit_pct": profit_pct,
            "profit_abs": (current - avg_cost) * qty,
        }
    return None


# ---------- public state helpers ------------------------------------------ #
def load_state() -> dict:
    return _load_state()


def save_state(state: dict) -> None:
    _save_state(state)
