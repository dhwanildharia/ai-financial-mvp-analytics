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

st.set_page_config(page_title="AI Data Chat — Fixed History", layout="wide")
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
    """
    Your function-calling implementation. Returns a dict or {'error': ...}.
    """
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
    # 1. Record the user message
    st.session_state.history.append({"role": "user", "content": user_query})

    # 2. First-pass: let GPT try to call query_data
    messages = st.session_state.history.copy()
    resp = ask_gpt(messages)
    msg = resp.choices[0].message

    # 3. If GPT did call the function:
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)

        # 3a. If the function returned an error key, reply with the sorry message
        if "error" in result:
            assistant_reply = "Sorry, I don't have the data to answer that question."
        else:
            # 3b. Record the function call result
            st.session_state.history.append({
                "role": "function",
                "name": msg.function_call.name,
                "content": json.dumps(result)
            })
            # 3c. Ask GPT to format a natural answer based on the function result
            messages = st.session_state.history.copy()
            final_resp = ask_gpt(messages)
            assistant_reply = final_resp.choices[0].message.content

        # 3d. Record the assistant's reply
        st.session_state.history.append({"role": "assistant", "content": assistant_reply})

    else:
        # 4. GPT did not call our function -> out-of-scope
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
            func_content = entry.get("content")
            if func_content is not None:
                st.markdown(f"**Function `{func_name}` returned:** {func_content}")
        # skip system messages

# --- Streamlit layout ---
render_history()
query = st.text_input("Enter your question here", key="input")
if st.button("Ask AI"):
    process_user_query(query)
    st.experimental_rerun()
