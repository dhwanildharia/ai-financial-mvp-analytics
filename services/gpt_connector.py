import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt: str) -> str:
    # For older/newer SDKs, this endpoint is more stable
    resp = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=500,
        temperature=0.5,
    )
    return resp.choices[0].text.strip()
