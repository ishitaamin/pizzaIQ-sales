import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import joblib
import os

# Import our custom cached data loader
from utils.data_loader import load_csv

# --- Page Configuration ---
st.set_page_config(page_title="PizzaSalesIQ Dashboard", page_icon="🍕", layout="wide")

# --- Custom CSS for Polish ---
st.markdown("""
    <style>
    .main-header {text-align: center; color: #E74C3C; font-size: 3rem; font-weight: bold; margin-bottom: 0;}
    .sub-header {text-align: center; color: #7F8C8D; font-size: 1.2rem; margin-bottom: 2rem;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🍕 PizzaSalesIQ</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Interactive Business Intelligence & AI Forecasting</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Load All Data Upfront ---
# The @st.cache_data in data_loader makes this instant after the first load
df_last_week = load_csv("1.csv", date_columns=["order_date"])
df_monthly = load_csv("month_sales.csv")
df_avg = load_csv("avg.csv")
df_discount = load_csv("discount.csv")
df_peak = load_csv("updated_orders.csv")
df_summary = load_csv("pizza_sales_summary.csv")
df_size = load_csv("pizza_size_distribution.csv")
df_overall = load_csv("pizza_sales_data23.zip") # Assuming you kept the .zip!

# --- Load Pre-trained ML Models ---
@st.cache_resource(show_spinner=False)
def load_models():
    """Loads the pre-trained dictionary of models from disk only once."""
    model_path = 'models/pizza_models.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

models_dict = load_models()

# --- Tabbed Navigation Layout ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary", 
    "📈 Trends & Seasonality", 
    "🍕 Pizza Analytics", 
    "👥 Customer Behavior",
    "🔮 AI Inventory Forecast"
])

# ==========================================
# TAB 1: EXECUTIVE SUMMARY (Overall & Last Week)
# ==========================================
with tab1:
    if df_overall is not None:
        try:
            # Clean and convert data
            df_overall['order_date'] = pd.to_datetime(df_overall['order_date'], errors='coerce')
            df_overall['quantity'] = pd.to_numeric(df_overall['quantity'], errors='coerce').fillna(0).astype(int)
            df_overall['price'] = pd.to_numeric(df_overall['price'], errors='coerce').fillna(0.0)
            df_overall['discount'] = pd.to_numeric(df_overall['discount'], errors='coerce').fillna(0.0)

            total_pizzas_sold = df_overall['quantity'].sum()
            total_revenue = (df_overall['quantity'] * df_overall['price']).sum()
            
            # Top-level metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Total Revenue (All Time)", value=f"₹{total_revenue:,.2f}")
            col2.metric(label="Total Pizzas Sold", value=f"{total_pizzas_sold:,}")
            
            # Holidays vs Non-Holidays
            holiday_sales = df_overall[df_overall['is_holiday'] == 1]
            holiday_revenue = (holiday_sales['quantity'] * holiday_sales['price']).sum()
            col3.metric(label="Holiday Revenue", value=f"₹{holiday_revenue:,.2f}")
            
            discounted_orders = df_overall[df_overall['discount'] > 0]
            discount_rate = (discounted_orders['quantity'] * discounted_orders['price']).sum() / total_revenue * 100 if total_revenue > 0 else 0
            col4.metric(label="Discounted Sales %", value=f"{discount_rate:.1f}%")

            st.markdown("<br>", unsafe_allow_html=True)

            # Revenue over time chart
            st.subheader("Monthly Revenue Growth")
            revenue_by_month = df_overall.groupby(pd.Grouper(key='order_date', freq='ME')).apply(lambda x: (x['quantity'] * x['price']).sum())
            revenue_by_month = revenue_by_month.reset_index().rename(columns={0: 'monthly_revenue'})
            
            st.line_chart(revenue_by_month.set_index('order_date')['monthly_revenue'])

        except Exception as e:
            st.error(f"Error processing overall insights: {e}")
    else:
        st.warning("Missing 'pizza_sales_data23' dataset.")

    st.markdown("---")
    
    # Last Week Pulse
    if df_last_week is not None:
        st.subheader("Last Week's Pulse")
        total_orders_lw = df_last_week.shape[0]
        total_pizzas_lw = df_last_week["total_quantity"].sum()
        total_revenue_lw = df_last_week["bill_amount"].sum()

        lw_col1, lw_col2, lw_col3 = st.columns(3)
        lw_col1.metric("Orders (Last 7 Days)", total_orders_lw)
        lw_col2.metric("Pizzas Sold", total_pizzas_lw)
        lw_col3.metric("Revenue", f"₹{total_revenue_lw:,.2f}")
        
        avg_pizzas_per_order = total_pizzas_lw / total_orders_lw if total_orders_lw else 0
        st.info(f"💡 **Operational Insight:** Customers ordered an average of **{avg_pizzas_per_order:.2f} pizzas per order** last week. Use this baseline for box inventory forecasting.")
    else:
        st.warning("Missing '1.csv' for last week's data.")


# ==========================================
# TAB 2: TRENDS & SEASONALITY
# ==========================================
with tab2:
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t1:
        st.subheader("📅 Monthly Sales Trajectory")
        if df_monthly is not None:
            df_monthly['year_month'] = pd.to_datetime(df_monthly['year_month'], format='%Y-%m')
            df_monthly['month'] = df_monthly['year_month'].dt.month
            df_monthly['year'] = df_monthly['year_month'].dt.year
            pivot = df_monthly.pivot(index='month', columns='year', values='total_pizzas_sold')
            st.line_chart(pivot)
            
            df_monthly['quarter'] = df_monthly['year_month'].dt.to_period('Q')
            seasonal = df_monthly.groupby('quarter')['total_pizzas_sold'].sum()
            st.bar_chart(seasonal)
        else:
            st.warning("Missing 'month_sales.csv'.")

    with col_t2:
        st.subheader("Day-Type Averages")
        if df_avg is not None:
            df_avg[['avg_orders_per_day','avg_pizzas_per_day','avg_revenue_per_day']] = df_avg[['avg_orders_per_day','avg_pizzas_per_day','avg_revenue_per_day']].apply(pd.to_numeric)
            st.dataframe(df_avg.set_index('day_type'), use_container_width=True)
            
            weekend_avg = df_avg.loc[df_avg['day_type'].isin(['Saturday', 'Sunday']), 'avg_revenue_per_day'].mean()
            weekday_avg = df_avg.loc[~df_avg['day_type'].isin(['Saturday', 'Sunday']), 'avg_revenue_per_day'].mean()
            
            st.success(f"📈 **Revenue Insight:** Weekends generate **₹{weekend_avg:.2f}** on average versus **₹{weekday_avg:.2f}** on weekdays. Ensure staff scaling aligns with this surge.")
        else:
            st.warning("Missing 'avg.csv'.")


# ==========================================
# TAB 3: PIZZA ANALYTICS
# ==========================================
with tab3:
    st.subheader("Top Performing Pizzas")
    if df_summary is not None:
        df_summary[['total_quantity_sold','total_revenue']] = df_summary[['total_quantity_sold','total_revenue']].apply(pd.to_numeric)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write("**Units Sold by Pizza**")
            st.bar_chart(df_summary.set_index('pizza_name')['total_quantity_sold'], color="#E74C3C")
        with col_p2:
            st.write("**Total Revenue by Pizza**")
            st.bar_chart(df_summary.set_index('pizza_name')['total_revenue'], color="#2ECC71")

        best_selling = df_summary.loc[df_summary['total_quantity_sold'].idxmax(),'pizza_name']
        top_revenue = df_summary.loc[df_summary['total_revenue'].idxmax(),'pizza_name']
        st.info(f"🏆 **Menu Strategy:** **{best_selling}** drives volume, while **{top_revenue}** drives top-line revenue. Consider bundling them together.")
    else:
        st.warning("Missing 'pizza_sales_summary.csv'.")

    st.markdown("---")
    
    st.subheader("Size Distribution")
    if df_size is not None:
        df_size['quantity_by_size'] = df_size['quantity_by_size'].astype(int)
        size_totals = df_size.groupby('pizza_size')['quantity_by_size'].sum().sort_values(ascending=False)
        st.bar_chart(size_totals, color="#3498DB")
    else:
        st.warning("Missing 'pizza_size_distribution.csv'.")


# ==========================================
# TAB 4: CUSTOMER BEHAVIOR
# ==========================================
with tab4:
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("⏰ Peak Order Hours")
        if df_peak is not None:
            df_peak['order_hour'] = pd.to_numeric(df_peak['order_hour'], errors='coerce')
            df_peak = df_peak.dropna(subset=['order_hour'])
            df_peak['order_hour'] = df_peak['order_hour'].astype(int)

            avg_by_hour = df_peak.groupby('order_hour')['number_of_orders'].mean()
            st.area_chart(avg_by_hour, color="#9B59B6")
            
            peak = avg_by_hour.idxmax()
            st.info(f"⏱️ **Peak Hour:** {peak}:00 handles the highest average volume. Optimize kitchen prep 30 mins prior.")
        else:
            st.warning("Missing 'updated_orders.csv'.")

    with col_c2:
        st.subheader("🎟️ Discount Campaign ROI")
        if df_discount is not None:
            df_discount['usage_count'] = df_discount['usage_count'].astype(int)
            df_discount = df_discount[df_discount['discount_type'] != 'none']
            st.bar_chart(df_discount.set_index('discount_type')['usage_count'], color="#F1C40F")
            
            top_discount = df_discount.loc[df_discount['usage_count'].idxmax(),'discount_type']
            st.success(f"🎯 **Marketing Insight:** The **{top_discount}** discount drives the most conversions. Emphasize this mechanic in future ad spend.")
        else:
            st.warning("Missing 'discount.csv'.")

# ==========================================
# TAB 5: AI INVENTORY FORECAST
# ==========================================
with tab5:
    st.markdown("<h2 style='color:#8E44AD;'>Next-Week Demand Predictions</h2>", unsafe_allow_html=True)
    st.write("Instantly generating next week's inventory requirements using pre-trained Holt-Winters Exponential Smoothing models.")

    if models_dict is None:
        st.error("⚠️ Pre-trained models not found! Please run 'models/train_model.py' first to generate the models.")
    else:
        forecasts = {}
        with st.spinner("⏳ Running AI inference engine..."):
            for (name, size), fit_model in models_dict.items():
                try:
                    pred = fit_model.forecast(1)
                    forecasts[(name, size)] = int(round(pred.iloc[0]))
                except Exception as e:
                    forecasts[(name, size)] = "Error"

        # Convert to DataFrame
        pred_df = pd.DataFrame([
            {'Pizza Name': name, 'Size': size, 'Predicted Quantity': qty}
            for (name, size), qty in forecasts.items()
        ])
        
        # Clean data (handle any potential 'Error' strings from failed models)
        pred_df['Predicted Quantity'] = pd.to_numeric(pred_df['Predicted Quantity'], errors='coerce').fillna(0).astype(int)

        # --- Top Level Metrics ---
        total_predicted = pred_df['Predicted Quantity'].sum()
        top_pizza_row = pred_df.loc[pred_df['Predicted Quantity'].idxmax()]
        top_pizza_name = f"{top_pizza_row['Pizza Name']} ({top_pizza_row['Size']})"
        top_pizza_qty = top_pizza_row['Predicted Quantity']

        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.metric(label="Total Pizzas to Prep Next Week", value=f"{total_predicted:,}")
        col_f2.metric(label="Highest Demand Item", value=top_pizza_name)
        col_f3.metric(label="Peak Item Quantity", value=f"{top_pizza_qty:,}")

        st.markdown("---")

        # --- Detailed Visualizations ---
        col_table, col_chart = st.columns([1.2, 1])

        with col_table:
            st.subheader("📋 Detailed Action Plan")
            st.write("Review the specific inventory requirements per item.")
            
            # Advanced Streamlit Dataframe with embedded progress bars
            st.dataframe(
                pred_df.sort_values('Predicted Quantity', ascending=False),
                column_config={
                    "Predicted Quantity": st.column_config.ProgressColumn(
                        "Predicted Quantity",
                        help="Volume of pizzas predicted for next week",
                        format="%d",
                        min_value=0,
                        max_value=int(pred_df['Predicted Quantity'].max()),
                    ),
                },
                hide_index=True,
                use_container_width=True,
                height=400
            )

        with col_chart:
            st.subheader("📈 Top 10 Items to Stock")
            st.write("Focus supply chain efforts on these high-velocity items.")
            
            top_10 = pred_df.sort_values('Predicted Quantity', ascending=False).head(10)
            # Create a combined label for the chart
            top_10['Item'] = top_10['Pizza Name'] + " (" + top_10['Size'] + ")"
            
            st.bar_chart(top_10.set_index('Item')['Predicted Quantity'], color="#8E44AD")

        # --- Download Section ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Export Data:** Download these predictions to integrate with your existing Kitchen Display System (KDS) or inventory management software.")
        
        csv = pred_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Predictions as CSV",
            data=csv,
            file_name='next_week_pizza_predictions.csv',
            mime='text/csv'
        )