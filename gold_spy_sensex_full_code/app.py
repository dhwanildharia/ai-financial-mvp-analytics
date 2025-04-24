import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gold vs SPY vs Sensex", layout="wide")
st.title("📊 Compare: Gold vs S&P 500 vs BSE Sensex")

# Load merged data
df = pd.read_csv('data/merged_data_open_close.csv', parse_dates=['Date'])
df.set_index('Date', inplace=True)

# Display line chart
st.line_chart(df)