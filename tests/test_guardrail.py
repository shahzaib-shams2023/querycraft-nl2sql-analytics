import pytest
from app.engine.guardrail import SQLSecurityGuardrail


def test_guardrail_permits_safe_select():
    sql = "SELECT id, name FROM customers WHERE country = 'USA'"
    is_safe, sanitized, err = SQLSecurityGuardrail.validate_and_sanitize(sql)
    assert is_safe is True
    assert err is None
    assert "LIMIT" in sanitized


def test_guardrail_permits_safe_cte():
    sql = "WITH top_cust AS (SELECT customer_id, SUM(total_amount) as rev FROM orders GROUP BY customer_id) SELECT * FROM top_cust"
    is_safe, sanitized, err = SQLSecurityGuardrail.validate_and_sanitize(sql)
    assert is_safe is True
    assert err is None


def test_guardrail_blocks_drop_table():
    sql = "DROP TABLE customers;"
    is_safe, sanitized, err = SQLSecurityGuardrail.validate_and_sanitize(sql)
    assert is_safe is False
    assert "DROP" in err


def test_guardrail_blocks_delete_mutation():
    sql = "DELETE FROM orders WHERE id = 1"
    is_safe, sanitized, err = SQLSecurityGuardrail.validate_and_sanitize(sql)
    assert is_safe is False
    assert "DELETE" in err


def test_guardrail_blocks_multi_statement_injection():
    sql = "SELECT * FROM products; DROP TABLE customers;"
    is_safe, sanitized, err = SQLSecurityGuardrail.validate_and_sanitize(sql)
    assert is_safe is False
    assert "Multiple SQL statements detected" in err


def test_guardrail_blocks_admin_commands():
    sql = "ATTACH DATABASE 'malicious.db' AS pwn;"
    is_safe, sanitized, err = SQLSecurityGuardrail.validate_and_sanitize(sql)
    assert is_safe is False
    assert "ATTACH" in err

