from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "QueryCraft" in data["service"]


def test_schema_api():
    res = client.get("/api/schema")
    assert res.status_code == 200
    data = res.json()
    assert "customers" in data
    assert "orders" in data


def test_query_api_valid():
    payload = {
        "prompt": "Show top customers by total revenue",
        "auto_execute": True
    }
    res = client.post("/api/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_safe"] is True
    assert data["execution_result"] is not None
    assert data["execution_result"]["row_count"] > 0
    assert data["chart_recommendation"] is not None


def test_query_api_blocks_injection():
    payload = {
        "prompt": "DROP TABLE customers; SELECT * FROM products",
        "auto_execute": True
    }
    # Raw SQL execution of drop
    res = client.post("/api/execute-raw", json={"sql": "DROP TABLE customers;"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_safe"] is False
    assert "DROP" in data["error"]

