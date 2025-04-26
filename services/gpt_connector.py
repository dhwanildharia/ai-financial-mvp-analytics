import os
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

_FUNCTIONS = [
    {
        "name": "query_data",
        "description": "Perform a specific analysis on the loaded financial dataset.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Type of analysis to perform",
                    "enum": ["correlation", "growth", "best_day", "head", "tail"]
                },
                "column_x": {
                    "type": "string",
                    "description": "First column name (for correlation)"
                },
                "column_y": {
                    "type": "string",
                    "description": "Second column name (for correlation)"
                },
                "years": {
                    "type": "integer",
                    "description": "Number of years for growth calculation"
                },
                "index": {
                    "type": "string",
                    "description": "Column name (e.g. SPY_Close or Sensex_Close) for best_day"
                },
                "n": {
                    "type": "integer",
                    "description": "Number of rows for head/tail"
                }
            },
            "required": ["operation"]
        }
    }
]

def ask_gpt(messages: list[dict]) -> dict:
    return _client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=messages,
        functions=_FUNCTIONS,
        function_call="auto",
    )

def list_models() -> list[str]:
    resp = _client.models.list()
    return [m.id for m in resp.data]
