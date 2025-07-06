# app.py

import streamlit as st
import pandas as pd

from data import generate_template, load_input
from calculations import (
    calculate_aggregates,
    calculate_ratios,
    calculate_break_even,
    calculate_turnover,
    calculate_productivity,
    calculate_liquidity,
    calculate_capital_structure,
    calculate_growth,
    calculate_value_added,
    calculate_others,
    calculate_cash_flows,
)
from ui import show_table
from constants import ALL_REQUIRED_COLUMNS

# ページ設定：ワイドレイアウト
st.set_page_config(
    page_title="📊 財務分析Webアプリ",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📊 財務分析Webアプリ")

    # 1. データ入力
    st.sidebar.header("📂 データ入力")
    uploaded = st.sidebar.file_uploader("Excel/CSV をアップロード", type=["xlsx","csv"])
    if uploaded:
        try:
            df_input = load_input(uploaded)
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")
            return
    else:
        df_input = generate_template()

    # 2. 必須列チェック
    missing = set(ALL_REQUIRED_COLUMNS) - set(df_input.columns)
    if missing:
        st.error(f"必須カラムが不足しています: {sorted(missing)}")
        return

    # 3. 型変換・欠損補完
    df_input = df_input.convert_dtypes()
    for c in df_input.columns.difference(["年度"]):
        df_input[c] = pd.to_numeric(df_input[c], errors="coerce").fillna(0)

    # 4. 入力データ表示
    transpose_input = st.checkbox("入力データを縦横入れ替え", key="ti")
    show_table(
        df=df_input,
        title="📥 入力データ",
        transpose=transpose_input,
    )

    # 5. 計算実行
    df_agg     = calculate_aggregates(df_input)
    df_ratios  = calculate_ratios(df_agg)
    df_be      = calculate_break_even(df_agg)
    df_to      = calculate_turnover(df_agg)
    df_pr      = calculate_productivity(df_agg)
    df_li      = calculate_liquidity(df_agg)
    df_cs      = calculate_capital_structure(df_agg)
    df_gr      = calculate_growth(df_agg)
    df_va      = calculate_value_added(df_agg)
    df_ot      = calculate_others(df_agg)
    df_cf      = calculate_cash_flows(df_agg)

    # 6. 各種指標タブ表示
    transpose_metrics = st.checkbox("指標一覧を縦横入れ替え", key="tm")
    tabs   = st.tabs([
        "📈 収益性","⚖️ 分岐点","🔄 回転率","👷 生産性",
        "💧 流動性","🏛️ 資本構成","🚀 成長性","✨ 付加価値","🔧 その他"
    ])
    dfs     = [df_ratios, df_be, df_to, df_pr, df_li, df_cs, df_gr, df_va, df_ot]
    titles  = [
        "📈 収益性分析","⚖️ 損益分岐点分析","🔄 回転率・回転期間分析",
        "👷 生産性分析","💧 短期支払能力分析","🏛️ 資本構成分析",
        "🚀 成長性分析","✨ 付加価値分析","🔧 その他指標"
    ]
    # 収益性タブのみ百分率で色付け・単位"%"
    color_subsets = [["ROA","ROE"]] + [None]*8
    units         = ["%"] + [""]*8

    for df_m, title, subset, unit, tab in zip(dfs, titles, color_subsets, units, tabs):
        with tab:
            # ── トレンドグラフ ──
            st.line_chart(df_m.set_index("年度"), use_container_width=True)
            # ── テーブル表示 ──
            show_table(
                df=df_m,
                title=title,
                transpose=transpose_metrics,
                color_subset=subset,
                unit=unit
            )

    # 7. キャッシュフロー計算書
    transpose_cf = st.checkbox("CF計算書を縦横入れ替え", key="tcf")
    # 千円単位に変換
    df_cf_disp = df_cf.copy()
    df_cf_disp[["営業CF","投資CF","財務CF","現金増減"]] = (
        df_cf_disp[["営業CF","投資CF","財務CF","現金増減"]] / 1000
    ).round(1)
    df_cf_disp.rename(
        columns=lambda c: f"{c}(千円)" if c != "年度" else c,
        inplace=True
    )
    show_table(
        df=df_cf_disp,
        title="💰 キャッシュフロー計算書",
        transpose=transpose_cf,
        unit="千円"
    )
    # グラフは常に表示
    st.bar_chart(
        df_cf.set_index("年度")[["営業CF","投資CF","財務CF"]],
        use_container_width=True
    )

if __name__ == "__main__":
    main()

