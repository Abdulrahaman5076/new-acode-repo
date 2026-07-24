"""
Code Whisperer - Central Configuration
Single source of truth for every setting in the application.
When something needs changing, you change it here and nowhere else.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ---- Application ----
    APP_NAME = "Code Whisperer"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Paste AI-generated code. Understand it instantly."
    
    # ---- Gemini AI ----
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-1.5-pro"
    GEMINI_TEMPERATURE = 0.2
    GEMINI_MAX_TOKENS = 4096
    
    # ---- Code Limits ----
    MAX_CODE_CHARS = 20000
    MAX_CODE_LINES = 10000
    
    # ---- Rate Limiting ----
    RATE_LIMIT_REQUESTS = 30
    RATE_LIMIT_WINDOW_SECONDS = 60
    
    # ---- Cache ----
    CACHE_ENABLED = True
    CACHE_SIZE = 200
    CACHE_TTL_SECONDS = 1800  # 30 minutes
    
    # ---- Security ----
    BLOCKED_PATTERNS = [
        "os.system(", "subprocess.call(", "eval(", "exec(",
        "__import__(", "open(", "rm -rf", "DROP TABLE",
    ]

config = Config()