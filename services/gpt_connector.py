import os
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

def list_models() -> list[str]:
    resp = _client.models.list()
    return [m.id for m in resp.data]

def ask_gpt(prompt: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    resp = _client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )
    return resp.choices[0].message.content
