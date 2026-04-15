import functools
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def save_to_file(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения результата отчёта в JSON-файл.
    Если filename не указан, генерирует имя на основе функции и даты.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            result = func(*args, **kwargs)
            # Определяем имя файла
            if filename is None:
                file_name = f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                file_name = filename
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Report saved to {file_name}")
            return result

        return wrapper

    return decorator


@save_to_file()
def spending_by_category(
    df: pd.DataFrame, category: str, date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Возвращает траты по заданной категории за последние 3 месяца (от переданной даты).

    Параметры:
    - df: DataFrame с транзакциями (должен содержать столбцы 'Дата операции', 'Сумма операции', 'Категория')
    - category: название категории (например, 'Супермаркеты')
    - date: опциональная строка с датой в формате 'YYYY-MM-DD HH:MM:SS' или 'YYYY-MM-DD'

    Возвращает словарь: {"category": str, "spending": float, "period_start": str, "period_end": str}
    """
    if date is None:
        end_date = datetime.now()
    else:
        try:
            end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=90)

    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    filtered = df.loc[mask]

    category_mask = filtered["Категория"] == category
    expenses = filtered.loc[category_mask & (filtered["Сумма операции"] < 0), "Сумма операции"]

    total_spent = round(abs(expenses.sum()), 2)
    # Преобразуем numpy.float64 в стандартный float для JSON-сериализации
    total_spent = float(total_spent)

    return {
        "category": category,
        "spending": total_spent,
        "period_start": start_date.strftime("%Y-%m-%d"),
        "period_end": end_date.strftime("%Y-%m-%d"),
    }