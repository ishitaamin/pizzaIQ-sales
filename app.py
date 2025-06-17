import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import numpy as np

# Page config
st.set_page_config(page_title="🍕 Pizza Sales Dashboard", layout="wide")

# Title with styling
st.markdown("<h1 style='text-align:center; color:#E74C3C;'>🍕 Pizza Sales Insights Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar file uploader for missing files
st.sidebar.header("Upload CSV files (if missing)")
uploaded_files = {}
for fname in ["1.csv", "month_sales.csv", "avg.csv", "discount.csv", "peak_hours.csv", "pizza_sales_summary.csv", "pizza_size_distribution.csv", "yearly_sales_increase.csv"]:
    uploaded = st.sidebar.file_uploader(f"Upload {fname}", type="csv", key=fname)
    if uploaded:
        uploaded_files[fname] = uploaded

# --- Section 1: Last Week Sales ---
st.markdown("<h2 style='color:#D35400;'>1. Last Week Sales Summary</h2>", unsafe_allow_html=True)
try:
    if "1.csv" in uploaded_files:
        df1 = pd.read_csv(uploaded_files["1.csv"], parse_dates=["order_date"])
    else:
        df1 = pd.read_csv("1.csv", parse_dates=["order_date"])

    total_orders = df1.shape[0]
    total_pizzas = df1["total_quantity"].sum()
    total_revenue = df1["bill_amount"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders", total_orders)
    c2.metric("Total Pizzas Sold", total_pizzas)
    c3.metric("Total Revenue", f"₹{total_revenue:,.2f}")

    df1["weekday"] = df1["order_date"].dt.day_name()
    trend = df1.groupby("weekday")[['order_id','total_quantity']].agg(
        Orders=('order_id','count'), Pizzas=('total_quantity','sum')
    ).reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    st.subheader("📈 Orders & Pizzas Sold by Day")
    st.line_chart(trend)

    st.markdown(f"Last week, **Saturday** had the highest pizza sales with {trend.loc['Saturday', 'Pizzas']} pizzas sold.")

    # Added Insight
    avg_pizzas_per_order = total_pizzas / total_orders if total_orders else 0
    st.markdown(f"💡 On average, customers ordered about **{avg_pizzas_per_order:.2f} pizzas per order**, indicating the typical order size.")

    busiest_day_orders = trend['Orders'].idxmax()
    st.markdown(f"🔍 The busiest day by number of orders was **{busiest_day_orders}**, suggesting peak demand times to optimize staffing.")

except FileNotFoundError:
    st.warning("Please upload 1.csv for last week sales.")

st.markdown("---")

# --- Section 2: Monthly Trends ---
st.markdown("<h2 style='color:#D35400;'>2. Monthly Sales Trends</h2>", unsafe_allow_html=True)
try:
    if "month_sales.csv" in uploaded_files:
        df2 = pd.read_csv(uploaded_files["month_sales.csv"])
    else:
        df2 = pd.read_csv("month_sales.csv")

    df2['year_month'] = pd.to_datetime(df2['year_month'], format='%Y-%m')
    df2['month'] = df2['year_month'].dt.month
    df2['year'] = df2['year_month'].dt.year

    pivot = df2.pivot(index='month', columns='year', values='total_pizzas_sold')
    st.subheader("📅 Monthly Pizzas Sold by Year")
    st.line_chart(pivot)

    avg_sales = df2.groupby('month')['total_pizzas_sold'].mean()
    st.subheader("🍕 Average Pizzas Sold by Month")

    fig, ax = plt.subplots(figsize=(5,5))
    avg_sales.plot.pie(autopct='%1.1f%%', startangle=90, cmap='tab20', ax=ax)
    ax.set_ylabel('')
    st.pyplot(fig)

    df2['quarter'] = df2['year_month'].dt.to_period('Q')
    seasonal = df2.groupby('quarter')['total_pizzas_sold'].sum()
    st.subheader("📊 Quarterly Sales Trend")
    st.bar_chart(seasonal)

    st.markdown("Notice the seasonal peaks—typically sales increase in Q4, likely due to holidays.")

    # Added Insight
    highest_month = avg_sales.idxmax()
    highest_avg = avg_sales.max()
    st.markdown(f"📈 **{pd.to_datetime(highest_month, format='%m').strftime('%B')}** consistently has the highest average sales, making it a prime month for targeted promotions.")

    seasonal_diff = seasonal.max() - seasonal.min()
    if seasonal_diff > 1000:
        st.markdown("⚠️ Large seasonal fluctuations suggest adjusting inventory and staff to handle peak quarters effectively.")
    else:
        st.markdown("ℹ️ Seasonal sales remain relatively steady throughout the year.")

except FileNotFoundError:
    st.warning("Please upload month_sales.csv for monthly trends.")

st.markdown("---")

# --- Section 3: Day-Type Averages ---
st.markdown("<h2 style='color:#D35400;'>3. Day-Type Averages</h2>", unsafe_allow_html=True)
try:
    if "avg.csv" in uploaded_files:
        df3 = pd.read_csv(uploaded_files["avg.csv"])
    else:
        df3 = pd.read_csv("avg.csv")

    df3[['avg_orders_per_day','avg_pizzas_per_day','avg_revenue_per_day']] = df3[['avg_orders_per_day','avg_pizzas_per_day','avg_revenue_per_day']].apply(pd.to_numeric)
    st.dataframe(df3.set_index('day_type'))

    st.subheader("📊 Comparison by Day Type")
    st.bar_chart(df3.set_index('day_type')[['avg_orders_per_day','avg_pizzas_per_day','avg_revenue_per_day']])

    best = df3.loc[df3['avg_revenue_per_day'].idxmax(),'day_type']
    st.markdown(f"💡 Highest average revenue on: **{best}** days.")

    # Added Insight
    weekend_avg_revenue = df3.loc[df3['day_type'].isin(['Saturday', 'Sunday']), 'avg_revenue_per_day'].mean()
    weekday_avg_revenue = df3.loc[~df3['day_type'].isin(['Saturday', 'Sunday']), 'avg_revenue_per_day'].mean()
    st.markdown(f"📊 Weekends generate on average **₹{weekend_avg_revenue:.2f}** in revenue vs **₹{weekday_avg_revenue:.2f}** on weekdays, indicating higher weekend demand.")

except FileNotFoundError:
    st.warning("Please upload avg.csv for day-type averages.")

st.markdown("---")

# --- Section 4: Discount Impact ---
st.markdown("<h2 style='color:#D35400;'>4. Discount Impact on Sales</h2>", unsafe_allow_html=True)
try:
    if "discount.csv" in uploaded_files:
        df4 = pd.read_csv(uploaded_files["discount.csv"])
    else:
        df4 = pd.read_csv("discount.csv")

    df4['usage_count'] = df4['usage_count'].astype(int)
    df4 = df4[df4['discount_type']!='none']

    st.subheader("🎟️ Usage Count by Discount Type")
    st.bar_chart(df4.set_index('discount_type')['usage_count'])

    top_discount = df4.loc[df4['usage_count'].idxmax(),'discount_type']
    st.markdown(f"🎯 Most used discount: **{top_discount}**")

    # Added Insight
    total_discounts = df4['usage_count'].sum()
    st.markdown(f"💡 Discounts were used a total of **{total_discounts}** times, showing their influence on purchase behavior.")
    if 'percentage' in df4['discount_type'].values:
        st.markdown("🔎 Percentage discounts seem popular — consider emphasizing them in future campaigns for better customer engagement.")

except FileNotFoundError:
    st.warning("Please upload discount.csv for discount analysis.")

st.markdown("---")

# --- Section 5: Peak Hours ---
st.markdown("<h2 style='color:#D35400;'>5. Peak Order Hours</h2>", unsafe_allow_html=True)
try:
    if "peak_hours.csv" in uploaded_files:
        df5 = pd.read_csv(uploaded_files["peak_hours.csv"])
    else:
        df5 = pd.read_csv("updated_orders.csv")

    df5['order_hour'] = pd.to_numeric(df5['order_hour'], errors='coerce')
    df5 = df5.dropna(subset=['order_hour'])
    df5['order_hour'] = df5['order_hour'].astype(int)

    avg_by_hour = df5.groupby('order_hour')['number_of_orders'].mean()
    st.subheader("⏰ Average Orders by Hour")
    st.line_chart(avg_by_hour)

    peak = avg_by_hour.idxmax()
    st.markdown(f"⏱️ Peak hour: **{peak}:00** with average {avg_by_hour.max():.1f} orders.")

    # Added Insight
    offpeak_hours = avg_by_hour[avg_by_hour < avg_by_hour.mean()]
    st.markdown(f"🔍 Lower order volume during hours: {', '.join(map(str, offpeak_hours.index))}. Consider special offers or promotions during these times to boost sales.")

except FileNotFoundError:
    st.warning("Please upload peak_hours.csv for hourly analysis.")

st.markdown("---")

# --- Section 6: Top Pizzas ---
st.markdown("<h2 style='color:#D35400;'>6. Top Pizza Performance</h2>", unsafe_allow_html=True)
try:
    if "pizza_sales_summary.csv" in uploaded_files:
        df6 = pd.read_csv(uploaded_files["pizza_sales_summary.csv"])
    else:
        df6 = pd.read_csv("pizza_sales_summary.csv")

    df6[['total_quantity_sold','total_revenue']] = df6[['total_quantity_sold','total_revenue']].apply(pd.to_numeric)

    st.subheader("🍕 Units Sold by Pizza")
    st.bar_chart(df6.set_index('pizza_name')['total_quantity_sold'])

    st.subheader("💰 Revenue by Pizza")
    st.bar_chart(df6.set_index('pizza_name')['total_revenue'])

    best_selling = df6.loc[df6['total_quantity_sold'].idxmax(),'pizza_name']
    top_revenue = df6.loc[df6['total_revenue'].idxmax(),'pizza_name']

    st.markdown(f"🏆 Best selling pizza: **{best_selling}**, Highest revenue: **{top_revenue}**")

    # Added Insight
    best_selling_qty = df6['total_quantity_sold'].max()
    revenue_from_best = df6.loc[df6['pizza_name'] == best_selling, 'total_revenue'].values[0]
    st.markdown(f"💡 The best selling pizza sold **{best_selling_qty} units**, generating revenue of ₹{revenue_from_best:,.2f}. Consider upselling complementary items with this pizza.")

except FileNotFoundError:
    st.warning("Please upload pizza_sales_summary.csv for top pizzas.")

st.markdown("---")

# --- Section 7: Pizza Size Distribution ---
st.markdown("<h2 style='color:#D35400;'>7. Pizza Size Preferences</h2>", unsafe_allow_html=True)
try:
    if "pizza_size_distribution.csv" in uploaded_files:
        df7 = pd.read_csv(uploaded_files["pizza_size_distribution.csv"])
    else:
        df7 = pd.read_csv("pizza_size_distribution.csv")

    df7['quantity_by_size'] = df7['quantity_by_size'].astype(int)
    size_totals = df7.groupby('pizza_size')['quantity_by_size'].sum().sort_values(ascending=False)

    st.subheader("📏 Total Quantity by Size")
    st.bar_chart(size_totals)

    combo = df7.loc[df7['quantity_by_size'].idxmax()]
    st.markdown(f"🔥 Most popular combo: **{combo.pizza_name} ({combo.pizza_size})** with {combo.quantity_by_size} sold.")

except FileNotFoundError:
    st.warning("Please upload pizza_size_distribution.csv for size analysis.")

st.markdown("---")
# --- Section 8: Comprehensive Sales Insights ---
st.markdown("<h2 style='color:#2874A6;'>8. Comprehensive Sales Insights</h2>", unsafe_allow_html=True)

try:
    # Load data from uploaded file or local
    if "pizza_orders.csv" in uploaded_files:
        df8 = pd.read_csv(uploaded_files["pizza_orders.csv"])
    else:
        df8 = pd.read_csv("pizza_sales_data23.csv")

   

    # Convert data types
    df8['order_date'] = pd.to_datetime(df8['order_date'], errors='coerce')
    df8['quantity'] = pd.to_numeric(df8['quantity'], errors='coerce').fillna(0).astype(int)
    df8['price'] = pd.to_numeric(df8['price'], errors='coerce').fillna(0.0)
    df8['total_bill_amount'] = pd.to_numeric(df8['total_bill_amount'], errors='coerce').fillna(0.0)
    df8['discount'] = pd.to_numeric(df8['discount'], errors='coerce').fillna(0.0)

    # Basic summary
    total_orders = df8['order_id'].nunique()
    total_pizzas_sold = df8['quantity'].sum()
    total_revenue = (df8['quantity'] * df8['price']).sum()
    avg_order_value = df8.groupby('order_id').apply(lambda x: (x['quantity'] * x['price']).sum()).mean()

    st.subheader("📊 Overall Sales Summary")
    # st.markdown(f"- Total unique orders: **{total_orders}**")
    st.markdown(f"- Total pizzas sold: **{total_pizzas_sold}**")
    st.markdown(f"- Total revenue generated: **${total_revenue:,.2f}**")
    # st.markdown(f"- Average order value: **${avg_order_value:,.2f}**")

    # Revenue over time
    revenue_by_month = df8.groupby(pd.Grouper(key='order_date', freq='M')).apply(lambda x: (x['quantity'] * x['price']).sum())
    revenue_by_month = revenue_by_month.reset_index().rename(columns={0: 'monthly_revenue'})

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(revenue_by_month['order_date'], revenue_by_month['monthly_revenue'], marker='o', color='#2874A6')
    ax.set_title('Monthly Revenue Over Time')
    ax.set_xlabel('Month')
    ax.set_ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Most popular pizza by quantity
    pizza_quantity = df8.groupby('pizza_name')['quantity'].sum().sort_values(ascending=False)
    most_popular_pizza = pizza_quantity.idxmax()
    st.markdown(f"🍕 The most popular pizza is **{most_popular_pizza}**, with **{pizza_quantity.max()}** units sold.")

    # Most popular pizza size by quantity
    size_quantity = df8.groupby('pizza_size')['quantity'].sum().sort_values(ascending=False)
    most_popular_size = size_quantity.idxmax()
    st.markdown(f"📏 The most popular pizza size is **{most_popular_size}**, with **{size_quantity.max()}** pizzas sold.")

    # Sales during holidays vs non-holidays
    holiday_sales = df8[df8['is_holiday'] == 1].copy()
    non_holiday_sales = df8[df8['is_holiday'] == 0].copy()
    holiday_revenue = (holiday_sales['quantity'] * holiday_sales['price']).sum()
    non_holiday_revenue = (non_holiday_sales['quantity'] * non_holiday_sales['price']).sum()

    st.markdown(f"🎉 Revenue on holidays: **{holiday_revenue:,.2f}**")
    st.markdown(f"📅 Revenue on non-holidays: **{non_holiday_revenue:,.2f}**")

    # Discounts impact
    discounted_orders = df8[df8['discount'] > 0]
    discount_rate = (discounted_orders['quantity'] * discounted_orders['price']).sum() / total_revenue * 100 if total_revenue > 0 else 0
    st.markdown(f"🏷️ Percentage of revenue from discounted sales: **{discount_rate:.2f}%**")

except FileNotFoundError:
    st.warning("Please upload pizza_orders.csv for sales insights.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")

st.markdown("---")



