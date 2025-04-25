import os
from openai import OpenAI

# Initialize v1 client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt: str) -> str:
    """Send prompt to gpt-3.5-turbo and return the assistant's reply."""
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",            # switch to a model you definitely have access to
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )
    return resp.choices[0].message.content
