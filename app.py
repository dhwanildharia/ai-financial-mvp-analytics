import os
import json
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt, list_models

st.set_page_config(page_title="AI Data Chat", layout="wide")
st.title("📊 Gold vs SPY vs Sensex — AI Q&A with Memory")

# Load data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "merged_data_open_close.csv")
df = load_data(CSV_PATH)

# Initialize session messages
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role":"system","content":"You are a financial data assistant. Use 'query_data' to fetch data."}
    ]

# Sidebar
st.sidebar.header("Data files")
st.sidebar.write(sorted(os.listdir(DATA_DIR)))
with st.sidebar.expander("Model settings"):
    try:
        st.write(list_models())
    except Exception as e:
        st.write("Error listing models:", e)
    st.write("Current:", os.getenv("OPENAI_MODEL","gpt-3.5-turbo"))

# query_data implementation
def query_data(operation, column_x=None, column_y=None, years=5, index=None, n=5):
    if operation == "correlation":
        return {"correlation": df[column_x].corr(df[column_y])}
    elif operation == "growth":
        latest=df.index.max(); start=latest-pd.DateOffset(years=years)
        sub=df.loc[df.index>=start]
        return {"spy_growth_pct":(sub["SPY_Close"].iloc[-1]/sub["SPY_Close"].iloc[0]-1)*100,
                "sensex_growth_pct":(sub["Sensex_Close"].iloc[-1]/sub["Sensex_Close"].iloc[0]-1)*100}
    elif operation=="best_day":
        pct=df[index].pct_change().dropna()
        return {"best_day":pct.groupby(pct.index.day_name()).mean().idxmax()}
    elif operation=="head":
        return {"data":df.head(n).reset_index().to_dict("records")}
    elif operation=="tail":
        return {"data":df.tail(n).reset_index().to_dict("records")}
    else:
        return {"error":f"Unknown operation {operation}"}

# Process query
def process_query(query):
    st.session_state.messages.append({"role":"user","content":query})
    resp = ask_gpt(st.session_state.messages)
    msg = resp.choices[0].message
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)
        st.session_state.messages.append({"role":"function","name":msg.function_call.name,"content":json.dumps(result)})
        # Final assistant response
        final = ask_gpt(st.session_state.messages + [{"role":"function","name":msg.function_call.name,"content":json.dumps(result)}]).choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":final})
    else:
        st.session_state.messages.append({"role":"assistant","content":msg.content})

# Display history
for m in st.session_state.messages[1:]:
    if m["role"]=="user":
        st.markdown(f"**You:** {m['content']}")
    elif m["role"]=="assistant":
        st.markdown(f"**GPT:** {m['content']}")
    else:
        st.markdown(f"**Function {m['name']} returned:** {m['content']}")

# Input
query = st.text_input("Enter your question here", key="input")
if st.button("Ask AI"):
    process_query(query)
