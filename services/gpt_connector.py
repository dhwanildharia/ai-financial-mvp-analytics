import os
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

_FUNCTIONS = [
    {
        "name": "query_data",
        "description": "Perform analysis on the financial dataset.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["correlation", "growth", "best_day", "head", "tail"]},
                "column_x": {"type": "string"},
                "column_y": {"type": "string"},
                "years": {"type": "integer"},
                "index": {"type": "string"},
                "n": {"type": "integer"}
            },
            "required": ["operation"]
        }
    }
]

def ask_gpt_with_functions(messages):
    return _client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=messages,
        functions=_FUNCTIONS,
        function_call="auto",
    )

ask_gpt = ask_gpt_with_functions
