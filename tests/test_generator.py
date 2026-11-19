import asyncio
from app.engine.generator import SQLGenerator
from app.engine.explainer import SQLExplainer
from app.db.schema_inspector import SchemaInspector
from app.db.connection import init_db


def test_sql_generator_creates_queries():
    init_db()
    generator = SQLGenerator()
    schema_meta = SchemaInspector.get_complete_schema_metadata()

    async def run():
        return await generator.generate_sql("Show top customers by total revenue", schema_meta)

    sql = asyncio.run(run())
    assert "SELECT" in sql.upper()
    assert "FROM customers" in sql or "customers c" in sql
    assert "SUM" in sql.upper() or "TOTAL" in sql.upper()


def test_sql_explainer_produces_explanation():
    sql = "SELECT c.name, SUM(o.total_amount) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name ORDER BY 2 DESC LIMIT 5"
    explanation = SQLExplainer.explain_sql(sql)
    assert "customers" in explanation.lower()
    assert "orders" in explanation.lower()
    assert "financial sums" in explanation or "groups metrics" in explanation

