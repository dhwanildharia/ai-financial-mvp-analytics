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
                "column_x": {"type": "string", "description": "First column name (for correlation)"},
                "column_y": {"type": "string", "description": "Second column name (for correlation)"},
                "years": {"type": "integer", "description": "Number of years for growth calculation"},
                "index": {"type": "string", "description": "Column name for best_day"},
                "n": {"type": "integer", "description": "Number of rows for head/tail"}
            },
            "required": ["operation"]
        }
    }
]
