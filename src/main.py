import logging
from datetime import datetime

import pandas as pd

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import get_transactions_dataframe, load_user_settings
from src.views import generate_main_page_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    json_result = generate_main_page_json("2021-12-31 23:59:59", "data/operations.xlsx")
    logger.info("Главная страница JSON:\n" + json_result)

    df = get_transactions_dataframe("data/operations.xlsx")
    transactions_list = df.to_dict(orient="records")
    for tx in transactions_list:
        if isinstance(tx["Дата операции"], pd.Timestamp):
            tx["Дата операции"] = tx["Дата операции"].strftime("%Y-%m-%d %H:%M:%S")
        tx["Сумма операции"] = float(tx["Сумма операции"])

    saved = investment_bank("2021-12", transactions_list, 50)
    logger.info(f"Инвесткопилка за 2021-12 при лимите 50: {saved} руб.")

    report = spending_by_category(df, "Супермаркеты", "2021-12-31 23:59:59")
    logger.info(f"Отчёт по категории: {report}")