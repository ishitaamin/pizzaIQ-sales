import pandas as pd
import streamlit as st
import os
import zipfile

@st.cache_data(show_spinner=False)
def load_csv(file_name, date_columns=None):
    """
    Loads a CSV file (or a CSV inside a ZIP) from the data directory.
    Handles __MACOSX metadata folders automatically.
    """
    file_path = os.path.join("data", file_name)
    
    if not os.path.exists(file_path):
        return None
        
    try:
        # Check if it's a zip file
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as z:
                # Filter out __MACOSX and non-csv files
                csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
                if not csv_files:
                    st.error(f"No CSV file found in {file_name}")
                    return None
                # Open the first valid CSV found
                with z.open(csv_files[0]) as f:
                    if date_columns:
                        return pd.read_csv(f, parse_dates=date_columns)
                    return pd.read_csv(f)
        
        # Standard CSV loading
        if date_columns:
            return pd.read_csv(file_path, parse_dates=date_columns)
        return pd.read_csv(file_path)
        
    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
        return None