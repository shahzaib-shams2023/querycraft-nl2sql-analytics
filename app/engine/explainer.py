import re
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from app.db.connection import engine
from app.models.schemas import ChartRecommendation, ExecutionResult


class SQLExplainer:
    @staticmethod
    def explain_sql(sql: str) -> str:
        """Produce a structured, plain-English summary of what the query calculates."""
        sql_clean = sql.strip().upper()
        clauses = []

        # Tables
        from_match = re.search(r"FROM\s+([a-zA-Z_]+)", sql_clean)
        table = from_match.group(1).lower() if from_match else "database"
        clauses.append(f"Queries the `{table}` dataset")

        # Joins
        joins = re.findall(r"JOIN\s+([a-zA-Z_]+)", sql_clean)
        if joins:
            clauses.append(f"combines related records from {', '.join([f'`{j.lower()}`' for j in joins])}")

        # Aggregations
        if "SUM" in sql_clean:
            clauses.append("calculates cumulative financial sums")
        if "AVG" in sql_clean:
            clauses.append("computes average metrics across segments")
        if "COUNT" in sql_clean:
            clauses.append("counts total volume of entries")

        # Filtering
        if "WHERE" in sql_clean:
            clauses.append("applies conditional status and date filtering")

        # Grouping
        if "GROUP BY" in sql_clean:
            clauses.append("groups metrics by analytical dimensions")

        # Ordering & Limit
        if "ORDER BY" in sql_clean:
            clauses.append("sorts the highest priority results in descending order")
        if "LIMIT" in sql_clean:
            limit_m = re.search(r"LIMIT\s+(\d+)", sql_clean)
            limit_num = limit_m.group(1) if limit_m else "N"
            clauses.append(f"restricts output to top {limit_num} records")

        return "This query " + "; ".join(clauses) + "."

    @staticmethod
    def recommend_chart(columns: List[str], rows: List[Dict[str, Any]]) -> ChartRecommendation:
        """Selects optimal chart representation based on column types and cardinalities."""
        if not rows or not columns:
            return ChartRecommendation(
                recommended_type="metric_card",
                title="No Data",
                insights="The query returned zero matching records."
            )

        if len(rows) == 1 and len(columns) == 1:
            col = columns[0]
            val = rows[0][col]
            return ChartRecommendation(
                recommended_type="metric_card",
                title=col.replace("_", " ").title(),
                insights=f"Single aggregate value: {val}"
            )

        # Categorical x-axis candidate
        categorical_candidates = [
            c for c in columns if any(k in c.lower() for k in ["name", "status", "category", "country", "plan", "tier"])
        ]
        # Numerical y-axis candidate
        numerical_candidates = [
            c for c in columns if any(k in c.lower() for k in ["amount", "total", "spent", "revenue", "mrr", "count", "value", "price"])
        ]

        x_col = categorical_candidates[0] if categorical_candidates else columns[0]
        y_col = numerical_candidates[0] if numerical_candidates else (columns[1] if len(columns) > 1 else columns[0])

        # If analyzing status distribution or few categories (< 5), recommend doughnut/pie
        if "status" in x_col.lower() or (len(rows) <= 5 and any(k in x_col.lower() for k in ["tier", "plan", "category"])):
            return ChartRecommendation(
                recommended_type="doughnut",
                x_axis_column=x_col,
                y_axis_column=y_col,
                title=f"Distribution of {y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                insights="Proportional breakdown highlighting the relative market share of each segment."
            )

        # Default to bar chart for comparisons
        return ChartRecommendation(
            recommended_type="bar",
            x_axis_column=x_col,
            y_axis_column=y_col,
            title=f"{y_col.replace('_', ' ').title()} across {x_col.replace('_', ' ').title()}",
            insights=f"Ranked comparison illustrating key revenue and volume differentials."
        )

    @staticmethod
    def get_query_plan(sql: str) -> List[str]:
        """Fetch EXPLAIN QUERY PLAN from database."""
        plans = []
        try:
            with engine.connect() as conn:
                res = conn.execute(text(f"EXPLAIN QUERY PLAN {sql}"))
                for row in res.fetchall():
                    plans.append(str(row))
        except Exception:
            pass
        return plans

