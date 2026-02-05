import json
from typing import Any, Optional

from anthropic import AsyncAnthropic

from app.core.config import settings


class LLMService:
    """Service for LLM-powered features"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.API_KEY)
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS

    async def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to Claude API"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    async def generate_sql_query(self, question: str, schema: dict[str, Any]) -> str:
        """Generate SQL query from natural language question"""
        system_prompt = """You are a SQL expert. Generate SQL queries based on user questions.
The data is stored in a table called 'df'.

IMPORTANT RULES:
1. Only return the SQL query, nothing else
2. Use standard SQL syntax compatible with SQLite
3. Use column names exactly as they appear in the schema
4. Handle potential NULL values appropriately
5. Do not use any DDL statements (CREATE, DROP, ALTER, etc.)
6. Only use SELECT statements"""

        schema_str = self._format_schema(schema)
        user_prompt = f"""Schema:
{schema_str}

Question: {question}

Generate a SQL query to answer this question. Only return the SQL query, no explanation."""

        response = await self._call_claude(system_prompt, user_prompt)
        query = response.strip()
        if query.startswith("```sql"):
            query = query[6:]
        if query.startswith("```"):
            query = query[3:]
        if query.endswith("```"):
            query = query[:-3]
        return query.strip()

    async def generate_pandas_operations(self, question: str, schema: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate pandas operations from natural language question"""
        system_prompt = """You are a pandas expert. Generate a list of pandas operations based on user questions.

Return a JSON array of operations. Each operation is an object with a 'type' and relevant parameters.

Supported operation types:
- {"type": "filter", "condition": "column > value"}
- {"type": "select", "columns": ["col1", "col2"]}
- {"type": "sort", "by": "column", "ascending": true/false}
- {"type": "groupby", "by": ["col"], "agg": {"col2": "mean"}}
- {"type": "head", "n": 10}
- {"type": "drop_na", "columns": ["col1"]}
- {"type": "rename", "mapping": {"old": "new"}}

IMPORTANT: Only return valid JSON array, no explanation."""

        schema_str = self._format_schema(schema)
        user_prompt = f"""Schema:
{schema_str}

Question: {question}

Generate pandas operations to answer this question. Only return the JSON array."""

        response = await self._call_claude(system_prompt, user_prompt)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return json.loads(response.strip())

    async def suggest_visualizations(
        self,
        schema: dict[str, Any],
        sample_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Suggest appropriate visualizations based on data"""
        system_prompt = """You are a data visualization expert. Analyze the data schema and suggest appropriate visualizations.

Return a JSON array of visualization suggestions. Each suggestion should have:
- chart_type: one of "bar", "line", "scatter", "pie", "histogram", "heatmap", "box", "area", "table"
- title: a descriptive title
- description: what this visualization shows
- confidence: 0-1 score of how appropriate this viz is
- config: {"x_column": "...", "y_column": "...", "color_column": "...", "aggregation": "..."}
- reasoning: why this visualization is appropriate

Consider data types, number of unique values, and relationships between columns.

Return 3-5 suggestions ordered by confidence. Only return valid JSON array."""

        schema_str = self._format_schema(schema)
        sample_str = json.dumps(sample_data[:5], default=str)

        user_prompt = f"""Schema:
{schema_str}

Sample data:
{sample_str}

Suggest appropriate visualizations for this data."""

        response = await self._call_claude(system_prompt, user_prompt)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return json.loads(response.strip())

    async def generate_visualization_from_nl(
        self,
        description: str,
        schema: dict[str, Any],
        sample_data: list[dict[str, Any]],
        context_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Generate a complete visualization configuration from natural language.

        Args:
            description: User's natural language description
            schema: Dataset schema with column info
            sample_data: Sample rows for context

        Returns:
            {
                "chart_type": "bar",
                "title": "Average Screen Time by Age Group",
                "config": {
                    "x_column": "age_group",
                    "y_column": "screen_time",
                    "aggregation": "mean"
                },
                "reasoning": "User requested average, which maps to mean aggregation..."
            }

        Raises:
            ValueError: If description cannot be parsed
        """
        context_section = ""
        if context_metadata:
            context_section = self._format_context_for_prompt(context_metadata)

        system_prompt = f"""You are a data visualization expert. Parse natural language descriptions into visualization configurations.
{f'''
BUSINESS CONTEXT (use this to improve accuracy):
{context_section}

When business context is provided:
- Map business terms to technical column names using glossary and column metadata
- Use pre-defined metrics when mentioned (e.g., if user says "avg_screen_time", use that metric)
- Apply filters by name if referenced
- Prefer business names over technical column names in titles
''' if context_section else ''}
RULES:
1. Only use columns from the provided schema
2. Choose chart types based on data types and user intent:
   - bar: categorical x-axis, numeric y-axis, for comparisons
   - line: time-series or sequential data, show trends
   - scatter: two numeric columns, explore relationships
   - pie: categorical data, show proportions (only when explicitly requested)
   - histogram: single numeric column, show distribution
   - box: numeric data grouped by categories, statistical spread
   - area: cumulative trends over time
   - heatmap: correlations or 2D patterns

3. Map common aggregation terms:
   - "average" → "mean"
   - "total" / "sum" → "sum"
   - "count" / "number of" → "count"
   - "maximum" / "highest" → "max"
   - "minimum" / "lowest" → "min"

4. If description is ambiguous, make reasonable assumptions based on data types

5. Return ONLY valid JSON, no markdown code blocks

OUTPUT FORMAT:
{{
  "chart_type": "bar" | "line" | "scatter" | "pie" | "histogram" | "heatmap" | "box" | "area",
  "title": "Descriptive Title",
  "config": {{
    "x_column": "column_name",
    "y_column": "column_name" | ["col1", "col2"],
    "color_column": "column_name",
    "aggregation": "mean" | "sum" | "count" | "min" | "max"
  }},
  "reasoning": "Brief explanation of chart type choice"
}}

ERROR FORMAT (if cannot parse):
{{
  "error": "Explanation of what's unclear",
  "suggestions": ["Suggestion 1", "Suggestion 2"]
}}"""

        schema_str = self._format_schema(schema)
        sample_str = json.dumps(sample_data[:3], default=str)

        user_prompt = f"""Schema:
{schema_str}

Sample data:
{sample_str}

User request: "{description}"

Parse this into a visualization configuration."""

        response = await self._call_claude(system_prompt, user_prompt)

        # Clean markdown
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        parsed = json.loads(response.strip())

        # Check for error response from LLM
        if "error" in parsed:
            raise ValueError(parsed["error"])

        # Validate required fields
        if "chart_type" not in parsed or "config" not in parsed:
            raise ValueError("Could not determine chart type and columns from description")

        return parsed

    async def generate_insights(self, stats: dict[str, Any]) -> list[str]:
        """Generate insights about the data"""
        system_prompt = """You are a data analyst. Generate key insights about the data based on the provided statistics.

Return a JSON array of insight strings. Each insight should be:
- Specific and actionable
- Based on the statistics provided
- Written in clear, non-technical language

Return 3-5 insights. Only return valid JSON array of strings."""

        stats_str = json.dumps(stats, default=str)
        user_prompt = f"""Data statistics:
{stats_str}

Generate key insights about this data."""

        response = await self._call_claude(system_prompt, user_prompt)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return json.loads(response.strip())

    def _format_schema(self, schema: dict[str, Any]) -> str:
        """Format schema for LLM prompt"""
        lines = []
        for col in schema.get("columns", []):
            name = col.get("name", "")
            dtype = col.get("dtype", "")
            samples = col.get("sample_values", [])
            lines.append(f"- {name} ({dtype}): sample values = {samples}")
        return "\n".join(lines)

    def _format_context_for_prompt(self, context_metadata: dict[str, Any]) -> str:
        """
        Format context metadata into readable sections for LLM.

        Args:
            context_metadata: Dictionary with business context

        Returns:
            Formatted string with context sections
        """
        if not context_metadata:
            return ""

        sections = []

        # Dataset description
        if context_metadata.get("description"):
            sections.append(f"Dataset: {context_metadata['name']}")
            sections.append(f"Description: {context_metadata['description']}\n")

        # Column business names and descriptions
        columns = context_metadata.get("columns", [])
        if columns:
            sections.append("COLUMN METADATA:")
            for col in columns:
                col_line = f"- {col['name']}"
                if col.get("business_name"):
                    col_line += f" (Business name: {col['business_name']})"
                if col.get("description"):
                    col_line += f": {col['description']}"
                sections.append(col_line)
            sections.append("")

        # Pre-defined metrics
        metrics = context_metadata.get("metrics", [])
        if metrics:
            sections.append("PRE-DEFINED METRICS:")
            for metric in metrics:
                metric_line = f"- {metric.get('name', metric.get('id'))}"
                if metric.get("expression"):
                    metric_line += f" = {metric['expression']}"
                if metric.get("description"):
                    metric_line += f" ({metric['description']})"
                sections.append(metric_line)
            sections.append("")

        # Glossary terms
        glossary = context_metadata.get("glossary", [])
        if glossary:
            sections.append("GLOSSARY TERMS:")
            for term in glossary:
                term_line = f"- {term.get('term')}"
                if term.get("definition"):
                    term_line += f": {term['definition']}"
                if term.get("related_columns"):
                    term_line += f" [Related columns: {', '.join(term['related_columns'])}]"
                sections.append(term_line)
            sections.append("")

        # Available filters
        filters = context_metadata.get("filters", [])
        if filters:
            sections.append("AVAILABLE FILTERS:")
            for filter_def in filters:
                filter_line = f"- {filter_def.get('name', filter_def.get('id'))}"
                if filter_def.get("condition"):
                    filter_line += f": {filter_def['condition']}"
                sections.append(filter_line)
            sections.append("")

        return "\n".join(sections)

    async def analyze_multi_dataset_query(
        self,
        question: str,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyze a natural language question to determine which datasets,
        metrics, and filters are needed.

        Args:
            question: Natural language question
            context: Parsed context dictionary

        Returns:
            Analysis with required datasets, metrics, filters
        """
        system_prompt = """You are a data analysis expert. Analyze the user's question and determine:
1. Which datasets are needed
2. Which metrics (if any) should be calculated
3. Which filters (if any) should be applied
4. What columns to select

Return a JSON object with:
{
  "required_datasets": ["dataset_id1", "dataset_id2"],
  "required_metrics": ["metric_id1"],
  "required_filters": ["filter_id1"],
  "select_columns": ["col1", "col2"],
  "reasoning": "explanation"
}

Only return valid JSON, no explanation outside the object."""

        # Format context info
        datasets_info = []
        for ds in context.get('datasets', []):
            ds_info = f"- {ds['id']}: {ds['name']}"
            if ds.get('description'):
                ds_info += f" - {ds['description']}"
            datasets_info.append(ds_info)

        metrics_info = []
        for metric in context.get('metrics', []):
            metrics_info.append(f"- {metric['id']}: {metric['name']} = {metric['expression']}")

        filters_info = []
        for filter_def in context.get('filters', []):
            filters_info.append(f"- {filter_def['id']}: {filter_def['name']}")

        user_prompt = f"""Context information:

Datasets:
{chr(10).join(datasets_info)}

Metrics:
{chr(10).join(metrics_info) if metrics_info else "None"}

Filters:
{chr(10).join(filters_info) if filters_info else "None"}

User question: {question}

Analyze what's needed to answer this question."""

        response = await self._call_claude(system_prompt, user_prompt)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return json.loads(response.strip())

    async def generate_sql_with_context(
        self,
        question: str,
        schema: dict[str, Any],
        context: dict[str, Any],
        dataset_id: str
    ) -> str:
        """
        Generate SQL query using context metadata.

        Args:
            question: Natural language question
            schema: Dataset schema
            context: Context definition
            dataset_id: Target dataset ID

        Returns:
            Generated SQL query
        """
        system_prompt = """You are a SQL expert with access to rich dataset metadata.
Generate SQL queries based on user questions, using the provided context for guidance.

IMPORTANT RULES:
1. Only return the SQL query, nothing else
2. Use column business names and descriptions to understand intent
3. Apply pre-defined metrics when relevant
4. Use standard SQL syntax compatible with SQLite
5. Handle NULL values appropriately
6. Only use SELECT statements
7. The table name is 'df'"""

        # Find dataset in context
        dataset_info = None
        for ds in context.get('datasets', []):
            if ds['id'] == dataset_id:
                dataset_info = ds
                break

        # Format enhanced schema with business metadata
        schema_lines = []
        if dataset_info and dataset_info.get('columns'):
            for col in dataset_info['columns']:
                line = f"- {col['name']} ({col.get('data_type', 'unknown')})"
                if col.get('business_name'):
                    line += f" [Business name: {col['business_name']}]"
                if col.get('description'):
                    line += f" - {col['description']}"
                schema_lines.append(line)
        else:
            schema_lines = [self._format_schema(schema)]

        # Include relevant metrics
        metrics_lines = []
        for metric in context.get('metrics', []):
            if not metric.get('datasets') or dataset_id in metric.get('datasets', []):
                metrics_lines.append(f"- {metric['name']}: {metric['expression']}")

        user_prompt = f"""Schema:
{chr(10).join(schema_lines)}

Available metrics:
{chr(10).join(metrics_lines) if metrics_lines else "None"}

User question: {question}

Generate a SQL query to answer this question."""

        response = await self._call_claude(system_prompt, user_prompt)
        query = response.strip()
        if query.startswith("```sql"):
            query = query[6:]
        if query.startswith("```"):
            query = query[3:]
        if query.endswith("```"):
            query = query[:-3]
        return query.strip()
