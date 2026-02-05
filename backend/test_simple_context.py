"""
Test script for Simple Context Format
Demonstrates creating contexts with plain markdown (no YAML)
"""

import asyncio
import sys
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, '/Users/pallavichandrashekar/Codex/insight-forge/backend')

from app.services.context_service import ContextService, ContextServiceError

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///insightforge.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def test_simple_context_format():
    """Test creating a context with plain markdown (no YAML)"""
    print("=" * 70)
    print("TEST: Simple Context Format (Plain Markdown)")
    print("=" * 70)

    # Sample plain markdown content (no YAML frontmatter)
    simple_content = """# About Dataset
📦 Amazon Reviews & AI Narratives Dataset

## 📖 Overview
This dataset contains structured information for ~5,000 Amazon products enriched with AI-generated review narratives. It combines product metadata (category, pricing, ratings, links) with natural language summaries generated using large language models (LLMs).

The dataset is suitable for NLP research, data science projects, recommendation systems, product analytics, and machine learning experimentation.

## 📊 Key Fields
- Product name and categories
- Ratings and number of reviews
- Pricing information
- Product links
- AI-generated narratives
- Selected best model
- Evaluation score

## 🧠 Potential Use Cases
- Natural Language Processing (summarization, text quality evaluation)
- Product review analysis
- Recommender systems
- Sentiment analysis
- E-commerce analytics
- Dataset for ML / AI portfolios
- Prompt engineering research
- Feature engineering projects
"""

    # Use existing dataset from database
    dataset_id = UUID("38875e33-0d72-4df6-bfaf-792e11f40015")
    user_id = UUID("d9294895-bf0c-4ea0-a768-ada263f616f9")

    async with AsyncSessionLocal() as db:
        context_service = ContextService(db)

        print("\n📝 Creating context with simple markdown format...")
        print(f"   Dataset ID: {dataset_id}")
        print(f"   Content length: {len(simple_content)} characters")
        print(f"   Format: Plain markdown (no YAML)")

        try:
            # Create context with simple format
            context = await context_service.create_context(
                user_id=user_id,
                content=simple_content,
                validate=True,
                dataset_id=dataset_id  # Required for simple format
            )

            print("\n✅ SUCCESS: Context created!")
            print(f"\n📋 Context Details:")
            print(f"   ID: {context.id}")
            print(f"   Name: {context.name}")
            print(f"   Version: {context.version}")
            print(f"   Type: {context.context_type.value}")
            print(f"   Status: {context.status.value}")
            print(f"   Description: {context.description[:100]}...")
            print(f"\n📊 Datasets linked: {len(context.datasets)}")
            for ds in context.datasets:
                print(f"   - {ds.get('name')} (ID: {ds.get('dataset_id')})")

            print(f"\n📄 Markdown content preview:")
            print(f"   {context.markdown_content[:200]}...")

            return context

        except ContextServiceError as e:
            print(f"\n❌ FAIL: {str(e)}")
            return None


async def test_structured_vs_simple():
    """Compare structured (YAML) vs simple (plain markdown) formats"""
    print("\n" + "=" * 70)
    print("COMPARISON: Structured vs Simple Format")
    print("=" * 70)

    print("\n📝 STRUCTURED FORMAT (with YAML):")
    print("-" * 70)
    structured_example = """---
name: "Internet Usage Analysis"
version: "1.0.0"
description: "Daily internet usage patterns"
datasets:
  - id: "usage"
    name: "Internet Usage"
    dataset_id: "38875e33-0d72-4df6-bfaf-792e11f40015"
metrics:
  - id: "avg_screen_time"
    expression: "AVG(total_screen_time)"
---

# Internet Usage Analysis

This dataset tracks daily internet usage patterns...
"""
    print(structured_example)

    print("\n📝 SIMPLE FORMAT (plain markdown):")
    print("-" * 70)
    simple_example = """# Internet Usage Analysis

This dataset tracks daily internet usage patterns...

## Key Metrics
- Average screen time
- Social media usage
- Device preferences
"""
    print(simple_example)

    print("\n🔍 Key Differences:")
    print("   Structured: Full control, metrics, glossary, filters")
    print("   Simple: Just description, auto-generated metadata")
    print("\n✨ Benefits of Simple Format:")
    print("   ✅ No YAML knowledge required")
    print("   ✅ Write natural markdown documentation")
    print("   ✅ Quick to create")
    print("   ✅ Perfect for basic contexts")
    print("\n⚙️  When to use Structured Format:")
    print("   ✅ Need pre-defined metrics")
    print("   ✅ Need business glossary terms")
    print("   ✅ Need custom filters")
    print("   ✅ Multi-dataset relationships")


async def test_backward_compatibility():
    """Test that old structured format still works"""
    print("\n" + "=" * 70)
    print("TEST: Backward Compatibility (Structured Format)")
    print("=" * 70)

    structured_content = """---
name: "Test Backward Compatibility"
version: "1.0.0"
description: "Testing that old format still works"
datasets:
  - id: "test"
    name: "Test Dataset"
    dataset_id: "38875e33-0d72-4df6-bfaf-792e11f40015"
---

# Test Context

This is a test of the structured format.
"""

    user_id = UUID("d9294895-bf0c-4ea0-a768-ada263f616f9")

    async with AsyncSessionLocal() as db:
        context_service = ContextService(db)

        print("\n📝 Creating context with structured format (original)...")

        try:
            context = await context_service.create_context(
                user_id=user_id,
                content=structured_content,
                validate=True
                # No dataset_id needed for structured format
            )

            print("\n✅ SUCCESS: Structured format still works!")
            print(f"   Name: {context.name}")
            print(f"   Version: {context.version}")
            print("\n✨ Backward compatibility maintained!")

            return context

        except ContextServiceError as e:
            print(f"\n❌ FAIL: {str(e)}")
            return None


async def run_all_tests():
    """Run all simple context tests"""
    print("\n" + "=" * 70)
    print("SIMPLE CONTEXT FORMAT - TEST SUITE")
    print("=" * 70)

    # Test 1: Simple format
    context1 = await test_simple_context_format()

    # Test 2: Comparison
    await test_structured_vs_simple()

    # Test 3: Backward compatibility
    context2 = await test_backward_compatibility()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)

    if context1 and context2:
        print("\n✅ All tests passed!")
        print("\n📊 Summary:")
        print("   ✅ Simple format works (plain markdown)")
        print("   ✅ Structured format works (YAML + markdown)")
        print("   ✅ Backward compatibility maintained")
        print("\n💡 Usage:")
        print("   - Use simple format for quick documentation")
        print("   - Use structured format for advanced features")
    else:
        print("\n⚠️  Some tests failed. Check output above.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
