"""
Context Service
Handles CRUD operations for context files
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.context import Context, ContextType, ContextStatus
from app.services.context_parser import ContextParser, ContextParseError, ContextSerializer
from app.services.context_validator import ContextValidator


class ContextServiceError(Exception):
    """Raised when context service operations fail"""
    pass


class ContextService:
    """Service for managing context files"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _auto_populate_dataset_context_ids(self, context: Context) -> None:
        """
        Auto-populate context_id in datasets when context is created/updated.

        Strategy:
        - Extract dataset IDs from context.datasets JSON
        - Update matching datasets to point to this context
        - Only update datasets owned by same user (security)

        Args:
            context: Context object with datasets JSON
        """
        from app.models.dataset import Dataset
        from sqlalchemy import update

        if not context.datasets:
            return

        # Extract UUIDs from JSON
        dataset_ids = []
        for ds in context.datasets:
            dataset_id = ds.get("dataset_id")
            if dataset_id:
                try:
                    dataset_ids.append(UUID(dataset_id))
                except (ValueError, TypeError):
                    continue  # Skip invalid UUIDs

        if not dataset_ids:
            return

        # Bulk update all matching datasets
        stmt = (
            update(Dataset)
            .where(Dataset.id.in_(dataset_ids))
            .where(Dataset.user_id == context.user_id)  # Security: only own datasets
            .values(context_id=context.id)
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def create_context(
        self,
        user_id: UUID,
        content: str,
        validate: bool = True,
        dataset_id: Optional[UUID] = None
    ) -> Context:
        """
        Create a new context from file content.

        Supports TWO formats:
        1. Structured: YAML frontmatter + Markdown
        2. Simple: Plain markdown (requires dataset_id parameter)

        Args:
            user_id: User ID
            content: Full context file content
            validate: Whether to validate context (default: True)
            dataset_id: Dataset ID (required for simple format, optional for structured)

        Returns:
            Created Context object

        Raises:
            ContextServiceError: If creation fails
        """
        try:
            # Parse context file (handles both formats)
            dataset_id_str = str(dataset_id) if dataset_id else None
            parsed = ContextParser.parse_and_validate(content, dataset_id=dataset_id_str)
        except ContextParseError as e:
            raise ContextServiceError(f"Context parsing failed: {str(e)}")

        # Check for duplicate (same name + version)
        existing = await self.get_by_name_version(
            user_id,
            parsed["name"],
            parsed["version"]
        )
        if existing:
            raise ContextServiceError(
                f"Context '{parsed['name']}' version '{parsed['version']}' already exists"
            )

        # Validate if requested
        validation_status = "passed"
        validation_errors = None
        validation_warnings = None

        if validate:
            validator = ContextValidator(self.db, user_id)
            validation_result = await validator.validate(parsed)

            validation_status = validation_result.get_status()
            if validation_result.errors:
                validation_errors = validation_result.errors
            if validation_result.warnings:
                validation_warnings = validation_result.warnings

            # Block creation if validation failed with errors
            if validation_status == "failed":
                raise ContextServiceError(
                    f"Context validation failed: {len(validation_result.errors)} errors found",
                    validation_result.to_dict()
                )

        # Create context object
        context = Context(
            user_id=user_id,
            name=parsed["name"],
            version=parsed["version"],
            description=parsed["description"],
            context_type=ContextType(parsed["context_type"]),
            status=ContextStatus(parsed.get("status", "active")),
            tags=parsed.get("tags"),
            category=parsed.get("category"),
            owner=parsed.get("owner"),
            created_by_email=parsed.get("created_by_email"),
            markdown_content=parsed["markdown_content"],
            parsed_yaml=parsed["parsed_yaml"],
            datasets=parsed["datasets"],
            relationships=parsed.get("relationships"),
            metrics=parsed.get("metrics"),
            business_rules=parsed.get("business_rules"),
            filters=parsed.get("filters"),
            settings=parsed.get("settings"),
            data_model=parsed.get("data_model"),
            glossary=parsed.get("glossary"),
            validation_status=validation_status,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            file_size_bytes=parsed["file_size_bytes"],
            file_hash=parsed["file_hash"]
        )

        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)

        # Auto-populate dataset FKs
        await self._auto_populate_dataset_context_ids(context)

        return context

    async def get_context(self, context_id: UUID, user_id: UUID) -> Optional[Context]:
        """
        Get context by ID.

        Args:
            context_id: Context ID
            user_id: User ID (for authorization)

        Returns:
            Context object or None
        """
        stmt = select(Context).where(
            and_(
                Context.id == context_id,
                Context.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_version(
        self,
        user_id: UUID,
        name: str,
        version: str
    ) -> Optional[Context]:
        """Get context by name and version"""
        stmt = select(Context).where(
            and_(
                Context.user_id == user_id,
                Context.name == name,
                Context.version == version
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_contexts(
        self,
        user_id: UUID,
        context_type: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Context]:
        """
        List contexts with filters.

        Args:
            user_id: User ID
            context_type: Filter by context_type
            category: Filter by category
            status: Filter by status
            tags: Filter by tags (any match)
            search: Search in name/description
            skip: Pagination offset
            limit: Maximum results

        Returns:
            List of Context objects
        """
        stmt = select(Context).where(Context.user_id == user_id)

        # Apply filters
        if context_type:
            stmt = stmt.where(Context.context_type == context_type)

        if category:
            stmt = stmt.where(Context.category == category)

        if status:
            stmt = stmt.where(Context.status == status)

        if tags:
            # Match any of the provided tags
            stmt = stmt.where(Context.tags.op('?|')(tags))

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Context.name.ilike(search_pattern),
                    Context.description.ilike(search_pattern)
                )
            )

        # Order and paginate
        stmt = stmt.order_by(Context.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_context(
        self,
        context_id: UUID,
        user_id: UUID,
        content: str,
        validate: bool = True,
        dataset_id: Optional[UUID] = None
    ) -> Context:
        """
        Update context with new content.

        Supports both structured (YAML) and simple (plain markdown) formats.

        Args:
            context_id: Context ID
            user_id: User ID
            content: New context file content
            validate: Whether to validate
            dataset_id: Dataset ID (required for simple format)

        Returns:
            Updated Context object

        Raises:
            ContextServiceError: If update fails
        """
        # Get existing context
        context = await self.get_context(context_id, user_id)
        if not context:
            raise ContextServiceError("Context not found")

        # Parse new content (handles both formats)
        try:
            dataset_id_str = str(dataset_id) if dataset_id else None
            parsed = ContextParser.parse_and_validate(content, dataset_id=dataset_id_str)
        except ContextParseError as e:
            raise ContextServiceError(f"Context parsing failed: {str(e)}")

        # Validate if requested
        validation_status = "passed"
        validation_errors = None
        validation_warnings = None

        if validate:
            validator = ContextValidator(self.db, user_id)
            validation_result = await validator.validate(parsed)

            validation_status = validation_result.get_status()
            if validation_result.errors:
                validation_errors = validation_result.errors
            if validation_result.warnings:
                validation_warnings = validation_result.warnings

            if validation_status == "failed":
                raise ContextServiceError(
                    f"Context validation failed: {len(validation_result.errors)} errors found",
                    validation_result.to_dict()
                )

        # Update context fields
        context.name = parsed["name"]
        context.version = parsed["version"]
        context.description = parsed["description"]
        context.context_type = ContextType(parsed["context_type"])
        context.status = ContextStatus(parsed.get("status", context.status.value))
        context.tags = parsed.get("tags")
        context.category = parsed.get("category")
        context.owner = parsed.get("owner")
        context.created_by_email = parsed.get("created_by_email")
        context.markdown_content = parsed["markdown_content"]
        context.parsed_yaml = parsed["parsed_yaml"]
        context.datasets = parsed["datasets"]
        context.relationships = parsed.get("relationships")
        context.metrics = parsed.get("metrics")
        context.business_rules = parsed.get("business_rules")
        context.filters = parsed.get("filters")
        context.settings = parsed.get("settings")
        context.data_model = parsed.get("data_model")
        context.glossary = parsed.get("glossary")
        context.validation_status = validation_status
        context.validation_errors = validation_errors
        context.validation_warnings = validation_warnings
        context.file_size_bytes = parsed["file_size_bytes"]
        context.file_hash = parsed["file_hash"]

        await self.db.commit()
        await self.db.refresh(context)

        # Update dataset FKs (in case datasets changed)
        await self._auto_populate_dataset_context_ids(context)

        return context

    async def delete_context(self, context_id: UUID, user_id: UUID) -> bool:
        """
        Delete context.

        Args:
            context_id: Context ID
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        context = await self.get_context(context_id, user_id)
        if not context:
            return False

        await self.db.delete(context)
        await self.db.commit()
        return True

    async def get_context_full_content(
        self,
        context_id: UUID,
        user_id: UUID
    ) -> Optional[str]:
        """
        Get full context file content (YAML + Markdown).

        Args:
            context_id: Context ID
            user_id: User ID

        Returns:
            Full context file content or None
        """
        context = await self.get_context(context_id, user_id)
        if not context:
            return None

        # Reconstruct full file
        return ContextSerializer.serialize(
            context.parsed_yaml,
            context.markdown_content
        )

    async def search_glossary(
        self,
        user_id: UUID,
        term: str
    ) -> List[Dict[str, Any]]:
        """
        Search glossary terms across all contexts.

        Args:
            user_id: User ID
            term: Search term

        Returns:
            List of matching glossary entries with context info
        """
        stmt = select(Context).where(
            and_(
                Context.user_id == user_id,
                Context.glossary.isnot(None)
            )
        )

        result = await self.db.execute(stmt)
        contexts = result.scalars().all()

        matches = []
        search_term = term.lower()

        for context in contexts:
            if not context.glossary:
                continue

            for entry in context.glossary:
                entry_term = entry.get("term", "").lower()
                synonyms = [s.lower() for s in entry.get("synonyms", [])]

                if search_term in entry_term or any(search_term in syn for syn in synonyms):
                    matches.append({
                        "context_id": str(context.id),
                        "context_name": context.name,
                        "term": entry.get("term"),
                        "definition": entry.get("definition"),
                        "synonyms": entry.get("synonyms"),
                        "related_columns": entry.get("related_columns"),
                        "examples": entry.get("examples")
                    })

        return matches

    async def get_metrics_by_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get all metrics applicable to a specific dataset.

        Args:
            user_id: User ID
            dataset_id: Dataset ID

        Returns:
            List of metrics with context info
        """
        dataset_id_str = str(dataset_id)

        stmt = select(Context).where(
            and_(
                Context.user_id == user_id,
                Context.metrics.isnot(None)
            )
        )

        result = await self.db.execute(stmt)
        contexts = result.scalars().all()

        metrics = []

        for context in contexts:
            if not context.metrics:
                continue

            # Check if this context includes the dataset
            context_dataset_ids = [ds.get("dataset_id") for ds in context.datasets]
            if dataset_id_str not in context_dataset_ids:
                continue

            for metric in context.metrics:
                # Check if metric applies to this dataset
                metric_datasets = metric.get("datasets", [])
                if not metric_datasets:  # Applies to all
                    metrics.append({
                        "context_id": str(context.id),
                        "context_name": context.name,
                        **metric
                    })
                else:
                    # Check if dataset is in the metric's dataset list
                    for ds_id in context.datasets:
                        if ds_id["dataset_id"] == dataset_id_str and ds_id["id"] in metric_datasets:
                            metrics.append({
                                "context_id": str(context.id),
                                "context_name": context.name,
                                **metric
                            })
                            break

        return metrics

    async def get_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get statistics about user's contexts"""
        stmt = select(
            func.count(Context.id).label("total"),
            func.count(Context.id).filter(Context.context_type == ContextType.SINGLE_DATASET).label("single_dataset"),
            func.count(Context.id).filter(Context.context_type == ContextType.MULTI_DATASET).label("multi_dataset"),
            func.count(Context.id).filter(Context.status == ContextStatus.ACTIVE).label("active"),
            func.count(Context.id).filter(Context.validation_status == "failed").label("failed_validation")
        ).where(Context.user_id == user_id)

        result = await self.db.execute(stmt)
        row = result.one()

        return {
            "total_contexts": row.total,
            "single_dataset_contexts": row.single_dataset,
            "multi_dataset_contexts": row.multi_dataset,
            "active_contexts": row.active,
            "failed_validation": row.failed_validation
        }

    async def find_active_context_by_dataset(
        self,
        dataset_id: UUID,
        user_id: UUID
    ) -> Optional[Context]:
        """
        Find active context using FK relationship (10x faster than Phase 1).

        Performance: ~5ms vs ~50ms in Phase 1

        Args:
            dataset_id: Dataset ID
            user_id: User ID for authorization

        Returns:
            Active Context or None
        """
        from app.models.dataset import Dataset

        # Direct FK lookup with JOIN (~5ms)
        stmt = (
            select(Context)
            .join(Dataset, Dataset.context_id == Context.id)
            .where(
                and_(
                    Dataset.id == dataset_id,
                    Dataset.user_id == user_id,
                    Context.status == ContextStatus.ACTIVE
                )
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_context_metadata_for_dataset(
        self,
        context: Context,
        dataset_id: UUID
    ) -> Dict[str, Any]:
        """
        Extract context metadata relevant for a specific dataset.

        Args:
            context: Context object
            dataset_id: Dataset ID to extract metadata for

        Returns:
            Dictionary with formatted metadata for LLM prompt:
            {
                "name": "Context name",
                "description": "Context description",
                "columns": [{"name": "col", "business_name": "Business Name", "description": "..."}],
                "metrics": [{"id": "metric1", "name": "Metric Name", "expression": "AVG(col)"}],
                "glossary": [{"term": "Term", "definition": "...", "related_columns": [...]}],
                "filters": [{"id": "filter1", "name": "Filter Name", "condition": "..."}]
            }
        """
        dataset_id_str = str(dataset_id)

        # Find the specific dataset in context
        dataset_info = None
        for ds in context.datasets:
            if ds.get("dataset_id") == dataset_id_str:
                dataset_info = ds
                break

        metadata = {
            "name": context.name,
            "description": context.description,
            "columns": [],
            "metrics": [],
            "glossary": [],
            "filters": []
        }

        # Extract column metadata with business names and descriptions
        if dataset_info and dataset_info.get("columns"):
            for col in dataset_info["columns"]:
                col_meta = {
                    "name": col.get("name"),
                    "business_name": col.get("business_name"),
                    "description": col.get("description"),
                    "data_type": col.get("data_type")
                }
                metadata["columns"].append(col_meta)

        # Extract metrics that apply to this dataset
        if context.metrics:
            for metric in context.metrics:
                # Check if metric applies to this dataset
                metric_datasets = metric.get("datasets", [])
                if not metric_datasets:  # Applies to all datasets
                    metadata["metrics"].append(metric)
                else:
                    # Find matching dataset by id
                    for ds in context.datasets:
                        if ds.get("dataset_id") == dataset_id_str and ds.get("id") in metric_datasets:
                            metadata["metrics"].append(metric)
                            break

        # Extract glossary terms
        if context.glossary:
            metadata["glossary"] = context.glossary

        # Extract filters
        if context.filters:
            metadata["filters"] = context.filters

        return metadata
