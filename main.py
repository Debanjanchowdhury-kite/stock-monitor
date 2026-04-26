"""
main.py — entry point. Run this from cron / cloud function once a day.

Usage:
    python main.py
"""
import logging
from config import (
    US_BUY_WATCHLIST, INDIA_BUY_WATCHLIST, INDIA_HOLDINGS, ALERT_MODE,
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
    log.info("Fetching US prices for: %s", US_BUY_WATCHLIST)
    prices = fetch_us_prices(US_BUY_WATCHLIST)
    fired = 0
    for sym, p in prices.items():
        alert = check_buy_signal(sym, p["current"], p["prev_close"], state)
        if alert:
            send_telegram(format_buy_alert("US", alert, "INDmoney"))
            fired += 1
    return fired


def run_india_buy_alerts(state: dict) -> int:
    log.info("Fetching India prices for: %s", INDIA_BUY_WATCHLIST)
    prices = fetch_india_prices(INDIA_BUY_WATCHLIST)
    fired = 0
    for sym, p in prices.items():
        alert = check_buy_signal(sym, p["current"], p["prev_close"], state)
        if alert:
            send_telegram(format_buy_alert("India", alert, "Zerodha"))
            fired += 1
    return fired


def run_india_sell_alerts() -> int:
    holdings = list(INDIA_HOLDINGS.keys())
    log.info("Fetching India prices for sell-check: %d symbols", len(holdings))
    prices = fetch_india_prices(holdings)
    fired = 0
    for sym, p in prices.items():
        h = INDIA_HOLDINGS[sym]
        alert = check_sell_signal(sym, p["current"], h["avg_cost"], h["qty"])
        if alert:
            send_telegram(format_sell_alert(alert))
            fired += 1
    return fired


def main():
    log.info("=== Stock monitor starting (mode=%s) ===", ALERT_MODE)
    state = load_state()

    us_fired = run_us_buy_alerts(state)
    in_buy_fired = run_india_buy_alerts(state)
    in_sell_fired = run_india_sell_alerts()

    save_state(state)
    log.info("Done. Alerts fired — US buy: %d | India buy: %d | India sell: %d",
             us_fired, in_buy_fired, in_sell_fired)


if __name__ == "__main__":
    main()
