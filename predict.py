import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import streamlit as st
import joblib


# --- Title ---
st.title("🍕 Weekly Pizza Sales Forecast")

# --- Upload CSV or Load Default ---
uploaded_file = st.file_uploader("Upload Pizza Sales CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=['order_date'])
else:
    df = pd.read_csv('pizza_sales_data23.csv', parse_dates=['order_date'])

# --- Preprocessing ---
df['week_start'] = df['order_date'] - pd.to_timedelta(df['order_date'].dt.weekday, unit='d')
weekly = (
    df.groupby(['week_start', 'pizza_name', 'pizza_size'])['quantity']
    .sum()
    .reset_index()
)
pivot = weekly.pivot_table(
    index='week_start',
    columns=['pizza_name', 'pizza_size'],
    values='quantity',
    fill_value=0
)

# --- Forecasting ---
forecasts = {}
with st.spinner("⏳ Generating next-week predictions..."):
    for (name, size), series in pivot.items():
        try:
            model = ExponentialSmoothing(series, trend='add', seasonal='add', seasonal_periods=52)
            fit = model.fit(optimized=True)
            pred = fit.forecast(1)
            forecasts[(name, size)] = int(round(pred.iloc[0]))
        except Exception as e:
            forecasts[(name, size)] = f"Error: {str(e)}"

# --- Display Forecasts ---
pred_df = pd.DataFrame([
    {'pizza_name': name, 'pizza_size': size, 'predicted_quantity': qty}
    for (name, size), qty in forecasts.items()
])
st.subheader("📈 Next Week's Predicted Sales")
st.dataframe(pred_df)

joblib.dump(model, 'pizza_quantity_model.pkl')
print("Model saved to 'pizza_quantity_model.pkl'")

# --- Optional: Download CSV ---
csv = pred_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Predictions as CSV",
    data=csv,
    file_name='next_week_pizza_predictions.csv',
    mime='text/csv'
)
