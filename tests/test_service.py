import json
import pytest
from src.services import investment_bank


def test_investment_bank_valid():
    transactions = [
        {"Дата операции": "2021-12-15 10:00:00", "Сумма операции": -1712},
        {"Дата операции": "2021-12-20 15:30:00", "Сумма операции": -250},
        {"Дата операции": "2021-11-30 23:59:59", "Сумма операции": -1000},
        {"Дата операции": "2021-12-01 00:00:00", "Сумма операции": 500},
    ]
    result = investment_bank("2021-12", transactions, 50)
    assert result == 38.0  # только первая транзакция даёт 38 рублей округления


def test_investment_bank_invalid_month_format():
    result = investment_bank("2021-13", [], 50)
    # Теперь result – строка JSON
    error_dict = json.loads(result)
    assert "error" in error_dict


def test_investment_bank_month_out_of_range():
    result = investment_bank("2021-13", [], 50)
    error_dict = json.loads(result)
    assert "error" in error_dict


def test_investment_bank_invalid_limit():
    result = investment_bank("2021-12", [], 0)
    error_dict = json.loads(result)
    assert "error" in error_dict