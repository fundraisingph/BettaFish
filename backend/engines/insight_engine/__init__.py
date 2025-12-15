"""
InsightEngine FastAPI Implementation
Database mining and sentiment analysis agent for BettaFish
"""

from .api.routes import router as insight_router
from .services.insight_service import InsightService
from .models.schemas import *

__all__ = ["insight_router", "InsightService"]