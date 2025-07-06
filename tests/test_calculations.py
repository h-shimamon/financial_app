# tests/test_calculations.py

import pandas as pd
import pytest

from data import generate_template
from calculations import calculate_aggregates, calculate_ratios

@pytest.fixture
def df_template():
    # ダミーデータを用意
    return generate_template()

def test_aggregates_columns(df_template):
    df = calculate_aggregates(df_template)
    # ここで必ず存在すべき列を列挙
    expected = ["流動資産", "固定資産", "流動負債", "純資産", "売上原価", "営業利益", "純利益"]
    for col in expected:
        assert col in df.columns

def test_ratios_non_negative(df_template):
    df_agg = calculate_aggregates(df_template)
    df_rat = calculate_ratios(df_agg)
    # ROA/ROE がすべて 0 以上であること
    assert (df_rat["ROA"] >= 0).all()
    assert (df_rat["ROE"] >= 0).all()
