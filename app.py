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
    "Available analyses via `query_data`:\n"
    "• correlation\n"
    "• growth (percentage)\n"
    "• absolute_growth (absolute change)\n"
    "• best_day\n"
    "• head, tail\n\n"
    "When you get a question you CAN answer from the data, you *must* call `query_data`.\n"
    "If you CANNOT answer it from the data, you must reply exactly:\n"
    "`Sorry, I don't have the data to answer that question.`"
)

st.set_page_config(page_title="AI Data Chat — Fixed Rerun", layout="wide")
st.title("📊 Gold vs SPY vs Sensex — Robust Q&A with History")

@st.cache_data
def load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

# Load your merged dataset
df = load_df("data/merged_data_open_close.csv")

# Initialize history on first load
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "system", "content": SYSTEM_MESSAGE}
    ]

def query_data(operation, column_x=None, column_y=None, years=5, index=None, n=5):
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
    """Send the user query through GPT+function-calling, update history."""
    st.session_state.history.append({"role": "user", "content": user_query})

    # First-pass: let GPT try to call query_data
    messages = st.session_state.history.copy()
    resp = ask_gpt(messages)
    msg = resp.choices[0].message

    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)

        if "error" in result:
            assistant_reply = "Sorry, I don't have the data to answer that question."
        else:
            # Record the function call result
            st.session_state.history.append({
                "role": "function",
                "name": msg.function_call.name,
                "content": json.dumps(result)
            })
            # Ask GPT to produce a natural-language reply
            messages = st.session_state.history.copy()
            final_resp = ask_gpt(messages)
            assistant_reply = final_resp.choices[0].message.content

        st.session_state.history.append({"role": "assistant", "content": assistant_reply})

    else:
        # No function call → out-of-scope
        assistant_reply = "Sorry, I don't have the data to answer that question."
        st.session_state.history.append({"role": "assistant", "content": assistant_reply})

def render_history():
    """Safely render the full chat history without KeyErrors."""
    for entry in st.session_state.history:
        role = entry.get("role")
        if role == "user":
            st.markdown(f"**You:** {entry.get('content','')}")
        elif role == "assistant":
            st.markdown(f"**GPT:** {entry.get('content','')}")
        elif role == "function":
            func_name = entry.get("name", "query_data")
            content = entry.get("content", "")
            st.markdown(f"**Function `{func_name}` returned:** {content}")
        # skip system messages

# --- Streamlit UI ---
render_history()

query_input = st.text_input("Enter your question here", key="input")
if st.button("Ask AI"):
    process_user_query(query_input)
    # No explicit rerun; Streamlit will automatically rerun on state change

