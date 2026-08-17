"""
Captain AI OS - Continuous Learning Engine (Volume 9 Part 9E)
Responsible for analyzing interaction telemetry, user preferences, tool success rates,
and adapting system behavior over time.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
import time


class FeedbackType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class FeedbackRecord(BaseModel):
    feedback_id: str
    user_id: str
    action_type: str
    feedback_type: FeedbackType
    comments: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class UserPreferenceProfile(BaseModel):
    user_id: str
    preferred_tone: str = "concise"
    favorite_tools: List[str] = Field(default_factory=list)
    confidence_adjustments: Dict[str, float] = Field(default_factory=dict)


class LearningEngine:
    """Adaptive learning engine for user preferences and tool policy tuning."""

    def __init__(self):
        self.profiles: Dict[str, UserPreferenceProfile] = {}
        self.feedback_history: List[FeedbackRecord] = []

    def get_or_create_profile(self, user_id: str) -> UserPreferenceProfile:
        """Retrieves or initializes a user preference profile."""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserPreferenceProfile(user_id=user_id)
        return self.profiles[user_id]

    def record_feedback(self, feedback: FeedbackRecord):
        """Processes feedback to adapt preference profiles and action weights."""
        self.feedback_history.append(feedback)
        profile = self.get_or_create_profile(feedback.user_id)

        action = feedback.action_type
        curr_adj = profile.confidence_adjustments.get(action, 0.0)

        if feedback.feedback_type == FeedbackType.POSITIVE:
            profile.confidence_adjustments[action] = round(curr_adj + 0.05, 2)
            if action not in profile.favorite_tools:
                profile.favorite_tools.append(action)
        elif feedback.feedback_type == FeedbackType.NEGATIVE:
            profile.confidence_adjustments[action] = round(curr_adj - 0.1, 2)
            if action in profile.favorite_tools:
                profile.favorite_tools.remove(action)

    def adapt_action_confidence(self, user_id: str, action_type: str, base_confidence: float) -> float:
        """Applies learned user preference adjustments to action confidence scores."""
        profile = self.get_or_create_profile(user_id)
        adj = profile.confidence_adjustments.get(action_type, 0.0)
        return max(0.0, min(1.0, base_confidence + adj))
