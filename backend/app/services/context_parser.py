"""
Context Parser Service
Parses YAML frontmatter and Markdown content from context files
"""
import yaml
import re
import hashlib
from typing import Dict, Any, Tuple, Optional
from datetime import datetime


class ContextParseError(Exception):
    """Raised when context file parsing fails"""
    pass


class ContextParser:
    """
    Parses context files with YAML frontmatter and Markdown content.

    Format:
    ---
    [YAML Frontmatter]
    ---
    [Markdown Content]
    """

    @classmethod
    def parse(cls, content: str, dataset_id: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
        """
        Parse context file into YAML frontmatter and markdown content.

        Supports TWO formats:
        1. Structured: YAML frontmatter + Markdown (original format)
        2. Simple: Plain markdown only (new simplified format)

        Args:
            content: Full context file content
            dataset_id: Required for simple format (optional for structured)

        Returns:
            Tuple of (parsed_yaml_dict, markdown_content)

        Raises:
            ContextParseError: If parsing fails
        """
        # Check if content starts with YAML frontmatter
        yaml_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n(.*)$',
            content,
            re.DOTALL
        )

        if yaml_match:
            # STRUCTURED FORMAT: Parse YAML frontmatter
            yaml_content = yaml_match.group(1)
            markdown_content = yaml_match.group(2).strip()

            # Parse YAML
            try:
                parsed_yaml = yaml.safe_load(yaml_content)
                if not isinstance(parsed_yaml, dict):
                    raise ContextParseError("YAML frontmatter must be a dictionary")
            except yaml.YAMLError as e:
                raise ContextParseError(f"YAML parsing error: {str(e)}")

            return parsed_yaml, markdown_content

        else:
            # SIMPLE FORMAT: Plain markdown - auto-generate structure
            # Supports both single and multi-dataset via markdown sections

            # Extract title from first header (if exists)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            name = title_match.group(1).strip() if title_match else "Dataset Context"

            # Extract first paragraph as short description
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
            short_description = paragraphs[0][:200] if paragraphs else "Dataset context documentation"

            # Check for multi-dataset markers using ## Dataset: or ## Datasets sections
            datasets_list = cls._extract_datasets_from_markdown(content, dataset_id)

            # Determine context type
            context_type = "multi_dataset" if len(datasets_list) > 1 else "single_dataset"

            # Extract relationships from markdown
            relationships = cls._extract_relationships_from_markdown(content)

            # Auto-generate YAML structure
            parsed_yaml = {
                "name": name,
                "version": "1.0.0",
                "description": short_description,
                "context_type": context_type,
                "status": "active",
                "datasets": datasets_list
            }

            # Add relationships if found
            if relationships:
                parsed_yaml["relationships"] = relationships

            return parsed_yaml, content

    @classmethod
    def _extract_datasets_from_markdown(cls, content: str, dataset_id: Optional[str] = None) -> list:
        """
        Extract dataset definitions from simple markdown format.

        Supports patterns like:
        ## Dataset: Orders (id: order-uuid)
        ## Dataset: Customers (id: customer-uuid)

        Or:
        ## Datasets
        - Orders (id: order-uuid)
        - Customers (id: customer-uuid)
        """
        datasets = []

        # Pattern 1: Individual headers "## Dataset: Name (id: uuid)"
        pattern1 = r'##\s+Dataset:\s+(.+?)\s+\(id:\s*([a-f0-9-]+)\)'
        matches1 = re.finditer(pattern1, content, re.IGNORECASE)

        for match in matches1:
            dataset_name = match.group(1).strip()
            dataset_uuid = match.group(2).strip()
            datasets.append({
                "id": dataset_name.lower().replace(" ", "_"),
                "name": dataset_name,
                "dataset_id": dataset_uuid
            })

        # Pattern 2: List under "## Datasets" header
        pattern2 = r'##\s+Datasets?\s*\n((?:[-*]\s+.+\n?)+)'
        match2 = re.search(pattern2, content, re.IGNORECASE)

        if match2:
            list_content = match2.group(1)
            # Extract each list item: "- Name (id: uuid)"
            item_pattern = r'[-*]\s+(.+?)\s+\(id:\s*([a-f0-9-]+)\)'
            for item_match in re.finditer(item_pattern, list_content):
                dataset_name = item_match.group(1).strip()
                dataset_uuid = item_match.group(2).strip()
                datasets.append({
                    "id": dataset_name.lower().replace(" ", "_"),
                    "name": dataset_name,
                    "dataset_id": dataset_uuid
                })

        # Fallback: If no datasets found and dataset_id provided, create single dataset
        if not datasets and dataset_id:
            # Extract name from first header
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            name = title_match.group(1).strip() if title_match else "Dataset Context"

            datasets.append({
                "id": "main",
                "name": name,
                "dataset_id": dataset_id
            })

        if not datasets:
            raise ContextParseError(
                "No datasets found. For simple format, either:\n"
                "1. Provide dataset_id parameter (single dataset), OR\n"
                "2. Use markdown syntax:\n"
                "   ## Dataset: Orders (id: your-uuid)\n"
                "   ## Dataset: Customers (id: your-uuid)"
            )

        return datasets

    @classmethod
    def _extract_relationships_from_markdown(cls, content: str) -> Optional[list]:
        """
        Extract relationship definitions from markdown.

        Supports pattern:
        ## Relationships
        - Orders → Customers via customer_id
        - Orders → Products via product_id
        """
        relationships = []

        # Find relationships section
        pattern = r'##\s+Relationships?\s*\n((?:[-*]\s+.+\n?)+)'
        match = re.search(pattern, content, re.IGNORECASE)

        if not match:
            return None

        list_content = match.group(1)

        # Extract each relationship: "- From → To via column" or "- From -> To via column"
        rel_pattern = r'[-*]\s+(\w+)\s*(?:→|->)\s*(\w+)\s+via\s+(\w+)'

        for rel_match in re.finditer(rel_pattern, list_content):
            from_dataset = rel_match.group(1).strip().lower()
            to_dataset = rel_match.group(2).strip().lower()
            column = rel_match.group(3).strip()

            relationships.append({
                "id": f"{from_dataset}_{to_dataset}",
                "name": f"{from_dataset.title()} to {to_dataset.title()}",
                "type": "many_to_one",
                "from_dataset": from_dataset,
                "from_column": column,
                "to_dataset": to_dataset,
                "to_column": column,
                "description": f"Relationship from {from_dataset} to {to_dataset} via {column}"
            })

        return relationships if relationships else None

    @staticmethod
    def validate_required_fields(parsed_yaml: Dict[str, Any]) -> None:
        """
        Validate that all required fields are present.

        Args:
            parsed_yaml: Parsed YAML dictionary

        Raises:
            ContextParseError: If required fields are missing
        """
        required_fields = ["name", "version", "description", "datasets"]

        missing_fields = [
            field for field in required_fields
            if field not in parsed_yaml or parsed_yaml[field] is None
        ]

        if missing_fields:
            raise ContextParseError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        # Validate datasets is a non-empty array
        datasets = parsed_yaml.get("datasets", [])
        if not isinstance(datasets, list) or len(datasets) == 0:
            raise ContextParseError("'datasets' must be a non-empty array")

        # Validate each dataset has required fields
        for i, dataset in enumerate(datasets):
            dataset_required = ["id", "name", "dataset_id"]
            missing = [
                field for field in dataset_required
                if field not in dataset or dataset[field] is None
            ]
            if missing:
                raise ContextParseError(
                    f"Dataset at index {i} missing required fields: {', '.join(missing)}"
                )

    @staticmethod
    def validate_version_format(version: str) -> bool:
        """
        Validate semantic version format (e.g., "1.0.0", "2.1.3").

        Args:
            version: Version string

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    @staticmethod
    def extract_datasets(parsed_yaml: Dict[str, Any]) -> list:
        """Extract and normalize datasets array"""
        return parsed_yaml.get("datasets", [])

    @staticmethod
    def extract_relationships(parsed_yaml: Dict[str, Any]) -> Optional[list]:
        """Extract relationships array (if present)"""
        return parsed_yaml.get("relationships")

    @staticmethod
    def extract_metrics(parsed_yaml: Dict[str, Any]) -> Optional[list]:
        """Extract metrics array (if present)"""
        return parsed_yaml.get("metrics")

    @staticmethod
    def extract_business_rules(parsed_yaml: Dict[str, Any]) -> Optional[list]:
        """Extract business_rules array (if present)"""
        return parsed_yaml.get("business_rules")

    @staticmethod
    def extract_filters(parsed_yaml: Dict[str, Any]) -> Optional[list]:
        """Extract filters array (if present)"""
        return parsed_yaml.get("filters")

    @staticmethod
    def extract_settings(parsed_yaml: Dict[str, Any]) -> Optional[Dict]:
        """Extract settings object (if present)"""
        return parsed_yaml.get("settings")

    @staticmethod
    def extract_data_model(parsed_yaml: Dict[str, Any]) -> Optional[Dict]:
        """Extract data_model object (if present)"""
        return parsed_yaml.get("data_model")

    @staticmethod
    def extract_glossary(parsed_yaml: Dict[str, Any]) -> Optional[list]:
        """Extract glossary array (if present)"""
        return parsed_yaml.get("glossary")

    @staticmethod
    def determine_context_type(parsed_yaml: Dict[str, Any]) -> str:
        """
        Determine context type based on content.

        Returns:
            "single_dataset" or "multi_dataset"
        """
        # Check if context_type is explicitly set
        if "context_type" in parsed_yaml:
            return parsed_yaml["context_type"]

        # Infer from content
        datasets = parsed_yaml.get("datasets", [])
        relationships = parsed_yaml.get("relationships", [])

        # If only 1 dataset and no relationships, it's single-dataset
        if len(datasets) == 1 and len(relationships) == 0:
            return "single_dataset"

        # Otherwise, it's multi-dataset
        return "multi_dataset"

    @staticmethod
    def calculate_file_hash(content: str) -> str:
        """
        Calculate SHA-256 hash of content for deduplication.

        Args:
            content: File content

        Returns:
            Hex string of SHA-256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def normalize_timestamps(parsed_yaml: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize timestamp fields to ISO 8601 format.

        Args:
            parsed_yaml: Parsed YAML dictionary

        Returns:
            Updated dictionary with normalized timestamps
        """
        timestamp_fields = ["created_at", "updated_at"]

        for field in timestamp_fields:
            if field in parsed_yaml and parsed_yaml[field]:
                value = parsed_yaml[field]
                # If it's a datetime object, convert to ISO string
                if isinstance(value, datetime):
                    parsed_yaml[field] = value.isoformat()
                # If it's a string, validate ISO format
                elif isinstance(value, str):
                    try:
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        # Invalid format, set to None
                        parsed_yaml[field] = None

        return parsed_yaml

    @classmethod
    def parse_and_validate(cls, content: str, dataset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse and perform basic validation on context file.

        Supports both structured (YAML) and simple (plain markdown) formats.

        Args:
            content: Full context file content
            dataset_id: Required for simple format (optional for structured)

        Returns:
            Dictionary with parsed components

        Raises:
            ContextParseError: If parsing or validation fails
        """
        # Parse YAML and Markdown (handles both formats)
        parsed_yaml, markdown_content = cls.parse(content, dataset_id=dataset_id)

        # Validate required fields
        cls.validate_required_fields(parsed_yaml)

        # Validate version format
        version = parsed_yaml.get("version", "")
        if not cls.validate_version_format(version):
            raise ContextParseError(
                f"Invalid version format: {version}. "
                "Expected semantic version (e.g., '1.0.0')"
            )

        # Normalize timestamps
        parsed_yaml = cls.normalize_timestamps(parsed_yaml)

        # Determine context type
        context_type = cls.determine_context_type(parsed_yaml)

        # Calculate file hash
        file_hash = cls.calculate_file_hash(content)

        # Extract all components
        result = {
            "parsed_yaml": parsed_yaml,
            "markdown_content": markdown_content,
            "name": parsed_yaml["name"],
            "version": parsed_yaml["version"],
            "description": parsed_yaml["description"],
            "context_type": context_type,
            "status": parsed_yaml.get("status", "active"),
            "tags": parsed_yaml.get("tags"),
            "category": parsed_yaml.get("category"),
            "owner": parsed_yaml.get("owner"),
            "created_by_email": parsed_yaml.get("created_by"),
            "datasets": cls.extract_datasets(parsed_yaml),
            "relationships": cls.extract_relationships(parsed_yaml),
            "metrics": cls.extract_metrics(parsed_yaml),
            "business_rules": cls.extract_business_rules(parsed_yaml),
            "filters": cls.extract_filters(parsed_yaml),
            "settings": cls.extract_settings(parsed_yaml),
            "data_model": cls.extract_data_model(parsed_yaml),
            "glossary": cls.extract_glossary(parsed_yaml),
            "file_hash": file_hash,
            "file_size_bytes": len(content.encode('utf-8')),
        }

        return result


class ContextSerializer:
    """
    Serializes context data back to YAML + Markdown format.
    """

    @staticmethod
    def serialize(parsed_yaml: Dict[str, Any], markdown_content: str) -> str:
        """
        Serialize parsed YAML and markdown back to context file format.

        Args:
            parsed_yaml: Parsed YAML dictionary
            markdown_content: Markdown content

        Returns:
            Full context file content
        """
        # Convert to YAML
        yaml_str = yaml.dump(
            parsed_yaml,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )

        # Combine with markdown
        return f"---\n{yaml_str}---\n\n{markdown_content}"

    @staticmethod
    def update_version(content: str, new_version: str) -> str:
        """
        Update version in context file.

        Args:
            content: Full context file content
            new_version: New version string

        Returns:
            Updated context file content
        """
        parsed_yaml, markdown_content = ContextParser.parse(content)
        parsed_yaml["version"] = new_version
        parsed_yaml["updated_at"] = datetime.utcnow().isoformat()
        return ContextSerializer.serialize(parsed_yaml, markdown_content)
