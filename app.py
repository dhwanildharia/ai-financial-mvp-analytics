# app.py
import os
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt

st.set_page_config(page_title="Gold vs SPY vs Sensex with AI", layout="wide")
st.title("📊 Gold vs S&P 500 vs BSE Sensex — with AI Analysis")

DATA_DIR = "data"
csv_path = os.path.join(DATA_DIR, "merged_data_open_close.csv")

# Sanity checks
if not os.path.isdir(DATA_DIR):
    st.error(f"❌ Could not find `{DATA_DIR}` folder.")
    st.stop()
if not os.path.isfile(csv_path):
    st.error(f"❌ Missing data file: `{csv_path}`")
    st.stop()

# Show files
st.sidebar.header("Data files")
st.sidebar.write(sorted(os.listdir(DATA_DIR)))

# Load & plot
df = pd.read_csv(csv_path, parse_dates=["Date"])
df.set_index("Date", inplace=True)
st.line_chart(df)

# AI Chat
st.header("🤖 Ask AI about the data")
query = st.text_input("Enter your question here")
if st.button("Ask AI"):
    with st.spinner("Thinking..."):
        prompt = (
            f"You are a financial data assistant. The dataframe has columns: "
            f"{', '.join(df.columns)}.\n"
            f"Using only this data, answer: {query}"
        )
        try:
            answer = ask_gpt(prompt)
            st.markdown(answer)
        except Exception as e:
            st.error(f"❌ API request failed: {e}")

