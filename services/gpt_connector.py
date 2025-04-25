# services/gpt_connector.py
import os
from openai import OpenAI

# Initialize the new v1 client
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt: str) -> str:
    """
    Send a single-user message to GPT-4 and return the assistant's reply.
    """
    resp = _client.chat.completions.create(
        model="gpt-4",                # or your GPT-4 variant
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )
    return resp.choices[0].message.content
