"""
Context API Routes
Endpoints for managing context files
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query as QueryParam
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.context import Context
from app.services.context_service import ContextService, ContextServiceError
from app.schemas.context import (
    ContextCreate,
    ContextResponse,
    ContextListResponse,
    ContextDetailResponse,
    ContextUpdate,
    ContextStatsResponse,
    GlossarySearchResponse,
    MetricResponse
)

router = APIRouter(prefix="/contexts", tags=["contexts"])


@router.post("/", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def create_context(
    content: str,
    validate: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new context from YAML + Markdown content.

    **Parameters:**
    - **content**: Full context file content (YAML frontmatter + Markdown)
    - **validate**: Whether to validate context (default: true)

    **Returns:**
    - Created context metadata
    """
    service = ContextService(db)

    try:
        context = await service.create_context(
            user_id=current_user.id,
            content=content,
            validate=validate
        )
        return context.to_dict()
    except ContextServiceError as e:
        # Check if error has validation details
        if hasattr(e, 'args') and len(e.args) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e.args[0]),
                    "validation": e.args[1]
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/upload", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def upload_context_file(
    file: UploadFile = File(...),
    validate: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a context file (.md or .yaml).

    **Parameters:**
    - **file**: Context file to upload
    - **validate**: Whether to validate context (default: true)

    **Returns:**
    - Created context metadata
    """
    # Read file content
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded text"
        )

    # Validate file extension
    if not file.filename.endswith(('.md', '.yaml', '.yml')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have .md, .yaml, or .yml extension"
        )

    service = ContextService(db)

    try:
        context = await service.create_context(
            user_id=current_user.id,
            content=content_str,
            validate=validate
        )
        return context.to_dict()
    except ContextServiceError as e:
        if hasattr(e, 'args') and len(e.args) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e.args[0]),
                    "validation": e.args[1]
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ContextListResponse])
async def list_contexts(
    context_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = QueryParam(None),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all contexts with optional filters.

    **Query Parameters:**
    - **context_type**: Filter by type (single_dataset, multi_dataset)
    - **category**: Filter by category
    - **status**: Filter by status (active, draft, deprecated)
    - **tags**: Filter by tags (can specify multiple)
    - **search**: Search in name and description
    - **skip**: Pagination offset
    - **limit**: Maximum results (max 100)

    **Returns:**
    - List of contexts
    """
    service = ContextService(db)

    contexts = await service.list_contexts(
        user_id=current_user.id,
        context_type=context_type,
        category=category,
        status=status,
        tags=tags,
        search=search,
        skip=skip,
        limit=min(limit, 100)
    )

    return [context.to_dict() for context in contexts]


@router.get("/stats", response_model=ContextStatsResponse)
async def get_context_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about user's contexts.

    **Returns:**
    - Context statistics
    """
    service = ContextService(db)
    stats = await service.get_statistics(current_user.id)
    return stats


@router.get("/{context_id}", response_model=ContextDetailResponse)
async def get_context(
    context_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get context details by ID.

    **Parameters:**
    - **context_id**: Context UUID

    **Returns:**
    - Full context details including parsed YAML
    """
    service = ContextService(db)

    context = await service.get_context(context_id, current_user.id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )

    # Return detailed response
    return {
        **context.to_dict(),
        "parsed_yaml": context.parsed_yaml,
        "markdown_content": context.markdown_content,
        "datasets": context.datasets,
        "relationships": context.relationships,
        "metrics": context.metrics,
        "business_rules": context.business_rules,
        "filters": context.filters,
        "settings": context.settings,
        "data_model": context.data_model,
        "glossary": context.glossary,
        "validation_errors": context.validation_errors,
        "validation_warnings": context.validation_warnings
    }


@router.get("/{context_id}/download")
async def download_context(
    context_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download context as original file.

    **Parameters:**
    - **context_id**: Context UUID

    **Returns:**
    - Context file content
    """
    from fastapi.responses import PlainTextResponse

    service = ContextService(db)

    content = await service.get_context_full_content(context_id, current_user.id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )

    context = await service.get_context(context_id, current_user.id)
    filename = f"{context.name}_v{context.version}.md"

    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.put("/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: UUID,
    content: str,
    validate: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update context with new content.

    **Parameters:**
    - **context_id**: Context UUID
    - **content**: New context file content
    - **validate**: Whether to validate (default: true)

    **Returns:**
    - Updated context metadata
    """
    service = ContextService(db)

    try:
        context = await service.update_context(
            context_id=context_id,
            user_id=current_user.id,
            content=content,
            validate=validate
        )
        return context.to_dict()
    except ContextServiceError as e:
        if hasattr(e, 'args') and len(e.args) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e.args[0]),
                    "validation": e.args[1]
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{context_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_context(
    context_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a context.

    **Parameters:**
    - **context_id**: Context UUID
    """
    service = ContextService(db)

    deleted = await service.delete_context(context_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )


@router.get("/glossary/search", response_model=List[GlossarySearchResponse])
async def search_glossary(
    term: str = QueryParam(..., min_length=2),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search glossary terms across all contexts.

    **Query Parameters:**
    - **term**: Search term (minimum 2 characters)

    **Returns:**
    - List of matching glossary entries
    """
    service = ContextService(db)

    results = await service.search_glossary(current_user.id, term)
    return results


@router.get("/datasets/{dataset_id}/metrics", response_model=List[MetricResponse])
async def get_metrics_for_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all metrics applicable to a specific dataset.

    **Parameters:**
    - **dataset_id**: Dataset UUID

    **Returns:**
    - List of metrics from all contexts that include this dataset
    """
    service = ContextService(db)

    metrics = await service.get_metrics_by_dataset(current_user.id, dataset_id)
    return metrics
