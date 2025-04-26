import os
import json
import streamlit as st
import pandas as pd
from services.gpt_connector import ask_gpt

SYSTEM_MESSAGE = (
    "You are a financial data assistant with a dataset containing columns: "
    "Date, Gold_Price, SPY_Open, SPY_Close, Sensex_Open, Sensex_Close. "
    "Available analyses: correlation, growth (%), absolute_growth (absolute change), best_day, head, tail. "
    "Use the function 'query_data' to answer from the dataset. "
    "If you don't have the data, respond: 'Sorry, I don't have the data to answer that question.'"
)

st.set_page_config(page_title="AI Data Chat Final", layout="wide")
st.title("📊 Gold vs SPY vs Sensex — Robust Data-Driven Q&A with History")

@st.cache_data
def load_df(path):
    df = pd.read_csv(path, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    return df

df = load_df("data/merged_data_open_close.csv")

if 'history' not in st.session_state:
    st.session_state.history = [{'role': 'system', 'content': SYSTEM_MESSAGE}]

def query_data(operation, column_x=None, column_y=None, years=5, index=None, n=5):
    try:
        if operation == 'correlation':
            return {'correlation': df[column_x].corr(df[column_y])}
        elif operation == 'growth':
            sub = df[df.index >= df.index.max() - pd.DateOffset(years=years)]
            return {
                'spy_growth_pct': (sub['SPY_Close'].iloc[-1]/sub['SPY_Close'].iloc[0]-1)*100,
                'sensex_growth_pct': (sub['Sensex_Close'].iloc[-1]/sub['Sensex_Close'].iloc[0]-1)*100
            }
        elif operation == 'absolute_growth':
            sub = df[df.index >= df.index.max() - pd.DateOffset(years=years)]
            return {
                'spy_absolute': sub['SPY_Close'].iloc[-1] - sub['SPY_Close'].iloc[0],
                'sensex_absolute': sub['Sensex_Close'].iloc[-1] - sub['Sensex_Close'].iloc[0]
            }
        elif operation == 'best_day':
            pct = df[index].pct_change().dropna()
            return {'best_day': pct.groupby(pct.index.day_name()).mean().idxmax()}
        elif operation == 'head':
            return {'data': df.head(n).reset_index().to_dict('records')}
        elif operation == 'tail':
            return {'data': df.tail(n).reset_index().to_dict('records')}
        else:
            return {'error': 'Unknown operation'}
    except Exception:
        return {'error': 'Data error'}

def process(query):
    st.session_state.history.append({'role': 'user', 'content': query})
    messages = st.session_state.history.copy()
    resp = ask_gpt(messages)
    msg = resp.choices[0].message
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        result = query_data(**args)
        if 'error' in result:
            reply = "Sorry, I don't have the data to answer that question."
        else:
            st.session_state.history.append({'role': 'function', 'name': msg.function_call.name, 'content': json.dumps(result)})
            messages = st.session_state.history.copy()
            final = ask_gpt(messages).choices[0].message.content
            reply = final
        st.session_state.history.append({'role': 'assistant', 'content': reply})
    else:
        reply = "Sorry, I don't have the data to answer that question."
        st.session_state.history.append({'role': 'assistant', 'content': reply})

def render_history():
    for m in st.session_state.history:
        role = m.get('role')
        if role == 'user':
            st.markdown(f"**You:** {m['content']}")
        elif role == 'assistant':
            st.markdown(f"**GPT:** {m['content']}")
        elif role == 'function':
            func_name = m.get('name', 'query_data')
            st.markdown(f"**Function {func_name} returned:** {m['content']}")
        # ignore 'system' or other roles

render_history()
st.text_input("Enter your question here", key='input')
if st.button("Ask AI"):
    process(st.session_state.input)
    st.experimental_rerun()
