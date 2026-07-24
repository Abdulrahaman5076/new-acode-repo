"""
Code Whisperer - Gemini AI Engine
Handles all communication with Google's Gemini API.
Includes retry logic, caching, and graceful degradation.
"""

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config
from utils import cache

# ---------------------------------------------------------------------------
# Gemini Client
# ---------------------------------------------------------------------------
class GeminiEngine:
    """
    Wrapper around Google Gemini API with:
    - Automatic retries on failure
    - Response caching to save API calls
    - Graceful error handling
    """
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for GeminiEngine")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": config.GEMINI_TEMPERATURE,
                "max_output_tokens": config.GEMINI_MAX_TOKENS,
            }
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _call_api(self, prompt: str) -> str:
        """Internal method. Calls Gemini API with retry logic."""
        response = self.model.generate_content(prompt)
        return response.text
    
    def explain_code(self, code: str, parsed_summary: str) -> str:
        """
        Generates a comprehensive, plain-English explanation of the codebase.
        Uses caching to avoid redundant API calls for identical code.
        """
        # Check cache first
        cache_key = cache.make_key(code)
        cached_response = cache.get(cache_key)
        if cached_response:
            return f"{cached_response}\n\n*(Result retrieved from cache)*"
        
        # Build the prompt
        prompt = f"""You are a senior software architect mentoring a junior developer.

The developer has inherited an AI-generated codebase and needs to understand it completely.

PARSED STRUCTURE:
- Functions: {parsed_summary.split('Functions:')[-1].split('Classes:')[0].strip() if 'Functions:' in parsed_summary else 'N/A'}
- Classes: {parsed_summary.split('Classes:')[-1].split('Call Graph:')[0].strip() if 'Classes:' in parsed_summary else 'N/A'}
- Entry Points: {parsed_summary.split('Entry Points:')[-1].split('Orphans:')[0].strip() if 'Entry Points:' in parsed_summary else 'N/A'}

FULL SOURCE CODE:
```python
{code[:15000]}