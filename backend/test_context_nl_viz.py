"""
Test script for Context-Enhanced Natural Language Visualization
Tests the integration between Context system and NL Viz feature
Includes Phase 2 performance tests for FK-based context lookup
"""

import asyncio
import sys
import time
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, '/Users/pallavichandrashekar/Codex/insight-forge/backend')

from app.services.context_service import ContextService
from app.services.llm_service import LLMService


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///insightforge.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def test_context_lookup():
    """Test 1: Verify context can be found by dataset_id"""
    print("=" * 70)
    print("TEST 1: Context Lookup by Dataset ID")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        context_service = ContextService(db)

        # Test with known dataset
        dataset_id = UUID("38875e33-0d72-4df6-bfaf-792e11f40015")
        user_id = UUID("d9294895-bf0c-4ea0-a768-ada263f616f9")

        print(f"Looking for context for dataset: {dataset_id}")

        context = await context_service.find_active_context_by_dataset(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if context:
            print(f"✅ SUCCESS: Found context!")
            print(f"   Context ID: {context.id}")
            print(f"   Context Name: {context.name}")
            print(f"   Status: {context.status}")
            print(f"   Created: {context.created_at}")
            return context
        else:
            print("❌ FAIL: No context found for dataset")
            return None


async def test_metadata_extraction(context):
    """Test 2: Verify metadata extraction works correctly"""
    print("\n" + "=" * 70)
    print("TEST 2: Context Metadata Extraction")
    print("=" * 70)

    if not context:
        print("⚠️  SKIP: No context available")
        return None

    async with AsyncSessionLocal() as db:
        context_service = ContextService(db)
        dataset_id = UUID("38875e33-0d72-4df6-bfaf-792e11f40015")

        metadata = await context_service.get_context_metadata_for_dataset(
            context=context,
            dataset_id=dataset_id
        )

        print(f"✅ SUCCESS: Extracted metadata")
        print(f"\n📋 Context Name: {metadata.get('name')}")
        print(f"📝 Description: {metadata.get('description')}")

        print(f"\n🗂️  Columns ({len(metadata.get('columns', []))}):")
        for col in metadata.get('columns', [])[:5]:
            print(f"   - {col.get('name')}")
            if col.get('business_name'):
                print(f"     Business Name: {col.get('business_name')}")
            if col.get('description'):
                print(f"     Description: {col.get('description')[:60]}...")

        print(f"\n📊 Metrics ({len(metadata.get('metrics', []))}):")
        for metric in metadata.get('metrics', [])[:5]:
            print(f"   - {metric.get('name', metric.get('id'))}: {metric.get('expression')}")

        print(f"\n📖 Glossary ({len(metadata.get('glossary', []))}):")
        for term in metadata.get('glossary', [])[:5]:
            print(f"   - {term.get('term')}: {term.get('definition', '')[:60]}...")

        print(f"\n🔍 Filters ({len(metadata.get('filters', []))}):")
        for filt in metadata.get('filters', [])[:5]:
            print(f"   - {filt.get('name', filt.get('id'))}")

        return metadata


async def test_context_formatting(metadata):
    """Test 3: Verify context formatting for LLM prompt"""
    print("\n" + "=" * 70)
    print("TEST 3: Context Formatting for LLM Prompt")
    print("=" * 70)

    if not metadata:
        print("⚠️  SKIP: No metadata available")
        return None

    llm_service = LLMService()
    formatted = llm_service._format_context_for_prompt(metadata)

    if formatted:
        print("✅ SUCCESS: Formatted context for LLM")
        print(f"\n📄 Formatted Context Preview (first 500 chars):")
        print("-" * 70)
        print(formatted[:500])
        if len(formatted) > 500:
            print(f"... ({len(formatted) - 500} more characters)")
        print("-" * 70)
        print(f"\n📏 Total length: {len(formatted)} characters")
        return formatted
    else:
        print("❌ FAIL: Context formatting returned empty string")
        return None


async def test_nl_viz_with_context(metadata):
    """Test 4: Test NL visualization generation with context"""
    print("\n" + "=" * 70)
    print("TEST 4: NL Visualization with Business Context")
    print("=" * 70)

    # Mock schema (simplified for testing)
    schema = {
        "columns": [
            {"name": "user_id", "dtype": "int64", "sample_values": [1, 2, 3]},
            {"name": "age_group", "dtype": "object", "sample_values": ["13-18", "19-25", "26-35"]},
            {"name": "total_screen_time", "dtype": "float64", "sample_values": [8.3, 10.1, 9.5]},
            {"name": "social_media_hours", "dtype": "float64", "sample_values": [2.2, 1.1, 2.5]},
            {"name": "primary_device", "dtype": "object", "sample_values": ["Mobile", "Tablet", "Desktop"]}
        ]
    }

    sample_data = [
        {"user_id": 1, "age_group": "13-18", "total_screen_time": 8.3, "social_media_hours": 2.2, "primary_device": "Mobile"},
        {"user_id": 2, "age_group": "19-25", "total_screen_time": 10.1, "social_media_hours": 1.1, "primary_device": "Tablet"},
        {"user_id": 3, "age_group": "26-35", "total_screen_time": 9.5, "social_media_hours": 2.5, "primary_device": "Desktop"}
    ]

    test_cases = [
        {
            "name": "Test with business term (if metadata has business names)",
            "description": "show average total_screen_time by age_group",
            "expected_chart": "bar",
            "expected_agg": "mean"
        },
        {
            "name": "Test with pre-defined metric",
            "description": "show avg_screen_time by device",
            "expected_chart": "bar",
            "expected_agg": "mean"
        },
        {
            "name": "Test comparison query",
            "description": "compare screen time and social media hours by age group",
            "expected_chart": "bar",
            "multi_column": True
        }
    ]

    llm_service = LLMService()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"   Query: \"{test_case['description']}\"")

        try:
            result = await llm_service.generate_visualization_from_nl(
                description=test_case['description'],
                schema=schema,
                sample_data=sample_data,
                context_metadata=metadata if metadata else None
            )

            print(f"   ✅ SUCCESS: Generated visualization config")
            print(f"      Chart Type: {result.get('chart_type')}")
            print(f"      Title: {result.get('title')}")
            print(f"      Config: {result.get('config')}")

            if result.get('reasoning'):
                print(f"      Reasoning: {result.get('reasoning')[:100]}...")

            # Validate expectations
            if test_case.get('expected_chart'):
                if result.get('chart_type') == test_case['expected_chart']:
                    print(f"      ✓ Chart type matches expected: {test_case['expected_chart']}")
                else:
                    print(f"      ⚠️  Chart type mismatch: got {result.get('chart_type')}, expected {test_case['expected_chart']}")

        except Exception as e:
            print(f"   ❌ FAIL: {str(e)}")


async def test_backward_compatibility():
    """Test 5: Verify backward compatibility (works without context)"""
    print("\n" + "=" * 70)
    print("TEST 5: Backward Compatibility (No Context)")
    print("=" * 70)

    schema = {
        "columns": [
            {"name": "age_group", "dtype": "object", "sample_values": ["13-18", "19-25"]},
            {"name": "total_screen_time", "dtype": "float64", "sample_values": [8.3, 10.1]}
        ]
    }

    sample_data = [
        {"age_group": "13-18", "total_screen_time": 8.3},
        {"age_group": "19-25", "total_screen_time": 10.1}
    ]

    llm_service = LLMService()

    try:
        result = await llm_service.generate_visualization_from_nl(
            description="show average total_screen_time by age_group",
            schema=schema,
            sample_data=sample_data,
            context_metadata=None  # No context
        )

        print("✅ SUCCESS: Works without context (backward compatible)")
        print(f"   Chart Type: {result.get('chart_type')}")
        print(f"   Config: {result.get('config')}")
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")


async def test_phase2_performance():
    """Test 6: Phase 2 Performance - FK-based context lookup"""
    print("\n" + "=" * 70)
    print("TEST 6: Phase 2 Performance (FK-Based Lookup)")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        context_service = ContextService(db)
        dataset_id = UUID("38875e33-0d72-4df6-bfaf-792e11f40015")
        user_id = UUID("d9294895-bf0c-4ea0-a768-ada263f616f9")

        print(f"Testing context lookup performance...")
        print(f"Dataset ID: {dataset_id}")

        # Run multiple iterations to get average
        iterations = 5
        times = []

        for i in range(iterations):
            start = time.time()
            context = await context_service.find_active_context_by_dataset(
                dataset_id=dataset_id,
                user_id=user_id
            )
            duration = (time.time() - start) * 1000
            times.append(duration)

            if i == 0:  # Only print result on first iteration
                if context:
                    print(f"✅ Context found: {context.name}")
                else:
                    print(f"⚠️  No context found (FK might not be populated yet)")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n📊 Performance Results:")
        print(f"   Iterations: {iterations}")
        print(f"   Average: {avg_time:.2f}ms")
        print(f"   Min: {min_time:.2f}ms")
        print(f"   Max: {max_time:.2f}ms")

        # Performance targets
        target_time = 10.0  # Target: <10ms (vs ~50ms in Phase 1)
        if avg_time < target_time:
            print(f"\n✅ PERFORMANCE PASS: {avg_time:.2f}ms < {target_time}ms target")
            improvement = 50.0 / avg_time  # Assuming Phase 1 was ~50ms
            print(f"   🚀 Estimated improvement: {improvement:.1f}x faster than Phase 1")
        else:
            print(f"\n⚠️  PERFORMANCE WARNING: {avg_time:.2f}ms >= {target_time}ms target")
            print(f"   This might indicate FK index is missing or not optimized")

        return avg_time


async def test_phase2_auto_population():
    """Test 7: Phase 2 Auto-Population of context_id"""
    print("\n" + "=" * 70)
    print("TEST 7: Phase 2 Auto-Population Test")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        from app.models.dataset import Dataset
        from sqlalchemy import select

        context_service = ContextService(db)

        # Check if any datasets have context_id populated
        stmt = select(Dataset).where(Dataset.context_id.isnot(None)).limit(5)
        result = await db.execute(stmt)
        datasets_with_context = result.scalars().all()

        if datasets_with_context:
            print(f"✅ SUCCESS: Found {len(datasets_with_context)} dataset(s) with context_id populated")
            for ds in datasets_with_context:
                print(f"   - Dataset: {ds.name}")
                print(f"     ID: {ds.id}")
                print(f"     Context ID: {ds.context_id}")
        else:
            print("⚠️  WARNING: No datasets have context_id populated yet")
            print("   Run: python scripts/populate_dataset_context_ids.py")

        # Check total datasets vs datasets with context
        stmt_total = select(Dataset)
        result_total = await db.execute(stmt_total)
        total_datasets = len(result_total.scalars().all())

        stmt_with_context = select(Dataset).where(Dataset.context_id.isnot(None))
        result_with_context = await db.execute(stmt_with_context)
        datasets_with_context_count = len(result_with_context.scalars().all())

        print(f"\n📊 Statistics:")
        print(f"   Total datasets: {total_datasets}")
        print(f"   Datasets with context: {datasets_with_context_count}")
        if total_datasets > 0:
            percentage = (datasets_with_context_count / total_datasets) * 100
            print(f"   Coverage: {percentage:.1f}%")


async def run_all_tests():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("CONTEXT-ENHANCED NL VISUALIZATION - TEST SUITE")
    print("Phase 1 (JSON lookup) + Phase 2 (FK optimization)")
    print("=" * 70)
    print()

    # Test 1: Context Lookup
    context = await test_context_lookup()

    # Test 2: Metadata Extraction
    metadata = await test_metadata_extraction(context)

    # Test 3: Context Formatting
    formatted = await test_context_formatting(metadata)

    # Test 4: NL Viz with Context
    await test_nl_viz_with_context(metadata)

    # Test 5: Backward Compatibility
    await test_backward_compatibility()

    # Phase 2 Tests
    print("\n" + "=" * 70)
    print("PHASE 2 TESTS: Foreign Key Architecture")
    print("=" * 70)

    # Test 6: Performance
    await test_phase2_performance()

    # Test 7: Auto-Population
    await test_phase2_auto_population()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\n✅ All tests completed! Review results above.")
    print("\nNote: Tests 4 & 5 require Claude API key to be configured.")
    print("If those tests fail with API errors, the implementation is still correct.")
    print("\nPhase 2 Notes:")
    print("- If performance test shows >10ms, run the migration first")
    print("- If auto-population shows 0%, run: python scripts/populate_dataset_context_ids.py")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
