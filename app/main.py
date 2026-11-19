from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
import time
import os

from app.config import settings
from app.db.connection import init_db, engine
from app.db.schema_inspector import SchemaInspector
from app.models.schemas import QueryRequest, QueryResponse, ExecutionResult, RawExecuteRequest
from app.engine.guardrail import SQLSecurityGuardrail
from app.engine.generator import SQLGenerator
from app.engine.explainer import SQLExplainer

# Ensure database is initialized
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Enterprise Natural Language to SQL Analytics Platform with Schema Introspection & Guardrails",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = SQLGenerator()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "QueryCraft NL-to-SQL Analytics API is active."}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "database": "sqlite-connected",
        "llm_mode": "online" if settings.llm_api_key else "offline-simulation"
    }


@app.get("/api/schema")
async def get_database_schema():
    """Retrieve database tables, column types, and sample data."""
    return SchemaInspector.get_complete_schema_metadata()


@app.post("/api/query", response_model=QueryResponse)
async def process_natural_language_query(request: QueryRequest):
    schema_meta = SchemaInspector.get_complete_schema_metadata()
    
    # Step 1: Translate prompt to SQL
    raw_sql = await generator.generate_sql(request.prompt, schema_meta, dialect=request.dialect)

    # Step 2: Validate through security guardrail
    is_safe, sanitized_sql, error_msg = SQLSecurityGuardrail.validate_and_sanitize(raw_sql)
    if not is_safe:
        return QueryResponse(
            prompt=request.prompt,
            generated_sql=raw_sql,
            is_safe=False,
            explanation="Query rejected by security guardrail.",
            error=error_msg
        )

    # Step 3: Explanation & Execution
    explanation = SQLExplainer.explain_sql(sanitized_sql)
    exec_result = None
    chart_rec = None

    if request.auto_execute:
        start_time = time.time()
        try:
            with engine.connect() as conn:
                res = conn.execute(text(sanitized_sql))
                rows = [dict(r) for r in res.mappings()]
                columns = list(rows[0].keys()) if rows else []
                exec_time_ms = round((time.time() - start_time) * 1000, 2)
                explain_plan = SQLExplainer.get_query_plan(sanitized_sql)

                exec_result = ExecutionResult(
                    columns=columns,
                    rows=rows,
                    row_count=len(rows),
                    execution_time_ms=exec_time_ms,
                    explain_plan=explain_plan
                )
                chart_rec = SQLExplainer.recommend_chart(columns, rows)
        except Exception as e:
            return QueryResponse(
                prompt=request.prompt,
                generated_sql=sanitized_sql,
                is_safe=True,
                explanation=explanation,
                error=f"SQL Execution Error: {str(e)}"
            )

    return QueryResponse(
        prompt=request.prompt,
        generated_sql=sanitized_sql,
        is_safe=True,
        explanation=explanation,
        execution_result=exec_result,
        chart_recommendation=chart_rec
    )


@app.post("/api/execute-raw", response_model=QueryResponse)
async def execute_raw_sql(request: RawExecuteRequest):
    """Execute raw SQL safely through security guardrail sandbox."""
    is_safe, sanitized_sql, error_msg = SQLSecurityGuardrail.validate_and_sanitize(request.sql)
    if not is_safe:
        return QueryResponse(
            prompt="Direct SQL Execution",
            generated_sql=request.sql,
            is_safe=False,
            explanation="Rejected by security guardrail.",
            error=error_msg
        )

    explanation = SQLExplainer.explain_sql(sanitized_sql)
    start_time = time.time()
    try:
        with engine.connect() as conn:
            res = conn.execute(text(sanitized_sql))
            rows = [dict(r) for r in res.mappings()]
            columns = list(rows[0].keys()) if rows else []
            exec_time_ms = round((time.time() - start_time) * 1000, 2)
            explain_plan = SQLExplainer.get_query_plan(sanitized_sql)

            exec_result = ExecutionResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=exec_time_ms,
                explain_plan=explain_plan
            )
            chart_rec = SQLExplainer.recommend_chart(columns, rows)

            return QueryResponse(
                prompt="Direct SQL Execution",
                generated_sql=sanitized_sql,
                is_safe=True,
                explanation=explanation,
                execution_result=exec_result,
                chart_recommendation=chart_rec
            )
    except Exception as e:
        return QueryResponse(
            prompt="Direct SQL Execution",
            generated_sql=sanitized_sql,
            is_safe=True,
            explanation=explanation,
            error=f"Execution Failed: {str(e)}"
        )
