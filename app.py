import os
import json
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt, list_models

st.set_page_config(page_title="AI Data Chat", layout="wide")
st.title("📊 Gold vs SPY vs Sensex — AI Q&A with Data Integration")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "merged_data_open_close.csv")
df = load_data(CSV_PATH)

st.sidebar.header("Data files")
st.sidebar.write(sorted(os.listdir(DATA_DIR)))

with st.sidebar.expander("🔧 Model settings"):
    try:
        models = list_models()
        st.write(models)
    except Exception as e:
        st.write("Error listing models:", e)
    st.write("Current model:", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    st.markdown("Set OPENAI_MODEL in Secrets to choose model.")

def query_data(operation, column_x=None, column_y=None, years=5, index=None, n=5):
    if operation == "correlation":
        corr = df[column_x].corr(df[column_y])
        return {"correlation": corr}
    elif operation == "growth":
        latest = df.index.max()
        start = latest - pd.DateOffset(years=years)
        sub = df.loc[df.index >= start]
        return {
            "spy_growth_pct": (sub["SPY_Close"].iloc[-1] / sub["SPY_Close"].iloc[0] - 1) * 100,
            "sensex_growth_pct": (sub["Sensex_Close"].iloc[-1] / sub["Sensex_Close"].iloc[0] - 1) * 100
        }
    elif operation == "best_day":
        pct = df[index].pct_change().dropna()
        return {"best_day": pct.groupby(pct.index.day_name()).mean().idxmax()}
    elif operation == "head":
        return {"data": df.head(n).reset_index().to_dict(orient="records")}
    elif operation == "tail":
        return {"data": df.tail(n).reset_index().to_dict(orient="records")}
    else:
        return {"error": f"Unknown operation {operation}"}

def process_query(query: str) -> str:
    messages = [
        {"role": "system", "content": "You are a financial data assistant. Use 'query_data' to fetch data."},
        {"role": "user", "content": query}
    ]
    resp = ask_gpt(messages)
    msg = resp.choices[0].message
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)
        messages.append(msg)
        messages.append({"role":"function","name":msg.function_call.name,"content":json.dumps(result)})
        final = ask_gpt(messages).choices[0].message.content
        return final
    return msg.content

st.header("🤖 Ask AI about the data")
user_query = st.text_input("Enter your question here")
if st.button("Ask AI"):
    answer = process_query(user_query)
    st.markdown(answer)
