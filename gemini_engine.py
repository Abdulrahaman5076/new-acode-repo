import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config
from utils import cache


class GeminiEngine:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")

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

        prompt = (
            "You are a senior software architect mentoring a junior developer.\n\n"
            "The developer inherited an AI-generated codebase and needs to understand it.\n\n"
            f"Parsed Summary:\n{parsed_summary}\n\n"
            "Source Code:\n\n"
            f"{code[:15000]}\n\n"
            "Explain:\n"
            "1. Purpose\n"
            "2. Architecture\n"
            "3. Main functions\n"
            "4. Main classes\n"
            "5. Data flow\n"
            "6. Entry points\n"
            "7. Security concerns\n"
            "8. Suggested improvements\n"
        )

        explanation = self._call_api(prompt)

        cache.set(cache_key, explanation)

        return explanation