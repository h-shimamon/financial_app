# ui.py

import streamlit as st
import pandas as pd

def show_table(
    df: pd.DataFrame,
    title: str,
    transpose: bool = False,
    color_subset: list[str] | None = None,
    unit: str = ""
):
    """
    DataFrame をエクスパンダー内に表示する共通関数。
    - transpose: 転置表示するかどうか
    - color_subset: 背景グラデーションをかける列 (非転置時のみ)
    - unit: "{:.1f}" の後に付与する文字列 (例: "%" や "千円")
    """
    with st.expander(title, expanded=True):
        # ベースの表示用 DF
        disp = df.set_index("年度")
        if transpose:
            disp = disp.T
            disp.index.name = "指標"
            # 転置時はカラーは無視し、単位のみ付与
            if unit:
                styled = disp.round(1).astype(str) + unit
                st.dataframe(styled, use_container_width=True)
            else:
                st.dataframe(disp, use_container_width=True)
            return

        # 非転置時の表示
        if color_subset:
            try:
                # matplotlib 利用可能ならグラデーション
                sty = disp.style.background_gradient(subset=color_subset, axis=0)
                sty = sty.format("{:.1f}" + unit)
                st.dataframe(sty, use_container_width=True)
            except ImportError:
                # matplotlib がなければ通常表示で単位のみ付与
                if unit:
                    styled = disp.round(1).astype(str) + unit
                    st.dataframe(styled, use_container_width=True)
                else:
                    st.dataframe(disp, use_container_width=True)
        else:
            # カラーなし・非転置
            if unit:
                styled = disp.round(1).astype(str) + unit
                st.dataframe(styled, use_container_width=True)
            else:
                st.dataframe(disp, use_container_width=True)
