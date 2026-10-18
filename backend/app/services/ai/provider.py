from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from app.schemas.xero import ProjectPlan, ChatMessage


class AIProvider(ABC):
    """Abstract interface for creative copilot AI providers."""

    @abstractmethod
    def generate_project_plan(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        existing_plan: Optional[ProjectPlan] = None,
    ) -> Tuple[Optional[ProjectPlan], str, List[str], Optional[str]]:
        """
        Processes user intent and conversation context.
        Returns:
            Tuple[
                Optional[ProjectPlan]: The generated or refined plan (None if more clarification needed),
                str: Conversational reply message to user,
                List[str]: Follow-up questions/prompts (empty if plan generated),
                Optional[str]: Scope/budget warning if detected
            ]
        """
        pass
