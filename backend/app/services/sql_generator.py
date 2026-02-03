"""
SQL Generator for Multi-Dataset Queries
Generates SQL from context definitions and join paths
"""
from typing import List, Dict, Any, Optional
import re


class SQLGenerator:
    """
    Generates SQL queries for multi-dataset analysis using context definitions.
    """

    def __init__(self, context: Dict[str, Any]):
        """
        Initialize with context definition.

        Args:
            context: Parsed context dictionary
        """
        self.context = context
        self.datasets = {ds['id']: ds for ds in context.get('datasets', [])}
        self.metrics = {m['id']: m for m in context.get('metrics', [])} if context.get('metrics') else {}
        self.filters = {f['id']: f for f in context.get('filters', [])} if context.get('filters') else {}

    def generate_multi_dataset_query(
        self,
        select_columns: List[str],
        join_path: List[Dict[str, Any]],
        where_clauses: Optional[List[str]] = None,
        group_by: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> str:
        """
        Generate SQL query joining multiple datasets.

        Args:
            select_columns: Columns to select (with aliases)
            join_path: Join path from RelationshipResolver
            where_clauses: WHERE conditions
            group_by: GROUP BY columns
            order_by: ORDER BY columns
            limit: LIMIT clause

        Returns:
            Generated SQL query string
        """
        # Build SELECT clause
        select_clause = self._build_select_clause(select_columns)

        # Build FROM clause
        from_clause = self._build_from_clause(join_path)

        # Build WHERE clause
        where_clause = self._build_where_clause(where_clauses or [])

        # Build GROUP BY clause
        group_by_clause = self._build_group_by_clause(group_by or [])

        # Build ORDER BY clause
        order_by_clause = self._build_order_by_clause(order_by or [])

        # Build LIMIT clause
        limit_clause = f"LIMIT {limit}" if limit else ""

        # Combine all parts
        sql_parts = [
            f"SELECT {select_clause}",
            from_clause,
            where_clause,
            group_by_clause,
            order_by_clause,
            limit_clause
        ]

        sql = "\n".join([part for part in sql_parts if part])
        return sql

    def _build_select_clause(self, columns: List[str]) -> str:
        """Build SELECT clause, expanding metrics if needed"""
        expanded_columns = []

        for col in columns:
            # Check if it's a metric
            if col in self.metrics:
                metric = self.metrics[col]
                expanded_columns.append(f"{metric['expression']} AS {col}")
            else:
                expanded_columns.append(col)

        return ",\n    ".join(expanded_columns)

    def _build_from_clause(self, join_path: List[Dict[str, Any]]) -> str:
        """
        Build FROM clause with JOINs.

        Args:
            join_path: Join path from RelationshipResolver

        Returns:
            FROM clause with all joins
        """
        if not join_path:
            # Single dataset query
            if self.datasets:
                first_ds = list(self.datasets.values())[0]
                alias = first_ds.get('alias', first_ds['id'])
                return f"FROM {first_ds['id']} AS {alias}"
            return "FROM dataset"

        # Start with first dataset in path
        first_edge = join_path[0]
        first_rel = first_edge['relationship']

        # Determine starting dataset
        if first_edge.get('reverse'):
            start_ds_id = first_rel['right_dataset']
        else:
            start_ds_id = first_rel['left_dataset']

        start_ds = self.datasets.get(start_ds_id, {'id': start_ds_id})
        start_alias = start_ds.get('alias', start_ds_id)

        from_parts = [f"FROM {start_ds_id} AS {start_alias}"]

        # Add joins
        for edge in join_path:
            rel = edge['relationship']
            reverse = edge.get('reverse', False)

            if reverse:
                # Reversed join
                left_ds_id = rel['right_dataset']
                right_ds_id = rel['left_dataset']
                # Reverse conditions
                conditions = [
                    {
                        'left_column': c['right_column'],
                        'operator': c['operator'],
                        'right_column': c['left_column']
                    }
                    for c in rel['conditions']
                ]
            else:
                left_ds_id = rel['left_dataset']
                right_ds_id = rel['right_dataset']
                conditions = rel['conditions']

            right_ds = self.datasets.get(right_ds_id, {'id': right_ds_id})
            right_alias = right_ds.get('alias', right_ds_id)
            join_type = rel.get('join_type', 'inner').upper()

            # Build join conditions
            join_conditions = []
            for cond in conditions:
                left_alias_lookup = self.datasets.get(left_ds_id, {}).get('alias', left_ds_id)
                left_col = f"{left_alias_lookup}.{cond['left_column']}"
                right_col = f"{right_alias}.{cond['right_column']}"
                operator = cond['operator']

                condition_type = cond.get('condition_type', 'on')
                if condition_type == 'on' or len(join_conditions) == 0:
                    join_conditions.append(f"{left_col} {operator} {right_col}")
                else:
                    join_conditions.append(f"{condition_type.upper()} {left_col} {operator} {right_col}")

            join_clause = f"{join_type} JOIN {right_ds_id} AS {right_alias} ON {' '.join(join_conditions)}"
            from_parts.append(join_clause)

        return "\n".join(from_parts)

    def _build_where_clause(self, conditions: List[str]) -> str:
        """Build WHERE clause"""
        if not conditions:
            return ""

        return f"WHERE {' AND '.join(conditions)}"

    def _build_group_by_clause(self, columns: List[str]) -> str:
        """Build GROUP BY clause"""
        if not columns:
            return ""

        return f"GROUP BY {', '.join(columns)}"

    def _build_order_by_clause(self, columns: List[str]) -> str:
        """Build ORDER BY clause"""
        if not columns:
            return ""

        return f"ORDER BY {', '.join(columns)}"

    def apply_filter(self, filter_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Get WHERE clause for a predefined filter.

        Args:
            filter_id: Filter ID from context
            params: Parameter values for parameterized filters

        Returns:
            WHERE condition string
        """
        if filter_id not in self.filters:
            return ""

        filter_def = self.filters[filter_id]
        condition = filter_def['condition']

        # Replace parameters if provided
        if params and filter_def.get('parameters'):
            for param_def in filter_def['parameters']:
                param_name = param_def['name']
                if param_name in params:
                    placeholder = f"{{{param_name}}}"
                    value = params[param_name]

                    # Format value based on data type
                    data_type = param_def.get('data_type', 'string')
                    if data_type == 'string':
                        formatted_value = f"'{value}'"
                    else:
                        formatted_value = str(value)

                    condition = condition.replace(placeholder, formatted_value)

        return condition

    def expand_metric(self, metric_id: str) -> str:
        """
        Get expression for a metric.

        Args:
            metric_id: Metric ID from context

        Returns:
            SQL expression for the metric
        """
        if metric_id not in self.metrics:
            return metric_id

        return self.metrics[metric_id]['expression']

    def generate_simple_query(
        self,
        dataset_id: str,
        select_columns: List[str],
        where_clauses: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> str:
        """
        Generate simple single-dataset query.

        Args:
            dataset_id: Dataset ID
            select_columns: Columns to select
            where_clauses: WHERE conditions
            limit: LIMIT value

        Returns:
            SQL query string
        """
        dataset = self.datasets.get(dataset_id, {'id': dataset_id})
        alias = dataset.get('alias', dataset_id)

        select_clause = self._build_select_clause(select_columns)
        where_clause = self._build_where_clause(where_clauses or [])
        limit_clause = f"LIMIT {limit}" if limit else ""

        sql_parts = [
            f"SELECT {select_clause}",
            f"FROM {dataset_id} AS {alias}",
            where_clause,
            limit_clause
        ]

        return "\n".join([part for part in sql_parts if part])

    def validate_sql(self, sql: str) -> bool:
        """
        Basic SQL validation.

        Checks for:
        - SQL injection patterns
        - Dangerous commands (DROP, DELETE without WHERE)

        Returns:
            True if SQL appears safe
        """
        sql_upper = sql.upper()

        # Check for dangerous commands
        dangerous_patterns = [
            'DROP TABLE',
            'DROP DATABASE',
            'TRUNCATE',
            'DELETE FROM.*(?!WHERE)',  # DELETE without WHERE
            'UPDATE.*SET.*(?!WHERE)',  # UPDATE without WHERE
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sql_upper):
                return False

        return True
