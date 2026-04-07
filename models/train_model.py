# models/train_model.py

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import joblib
import os

def train_and_save_models():
    print("Loading historical data...")
    # Assuming your data is in the data folder we created earlier
    df = pd.read_csv('../data/pizza_sales_data23.csv', parse_dates=['order_date'])

    print("Preprocessing data...")
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

    models_dict = {}
    print("Training models for each pizza variant. This might take a minute...")
    
    # Train a model for EVERY pizza/size combination
    for (name, size), series in pivot.items():
        try:
            model = ExponentialSmoothing(series, trend='add', seasonal='add', seasonal_periods=52)
            fit = model.fit(optimized=True)
            models_dict[(name, size)] = fit  # Save the fitted model to the dictionary
        except Exception as e:
            print(f"Could not train model for {name} ({size}): {e}")

    # Save the entire dictionary of models
    save_path = 'pizza_models.pkl'
    joblib.dump(models_dict, save_path)
    print(f"✅ Success! All models saved to models/{save_path}")

if __name__ == "__main__":
    train_and_save_models()