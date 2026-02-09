"""
Simple caching for context chat responses

Caches frequently asked questions to reduce API costs and improve response time.
"""

import hashlib
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from collections import OrderedDict


class ChatCache:
    """
    Simple LRU cache for chat responses.

    Uses in-memory storage with TTL (Time To Live).
    Can be upgraded to Redis for distributed caching.
    """

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached items (LRU eviction)
            ttl_hours: Time to live for cached items in hours
        """
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.hits = 0
        self.misses = 0

    def _generate_key(
        self,
        context_id: str,
        question: str,
        conversation_history: Optional[List[dict]] = None
    ) -> str:
        """
        Generate cache key from context ID and question.

        Args:
            context_id: Context UUID
            question: User's question
            conversation_history: Previous conversation (optional)

        Returns:
            Cache key (hash)
        """
        # For simplicity, only cache questions without conversation history
        # (First-time questions are most common and valuable to cache)
        if conversation_history:
            return None  # Don't cache follow-ups for now

        # Normalize question (lowercase, strip whitespace)
        normalized_question = question.lower().strip()

        # Create cache key
        key_data = f"{context_id}:{normalized_question}"
        cache_key = hashlib.md5(key_data.encode()).hexdigest()

        return cache_key

    def get(
        self,
        context_id: str,
        question: str,
        conversation_history: Optional[List[dict]] = None
    ) -> Optional[Dict]:
        """
        Get cached response if available.

        Args:
            context_id: Context UUID
            question: User's question
            conversation_history: Previous conversation

        Returns:
            Cached response dict or None
        """
        cache_key = self._generate_key(context_id, question, conversation_history)

        if not cache_key:
            return None

        if cache_key in self.cache:
            cached_item = self.cache[cache_key]

            # Check if expired
            if datetime.now() - cached_item['timestamp'] > self.ttl:
                # Expired, remove it
                del self.cache[cache_key]
                self.misses += 1
                return None

            # Move to end (mark as recently used)
            self.cache.move_to_end(cache_key)

            self.hits += 1
            return cached_item['response']

        self.misses += 1
        return None

    def set(
        self,
        context_id: str,
        question: str,
        response: Dict,
        conversation_history: Optional[List[dict]] = None
    ):
        """
        Cache a response.

        Args:
            context_id: Context UUID
            question: User's question
            response: Response to cache
            conversation_history: Previous conversation
        """
        cache_key = self._generate_key(context_id, question, conversation_history)

        if not cache_key:
            return  # Don't cache follow-ups

        # Evict oldest item if cache is full
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest (first) item

        # Add to cache
        self.cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now(),
            'question': question,
            'context_id': context_id
        }

    def clear_context(self, context_id: str):
        """
        Clear all cached responses for a specific context.

        Useful when context is updated.

        Args:
            context_id: Context UUID to clear
        """
        keys_to_remove = [
            key for key, value in self.cache.items()
            if value['context_id'] == context_id
        ]

        for key in keys_to_remove:
            del self.cache[key]

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests
        }


# Global cache instance
_chat_cache_instance = None


def get_chat_cache() -> ChatCache:
    """Get or create global chat cache instance."""
    global _chat_cache_instance
    if _chat_cache_instance is None:
        _chat_cache_instance = ChatCache(max_size=1000, ttl_hours=24)
    return _chat_cache_instance
