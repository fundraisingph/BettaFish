"""
Core module for BettaFish backend.

Contains configuration, database, and utility functions.
"""

from .config import settings
from .database import get_db_connection, get_transaction

__all__ = ["settings", "get_prisma", "get_transaction"]