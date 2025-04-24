import streamlit as st
import pandas as pd
import os

# Install openai if not present
try:
    import openai
except ImportError:
    os.system("pip install openai")

from services.gpt_connector import ask_gpt

st.set_page_config(page_title="Gold vs SPY vs Sensex with AI", layout="wide")
st.title("📊 Gold vs S&P 500 vs BSE Sensex — with AI Analysis")

# Debug: list installed packages including openai
st.write("Installed packages:", [pkg.key for pkg in __import__('pkg_resources').working_set])

# Show available data files
st.sidebar.write("## Data Files")
st.sidebar.write(os.listdir("data"))

# Load merged data
df = pd.read_csv("data/merged_data_open_close.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)

# Plot time series
st.line_chart(df)

# AI Chat Interface
st.header("🤖 Ask AI about the data")
query = st.text_input("Enter your question here")
if st.button("Ask AI"):
    with st.spinner("Thinking..."):
        prompt = f"You are a financial data assistant. The dataframe has columns: {', '.join(df.columns)}. Using only the data, answer the following question: {query}"
        answer = ask_gpt(prompt)
        st.markdown(answer)
