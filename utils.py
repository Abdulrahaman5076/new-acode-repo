"""
Code Whisperer - Utility Functions
Validation, formatting, rate limiting, and error handling.
These are the foundation. Everything else depends on these being rock solid.
"""

import time
import hashlib
from datetime import datetime
from typing import Tuple, Optional
from config import config

# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------
def validate_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validates user-submitted code before any processing.
    Returns (is_valid, error_message).
    Never throws an exception.
    """
    if not code or not code.strip():
        return False, "Code cannot be empty."
    
    if len(code) > config.MAX_CODE_CHARS:
        return False, f"Code is too long. Maximum {config.MAX_CODE_CHARS:,} characters. Yours has {len(code):,}."
    
    if len(code.splitlines()) > config.MAX_CODE_LINES:
        return False, f"Too many lines. Maximum {config.MAX_CODE_LINES:,}. Yours has {len(code.splitlines()):,}."
    
    for pattern in config.BLOCKED_PATTERNS:
        if pattern in code:
            return False, f"Potentially dangerous code detected: '{pattern}'. This is blocked for security."
    
    return True, None

# ---------------------------------------------------------------------------
# Rate Limiter (Sliding Window)
# ---------------------------------------------------------------------------
class RateLimiter:
    """
    Sliding window rate limiter.
    Allows N requests per window without any external dependencies.
    """
    def __init__(self):
        self.requests = []
    
    def is_allowed(self) -> bool:
        now = time.time()
        window_start = now - config.RATE_LIMIT_WINDOW_SECONDS
        self.requests = [t for t in self.requests if t > window_start]
        
        if len(self.requests) >= config.RATE_LIMIT_REQUESTS:
            return False
        
        self.requests.append(now)
        return True
    
    def remaining(self) -> int:
        now = time.time()
        window_start = now - config.RATE_LIMIT_WINDOW_SECONDS
        self.requests = [t for t in self.requests if t > window_start]
        return max(0, config.RATE_LIMIT_REQUESTS - len(self.requests))

# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------
def format_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def format_number(n: int) -> str:
    return f"{n:,}"

def truncate_string(s: str, max_len: int = 100) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len-3] + "..."

# ---------------------------------------------------------------------------
# Simple Cache
# ---------------------------------------------------------------------------
class SimpleCache:
    """
    In-memory cache with TTL. No Redis needed.
    For when you have thousands of users and can't afford to hit the AI API twice.
    """
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[str]:
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: str, ttl: int = None):
        if ttl is None:
            ttl = config.CACHE_TTL_SECONDS
        self._cache[key] = (value, time.time() + ttl)
        
        # Evict oldest if over capacity
        if len(self._cache) > config.CACHE_SIZE:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
    
    def make_key(self, code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

# Global instances
cache = SimpleCache()
rate_limiter = RateLimiter()