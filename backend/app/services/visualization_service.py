import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json
from typing import Any, Optional, Dict, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visualization import Visualization, ChartType
from app.models.user import User
from app.services.llm_service import LLMService
from app.services.context_service import ContextService


class VisualizationService:
    """Service for visualization generation"""

    @staticmethod
    def create_plotly_chart(
        df: pd.DataFrame,
        chart_type: ChartType,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a Plotly chart from DataFrame"""
        x_col = config.get("x_column")
        y_col = config.get("y_column")
        color_col = config.get("color_column")
        title = config.get("title", "")
        x_label = config.get("x_label")
        y_label = config.get("y_label")
        aggregation = config.get("aggregation")

        # Handle list of columns - convert single-element lists to strings
        if isinstance(x_col, list) and len(x_col) == 1:
            x_col = x_col[0]
        if isinstance(y_col, list):
            if len(y_col) == 1:
                y_col = y_col[0]
            elif len(y_col) > 1 and aggregation and x_col:
                # Multi-column aggregation for bar/line/area charts
                agg_func = aggregation.lower()
                try:
                    # Group by x_col and aggregate all y columns
                    df_agg = df.groupby(x_col)[y_col].agg(agg_func).reset_index()

                    # Melt to long format for Plotly (creates 'variable' and 'value' columns)
                    df = df_agg.melt(
                        id_vars=[x_col],
                        value_vars=y_col,
                        var_name='Series',
                        value_name='Value'
                    )

                    # Update config for melted dataframe
                    y_col = 'Value'
                    color_col = 'Series'  # Use Series as color to separate the lines/bars
                    y_label = y_label or 'Value'

                except Exception as e:
                    raise ValueError(f"Aggregation failed: {str(e)}")

        # Set default labels if not provided
        if not x_label:
            x_label = x_col if isinstance(x_col, str) else None
        if not y_label:
            y_label = y_col if isinstance(y_col, str) else None

        # Build labels dict, excluding None values to prevent Plotly errors
        labels = {}
        if x_col and x_label:
            labels[x_col] = x_label
        if y_col and y_label and isinstance(y_col, str):
            labels[y_col] = y_label

        if chart_type == ChartType.BAR:
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title,
                labels=labels if labels else None,
            )
        elif chart_type == ChartType.LINE:
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title,
                labels=labels if labels else None,
            )
        elif chart_type == ChartType.SCATTER:
            size_col = config.get("size_column")
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                size=size_col,
                title=title,
                labels=labels if labels else None,
            )
        elif chart_type == ChartType.PIE:
            fig = px.pie(
                df,
                names=x_col,
                values=y_col,
                title=title,
            )
        elif chart_type == ChartType.HISTOGRAM:
            histogram_labels = {}
            if x_col and x_label:
                histogram_labels[x_col] = x_label
            fig = px.histogram(
                df,
                x=x_col,
                color=color_col,
                title=title,
                labels=histogram_labels if histogram_labels else None,
            )
        elif chart_type == ChartType.HEATMAP:
            # For heatmap, expect a correlation matrix or pivot table
            if x_col and y_col:
                pivot = df.pivot_table(
                    values=config.get("values_column"),
                    index=y_col,
                    columns=x_col,
                    aggfunc=config.get("aggregation", "mean"),
                )
                fig = px.imshow(
                    pivot,
                    title=title,
                    labels=dict(x=x_label, y=y_label, color="Value"),
                )
            else:
                # Correlation heatmap
                numeric_cols = df.select_dtypes(include=["number"]).columns
                corr = df[numeric_cols].corr()
                fig = px.imshow(
                    corr,
                    title=title or "Correlation Heatmap",
                    labels=dict(color="Correlation"),
                )
        elif chart_type == ChartType.BOX:
            fig = px.box(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title,
                labels=labels if labels else None,
            )
        elif chart_type == ChartType.AREA:
            fig = px.area(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title,
                labels=labels if labels else None,
            )
        else:
            # Default to table
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns)),
                cells=dict(values=[df[col] for col in df.columns])
            )])

        # Convert to JSON-safe format (converts numpy arrays to lists)
        return json.loads(pio.to_json(fig))

    @staticmethod
    async def save_visualization(
        db: AsyncSession,
        user: User,
        dataset_id: UUID,
        chart_type: ChartType,
        config: dict[str, Any],
        chart_data: dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        query_id: Optional[UUID] = None,
    ) -> Visualization:
        """Save visualization to database"""
        viz = Visualization(
            user_id=user.id,
            dataset_id=dataset_id,
            query_id=query_id,
            name=name,
            description=description,
            chart_type=chart_type,
            config=config,
            chart_data=chart_data,
        )
        db.add(viz)
        await db.commit()
        await db.refresh(viz)
        return viz

    @staticmethod
    async def get_visualization(
        db: AsyncSession,
        viz_id: UUID,
        user_id: UUID,
    ) -> Optional[Visualization]:
        """Get visualization by ID for a specific user"""
        result = await db.execute(
            select(Visualization).where(
                Visualization.id == viz_id,
                Visualization.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_visualizations(
        db: AsyncSession,
        user_id: UUID,
        dataset_id: Optional[UUID] = None,
    ) -> list[Visualization]:
        """Get all visualizations for a user"""
        query = select(Visualization).where(Visualization.user_id == user_id)
        if dataset_id:
            query = query.where(Visualization.dataset_id == dataset_id)
        query = query.order_by(Visualization.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def delete_visualization(db: AsyncSession, viz: Visualization) -> None:
        """Delete a visualization"""
        await db.delete(viz)
        await db.commit()

    @staticmethod
    async def suggest_visualizations_with_context(
        df: pd.DataFrame,
        context_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        dataset_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest visualizations using context metadata for better recommendations.

        Args:
            df: DataFrame to visualize
            context_id: Context ID
            user_id: User ID
            db: Database session
            dataset_id: Optional dataset ID for filtering context columns

        Returns:
            List of visualization suggestions with enhanced metadata
        """
        # Load context
        context_service = ContextService(db)
        context = await context_service.get_context(context_id, user_id)

        if not context:
            # Fallback to regular suggestions
            return await VisualizationService.suggest_visualizations_simple(df)

        # Get schema with context enhancement
        schema = {
            'columns': []
        }

        # Find dataset in context
        dataset_info = None
        if dataset_id:
            for ds in context.datasets:
                if ds.get('id') == dataset_id or ds.get('dataset_id') == str(dataset_id):
                    dataset_info = ds
                    break

        # Build enhanced schema with business context
        for col in df.columns:
            col_info = {
                'name': str(col),
                'dtype': str(df[col].dtype),
                'unique_count': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(3).tolist() if not df[col].isnull().all() else []
            }

            # Add business metadata from context
            if dataset_info and dataset_info.get('columns'):
                for ctx_col in dataset_info['columns']:
                    if ctx_col['name'] == str(col):
                        col_info['business_name'] = ctx_col.get('business_name', '')
                        col_info['description'] = ctx_col.get('description', '')
                        col_info['tags'] = ctx_col.get('tags', [])
                        break

            schema['columns'].append(col_info)

        # Get sample data
        sample_data = df.head(5).to_dict('records')

        # Use LLM with context
        llm_service = LLMService()

        # Enhanced prompt with business context
        system_prompt = """You are a data visualization expert with access to rich business context.
Analyze the data and suggest appropriate visualizations considering business meanings.

Return a JSON array of visualization suggestions. Each suggestion should have:
- chart_type: "bar", "line", "scatter", "pie", "histogram", "heatmap", "box", "area"
- title: descriptive title using business terminology
- description: what business insights this shows
- confidence: 0-1 score
- config: {"x_column": "...", "y_column": "...", "color_column": "...", "aggregation": "..."}
- reasoning: why this is appropriate from a business perspective
- business_use_case: specific business scenario this addresses

Prioritize visualizations that reveal business insights. Return 3-5 suggestions."""

        # Format context metadata
        column_descriptions = []
        for col_info in schema['columns']:
            desc = f"- {col_info['name']}"
            if col_info.get('business_name'):
                desc += f" ({col_info['business_name']})"
            if col_info.get('description'):
                desc += f": {col_info['description']}"
            column_descriptions.append(desc)

        user_prompt = f"""Data schema with business context:
{chr(10).join(column_descriptions)}

Sample data:
{json.dumps(sample_data[:3], default=str)}

Suggest visualizations that provide business insights."""

        response = await llm_service._call_claude(system_prompt, user_prompt)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        suggestions = json.loads(response.strip())

        # Enhance suggestions with metric recommendations
        if context.metrics:
            for suggestion in suggestions:
                relevant_metrics = []
                for metric in context.metrics:
                    # Check if metric applies to this dataset
                    metric_datasets = metric.get('datasets', [])
                    if not metric_datasets or (dataset_id and dataset_id in metric_datasets):
                        relevant_metrics.append({
                            'id': metric['id'],
                            'name': metric['name'],
                            'expression': metric['expression']
                        })

                if relevant_metrics:
                    suggestion['suggested_metrics'] = relevant_metrics

        return suggestions

    @staticmethod
    async def suggest_visualizations_simple(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Simple visualization suggestions without context.

        Args:
            df: DataFrame to visualize

        Returns:
            List of basic visualization suggestions
        """
        schema = {
            'columns': [
                {
                    'name': str(col),
                    'dtype': str(df[col].dtype),
                    'unique_count': int(df[col].nunique()),
                    'sample_values': df[col].dropna().head(3).tolist() if not df[col].isnull().all() else []
                }
                for col in df.columns
            ]
        }

        sample_data = df.head(5).to_dict('records')

        llm_service = LLMService()
        return await llm_service.suggest_visualizations(schema, sample_data)

    @staticmethod
    def create_multi_dataset_chart(
        dataframes: Dict[str, pd.DataFrame],
        chart_type: ChartType,
        config: Dict[str, Any],
        join_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create visualization from multiple datasets.

        Args:
            dataframes: Dict of {dataset_id: DataFrame}
            chart_type: Chart type
            config: Chart configuration
            join_info: Optional join information

        Returns:
            Plotly chart data
        """
        # Merge dataframes if needed
        if len(dataframes) > 1 and join_info:
            # Perform merge based on join_info
            merged_df = None
            for idx, (ds_id, df) in enumerate(dataframes.items()):
                if idx == 0:
                    merged_df = df.copy()
                else:
                    # Simple merge - in production would use join_info
                    merge_on = join_info.get('join_columns', [])
                    if merge_on:
                        merged_df = merged_df.merge(df, on=merge_on, how='inner')

            df = merged_df
        else:
            # Use first dataframe
            df = list(dataframes.values())[0]

        # Create chart using standard method
        return VisualizationService.create_plotly_chart(df, chart_type, config)
