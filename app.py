import streamlit as st
import pandas as pd
import os
from services.gpt_connector import ask_gpt

st.set_page_config(page_title="Gold vs SPY vs Sensex with AI", layout="wide")
st.title("📊 Gold vs S&P 500 vs BSE Sensex — with AI Analysis")

# Debug: list data files
st.sidebar.write("Data files:", os.listdir("data"))

# Load merged dataset
df = pd.read_csv("data/merged_data_open_close.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)
st.line_chart(df)

# AI Chat Interface
st.header("🤖 Ask AI about the data")
query = st.text_input("Enter your question here")
if st.button("Ask AI"):
    with st.spinner("Thinking..."):
        prompt = (
            f"You are a financial data assistant. The dataframe columns are {', '.join(df.columns)}. "
            f"Answer using only this data: {query}"
        )
        answer = ask_gpt(prompt)
        st.markdown(answer)
