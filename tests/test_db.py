import pytest
from sqlalchemy import text
from app.db.connection import init_db, engine
from app.db.schema_inspector import SchemaInspector


def test_database_initialization_and_seeding():
    init_db()
    with engine.connect() as conn:
        cust_count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        orders_count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        products_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        subs_count = conn.execute(text("SELECT COUNT(*) FROM subscriptions")).scalar()

    assert cust_count >= 10
    assert orders_count >= 10
    assert products_count >= 5
    assert subs_count >= 10


def test_schema_inspector_extracts_metadata():
    init_db()
    meta = SchemaInspector.get_complete_schema_metadata()
    assert "customers" in meta
    assert "orders" in meta
    assert "products" in meta
    assert "subscriptions" in meta

    cust_cols = [c["name"] for c in meta["customers"]["columns"]]
    assert "name" in cust_cols
    assert "email" in cust_cols
    assert "plan_tier" in cust_cols
    assert len(meta["customers"]["samples"]) > 0

