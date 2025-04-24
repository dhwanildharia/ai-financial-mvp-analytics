import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gold vs SPY vs Sensex", layout="wide")
st.title("📊 Gold vs S&P 500 vs BSE Sensex")

# Load merged data
df = pd.read_csv("merged_data.csv", parse_dates=["Date"])
df = df.set_index("Date")

# Display line chart
st.line_chart(df)