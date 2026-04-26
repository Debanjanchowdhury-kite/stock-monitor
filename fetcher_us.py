"""
fetcher_us.py — fetches US market prices via yfinance.
"""
import yfinance as yf
import logging

log = logging.getLogger(__name__)


def fetch_us_prices(tickers: list[str]) -> dict:
    """
    Returns dict: { "SMH": {"current": 245.10, "prev_close": 248.50}, ... }
    Skips tickers that fail to fetch (logs a warning).
    """
    out = {}
    for tkr in tickers:
        try:
            t = yf.Ticker(tkr)
            # 5d window so we always have a previous close even on Mondays/holidays
            hist = t.history(period="5d")
            if hist.empty or len(hist) < 2:
                log.warning("Not enough data for %s", tkr)
                continue
            current = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2])
            out[tkr] = {"current": current, "prev_close": prev_close}
        except Exception as e:
            log.warning("Failed to fetch %s: %s", tkr, e)
    return out
