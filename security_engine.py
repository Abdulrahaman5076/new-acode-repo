"""
Code Whisperer - Security Engine
Scans code for common vulnerabilities and anti-patterns.
"""

import re
from dataclasses import dataclass, field
from typing import List

@dataclass
class SecurityIssue:
    severity: str      # CRITICAL, HIGH, MEDIUM, LOW
    category: str      # HARDCODED_SECRET, INJECTION, UNSAFE_EVAL, etc.
    line: int
    description: str
    suggestion: str

@dataclass
class SecurityReport:
    issues: List[SecurityIssue] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "CRITICAL")
    
    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

class SecurityScanner:
    """
    Scans source code for security vulnerabilities.
    Each rule is a (pattern, severity, category, description, suggestion) tuple.
    """
    
    RULES = [
        # (regex pattern, severity, category, description, suggestion)
        (
            r'(?:api_key|apikey|secret|password|token)\s*=\s*["\'][^"\']+["\']',
            "CRITICAL",
            "HARDCODED_SECRET",
            "Hardcoded secret or API key found.",
            "Use environment variables: os.getenv('SECRET')"
        ),
        (
            r'eval\s*\(',
            "CRITICAL",
            "UNSAFE_EVAL",
            "Use of eval() can execute arbitrary code.",
            "Use json.loads() for parsing or ast.literal_eval() for expressions."
        ),
        (
            r'exec\s*\(',
            "CRITICAL",
            "UNSAFE_EXEC",
            "Use of exec() can execute arbitrary code.",
            "Remove exec() entirely. There is almost always a safer alternative."
        ),
        (
            r'os\.system\s*\(',
            "HIGH",
            "COMMAND_INJECTION",
            "os.system() with user input enables command injection.",
            "Use subprocess.run() with shell=False and argument lists."
        ),
        (
            r'subprocess\.call\s*\(.*shell\s*=\s*True',
            "HIGH",
            "COMMAND_INJECTION",
            "subprocess with shell=True is vulnerable to injection.",
            "Set shell=False and pass arguments as a list."
        ),
        (
            r'(?:SELECT|INSERT|UPDATE|DELETE).*\%s.*\%',
            "HIGH",
            "SQL_INJECTION",
            "String formatting in SQL query may enable SQL injection.",
            "Use parameterized queries with ? placeholders."
        ),
        (
            r'pickle\.loads?\s*\(',
            "MEDIUM",
            "UNSAFE_DESERIALIZATION",
            "pickle can execute arbitrary code during deserialization.",
            "Use json.loads() for data or a safe serialization format."
        ),
        (
            r'password\s*=\s*input\s*\(',
            "MEDIUM",
            "PASSWORD_VISIBLE",
            "Password input may be visible on screen.",
            "Use getpass.getpass() for password input."
        ),
    ]
    
    def scan(self, code: str) -> SecurityReport:
        report = SecurityReport()
        lines = code.splitlines()
        
        for pattern, severity, category, description, suggestion in self.RULES:
            for match in re.finditer(pattern, code, re.IGNORECASE):
                line_no = code[:match.start()].count("\n") + 1
                line_content = lines[line_no - 1] if line_no <= len(lines) else ""
                
                issue = SecurityIssue(
                    severity=severity,
                    category=category,
                    line=line_no,
                    description=f"{description}\nFound: `{line_content.strip()[:80]}...`" if len(line_content.strip()) > 80 else f"{description}\nFound: `{line_content.strip()}`",
                    suggestion=suggestion,
                )
                report.issues.append(issue)
        
        return report