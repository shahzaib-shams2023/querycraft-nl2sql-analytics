from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Natural language analytics question")
    dialect: str = Field("sqlite", description="Target SQL dialect: sqlite or postgresql")
    auto_execute: bool = Field(True, description="Whether to execute query immediately")


class ChartRecommendation(BaseModel):
    recommended_type: str = Field(..., description="bar, line, pie, doughnut, or metric_card")
    x_axis_column: Optional[str] = None
    y_axis_column: Optional[str] = None
    title: str
    insights: str


class ExecutionResult(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    explain_plan: Optional[List[str]] = None


class QueryResponse(BaseModel):
    prompt: str
    generated_sql: str
    is_safe: bool
    explanation: str
    execution_result: Optional[ExecutionResult] = None
    chart_recommendation: Optional[ChartRecommendation] = None
    error: Optional[str] = None


class RawExecuteRequest(BaseModel):
    sql: str = Field(..., min_length=5, description="Direct SQL query for sandboxed execution")

