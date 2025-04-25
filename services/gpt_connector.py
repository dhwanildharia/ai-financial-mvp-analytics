import os
from openai import OpenAI

# Initialize v1 client
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

def list_models() -> list[str]:
    """
    Return all model IDs your API key can access.
    """
    resp = _client.models.list()
    return [m.id for m in resp.data]

def ask_gpt(prompt: str) -> str:
    """
    Send a prompt to OpenAI and return the assistant's reply.
    Picks the model from OPENAI_MODEL (fallback to gpt-3.5-turbo).
    """
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    response = _client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )
    return response.choices[0].message.content
