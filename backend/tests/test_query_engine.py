"""Unit tests for QueryEngine service"""
import pytest
import pandas as pd
from app.services.query_engine import QueryEngine


class TestSQLExecution:
    """Test SQL query execution"""

    def test_basic_select_all(self, sample_dataframe):
        """Test basic SELECT * query"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(df, "SELECT * FROM df")

        assert len(result) == len(df)
        assert list(result.columns) == list(df.columns)
        assert execution_time > 0

    def test_select_with_where_clause(self, sample_dataframe):
        """Test SELECT with WHERE clause"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df, "SELECT * FROM df WHERE age > 30"
        )

        assert len(result) == 3  # Ages 35, 40, 45
        assert all(result["age"] > 30)
        assert execution_time > 0

    def test_select_specific_columns(self, sample_dataframe):
        """Test SELECT with specific columns"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df, "SELECT name, salary FROM df"
        )

        assert len(result.columns) == 2
        assert "name" in result.columns
        assert "salary" in result.columns
        assert execution_time > 0

    def test_select_with_limit(self, sample_dataframe):
        """Test SELECT with LIMIT"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df, "SELECT * FROM df LIMIT 3"
        )

        assert len(result) == 3
        assert execution_time > 0

    def test_select_with_order_by(self, sample_dataframe):
        """Test SELECT with ORDER BY"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df, "SELECT * FROM df ORDER BY salary DESC"
        )

        assert len(result) == len(df)
        assert result.iloc[0]["salary"] == 90000  # Highest salary
        assert result.iloc[-1]["salary"] == 50000  # Lowest salary
        assert execution_time > 0

    def test_select_with_group_by(self, sample_dataframe):
        """Test SELECT with GROUP BY"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df, "SELECT department, COUNT(*) as count FROM df GROUP BY department"
        )

        assert len(result) == 3  # 3 departments
        assert "count" in result.columns
        assert execution_time > 0

    def test_select_with_aggregations(self, sample_dataframe):
        """Test SELECT with aggregation functions"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df,
            """
            SELECT
                department,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary,
                MIN(salary) as min_salary
            FROM df
            GROUP BY department
            ORDER BY avg_salary DESC
            """
        )

        assert len(result) > 0
        assert all(col in result.columns for col in
                  ["department", "employee_count", "avg_salary", "max_salary", "min_salary"])
        assert execution_time > 0

    def test_complex_where_clause(self, sample_dataframe):
        """Test complex WHERE clause with AND/OR"""
        df = sample_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df,
            "SELECT * FROM df WHERE (age > 30 AND salary > 70000) OR department = 'Sales'"
        )

        assert len(result) > 0
        assert execution_time > 0


class TestPandasOperations:
    """Test Pandas operations execution"""

    def test_filter_operation(self, sample_dataframe):
        """Test filter operation"""
        df = sample_dataframe
        operations = [
            {"type": "filter", "condition": "age > 30"}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result) == 3
        assert all(result["age"] > 30)
        assert execution_time > 0

    def test_select_columns(self, sample_dataframe):
        """Test column selection"""
        df = sample_dataframe
        operations = [
            {"type": "select", "columns": ["name", "age"]}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result.columns) == 2
        assert "name" in result.columns
        assert "age" in result.columns
        assert execution_time > 0

    def test_sort_operation(self, sample_dataframe):
        """Test sort operation"""
        df = sample_dataframe
        operations = [
            {"type": "sort", "by": "salary", "ascending": False}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert result.iloc[0]["salary"] == 90000
        assert result.iloc[-1]["salary"] == 50000
        assert execution_time > 0

    def test_head_operation(self, sample_dataframe):
        """Test head operation"""
        df = sample_dataframe
        operations = [
            {"type": "head", "n": 3}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result) == 3
        assert execution_time > 0

    def test_tail_operation(self, sample_dataframe):
        """Test tail operation"""
        df = sample_dataframe
        operations = [
            {"type": "tail", "n": 2}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result) == 2
        assert execution_time > 0

    def test_groupby_operation(self, sample_dataframe):
        """Test groupby operation"""
        df = sample_dataframe
        operations = [
            {
                "type": "groupby",
                "by": ["department"],
                "agg": {"salary": "mean", "age": "count"}
            }
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result) == 3  # 3 departments
        assert "salary" in result.columns
        assert "age" in result.columns
        assert execution_time > 0

    def test_drop_na_operation(self):
        """Test drop_na operation"""
        df = pd.DataFrame({
            "a": [1, 2, None, 4],
            "b": [1, None, 3, 4]
        })
        operations = [
            {"type": "drop_na"}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result) == 2  # Only rows without NaN
        assert execution_time > 0

    def test_fillna_operation(self):
        """Test fillna operation"""
        df = pd.DataFrame({
            "a": [1, 2, None, 4],
            "b": [1, None, 3, 4]
        })
        operations = [
            {"type": "fillna", "value": 0}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert result["a"].isnull().sum() == 0
        assert result["b"].isnull().sum() == 0
        assert execution_time > 0

    def test_rename_operation(self, sample_dataframe):
        """Test rename operation"""
        df = sample_dataframe
        operations = [
            {"type": "rename", "mapping": {"name": "employee_name", "age": "employee_age"}}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert "employee_name" in result.columns
        assert "employee_age" in result.columns
        assert "name" not in result.columns
        assert "age" not in result.columns
        assert execution_time > 0

    def test_chained_operations(self, sample_dataframe):
        """Test multiple chained operations"""
        df = sample_dataframe
        operations = [
            {"type": "filter", "condition": "age > 25"},
            {"type": "select", "columns": ["name", "salary", "department"]},
            {"type": "sort", "by": "salary", "ascending": False},
            {"type": "head", "n": 3}
        ]
        result, execution_time = QueryEngine.execute_pandas_operations(df, operations)

        assert len(result) == 3
        assert len(result.columns) == 3
        # Check that salary is sorted in descending order
        assert all(result["salary"].iloc[i] >= result["salary"].iloc[i+1]
                  for i in range(len(result)-1))
        assert execution_time > 0


class TestSalesAnalysis:
    """Test queries on sales data"""

    def test_top_products_by_revenue(self, sample_sales_dataframe):
        """Test finding top products by revenue"""
        df = sample_sales_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df,
            """
            SELECT
                product,
                SUM(quantity * price) as total_revenue,
                SUM(quantity) as total_quantity
            FROM df
            GROUP BY product
            ORDER BY total_revenue DESC
            """
        )

        assert len(result) == 4  # 4 unique products
        assert "total_revenue" in result.columns
        assert result.iloc[0]["product"] == "Laptop"  # Highest revenue
        assert execution_time > 0

    def test_customer_purchase_analysis(self, sample_sales_dataframe):
        """Test customer purchase analysis"""
        df = sample_sales_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df,
            """
            SELECT
                customer,
                COUNT(*) as order_count,
                SUM(quantity * price) as total_spent
            FROM df
            GROUP BY customer
            ORDER BY total_spent DESC
            """
        )

        assert len(result) == 5  # 5 unique customers
        assert "order_count" in result.columns
        assert "total_spent" in result.columns
        assert execution_time > 0

    def test_average_order_value(self, sample_sales_dataframe):
        """Test calculating average order value"""
        df = sample_sales_dataframe
        result, execution_time = QueryEngine.execute_sql(
            df,
            """
            SELECT
                AVG(quantity * price) as avg_order_value,
                MIN(quantity * price) as min_order_value,
                MAX(quantity * price) as max_order_value
            FROM df
            """
        )

        assert len(result) == 1
        assert "avg_order_value" in result.columns
        assert execution_time > 0


class TestDataFrameStats:
    """Test DataFrame statistics"""

    def test_get_basic_stats(self, sample_dataframe):
        """Test getting basic DataFrame statistics"""
        df = sample_dataframe
        stats = QueryEngine.get_dataframe_stats(df)

        assert stats["row_count"] == 5
        assert stats["column_count"] == 5
        assert "columns" in stats

    def test_numeric_column_stats(self, sample_dataframe):
        """Test numeric column statistics"""
        df = sample_dataframe
        stats = QueryEngine.get_dataframe_stats(df)

        age_stats = stats["columns"]["age"]
        assert age_stats["dtype"] == "int64"
        assert age_stats["null_count"] == 0
        assert age_stats["unique_count"] == 5
        assert "min" in age_stats
        assert "max" in age_stats
        assert "mean" in age_stats
        assert "std" in age_stats

    def test_string_column_stats(self, sample_dataframe):
        """Test string column statistics"""
        df = sample_dataframe
        stats = QueryEngine.get_dataframe_stats(df)

        name_stats = stats["columns"]["name"]
        assert name_stats["dtype"] == "object"
        assert name_stats["null_count"] == 0
        assert name_stats["unique_count"] == 5

    def test_stats_with_nulls(self):
        """Test statistics with null values"""
        df = pd.DataFrame({
            "a": [1, 2, None, 4, 5],
            "b": ["x", "y", None, "z", "w"]
        })
        stats = QueryEngine.get_dataframe_stats(df)

        assert stats["columns"]["a"]["null_count"] == 1
        assert stats["columns"]["b"]["null_count"] == 1
