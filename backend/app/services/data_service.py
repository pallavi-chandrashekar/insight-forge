import os
import aiohttp
import pandas as pd
from io import BytesIO
from typing import Optional, Any
from uuid import UUID
from fastapi import UploadFile
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.dataset import Dataset, SourceType
from app.models.user import User
from app.models.context import Context


class DataService:
    """Service for data import and processing"""

    SUPPORTED_EXTENSIONS = {
        ".csv": "csv",
        ".json": "json",
        ".xlsx": "excel",
        ".xls": "excel",
        ".parquet": "parquet",
    }

    @staticmethod
    def get_file_type(filename: str) -> Optional[str]:
        """Get file type from filename extension"""
        ext = os.path.splitext(filename.lower())[1]
        return DataService.SUPPORTED_EXTENSIONS.get(ext)

    @staticmethod
    async def parse_file(file: UploadFile) -> pd.DataFrame:
        """Parse uploaded file to DataFrame"""
        content = await file.read()
        file_type = DataService.get_file_type(file.filename)

        if file_type == "csv":
            return pd.read_csv(BytesIO(content))
        elif file_type == "json":
            try:
                return pd.read_json(BytesIO(content))
            except ValueError:
                import json
                data = json.loads(content)
                if isinstance(data, list):
                    return pd.json_normalize(data)
                return pd.json_normalize([data])
        elif file_type == "excel":
            return pd.read_excel(BytesIO(content))
        elif file_type == "parquet":
            return pd.read_parquet(BytesIO(content))
        else:
            raise ValueError(f"Unsupported file type: {file.filename}")

    @staticmethod
    async def fetch_url(url: str) -> pd.DataFrame:
        """Fetch data from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
                content_type = response.headers.get("Content-Type", "")

                if "csv" in content_type or url.endswith(".csv"):
                    return pd.read_csv(BytesIO(content))
                elif "json" in content_type or url.endswith(".json"):
                    try:
                        return pd.read_json(BytesIO(content))
                    except ValueError:
                        import json
                        data = json.loads(content)
                        if isinstance(data, list):
                            return pd.json_normalize(data)
                        return pd.json_normalize([data])
                elif url.endswith(".xlsx") or url.endswith(".xls"):
                    return pd.read_excel(BytesIO(content))
                elif url.endswith(".parquet"):
                    return pd.read_parquet(BytesIO(content))
                else:
                    try:
                        return pd.read_csv(BytesIO(content))
                    except Exception:
                        return pd.read_json(BytesIO(content))

    @staticmethod
    async def scrape_webpage(url: str, selector: Optional[str] = None) -> pd.DataFrame:
        """Scrape table data from webpage"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "lxml")

        if selector:
            element = soup.select_one(selector)
            if element and element.name == "table":
                tables = pd.read_html(str(element))
                if tables:
                    return tables[0]
            raise ValueError(f"No table found with selector: {selector}")
        else:
            tables = pd.read_html(html)
            if not tables:
                raise ValueError("No tables found on the page")
            return tables[0]

    @staticmethod
    def infer_schema(df: pd.DataFrame) -> dict[str, Any]:
        """Infer schema from DataFrame"""
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample_values = df[col].dropna().head(3).tolist()
            columns.append({
                "name": str(col),
                "dtype": dtype,
                "nullable": bool(df[col].isnull().any()),
                "sample_values": sample_values,
            })

        return {
            "columns": columns,
            "total_rows": len(df),
            "total_columns": len(df.columns),
        }

    @staticmethod
    async def save_dataset(
        db: AsyncSession,
        user: User,
        name: str,
        df: pd.DataFrame,
        source_type: SourceType,
        file_path: Optional[str] = None,
        original_filename: Optional[str] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dataset:
        """Save dataset metadata to database"""
        schema = DataService.infer_schema(df)

        dataset = Dataset(
            user_id=user.id,
            name=name,
            description=description,
            source_type=source_type,
            source_url=source_url,
            file_path=file_path,
            original_filename=original_filename,
            file_size=os.path.getsize(file_path) if file_path and os.path.exists(file_path) else None,
            file_type=DataService.get_file_type(original_filename) if original_filename else None,
            schema=schema,
            row_count=len(df),
            column_count=len(df.columns),
        )

        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        return dataset

    @staticmethod
    async def get_dataset(db: AsyncSession, dataset_id: UUID, user_id: UUID) -> Optional[Dataset]:
        """Get dataset by ID for a specific user"""
        result = await db.execute(
            select(Dataset).where(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_datasets(db: AsyncSession, user_id: UUID) -> list[Dataset]:
        """Get all datasets for a user"""
        result = await db.execute(
            select(Dataset).where(Dataset.user_id == user_id).order_by(Dataset.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def check_context_dependencies(db: AsyncSession, dataset: Dataset) -> dict:
        """
        Check if the dataset's context is linked to other datasets.

        Returns:
            dict with:
            - has_context: bool
            - context_id: str or None
            - context_name: str or None
            - other_datasets: list of {id, name} for other datasets using same context
            - can_delete_directly: bool (True if no other datasets use the context)
        """
        if not dataset.context_id:
            return {
                "has_context": False,
                "context_id": None,
                "context_name": None,
                "other_datasets": [],
                "can_delete_directly": True
            }

        # Get the context
        context = await db.get(Context, dataset.context_id)
        if not context:
            return {
                "has_context": False,
                "context_id": None,
                "context_name": None,
                "other_datasets": [],
                "can_delete_directly": True
            }

        # Find other datasets linked to the same context
        result = await db.execute(
            select(Dataset).where(
                Dataset.context_id == dataset.context_id,
                Dataset.id != dataset.id
            )
        )
        other_datasets = result.scalars().all()

        return {
            "has_context": True,
            "context_id": str(context.id),
            "context_name": context.name,
            "other_datasets": [{"id": str(ds.id), "name": ds.name} for ds in other_datasets],
            "can_delete_directly": len(other_datasets) == 0
        }

    @staticmethod
    async def delete_dataset(
        db: AsyncSession,
        dataset: Dataset,
        delete_context: bool = True,
        delete_linked_datasets: bool = False
    ) -> dict:
        """
        Delete a dataset and optionally its linked context.

        Args:
            db: Database session
            dataset: Dataset to delete
            delete_context: If True, delete the linked context (default: True)
            delete_linked_datasets: If True, also delete other datasets linked to same context

        Returns:
            dict with deletion summary
        """
        deleted_datasets = []
        deleted_context = None

        context_id = dataset.context_id
        context = None

        if context_id:
            context = await db.get(Context, context_id)

        # If deleting linked datasets too
        if delete_linked_datasets and context_id:
            # Find and delete all datasets linked to this context
            result = await db.execute(
                select(Dataset).where(Dataset.context_id == context_id)
            )
            linked_datasets = result.scalars().all()

            for ds in linked_datasets:
                if ds.file_path and os.path.exists(ds.file_path):
                    os.remove(ds.file_path)
                deleted_datasets.append({"id": str(ds.id), "name": ds.name})
                await db.delete(ds)
        else:
            # Just delete this dataset
            if dataset.file_path and os.path.exists(dataset.file_path):
                os.remove(dataset.file_path)
            deleted_datasets.append({"id": str(dataset.id), "name": dataset.name})
            await db.delete(dataset)

        # Delete context if requested and exists
        if delete_context and context:
            deleted_context = {"id": str(context.id), "name": context.name}
            await db.delete(context)

        await db.commit()

        return {
            "deleted_datasets": deleted_datasets,
            "deleted_context": deleted_context
        }

    @staticmethod
    def load_dataframe(dataset: Dataset) -> pd.DataFrame:
        """Load DataFrame from stored dataset"""
        if not dataset.file_path or not os.path.exists(dataset.file_path):
            raise ValueError("Dataset file not found")

        file_type = dataset.file_type
        if file_type == "csv":
            return pd.read_csv(dataset.file_path)
        elif file_type == "json":
            return pd.read_json(dataset.file_path)
        elif file_type == "excel":
            return pd.read_excel(dataset.file_path)
        elif file_type == "parquet":
            return pd.read_parquet(dataset.file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def get_preview(df: pd.DataFrame, limit: int = 100) -> dict[str, Any]:
        """Get preview of DataFrame"""
        preview_df = df.head(limit)
        return {
            "columns": list(df.columns),
            "data": preview_df.to_dict(orient="records"),
            "total_rows": len(df),
            "preview_rows": len(preview_df),
        }
