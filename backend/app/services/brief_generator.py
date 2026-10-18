"""AI Brief Builder service using Gemini API with intelligent local NLP fallback."""

import json
import logging
import re
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)


def generate_structured_brief(prompt: str, additional_notes: str = "") -> Dict[str, Any]:
    """Generates structured brief from natural language prompt.
    
    Tries Google Gemini first if API key is present; otherwise falls back to
    the intelligent keyword extraction engine.
    """
    if settings.GEMINI_API_KEY:
        try:
            return _generate_with_gemini(prompt, additional_notes)
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}. Falling back to local NLP engine.")
            
    return _generate_with_fallback(prompt, additional_notes)


def _generate_with_gemini(prompt: str, additional_notes: str = "") -> Dict[str, Any]:
    """Uses google-genai client to extract structured brief JSON."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    system_instruction = (
        "You are an expert AI Creative Director for Maccall, a premier luxury AI creator marketplace in India. "
        "Your role is to analyze a natural language prompt from a brand and convert it into a crisp, "
        "hyper-detailed creative brief JSON specification. "
        "IMPORTANT: All budget values (budget_min, budget_max) must be in Indian Rupees (INR). "
        "recommended_creator_category must be exactly one of: "
        "'AI Images', 'AI Videos', '3D & CGI', 'Product Ads', 'Fashion', 'Social Media', 'Animation', 'Graphic Design', 'Audio & Voice'."
    )

    full_user_content = f"Brand Prompt:\n{prompt}\n\nAdditional Notes:\n{additional_notes or 'None'}"

    schema = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "description": {"type": "STRING"},
            "content_type": {"type": "STRING"},
            "style": {"type": "STRING"},
            "target_audience": {"type": "STRING"},
            "platform": {"type": "ARRAY", "items": {"type": "STRING"}},
            "duration": {"type": "STRING"},
            "aspect_ratio": {"type": "STRING"},
            "deliverables": {"type": "ARRAY", "items": {"type": "STRING"}},
            "tools_suggested": {"type": "ARRAY", "items": {"type": "STRING"}},
            "budget_min": {"type": "NUMBER"},
            "budget_max": {"type": "NUMBER"},
            "suggested_timeline_days": {"type": "INTEGER"},
            "recommended_creator_category": {"type": "STRING"},
        },
        "required": [
            "title", "description", "content_type", "style", "target_audience",
            "platform", "duration", "aspect_ratio", "deliverables", "tools_suggested",
            "budget_min", "budget_max", "suggested_timeline_days", "recommended_creator_category"
        ],
    }

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.3,
        ),
    )

    parsed = json.loads(response.text)
    parsed["raw_prompt"] = prompt
    return parsed


def _generate_with_fallback(prompt: str, additional_notes: str = "") -> Dict[str, Any]:
    """Intelligent rule-based and keyword extraction engine."""
    p_lower = (prompt + " " + (additional_notes or "")).lower()

    # Determine Content Type
    content_type = "video"
    if any(k in p_lower for k in ["3d", "render", "cgi", "unreal", "blender", "spatial", "sneaker render"]):
        content_type = "3d"
    elif any(k in p_lower for k in ["fashion", "couture", "editorial fashion", "runway", "lookbook", "apparel", "textile"]):
        content_type = "fashion"
    elif any(k in p_lower for k in ["social", "reels", "tiktok", "instagram", "youtube", "thumbnail", "meme", "viral"]):
        content_type = "social_media"
    elif any(k in p_lower for k in ["animation", "animated", "motion graphics", "explainer", "anime"]):
        content_type = "animation"
    elif any(k in p_lower for k in ["audio", "soundtrack", "sfx", "voice", "voiceover", "music", "sonic", "podcast"]):
        content_type = "audio"
    elif any(k in p_lower for k in ["brand identity", "logo", "packaging", "typography", "branding", "graphic", "poster"]):
        content_type = "branding"
    elif any(k in p_lower for k in ["product", "ad", "advertisement", "commercial", "showcase", "campaign", "ecommerce"]):
        content_type = "product_ads"
    elif any(k in p_lower for k in ["image", "photo", "photography", "still", "portrait", "concept art"]):
        content_type = "image"

    # Map content_type to Discover core category
    CATEGORY_MAP = {
        "3d": "3D & CGI",
        "fashion": "Fashion",
        "social_media": "Social Media",
        "animation": "Animation & Motion",
        "audio": "Audio & Voice",
        "branding": "Branding & Design",
        "image": "AI Images",
        "product_ads": "Product Advertising",
        "video": "AI Video",
    }
    recommended_creator_category = CATEGORY_MAP.get(content_type, "AI Video")

    # Determine Style
    styles = []
    if any(k in p_lower for k in ["luxury", "haute", "editorial", "warm", "sophisticated", "vogue"]):
        styles.append("Warm Editorial Luxury")
    if any(k in p_lower for k in ["cyberpunk", "sci-fi", "futuristic", "neon", "tech", "hologram"]):
        styles.append("Sci-Fi Cyberpunk")
    if any(k in p_lower for k in ["cinematic", "film", "anamorphic", "35mm", "movie", "dramatic"]):
        styles.append("Cinematic 35mm")
    if any(k in p_lower for k in ["hyper-real", "photoreal", "ultra realistic", "8k", "dslr"]):
        styles.append("Hyper-real Photorealism")
    if any(k in p_lower for k in ["surreal", "dream", "ethereal", "abstract", "cosmic"]):
        styles.append("Ethereal Surrealism")
    if any(k in p_lower for k in ["minimal", "clean", "nordic", "organic", "raw"]):
        styles.append("Minimal Organic")

    style = ", ".join(styles) if styles else "Warm Editorial Luxury"

    # Determine Suggested Tools
    tools = []
    if any(k in p_lower for k in ["midjourney", "mj", "photo", "image", "concept"]):
        tools.append("Midjourney v6")
    if any(k in p_lower for k in ["runway", "gen-3", "gen3", "video", "motion"]):
        tools.append("Runway Gen-3")
    if any(k in p_lower for k in ["comfy", "comfyui", "flux", "controlnet", "lora"]):
        tools.append("ComfyUI Flux")
    if any(k in p_lower for k in ["kling", "kling ai"]):
        tools.append("Kling AI")
    if any(k in p_lower for k in ["luma", "dream machine"]):
        tools.append("Luma Dream Machine")
    if any(k in p_lower for k in ["sora", "openai"]):
        tools.append("Sora")
    if any(k in p_lower for k in ["suno", "udio", "sound", "audio", "elevenlabs"]):
        tools.append("ElevenLabs / Suno")
    if not tools:
        tools = ["Midjourney v6", "Runway Gen-3", "ComfyUI Flux"]

    # Determine Platforms & Aspect Ratio
    platforms = []
    aspect_ratio = "9:16"
    if any(k in p_lower for k in ["reels", "instagram", "ig", "stories", "tiktok", "vertical", "9:16"]):
        platforms.extend(["Instagram Reels", "TikTok"])
        aspect_ratio = "9:16"
    if any(k in p_lower for k in ["youtube", "horizontal", "landscape", "tv", "commercial", "16:9"]):
        platforms.append("YouTube")
        aspect_ratio = "16:9"
    if any(k in p_lower for k in ["feed", "square", "1:1"]):
        platforms.append("Social Feed")
        aspect_ratio = "1:1"
    if not platforms:
        platforms = ["Instagram Reels", "TikTok", "YouTube Shorts"]

    # Determine Duration
    duration_match = re.search(r'(\d+)\s*(?:sec|second|s\b|min|minute)', p_lower)
    if duration_match:
        val = duration_match.group(1)
        duration = f"{val} seconds"
    elif "reel" in p_lower or "short" in p_lower:
        duration = "15-30 seconds"
    elif "commercial" in p_lower:
        duration = "60 seconds"
    else:
        duration = "30 seconds"

    # Budget Extraction — handles both ₹/rupees (INR) and $ (convert to INR ~83x)
    # INR patterns: ₹60000, 60000 rupees, 60k rupees, Rs 60000
    budget_min = 25000.0
    budget_max = 75000.0

    inr_match = re.findall(r'(?:₹|rs\.?|rupees?)\s*([\d,]+(?:\.\d+)?)\s*(?:k)?|'
                           r'([\d,]+(?:\.\d+)?)\s*(?:k)?\s*(?:₹|rupees?|rs\.?|inr)',
                           p_lower)
    usd_match = re.findall(r'\$\s*([\d,]+(?:\.\d+)?)\s*(?:k)?|([\d,]+(?:\.\d+)?)\s*(?:k)?\s*(?:usd|dollars?)',
                           p_lower)

    # Generic number match as fallback
    generic_nums = re.findall(r'\b(\d[\d,]*(?:\.\d+)?)\s*(k)?\b', p_lower)

    inr_values = []
    for g1, g2 in inr_match:
        raw = (g1 or g2).replace(",", "")
        if raw:
            val = float(raw)
            if val < 1000:
                val *= 1000  # treat "60k" or "60" as 60000
            inr_values.append(val)

    usd_values = []
    for g1, g2 in usd_match:
        raw = (g1 or g2).replace(",", "")
        if raw:
            val = float(raw) * 83  # approx INR conversion
            if val < 1000:
                val *= 1000
            usd_values.append(val)

    all_budget_nums = inr_values or usd_values
    if not all_budget_nums:
        # try generic numbers that look like budgets (>= 1000)
        for raw, suffix in generic_nums:
            clean = raw.replace(",", "")
            if clean:
                num = float(clean)
                if suffix == "k":
                    num *= 1000
                if 1000 <= num <= 10_000_000:
                    all_budget_nums.append(num)

    if len(all_budget_nums) == 1:
        budget_min = all_budget_nums[0] * 0.8
        budget_max = all_budget_nums[0] * 1.2
    elif len(all_budget_nums) >= 2:
        budget_min = min(all_budget_nums)
        budget_max = max(all_budget_nums)

    # Timeline extraction (days)
    timeline_days = 7
    timeline_match = re.search(r'(\d+)\s*(?:business\s*)?days?', p_lower)
    if timeline_match:
        timeline_days = int(timeline_match.group(1))
    elif "week" in p_lower:
        timeline_days = 7
    elif "fortnight" in p_lower or "two week" in p_lower:
        timeline_days = 14

    # Deliverables
    deliverables = [
        f"Master 4K Render ({aspect_ratio})",
        "Clean Plate & Motion Graphics Stems",
        "Color Graded ProRes Master",
        "AI Generation Prompt & Workflow Log"
    ]

    # Target Audience
    target_audience = "High-end luxury consumers and digital fashion enthusiasts aged 22-40"
    if any(k in p_lower for k in ["gen z", "youth", "streetwear"]):
        target_audience = "Gen-Z aesthetic tastemakers and streetwear culture enthusiasts"
    elif any(k in p_lower for k in ["tech", "b2b", "founder", "saas"]):
        target_audience = "Forward-thinking tech founders, investors, and early adopters"

    # Title generation
    first_sentence = prompt.strip().split(".")[0][:60].strip()
    title = f"{first_sentence.title()}" if first_sentence else "Luxury AI Visual Campaign"
    if len(title) < 15:
        title = f"{title} - AI Creative Brief"

    return {
        "title": title,
        "description": prompt.strip(),
        "content_type": content_type,
        "style": style,
        "target_audience": target_audience,
        "platform": list(set(platforms)),
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "deliverables": deliverables,
        "tools_suggested": list(set(tools)),
        "budget_min": round(budget_min, 2),
        "budget_max": round(budget_max, 2),
        "suggested_timeline_days": timeline_days,
        "recommended_creator_category": recommended_creator_category,
        "raw_prompt": prompt,
    }

