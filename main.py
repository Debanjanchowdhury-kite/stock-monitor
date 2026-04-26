"""
main.py — entry point. Run this from cron / cloud function once a day.

Usage:
    python main.py
"""
import logging
from config import (
    US_BUY_WATCHLIST, INDIA_BUY_WATCHLIST, INDIA_HOLDINGS, ALERT_MODE,
    PROFIT_THRESHOLD_PCT, DROP_THRESHOLD_PCT,
)
from fetcher_us import fetch_us_prices
from fetcher_india import fetch_india_prices
from signals import (
    check_buy_signal, check_sell_signal, load_state, save_state,
)
from notifier import send_telegram, format_buy_alert, format_sell_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")


def run_us_buy_alerts(state: dict) -> int:
    print(f"\n--- US BUY CHECK (drop threshold {DROP_THRESHOLD_PCT}%) ---")
    prices = fetch_us_prices(US_BUY_WATCHLIST)
    fired = 0
    for sym, p in prices.items():
        print(f"  [US]    {sym:<12} current={p['current']:>10.2f}  prev={p['prev_close']:>10.2f}")
        alert = check_buy_signal(sym, p["current"], p["prev_close"], state)
        if alert:
            print(f"          --> BUY ALERT triggered ({alert['drop_pct']:.2f}% off {alert['ref_label']})")
            send_telegram(format_buy_alert("US", alert, "INDmoney"))
            fired += 1
    return fired


def run_india_buy_alerts(state: dict) -> int:
    print(f"\n--- INDIA BUY CHECK (drop threshold {DROP_THRESHOLD_PCT}%) ---")
    prices = fetch_india_prices(INDIA_BUY_WATCHLIST)
    fired = 0
    for sym, p in prices.items():
        alert = check_buy_signal(sym, p["current"], p["prev_close"], state)
        if alert:
            print(f"          --> BUY ALERT triggered ({alert['drop_pct']:.2f}% off {alert['ref_label']})")
            send_telegram(format_buy_alert("India", alert, "Zerodha"))
            fired += 1
    return fired


def run_india_sell_alerts() -> int:
    print(f"\n--- INDIA SELL CHECK (profit threshold {PROFIT_THRESHOLD_PCT}%) ---")
    holdings = list(INDIA_HOLDINGS.keys())
    prices = fetch_india_prices(holdings)
    fired = 0
    print(f"\n  {'Symbol':<12} {'AvgCost':>10} {'Current':>10} {'Profit%':>10}")
    print(f"  {'-' * 48}")
    for sym in holdings:
        if sym not in prices:
            print(f"  {sym:<12} {INDIA_HOLDINGS[sym]['avg_cost']:>10.2f} {'NO DATA':>10}")
            continue
        h = INDIA_HOLDINGS[sym]
        cur = prices[sym]["current"]
        pct = (cur - h["avg_cost"]) / h["avg_cost"] * 100
        flag = "  <-- ALERT" if pct >= PROFIT_THRESHOLD_PCT else ""
        print(f"  {sym:<12} {h['avg_cost']:>10.2f} {cur:>10.2f} {pct:>9.2f}%{flag}")
        alert = check_sell_signal(sym, cur, h["avg_cost"], h["qty"])
        if alert:
            send_telegram(format_sell_alert(alert))
            fired += 1
    return fired


def main():
    print(f"\n{'=' * 60}")
    print(f"STOCK MONITOR — mode={ALERT_MODE}")
    print(f"{'=' * 60}")
    state = load_state()

    us_fired = run_us_buy_alerts(state)
    in_buy_fired = run_india_buy_alerts(state)
    in_sell_fired = run_india_sell_alerts()

    save_state(state)
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: US buy={us_fired} | India buy={in_buy_fired} | India sell={in_sell_fired}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
