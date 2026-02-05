import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.query import Query
from app.schemas.visualization import VizRequest, VizResponse, VizSuggestion, NLVizRequest, NLVizResponse
from app.services.data_service import DataService
from app.services.visualization_service import VisualizationService
from app.services.llm_service import LLMService
from app.services.context_service import ContextService


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


@router.post("/from-natural-language", response_model=NLVizResponse, status_code=status.HTTP_201_CREATED)
async def generate_from_natural_language(
    request: NLVizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate visualization from natural language description"""

    # Get dataset
    dataset = await DataService.get_dataset(db, request.dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    # Load DataFrame
    try:
        df = DataService.load_dataframe(dataset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading dataset: {str(e)}",
        )

    # Try to find active context for this dataset
    context = None
    context_metadata = None
    try:
        context_service = ContextService(db)
        context = await context_service.find_active_context_by_dataset(
            dataset_id=request.dataset_id,
            user_id=current_user.id
        )

        # Extract metadata if context exists
        if context:
            context_metadata = await context_service.get_context_metadata_for_dataset(
                context=context,
                dataset_id=request.dataset_id
            )
    except Exception as e:
        # Log error but don't fail the request if context lookup fails
        print(f"Warning: Context lookup failed: {str(e)}")

    # Parse natural language
    try:
        llm_service = LLMService()
        parsed_config = await llm_service.generate_visualization_from_nl(
            description=request.description,
            schema=dataset.schema,
            sample_data=df.head(5).to_dict(orient="records"),
            context_metadata=context_metadata,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Could not understand request",
                "message": str(e),
                "suggestions": [
                    "Specify the chart type (e.g., 'bar chart')",
                    "Mention columns to visualize",
                    "Example: 'show total sales by region'"
                ]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing description: {str(e)}",
        )

    # Validate columns exist
    available_cols = [col["name"] for col in dataset.schema.get("columns", [])]
    x_col = parsed_config["config"].get("x_column")
    y_col = parsed_config["config"].get("y_column")

    if x_col and x_col not in available_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Column not found",
                "missing": x_col,
                "available": available_cols
            }
        )
    if y_col and isinstance(y_col, str) and y_col not in available_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Column not found",
                "missing": y_col,
                "available": available_cols
            }
        )
    if y_col and isinstance(y_col, list):
        for col in y_col:
            if col not in available_cols:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Column not found",
                        "missing": col,
                        "available": available_cols
                    }
                )

    # Generate chart
    try:
        chart_data = VisualizationService.create_plotly_chart(
            df=df,
            chart_type=parsed_config["chart_type"],
            config=parsed_config["config"],
        )

        # Save visualization
        viz = await VisualizationService.save_visualization(
            db=db,
            user=current_user,
            dataset_id=request.dataset_id,
            chart_type=parsed_config["chart_type"],
            config=parsed_config["config"],
            chart_data=chart_data,
            name=request.name or parsed_config.get("title"),
            description=f"Generated from: {request.description}",
        )

        return {
            "visualization": viz,
            "parsed_intent": parsed_config,
            "suggestions": None,
            "context_used": context is not None,
            "context_name": context.name if context else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating visualization: {str(e)}",
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
