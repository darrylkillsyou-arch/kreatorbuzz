import re
import copy
from typing import List, Optional, Tuple, Dict, Any
from app.schemas.xero import (
    ProjectPlan,
    ChatMessage,
    DeliverableItem,
    BudgetBreakdownItem,
    MilestoneItem,
)
from app.services.ai.provider import AIProvider

# Valid core categories in CODE XERO
VALID_CATEGORIES = [
    "AI Video",
    "AI Images",
    "3D & CGI",
    "Product Advertising",
    "Fashion",
    "Social Media",
    "Animation & Motion",
    "Branding & Design",
    "Audio & Voice",
]

CATEGORY_RATES = {
    "3D & CGI": 35000.0,
    "AI Images": 12000.0,
    "AI Video": 18000.0,
    "Animation & Motion": 22000.0,
    "Audio & Voice": 18000.0,
    "Branding & Design": 14000.0,
    "Fashion": 22000.0,
    "Product Advertising": 20000.0,
    "Social Media": 10000.0,
}


def sanitize_category(cat: str) -> str:
    c_lower = cat.lower().strip()
    if "3d" in c_lower or "cgi" in c_lower:
        return "3D & CGI"
    if "fashion" in c_lower:
        return "Fashion"
    if "social" in c_lower:
        return "Social Media"
    if "animation" in c_lower or "motion" in c_lower:
        return "Animation & Motion"
    if "audio" in c_lower or "voice" in c_lower:
        return "Audio & Voice"
    if "branding" in c_lower or "graphic" in c_lower:
        return "Branding & Design"
    if "product" in c_lower:
        return "Product Advertising"
    if "image" in c_lower or "photo" in c_lower:
        return "AI Images"
    return "AI Video"


def extract_budget(text: str) -> Optional[float]:
    t = text.lower()
    inr_patterns = [
        r'(?:₹|rs\.?|rupees?|inr)\s*([\d,]+(?:\.\d+)?)\s*(k)?',
        r'([\d,]+(?:\.\d+)?)\s*(k)?\s*(?:₹|rupees?|rs\.?|inr)',
        r'budget\s*(?:is|of|around|:)?\s*(?:₹|rs\.?)?\s*([\d,]+(?:\.\d+)?)\s*(k)?',
        r'(?:around|under|about|for|to|at)\s*([\d,]+(?:\.\d+)?)\s*(k)\b',
        r'\b([\d,]+(?:\.\d+)?)\s*k\b',
    ]
    for pat in inr_patterns:
        match = re.search(pat, t)
        if match:
            groups = [g for g in match.groups() if g is not None]
            val_str = groups[0].replace(",", "")
            val = float(val_str)
            if "k" in groups or val < 1000:
                val *= 1000
            return max(5000.0, val)
    return None


def extract_timeline(text: str) -> Optional[int]:
    t = text.lower()
    match = re.search(r'(\d+)\s*(?:business\s*)?days?', t)
    if match:
        return max(1, min(180, int(match.group(1))))
    if "week" in t:
        w_match = re.search(r'(\d+)\s*weeks?', t)
        if w_match:
            return int(w_match.group(1)) * 7
        return 7
    return None


def check_scope_and_budget(
    category: str,
    budget: float,
    deliverables: List[DeliverableItem],
    text: str = ""
) -> Optional[str]:
    """Inspects scope vs marketplace creator base rates to warn about unrealistic demands."""
    min_base_rate = CATEGORY_RATES.get(category, 18000.0)
    total_qty = sum(d.quantity for d in deliverables) if deliverables else 1
    
    # Check for multi-format excessive scope on low budget
    t = text.lower()
    many_reels = "5 reels" in t or "10 reels" in t or (total_qty > 5)
    many_images = "30 product" in t or "30 image" in t or "50 photo" in t or "images" in t and "30" in t
    has_3d = "3d" in t or "cgi" in t or "animation" in t
    has_music = "music video" in t or "sound design" in t
    
    scope_indicators = sum([many_reels, many_images, has_3d, has_music])

    if (budget < 25000 and scope_indicators >= 2) or (budget < 15000 and total_qty > 3):
        return (
            f"Scope Warning: Requested multi-format deliverables (including 3D/animation and multiple reels) "
            f"exceed verified CODE XERO creator rate baselines for ₹{budget:,.0f}. "
            f"Marketplace base rate for top creators in {category} starts at ₹{min_base_rate:,.0f}/day. "
            f"Recommended: Consider prioritizing core deliverables or allocating ₹{max(budget * 2.5, 45000):,.0f}."
        )
    return None


def generate_budget_breakdown(budget: float) -> List[BudgetBreakdownItem]:
    return [
        BudgetBreakdownItem(item="Creator Production & Directing", amount=round(budget * 0.65, 0), percentage=65.0),
        BudgetBreakdownItem(item="Visual Effects & Generative AI Compute", amount=round(budget * 0.15, 0), percentage=15.0),
        BudgetBreakdownItem(item="Post-Processing & Audio Engineering", amount=round(budget * 0.12, 0), percentage=12.0),
        BudgetBreakdownItem(item="Contingency & Revision Reserve", amount=round(budget * 0.08, 0), percentage=8.0),
    ]


def generate_milestones(category: str, timeline_days: int) -> List[MilestoneItem]:
    d1 = max(1, round(timeline_days * 0.25))
    d2 = max(1, round(timeline_days * 0.40))
    d3 = max(1, round(timeline_days * 0.20))
    d4 = max(1, timeline_days - (d1 + d2 + d3))

    if category in ["3D & CGI"]:
        return [
            MilestoneItem(step=1, title="Concept & Spatial Scene Framing", description="3D viewport layout, moodboard & shader lookdev", duration_days=d1),
            MilestoneItem(step=2, title="Base Geometry & High-Res Texturing", description="Core mesh modeling, lighting setups & materials", duration_days=d2),
            MilestoneItem(step=3, title="First Motion & Lighting Render Pass", description="Animation pass & test camera cuts for review", duration_days=d3),
            MilestoneItem(step=4, title="Master 4K Upscale & Asset Packaging", description="Final denoise, color grade & master deliverables release", duration_days=d4),
        ]
    elif category in ["AI Video", "Product Advertising", "Fashion"]:
        return [
            MilestoneItem(step=1, title="Creative Direction & Prompt Styleframes", description="Style frames, character/product consistency prompts & narrative arc", duration_days=d1),
            MilestoneItem(step=2, title="Rough Cut & Kinetic Motion Pass", description="Latent diffusion generation, camera motion passes & initial pacing", duration_days=d2),
            MilestoneItem(step=3, title="Color Grading, Sound Design & Audio Stems", description="Fine audio sync, Foley soundscapes, anamorphic optical grade", duration_days=d3),
            MilestoneItem(step=4, title="Final 4K Master & Platform Cuts", description="Multi-aspect exports (9:16, 16:9) and prompt provenance logs", duration_days=d4),
        ]
    elif category in ["Social Media"]:
        return [
            MilestoneItem(step=1, title="Hook Concepts & Audio Moodboard", description="Scripting, viral hook formulations & visual references", duration_days=d1),
            MilestoneItem(step=2, title="Draft Reel Sequences", description="AI generated cuts with kinetic pacing and on-screen typography", duration_days=d2),
            MilestoneItem(step=3, title="Sound Effects & Revision Polish", description="Sound enhancement, caption syncing & pacing adjustments", duration_days=d3),
            MilestoneItem(step=4, title="High-Res 9:16 Social Exports", description="Optimized mobile bitrate exports & launch-ready stems", duration_days=d4),
        ]
    elif category in ["Audio & Voice"]:
        return [
            MilestoneItem(step=1, title="Sonic Architecture & Voice Prompting", description="Voice profile calibration, timbre selection & script pacing", duration_days=d1),
            MilestoneItem(step=2, title="Full Vocal Render & Synthesized Pass", description="Multi-take voice synthesis and initial arrangement", duration_days=d2),
            MilestoneItem(step=3, title="Mixing, Mastering & EQ Balancing", description="Dynamic range compression, spatial stereo enhancement & de-essing", duration_days=d3),
            MilestoneItem(step=4, title="Master Audio Stems & FLAC Delivery", description="Uncompressed 24-bit/48kHz WAV master and isolated stems", duration_days=d4),
        ]
    else:
        return [
            MilestoneItem(step=1, title="Creative Direction & Prompt Exploration", description="Seed discovery, style benchmarks & visual identity alignment", duration_days=d1),
            MilestoneItem(step=2, title="Primary Asset Synthesis", description="High-resolution generation pass across hero angles", duration_days=d2),
            MilestoneItem(step=3, title="Retouching & Inpainting Refinement", description="Artifact removal, precision mask inpainting & color balance", duration_days=d3),
            MilestoneItem(step=4, title="Production Delivery Package", description="Full-resolution lossless assets with layer masks & workflow docs", duration_days=d4),
        ]


class FallbackAIProvider(AIProvider):
    """Deterministic, robust NLP creative project plan engine."""

    def generate_project_plan(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        existing_plan: Optional[ProjectPlan] = None,
    ) -> Tuple[Optional[ProjectPlan], str, List[str], Optional[str]]:
        msg = user_message.strip()
        msg_lower = msg.lower()

        # Combine all user history for holistic context
        all_user_text = " ".join(
            [m.content for m in conversation_history if m.role == "user"] + [msg]
        )
        combined_lower = all_user_text.lower()

        # Check for underspecified prompt (PART 6 requirement)
        underspecified_triggers = [
            "something cool",
            "make something cool",
            "something nice",
            "need something cool for my brand",
            "help me with my brand",
            "cool project",
        ]
        is_bare_or_vague = (
            any(t in msg_lower for t in underspecified_triggers) or
            (len(msg.split()) <= 4 and not any(k in msg_lower for k in ["video", "ad", "image", "3d", "reels", "voice", "perfume", "sneaker", "fashion"]))
        )

        if not existing_plan and is_bare_or_vague:
            follow_ups = [
                "What format are you envisioning? (e.g. 4K Cinematic Video, 3D CGI, or Social Reels)",
                "Which platforms will this launch on? (Instagram, YouTube, Web)",
                "What is your target budget and delivery timeline?",
            ]
            reply = (
                "I'd love to help craft an exceptional campaign! To tailor the creative specifications, "
                "could you share a bit more about what you're creating?"
            )
            return None, reply, follow_ups, None

        # If we have an existing plan, this is a conversational refinement (PART 7)
        if existing_plan:
            plan = copy.deepcopy(existing_plan)
            reply, scope_warning = self._refine_existing_plan(plan, msg, msg_lower)
            return plan, reply, [], scope_warning

        # Otherwise, build a fresh project plan
        plan, scope_warning = self._build_fresh_plan(msg, combined_lower, all_user_text)
        reply = (
            f"I have crafted a complete creative project blueprint for **{plan.project_title}**! "
            f"Review the specifications, budget allocation, and milestones below. "
            f"You can refine any parameter conversationally (e.g., 'Make it cheaper', 'Reduce timeline to 5 days')."
        )
        return plan, reply, [], scope_warning

    def _build_fresh_plan(self, msg: str, combined_lower: str, all_user_text: str) -> Tuple[ProjectPlan, Optional[str]]:
        # 1. Determine Core Category & Format
        core_category = "AI Video"
        content_format = "video"
        specializations = ["Cinematic Commercial Video & Brand Films"]

        if any(k in combined_lower for k in ["3d", "cgi", "sneaker cgi", "sneaker render", "blender", "unreal", "spatial"]):
            core_category = "3D & CGI"
            content_format = "3d"
            specializations = ["3D Product Rendering & CGI", "Futuristic Product Animation"]
        elif any(k in combined_lower for k in ["fashion", "couture", "indian couture", "editorial", "runway", "lookbook", "apparel"]):
            core_category = "Fashion"
            content_format = "video" if "video" in combined_lower or "film" in combined_lower else "image"
            specializations = ["Haute Couture Runway & Editorial", "AI Fashion Campaigns"]
        elif any(k in combined_lower for k in ["reels", "reel", "tiktok", "instagram reel", "social media", "shorts", "viral"]):
            core_category = "Social Media"
            content_format = "video"
            specializations = ["Short-form Video & Reels Creation", "Viral Social Content Production"]
        elif any(k in combined_lower for k in ["voice", "voiceover", "sound design", "audio", "podcast", "sfx", "music"]):
            core_category = "Audio & Voice"
            content_format = "audio"
            specializations = ["AI Voice & Voice-over", "Sonic Branding & Sound Design"]
        elif any(k in combined_lower for k in ["perfume", "product ad", "commercial", "skincare", "beauty ad", "beverage"]):
            core_category = "Product Advertising"
            content_format = "video"
            specializations = ["Product Video & Commercial Ads", "Luxury Commercial Direction"]
        elif any(k in combined_lower for k in ["image", "photo", "stills", "concept art", "photography"]):
            core_category = "AI Images"
            content_format = "image"
            specializations = ["Generative Concept Art", "High-Fashion Editorial Stills"]

        # 2. Extract Budget & Timeline
        budget = extract_budget(all_user_text) or 60000.0
        timeline_days = extract_timeline(all_user_text) or 7

        # 3. Platforms
        platforms = ["Instagram"]
        if "instagram" in combined_lower or "reels" in combined_lower or "reel" in combined_lower:
            platforms = ["Instagram Reels", "Instagram Feed"]
        if "tiktok" in combined_lower:
            platforms.append("TikTok")
        if "youtube" in combined_lower:
            platforms.append("YouTube (16:9)")
        if len(platforms) == 1 and "Instagram" in platforms:
            platforms = ["Instagram Reels", "Instagram Feed", "Digital Out-of-Home"]

        # 4. Deliverables
        aspect_ratio = "9:16" if "reels" in combined_lower or "tiktok" in combined_lower else ("16:9" if "youtube" in combined_lower else "9:16")
        
        # Check quantity of reels / images requested
        reel_match = re.search(r'(\d+)\s*(?:instagram\s*)?reels?', combined_lower)
        num_reels = int(reel_match.group(1)) if reel_match else (3 if "reels" in combined_lower else 1)

        deliverables = []
        if core_category == "Social Media" or "reel" in combined_lower:
            deliverables.append(DeliverableItem(name=f"{num_reels}x High-Impact Instagram Reels ({aspect_ratio})", type="video", quantity=num_reels, duration_seconds=20, aspect_ratio=aspect_ratio))
            deliverables.append(DeliverableItem(name="Raw Audio Stems & Sound Design Mix", type="audio", quantity=1))
            deliverables.append(DeliverableItem(name="Thumbnail & Cover Stills", type="image", quantity=num_reels, aspect_ratio="9:16"))
        elif core_category == "3D & CGI":
            deliverables.append(DeliverableItem(name="4K Master 3D CGI Commercial Film (20s)", type="video", quantity=1, duration_seconds=20, aspect_ratio="9:16"))
            deliverables.append(DeliverableItem(name="3x High-Res Still Keyframe Renders", type="image", quantity=3, aspect_ratio="1:1"))
            deliverables.append(DeliverableItem(name="3D Project Stems & Clean Passes", type="document", quantity=1))
        elif core_category == "Audio & Voice":
            deliverables.append(DeliverableItem(name="30-Second Commercial AI Voiceover Master", type="audio", quantity=1, duration_seconds=30))
            deliverables.append(DeliverableItem(name="Custom Foley & Ambient Sound Design Stems", type="audio", quantity=1))
            deliverables.append(DeliverableItem(name="Mixed & Mastered WAV (24-bit/48kHz)", type="audio", quantity=1))
        elif core_category == "Fashion":
            deliverables.append(DeliverableItem(name="Cinematic Runway / Editorial Master Film (30s)", type="video", quantity=1, duration_seconds=30, aspect_ratio=aspect_ratio))
            deliverables.append(DeliverableItem(name="5x Haute Couture Campaign Keyframe Stills", type="image", quantity=5, aspect_ratio="4:5"))
            deliverables.append(DeliverableItem(name="Color-Graded ProRes Archive", type="video", quantity=1))
        else:
            deliverables.append(DeliverableItem(name="Master 4K Cinematic Product Ad (20s)", type="video", quantity=1, duration_seconds=20, aspect_ratio=aspect_ratio))
            deliverables.append(DeliverableItem(name="3x Social Cutdowns (10s Hooks)", type="video", quantity=3, duration_seconds=10, aspect_ratio="9:16"))
            deliverables.append(DeliverableItem(name="Sound Design & Motion Graphics Stems", type="audio", quantity=1))

        # 5. Tools & Styles
        tools = ["Midjourney v6", "Runway Gen-3", "ComfyUI Flux"]
        if core_category == "3D & CGI":
            tools = ["Blender", "Unreal Engine 5", "Cinema 4D", "Runway Gen-3"]
        elif core_category == "Audio & Voice":
            tools = ["ElevenLabs", "Suno v3", "Logic Pro X", "iZotope RX"]
        elif core_category == "Fashion":
            tools = ["Midjourney v6", "Kling AI", "Magnific AI", "ComfyUI"]

        styles = ["Warm Editorial Luxury", "Cinematic 35mm"]
        if "futuristic" in combined_lower or "sneaker" in combined_lower:
            styles = ["Futuristic Cyberpunk", "Hyperreal Photorealism"]
        if "couture" in combined_lower or "indian" in combined_lower:
            styles = ["Regal Indian Couture", "High-Fashion Editorial"]

        # Scope warning check
        scope_warning = check_scope_and_budget(core_category, budget, deliverables, all_user_text)

        # Title
        first_clean = re.sub(r'[^a-zA-Z0-9\s]', '', msg).strip().title()
        words = first_clean.split()[:5]
        title = " ".join(words) if words else "Luxury AI Visual Campaign"
        if len(title) < 12:
            title = f"{title} — Creative Project Plan"

        plan = ProjectPlan(
            project_title=title,
            summary=f"Commercial {core_category.lower()} project focused on delivering high-production-value visual assets for {', '.join(platforms)}.",
            objective="Drive brand prestige, customer acquisition, and high-engagement social impact.",
            target_audience="Discerning luxury consumers, trendsetters, and high-value target demographics.",
            creative_direction=f"Elevated visual storytelling pairing {styles[0]} aesthetics with cutting-edge generative tools.",
            core_category=core_category,
            specializations=specializations,
            content_format=content_format,
            deliverables=deliverables,
            duration="20-30 seconds" if content_format == "video" else None,
            platforms=platforms,
            timeline_days=timeline_days,
            budget=budget,
            budget_breakdown=generate_budget_breakdown(budget),
            milestones=generate_milestones(core_category, timeline_days),
            preferred_tools=tools,
            style_direction=styles,
            risks_and_production_notes=[
                "Prompt drift risk mitigated by locking character/product LoRA weights early in Milestone 1.",
                "Ensure client brand guidelines and packaging vector assets are submitted before Milestone 2.",
                "Render quality passes verified at 4K resolution before milestone release."
            ],
            creator_requirements=[
                f"Demonstrated portfolio in {core_category} with high fidelity lighting.",
                f"Proficiency in {tools[0]} and {tools[1]}.",
                f"SLA on-time delivery rate > 95%."
            ],
            scope_warning=scope_warning,
        )
        return plan, scope_warning

    def _refine_existing_plan(self, plan: ProjectPlan, msg: str, msg_lower: str) -> Tuple[str, Optional[str]]:
        changes = []

        # 1. Budget changes
        new_b = extract_budget(msg)
        if new_b is not None:
            plan.budget = new_b
            plan.budget_breakdown = generate_budget_breakdown(new_b)
            changes.append(f"updated budget to ₹{new_b:,.0f}")
        elif "make it cheaper" in msg_lower or "cheaper" in msg_lower or "reduce budget" in msg_lower:
            plan.budget = max(10000.0, round(plan.budget * 0.75, 0))
            plan.budget_breakdown = generate_budget_breakdown(plan.budget)
            changes.append(f"reduced budget to ₹{plan.budget:,.0f}")
        elif "more premium" in msg_lower or "increase budget" in msg_lower or "higher budget" in msg_lower:
            plan.budget = round(plan.budget * 1.35, 0)
            plan.budget_breakdown = generate_budget_breakdown(plan.budget)
            if "Ultra-Luxury Master Grade" not in plan.style_direction:
                plan.style_direction.insert(0, "Ultra-Luxury Master Grade")
            changes.append(f"elevated production budget to ₹{plan.budget:,.0f} with premium grade specifications")

        # 2. Timeline changes
        new_t = extract_timeline(msg)
        if new_t is not None:
            plan.timeline_days = new_t
            plan.milestones = generate_milestones(plan.core_category, new_t)
            changes.append(f"adjusted timeline to {new_t} days")
        elif "faster" in msg_lower or "expedite" in msg_lower:
            plan.timeline_days = max(3, plan.timeline_days - 2)
            plan.milestones = generate_milestones(plan.core_category, plan.timeline_days)
            changes.append(f"expedited delivery to {plan.timeline_days} days")

        # 3. Format / Category change
        if "3d" in msg_lower or "cgi" in msg_lower or "render" in msg_lower:
            plan.core_category = "3D & CGI"
            plan.content_format = "3d"
            plan.specializations = ["3D Product Rendering & CGI", "Futuristic Product Animation"]
            plan.preferred_tools = ["Blender", "Unreal Engine 5", "Cinema 4D", "Octane Render"]
            plan.deliverables = [
                DeliverableItem(name="3D CGI Master Hero Render & Animation (15s)", type="3d", quantity=1, aspect_ratio="9:16"),
                DeliverableItem(name="3x High-Poly Close-up Stills", type="image", quantity=3, aspect_ratio="1:1"),
                DeliverableItem(name="Unreal/Blender Source Project Files", type="document", quantity=1),
            ]
            plan.milestones = generate_milestones(plan.core_category, plan.timeline_days)
            changes.append("switched campaign format to 3D & CGI")
        elif "still images" in msg_lower or "stills" in msg_lower or "photos" in msg_lower or "change it to still" in msg_lower:
            plan.core_category = "AI Images"
            plan.content_format = "image"
            plan.duration = None
            plan.specializations = ["Generative Concept Art", "High-Fashion Editorial Stills"]
            plan.deliverables = [
                DeliverableItem(name="5x High-Fashion Editorial Hero Stills", type="image", quantity=5, aspect_ratio="4:5"),
                DeliverableItem(name="Prompt Engineering Archive & Seed Logs", type="document", quantity=1),
            ]
            plan.milestones = generate_milestones(plan.core_category, plan.timeline_days)
            changes.append("switched campaign format to AI Still Images")
        elif "reels" in msg_lower and "add" in msg_lower:
            r_match = re.search(r'add\s*(\d+)\s*reels?', msg_lower)
            add_qty = int(r_match.group(1)) if r_match else 2
            plan.deliverables.append(
                DeliverableItem(name=f"{add_qty}x Additional Viral Social Reels", type="video", quantity=add_qty, duration_seconds=15, aspect_ratio="9:16")
            )
            changes.append(f"added {add_qty} Instagram Reels to deliverables")
        elif "remove voiceover" in msg_lower or "without voiceover" in msg_lower:
            plan.deliverables = [d for d in plan.deliverables if "voiceover" not in d.name.lower()]
            if "Audio & Voice" == plan.core_category:
                plan.core_category = "AI Video"
            changes.append("removed voiceover components from production scope")
        elif "remove one deliverable" in msg_lower or "remove deliverable" in msg_lower:
            if len(plan.deliverables) > 1:
                removed = plan.deliverables.pop()
                changes.append(f"removed deliverable '{removed.name}'")

        # 4. Style adjustments
        if "more cinematic" in msg_lower or "cinematic" in msg_lower:
            if "Cinematic 35mm" not in plan.style_direction:
                plan.style_direction.append("Cinematic 35mm")
            changes.append("deepened cinematic 35mm anamorphic creative direction")
        if "darker" in msg_lower or "make it darker" in msg_lower:
            plan.style_direction.append("Moody Noir High-Contrast")
            changes.append("added moody noir high-contrast lighting palette")
        if "futuristic" in msg_lower or "more futuristic" in msg_lower:
            plan.style_direction.append("Neo-Futuristic Hyperreal")
            changes.append("integrated neo-futuristic hyperreal aesthetics")
        if "editorial fashion" in msg_lower or "switch to editorial fashion" in msg_lower:
            plan.core_category = "Fashion"
            plan.specializations = ["Haute Couture Runway & Editorial", "AI Fashion Campaigns"]
            plan.style_direction = ["Haute Couture Editorial", "Warm Luxury Glow"]
            changes.append("switched creative specialization to Haute Couture Editorial Fashion")

        # Check scope warning on modified state
        scope_warning = check_scope_and_budget(plan.core_category, plan.budget, plan.deliverables, msg)
        plan.scope_warning = scope_warning

        summary_changes = "; ".join(changes) if changes else "updated project specifications"
        reply = f"Understood! I've {summary_changes}. Your project plan and creator matches have evolved accordingly."
        return reply, scope_warning
