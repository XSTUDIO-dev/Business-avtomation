import pandas as pd

from automation.pipeline import clean, kpis, normalize_phone

COLS = ["order_id", "created_at", "customer", "phone", "product", "qty", "price", "status", "channel"]


def test_normalize_phone():
    assert normalize_phone("8 (916) 555-12-34") == "+79165551234"
    assert normalize_phone("+7 916 555 12 34") == "+79165551234"
    assert normalize_phone("9165551234") == "+79165551234"
    assert normalize_phone("12345") is None and normalize_phone(None) is None


def test_clean_removes_duplicates_and_garbage():
    df = pd.DataFrame([
        ["A1", "2026-10-01 10:00", "Анна", "8 916 555 12 34", "Кофе", 2, 500, "paid", "Сайт"],
        ["A1", "2026-10-01 10:00", "Анна", "8 916 555 12 34", "Кофе", 2, 500, "paid", "Сайт"],   # дубль
        ["A2", "2026-10-01 11:00", "Игорь", "123", "Кофе", 1, 500, "paid", "Сайт"],               # битый телефон
        ["A3", "2026-10-02 11:00", "Ольга", "+79031112233", "Кофе", 0, 500, "paid", "Сайт"],      # qty = 0
    ], columns=COLS)
    out, st = clean(df)
    assert (st["duplicates"], st["dropped"], len(out)) == (1, 2, 1)
    assert out.iloc[0]["phone"] == "+79165551234" and out.iloc[0]["amount"] == 1000


def test_kpis():
    df = pd.DataFrame([
        ["B1", "2026-10-01 10:00", "Анна", "+79165551234", "Кофе", 1, 1000, "paid", "Сайт"],
        ["B2", "2026-10-02 10:00", "Анна", "+79165551234", "Кофе", 1, 500, "paid", "Бот"],
        ["B3", "2026-10-02 12:00", "Ольга", "+79031112233", "Кофе", 1, 700, "cancelled", "Сайт"],
    ], columns=COLS)
    df["created_at"] = pd.to_datetime(df["created_at"]); df["amount"] = df["qty"] * df["price"]
    k = kpis(df)
    assert k["revenue"] == 1500 and k["paid_orders"] == 2 and k["avg_check"] == 750
    assert round(k["cancel_rate"], 3) == 0.333 and k["repeat_share"] == 1.0
