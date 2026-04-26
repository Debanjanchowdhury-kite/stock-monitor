"""
fetcher_india.py — fetches NSE prices via Yahoo Finance (yfinance).

Uses print() so output ALWAYS shows in GitHub Actions logs regardless
of logging configuration.
"""
import yfinance as yf


def fetch_india_prices(symbols: list[str]) -> dict:
    """
    Returns: { "GOLDBEES": {"current": 78.50, "prev_close": 78.10}, ... }
    Output keys keep original symbol (no ".NS" suffix) so the rest of
    the script keeps working unchanged.
    """
    out = {}
    for sym in symbols:
        yahoo_ticker = f"{sym}.NS"
        try:
            t = yf.Ticker(yahoo_ticker)
            hist = t.history(period="5d")
            if hist.empty or len(hist) < 2:
                print(f"  [INDIA] {sym:<12} NO DATA from Yahoo")
                continue
            current = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2])
            out[sym] = {"current": current, "prev_close": prev_close}
            print(f"  [INDIA] {sym:<12} current={current:>10.2f}  prev={prev_close:>10.2f}")
        except Exception as e:
            print(f"  [INDIA] {sym:<12} ERROR: {e}")
    return out
