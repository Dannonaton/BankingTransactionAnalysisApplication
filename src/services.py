import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Union

from src.utils import round_up_to_limit

logger = logging.getLogger(__name__)


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> Union[float, str]:
    """
    Рассчитывает сумму, отложенную в инвесткопилку за указанный месяц.

    Параметры:
    - month: строка в формате 'YYYY-MM'
    - transactions: список словарей с транзакциями.
       Каждая транзакция должна содержать ключи 'Дата операции' и 'Сумма операции'.
    - limit: предел округления (10, 50, 100 и т.д.)

    Возвращает сумму (float) или JSON-строку с ошибкой.
    """
    if not isinstance(limit, int) or limit <= 0:
        return json.dumps({"error": "limit must be a positive integer"}, ensure_ascii=False)

    try:
        target_year, target_month = map(int, month.split("-"))
        if not (1 <= target_month <= 12):
            raise ValueError("Month must be between 1 and 12")
    except ValueError:
        return json.dumps(
            {"error": "month must be in format YYYY-MM and month between 1 and 12"},
            ensure_ascii=False,
        )

    total_saved = 0.0
    for tx in transactions:
        date_str = tx.get("Дата операции", "")
        if not date_str:
            continue
        try:
            tx_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                tx_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
        if tx_date.year == target_year and tx_date.month == target_month:
            amount = tx.get("Сумма операции", 0.0)
            if amount < 0:
                spent = abs(amount)
                rounded = round_up_to_limit(spent, limit)
                total_saved += rounded
    return round(total_saved, 2)