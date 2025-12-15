"""
MediaEngine - Multimodal Content Analysis Engine

This engine provides comprehensive media content analysis capabilities including:
- Multimodal search across web and social media
- Content analysis with sentiment detection
- Image and video processing
- Research and report generation
"""

from .agent import DeepSearchAgent
from .state.state import State as ResearchState

__version__ = "1.0.0"
__author__ = "BettaFish Team"

__all__ = [
    "DeepSearchAgent",
    "ResearchState",
]