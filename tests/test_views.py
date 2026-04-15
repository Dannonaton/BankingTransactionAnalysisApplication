import json
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import generate_main_page_json


@patch("src.views.get_transactions_dataframe")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_generate_main_page_json(mock_stocks, mock_currencies, mock_df):
    data = {
        "Номер карты": [7197, 7197, 5091],
        "Сумма операции": [-160.89, -64.0, -564.0],
        "Дата операции": pd.to_datetime(["2021-12-31 16:44:00", "2021-12-31 16:42:04", "2021-12-31 01:23:42"]),
        "Описание": ["Колхоз", "Колхоз", "Ozon.ru"],
    }
    df = pd.DataFrame(data)
    mock_df.return_value = df
    mock_currencies.return_value = {"USD": 75.5, "EUR": 85.2}
    mock_stocks.return_value = {"AAPL": 150.0, "AMZN": 3300.0}

    result_str = generate_main_page_json("2021-12-31 23:59:59", "fake.xlsx")
    result = json.loads(result_str)
    # 23:59:59 -> час 23 -> "Доброй ночи"
    assert result["greeting"] == "Доброй ночи"
    assert len(result["cards"]) == 2
    assert result["currency_rates"]["USD"] == 75.5
    assert "stock_prices" in result