"""Очистка заказов и расчёт KPI."""
from __future__ import annotations

import re

import pandas as pd


def normalize_phone(raw) -> str | None:
    """'8 (916) 555-12-34' -> '+79165551234'; мусор -> None."""
    digits = re.sub(r"\D+", "", str(raw if raw is not None else ""))
    if len(digits) == 11 and digits[0] in "78":
        return "+7" + digits[1:]
    if len(digits) == 10:
        return "+7" + digits
    return None


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Убирает дубли, приводит телефоны к единому виду, отбрасывает битые строки."""
    stats = {"loaded": len(df)}
    df = df.drop_duplicates("order_id", keep="last")
    stats["duplicates"] = stats["loaded"] - len(df)
    phones = df["phone"].map(normalize_phone)
    stats["phones_fixed"] = int((phones.notna() & (phones != df["phone"])).sum())
    df = df.assign(phone=phones)
    bad = df["phone"].isna() | (df["qty"] <= 0) | (df["price"] <= 0)
    stats["dropped"] = int(bad.sum())
    df = df[~bad].copy()
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["amount"] = df["qty"] * df["price"]
    stats["clean"] = len(df)
    return df, stats


def kpis(df: pd.DataFrame) -> dict:
    paid = df[df["status"] == "paid"]
    per_customer = paid.groupby("phone")["order_id"].count()
    return {
        "revenue": float(paid["amount"].sum()),
        "orders": len(df),
        "paid_orders": len(paid),
        "avg_check": float(paid["amount"].mean()) if len(paid) else 0.0,
        "cancel_rate": float((df["status"] == "cancelled").mean()) if len(df) else 0.0,
        "repeat_share": float((per_customer > 1).mean()) if len(per_customer) else 0.0,
        "daily": paid.groupby(paid["created_at"].dt.date)["amount"].sum(),
        "top_products": paid.groupby("product")["amount"].sum().sort_values(ascending=False).head(5),
        "by_channel": paid.groupby("channel")["amount"].sum().sort_values(ascending=False),
        "status": df["status"].value_counts(),
        "period": (df["created_at"].min().date(), df["created_at"].max().date()),
    }
