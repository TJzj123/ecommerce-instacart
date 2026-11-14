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
    orders = orders.dropna(subset=["days_since_prior_order"])
    df_merge = pd.merge(order_products, orders, on="order_id", how="inner")
    df_merge = pd.merge(df_merge, products, on="product_id", how="inner")

    np.random.seed(42)
    dept_price_map = {
        "bakery":4.5, "beverages":3.2, "snacks":2.8, "frozen":5,
        "dairy eggs":3.8, "produce":2.2, "meat seafood":8, "pantry":4
    }
    df_merge["price_base"] = df_merge["department"].map(dept_price_map)
    df_merge["product_price"] = df_merge["price_base"] * np.random.uniform(0.7,1.4,size=len(df_merge))
    df_merge["item_total"] = df_merge["product_price"]

    order_total = df_merge.groupby("order_id").agg(
        order_amount = ("item_total","sum"),
        user_id = ("user_id","first")
    ).reset_index()
    return df_merge, order_total, orders

df_merge, order_total, orders = load_data()

total_sales = order_total["order_amount"].sum()
total_order_cnt = order_total["order_id"].nunique()
avg_order_value = total_sales / total_order_cnt
user_reorder = df_merge.groupby("user_id")["reordered"].max()
reorder_rate = user_reorder.mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="总销售额", value=f"{total_sales:,.2f} $")
with col2:
    st.metric(label="平均客单价", value=f"{avg_order_value:.2f} $")
with col3:
    st.metric(label="用户复购率", value=f"{reorder_rate:.1%}")

st.divider()

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    dept_price = df_merge[["department","product_price"]].drop_duplicates(subset="product_id")
    fig_box = px.box(dept_price, x="department", y="product_price", title="各商品类别价格分布箱线图")
    st.plotly_chart(fig_box, use_container_width=True)

with row1_col2:
    funnel_data = pd.DataFrame({
        "stage":["浏览","加入购物车","下单支付","复购"],
        "count":[10000,4200,2100,950]
    })
    fig_funnel = px.funnel(funnel_data, x="count", y="stage", title="用户转化漏斗路径")
    st.plotly_chart(fig_funnel, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    daily_sale = pd.merge(order_total, orders[["order_id","order_dow"]], on="order_id")
    daily_sale = daily_sale.groupby("order_dow")["order_amount"].sum().reset_index()
    fig_sale = px.line(daily_sale, x="order_dow", y="order_amount", title="星期维度销售额趋势", markers=True)
    st.plotly_chart(fig_sale, use_container_width=True)

with row2_col2:
    top_depts = df_merge["department"].value_counts().head(8).index.tolist()
    df_top = df_merge[df_merge["department"].isin(top_depts)]
    order_dept = df_top.groupby("order_id")["department"].apply(set)
    mat = pd.DataFrame(np.zeros((len(top_depts),len(top_depts))), index=top_depts, columns=top_depts)
    for s in order_dept:
        lst = list(s)
        for i in lst:
            for j in lst:
                mat.loc[i,j] +=1
    fig_hm = px.imshow(mat, title="商品类别共同购买热力图", text_auto=".0f")
    st.plotly_chart(fig_hm, use_container_width=True)

st.markdown("### 📊说明")
st.markdown("原始数据集无商品价格，基于品类模拟单价；无浏览行为，漏斗数据为模拟演示。")
