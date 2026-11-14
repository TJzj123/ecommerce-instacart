import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="电商用户行为仪表盘", layout="wide")
st.title("🛒 Instacart电商销售与转化率可视化")

@st.cache_data
def load_data():
    orders = pd.read_csv("orders.csv")
    order_products = pd.read_csv("order_products.csv")
    products = pd.read_csv("products.csv")

    df_merge = pd.merge(order_products, orders, on="order_id", how="inner")
    df_merge = pd.merge(df_merge, products, on="product_id", how="inner")
    df_merge = df_merge.dropna(subset=["days_since_prior_order"])
    return df_merge

df_merge = load_data()

# 侧边栏筛选
st.sidebar.header("筛选条件")
weekday = st.sidebar.multiselect("下单星期", sorted(df_merge["order_dow"].unique()), default=sorted(df_merge["order_dow"].unique()))
hour_range = st.sidebar.slider("下单小时", 0, 23, (0, 23))

filter_df = df_merge[
    (df_merge["order_dow"].isin(weekday)) &
    (df_merge["order_hour_of_day"] >= hour_range[0]) &
    (df_merge["order_hour_of_day"] <= hour_range[1])
]

# 指标卡片
col1, col2, col3 = st.columns(3)
col1.metric("订单总数", filter_df["order_id"].nunique())
col2.metric("商品购买总量", len(filter_df))
col3.metric("用户数", filter_df["user_id"].nunique())

# 各星期订单数量
fig1 = px.histogram(filter_df, x="order_dow", title="各星期订单数量", labels={"order_dow": "星期"})
st.plotly_chart(fig1, use_container_width=True)

# 各时段订单数量
fig2 = px.histogram(filter_df, x="order_hour_of_day", title="各时段订单数量", labels={"order_hour_of_day": "下单小时"})
st.plotly_chart(fig2, use_container_width=True)

# 复购间隔分布
fig3 = px.histogram(
    filter_df.drop_duplicates("order_id"),
    x="days_since_prior_order",
    title="两次下单间隔天数",
    labels={"days_since_prior_order": "间隔天数"}
)
st.plotly_chart(fig3, use_container_width=True)
