import os
import time
import openai
from openai.error import RateLimitError, APIError

# Load API key from environment / Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt: str, retries: int = 3, backoff: float = 1.0) -> str:
    """
    Send a prompt to GPT-4 with exponential back-off on rate limits.
    Returns the assistant's reply text.
    """
    for i in range(retries):
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4",              # or your GPT-4 variant
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.5,
            )
            return resp.choices[0].message.content
        except RateLimitError:
            if i < retries - 1:
                time.sleep(backoff * (2 ** i))
                continue
            else:
                raise
        except APIError as e:
            # Other transient API errors could also be retried here
            raise

