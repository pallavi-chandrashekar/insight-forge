import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.dataset import SourceType
from app.schemas.dataset import (
    DatasetResponse,
    DatasetPreview,
    UrlImportRequest,
    ScrapeRequest,
)
from app.services.data_service import DataService


router = APIRouter()


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a data file"""
    # Validate file type
    file_type = DataService.get_file_type(file.filename)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported: CSV, JSON, Excel, Parquet",
        )

    # Parse file to DataFrame
    try:
        df = await DataService.parse_file(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(e)}",
        )

    # Save file to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_extension}")

    # Save DataFrame to file
    if file_type == "csv":
        df.to_csv(file_path, index=False)
    elif file_type == "json":
        df.to_json(file_path, orient="records")
    elif file_type == "excel":
        df.to_excel(file_path, index=False)
    elif file_type == "parquet":
        df.to_parquet(file_path, index=False)

    # Save dataset metadata
    dataset = await DataService.save_dataset(
        db=db,
        user=current_user,
        name=name,
        df=df,
        source_type=SourceType.FILE,
        file_path=file_path,
        original_filename=file.filename,
        description=description,
    )

    return dataset


@router.post("/from-url", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def import_from_url(
    request: UrlImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import data from URL"""
    try:
        df = await DataService.fetch_url(request.url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching URL: {str(e)}",
        )

    # Save DataFrame to file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.parquet")
    df.to_parquet(file_path, index=False)

    # Save dataset metadata
    dataset = await DataService.save_dataset(
        db=db,
        user=current_user,
        name=request.name,
        df=df,
        source_type=SourceType.URL,
        file_path=file_path,
        source_url=request.url,
        description=request.description,
    )

    return dataset


@router.post("/scrape", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def scrape_webpage(
    request: ScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Scrape data from webpage"""
    try:
        df = await DataService.scrape_webpage(request.url, request.selector)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error scraping webpage: {str(e)}",
        )

    # Save DataFrame to file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.parquet")
    df.to_parquet(file_path, index=False)

    # Save dataset metadata
    dataset = await DataService.save_dataset(
        db=db,
        user=current_user,
        name=request.name,
        df=df,
        source_type=SourceType.SCRAPE,
        file_path=file_path,
        source_url=request.url,
        description=request.description,
    )

    return dataset


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all datasets for current user"""
    datasets = await DataService.get_user_datasets(db, current_user.id)
    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dataset details"""
    dataset = await DataService.get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )
    return dataset


@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def preview_dataset(
    dataset_id: uuid.UUID,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dataset preview"""
    dataset = await DataService.get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    try:
        df = DataService.load_dataframe(dataset)
        preview = DataService.get_preview(df, limit)
        return {
            "dataset_id": dataset_id,
            **preview,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading dataset: {str(e)}",
        )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a dataset"""
    dataset = await DataService.get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    await DataService.delete_dataset(db, dataset)
