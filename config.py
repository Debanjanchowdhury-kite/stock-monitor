"""
config.py — All user-editable settings live here.

Fill in every section marked with >>> EDIT <<< before running.
"""

# =============================================================================
# >>> EDIT <<<  TELEGRAM BOT CREDENTIALS
# =============================================================================
# How to get these (one-time setup, takes ~2 minutes):
#   1. Open Telegram, search for "@BotFather", start a chat.
#   2. Send /newbot, follow prompts, copy the HTTP API token it gives you.
#   3. Search for "@userinfobot", start a chat — it replies with your chat ID.
# =============================================================================
import os
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


# =============================================================================
# ALERT MODE
# =============================================================================
# "DAILY_DROP" → alert when today's price is 15% below YESTERDAY'S close.
#                Almost never fires (circuit breakers usually kick in first).
#                This is what you literally asked for.
#
# "FROM_PEAK"  → alert when current price is 15% below the highest price
#                the script has observed (rolling watermark stored in
#                price_state.json). This is the practical "buy the dip" alert.
# =============================================================================
ALERT_MODE = "FROM_PEAK"    # tracks rolling peak in price_state.json

DROP_THRESHOLD_PCT = 20.0   # buy alert trigger (20% off observed peak)
PROFIT_THRESHOLD_PCT = 20.0 # sell alert trigger


# =============================================================================
# US TICKERS — buy alerts
# =============================================================================
US_BUY_WATCHLIST = ["SMH", "AIQ", "TSLA", "MSFT"]


# =============================================================================
# INDIAN TICKERS — buy alerts
# =============================================================================
# NSE symbols (no ".NS" suffix — nsepython handles that).
INDIA_BUY_WATCHLIST = ["GOLDBEES", "NIFTYBEES"]


# =============================================================================
# >>> EDIT <<<  INDIAN ETF HOLDINGS — sell alerts at +30% profit
# =============================================================================
# Loaded from your Holdings CSV. Update avg_cost if you buy more units.
# Symbol must match the NSE trading symbol exactly.
# =============================================================================
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
    "POWERGRID":  {"avg_cost": 303.60, "qty": 2},   # this is a stock, not ETF — included from your CSV
    "CPSEETF":    {"avg_cost": 87.15,  "qty": 6},
    "MOSMALL250": {"avg_cost": 15.45,  "qty": 26},
    "AXISVALUE":  {"avg_cost": 29.00,  "qty": 13},
    "MIDCAPETF":  {"avg_cost": 20.00,  "qty": 15},
    "NV20IETF":   {"avg_cost": 14.46,  "qty": 17},
    "MIDCAPIETF": {"avg_cost": 21.77,  "qty": 5},
}


# =============================================================================
# STATE FILE (used only when ALERT_MODE == "FROM_PEAK")
# =============================================================================
STATE_FILE = "price_state.json"
