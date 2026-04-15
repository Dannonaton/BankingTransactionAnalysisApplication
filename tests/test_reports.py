import pandas as pd
import pytest
from src.reports import spending_by_category


@pytest.fixture
def sample_df():
    """Создаёт DataFrame с транзакциями для тестирования отчётов."""
    # Генерируем 100 записей с равномерным распределением по датам
    dates = pd.date_range(start="2021-10-01", end="2022-01-31", periods=100)
    amounts = []
    categories = []
    for i in range(100):
        if i % 6 == 0:
            amounts.append(-100)
            categories.append("Супермаркеты")
        elif i % 6 == 1:
            amounts.append(-200)
            categories.append("Супермаркеты")
        elif i % 6 == 2:
            amounts.append(-50)
            categories.append("Аптеки")
        elif i % 6 == 3:
            amounts.append(-300)
            categories.append("Супермаркеты")
        elif i % 6 == 4:
            amounts.append(-400)
            categories.append("Супермаркеты")
        else:
            amounts.append(1000)
            categories.append("Пополнения")
    df = pd.DataFrame({
        "Дата операции": dates,
        "Сумма операции": amounts,
        "Категория": categories,
    })
    return df


def test_spending_by_category(sample_df):
    result = spending_by_category(sample_df, "Супермаркеты", "2021-12-31 23:59:59")
    assert result["category"] == "Супермаркеты"
    assert isinstance(result["spending"], float)
    assert "period_start" in result
    assert "period_end" in result