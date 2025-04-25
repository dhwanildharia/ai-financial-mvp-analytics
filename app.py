import os
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt, list_models
from openai.error import OpenAIError

st.set_page_config(page_title="Gold vs SPY vs Sensex with AI", layout="wide")
st.title("📊 Gold vs S&P 500 vs BSE Sensex — with AI Analysis")

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "merged_data_open_close.csv")

# Sanity checks
if not os.path.isdir(DATA_DIR):
    st.error(f"❌ Could not find `{DATA_DIR}` folder.")
    st.stop()
if not os.path.isfile(CSV_PATH):
    st.error(f"❌ Missing data file: `{CSV_PATH}`")
    st.stop()

# Sidebar: list data files & models
st.sidebar.header("Data files")
st.sidebar.write(sorted(os.listdir(DATA_DIR)))

with st.sidebar.expander("🔧 Model configuration"):
    st.write("**Available models:**")
    try:
        models = list_models()
        st.write(models)
    except Exception as e:
        st.write("Error listing models:", e)
    st.write("**Current model:**", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    st.markdown(
        "Set `OPENAI_MODEL` in Streamlit **Secrets** to your desired model ID."
    )

# Load & plot data
df = pd.read_csv(CSV_PATH, parse_dates=["Date"])
df.set_index("Date", inplace=True)
st.line_chart(df)

# AI Chat interface
st.header("🤖 Ask AI about the data")
query = st.text_input("Enter your question here")
if st.button("Ask AI"):
    with st.spinner("Thinking..."):
        prompt = (
            f"You are a financial data assistant. The dataframe has columns: "
            f"{', '.join(df.columns)}. Using only this data, answer:\n\n{query}"
        )
        try:
            answer = ask_gpt(prompt)
            st.markdown(answer)
        except OpenAIError as e:
            st.error(f"❌ OpenAI API error: {e}")

