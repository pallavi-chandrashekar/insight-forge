"""Populate context_id for existing datasets based on contexts

This script should be run once after the Phase 2 migration to populate
the context_id foreign key for all existing datasets.

Usage:
    cd backend
    python scripts/populate_dataset_context_ids.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.context import Context
from app.services.context_service import ContextService
from app.core.config import settings


async def populate_existing_datasets():
    """Populate context_id for all existing datasets"""
    print("🚀 Starting dataset context_id population...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print()

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        # Get all contexts
        result = await db.execute(select(Context))
        contexts = result.scalars().all()

        if not contexts:
            print("⚠️  No contexts found in database")
            return

        print(f"📁 Found {len(contexts)} contexts to process")
        print()

        context_service = ContextService(db)
        success_count = 0
        error_count = 0

        for i, context in enumerate(contexts, 1):
            try:
                print(f"[{i}/{len(contexts)}] Processing: {context.name} (v{context.version})")

                # Count datasets in this context
                dataset_count = len(context.datasets) if context.datasets else 0
                print(f"  📦 Datasets in context: {dataset_count}")

                if dataset_count == 0:
                    print("  ⏭️  Skipping (no datasets)")
                    print()
                    continue

                # Auto-populate
                await context_service._auto_populate_dataset_context_ids(context)

                print(f"  ✅ Updated datasets for context {context.id}")
                success_count += 1

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                error_count += 1

            print()

    print("=" * 60)
    print("✨ Population complete!")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(populate_existing_datasets())
