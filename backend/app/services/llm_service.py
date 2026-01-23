import json
from typing import Any

from anthropic import AsyncAnthropic

from app.core.config import settings


class LLMService:
    """Service for LLM-powered features"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
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
