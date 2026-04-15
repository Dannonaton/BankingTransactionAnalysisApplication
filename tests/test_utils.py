import pandas as pd
import pytest
from datetime import datetime
from src.utils import get_greeting, round_up_to_limit


@pytest.mark.parametrize(
    "hour, expected",
    [
        (5, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (4, "Доброй ночи"),
    ],
)
def test_get_greeting(hour, expected):
    dt = datetime(2024, 1, 1, hour, 0, 0)
    assert get_greeting(dt) == expected


@pytest.mark.parametrize(
    "amount, limit, expected",
    [
        (1712, 50, 38),
        (100, 50, 0),
        (101, 50, 49),
        (0, 50, 0),
        (250, 100, 50),
        (200, 100, 0),
    ],
)
def test_round_up_to_limit(amount, limit, expected):
    assert round_up_to_limit(amount, limit) == expected