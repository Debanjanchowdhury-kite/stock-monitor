"""
monitor.py - All-in-one stock monitor. No imports from other local files.
"""
import os
import json
import requests
import yfinance as yf

# ============================================================
# SETTINGS
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

ALERT_MODE = "FROM_PEAK"
DROP_THRESHOLD_PCT = 20.0
PROFIT_THRESHOLD_PCT = 20.0  # set to 20 for testing; change to 30 later

US_BUY_WATCHLIST = ["SMH", "AIQ", "TSLA", "MSFT"]
INDIA_BUY_WATCHLIST = ["GOLDBEES", "NIFTYBEES"]

INDIA_HOLDINGS = {
    "ALPHA":      {"avg_cost": 49.85,  "qty": 130},
    "MAHKTECH":   {"avg_cost": 23.37,  "qty": 182},
    "MOMIDMTM":   {"avg_cost": 61.78,  "qty": 61},
    "MOMENTUM50": {"avg_cost": 51.71,  "qty": 71},
    "HNGSNGBEES": {"avg_cost": 503.22, "qty": 5},
    "HDFCSML250": {"avg_cost": 156.97, "qty": 15},
    "JUNIORBEES": {"avg_cost": 682.50, "qty": 3},
    "FMCGIETF":   {"avg_cost": 58.14,  "qty": 33},
    "IT":         {"avg_cost": 39.71,  "qty": 47},
    "BANKBEES":   {"avg_cost": 548.55, "qty": 2},
    "ICICIB22":   {"avg_cost": 113.67, "qty": 7},
    "POWERGRID":  {"avg_cost": 303.60, "qty": 2},
    "CPSEETF":    {"avg_cost": 87.15,  "qty": 6},
    "MOSMALL250": {"avg_cost": 15.45,  "qty": 26},
    "AXISVALUE":  {"avg_cost": 29.00,  "qty": 13},
    "MIDCAPETF":  {"avg_cost": 20.00,  "qty": 15},
    "NV20IETF":   {"avg_cost": 14.46,  "qty": 17},
    "MIDCAPIETF": {"avg_cost": 21.77,  "qty": 5},
}

STATE_FILE = "price_state.json"

# ============================================================
# TELEGRAM
# ============================================================
def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("WARN: Telegram credentials missing")
        print(message)
        return False
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    try:
        r = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }, timeout=10)
        r.raise_for_status()
        print("  >>> Telegram message sent")
        return True
    except Exception as e:
        print("  >>> Telegram FAILED: " + str(e))
        return False

# ============================================================
# PRICE FETCHING
# ============================================================
def fetch_price(yahoo_ticker):
    try:
        t = yf.Ticker(yahoo_ticker)
        hist = t.history(period="5d")
        if hist.empty or len(hist) < 2:
            return None, None, "no data returned"
        current = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2])
        return current, prev_close, None
    except Exception as e:
        return None, None, str(e)

# ============================================================
# STATE
# ============================================================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============================================================
# MAIN LOGIC
# ============================================================
def check_buy(symbol, current, prev_close, state):
    if ALERT_MODE == "DAILY_DROP":
        reference = prev_close
        ref_label = "prev close"
    else:
        peak = state.get(symbol, {}).get("peak", current)
        peak = max(peak, current)
        state.setdefault(symbol, {})["peak"] = peak
        reference = peak
        ref_label = "observed peak"
    drop_pct = ((reference - current) / reference) * 100 if reference > 0 else 0
    if drop_pct >= DROP_THRESHOLD_PCT:
        return {"reference": reference, "ref_label": ref_label, "drop_pct": drop_pct}
    return None

def main():
    print("============================================================")
    print("STOCK MONITOR - mode=" + ALERT_MODE)
    print("Drop threshold: " + str(DROP_THRESHOLD_PCT) + "%")
    print("Profit threshold: " + str(PROFIT_THRESHOLD_PCT) + "%")
    print("============================================================")

    state = load_state()
    us_fired = 0
    india_buy_fired = 0
    india_sell_fired = 0

    # ---------- US BUY ----------
    print("\n--- US BUY CHECK ---")
    for sym in US_BUY_WATCHLIST:
        cur, prev, err = fetch_price(sym)
        if err:
            print("  [US] " + sym + " ERROR: " + err)
            continue
        print("  [US] " + sym.ljust(12) + " current=" + f"{cur:>10.2f}" + " prev=" + f"{prev:>10.2f}")
        alert = check_buy(sym, cur, prev, state)
        if alert:
            msg = ("BUY ALERT - US\n"
                   "Ticker: " + sym + "\n"
                   "Current: " + f"{cur:.2f}" + "\n"
                   "Reference: " + f"{alert['reference']:.2f}" + "\n"
                   "Drop: " + f"{alert['drop_pct']:.2f}" + "%\n"
                   "Buy on INDmoney")
            print("  --> BUY ALERT FIRED")
            send_telegram(msg)
            us_fired += 1

    # ---------- INDIA BUY ----------
    print("\n--- INDIA BUY CHECK ---")
    for sym in INDIA_BUY_WATCHLIST:
        cur, prev, err = fetch_price(sym + ".NS")
        if err:
            print("  [INDIA] " + sym + " ERROR: " + err)
            continue
        print("  [INDIA] " + sym.ljust(12) + " current=" + f"{cur:>10.2f}" + " prev=" + f"{prev:>10.2f}")
        alert = check_buy(sym, cur, prev, state)
        if alert:
            msg = ("BUY ALERT - INDIA\n"
                   "Ticker: " + sym + "\n"
                   "Current: Rs " + f"{cur:.2f}" + "\n"
                   "Reference: Rs " + f"{alert['reference']:.2f}" + "\n"
                   "Drop: " + f"{alert['drop_pct']:.2f}" + "%\n"
                   "Buy on Zerodha")
            print("  --> BUY ALERT FIRED")
            send_telegram(msg)
            india_buy_fired += 1

    # ---------- INDIA SELL ----------
    print("\n--- INDIA SELL CHECK ---")
    print("  " + "Symbol".ljust(12) + " " + "AvgCost".rjust(10) + " " + "Current".rjust(10) + " " + "Profit%".rjust(10))
    print("  " + "-" * 48)
    for sym, h in INDIA_HOLDINGS.items():
        cur, prev, err = fetch_price(sym + ".NS")
        if err:
            print("  " + sym.ljust(12) + " " + f"{h['avg_cost']:>10.2f}" + " ERROR: " + err)
            continue
        pct = (cur - h["avg_cost"]) / h["avg_cost"] * 100
        flag = "  <-- ALERT" if pct >= PROFIT_THRESHOLD_PCT else ""
        print("  " + sym.ljust(12) + " " + f"{h['avg_cost']:>10.2f}" + " " + f"{cur:>10.2f}" + " " + f"{pct:>9.2f}" + "%" + flag)
        if pct >= PROFIT_THRESHOLD_PCT:
            profit_abs = (cur - h["avg_cost"]) * h["qty"]
            msg = ("SELL ALERT - INDIA\n"
                   "Ticker: " + sym + "\n"
                   "Current: Rs " + f"{cur:.2f}" + "\n"
                   "Avg cost: Rs " + f"{h['avg_cost']:.2f}" + "\n"
                   "Qty held: " + str(h["qty"]) + "\n"
                   "Profit: " + f"{pct:.2f}" + "% (Rs " + f"{profit_abs:.2f}" + ")\n"
                   "Sell on Zerodha")
            send_telegram(msg)
            india_sell_fired += 1

    save_state(state)

    print("\n============================================================")
    print("SUMMARY: US buy=" + str(us_fired) + " | India buy=" + str(india_buy_fired) + " | India sell=" + str(india_sell_fired))
    print("============================================================")


if __name__ == "__main__":
    main()
