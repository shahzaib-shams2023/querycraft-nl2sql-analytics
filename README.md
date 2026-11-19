# QueryCraft: Enterprise Natural Language to SQL Analytics Platform

QueryCraft is a secure, production-grade Text-to-SQL data analytics platform designed to bridge the gap between non-technical business stakeholders and relational database warehouses.

---

## 🔍 The Problem
Business analysts and executives often need timely data insights but lack proficiency in complex SQL syntax, joins, aggregations, and CTEs. However, naive LLM-to-SQL implementations introduce catastrophic risks:
- **Destructive Mutation Injections**: Erroneous or malicious execution of `DROP`, `UPDATE`, or `DELETE` statements.
- **Hallucinated Schemas**: Referencing non-existent tables or invalid column types.
- **Runaway Unindexed Queries**: Producing cartesian products that exhaust database compute and memory.

## 💡 The Solution
QueryCraft provides an enterprise-ready pipeline with strict security guardrails and schema introspection:
1. **Dynamic Schema Introspection**: Extracts live tables, foreign key relationships, data types, and representative sample values.
2. **Dialect-Aware Translation**: Translates complex natural language questions into efficient, indexed SQL.
3. **AST Security Guardrails**: Forbids data mutations (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`), multi-statement semicolons, and enforces maximum row limits.
4. **Sandboxed Execution**: Executes safe read-only queries with millisecond timer telemetry and `EXPLAIN QUERY PLAN` extraction.
5. **Automated Visualizer**: Automatically inspects query cardinality to recommend and render Chart.js graphs (Bar, Doughnut, Line, Metric Cards).

---

## 🏛️ System Architecture

```
User Analytics Prompt
       │
       ▼
[Schema Inspector] ──► Extracts Tables, Columns, Foreign Keys & Samples
       │
       ▼
[SQL Generator] ─────► Dialect-Aware SQL Generation
       │
       ▼
[AST Guardrail] ─────► Validates Read-Only & Rejects Mutations/Injections
       │
       ▼
[Execution Sandbox] ─► Safe Query Execution & EXPLAIN PLAN Telemetry
       │
       ▼
[Explainer Engine] ──► Plain-English Breakdown & Chart Recommendation
       │
       ▼
Interactive Web Dashboard & REST API
```

---

## 🛠️ Technology Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: SQLite (built-in) / PostgreSQL compatible
- **Security**: AST Token Guardrails, SQL Injection Prevention
- **Frontend**: Responsive Tailwind CSS Dashboard, Chart.js Visualizer
- **Testing**: Pytest, Starlette TestClient
- **Containerization**: Docker, Docker Compose, GitHub Actions CI

---

## 🚀 Getting Started

### Installation
```bash
cd querycraft-nl2sql-analytics

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Optional: set `LLM_API_KEY` to connect OpenAI, Groq, or OpenRouter. If left empty, QueryCraft runs automatically with its deterministic local translation engine.

### Running the Platform
```bash
python -m uvicorn app.main:app --reload --port 8001
```
Navigate to `http://localhost:8001` to use the interactive dashboard, or `http://localhost:8001/docs` for API documentation.

---

## 🧪 Running Automated Tests
```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment
```bash
docker compose up --build
```
Access the application at `http://localhost:8001`.

---

## 📡 API Reference

### Natural Language Query
`POST /api/query`
```json
{
  "prompt": "Show top 5 customers by total revenue and order count",
  "auto_execute": true
}
```

Response:
```json
{
  "prompt": "Show top 5 customers by total revenue and order count",
  "generated_sql": "SELECT c.name, c.plan_tier, SUM(o.total_amount) AS total_spent ...",
  "is_safe": true,
  "explanation": "This query queries the customers dataset, combines related records ...",
  "execution_result": {
    "columns": ["name", "plan_tier", "country", "total_spent", "order_count"],
    "rows": [...],
    "row_count": 5,
    "execution_time_ms": 1.45
  },
  "chart_recommendation": {
    "recommended_type": "bar",
    "x_axis_column": "name",
    "y_axis_column": "total_spent",
    "title": "Total Spent across Name"
  }
}
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

