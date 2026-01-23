import time
import pandas as pd
from typing import Any, Optional
from pandasql import sqldf

from app.services.llm_service import LLMService


class QueryEngine:
    """Service for executing queries on data"""

    @staticmethod
    def execute_sql(df: pd.DataFrame, query: str) -> tuple[pd.DataFrame, float]:
        """Execute SQL query on DataFrame using pandasql"""
        start_time = time.time()
        local_env = {"df": df}
        result = sqldf(query, local_env)
        execution_time = (time.time() - start_time) * 1000
        return result, execution_time

    @staticmethod
    def execute_pandas_operations(df: pd.DataFrame, operations: list[dict[str, Any]]) -> tuple[pd.DataFrame, float]:
        """Execute a series of pandas operations on DataFrame"""
        start_time = time.time()
        result = df.copy()

        for op in operations:
            op_type = op.get("type")

            if op_type == "filter":
                condition = op.get("condition", "")
                result = result.query(condition)
            elif op_type == "select":
                columns = op.get("columns", [])
                result = result[columns]
            elif op_type == "sort":
                by = op.get("by")
                ascending = op.get("ascending", True)
                result = result.sort_values(by=by, ascending=ascending)
            elif op_type == "groupby":
                by = op.get("by", [])
                agg = op.get("agg", {})
                result = result.groupby(by).agg(agg).reset_index()
            elif op_type == "head":
                n = op.get("n", 10)
                result = result.head(n)
            elif op_type == "tail":
                n = op.get("n", 10)
                result = result.tail(n)
            elif op_type == "drop_na":
                columns = op.get("columns")
                if columns:
                    result = result.dropna(subset=columns)
                else:
                    result = result.dropna()
            elif op_type == "fillna":
                value = op.get("value", 0)
                columns = op.get("columns")
                if columns:
                    result[columns] = result[columns].fillna(value)
                else:
                    result = result.fillna(value)
            elif op_type == "rename":
                mapping = op.get("mapping", {})
                result = result.rename(columns=mapping)

        execution_time = (time.time() - start_time) * 1000
        return result, execution_time

    @staticmethod
    async def natural_language_to_sql(question: str, schema: dict[str, Any]) -> str:
        """Convert natural language question to SQL query"""
        llm_service = LLMService()
        return await llm_service.generate_sql_query(question, schema)

    @staticmethod
    async def natural_language_to_pandas(question: str, schema: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert natural language question to pandas operations"""
        llm_service = LLMService()
        return await llm_service.generate_pandas_operations(question, schema)

    @staticmethod
    async def execute_natural_language_query(
        df: pd.DataFrame,
        question: str,
        schema: dict[str, Any],
        prefer_sql: bool = True,
    ) -> tuple[pd.DataFrame, str, float]:
        """Execute natural language query"""
        if prefer_sql:
            generated_query = await QueryEngine.natural_language_to_sql(question, schema)
            result, execution_time = QueryEngine.execute_sql(df, generated_query)
        else:
            operations = await QueryEngine.natural_language_to_pandas(question, schema)
            generated_query = str(operations)
            result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        return result, generated_query, execution_time

    @staticmethod
    def get_dataframe_stats(df: pd.DataFrame) -> dict[str, Any]:
        """Get basic statistics for DataFrame"""
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": {},
        }

        for col in df.columns:
            col_stats = {
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
            }

            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    "min": float(df[col].min()) if not df[col].isnull().all() else None,
                    "max": float(df[col].max()) if not df[col].isnull().all() else None,
                    "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                    "std": float(df[col].std()) if not df[col].isnull().all() else None,
                })

            stats["columns"][str(col)] = col_stats

        return stats
