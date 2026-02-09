"""
Question Type Classification for Documentation Chat

Classifies user questions to customize response format.
"""

from enum import Enum
from typing import Tuple
import re


class QuestionType(Enum):
    """Types of questions users can ask about documentation"""
    CONCEPT = "concept"  # What is X? Explain Y
    HOW_TO = "how_to"  # How do I...? How can I...?
    TROUBLESHOOTING = "troubleshooting"  # Why doesn't...? Error with...
    COMPARISON = "comparison"  # Difference between X and Y? X vs Y?
    EXAMPLE = "example"  # Show me example, Give me example
    BEST_PRACTICE = "best_practice"  # Best practices, recommendations
    OVERVIEW = "overview"  # Summarize, Overview, Main topics


class QuestionClassifier:
    """Classifies questions to optimize response format"""

    # Patterns for each question type
    PATTERNS = {
        QuestionType.CONCEPT: [
            r'\bwhat\s+(is|are)\b',
            r'\bexplain\b',
            r'\bdefine\b',
            r'\bdefinition\b',
            r'\btell me about\b',
        ],
        QuestionType.HOW_TO: [
            r'\bhow\s+(do|can|to)\b',
            r'\bsteps to\b',
            r'\bway to\b',
            r'\bcreate\b',
            r'\bmake\b',
            r'\bimplement\b',
        ],
        QuestionType.TROUBLESHOOTING: [
            r'\bwhy\s+(doesn\'t|not|won\'t)\b',
            r'\berror\b',
            r'\bfail(s|ed|ing)?\b',
            r'\bissue\b',
            r'\bproblem\b',
            r'\bnot working\b',
            r'\bdebug\b',
        ],
        QuestionType.COMPARISON: [
            r'\bdifference\b',
            r'\bvs\b',
            r'\bversus\b',
            r'\bcompare\b',
            r'\bbetter\b',
            r'\bwhen to use\b',
            r'\bwhich one\b',
        ],
        QuestionType.EXAMPLE: [
            r'\bexample\b',
            r'\bshow me\b',
            r'\bdemo\b',
            r'\bsample\b',
            r'\billustrat\w+\b',
        ],
        QuestionType.BEST_PRACTICE: [
            r'\bbest\s+practice\b',
            r'\brecommend\w+\b',
            r'\bshould I\b',
            r'\badvice\b',
            r'\btips\b',
            r'\bguidelines\b',
        ],
        QuestionType.OVERVIEW: [
            r'\bsummar\w+\b',
            r'\boverview\b',
            r'\bmain\s+topics\b',
            r'\bkey\s+concepts\b',
            r'\bwhat\s+are\s+the\s+main\b',
            r'\blist\s+(all|the)\b',
        ],
    }

    @classmethod
    def classify(cls, question: str) -> Tuple[QuestionType, float]:
        """
        Classify a question into a type.

        Args:
            question: The user's question

        Returns:
            Tuple of (QuestionType, confidence_score)
        """
        question_lower = question.lower()

        # Check each pattern
        scores = {qtype: 0 for qtype in QuestionType}

        for qtype, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    scores[qtype] += 1

        # Find highest scoring type
        if max(scores.values()) == 0:
            # Default to CONCEPT if no patterns match
            return QuestionType.CONCEPT, 0.5

        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type] / 3, 1.0)  # Normalize to 0-1

        return best_type, confidence

    @classmethod
    def get_response_guidelines(cls, question_type: QuestionType) -> str:
        """
        Get response formatting guidelines based on question type.

        Args:
            question_type: The classified question type

        Returns:
            Specific guidelines for this question type
        """
        guidelines = {
            QuestionType.CONCEPT: """
CONCEPT EXPLANATION FORMAT:
1. Start with a clear, one-sentence definition
2. Explain key characteristics and features
3. Provide code examples if available
4. Mention common use cases
5. Compare to related concepts if helpful
""",
            QuestionType.HOW_TO: """
HOW-TO FORMAT:
1. List step-by-step instructions
2. Show complete, runnable code examples
3. Explain what each step does
4. Include common pitfalls or gotchas
5. Provide alternative approaches if any
""",
            QuestionType.TROUBLESHOOTING: """
TROUBLESHOOTING FORMAT:
1. Identify the likely cause
2. Show how to diagnose the issue
3. Provide solution with code examples
4. List common mistakes that cause this
5. Suggest preventive measures
""",
            QuestionType.COMPARISON: """
COMPARISON FORMAT:
1. Brief description of each option
2. Side-by-side comparison table or list
3. When to use each option
4. Code examples for both
5. Recommendation based on use case
""",
            QuestionType.EXAMPLE: """
EXAMPLE FORMAT:
1. Start with a complete, runnable code example
2. Explain each part of the code
3. Show expected output if available
4. Provide variations or alternatives
5. Link to related examples
""",
            QuestionType.BEST_PRACTICE: """
BEST PRACTICES FORMAT:
1. List recommended practices as bullet points
2. Explain WHY each practice is important
3. Show code examples of good vs bad
4. Mention common anti-patterns to avoid
5. Cite specific sections from documentation
""",
            QuestionType.OVERVIEW: """
OVERVIEW FORMAT:
1. High-level summary in 2-3 sentences
2. Bullet list of main topics/sections
3. Brief description of each topic
4. Suggest which topics to explore first
5. Provide navigation to detailed sections
""",
        }

        return guidelines.get(question_type, guidelines[QuestionType.CONCEPT])
