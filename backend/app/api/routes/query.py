import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.query import Query, QueryType
from app.schemas.query import (
    QueryRequest,
    QueryResponse,
    NaturalLanguageQueryRequest,
    QueryHistoryItem,
)
from app.services.data_service import DataService
from app.services.query_engine import QueryEngine
from sqlalchemy import select


router = APIRouter()


@router.post("/execute", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def execute_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a query (SQL or Pandas)"""
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

    # Execute query
    try:
        if request.query_type == QueryType.SQL:
            result_df, execution_time = QueryEngine.execute_sql(df, request.query)
            generated_query = None
        elif request.query_type == QueryType.PANDAS:
            import json
            operations = json.loads(request.query)
            result_df, execution_time = QueryEngine.execute_pandas_operations(df, operations)
            generated_query = None
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid query type. Use 'sql' or 'pandas'",
            )

        # Create preview
        preview_data = result_df.head(100).to_dict(orient="records")

        # Save query
        query = Query(
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            name=request.name,
            query_type=request.query_type,
            original_input=request.query,
            generated_query=generated_query,
            result_preview=preview_data,
            result_row_count=str(len(result_df)),
            execution_time_ms=str(round(execution_time, 2)),
        )
        db.add(query)
        await db.commit()
        await db.refresh(query)

        return query

    except Exception as e:
        # Save query with error
        query = Query(
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            name=request.name,
            query_type=request.query_type,
            original_input=request.query,
            error_message=str(e),
        )
        db.add(query)
        await db.commit()
        await db.refresh(query)

        return query


@router.post("/natural-language", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def execute_natural_language_query(
    request: NaturalLanguageQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a natural language query"""
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

    # Execute natural language query
    try:
        result_df, generated_query, execution_time = await QueryEngine.execute_natural_language_query(
            df=df,
            question=request.question,
            schema=dataset.schema,
            prefer_sql=True,
        )

        # Create preview
        preview_data = result_df.head(100).to_dict(orient="records")

        # Save query
        query = Query(
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            name=request.name,
            query_type=QueryType.NATURAL_LANGUAGE,
            original_input=request.question,
            generated_query=generated_query,
            result_preview=preview_data,
            result_row_count=str(len(result_df)),
            execution_time_ms=str(round(execution_time, 2)),
        )
        db.add(query)
        await db.commit()
        await db.refresh(query)

        return query

    except Exception as e:
        # Save query with error
        query = Query(
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            name=request.name,
            query_type=QueryType.NATURAL_LANGUAGE,
            original_input=request.question,
            error_message=str(e),
        )
        db.add(query)
        await db.commit()
        await db.refresh(query)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing query: {str(e)}",
        )


@router.get("/history", response_model=list[QueryHistoryItem])
async def get_query_history(
    dataset_id: uuid.UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get query history for current user"""
    from app.models.dataset import Dataset

    query_builder = (
        select(Query, Dataset.name)
        .join(Dataset, Query.dataset_id == Dataset.id)
        .where(Query.user_id == current_user.id)
    )

    if dataset_id:
        query_builder = query_builder.where(Query.dataset_id == dataset_id)

    query_builder = query_builder.order_by(Query.created_at.desc())

    result = await db.execute(query_builder)
    queries = result.all()

    return [
        QueryHistoryItem(
            id=q.id,
            dataset_id=q.dataset_id,
            dataset_name=dataset_name,
            name=q.name,
            query_type=q.query_type,
            original_input=q.original_input,
            created_at=q.created_at,
        )
        for q, dataset_name in queries
    ]


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific query"""
    result = await db.execute(
        select(Query).where(
            Query.id == query_id,
            Query.user_id == current_user.id,
        )
    )
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    return query
