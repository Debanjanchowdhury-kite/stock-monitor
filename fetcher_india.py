"""
fetcher_india.py — fetches NSE prices via Yahoo Finance (yfinance).

NSE blocks data-center IPs (GitHub Actions, AWS, etc.), so we use Yahoo
Finance instead — same library as the US fetcher. Indian NSE tickers on
Yahoo just need a ".NS" suffix appended (e.g., "GOLDBEES" -> "GOLDBEES.NS").
"""
import yfinance as yf
import logging

log = logging.getLogger(__name__)


def fetch_india_prices(symbols: list[str]) -> dict:
    """
    Returns: { "GOLDBEES": {"current": 78.50, "prev_close": 78.10}, ... }

    Note: Output keys are the original symbols WITHOUT ".NS" so the rest of
    the script (signals, holdings dict) keeps working unchanged.
    """
    out = {}
    for sym in symbols:
        yahoo_ticker = f"{sym}.NS"
        try:
            t = yf.Ticker(yahoo_ticker)
            hist = t.history(period="5d")
            if hist.empty or len(hist) < 2:
                log.warning("Not enough data for %s (%s)", sym, yahoo_ticker)
                continue
            current = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2])
            out[sym] = {"current": current, "prev_close": prev_close}
            log.info("Fetched %s: current=%.2f prev=%.2f",
                     sym, current, prev_close)
        except Exception as e:
            log.warning("Failed to fetch %s (%s): %s", sym, yahoo_ticker, e)
    return out
