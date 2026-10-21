"""Сводка в Telegram (опционально)."""
import os

import httpx

from .report import rub


def build_message(k) -> str:
    a, b = k["period"]
    top = "\n".join(f"  • {n}: {rub(v)}" for n, v in k["top_products"].head(3).items())
    return (f"<b>Ember Roasters · отчёт {a:%d.%m}–{b:%d.%m}</b>\n"
            f"Выручка: <b>{rub(k['revenue'])}</b>\nОплаченных заказов: {k['paid_orders']}\n"
            f"Средний чек: {rub(k['avg_check'])}\nОтмены: {k['cancel_rate']:.1%}\n\nТоп-3:\n{top}")


def send_telegram(text: str, token: str | None = None, chat_id: str | None = None) -> bool:
    """True — отправлено; False — не заданы токен/чат (dry-run)."""
    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return False
    r = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                   json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
    r.raise_for_status()
    return True
