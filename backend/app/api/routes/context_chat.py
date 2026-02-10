"""
Context Chat API - Ask questions about documentation contexts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.context_service import ContextService
from app.services.llm_helpers import get_user_llm_service
from app.services.question_classifier import QuestionClassifier
from app.services.chat_cache import get_chat_cache
from app.services.source_extractor import SourceExtractor
from app.services.doc_chunker import DocChunker


router = APIRouter()


class ContextChatRequest(BaseModel):
    """Request to ask a question about a context"""
    context_id: str
    question: str
    conversation_history: Optional[List[dict]] = None  # For follow-up questions


class ContextChatResponse(BaseModel):
    """Response with answer about the context"""
    answer: str
    context_name: str
    context_id: str
    sources: Optional[List[str]] = None  # Relevant sections from the context
    follow_up_suggestions: Optional[List[str]] = None


@router.post("/ask", response_model=ContextChatResponse)
async def ask_context_question(
    request: ContextChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question about a documentation context.

    This allows users to query the documentation directly:
    - "What does this doc say about window functions?"
    - "Explain the best practices mentioned"
    - "What are the key concepts?"
    """
    # Get the context
    context_service = ContextService(db)

    try:
        context_id = UUID(request.context_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid context ID format"
        )

    context = await context_service.get_context(context_id, current_user.id)

    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )

    # Check cache first
    cache = get_chat_cache()
    cached_response = cache.get(
        context_id=str(context_id),
        question=request.question,
        conversation_history=request.conversation_history
    )

    if cached_response:
        # Return cached response
        return ContextChatResponse(**cached_response)

    # Get LLM service
    llm_service = get_user_llm_service(current_user)

    # Build conversation history
    conversation = request.conversation_history or []

    # Classify question type to optimize response
    question_type, confidence = QuestionClassifier.classify(request.question)
    response_guidelines = QuestionClassifier.get_response_guidelines(question_type)

    # For large docs, use semantic search to find relevant sections
    documentation_content = context.markdown_content
    using_chunking = False

    if DocChunker.should_chunk(context.markdown_content):
        # Chunk and find relevant sections
        chunks = DocChunker.chunk_by_sections(context.markdown_content)
        relevant_chunks = DocChunker.find_relevant_chunks(
            chunks=chunks,
            question=request.question,
            max_chunks=5,
            max_total_words=8000
        )

        if relevant_chunks:
            documentation_content = DocChunker.reconstruct_context(relevant_chunks)
            using_chunking = True

    # Create prompt for documentation Q&A
    chunking_note = "\nNOTE: Large documentation was chunked. Only the most relevant sections are shown above." if using_chunking else ""

    system_prompt = f"""You are a helpful documentation assistant. You have access to the following documentation:

DOCUMENTATION TITLE: {context.name}
DESCRIPTION: {context.description}

DOCUMENTATION CONTENT:
{documentation_content}{chunking_note}

Your task is to answer questions about this documentation accurately and helpfully.

ANSWER GUIDELINES:
1. **Always include code examples** if they exist in the documentation
2. **Show practical usage** - demonstrate HOW to use concepts, not just WHAT they are
3. **Extract and display actual code snippets** from the documentation
4. **Use clear structure**: Definition → Key Features → Code Examples → Best Practices
5. **Be specific and actionable** - prefer "Here's how to create a DataFrame:" over "DataFrames can be created"
6. **Quote exact code** from the docs when available
7. If something is not mentioned in the docs, say so clearly
8. Keep explanations clear but thorough

FORMATTING:
- Use markdown for better readability
- Show code in ```python blocks
- Use bullet points for lists
- Bold important concepts

{response_guidelines}
"""

    # Build message history
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add conversation history
    for msg in conversation:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    # Add current question
    messages.append({
        "role": "user",
        "content": request.question
    })

    # Get answer from LLM
    try:
        # Use extended token limit for documentation Q&A to allow detailed responses with code examples
        answer = await llm_service.chat(messages, max_tokens=8192)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer: {str(e)}"
        )

    # Generate follow-up suggestions
    follow_up_prompt = f"""Based on this question: "{request.question}"
And this answer: "{answer}"

Suggest 3 relevant, practical follow-up questions the user might want to ask about the documentation.

MAKE SUGGESTIONS:
- Specific and actionable (e.g., "How do I create a DataFrame from a CSV file?" not "Tell me more about DataFrames")
- Natural next steps in learning (e.g., after learning what DataFrames are, ask about common operations)
- Focused on practical usage and examples

Return as a JSON array of 3 question strings.
Example: ["How do I filter rows in a DataFrame?", "What's the difference between select and filter?", "How do I save a DataFrame to a file?"]
"""

    try:
        follow_ups_raw = await llm_service.generate_structured_output(
            follow_up_prompt,
            output_format="json"
        )
        # Parse the suggestions
        import json
        follow_ups = json.loads(follow_ups_raw) if isinstance(follow_ups_raw, str) else follow_ups_raw
        if isinstance(follow_ups, list):
            follow_up_suggestions = follow_ups[:3]
        else:
            follow_up_suggestions = None
    except Exception:
        follow_up_suggestions = None

    # Extract source citations
    sources = SourceExtractor.extract_sources(
        markdown_content=context.markdown_content,
        answer=answer,
        max_sources=5
    )

    # Format sources for response
    source_citations = [
        f"{src['section']} (line {src['line_number']})" if src.get('line_number')
        else src['section']
        for src in sources
    ] if sources else None

    # Prepare response
    response_data = {
        "answer": answer,
        "context_name": context.name,
        "context_id": str(context.id),
        "sources": source_citations,
        "follow_up_suggestions": follow_up_suggestions
    }

    # Cache the response
    cache.set(
        context_id=str(context_id),
        question=request.question,
        response=response_data,
        conversation_history=request.conversation_history
    )

    return ContextChatResponse(**response_data)


@router.get("/{context_id}/summary")
async def get_context_summary(
    context_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get an AI-generated summary of a documentation context.
    """
    context_service = ContextService(db)

    try:
        ctx_id = UUID(context_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid context ID format"
        )

    context = await context_service.get_context(ctx_id, current_user.id)

    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )

    # Generate summary
    llm_service = get_user_llm_service(current_user)

    summary_prompt = f"""Analyze this documentation and provide a structured summary:

TITLE: {context.name}
DESCRIPTION: {context.description}

CONTENT:
{context.markdown_content[:5000]}  # First 5000 chars

Provide:
1. Main topics covered (3-5 bullet points)
2. Key concepts explained
3. Practical examples or patterns mentioned
4. Target audience/use cases

Format as markdown.
"""

    try:
        summary = await llm_service.generate_text(summary_prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )

    return {
        "context_id": str(context.id),
        "context_name": context.name,
        "summary": summary,
        "content_length": len(context.markdown_content)
    }


@router.get("/{context_id}/topics")
async def extract_topics(
    context_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract main topics/sections from documentation.
    """
    context_service = ContextService(db)

    try:
        ctx_id = UUID(context_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid context ID format"
        )

    context = await context_service.get_context(ctx_id, current_user.id)

    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )

    # Extract headers from markdown
    import re
    content = context.markdown_content
    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)

    # Organize by level
    topics = []
    for header in headers[:20]:  # Limit to 20 topics
        topics.append({
            "title": header.strip(),
            "type": "section"
        })

    return {
        "context_id": str(context.id),
        "context_name": context.name,
        "topics": topics,
        "total_sections": len(headers)
    }


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get chat cache statistics.

    Returns cache performance metrics.
    """
    cache = get_chat_cache()
    stats = cache.get_stats()

    return {
        "cache_stats": stats,
        "message": "Cache is improving response times and reducing API costs"
    }
