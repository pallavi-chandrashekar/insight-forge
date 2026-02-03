"""
Context Validation Engine
Performs multi-level validation on context files
"""
from typing import Dict, Any, List, Tuple, Optional, Set
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.dataset import Dataset


class ValidationResult:
    """Validation result with errors and warnings"""

    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.passed = True

    def add_error(
        self,
        code: str,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Add validation error"""
        self.errors.append({
            "code": code,
            "message": message,
            "field": field,
            "severity": "error",
            "details": details or {}
        })
        self.passed = False

    def add_warning(
        self,
        code: str,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Add validation warning"""
        self.warnings.append({
            "code": code,
            "message": message,
            "field": field,
            "severity": "warning",
            "details": details or {}
        })

    def get_status(self) -> str:
        """Get overall validation status"""
        if len(self.errors) > 0:
            return "failed"
        elif len(self.warnings) > 0:
            return "warning"
        else:
            return "passed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.get_status(),
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }


class ContextValidator:
    """
    Multi-level validation for context files.

    Validation Levels:
    1. Schema Validation (handled by ContextParser)
    2. Semantic Validation (dataset existence, column references)
    3. Circular Dependency Detection (for relationships)
    4. Business Rule Validation (SQL syntax)
    """

    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id

    async def validate(self, parsed_context: Dict[str, Any]) -> ValidationResult:
        """
        Perform complete validation on parsed context.

        Args:
            parsed_context: Parsed context data from ContextParser

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()

        # Level 1: Schema validation (already done by parser, but double-check)
        self._validate_schema(parsed_context, result)

        # Level 2: Semantic validation
        await self._validate_semantics(parsed_context, result)

        # Level 3: Circular dependency detection
        if parsed_context.get("context_type") == "multi_dataset":
            self._validate_relationships(parsed_context, result)

        # Level 4: Business rule validation
        self._validate_business_rules(parsed_context, result)

        return result

    def _validate_schema(
        self,
        parsed_context: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate basic schema requirements"""
        # Check name format
        name = parsed_context.get("name", "")
        if not name or len(name) < 3 or len(name) > 100:
            result.add_error(
                "INVALID_NAME",
                f"Context name must be 3-100 characters, got: {len(name)}",
                field="name"
            )

        # Check description length
        description = parsed_context.get("description", "")
        if not description or len(description) < 10:
            result.add_error(
                "INVALID_DESCRIPTION",
                f"Description must be at least 10 characters, got: {len(description)}",
                field="description"
            )

        # Check context_type
        context_type = parsed_context.get("context_type")
        if context_type not in ["single_dataset", "multi_dataset"]:
            result.add_error(
                "INVALID_CONTEXT_TYPE",
                f"Invalid context_type: {context_type}",
                field="context_type"
            )

    async def _validate_semantics(
        self,
        parsed_context: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate semantic correctness (dataset references, columns, etc.)"""
        datasets = parsed_context.get("datasets", [])

        # Fetch all dataset IDs from database for this user
        dataset_ids = []
        dataset_schemas = {}

        for ds_def in datasets:
            dataset_id_str = ds_def.get("dataset_id")
            if not dataset_id_str:
                result.add_error(
                    "MISSING_DATASET_ID",
                    f"Dataset '{ds_def.get('id')}' missing dataset_id",
                    field="datasets"
                )
                continue

            try:
                dataset_id = UUID(dataset_id_str)
                dataset_ids.append(dataset_id)
            except (ValueError, TypeError):
                result.add_error(
                    "INVALID_DATASET_ID",
                    f"Invalid UUID for dataset '{ds_def.get('id')}': {dataset_id_str}",
                    field="datasets"
                )
                continue

        # Check if datasets exist in database
        if dataset_ids:
            stmt = select(Dataset).where(
                Dataset.id.in_(dataset_ids),
                Dataset.user_id == self.user_id
            )
            db_result = await self.db.execute(stmt)
            existing_datasets = db_result.scalars().all()

            existing_ids = {str(ds.id) for ds in existing_datasets}
            for ds in existing_datasets:
                dataset_schemas[str(ds.id)] = ds.schema

            # Check for missing datasets
            for ds_def in datasets:
                ds_id = ds_def.get("dataset_id")
                if ds_id not in existing_ids:
                    result.add_error(
                        "DATASET_NOT_FOUND",
                        f"Dataset '{ds_def.get('name')}' with ID {ds_id} not found or not owned by user",
                        field="datasets",
                        details={"dataset_id": ds_id}
                    )

        # Validate column references in relationships
        await self._validate_column_references(
            parsed_context,
            dataset_schemas,
            result
        )

    async def _validate_column_references(
        self,
        parsed_context: Dict[str, Any],
        dataset_schemas: Dict[str, Dict],
        result: ValidationResult
    ):
        """Validate that column references in relationships exist"""
        relationships = parsed_context.get("relationships", [])
        if not relationships:
            return

        datasets = parsed_context.get("datasets", [])
        dataset_id_map = {
            ds["id"]: ds["dataset_id"] for ds in datasets
        }

        for rel in relationships:
            left_ds_id = rel.get("left_dataset")
            right_ds_id = rel.get("right_dataset")

            # Check if datasets referenced in relationship exist
            if left_ds_id not in dataset_id_map:
                result.add_error(
                    "UNKNOWN_DATASET_IN_RELATIONSHIP",
                    f"Relationship '{rel.get('id')}' references unknown dataset: {left_ds_id}",
                    field="relationships"
                )
                continue

            if right_ds_id not in dataset_id_map:
                result.add_error(
                    "UNKNOWN_DATASET_IN_RELATIONSHIP",
                    f"Relationship '{rel.get('id')}' references unknown dataset: {right_ds_id}",
                    field="relationships"
                )
                continue

            # Get actual dataset IDs
            left_real_id = dataset_id_map[left_ds_id]
            right_real_id = dataset_id_map[right_ds_id]

            # Check column existence
            left_schema = dataset_schemas.get(left_real_id, {})
            right_schema = dataset_schemas.get(right_real_id, {})

            conditions = rel.get("conditions", [])
            for condition in conditions:
                left_col = condition.get("left_column")
                right_col = condition.get("right_column")

                # Validate left column exists
                if left_schema and left_col:
                    left_columns = [c["name"] for c in left_schema.get("columns", [])]
                    if left_col not in left_columns:
                        result.add_error(
                            "COLUMN_NOT_FOUND",
                            f"Column '{left_col}' not found in dataset '{left_ds_id}'",
                            field="relationships",
                            details={
                                "relationship": rel.get("id"),
                                "dataset": left_ds_id,
                                "column": left_col
                            }
                        )

                # Validate right column exists
                if right_schema and right_col:
                    right_columns = [c["name"] for c in right_schema.get("columns", [])]
                    if right_col not in right_columns:
                        result.add_error(
                            "COLUMN_NOT_FOUND",
                            f"Column '{right_col}' not found in dataset '{right_ds_id}'",
                            field="relationships",
                            details={
                                "relationship": rel.get("id"),
                                "dataset": right_ds_id,
                                "column": right_col
                            }
                        )

    def _validate_relationships(
        self,
        parsed_context: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate relationships and detect circular dependencies"""
        relationships = parsed_context.get("relationships", [])
        if not relationships:
            # Multi-dataset context without relationships
            result.add_warning(
                "NO_RELATIONSHIPS",
                "Multi-dataset context has no relationships defined",
                field="relationships"
            )
            return

        # Validate join types
        valid_join_types = ["inner", "left", "right", "outer"]
        for rel in relationships:
            join_type = rel.get("join_type")
            if join_type not in valid_join_types:
                result.add_error(
                    "INVALID_JOIN_TYPE",
                    f"Invalid join_type in relationship '{rel.get('id')}': {join_type}",
                    field="relationships"
                )

        # Check for circular dependencies
        self._detect_circular_dependencies(relationships, result)

        # Check for duplicate relationship definitions
        self._check_duplicate_relationships(relationships, result)

    def _detect_circular_dependencies(
        self,
        relationships: List[Dict],
        result: ValidationResult
    ):
        """Detect circular dependencies in relationship graph"""
        # Build adjacency list
        graph: Dict[str, Set[str]] = {}

        for rel in relationships:
            left = rel.get("left_dataset")
            right = rel.get("right_dataset")

            if left not in graph:
                graph[left] = set()
            graph[left].add(right)

        # DFS to detect cycles
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    cycle = has_cycle(neighbor, visited, rec_stack)
                    if cycle:
                        return [node] + cycle
                elif neighbor in rec_stack:
                    return [node, neighbor]

            rec_stack.remove(node)
            return None

        visited: Set[str] = set()
        for node in graph:
            if node not in visited:
                rec_stack: Set[str] = set()
                cycle = has_cycle(node, visited, rec_stack)
                if cycle:
                    result.add_error(
                        "CIRCULAR_DEPENDENCY",
                        f"Circular dependency detected in relationships: {' → '.join(cycle)}",
                        field="relationships",
                        details={"cycle": cycle}
                    )
                    break

    def _check_duplicate_relationships(
        self,
        relationships: List[Dict],
        result: ValidationResult
    ):
        """Check for duplicate relationship definitions"""
        seen_pairs: Set[Tuple[str, str]] = set()

        for rel in relationships:
            left = rel.get("left_dataset")
            right = rel.get("right_dataset")
            pair = (left, right)

            if pair in seen_pairs:
                result.add_warning(
                    "DUPLICATE_RELATIONSHIP",
                    f"Duplicate relationship between '{left}' and '{right}'",
                    field="relationships",
                    details={"left": left, "right": right}
                )

            seen_pairs.add(pair)

    def _validate_business_rules(
        self,
        parsed_context: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate business rules syntax"""
        business_rules = parsed_context.get("business_rules", [])
        if not business_rules:
            return

        for rule in business_rules:
            # Validate severity
            severity = rule.get("severity")
            if severity not in ["error", "warning", "info"]:
                result.add_error(
                    "INVALID_SEVERITY",
                    f"Invalid severity in rule '{rule.get('id')}': {severity}",
                    field="business_rules"
                )

            # Validate rule_type
            rule_type = rule.get("rule_type")
            if rule_type not in ["validation", "quality", "constraint"]:
                result.add_error(
                    "INVALID_RULE_TYPE",
                    f"Invalid rule_type in rule '{rule.get('id')}': {rule_type}",
                    field="business_rules"
                )

            # Basic SQL syntax check (condition must be non-empty)
            condition = rule.get("condition", "").strip()
            if not condition:
                result.add_error(
                    "EMPTY_RULE_CONDITION",
                    f"Rule '{rule.get('id')}' has empty condition",
                    field="business_rules"
                )
