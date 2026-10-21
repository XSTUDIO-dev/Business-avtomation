"""Демо-данные вымышленной кофейни Ember Roasters: python -m automation.demo_data"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

PRODUCTS = [("Эфиопия Иргачеффе 250 г", 890), ("Колумбия Супремо 250 г", 790), ("Кения AA 250 г", 990),
            ("Бразилия Сантос 1 кг", 2190), ("Дрип-пакеты, 10 шт.", 650), ("Воронка V60", 1450), ("Подписка, 2 пачки", 1590)]
CHANNELS = ["Сайт", "Telegram-бот", "Mini App", "Instagram", "Авито"]
NAMES = ["Анна", "Игорь", "Мария", "Дмитрий", "Елена", "Сергей", "Ольга", "Павел", "Наталья", "Артём", "Ксения", "Виктор"]


def _dirty(rng, n):
    return rng.choice([f"+7 ({n[:3]}) {n[3:6]}-{n[6:8]}-{n[8:]}", f"8{n}", f"7{n}"])


def generate(seed=7):
    rng = random.Random(seed)
    customers = [(rng.choice(NAMES), "9" + "".join(rng.choice("0123456789") for _ in range(9))) for _ in range(140)]
    start, rows = datetime(2026, 9, 20), []
    for i in range(430):
        name, n = rng.choice(customers)
        product, price = rng.choices(PRODUCTS, [26, 22, 14, 9, 14, 5, 10])[0]
        ts = start + timedelta(days=rng.randrange(30), hours=rng.randrange(8, 23), minutes=rng.randrange(60))
        rows.append({"order_id": f"EM-{1001 + i}", "created_at": ts.strftime("%Y-%m-%d %H:%M"), "customer": name,
                     "phone": f"+7{n}" if rng.random() > .3 else _dirty(rng, n), "product": product,
                     "qty": rng.choices([1, 2, 3], [75, 20, 5])[0], "price": price,
                     "status": rng.choices(["paid", "new", "cancelled"], [82, 7, 11])[0],
                     "channel": rng.choices(CHANNELS, [34, 26, 18, 12, 10])[0]})
    rows += [dict(r) for r in rng.sample(rows, 12)]            # дубликаты
    for r in rng.sample(rows[:430], 7):
        r["phone"] = "12345"                                    # битые телефоны
    for r in rng.sample(rows[:430], 3):
        r["qty"] = 0                                            # нулевое количество
    return sorted(rows, key=lambda r: r["created_at"])


if __name__ == "__main__":
    rows = generate()
    path = Path("data/orders.csv")
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"Сохранено {len(rows)} строк → {path}")
