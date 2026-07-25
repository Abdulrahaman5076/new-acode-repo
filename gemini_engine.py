"""
Code Whisperer - Gemini AI Engine
Handles communication with Google's Gemini API.
"""

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config
from utils import cache


class GeminiEngine:
    """Gemini API wrapper."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required.")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": config.GEMINI_TEMPERATURE,
                "max_output_tokens": config.GEMINI_MAX_TOKENS,
            },
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _call_api(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def explain_code(self, code: str, parsed_summary: str) -> str:
        cache_key = cache.make_key(code)

        cached = cache.get(cache_key)
        if cached:
            return cached + "\n\n*(Retrieved from cache)*"

        prompt = f"""
You are a senior software architect.

Explain the following codebase in simple English.

Parsed Summary:
{parsed_summary}

Source Code:

```python
{code[:15000]}