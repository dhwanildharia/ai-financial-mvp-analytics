import os
import json
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt

SYSTEM_MESSAGE = (
    "You are a financial data assistant with a dataset containing columns: "
    "Date, Gold_Price, SPY_Open, SPY_Close, Sensex_Open, Sensex_Close. "
    "Use the function 'query_data' to answer queries. "
    "If you don't have the data, respond: 'Sorry, I don't have the data to answer that question.'"
)

st.set_page_config(page_title="AI Data Chat Robust", layout="wide")
st.title("📊 Gold vs SPY vs Sensex — Robust Data-Driven Q&A with History")

@st.cache_data
def load_dataframe(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

df = load_dataframe("data/merged_data_open_close.csv")

# Initialize history
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_MESSAGE}
    ]

def query_data(operation, column_x=None, column_y=None, years=5, index=None, n=5):
    try:
        if operation == "correlation":
            return {"correlation": df[column_x].corr(df[column_y])}
        elif operation == "growth":
            latest = df.index.max()
            start = latest - pd.DateOffset(years=years)
            sub = df.loc[df.index >= start]
            return {
                "spy_growth_pct": (sub["SPY_Close"].iloc[-1] / sub["SPY_Close"].iloc[0] - 1) * 100,
                "sensex_growth_pct": (sub["Sensex_Close"].iloc[-1] / sub["Sensex_Close"].iloc[0] - 1) * 100
            }
        elif operation == "best_day":
            series = df[index].pct_change().dropna()
            best = series.groupby(series.index.day_name()).mean().idxmax()
            return {"best_day": best}
        elif operation == "head":
            return {"data": df.head(n).reset_index().to_dict(orient="records")}
        elif operation == "tail":
            return {"data": df.tail(n).reset_index().to_dict(orient="records")}
        else:
            return {"error": f"Unknown operation '{operation}'"}
    except Exception:
        return {"error": "Data error"}

def process_query(user_query):
    # Append user
    st.session_state.messages.append({"role": "user", "content": user_query})
    # Try function-calling
    response = ask_gpt(st.session_state.messages)
    msg = response.choices[0].message
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)
        if "error" in result:
            assistant_text = "Sorry, I don't have the data to answer that question."
        else:
            # append function call and result
            st.session_state.messages.append({"role":"assistant", "function_call":msg.function_call})
            st.session_state.messages.append({"role":"function","name":msg.function_call.name,"content":json.dumps(result)})
            # get final NL answer
            final_resp = ask_gpt(st.session_state.messages)
            assistant_text = final_resp.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":assistant_text})
    else:
        assistant_text = "Sorry, I don't have the data to answer that question."
        st.session_state.messages.append({"role":"assistant","content":assistant_text})

# Display history
for m in st.session_state.messages:
    role = m.get("role")
    if role == "user":
        st.markdown(f"**You:** {m['content']}")
    elif role == "assistant":
        st.markdown(f"**GPT:** {m['content']}")
    elif role == "function":
        st.markdown(f"**Function {m['name']} returned:** {m['content']}")

# Input
query = st.text_input("Enter your question here", key="input")
if st.button("Ask AI"):
    process_query(query)
