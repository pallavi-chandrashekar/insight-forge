"""
Source Citation Extractor for Documentation Chat

Identifies which sections of documentation were used to answer questions.
"""

import re
from typing import List, Dict, Optional
from difflib import SequenceMatcher


class SourceExtractor:
    """
    Extracts source citations from documentation based on LLM response.

    Methods:
    - Find quoted text in documentation
    - Extract relevant sections
    - Provide line numbers and section headers
    """

    @classmethod
    def extract_sources(
        cls,
        markdown_content: str,
        answer: str,
        max_sources: int = 5
    ) -> List[Dict[str, any]]:
        """
        Extract source citations from documentation.

        Strategy:
        1. Find code blocks quoted in answer
        2. Find text snippets that match documentation
        3. Identify section headers near those snippets
        4. Return source references with context

        Args:
            markdown_content: Full documentation markdown
            answer: LLM's answer text
            max_sources: Maximum number of sources to return

        Returns:
            List of source dicts with section, text, and line numbers
        """
        sources = []

        # Extract code blocks from answer
        code_blocks_in_answer = cls._extract_code_blocks(answer)

        # Find matching code blocks in documentation
        for code_block in code_blocks_in_answer:
            source = cls._find_code_in_docs(code_block, markdown_content)
            if source:
                sources.append(source)

        # Extract quoted text from answer
        quoted_texts = cls._extract_quoted_text(answer)

        # Find matching quotes in documentation
        for quote in quoted_texts:
            # Skip if too short
            if len(quote.strip()) < 20:
                continue

            source = cls._find_text_in_docs(quote, markdown_content)
            if source:
                sources.append(source)

        # Remove duplicates and limit
        unique_sources = cls._deduplicate_sources(sources)

        return unique_sources[:max_sources]

    @classmethod
    def _extract_code_blocks(cls, text: str) -> List[str]:
        """Extract code blocks from markdown text."""
        pattern = r'```(?:python|py)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [match.strip() for match in matches if match.strip()]

    @classmethod
    def _extract_quoted_text(cls, text: str) -> List[str]:
        """Extract quoted text (> quotes or "quotes")."""
        quotes = []

        # Extract > blockquotes
        blockquote_pattern = r'^>\s*(.+)$'
        blockquotes = re.findall(blockquote_pattern, text, re.MULTILINE)
        quotes.extend(blockquotes)

        # Extract "quoted text"
        quote_pattern = r'"([^"]{20,})"'
        quoted = re.findall(quote_pattern, text)
        quotes.extend(quoted)

        return quotes

    @classmethod
    def _find_code_in_docs(cls, code: str, markdown_content: str) -> Optional[Dict]:
        """Find code block in documentation and return source reference."""
        # Normalize code (remove extra whitespace)
        normalized_code = ' '.join(code.split())

        # Extract all code blocks from documentation
        doc_code_blocks = cls._extract_code_blocks(markdown_content)

        for doc_code in doc_code_blocks:
            normalized_doc_code = ' '.join(doc_code.split())

            # Check similarity
            similarity = SequenceMatcher(None, normalized_code, normalized_doc_code).ratio()

            if similarity > 0.7:  # 70% match threshold
                # Find this code's location in the markdown
                line_num = cls._find_line_number(markdown_content, doc_code)
                section = cls._find_section_header(markdown_content, line_num)

                return {
                    "type": "code",
                    "section": section,
                    "text": doc_code[:200] + ("..." if len(doc_code) > 200 else ""),
                    "line_number": line_num,
                    "match_confidence": similarity
                }

        return None

    @classmethod
    def _find_text_in_docs(cls, quote: str, markdown_content: str) -> Optional[Dict]:
        """Find quoted text in documentation and return source reference."""
        # Normalize quote
        normalized_quote = ' '.join(quote.split()).lower()

        # Search in documentation
        normalized_content = markdown_content.lower()

        # Find with fuzzy matching
        if normalized_quote in normalized_content:
            # Find line number
            line_num = cls._find_line_number(markdown_content, quote)
            section = cls._find_section_header(markdown_content, line_num)

            return {
                "type": "quote",
                "section": section,
                "text": quote[:200] + ("..." if len(quote) > 200 else ""),
                "line_number": line_num,
                "match_confidence": 1.0
            }

        return None

    @classmethod
    def _find_line_number(cls, content: str, search_text: str) -> int:
        """Find line number of text in content."""
        lines = content.split('\n')
        normalized_search = ' '.join(search_text.split()).lower()

        for i, line in enumerate(lines, 1):
            normalized_line = ' '.join(line.split()).lower()
            if normalized_search[:50] in normalized_line or normalized_line in normalized_search:
                return i

        return 0

    @classmethod
    def _find_section_header(cls, content: str, line_number: int) -> str:
        """Find the section header above a given line number."""
        lines = content.split('\n')

        if line_number == 0 or line_number > len(lines):
            return "Documentation"

        # Search backwards for header
        for i in range(line_number - 1, -1, -1):
            line = lines[i]
            # Check for markdown headers (# Header)
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                return match.group(2).strip()

        return "Documentation"

    @classmethod
    def _deduplicate_sources(cls, sources: List[Dict]) -> List[Dict]:
        """Remove duplicate sources based on line numbers."""
        seen_lines = set()
        unique_sources = []

        for source in sources:
            line = source.get('line_number', 0)
            if line not in seen_lines:
                seen_lines.add(line)
                unique_sources.append(source)

        # Sort by line number
        unique_sources.sort(key=lambda x: x.get('line_number', 0))

        return unique_sources
