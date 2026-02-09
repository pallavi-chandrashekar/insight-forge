"""
Documentation Chunking and Semantic Search

For large documentation (>50KB), chunks content and finds most relevant sections.
This improves context window usage and answer quality.
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import math


class DocumentChunk:
    """Represents a chunk of documentation."""

    def __init__(self, content: str, section: str, start_line: int, end_line: int):
        self.content = content
        self.section = section
        self.start_line = start_line
        self.end_line = end_line
        self.word_count = len(content.split())

    def __repr__(self):
        return f"<Chunk: {self.section} ({self.word_count} words)>"


class DocChunker:
    """
    Chunks documentation and finds relevant sections based on questions.

    Strategy:
    1. Split documentation by markdown headers
    2. Rank chunks by relevance to question (TF-IDF-like scoring)
    3. Return top N most relevant chunks
    """

    # Threshold for using chunking (50KB)
    CHUNKING_THRESHOLD = 50 * 1024

    @classmethod
    def should_chunk(cls, markdown_content: str) -> bool:
        """
        Determine if documentation should be chunked.

        Args:
            markdown_content: Full documentation text

        Returns:
            True if content is large enough to benefit from chunking
        """
        return len(markdown_content) > cls.CHUNKING_THRESHOLD

    @classmethod
    def chunk_by_sections(cls, markdown_content: str) -> List[DocumentChunk]:
        """
        Split documentation into chunks based on markdown headers.

        Args:
            markdown_content: Full documentation markdown

        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        lines = markdown_content.split('\n')

        current_section = "Introduction"
        current_content = []
        section_start_line = 1

        for i, line in enumerate(lines, 1):
            # Check for markdown header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # Save previous chunk if it has content
                if current_content:
                    chunk_text = '\n'.join(current_content)
                    if chunk_text.strip():
                        chunks.append(DocumentChunk(
                            content=chunk_text,
                            section=current_section,
                            start_line=section_start_line,
                            end_line=i - 1
                        ))

                # Start new section
                current_section = header_match.group(2).strip()
                current_content = [line]
                section_start_line = i
            else:
                current_content.append(line)

        # Add final chunk
        if current_content:
            chunk_text = '\n'.join(current_content)
            if chunk_text.strip():
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    section=current_section,
                    start_line=section_start_line,
                    end_line=len(lines)
                ))

        return chunks

    @classmethod
    def find_relevant_chunks(
        cls,
        chunks: List[DocumentChunk],
        question: str,
        max_chunks: int = 5,
        max_total_words: int = 8000
    ) -> List[DocumentChunk]:
        """
        Find most relevant chunks for a question.

        Uses keyword matching and TF-IDF-like scoring.

        Args:
            chunks: List of DocumentChunk objects
            question: User's question
            max_chunks: Maximum number of chunks to return
            max_total_words: Maximum total words across all chunks

        Returns:
            List of most relevant chunks
        """
        if not chunks:
            return []

        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            score = cls._calculate_relevance_score(chunk, question)
            scored_chunks.append((chunk, score))

        # Sort by score (descending)
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # Select top chunks within word limit
        selected_chunks = []
        total_words = 0

        for chunk, score in scored_chunks:
            if len(selected_chunks) >= max_chunks:
                break

            if total_words + chunk.word_count > max_total_words:
                # Check if we can fit this chunk
                if total_words < max_total_words * 0.8:  # Use at least 80% of budget
                    continue  # Try next chunk
                else:
                    break  # We've used enough

            selected_chunks.append(chunk)
            total_words += chunk.word_count

        # Sort selected chunks by original order (maintain document flow)
        selected_chunks.sort(key=lambda x: x.start_line)

        return selected_chunks

    @classmethod
    def _calculate_relevance_score(cls, chunk: DocumentChunk, question: str) -> float:
        """
        Calculate relevance score for a chunk based on question.

        Uses:
        - Keyword overlap
        - Section title match
        - Code block presence (if question is about how-to)

        Args:
            chunk: DocumentChunk to score
            question: User's question

        Returns:
            Relevance score (higher is better)
        """
        score = 0.0

        # Extract keywords from question
        question_keywords = cls._extract_keywords(question.lower())

        # Extract keywords from chunk
        chunk_keywords = cls._extract_keywords(chunk.content.lower())
        section_keywords = cls._extract_keywords(chunk.section.lower())

        # Calculate keyword overlap with chunk content
        content_overlap = len(question_keywords & chunk_keywords)
        score += content_overlap * 2  # Weight: 2 points per matching keyword

        # Calculate keyword overlap with section title (higher weight)
        section_overlap = len(question_keywords & section_keywords)
        score += section_overlap * 5  # Weight: 5 points for section title match

        # Boost if question contains "how" and chunk has code blocks
        if any(word in question.lower() for word in ['how', 'example', 'show']):
            if '```' in chunk.content:
                score += 10  # Boost for code examples

        # Boost if question asks for specific term in section title
        for keyword in question_keywords:
            if keyword in chunk.section.lower():
                score += 3

        return score

    @classmethod
    def _extract_keywords(cls, text: str) -> set:
        """
        Extract keywords from text.

        Removes common stop words and short words.

        Args:
            text: Input text

        Returns:
            Set of keywords
        """
        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'than', 'too', 'very'
        }

        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter stop words and short words
        keywords = {
            word for word in words
            if word not in stop_words and len(word) > 2
        }

        return keywords

    @classmethod
    def reconstruct_context(cls, chunks: List[DocumentChunk]) -> str:
        """
        Reconstruct documentation context from selected chunks.

        Args:
            chunks: List of selected chunks

        Returns:
            Reconstructed markdown text
        """
        parts = []

        for chunk in chunks:
            parts.append(f"## {chunk.section}")
            parts.append(chunk.content)
            parts.append("")  # Empty line between sections

        return "\n".join(parts)
