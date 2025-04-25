import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )
    return resp.choices[0].message.content
