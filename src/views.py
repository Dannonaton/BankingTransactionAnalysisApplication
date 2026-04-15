import json
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.utils import (
    filter_by_date_range,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_transactions_dataframe,
    load_user_settings,
)


def generate_main_page_json(
    date_time_str: str, transactions_file: str = "data/operations.xlsx"
) -> str:
    """
    Генерирует JSON для главной страницы.

    Параметры:
    - date_time_str: строка в формате 'YYYY-MM-DD HH:MM:SS'
    - transactions_file: путь к Excel-файлу с транзакциями

    Возвращает JSON-строку.
    """
    current_dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    start_of_month = current_dt.replace(day=1, hour=0, minute=0, second=0)
    end_of_month = current_dt

    df = get_transactions_dataframe(transactions_file)
    df_month = filter_by_date_range(df, start_of_month, end_of_month)

    greeting = get_greeting(current_dt)

    cards_data = []
    for card, group in df_month.groupby("Номер карты", dropna=False):
        if pd.isna(card) or str(card) == "nan":
            continue
        # Номер карты может быть числом или строкой вида "*7197"
        card_str = str(card)
        if card_str.startswith("*"):
            last_four = card_str[-4:] if len(card_str) >= 4 else card_str
        else:
            # Если пришло целое число, берём последние 4 цифры
            last_four = card_str[-4:] if len(card_str) >= 4 else card_str
        expenses = group[group["Сумма операции"] < 0]["Сумма операции"].sum()
        cashback = abs(expenses) // 100
        cards_data.append(
            {
                "last_digits": last_four,
                "total_spent": round(abs(expenses), 2),
                "cashback": cashback,
            }
        )

    df_month["abs_amount"] = df_month["Сумма операции"].abs()
    top_transactions = (
        df_month.nlargest(5, "abs_amount")[["Дата операции", "Сумма операции", "Описание"]]
        .to_dict(orient="records")
    )
    for t in top_transactions:
        t["date"] = t["Дата операции"].strftime("%Y-%m-%d %H:%M:%S")
        t["amount"] = float(t["Сумма операции"])
        del t["Дата операции"]
        del t["Сумма операции"]

    user_settings = load_user_settings()
    currencies = user_settings.get("user_currencies", ["USD", "EUR"])
    stocks = user_settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    currency_rates = get_currency_rates(currencies)
    stock_prices = get_stock_prices(stocks)

    result = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)