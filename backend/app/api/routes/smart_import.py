"""
Smart Import Routes
Intelligently handles any URL and guides users to the right feature
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.dataset import SourceType
from app.services.smart_url_detector import SmartURLDetector, URLType
from app.services.kaggle_service import KaggleService
from app.services.data_service import DataService


router = APIRouter()


class SmartImportRequest(BaseModel):
    """Request to analyze any URL"""
    url: str
    dataset_name: Optional[str] = None


class SmartImportResponse(BaseModel):
    """Response with guidance on what to do with the URL"""
    url_type: str
    platform: Optional[str]
    message: dict
    can_import_data: bool
    can_create_context: bool
    documentation_content: Optional[str] = None


@router.post("/analyze-url", response_model=SmartImportResponse)
async def analyze_url(
    request: SmartImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze any URL and determine what the user should do with it.

    This endpoint intelligently detects:
    - Data files (CSV, JSON, etc.) → Can be imported
    - Documentation (README, guides) → Can be used as context
    - Dataset pages (Kaggle, GitHub) → Guide user to download link
    """

    # Quick detection based on URL pattern
    url_type, platform, metadata = SmartURLDetector.detect_url_type(request.url)

    # For unknown URLs, inspect the content
    if url_type == URLType.INVALID or metadata.get('needs_inspection'):
        inspection = await SmartURLDetector.inspect_url_content(request.url)
        if inspection['success']:
            url_type = inspection['type']
            metadata.update(inspection)

    # Generate user-friendly message
    message = SmartURLDetector.generate_user_message(url_type, platform, metadata)

    # Determine what actions are available
    # For dataset pages (Kaggle, etc.), allow both importing data AND creating context
    can_import_data = url_type in [URLType.DATA_FILE, URLType.DATASET_PAGE]
    can_create_context = url_type in [URLType.DOCUMENTATION, URLType.DATASET_PAGE]

    # Extract documentation content if applicable
    documentation_content = None
    if can_create_context and url_type in [URLType.DOCUMENTATION, URLType.DATASET_PAGE]:
        documentation_content = await SmartURLDetector.extract_documentation_from_url(request.url)

    return SmartImportResponse(
        url_type=url_type,
        platform=platform,
        message=message,
        can_import_data=can_import_data,
        can_create_context=can_create_context,
        documentation_content=documentation_content
    )


@router.post("/create-context-from-url")
async def create_context_from_url(
    request: SmartImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a context from a documentation URL.

    Extracts content from documentation pages and creates a context file.
    """
    from app.services.context_service import ContextService

    # Extract documentation
    documentation = await SmartURLDetector.extract_documentation_from_url(request.url)

    if not documentation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract documentation from URL"
        )

    # Add metadata to documentation
    # For generic docs, we create a simple format without dataset requirements
    title = request.dataset_name or 'Documentation'
    enhanced_doc = f"""# {title}

**Source:** {request.url}
**Imported:** Automatically from URL
**Type:** General Documentation

---

{documentation}
"""

    # Create context directly using simple format
    # Generic documentation doesn't need dataset associations
    context_service = ContextService(db)

    try:
        # Import here to avoid circular dependency
        from app.models.context import Context, ContextStatus
        import uuid

        # Create context object directly for generic documentation
        # This bypasses the parser which expects dataset information
        from app.models.context import ContextType

        # Create minimal parsed_yaml structure for generic docs
        parsed_yaml = {
            "name": title,
            "version": "1.0.0",
            "description": f"Documentation imported from {request.url}",
            "context_type": "single_dataset",
            "status": "active"
        }

        context = Context(
            user_id=current_user.id,
            name=title,
            version="1.0.0",
            description=f"Documentation imported from {request.url}",
            context_type=ContextType.SINGLE_DATASET,
            status=ContextStatus.ACTIVE,
            markdown_content=enhanced_doc,  # Correct field name
            parsed_yaml=parsed_yaml,  # Required field
            datasets=[],  # Empty datasets for generic documentation
            relationships=None,
            validation_status="skipped",
            validation_errors=None,
            validation_warnings=None
        )

        db.add(context)
        await db.commit()
        await db.refresh(context)

        return {
            "success": True,
            "context_id": str(context.id),
            "context_name": context.name,
            "message": "Context created successfully from documentation URL"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create context: {str(e)}"
        )


@router.get("/supported-platforms")
async def get_supported_platforms():
    """
    Get list of supported platforms for smart import.
    """
    return {
        "data_platforms": {
            "supported_formats": [".csv", ".json", ".xlsx", ".xls", ".parquet", ".tsv"],
            "examples": [
                "https://example.com/data.csv",
                "https://api.example.com/export.json",
                "https://storage.example.com/dataset.xlsx"
            ]
        },
        "documentation_platforms": {
            "supported": list(SmartURLDetector.DOC_PLATFORMS.values()),
            "examples": [
                "https://github.com/user/repo/README.md",
                "https://docs.google.com/document/d/...",
                "https://notion.so/Dataset-Guide"
            ]
        },
        "dataset_platforms": {
            "supported": list(SmartURLDetector.DATASET_PLATFORMS.values()),
            "guidance": "These platforms require you to find the 'Download' button to get the direct data URL",
            "examples": [
                "https://kaggle.com/datasets/...",
                "https://data.world/...",
                "https://huggingface.co/datasets/..."
            ]
        }
    }


class KaggleImportRequest(BaseModel):
    """Request to import dataset from Kaggle"""
    url: str
    dataset_name: str
    kaggle_username: Optional[str] = None  # Optional if stored credentials exist
    kaggle_key: Optional[str] = None  # Optional if stored credentials exist
    create_context: bool = True  # Also create context from page description
    save_credentials: bool = False  # Save credentials for future use


@router.post("/import-from-kaggle")
async def import_from_kaggle(
    request: KaggleImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Import a dataset directly from Kaggle using the Kaggle API.

    Credentials can be provided in the request OR use stored credentials.
    Optionally saves credentials for future use.
    """
    from app.core.encryption import encrypt_value, decrypt_value

    # Determine which credentials to use
    kaggle_username = request.kaggle_username
    kaggle_key = request.kaggle_key

    # If credentials not provided, try to use stored ones
    if not kaggle_username or not kaggle_key:
        if current_user.kaggle_username and current_user.kaggle_key_encrypted:
            kaggle_username = current_user.kaggle_username
            kaggle_key = decrypt_value(current_user.kaggle_key_encrypted)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kaggle credentials required. Please provide credentials or save them in settings."
            )

    # Download the dataset
    df, filename, error = await KaggleService.download_dataset(
        url=request.url,
        kaggle_username=kaggle_username,
        kaggle_key=kaggle_key
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    if df is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to download dataset from Kaggle"
        )

    # Save DataFrame to file (always as parquet for efficiency)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.parquet")
    df.to_parquet(file_path, index=False)

    # Save dataset metadata
    # Use .parquet extension since that's what we actually save
    parquet_filename = f"{file_id}.parquet"
    dataset = await DataService.save_dataset(
        db=db,
        user=current_user,
        name=request.dataset_name,
        df=df,
        source_type=SourceType.URL,
        file_path=file_path,
        source_url=request.url,
        original_filename=parquet_filename,  # Use parquet filename so file_type is correct
        description=f"Imported from Kaggle: {request.url}",
    )

    result = {
        "success": True,
        "dataset_id": str(dataset.id),
        "dataset_name": dataset.name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
    }

    # Optionally create context from Kaggle API metadata
    if request.create_context:
        try:
            from app.models.context import Context, ContextStatus, ContextType
            from app.services.context_validator import ContextValidator

            # Get metadata from Kaggle API (includes description)
            metadata, meta_error = await KaggleService.get_dataset_metadata(
                url=request.url,
                kaggle_username=kaggle_username,
                kaggle_key=kaggle_key
            )

            if metadata:
                # Get column info from dataset schema
                column_info = dataset.schema.get('columns', []) if dataset.schema else []

                # Format metadata as context document
                context_content = KaggleService.format_metadata_as_context(metadata, column_info)

                title = request.dataset_name + " Context"

                # Get first part of description for context description (limit to 500 chars)
                description_text = metadata.get('description') or f"Context for {request.dataset_name} from Kaggle"
                # Clean markdown for description field
                import re
                clean_description = re.sub(r'\*\*|\*|#', '', description_text)
                clean_description = clean_description[:500].strip()
                if len(description_text) > 500:
                    clean_description += "..."

                # Build parsed context structure for validation
                parsed_context = {
                    "name": title,
                    "version": "1.0.0",
                    "description": clean_description,
                    "context_type": "single_dataset",
                    "status": "active",
                    "datasets": [{
                        "id": "primary",
                        "dataset_id": str(dataset.id),
                        "name": dataset.name,
                        "description": f"Dataset imported from Kaggle: {request.url}"
                    }]
                }

                # Validate the context
                validator = ContextValidator(db, current_user.id)
                validation_result = await validator.validate(parsed_context)

                validation_status = validation_result.get_status()
                validation_errors = validation_result.errors if validation_result.errors else None
                validation_warnings = validation_result.warnings if validation_result.warnings else None

                # Only block on actual errors, not warnings
                if validation_status == "failed":
                    result["context_error"] = f"Validation failed: {validation_errors}"
                else:
                    context = Context(
                        user_id=current_user.id,
                        name=title,
                        version="1.0.0",
                        description=clean_description,
                        context_type=ContextType.SINGLE_DATASET,
                        status=ContextStatus.ACTIVE,
                        markdown_content=context_content,
                        parsed_yaml=parsed_context,
                        datasets=[{"dataset_id": str(dataset.id), "name": dataset.name}],
                        relationships=None,
                        validation_status=validation_status,
                        validation_errors=validation_errors,
                        validation_warnings=validation_warnings
                    )

                    db.add(context)
                    await db.commit()
                    await db.refresh(context)

                    result["context_id"] = str(context.id)
                    result["context_name"] = context.name
                    if validation_warnings:
                        result["context_warnings"] = validation_warnings
            else:
                result["context_error"] = meta_error or "Could not fetch metadata from Kaggle"

        except Exception as e:
            # Context creation failed but dataset was imported successfully
            result["context_error"] = str(e)

    # Save credentials if requested and they were provided in the request
    if request.save_credentials and request.kaggle_username and request.kaggle_key:
        try:
            current_user.kaggle_username = request.kaggle_username
            current_user.kaggle_key_encrypted = encrypt_value(request.kaggle_key)
            await db.commit()
            result["credentials_saved"] = True
        except Exception:
            result["credentials_saved"] = False

    return result


@router.post("/validate-kaggle-credentials")
async def validate_kaggle_credentials(
    kaggle_username: str,
    kaggle_key: str,
    current_user: User = Depends(get_current_user),
):
    """
    Validate Kaggle API credentials.
    """
    is_valid, message = KaggleService.validate_credentials(kaggle_username, kaggle_key)

    return {
        "valid": is_valid,
        "message": message
    }
