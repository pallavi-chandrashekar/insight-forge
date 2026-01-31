import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Any, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visualization import Visualization, ChartType
from app.models.user import User


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
        x_label = config.get("x_label") or x_col
        y_label = config.get("y_label") or y_col

        # Build labels dict, excluding None values to prevent Plotly errors
        labels = {}
        if x_col and x_label:
            labels[x_col] = x_label
        if y_col and y_label:
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

        return fig.to_dict()

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
