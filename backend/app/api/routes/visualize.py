import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.query import Query
from app.schemas.visualization import VizRequest, VizResponse, VizSuggestion
from app.services.data_service import DataService
from app.services.visualization_service import VisualizationService
from app.services.llm_service import LLMService


router = APIRouter()


@router.post("/generate", response_model=VizResponse, status_code=status.HTTP_201_CREATED)
async def generate_visualization(
    request: VizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a visualization"""
    # Get dataset
    dataset = await DataService.get_dataset(db, request.dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    # Load DataFrame (from query result if query_id provided, otherwise from dataset)
    try:
        if request.query_id:
            from sqlalchemy import select
            result = await db.execute(
                select(Query).where(
                    Query.id == request.query_id,
                    Query.user_id == current_user.id,
                )
            )
            query = result.scalar_one_or_none()
            if not query:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Query not found",
                )
            if not query.result_preview:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Query has no results to visualize",
                )
            # Load DataFrame from query results
            import pandas as pd
            df = pd.DataFrame(query.result_preview)
        else:
            df = DataService.load_dataframe(dataset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading data: {str(e)}",
        )

    # Generate chart
    try:
        chart_data = VisualizationService.create_plotly_chart(
            df=df,
            chart_type=request.chart_type,
            config=request.config.dict(),
        )

        # Save visualization
        viz = await VisualizationService.save_visualization(
            db=db,
            user=current_user,
            dataset_id=request.dataset_id,
            chart_type=request.chart_type,
            config=request.config.dict(),
            chart_data=chart_data,
            name=request.name,
            description=request.description,
            query_id=request.query_id,
        )

        return viz

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating visualization: {str(e)}",
        )


@router.post("/suggest", response_model=list[VizSuggestion])
async def suggest_visualizations(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-powered visualization suggestions"""
    # Get dataset
    dataset = await DataService.get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    # Load DataFrame for sample data
    try:
        df = DataService.load_dataframe(dataset)
        sample_data = df.head(5).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading dataset: {str(e)}",
        )

    # Get suggestions from LLM
    try:
        llm_service = LLMService()
        suggestions = await llm_service.suggest_visualizations(
            schema=dataset.schema,
            sample_data=sample_data,
        )

        # Convert to VizSuggestion objects
        return [
            VizSuggestion(
                chart_type=s["chart_type"],
                title=s["title"],
                description=s["description"],
                confidence=s["confidence"],
                config=s["config"],
                reasoning=s["reasoning"],
            )
            for s in suggestions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}",
        )


@router.get("/", response_model=list[VizResponse])
async def list_visualizations(
    dataset_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List visualizations for current user"""
    visualizations = await VisualizationService.get_user_visualizations(
        db=db,
        user_id=current_user.id,
        dataset_id=dataset_id,
    )
    return visualizations


@router.get("/{viz_id}", response_model=VizResponse)
async def get_visualization(
    viz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific visualization"""
    viz = await VisualizationService.get_visualization(db, viz_id, current_user.id)
    if not viz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visualization not found",
        )
    return viz


@router.delete("/{viz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visualization(
    viz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a visualization"""
    viz = await VisualizationService.get_visualization(db, viz_id, current_user.id)
    if not viz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visualization not found",
        )

    await VisualizationService.delete_visualization(db, viz)
