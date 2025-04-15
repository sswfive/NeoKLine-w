import datetime
import pandas as pd
import tushare as ts
import streamlit as st
import mplfinance as mpf
from config import TUSHARE_TOKEN
import matplotlib.pyplot as plt
from view.llm_qa import single_content_qa
from tools.stock_data import StockData

# 检查登录状态
if 'login_status' not in st.session_state or not st.session_state['login_status']:
    st.warning("请先登录后再访问此页面")
    st.stop()

st.markdown("# 股票K线分析")

if "stock_day_bar" not in st.session_state:
    st.session_state.stock_day_bar = False
if "cache_stock_day_bar" not in st.session_state:
    st.session_state.cache_stock_day_bar = {}


# 如果不是交易日，往前找最近的交易日
def get_nearest_trading_day(selected_date, open_date_df):
    calendar_dates = pd.to_datetime(open_date_df["cal_date"]).dt.date
    valid_dates = calendar_dates[calendar_dates <= selected_date]
    if len(valid_dates) == 0:
        return None
    return valid_dates.max()


@st.cache_data
def load_stock_basic():
    return pd.read_csv("data/stock_basic.csv")


@st.cache_data
def load_stock_open_day():
    df = pd.read_csv("data/stock_calender.csv").sort_values(
        by="cal_date", ascending=True
    )
    df["cal_date"] = pd.to_datetime(df["cal_date"], format="%Y%m%d")
    df = df[df["is_open"] == 1]
    df.index = range(df.shape[0])
    return df


stock_basic_df = load_stock_basic()
open_date_df = load_stock_open_day()
stock_list = stock_basic_df["ts_code"].tolist()

s1, s2, s3 = st.columns([1, 1, 1])
stock_id = s1.selectbox("请选择股票ID", options=stock_list, index=None)
now = datetime.datetime.now()
end_date: datetime.date = s2.date_input("请选择截止日期", value=now)
real_end_date: datetime.date = get_nearest_trading_day(end_date, open_date_df)
if real_end_date is None:
    st.error("所选日期无有效交易日，请重新选择")
    st.stop()

frequency = s3.selectbox(
    "请选择历史分析时间窗口(日)", options=[5, 10, 20, 60, 120, 240], index=0
)


# 获取指定日期的前N天的交易日作为开始时间
def get_start_date(end_date, frequency, open_date_df):
    calendar_dates = open_date_df["cal_date"].sort_values(ascending=True)
    end_idx = calendar_dates[calendar_dates == pd.to_datetime(end_date)].index[0]
    start_idx = end_idx - frequency + 1
    return calendar_dates.iloc[start_idx].date()


# 反过来理解：只有选择股票ID，并且之前没有缓存的，才可以生成
b1, b2 = st.columns([1, 1])
if b1.button(
    "生成图像",
    disabled=(stock_id == None) or (len(st.session_state.cache_stock_day_bar) > 0),
):
    st.session_state.stock_day_bar = True
if b2.button("清除重新生成"):
    st.session_state.cache_stock_day_bar = {}
    st.session_state.stock_day_bar = False

if st.session_state.stock_day_bar:
    if not st.session_state.cache_stock_day_bar:
        real_start_date: datetime.date = get_start_date(
            real_end_date, frequency, open_date_df
        )

        sd = StockData()
        stock_info_dict = sd.stock_info(stock_id)
        adj_df = sd.daily(stock_id, real_start_date, real_end_date)
        # 设置mplfinance的蜡烛颜色，up为阳线颜色，down为阴线颜色
        my_color = mpf.make_marketcolors(
            up="r", down="g", edge="inherit", wick="inherit", volume="inherit"
        )
        # 设置图表的背景色
        my_style = mpf.make_mpf_style(
            marketcolors=my_color,
            figcolor="(0.82, 0.83, 0.85)",
            gridcolor="(0.82, 0.83, 0.85)",
        )
        mpf.plot(adj_df, style=my_style, type="candle", volume=True, returnfig=True)
        stock_day_bar_img_path = (
            f"tmp/daybar-{stock_id}-{real_start_date}-{real_end_date}.png"
        )
        plt.savefig(stock_day_bar_img_path)  # 保存为PNG文件
        st.session_state.cache_stock_day_bar = {
            "stock_day_bar_img_path": stock_day_bar_img_path,
            "stock_info_dict": stock_info_dict,
        }
        st.rerun()
    else:
        stock_day_bar_img_path = st.session_state.cache_stock_day_bar[
            "stock_day_bar_img_path"
        ]
        stock_info_dict = st.session_state.cache_stock_day_bar["stock_info_dict"]
        st.markdown(
            '<div style="color: red; font-weight: bold; text-align: center;">如想调整以上相关配置，请点击"清除重新分析"按钮，否则将继续展示上次分析结果</div>',
            unsafe_allow_html=True,
        )
    content = {"img": [{"value": stock_day_bar_img_path}]}
    single_content_qa(content=content)
    st.markdown(
        f"**股票代码**：{stock_id} **股票名称**：{stock_info_dict['name']} "
        f"**行业**：{stock_info_dict['industry']}  **地区**：{stock_info_dict['area']} **上市日期**：{stock_info_dict['list_date']}"
    )
    st.image(stock_day_bar_img_path)
