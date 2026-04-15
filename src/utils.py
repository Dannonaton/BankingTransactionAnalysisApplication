import json
import logging
import os
from datetime import datetime, time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

USER_SETTINGS_PATH = "user_settings.json"


def load_user_settings() -> Dict[str, Any]:
    """Загружает настройки пользователя из JSON-файла."""
    with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_transactions_dataframe(file_path: str) -> pd.DataFrame:
    """Читает Excel-файл с транзакциями и возвращает DataFrame."""
    df = pd.read_excel(file_path, sheet_name="Отчет по операциям")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def filter_by_date_range(
    df: pd.DataFrame, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    """Фильтрует DataFrame по диапазону дат (включительно)."""
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    return df.loc[mask].copy()


def get_greeting(current_time: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = current_time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: List[str]) -> Dict[str, float]:
    """Получает курсы валют к RUB через API exchangerate.host."""
    url = "https://api.exchangerate.host/latest"
    params = {"base": "RUB", "symbols": ",".join(currencies)}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        rates = data.get("rates", {})
        return {cur: rates.get(cur, 0.0) for cur in currencies}
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        return {cur: 0.0 for cur in currencies}


def get_stock_prices(stocks: List[str]) -> Dict[str, float]:
    """Получает цены акций через Alpha Vantage API."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.error("API ключ Alpha Vantage не найден")
        return {stock: 0.0 for stock in stocks}

    prices = {}
    for symbol in stocks:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key,
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            price = data.get("Global Quote", {}).get("05. price")
            prices[symbol] = float(price) if price else 0.0
        except Exception as e:
            logger.error(f"Ошибка получения цены {symbol}: {e}")
            prices[symbol] = 0.0
    return prices


def round_up_to_limit(amount: float, limit: int) -> float:
    """Округляет сумму вверх до ближайшего кратного limit."""
    if amount <= 0:
        return 0.0
    return (limit - (amount % limit)) % limit


def format_transaction_for_json(transaction: pd.Series) -> Dict[str, Any]:
    """Преобразует строку транзакции в словарь для JSON."""
    return {
        "date": transaction["Дата операции"].strftime("%Y-%m-%d %H:%M:%S"),
        "amount": float(transaction["Сумма операции"]),
        "currency": transaction["Валюта операции"],
        "description": transaction["Описание"],
        "category": transaction.get("Категория", ""),
    }