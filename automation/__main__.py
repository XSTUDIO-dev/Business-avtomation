"""Запуск: python -m automation --input data/orders.csv"""
import argparse
import time
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import notify, pipeline, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="automation", description="Ежедневный отчёт по заказам")
    ap.add_argument("--input", default="data/orders.csv")
    ap.add_argument("--out", default="out")
    ap.add_argument("--no-notify", action="store_true")
    a = ap.parse_args(argv)
    con, t0 = Console(), time.perf_counter()
    con.print(Panel.fit("[bold]Ember Roasters[/] · автоматизация заказов", border_style="#4f8cff"))
    df, st = pipeline.clean(pd.read_csv(a.input, dtype={"phone": str}))
    con.print(f"[green]✓[/] Загружено [bold]{st['loaded']}[/] строк из [cyan]{a.input}[/]")
    con.print(f"[green]✓[/] Удалено дублей: [bold]{st['duplicates']}[/] · исправлено телефонов: [bold]{st['phones_fixed']}[/] · "
              f"отброшено битых строк: [bold]{st['dropped']}[/]")
    k = pipeline.kpis(df)
    t = Table(show_header=True, header_style="bold #9b7bff", border_style="#3a4157")
    t.add_column("Показатель"); t.add_column("Значение", justify="right")
    for name, val in [("Период", f"{k['period'][0]:%d.%m} – {k['period'][1]:%d.%m.%Y}"), ("Выручка", report.rub(k["revenue"])),
                      ("Оплаченных заказов", str(k["paid_orders"])), ("Средний чек", report.rub(k["avg_check"])),
                      ("Доля отмен", f"{k['cancel_rate']:.1%}"), ("Повторные клиенты", f"{k['repeat_share']:.1%}")]:
        t.add_row(name, val)
    con.print(t)
    out = Path(a.out) / f"{k['period'][1]}"
    out.mkdir(parents=True, exist_ok=True)
    report.save_excel(df, k, out / "report.xlsx")
    report.save_dashboard(k, out / "dashboard.png", f"Ember Roasters — продажи {k['period'][0]:%d.%m}–{k['period'][1]:%d.%m.%Y}")
    con.print(f"[green]✓[/] Excel-отчёт: [cyan]{out / 'report.xlsx'}[/]\n[green]✓[/] Дашборд: [cyan]{out / 'dashboard.png'}[/]")
    if a.no_notify:
        con.print("[yellow]–[/] Уведомление пропущено (--no-notify)")
    elif notify.send_telegram(notify.build_message(k)):
        con.print("[green]✓[/] Сводка отправлена в Telegram")
    else:
        con.print("[yellow]–[/] Telegram не настроен: dry-run (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID)")
    con.print(f"[dim]Готово за {time.perf_counter() - t0:.1f} с[/]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
