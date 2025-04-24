import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt: str) -> str:
    """Send a prompt to OpenAI GPT and return the answer."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        n=1,
        temperature=0.5,
    )
    return response.choices[0].message.content