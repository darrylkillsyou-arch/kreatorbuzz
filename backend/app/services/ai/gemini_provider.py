import json
import logging
from typing import List, Optional, Tuple, Dict, Any
from app.config import settings
from app.schemas.xero import ProjectPlan, ChatMessage
from app.services.ai.provider import AIProvider
from app.services.ai.fallback_provider import (
    FallbackAIProvider,
    sanitize_category,
    generate_budget_breakdown,
    generate_milestones,
    check_scope_and_budget,
    VALID_CATEGORIES,
)

logger = logging.getLogger(__name__)


class GeminiAIProvider(AIProvider):
    """Google Gemini AI integration for Xero AI 2.0 with strict fallback protection."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.fallback = FallbackAIProvider()

    def generate_project_plan(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        existing_plan: Optional[ProjectPlan] = None,
    ) -> Tuple[Optional[ProjectPlan], str, List[str], Optional[str]]:
        if not self.api_key:
            return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            system_instruction = (
                "You are Xero AI, the premier Creative Project Copilot for CODE XERO, an elite AI creator marketplace in India. "
                "Your mission: Help brands, agencies, and directors articulate, structure, and refine high-end creative visual projects. "
                "CRITICAL RULES: "
                "1. If the user's intent is very vague or underspecified (e.g. 'I want something cool for my brand'), DO NOT invent arbitrary specifications. "
                "   Instead set needs_clarification=true and provide 2-3 helpful follow_up_questions. "
                "2. When generating a plan, all budget values MUST be in Indian Rupees (INR). "
                "3. core_category MUST be strictly one of: "
                "['AI Video', 'AI Images', '3D & CGI', 'Product Advertising', 'Fashion', 'Social Media', 'Animation & Motion', 'Branding & Design', 'Audio & Voice']. "
                "4. When refining an existing plan, update the modified parameters while preserving existing relevant fields. "
                "5. Never output raw Markdown formatting inside JSON strings."
            )

            # Build conversational context
            history_summary = []
            for m in conversation_history:
                history_summary.append(f"{m.role.upper()}: {m.content}")
            
            prompt_payload = {
                "user_message": user_message,
                "conversation_history": history_summary,
                "existing_plan": existing_plan.model_dump() if existing_plan else None,
            }

            prompt_text = (
                f"Context and Current User Request:\n{json.dumps(prompt_payload, indent=2)}\n\n"
                f"Respond with JSON adhering to the copilot schema."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )

            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)

            # Check if Gemini flagged clarification
            if parsed.get("needs_clarification"):
                reply = parsed.get("reply", "Could you provide a few more details so I can build your project plan?")
                follow_ups = parsed.get("follow_up_questions", [
                    "What format are you envisioning? (e.g. Cinematic Video, 3D CGI, or Still Campaign)",
                    "What is your target budget and delivery timeline?",
                ])
                return None, reply, follow_ups, None

            # Validate and clamp structured plan
            plan_data = parsed.get("plan", parsed)
            plan_data["core_category"] = sanitize_category(plan_data.get("core_category", "AI Video"))
            
            # Ensure numbers are clamped safely
            raw_b = float(plan_data.get("budget", 60000.0))
            plan_data["budget"] = max(5000.0, min(100_000_000.0, raw_b))
            raw_t = int(plan_data.get("timeline_days", 7))
            plan_data["timeline_days"] = max(1, min(365, raw_t))

            # Guarantee budget breakdown and milestones exist
            if not plan_data.get("budget_breakdown"):
                plan_data["budget_breakdown"] = [
                    b.model_dump() for b in generate_budget_breakdown(plan_data["budget"])
                ]
            if not plan_data.get("milestones"):
                plan_data["milestones"] = [
                    m.model_dump() for m in generate_milestones(plan_data["core_category"], plan_data["timeline_days"])
                ]

            validated_plan = ProjectPlan(**plan_data)

            # Check scope warning
            scope_warning = check_scope_and_budget(
                validated_plan.core_category,
                validated_plan.budget,
                validated_plan.deliverables,
                user_message
            )
            validated_plan.scope_warning = scope_warning

            reply = parsed.get("reply") or f"I've tailored the project plan for **{validated_plan.project_title}**."
            return validated_plan, reply, [], scope_warning

        except Exception as e:
            logger.warning(f"Gemini copilot generation failed: {e}. Gracefully activating fallback NLP engine.")
            return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)
