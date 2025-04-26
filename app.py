import os
import json
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt

SYSTEM_MESSAGE = (
    "You are a financial data assistant with a dataset containing columns:\n"
    "- Date\n"
    "- Gold_Price\n"
    "- SPY_Open, SPY_Close\n"
    "- Sensex_Open, Sensex_Close\n\n"
    "You have one function available:\n"
    "  • query_data(operation, column_x, column_y, years, index, n)\n\n"
    "When a user asks something you *can* answer from the dataset, you *must* call `query_data`.\n"
    "If the user asks anything else (e.g. chit-chat, greetings, general knowledge), answer normally.\n"
    "Never reply “I don’t have the data” for general questions—only for data-related queries that truly fall outside your CSV."
)

st.set_page_config(page_title="AI Data Chat — Flexible", layout="wide")
st.title("📊 Gold vs SPY vs Sensex — Data-First Q&A with Fallback")

@st.cache_data
def load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

df = load_df("data/merged_data_open_close.csv")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "system", "content": SYSTEM_MESSAGE}
    ]

def query_data(operation, column_x=None, column_y=None, years=5, index=None, n=5):
    """Your existing data‐query logic."""
    try:
        if operation == "correlation":
            return {"correlation": df[column_x].corr(df[column_y])}

        elif operation == "growth":
            window = df[df.index >= df.index.max() - pd.DateOffset(years=years)]
            return {
                "spy_growth_pct": (window["SPY_Close"].iloc[-1] / window["SPY_Close"].iloc[0] - 1) * 100,
                "sensex_growth_pct": (window["Sensex_Close"].iloc[-1] / window["Sensex_Close"].iloc[0] - 1) * 100
            }

        elif operation == "absolute_growth":
            window = df[df.index >= df.index.max() - pd.DateOffset(years=years)]
            return {
                "spy_absolute": window["SPY_Close"].iloc[-1] - window["SPY_Close"].iloc[0],
                "sensex_absolute": window["Sensex_Close"].iloc[-1] - window["Sensex_Close"].iloc[0]
            }

        elif operation == "best_day":
            series = df[index].pct_change().dropna()
            best = series.groupby(series.index.day_name()).mean().idxmax()
            return {"best_day": best}

        elif operation == "head":
            return {"data": df.head(n).reset_index().to_dict("records")}

        elif operation == "tail":
            return {"data": df.tail(n).reset_index().to_dict("records")}

        else:
            return {"error": f"Unknown operation '{operation}'"}
    except Exception:
        return {"error": "Data error"}

def process_user_query(user_query: str):
    """Runs GPT with function‐calling, or falls back to normal GPT text answer."""
    # 1) record user message
    st.session_state.history.append({"role": "user", "content": user_query})

    # 2) let GPT choose to call function or not
    messages = st.session_state.history.copy()
    resp = ask_gpt(messages)
    msg = resp.choices[0].message

    # 3) if GPT requested our function, do data path
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)

        # if function returned an error, tell the user
        if "error" in result:
            assistant_text = "Sorry, I don't have the data to answer that question."
        else:
            # record the function result
            st.session_state.history.append({
                "role": "function",
                "name": msg.function_call.name,
                "content": json.dumps(result)
            })
            # ask GPT to format a natural reply using those results
            followup = ask_gpt(st.session_state.history.copy())
            assistant_text = followup.choices[0].message.content or "❓"

        # record GPT’s reply
        st.session_state.history.append({"role": "assistant", "content": assistant_text})

    else:
        # 4) No function_call → general question: use msg.content
        assistant_text = msg.content or "❓"
        st.session_state.history.append({"role": "assistant", "content": assistant_text})

def render_history():
    """Safely render user, assistant, and function messages."""
    for entry in st.session_state.history:
        role = entry.get("role")
        if role == "user":
            st.markdown(f"**You:** {entry.get('content','')}")
        elif role == "assistant":
            st.markdown(f"**GPT:** {entry.get('content','')}")
        elif role == "function":
            fn = entry.get("name", "query_data")
            st.markdown(f"**Function `{fn}` returned:** {entry.get('content','')}")
        # skip system messages

# ---- Streamlit UI ----
render_history()

# input area
query = st.text_input("Enter your question here", key="input")
if st.button("Ask AI"):
    process_user_query(query)
    # Streamlit auto-reruns on state change; no explicit rerun needed
