"""
notifier.py — sends formatted alerts to Telegram.
"""
import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_telegram(message: str) -> bool:
    if "PASTE_YOUR" in TELEGRAM_BOT_TOKEN or "PASTE_YOUR" in TELEGRAM_CHAT_ID:
        log.error("Telegram credentials not set in config.py")
        print("\n" + "=" * 60)
        print("TELEGRAM NOT CONFIGURED — would have sent:")
        print(message)
        print("=" * 60 + "\n")
        return False
    try:
        r = requests.post(
            TELEGRAM_API,
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message,
                  "parse_mode": "Markdown"},
            timeout=10,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        log.error("Telegram send failed: %s", e)
        return False


# ---------- formatters ---------------------------------------------------- #
def format_buy_alert(market: str, alert: dict, platform_hint: str) -> str:
    return (
        f"🟢 *BUY ALERT — {market}*\n\n"
        f"*Ticker:* `{alert['symbol']}`\n"
        f"*Current:* {alert['current']:.2f}\n"
        f"*Reference ({alert['ref_label']}):* {alert['reference']:.2f}\n"
        f"*Drop:* {alert['drop_pct']:.2f}%\n\n"
        f"_Buy on {platform_hint}_"
    )


def format_sell_alert(alert: dict) -> str:
    return (
        f"🔴 *SELL ALERT — India*\n\n"
        f"*Ticker:* `{alert['symbol']}`\n"
        f"*Current:* ₹{alert['current']:.2f}\n"
        f"*Avg cost:* ₹{alert['avg_cost']:.2f}\n"
        f"*Qty held:* {alert['qty']}\n"
        f"*Profit:* {alert['profit_pct']:.2f}% "
        f"(₹{alert['profit_abs']:.2f})\n\n"
        f"_Sell on Zerodha_"
    )
