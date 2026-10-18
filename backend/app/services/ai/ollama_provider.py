import json
import logging
import urllib.request
import urllib.error
from typing import List, Optional, Tuple, Dict, Any
from app.config import settings
from app.schemas.xero import (
    ProjectPlan,
    ChatMessage,
    DeliverableItem,
    BudgetBreakdownItem,
    MilestoneItem,
)
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


class OllamaAIProvider(AIProvider):
    """Ollama Cloud AI integration for Xero AI 2.0 with strict fallback protection."""

    def __init__(self, api_key: str, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key.strip()
        self.model = model or getattr(settings, "OLLAMA_MODEL", "glm-5.3-flash")
        self.base_url = (base_url or getattr(settings, "OLLAMA_BASE_URL", "https://ollama.com")).rstrip("/")
        self.fallback = FallbackAIProvider()
        self.last_used_fallback = False
        self.last_http_status = None
        self.last_error_detail = None

    def generate_project_plan(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        existing_plan: Optional[ProjectPlan] = None,
    ) -> Tuple[Optional[ProjectPlan], str, List[str], Optional[str]]:
        self.last_used_fallback = False
        self.last_http_status = None
        self.last_error_detail = None
        # Fast pre-check: if key is missing or placeholder, directly use deterministic fallback
        if not self.api_key or self.api_key.startswith("PASTE_"):
            logger.info("Ollama API key is unconfigured or placeholder. Using deterministic fallback.")
            self.last_used_fallback = True
            return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)

        try:
            # Build prompt payload with instructions and schema contract
            system_prompt = (
                "You are Xero AI, the Creative Project Copilot for CODE XERO, an elite AI creator marketplace in India.\n"
                "Your role: Analyze natural language briefs and conversational refinement commands to produce a structured project blueprint JSON.\n"
                "CRITICAL REQUIREMENTS:\n"
                "1. ONLY set needs_clarification=true if the user request is completely vague without any project type or domain (e.g. 'I need something cool for my brand'). If the user mentions a specific product, video, deliverable, or budget (e.g. 'perfume Instagram video around Rs 60,000'), you MUST set needs_clarification=false and generate the complete structured project plan blueprint JSON.\n"
                "2. When generating a plan, output JSON with the following structure:\n"
                "   {\n"
                "     \"needs_clarification\": false,\n"
                "     \"reply\": \"Conversational summary of what was generated/refined\",\n"
                "     \"follow_up_questions\": [],\n"
                "     \"plan\": {\n"
                "       \"project_title\": \"Title\",\n"
                "       \"summary\": \"Executive summary\",\n"
                "       \"objective\": \"Goal\",\n"
                "       \"target_audience\": \"Audience description\",\n"
                "       \"creative_direction\": \"Art and style guidance\",\n"
                "       \"core_category\": \"One of ['AI Video', 'AI Images', '3D & CGI', 'Product Advertising', 'Fashion', 'Social Media', 'Animation & Motion', 'Branding & Design', 'Audio & Voice']\",\n"
                "       \"specializations\": [\"Specific specialty 1\", \"Specific specialty 2\"],\n"
                "       \"content_format\": \"video | image | 3d | audio\",\n"
                "       \"deliverables\": [{\"name\": \"Deliverable name\", \"type\": \"video|image|3d|audio\", \"quantity\": 1, \"duration_seconds\": 20, \"aspect_ratio\": \"9:16\"}],\n"
                "       \"duration\": \"20 seconds\",\n"
                "       \"platforms\": [\"Instagram Reels\", \"TikTok\"],\n"
                "       \"timeline_days\": 7,\n"
                "       \"budget\": 60000,\n"
                "       \"preferred_tools\": [\"Midjourney v6\", \"Runway Gen-3\"],\n"
                "       \"style_direction\": [\"Warm Editorial Luxury\", \"Cinematic 35mm\"],\n"
                "       \"risks_and_production_notes\": [\"Note 1\", \"Note 2\"],\n"
                "       \"creator_requirements\": [\"Requirement 1\", \"Requirement 2\"]\n"
                "     }\n"
                "   }\n"
                "3. All budget amounts MUST be in Indian Rupees (INR).\n"
                "4. When modifying an existing plan, update only requested fields and preserve remaining specifications.\n"
                "5. Output valid JSON only, without markdown fences or extraneous text."
            )

            history_messages = [{"role": "system", "content": system_prompt}]
            for msg in conversation_history:
                history_messages.append({"role": msg.role, "content": msg.content})

            user_content = f"User Request: {user_message}"
            if existing_plan:
                user_content += f"\nExisting Active Project Plan:\n{json.dumps(existing_plan.model_dump(), indent=2)}"
            history_messages.append({"role": "user", "content": user_content})

            request_body = {
                "model": self.model,
                "messages": history_messages,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                }
            }

            url = f"{self.base_url}/api/chat"
            req = urllib.request.Request(
                url,
                data=json.dumps(request_body).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                method="POST"
            )

            # Strict 20s timeout to ensure responsiveness
            with urllib.request.urlopen(req, timeout=20) as resp:
                self.last_http_status = resp.status
                resp_data = json.loads(resp.read().decode("utf-8"))

            content = resp_data.get("message", {}).get("content", "").strip()
            if not content:
                logger.warning("Ollama returned empty response content. Triggering fallback.")
                self.last_used_fallback = True
                return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)

            # Strip markdown fences if present
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            parsed = json.loads(content)

            # Clarification branch
            if parsed.get("needs_clarification"):
                reply = parsed.get("reply", "Could you provide a few more details so I can tailor your project blueprint?")
                follow_ups = parsed.get("follow_up_questions") or [
                    "What format are you envisioning? (e.g. 4K Cinematic Video, 3D CGI, or Social Reels)",
                    "What is your target budget and delivery timeline?",
                ]
                return None, reply, follow_ups, None

            plan_dict = parsed.get("plan", parsed)
            if not isinstance(plan_dict, dict) or "core_category" not in plan_dict:
                # Attempt to extract if nested
                if "project_title" not in plan_dict:
                    logger.warning("Ollama response missing core project plan fields. Falling back.")
                    self.last_used_fallback = True
                    return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)

            # Sanitize category and clamp values
            plan_dict["core_category"] = sanitize_category(plan_dict.get("core_category", "AI Video"))
            raw_b = float(plan_dict.get("budget", 60000.0))
            plan_dict["budget"] = max(5000.0, min(100_000_000.0, raw_b))
            raw_t = int(plan_dict.get("timeline_days", 7))
            plan_dict["timeline_days"] = max(1, min(365, raw_t))

            # Guarantee budget breakdown and milestones
            if not plan_dict.get("budget_breakdown"):
                plan_dict["budget_breakdown"] = [
                    b.model_dump() for b in generate_budget_breakdown(plan_dict["budget"])
                ]
            if not plan_dict.get("milestones"):
                plan_dict["milestones"] = [
                    m.model_dump() for m in generate_milestones(plan_dict["core_category"], plan_dict["timeline_days"])
                ]

            validated_plan = ProjectPlan(**plan_dict)
            scope_warning = check_scope_and_budget(
                validated_plan.core_category,
                validated_plan.budget,
                validated_plan.deliverables,
                user_message
            )
            validated_plan.scope_warning = scope_warning

            reply = parsed.get("reply") or f"I've tailored the project blueprint for **{validated_plan.project_title}**."
            return validated_plan, reply, [], scope_warning

        except urllib.error.HTTPError as e:
            self.last_http_status = e.code
            try:
                err_body = e.read().decode("utf-8", errors="ignore")
                self.last_error_detail = f"HTTP {e.code}: {err_body[:200]}"
            except Exception:
                self.last_error_detail = f"HTTP {e.code}: {e.reason}"
            logger.warning(f"Ollama API HTTP error: {self.last_error_detail}. Triggering fallback.")
            self.last_used_fallback = True
            return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)
        except Exception as e:
            self.last_error_detail = str(e)
            logger.warning(f"Ollama AI generation failed: {e}. Gracefully falling back to deterministic engine.")
            self.last_used_fallback = True
            return self.fallback.generate_project_plan(user_message, conversation_history, existing_plan)
