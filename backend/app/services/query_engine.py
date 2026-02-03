import time
import pandas as pd
from typing import Any, Optional, Dict, List
from pandasql import sqldf
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import LLMService
from app.services.relationship_resolver import RelationshipResolver
from app.services.sql_generator import SQLGenerator
from app.services.context_service import ContextService


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

    @staticmethod
    async def execute_multi_dataset_query(
        dataframes: Dict[str, pd.DataFrame],
        context_id: UUID,
        question: str,
        user_id: UUID,
        db: AsyncSession
    ) -> tuple[pd.DataFrame, str, float, Dict[str, Any]]:
        """
        Execute natural language query across multiple datasets using context.

        Args:
            dataframes: Dict of {dataset_id: DataFrame}
            context_id: Context ID to use
            question: Natural language question
            user_id: User ID
            db: Database session

        Returns:
            Tuple of (result_df, generated_sql, execution_time, metadata)
        """
        # Load context
        context_service = ContextService(db)
        context = await context_service.get_context(context_id, user_id)

        if not context:
            raise ValueError(f"Context {context_id} not found")

        # Parse context
        context_dict = context.parsed_yaml

        # Determine required datasets from question using LLM
        llm_service = LLMService()
        analysis = await llm_service.analyze_multi_dataset_query(
            question,
            context_dict
        )

        required_datasets = analysis.get('required_datasets', [])
        required_metrics = analysis.get('required_metrics', [])
        required_filters = analysis.get('required_filters', [])

        # If only one dataset needed, use simple query
        if len(required_datasets) == 1:
            dataset_id = required_datasets[0]
            df = dataframes.get(dataset_id)
            if df is None:
                raise ValueError(f"Dataset {dataset_id} not found")

            # Generate SQL using context
            sql_generator = SQLGenerator(context_dict)
            schema = QueryEngine.get_dataframe_schema(df)
            generated_sql = await llm_service.generate_sql_with_context(
                question,
                schema,
                context_dict,
                dataset_id
            )

            result, execution_time = QueryEngine.execute_sql(df, generated_sql)

            metadata = {
                'context_id': str(context_id),
                'datasets_used': [dataset_id],
                'metrics_used': required_metrics,
                'filters_used': required_filters,
                'join_count': 0
            }

            return result, generated_sql, execution_time, metadata

        # Multi-dataset query - find join path
        relationships = context_dict.get('relationships', [])
        if not relationships:
            raise ValueError("Context has no relationships defined for multi-dataset query")

        resolver = RelationshipResolver(relationships)
        join_path = resolver.find_join_path_multi(required_datasets)

        if not join_path:
            raise ValueError(f"Cannot find join path connecting: {', '.join(required_datasets)}")

        # Generate SQL for multi-dataset query
        sql_generator = SQLGenerator(context_dict)

        # Get select columns from analysis or use *
        select_columns = analysis.get('select_columns', ['*'])

        # Apply filters if any
        where_clauses = []
        for filter_id in required_filters:
            filter_condition = sql_generator.apply_filter(filter_id)
            if filter_condition:
                where_clauses.append(filter_condition)

        # Generate multi-dataset SQL
        generated_sql = sql_generator.generate_multi_dataset_query(
            select_columns=select_columns,
            join_path=join_path,
            where_clauses=where_clauses if where_clauses else None
        )

        # Execute query by merging DataFrames
        result, execution_time = QueryEngine.execute_multi_dataset_sql(
            dataframes,
            generated_sql,
            join_path
        )

        metadata = {
            'context_id': str(context_id),
            'datasets_used': required_datasets,
            'metrics_used': required_metrics,
            'filters_used': required_filters,
            'join_count': len(join_path),
            'join_path': [edge['relationship']['id'] for edge in join_path]
        }

        return result, generated_sql, execution_time, metadata

    @staticmethod
    def execute_multi_dataset_sql(
        dataframes: Dict[str, pd.DataFrame],
        sql: str,
        join_path: List[Dict[str, Any]]
    ) -> tuple[pd.DataFrame, float]:
        """
        Execute SQL query across multiple DataFrames by joining them.

        Args:
            dataframes: Dict of {dataset_id: DataFrame}
            sql: Generated SQL query
            join_path: Join path from resolver

        Returns:
            Tuple of (result_df, execution_time)
        """
        start_time = time.time()

        # Merge DataFrames according to join path
        if not join_path:
            # Single dataset - use first available
            df = list(dataframes.values())[0]
        else:
            # Start with first dataset
            first_edge = join_path[0]
            first_rel = first_edge['relationship']

            if first_edge.get('reverse'):
                current_df = dataframes[first_rel['right_dataset']].copy()
                current_alias = first_rel['right_dataset']
            else:
                current_df = dataframes[first_rel['left_dataset']].copy()
                current_alias = first_rel['left_dataset']

            # Perform joins
            for edge in join_path:
                rel = edge['relationship']
                reverse = edge.get('reverse', False)

                if reverse:
                    right_df_id = rel['left_dataset']
                    left_on = [c['right_column'] for c in rel['conditions']]
                    right_on = [c['left_column'] for c in rel['conditions']]
                else:
                    right_df_id = rel['right_dataset']
                    left_on = [c['left_column'] for c in rel['conditions']]
                    right_on = [c['right_column'] for c in rel['conditions']]

                right_df = dataframes[right_df_id].copy()
                join_type = rel.get('join_type', 'inner')

                # Pandas merge
                current_df = current_df.merge(
                    right_df,
                    left_on=left_on,
                    right_on=right_on,
                    how=join_type,
                    suffixes=('', f'_{right_df_id}')
                )

            df = current_df

        # Execute SQL on merged DataFrame
        local_env = {"df": df}
        result = sqldf(sql, local_env)

        execution_time = (time.time() - start_time) * 1000
        return result, execution_time

    @staticmethod
    def get_dataframe_schema(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get DataFrame schema for LLM context.

        Args:
            df: DataFrame

        Returns:
            Schema dictionary
        """
        columns = []
        for col in df.columns:
            columns.append({
                'name': str(col),
                'type': str(df[col].dtype),
                'nullable': bool(df[col].isnull().any()),
                'unique_count': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(3).tolist() if not df[col].isnull().all() else []
            })

        return {
            'row_count': len(df),
            'columns': columns
        }
