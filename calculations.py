# calculations.py

import pandas as pd
import numpy as np
import streamlit as st
from constants import (
    CURRENT_ASSET_COLS,
    FIXED_ASSET_COLS,
    DEPRECIATION_COL,
    CURRENT_LIAB_COLS,
    FIXED_LIAB_COLS,
    EQUITY_COLS,
    TREASURY_COL,
    COGS_COLS,
    SGA_COLS,
    BORROW_COLS,
)

def _safe_sum(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    """
    指定された cols のうち、df に存在する列だけを合計し、
    欠落している列は警告して除外します。
    """
    present = [c for c in cols if c in df.columns]
    missing = set(cols) - set(present)
    if missing:
        st.warning(f"欠損列を除外しました: {missing}")
    return df[present].sum(axis=1)

@st.cache_data
def calculate_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # すべての数値列を coercion + 欠損 0 に
    for c in df.columns.difference(["年度"]):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # BS 集計
    df["流動資産"]   = _safe_sum(df, CURRENT_ASSET_COLS)
    df["固定資産"]   = _safe_sum(df, FIXED_ASSET_COLS) - df.get(DEPRECIATION_COL, 0)
    df["流動負債"]   = _safe_sum(df, CURRENT_LIAB_COLS)
    df["固定負債"]   = _safe_sum(df, FIXED_LIAB_COLS)
    df["純資産"]     = _safe_sum(df, EQUITY_COLS) - df.get(TREASURY_COL, 0)

    # PL 集計
    df["売上原価"]       = _safe_sum(df, COGS_COLS)
    df["販売管理費総額"] = _safe_sum(df, SGA_COLS)
    df["営業利益"]       = df["売上高"] - df["売上原価"] - df["販売管理費総額"]
    df["経常利益"]       = df["営業利益"]
    df["純利益"]         = df["経常利益"]

    return df

@st.cache_data
def calculate_ratios(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    total_assets = df["流動資産"] + df["固定資産"]
    df["ROA"]     = np.where(total_assets != 0, df["純利益"] / total_assets * 100, np.nan)
    df["ROE"]     = np.where(df["純資産"] != 0, df["純利益"] / df["純資産"] * 100, np.nan)
    df["粗利益率"]           = np.where(df["売上高"] != 0,
                                       (df["売上高"] - df["売上原価"]) / df["売上高"] * 100, np.nan)
    df["売上高対営業利益率"] = np.where(df["売上高"] != 0,
                                       df["営業利益"] / df["売上高"] * 100, np.nan)
    df["売上高対経常利益率"] = np.where(df["売上高"] != 0,
                                       df["経常利益"] / df["売上高"] * 100, np.nan)
    df["売上高対当期純利益率"]= np.where(df["売上高"] != 0,
                                       df["純利益"] / df["売上高"] * 100, np.nan)
    df["売上高対販管費比率"]   = np.where(df["売上高"] != 0,
                                       df["販売管理費総額"] / df["売上高"] * 100, np.nan)
    return df[[
        "年度","ROA","ROE","粗利益率",
        "売上高対営業利益率","売上高対経常利益率",
        "売上高対当期純利益率","売上高対販管費比率"
    ]]

@st.cache_data
def calculate_break_even(df: pd.DataFrame) -> pd.DataFrame:
    df_be = pd.DataFrame({"年度": df["年度"]})
    var_ratio = np.where(df["売上高"] != 0, df["売上原価"] / df["売上高"], np.nan)
    denom     = 1 - var_ratio
    df_be["損益分岐点売上高"] = np.where(denom != 0,
                                    df["販売管理費総額"] / denom, np.nan)
    df_be["損益分岐点比率"]   = np.where(df["売上高"] != 0,
                                    df_be["損益分岐点売上高"] / df["売上高"] * 100, np.nan)
    return df_be

@st.cache_data
def calculate_turnover(df: pd.DataFrame) -> pd.DataFrame:
    df_to = pd.DataFrame({"年度": df["年度"]})
    total_assets = df["流動資産"] + df["固定資産"]
    df_to["総資本回転率"]     = np.where(total_assets != 0,
                                       df["売上高"] / total_assets, np.nan)
    df_to["固定資産回転率"]   = np.where(df["固定資産"] != 0,
                                       df["売上高"] / df["固定資産"], np.nan)
    df_to["売上債権回転期間"] = np.where(df["売上高"] != 0,
                                       df["受取手形・売掛金"] / df["売上高"] * 365, np.nan)
    df_to["棚卸資産回転期間"] = np.where(df["売上原価"] != 0,
                                       df["棚卸資産"] / df["売上原価"] * 365, np.nan)
    df_to["買入債務回転期間"] = np.where(df["売上原価"] != 0,
                                       df["支払手形・買掛金"] / df["売上原価"] * 365, np.nan)
    return df_to

@st.cache_data
def calculate_productivity(df: pd.DataFrame) -> pd.DataFrame:
    df_pr = pd.DataFrame({"年度": df["年度"]})
    df_pr["一人当たり売上高"]   = np.where(df["従業員数"] != 0,
                                       df["売上高"] / df["従業員数"], np.nan)
    df_pr["一人当たり当期純利益"]= np.where(df["従業員数"] != 0,
                                       df["純利益"] / df["従業員数"], np.nan)
    return df_pr

@st.cache_data
def calculate_liquidity(df: pd.DataFrame) -> pd.DataFrame:
    df_li = pd.DataFrame({"年度": df["年度"]})
    df_li["流動比率"] = np.where(df["流動負債"] != 0,
                               df["流動資産"] / df["流動負債"] * 100, np.nan)
    df_li["当座比率"] = np.where(df["流動負債"] != 0,
                               (df["流動資産"] - df["棚卸資産"]) / df["流動負債"] * 100, np.nan)
    return df_li

@st.cache_data
def calculate_capital_structure(df: pd.DataFrame) -> pd.DataFrame:
    df_cs = pd.DataFrame({"年度": df["年度"]})
    total_liab = df["流動負債"] + df["固定負債"]
    denom      = total_liab + df["純資産"]
    df_cs["自己資本比率"]   = np.where(denom != 0,
                                   df["純資産"] / denom * 100, np.nan)
    df_cs["負債比率"]       = np.where(denom != 0,
                                   total_liab / denom * 100, np.nan)
    df_cs["固定長期適合率"] = np.where(df["純資産"] != 0,
                                   df["固定資産"] / df["純資産"] * 100, np.nan)
    total_assets           = df["流動資産"] + df["固定資産"]
    df_cs["固定比率"]       = np.where(total_assets != 0,
                                   df["固定資産"] / total_assets * 100, np.nan)
    return df_cs

@st.cache_data
def calculate_growth(df: pd.DataFrame) -> pd.DataFrame:
    df_gr = pd.DataFrame({"年度": df["年度"]})
    df_gr["売上高成長率"]   = df["売上高"].pct_change().fillna(0) * 100
    df_gr["経常利益成長率"] = df["経常利益"].pct_change().fillna(0) * 100
    df_gr["販管費増減率"]   = df["販売管理費総額"].pct_change().fillna(0) * 100
    df_gr["従業員数増減率"] = df["従業員数"].pct_change().fillna(0) * 100
    df_gr["総資産増加率"]   = (df["流動資産"] + df["固定資産"]).pct_change().fillna(0) * 100
    return df_gr

@st.cache_data
def calculate_value_added(df: pd.DataFrame) -> pd.DataFrame:
    df_va = pd.DataFrame({"年度": df["年度"]})
    df_va["加工高比率"]    = np.where(df["売上高"] != 0,
                                   df["加工高"] / df["売上高"] * 100, np.nan)
    df_va["労働分配率"]    = np.where(df["付加価値"] != 0,
                                   df["人件費"] / df["付加価値"] * 100, np.nan)
    df_va["資本生産性"]    = np.where((df["流動資産"] + df["固定資産"]) != 0,
                                   df["付加価値"] / (df["流動資産"] + df["固定資産"]) * 100, np.nan)
    df_va["付加価値生産性"]= np.where(df["従業員数"] != 0,
                                   df["付加価値"] / df["従業員数"], np.nan)
    return df_va

@st.cache_data
def calculate_others(df: pd.DataFrame) -> pd.DataFrame:
    df_ot = pd.DataFrame({"年度": df["年度"]})
    borrow           = _safe_sum(df, BORROW_COLS)
    total_assets     = df["流動資産"] + df["固定資産"]
    df_ot["借入金依存度"] = np.where(total_assets != 0,
                                   borrow / total_assets * 100, np.nan)
    return df_ot

@st.cache_data
def calculate_cash_flows(df: pd.DataFrame) -> pd.DataFrame:
    df_cf = pd.DataFrame({"年度": df["年度"]})
    num   = df.select_dtypes(include="number")
    delta = num.diff().fillna(0)
    df_cf["営業CF"]   = df["純利益"] + df["減価償却費"] + df["減価償却費_販管"]
    df_cf["投資CF"]   = -delta[FIXED_ASSET_COLS].sum(axis=1)
    df_cf["財務CF"]   = delta[BORROW_COLS].sum(axis=1)
    df_cf["現金増減"] = df["現金・預金"].diff().fillna(0)
    return df_cf

