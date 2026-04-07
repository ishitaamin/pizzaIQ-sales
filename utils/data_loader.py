import pandas as pd
import streamlit as st
import os

@st.cache_data(show_spinner=False)
def load_csv(file_name, date_columns=None):
    """
    Loads a CSV file from the data directory and caches the result.
    """
    file_path = os.path.join("data", file_name)
    
    if not os.path.exists(file_path):
        return None
        
    try:
        if date_columns:
            return pd.read_csv(file_path, parse_dates=date_columns)
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
        return None