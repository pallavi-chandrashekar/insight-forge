"""Integration tests for Query API endpoints"""
import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.dataset import Dataset, DatasetFormat
from app.models.user import User


class TestQueryExecutionAPI:
    """Test query execution API endpoints"""

    @pytest.fixture
    async def test_dataset(self, db_session: AsyncSession, test_user: User) -> Dataset:
        """Create a test dataset"""
        # Create sample data
        df = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Product A", "Product B", "Product C", "Product D", "Product E"],
            "category": ["Electronics", "Clothing", "Electronics", "Food", "Clothing"],
            "price": [299.99, 49.99, 599.99, 12.99, 79.99],
            "stock": [100, 250, 50, 500, 150]
        })

        # Create dataset
        dataset = Dataset(
            user_id=test_user.id,
            name="Test Products",
            filename="test_products.csv",
            format=DatasetFormat.CSV,
            file_path="/tmp/test_products.csv",
            row_count=len(df),
            column_count=len(df.columns),
            schema={
                "columns": [
                    {"name": "id", "type": "int64"},
                    {"name": "name", "type": "object"},
                    {"name": "category", "type": "object"},
                    {"name": "price", "type": "float64"},
                    {"name": "stock", "type": "int64"}
                ]
            }
        )

        # Save DataFrame
        df.to_csv("/tmp/test_products.csv", index=False)

        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)
        return dataset

    def test_execute_sql_query_success(
        self, client: TestClient, auth_headers: dict, test_dataset: Dataset
    ):
        """Test successful SQL query execution"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "sql",
                "query": "SELECT * FROM df WHERE price > 100",
                "name": "Expensive Products"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["query_type"] == "sql"
        assert data["name"] == "Expensive Products"
        assert data["result_preview"] is not None
        assert len(data["result_preview"]) == 2  # 2 products > $100
        assert data["execution_time_ms"] is not None
        assert data["error_message"] is None

    def test_execute_sql_query_with_aggregation(
        self, client: TestClient, auth_headers: dict, test_dataset: Dataset
    ):
        """Test SQL query with aggregation"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "sql",
                "query": """
                    SELECT category, COUNT(*) as count, AVG(price) as avg_price
                    FROM df
                    GROUP BY category
                    ORDER BY avg_price DESC
                """
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result_preview"] is not None
        assert len(data["result_preview"]) == 3  # 3 categories

    def test_execute_sql_query_invalid_syntax(
        self, client: TestClient, auth_headers: dict, test_dataset: Dataset
    ):
        """Test SQL query with invalid syntax"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "sql",
                "query": "SELECT * FORM df"  # Typo: FORM instead of FROM
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["error_message"] is not None

    def test_execute_pandas_operations(
        self, client: TestClient, auth_headers: dict, test_dataset: Dataset
    ):
        """Test Pandas operations execution"""
        operations = [
            {"type": "filter", "condition": "price > 50"},
            {"type": "sort", "by": "price", "ascending": False},
            {"type": "head", "n": 3}
        ]

        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "pandas",
                "query": str(operations).replace("'", '"'),
                "name": "Top 3 Expensive Products"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["query_type"] == "pandas"
        assert data["result_preview"] is not None
        assert len(data["result_preview"]) == 3

    def test_execute_query_dataset_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test query execution with non-existent dataset"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(uuid4()),
                "query_type": "sql",
                "query": "SELECT * FROM df"
            }
        )

        assert response.status_code == 404
        assert "Dataset not found" in response.json()["detail"]

    def test_execute_query_unauthorized(
        self, client: TestClient, test_dataset: Dataset
    ):
        """Test query execution without authentication"""
        response = client.post(
            "/api/query/execute",
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "sql",
                "query": "SELECT * FROM df"
            }
        )

        assert response.status_code == 401


class TestNaturalLanguageQueryAPI:
    """Test natural language query API endpoints"""

    @pytest.fixture
    async def sales_dataset(self, db_session: AsyncSession, test_user: User) -> Dataset:
        """Create a sales dataset for NL queries"""
        df = pd.DataFrame({
            "order_id": [1, 2, 3, 4, 5],
            "customer": ["Alice", "Bob", "Charlie", "Alice", "David"],
            "product": ["Laptop", "Mouse", "Keyboard", "Monitor", "Laptop"],
            "quantity": [1, 2, 1, 1, 2],
            "price": [1200.00, 25.00, 75.00, 300.00, 1200.00],
            "order_date": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
        })

        dataset = Dataset(
            user_id=test_user.id,
            name="Sales Data",
            filename="sales.csv",
            format=DatasetFormat.CSV,
            file_path="/tmp/sales.csv",
            row_count=len(df),
            column_count=len(df.columns),
            schema={
                "columns": [
                    {"name": col, "type": str(df[col].dtype)}
                    for col in df.columns
                ]
            }
        )

        df.to_csv("/tmp/sales.csv", index=False)

        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)
        return dataset

    @pytest.mark.skip(reason="Requires LLM API key and may incur costs")
    def test_natural_language_query_success(
        self, client: TestClient, auth_headers: dict, sales_dataset: Dataset
    ):
        """Test successful natural language query execution"""
        response = client.post(
            "/api/query/natural-language",
            headers=auth_headers,
            json={
                "dataset_id": str(sales_dataset.id),
                "question": "What are the top 3 products by total revenue?",
                "name": "Top Products"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["query_type"] == "natural_language"
        assert data["original_input"] == "What are the top 3 products by total revenue?"
        assert data["generated_query"] is not None
        assert data["result_preview"] is not None

    @pytest.mark.skip(reason="Requires LLM API key and may incur costs")
    def test_natural_language_customer_analysis(
        self, client: TestClient, auth_headers: dict, sales_dataset: Dataset
    ):
        """Test customer analysis via natural language"""
        response = client.post(
            "/api/query/natural-language",
            headers=auth_headers,
            json={
                "dataset_id": str(sales_dataset.id),
                "question": "How many orders did Alice make?"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result_preview"] is not None


class TestQueryHistoryAPI:
    """Test query history API endpoints"""

    @pytest.fixture
    async def dataset_with_queries(
        self, db_session: AsyncSession, test_user: User
    ) -> Dataset:
        """Create dataset with query history"""
        from app.models.query import Query, QueryType

        # Create dataset
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        dataset = Dataset(
            user_id=test_user.id,
            name="Test Dataset",
            filename="test.csv",
            format=DatasetFormat.CSV,
            file_path="/tmp/test.csv",
            row_count=3,
            column_count=2,
            schema={"columns": [{"name": "a", "type": "int64"}, {"name": "b", "type": "int64"}]}
        )
        df.to_csv("/tmp/test.csv", index=False)
        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)

        # Create some queries
        for i in range(3):
            query = Query(
                user_id=test_user.id,
                dataset_id=dataset.id,
                name=f"Query {i+1}",
                query_type=QueryType.SQL,
                original_input=f"SELECT * FROM df LIMIT {i+1}",
                result_row_count=str(i+1),
                execution_time_ms="100"
            )
            db_session.add(query)

        await db_session.commit()
        return dataset

    def test_get_query_history(
        self, client: TestClient, auth_headers: dict, dataset_with_queries: Dataset
    ):
        """Test getting query history"""
        response = client.get(
            "/api/query/history",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in q for q in data)
        assert all("query_type" in q for q in data)

    def test_get_query_history_filtered_by_dataset(
        self, client: TestClient, auth_headers: dict, dataset_with_queries: Dataset
    ):
        """Test getting query history filtered by dataset"""
        response = client.get(
            f"/api/query/history?dataset_id={dataset_with_queries.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(q["dataset_id"] == str(dataset_with_queries.id) for q in data)

    def test_get_query_history_empty(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting empty query history"""
        response = client.get(
            f"/api/query/history?dataset_id={uuid4()}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_specific_query(
        self, client: TestClient, auth_headers: dict, dataset_with_queries: Dataset
    ):
        """Test getting a specific query"""
        # First get the history to get a query ID
        history_response = client.get(
            "/api/query/history",
            headers=auth_headers
        )
        query_id = history_response.json()[0]["id"]

        # Get specific query
        response = client.get(
            f"/api/query/{query_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == query_id

    def test_get_query_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting non-existent query"""
        response = client.get(
            f"/api/query/{uuid4()}",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestQueryValidation:
    """Test query validation"""

    async def test_invalid_query_type(
        self, client: TestClient, auth_headers: dict, test_dataset: Dataset
    ):
        """Test invalid query type"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "invalid",
                "query": "SELECT * FROM df"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_empty_query(
        self, client: TestClient, auth_headers: dict, test_dataset: Dataset
    ):
        """Test empty query string"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "dataset_id": str(test_dataset.id),
                "query_type": "sql",
                "query": ""
            }
        )

        assert response.status_code == 422  # Validation error

    def test_missing_dataset_id(
        self, client: TestClient, auth_headers: dict
    ):
        """Test missing dataset_id"""
        response = client.post(
            "/api/query/execute",
            headers=auth_headers,
            json={
                "query_type": "sql",
                "query": "SELECT * FROM df"
            }
        )

        assert response.status_code == 422  # Validation error
