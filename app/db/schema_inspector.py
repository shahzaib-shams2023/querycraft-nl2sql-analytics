from sqlalchemy import inspect, text
from typing import Dict, List, Any
from app.db.connection import engine


class SchemaInspector:
    @staticmethod
    def get_complete_schema_metadata() -> Dict[str, Any]:
        """Extract table names, column types, foreign keys, and sample rows."""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        schema_dict = {}

        with engine.connect() as conn:
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                fks = inspector.get_foreign_keys(table_name)
                pk = inspector.get_pk_constraint(table_name)

                # Fetch up to 2 sample rows
                sample_rows = []
                try:
                    res = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 2"))
                    for row in res.mappings():
                        sample_rows.append(dict(row))
                except Exception:
                    pass

                schema_dict[table_name] = {
                    "columns": [{"name": c["name"], "type": str(c["type"])} for c in columns],
                    "primary_key": pk.get("constrained_columns", []),
                    "foreign_keys": [
                        {
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"]
                        }
                        for fk in fks
                    ],
                    "samples": sample_rows
                }

        return schema_dict

    @staticmethod
    def format_schema_for_llm(schema_metadata: Dict[str, Any]) -> str:
        """Render a concise DDL-style prompt representation for the LLM."""
        lines = []
        for table, meta in schema_metadata.items():
            cols = [f"{c['name']} ({c['type']})" for c in meta["columns"]]
            fk_strs = [f"FK {fk['constrained_columns']} -> {fk['referred_table']}({fk['referred_columns']})" for fk in meta["foreign_keys"]]
            line = f"Table `{table}`:\n  Columns: {', '.join(cols)}"
            if fk_strs:
                line += f"\n  Relationships: {'; '.join(fk_strs)}"
            lines.append(line)
        return "\n\n".join(lines)

