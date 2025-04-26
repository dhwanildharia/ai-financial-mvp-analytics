import os
import json
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt

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

st.sidebar.header("Data file")
st.sidebar.write(os.listdir(DATA_DIR))

# Function to execute calls
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

st.header("🤖 Ask AI about the data")
query = st.text_input("Your question")
if st.button("Ask AI"):
    messages = [
        {"role":"system","content":"You have access to the dataset via 'query_data' function."},
        {"role":"user","content":query}
    ]
    response = ask_gpt(messages)
    msg = response.choices[0].message
    if msg.get("function_call"):
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)
        messages.append(msg)
        messages.append({"role":"function","name":msg.function_call.name,"content":json.dumps(result)})
        final = ask_gpt(messages).choices[0].message.content
        st.markdown(final)
    else:
        st.markdown(msg.content)

