"""
fetcher_india.py — fetches NSE prices via nsepython (free, no auth).

nsepython scrapes NSE's public endpoints. It can occasionally fail when NSE
changes their website, so we wrap every call in try/except.
"""
import logging
import time
from nsepython import nse_eq

log = logging.getLogger(__name__)


def fetch_india_prices(symbols: list[str]) -> dict:
    """
    Returns: { "GOLDBEES": {"current": 78.50, "prev_close": 78.10}, ... }

    nse_eq() returns a dict with priceInfo.lastPrice and priceInfo.previousClose.
    We sleep 1s between calls to avoid hammering NSE.
    """
    out = {}
    for sym in symbols:
        try:
            data = nse_eq(sym)
            price_info = data.get("priceInfo", {})
            current = float(price_info.get("lastPrice", 0))
            prev_close = float(price_info.get("previousClose", 0))
            if current == 0 or prev_close == 0:
                log.warning("Zero price returned for %s — skipping", sym)
                continue
            out[sym] = {"current": current, "prev_close": prev_close}
            time.sleep(1)  # polite delay
        except Exception as e:
            log.warning("Failed to fetch %s from NSE: %s", sym, e)
    return out
