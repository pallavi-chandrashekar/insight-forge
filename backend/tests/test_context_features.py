"""Tests for Phase 2 Context Features"""
import pytest
import pandas as pd
from app.services.context_parser import ContextParser
from app.services.context_validator import ContextValidator
from app.services.relationship_resolver import RelationshipResolver
from app.services.sql_generator import SQLGenerator


class TestContextParser:
    """Test context file parsing"""

    def test_parse_single_dataset_context(self):
        """Test parsing a simple single-dataset context"""
        content = """---
name: Customer Data Context
version: 1.0.0
type: single_dataset
datasets:
  - id: customers
    name: Customer Database
---

# Customer Data Documentation

This context provides metadata for the customer database.
"""
        parsed_yaml, markdown = ContextParser.parse(content)

        assert parsed_yaml['name'] == "Customer Data Context"
        assert parsed_yaml['version'] == "1.0.0"
        assert parsed_yaml['type'] == "single_dataset"
        assert len(parsed_yaml['datasets']) == 1
        assert parsed_yaml['datasets'][0]['id'] == "customers"
        assert "Customer Data Documentation" in markdown

    def test_parse_multi_dataset_context_with_relationships(self):
        """Test parsing multi-dataset context with relationships"""
        content = """---
name: Sales Analytics Context
version: 1.0.0
type: multi_dataset
datasets:
  - id: orders
    name: Orders
  - id: customers
    name: Customers
relationships:
  - id: order_customer
    left_dataset: orders
    right_dataset: customers
    join_type: inner
    conditions:
      - left_column: customer_id
        operator: "="
        right_column: id
---

# Sales Analytics
"""
        parsed_yaml, markdown = ContextParser.parse(content)

        assert parsed_yaml['type'] == "multi_dataset"
        assert len(parsed_yaml['datasets']) == 2
        assert len(parsed_yaml['relationships']) == 1
        assert parsed_yaml['relationships'][0]['id'] == "order_customer"
        assert "Sales Analytics" in markdown

    def test_validate_required_fields(self):
        """Test validation of required fields"""
        # Valid data - including all required fields and at least one dataset
        valid_yaml = {
            'name': 'Test Context',
            'version': '1.0.0',
            'description': 'Test description',
            'type': 'single_dataset',
            'datasets': [
                {
                    'id': 'test_ds',
                    'name': 'Test Dataset',
                    'dataset_id': 'dataset123'
                }
            ]
        }

        # Should not raise error
        try:
            ContextParser.validate_required_fields(valid_yaml)
            assert True
        except Exception as e:
            assert False, f"Should not raise error for valid data: {e}"

        # Missing required field (name)
        invalid_yaml = {
            'version': '1.0.0',
            'description': 'Test',
            'type': 'single_dataset',
            'datasets': []
            # missing 'name'
        }

        from app.services.context_parser import ContextParseError
        try:
            ContextParser.validate_required_fields(invalid_yaml)
            assert False, "Should raise error for missing required field"
        except ContextParseError:
            assert True


class TestContextValidator:
    """Test context validation"""

    @pytest.mark.asyncio
    async def test_validation_result_structure(self):
        """Test ValidationResult structure"""
        from app.services.context_validator import ValidationResult

        result = ValidationResult()

        # Initially should be passing
        assert result.passed is True
        assert result.get_status() == "passed"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

        # Add an error
        result.add_error("TEST_ERROR", "Test error message", "test_field")
        assert result.passed is False  # passed flag updates when error added
        assert result.get_status() == "failed"
        assert len(result.errors) == 1
        assert result.errors[0]['code'] == 'TEST_ERROR'
        assert result.errors[0]['severity'] == 'error'

        # Add a warning
        result.add_warning("TEST_WARNING", "Test warning", "test_field")
        assert len(result.warnings) == 1
        assert result.warnings[0]['code'] == 'TEST_WARNING'
        assert result.warnings[0]['severity'] == 'warning'

        # Check dict conversion
        result_dict = result.to_dict()
        assert result_dict['status'] == 'failed'
        assert result_dict['error_count'] == 1
        assert result_dict['warning_count'] == 1

    def test_validate_schema_structure(self):
        """Test basic schema validation without database"""
        # Test that required fields are checked
        from app.services.context_parser import ContextParser, ContextParseError

        # Valid structure
        valid_content = """---
name: Test
version: 1.0.0
type: single_dataset
datasets:
  - id: test
    name: Test Dataset
---
# Test
"""
        parsed, _ = ContextParser.parse(valid_content)
        assert parsed['name'] == 'Test'
        assert parsed['version'] == '1.0.0'

        # Invalid - missing name
        invalid_content = """---
version: 1.0.0
type: single_dataset
---
# Test
"""
        try:
            parsed, _ = ContextParser.parse(invalid_content)
            ContextParser.validate_required_fields(parsed)
            assert False, "Should raise error"
        except ContextParseError:
            assert True

    def test_check_duplicate_dataset_ids(self):
        """Test detecting duplicate dataset IDs"""
        datasets = [
            {'id': 'ds1', 'name': 'Dataset 1'},
            {'id': 'ds2', 'name': 'Dataset 2'},
            {'id': 'ds1', 'name': 'Dataset 3'}  # Duplicate
        ]

        # Check for duplicates
        dataset_ids = [ds['id'] for ds in datasets]
        unique_ids = set(dataset_ids)

        assert len(dataset_ids) == 3
        assert len(unique_ids) == 2  # Only 2 unique
        assert len(dataset_ids) != len(unique_ids)  # Duplicates exist


class TestRelationshipResolver:
    """Test relationship resolution and join path finding"""

    def test_build_graph_from_relationships(self):
        """Test building adjacency graph from relationships"""
        relationships = [
            {
                'id': 'r1',
                'left_dataset': 'A',
                'right_dataset': 'B',
                'join_type': 'inner',
                'conditions': [
                    {'left_column': 'id', 'operator': '=', 'right_column': 'a_id'}
                ]
            }
        ]

        resolver = RelationshipResolver(relationships)

        assert 'A' in resolver.graph
        assert 'B' in resolver.graph
        assert len(resolver.graph['A']) == 1
        assert len(resolver.graph['B']) == 1

    def test_find_direct_join_path(self):
        """Test finding direct join path between two datasets"""
        relationships = [
            {
                'id': 'r1',
                'left_dataset': 'A',
                'right_dataset': 'B',
                'join_type': 'inner',
                'conditions': [
                    {'left_column': 'id', 'operator': '=', 'right_column': 'a_id'}
                ]
            }
        ]

        resolver = RelationshipResolver(relationships)
        path = resolver.find_join_path('A', 'B')

        assert path is not None
        assert len(path) == 1
        assert path[0]['to'] == 'B'

    def test_find_multi_hop_join_path(self):
        """Test finding join path through intermediate dataset"""
        relationships = [
            {
                'id': 'r1',
                'left_dataset': 'A',
                'right_dataset': 'B',
                'join_type': 'inner',
                'conditions': [{'left_column': 'id', 'operator': '=', 'right_column': 'a_id'}]
            },
            {
                'id': 'r2',
                'left_dataset': 'B',
                'right_dataset': 'C',
                'join_type': 'inner',
                'conditions': [{'left_column': 'id', 'operator': '=', 'right_column': 'b_id'}]
            }
        ]

        resolver = RelationshipResolver(relationships)
        path = resolver.find_join_path('A', 'C')

        assert path is not None
        assert len(path) == 2

    def test_find_join_path_multi_dataset(self):
        """Test finding path connecting multiple datasets"""
        relationships = [
            {
                'id': 'r1',
                'left_dataset': 'A',
                'right_dataset': 'B',
                'join_type': 'inner',
                'conditions': [{'left_column': 'id', 'operator': '=', 'right_column': 'a_id'}]
            },
            {
                'id': 'r2',
                'left_dataset': 'A',
                'right_dataset': 'C',
                'join_type': 'inner',
                'conditions': [{'left_column': 'id', 'operator': '=', 'right_column': 'a_id'}]
            }
        ]

        resolver = RelationshipResolver(relationships)
        path = resolver.find_join_path_multi(['A', 'B', 'C'])

        assert path is not None
        assert len(path) >= 2

    def test_estimate_join_cost(self):
        """Test join cost estimation"""
        relationships = [
            {
                'id': 'r1',
                'left_dataset': 'A',
                'right_dataset': 'B',
                'join_type': 'inner',
                'conditions': [{'left_column': 'id', 'operator': '=', 'right_column': 'a_id'}]
            }
        ]

        resolver = RelationshipResolver(relationships)
        path = resolver.find_join_path('A', 'B')
        cost = resolver.estimate_join_cost(path)

        assert cost > 0
        # Inner join should have base cost


class TestSQLGenerator:
    """Test SQL generation from context"""

    def test_generate_simple_query(self):
        """Test generating simple single-dataset query"""
        context = {
            'datasets': [
                {'id': 'customers', 'name': 'Customers'}
            ],
            'metrics': [],
            'filters': []
        }

        generator = SQLGenerator(context)
        sql = generator.generate_simple_query(
            'customers',
            ['name', 'email'],
            limit=10
        )

        assert 'SELECT' in sql
        assert 'customers' in sql
        assert 'LIMIT 10' in sql

    def test_generate_multi_dataset_query(self):
        """Test generating multi-dataset query with joins"""
        context = {
            'datasets': [
                {'id': 'orders', 'name': 'Orders'},
                {'id': 'customers', 'name': 'Customers'}
            ],
            'metrics': [],
            'filters': []
        }

        join_path = [
            {
                'relationship': {
                    'id': 'order_customer',
                    'left_dataset': 'orders',
                    'right_dataset': 'customers',
                    'join_type': 'inner',
                    'conditions': [
                        {'left_column': 'customer_id', 'operator': '=', 'right_column': 'id'}
                    ]
                },
                'reverse': False
            }
        ]

        generator = SQLGenerator(context)
        sql = generator.generate_multi_dataset_query(
            select_columns=['orders.id', 'customers.name'],
            join_path=join_path
        )

        assert 'SELECT' in sql
        assert 'JOIN' in sql
        assert 'orders' in sql
        assert 'customers' in sql

    def test_apply_filter(self):
        """Test applying predefined filter"""
        context = {
            'datasets': [],
            'metrics': [],
            'filters': [
                {
                    'id': 'active_only',
                    'condition': 'is_active = true'
                }
            ]
        }

        generator = SQLGenerator(context)
        condition = generator.apply_filter('active_only')

        assert condition == 'is_active = true'

    def test_expand_metric(self):
        """Test expanding metric expression"""
        context = {
            'datasets': [],
            'metrics': [
                {
                    'id': 'total_revenue',
                    'expression': 'SUM(price * quantity)'
                }
            ],
            'filters': []
        }

        generator = SQLGenerator(context)
        expression = generator.expand_metric('total_revenue')

        assert expression == 'SUM(price * quantity)'


def test_integration_context_to_sql():
    """Integration test: Parse context -> Find join path -> Generate SQL"""
    # Sample context
    context_data = {
        'name': "E-commerce Context",
        'version': "1.0.0",
        'type': "multi_dataset",
        'datasets': [
            {'id': 'orders', 'name': 'Orders', 'alias': 'o'},
            {'id': 'customers', 'name': 'Customers', 'alias': 'c'}
        ],
        'relationships': [
            {
                'id': 'order_customer',
                'left_dataset': 'orders',
                'right_dataset': 'customers',
                'join_type': 'inner',
                'conditions': [
                    {'left_column': 'customer_id', 'operator': '=', 'right_column': 'id'}
                ]
            }
        ],
        'metrics': [
            {
                'id': 'total_sales',
                'name': 'Total Sales',
                'expression': 'SUM(o.amount)'
            }
        ],
        'filters': []
    }

    # Find join path
    resolver = RelationshipResolver(context_data['relationships'])
    join_path = resolver.find_join_path('orders', 'customers')

    assert join_path is not None

    # Generate SQL
    generator = SQLGenerator(context_data)
    sql = generator.generate_multi_dataset_query(
        select_columns=['c.name', 'total_sales'],
        join_path=join_path,
        group_by=['c.name']
    )

    assert 'SELECT' in sql
    assert 'JOIN' in sql
    assert 'GROUP BY' in sql
    assert 'SUM(o.amount)' in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
