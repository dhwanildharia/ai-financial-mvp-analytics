import os
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

_FUNCTIONS = [{"name": "query_data", "description": "Perform analysis on the financial dataset.", "parameters": {"type": "object", "properties": {"operation": {"type": "string", "description": "Analysis type", "enum": ["correlation", "growth", "best_day", "head", "tail"]}, "column_x": {"type": "string", "description": "First column for correlation", "enum": ["Date", "Gold_Price", "SPY_Open", "SPY_Close", "Sensex_Open", "Sensex_Close"]}, "column_y": {"type": "string", "description": "Second column for correlation", "enum": ["Date", "Gold_Price", "SPY_Open", "SPY_Close", "Sensex_Open", "Sensex_Close"]}, "years": {"type": "integer", "description": "Years for growth calculation"}, "index": {"type": "string", "description": "Column for best_day analysis", "enum": ["Date", "Gold_Price", "SPY_Open", "SPY_Close", "Sensex_Open", "Sensex_Close"]}, "n": {"type": "integer", "description": "Number of rows for head/tail"}}, "required": ["operation"]}}]

def ask_gpt(messages):
    return _client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=messages,
        functions=_FUNCTIONS,
        function_call="auto"
    )

def list_models():
    resp = _client.models.list()
    return [m.id for m in resp.data]
