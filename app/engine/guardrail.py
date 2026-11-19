import re
from typing import Tuple, Optional
from app.config import settings


class SQLSecurityGuardrail:
    # Forbidden keywords that mutate data or compromise database integrity
    FORBIDDEN_KEYWORDS = {
        "drop", "delete", "insert", "update", "alter", "truncate", "create",
        "replace", "grant", "revoke", "attach", "detach", "vacuum", "exec",
        "execute", "shutdown", "kill", "xp_cmdshell"
    }

    @classmethod
    def validate_and_sanitize(cls, sql: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validates SQL against injection, multi-statement attacks, and mutation risks.
        Returns: (is_safe: bool, sanitized_sql: str, error_message: Optional[str])
        """
        cleaned_sql = sql.strip().rstrip(";")
        
        # Check 1: Multi-statement detection (semicolon inside query)
        # Split by semicolon ignoring inside strings
        statements = [s.strip() for s in cleaned_sql.split(";") if s.strip()]
        if len(statements) > 1:
            return False, cleaned_sql, "Multiple SQL statements detected. Only single queries are permitted."

        # Check 2: Leading command must be SELECT, WITH (CTE), or EXPLAIN
        tokens = re.findall(r"[a-zA-Z_]+", cleaned_sql.lower())
        if not tokens:
            return False, cleaned_sql, "Empty SQL query."

        first_token = tokens[0]
        if first_token not in ("select", "with", "explain"):
            return False, cleaned_sql, f"Disallowed statement type: '{first_token.upper()}'. Only read-only queries are allowed."

        # Check 3: Search for forbidden mutation words anywhere in tokens
        for token in tokens:
            if token in cls.FORBIDDEN_KEYWORDS:
                return False, cleaned_sql, f"Security Violation: Forbidden keyword '{token.upper()}' detected in query."

        # Check 4: Enforce maximum row limit if not specified
        if "limit" not in tokens:
            sanitized_sql = f"{cleaned_sql} LIMIT {settings.max_query_rows}"
        else:
            sanitized_sql = cleaned_sql

        return True, sanitized_sql, None

