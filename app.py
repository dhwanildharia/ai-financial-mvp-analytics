import os
import streamlit as st
import pandas as pd
from openai.error import RateLimitError
from services.gpt_connector import ask_gpt

st.set_page_config(page_title="Gold vs SPY vs Sensex with AI", layout="wide")
st.title("📊 Gold vs S&P 500 vs BSE Sensex — with AI Analysis")

# Ensure data folder exists
DATA_DIR = "data"
if not os.path.isdir(DATA_DIR):
    st.error(f"❌ Could not find `{DATA_DIR}` folder.")
    st.stop()

# List available data files
st.sidebar.header("Data files")
st.sidebar.write(os.listdir(DATA_DIR))

# Load merged dataset
csv_path = os.path.join(DATA_DIR, "merged_data_open_close.csv")
if not os.path.isfile(csv_path):
    st.error(f"❌ Missing merged data file: `{csv_path}`")
    st.stop()

df = pd.read_csv(csv_path, parse_dates=["Date"])
df.set_index("Date", inplace=True)
st.line_chart(df)

# AI Chat Interface
st.header("🤖 Ask AI about the data")
query = st.text_input("Enter your question here")
if st.button("Ask AI"):
    with st.spinner("Thinking..."):
        prompt = (
            f"You are a financial data assistant. The dataframe columns are: "
            f"{', '.join(df.columns)}. "
            f"Answer the following question based only on this data:\n\n{query}"
        )
        try:
            answer = ask_gpt(prompt)
            st.markdown(answer)
        except RateLimitError:
            st.error("⚠️ Rate limit exceeded. Please wait a moment and try again.")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
