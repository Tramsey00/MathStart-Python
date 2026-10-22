"""Bounded, redacted child output for repository verification.

Extracted from the retired development Harness. Product check wrappers use this
without importing an agent runner or granting it execution capabilities.
"""
import re

MAX_DIAGNOSTIC_CHARS = 16_384
SECRET_LINE = re.compile(
    r"(?i)(api[_-]?key|secret|password|authorization|bearer\s|token\s*[:=]|"
    r"postgres(?:ql)?://|set-cookie:|sessionid\s*=|dsn\s*[:=])"
)


def safe_diagnostic(value: str) -> str:
    lines = (
        "[redacted sensitive line]\n" if SECRET_LINE.search(line) else line
        for line in value.splitlines(keepends=True)
    )
    content = "".join(lines)
    if len(content) > MAX_DIAGNOSTIC_CHARS:
        return content[:MAX_DIAGNOSTIC_CHARS] + "\n[output truncated]\n"
    return content
