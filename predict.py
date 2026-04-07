import pandas as pd
import streamlit as st
import joblib
import os

# --- Page Configuration & Styling ---
st.set_page_config(page_title="PizzaSalesIQ | Forecast", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    .main-header {text-align: center; color: #8E44AD; font-size: 3rem; font-weight: bold; margin-bottom: 0;}
    .sub-header {text-align: center; color: #7F8C8D; font-size: 1.2rem; margin-bottom: 2rem;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🔮 AI Inventory Forecast</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Next-Week Demand Predictions powered by Holt-Winters Exponential Smoothing</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Load Pre-trained Models ---
@st.cache_resource(show_spinner=False)
def load_models():
    """Loads the pre-trained dictionary of models from disk only once."""
    model_path = 'models/pizza_models.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

models_dict = load_models()

# --- Instant Forecasting ---
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

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Pizzas to Prep Next Week", value=f"{total_predicted:,}")
    col2.metric(label="Highest Demand Item", value=top_pizza_name)
    col3.metric(label="Peak Item Quantity", value=f"{top_pizza_qty:,}")

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