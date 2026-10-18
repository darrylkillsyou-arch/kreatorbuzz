"""
Migration script for Community 2.0.
Replaces legacy demo posts with 21 high-quality, realistic community posts
spanning all 7 categories: Showcase, Hiring, Offering Services, Looking For Creator,
Collaboration, Announcement, Urgent Requirement.

Post media URLs are high-resolution creative imagery from Unsplash, completely distinct
from user avatar portraits.
"""

from app.database import SessionLocal
from app.models.community import CommunityPost, PostLike, PostComment, SavedPost
from app.models.users import User
from datetime import datetime, timedelta
import random

def migrate_community_posts():
    db = SessionLocal()
    try:
        # Step 1: Idempotency guard — if the canonical seed posts already exist, skip entirely.
        # This prevents accidental overwrites of real user-generated posts on re-runs.
        SEED_SENTINEL_TITLE = "Luxury Perfume CGI: Full Pipeline Breakdown"
        already_seeded = db.query(CommunityPost).filter(
            CommunityPost.title == SEED_SENTINEL_TITLE
        ).first()
        if already_seeded:
            print("Community 2.0 seed already applied (sentinel post found). Skipping to avoid overwriting real posts.")
            return
        print("No existing seed detected. Proceeding with Community 2.0 seeding...")

        # Step 2: Query creator and brand users
        creators = db.query(User).filter(User.role == "creator").order_by(User.id).all()
        brands = db.query(User).filter(User.role == "brand").order_by(User.id).all()

        if not creators:
            print("Error: No creator users found in DB.")
            return

        # Pick specific recognizable creators
        aarav = creators[0] if len(creators) > 0 else creators[0]
        meera = creators[1] if len(creators) > 1 else creators[0]
        kabir = creators[2] if len(creators) > 2 else creators[0]
        priya = creators[3] if len(creators) > 3 else creators[0]
        arjun = creators[4] if len(creators) > 4 else creators[0]
        rohan = creators[5] if len(creators) > 5 else creators[0]
        nisha = creators[6] if len(creators) > 6 else creators[0]
        dev = creators[7] if len(creators) > 7 else creators[0]
        anika = creators[8] if len(creators) > 8 else creators[0]

        brand_lumina = brands[0] if len(brands) > 0 else aarav
        brand_alexandra = brands[2] if len(brands) > 2 else (brands[0] if brands else aarav)
        brand_recruiter = brands[3] if len(brands) > 3 else (brands[0] if brands else aarav)

        now = datetime.utcnow()

        # Step 3: Define 21 realistic posts across 7 categories
        posts_data = [
            # ── SHOWCASE (6 posts) ──────────────────────────────────────────
            {
                "author": aarav,
                "post_type": "showcase",
                "title": "Luxury Perfume CGI: Full Pipeline Breakdown",
                "content": "Just wrapped a 4K cinematic product render for @LuxureBrand. The full pipeline: Blender 4.2 → Octane Render → Topaz Enhance → DaVinci Resolve Studio.\n\nTotal render time across 3x A100 GPUs: 6 hours. The brief was 'cinematic, warm, amber-lit, ultra-premium feel'. High-resolution lighting maps and shader breakdowns available for fellow creators.",
                "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1000&q=80",
                "tools_tags": ["Blender 4.2", "Octane Render", "Topaz Enhance", "DaVinci Resolve"],
                "base_likes": 38,
                "base_comments": 7,
                "delta_hours": 2,
            },
            {
                "author": meera,
                "post_type": "showcase",
                "title": "Haute Couture Spring 2027: AI Fashion Editorial",
                "content": "Six months of prompt architecture resulting in this 12-look editorial spread. Consistent facial structure and textile draping achieved via custom LoRA weights trained on 840 reference fabric swatches.\n\nEvery frame was directed like an analog Vogue shoot, not merely generated with a random seed.",
                "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1000&q=80",
                "tools_tags": ["Flux 1.1 Pro", "ComfyUI", "Custom LoRA", "Photoshop"],
                "base_likes": 54,
                "base_comments": 12,
                "delta_hours": 5,
            },
            {
                "author": kabir,
                "post_type": "showcase",
                "title": "Neon Cyberpunk Title Sequence in Runway Gen-3",
                "content": "Full 30-second motion title sequence for an indie sci-fi anthology. Combined Runway Gen-3 Alpha for camera camera tracking with ComfyUI AnimateDiff for volumetric light bloom.\n\nPrompt engineering tip: lock camera motion to subtle pan-left at 0.4 speed to prevent artifact warping.",
                "image_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1000&q=80",
                "tools_tags": ["Runway Gen-3", "ComfyUI", "After Effects", "Midjourney v6"],
                "base_likes": 29,
                "base_comments": 4,
                "delta_hours": 9,
            },
            {
                "author": priya,
                "post_type": "showcase",
                "title": "Kinetic Typography & Abstract 3D Spatial Audio",
                "content": "Exploration in generative typography synchronized to ElevenLabs spatial beats. The glyphs deform organically based on frequency spectrograms. Rendered in 60fps ProRes 422.",
                "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=1000&q=80",
                "tools_tags": ["TouchDesigner", "ElevenLabs", "After Effects", "Stable Video"],
                "base_likes": 42,
                "base_comments": 6,
                "delta_hours": 14,
            },
            {
                "author": rohan,
                "post_type": "showcase",
                "title": "Architectural Visualization: Solar Pavilion Concept",
                "content": "Parametric glass pavilion visualization developed for a zero-emission campus competition. Midjourney v6 architectural seeds refined in 3ds Max + V-Ray for accurate solar shadows and caustic reflections.",
                "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1000&q=80",
                "tools_tags": ["Midjourney v6", "V-Ray", "3ds Max", "Photoshop"],
                "base_likes": 31,
                "base_comments": 3,
                "delta_hours": 20,
            },
            {
                "author": dev,
                "post_type": "showcase",
                "title": "Macro Water Droplet Product Simulation",
                "content": "Beverage commercial asset: 4K macro simulation of condensation beads on cold glass. Used Kling AI 1.5 camera moves combined with Blender geometry nodes for fluid dynamics.",
                "image_url": "https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=1000&q=80",
                "tools_tags": ["Kling AI", "Blender", "DaVinci Resolve"],
                "base_likes": 27,
                "base_comments": 5,
                "delta_hours": 26,
            },

            # ── HIRING (3 posts) ────────────────────────────────────────────
            {
                "author": brand_lumina,
                "post_type": "hiring",
                "title": "Hiring: Senior AI Video Director for Luxury EV Campaign",
                "content": "Maison Lumina is commissioning a high-impact cinematic hero spot for an upcoming luxury electric vehicle launch.\n\n• Deliverables: 1x 30s 4K hero video + 3x 15s vertical social cuts\n• Budget: ₹85,000 - ₹1,20,000\n• Turnaround: 10 business days\n• Requirements: Proven experience in photorealistic automotive motion and lighting consistency.\n\nSubmit your portfolio directly or submit a brief proposal through CODE XERO.",
                "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1000&q=80",
                "tools_tags": ["Runway Gen-3", "Sora Enterprise", "DaVinci Resolve"],
                "base_likes": 46,
                "base_comments": 14,
                "delta_hours": 3,
            },
            {
                "author": brand_alexandra,
                "post_type": "hiring",
                "title": "Recruiting 3D Motion Designers for FinTech Product Relaunch",
                "content": "Monolith Studio is expanding our creative roster for a major tier-1 banking app redesign. Looking for 2 motion specialists comfortable with sleek abstract UI physics, 3D card interactions, and kinetic typography.\n\nBudget: ₹60,000 fixed milestone escrow. DM with your 3 strongest motion links.",
                "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1000&q=80",
                "tools_tags": ["After Effects", "Cinema 4D", "Figma"],
                "base_likes": 33,
                "base_comments": 8,
                "delta_hours": 8,
            },
            {
                "author": brand_recruiter,
                "post_type": "hiring",
                "title": "D2C Skincare Brand Seeking AI Visual Creator",
                "content": "We need 8 photorealistic lifestyle stills and 2 micro-animations showcasing botanical ingredients. Aesthetic: minimalist, dewy morning sunlight, Scandinavian interior warmth.\n\nBudget: ₹40,000. Verified escrow payout upon milestone approval.",
                "image_url": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1000&q=80",
                "tools_tags": ["Midjourney v6", "Flux 1.1 Pro"],
                "base_likes": 19,
                "base_comments": 5,
                "delta_hours": 16,
            },

            # ── ANNOUNCEMENT (3 posts) ──────────────────────────────────────
            {
                "author": aarav,
                "post_type": "announcement",
                "title": "CODE XERO Top Creator Q3 2026 — Thank You!",
                "content": "Honoured to be ranked #1 in Cinematic AI Video on CODE XERO this quarter! Over 14 completed projects, 100% on-time milestone delivery, and an average review rating of 4.95.\n\nBig thank you to every brand partner who trusted their creative vision with our studio.",
                "image_url": "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=1000&q=80",
                "tools_tags": ["Milestone Payouts", "Top Rated"],
                "base_likes": 88,
                "base_comments": 19,
                "delta_hours": 6,
            },
            {
                "author": meera,
                "post_type": "announcement",
                "title": "Studio Expansion: Launching Paris Creative Lab",
                "content": "Excited to share that Atelier Meera is officially opening our European AI creative lab in Paris this November. We will be partnering with European luxury maisons on generative print campaigns and virtual fitting rooms.",
                "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000&q=80",
                "tools_tags": ["Studio News", "Fashion AI"],
                "base_likes": 62,
                "base_comments": 11,
                "delta_hours": 18,
            },
            {
                "author": priya,
                "post_type": "announcement",
                "title": "Featured on AI Creators Global Annual Showcase",
                "content": "Our experimental sound-sculpture project was selected among the Top 50 Global AI Artworks of 2026. Gratitude to the CODE XERO community for early feedback on the audio-reactive shaders!",
                "image_url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=1000&q=80",
                "tools_tags": ["Award", "Audio-Reactive"],
                "base_likes": 47,
                "base_comments": 9,
                "delta_hours": 32,
            },

            # ── URGENT REQUIREMENT (3 posts) ────────────────────────────────
            {
                "author": brand_recruiter,
                "post_type": "urgent_requirement",
                "title": "URGENT: 3D Product Render Needed Within 48 Hours",
                "content": "Emergency requirement: We need a high-fidelity 3D product render for a luxury chronograph watch launching this Friday.\n\n• Deliverables: 1x 4K hero transparent PNG + 3x lifestyle angles with subtle lighting\n• Budget: ₹50,000 (rush fee included)\n• Kickoff: Immediate upon agreement\n\nPlease DM with your watch/jewelry render portfolio immediately.",
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1000&q=80",
                "tools_tags": ["Blender", "Octane Render", "Rush Delivery"],
                "base_likes": 24,
                "base_comments": 11,
                "delta_hours": 1,
            },
            {
                "author": brand_lumina,
                "post_type": "urgent_requirement",
                "title": "URGENT: Runway / Kling Specialist for Social Cutdowns (24H)",
                "content": "Need an experienced video AI editor to upscale and interpolate 4 existing 8-second video clips to 60fps 4K before tomorrow evening 6 PM IST. Raw assets ready for download. Budget: ₹25,000 paid immediately upon delivery.",
                "image_url": "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=1000&q=80",
                "tools_tags": ["Runway Gen-3", "Topaz Video AI", "Kling AI"],
                "base_likes": 18,
                "base_comments": 7,
                "delta_hours": 4,
            },
            {
                "author": arjun,
                "post_type": "urgent_requirement",
                "title": "URGENT: Voiceover Artist / ElevenLabs Prompt Engineer",
                "content": "Looking for a specialist to fine-tune an ultra-natural British RP voiceclone for an architectural documentary pitch deck. Needed by tonight 11 PM. Budget: ₹15,000 for 400 words.",
                "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=1000&q=80",
                "tools_tags": ["ElevenLabs", "Audio Engineering"],
                "base_likes": 12,
                "base_comments": 6,
                "delta_hours": 7,
            },

            # ── COLLABORATION (2 posts) ─────────────────────────────────────
            {
                "author": arjun,
                "post_type": "collaboration",
                "title": "Looking for Motion Designer: Hybrid AI + Live Film Collab",
                "content": "I specialize in photorealistic generative backdrops and character consistency. Seeking a talented motion designer / After Effects artist to team up on a 3-minute sci-fi music video for an indie artist.\n\nWe share 50/50 revenue split from the project budget (₹90,000 escrow). Drop your showreel below!",
                "image_url": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1000&q=80",
                "tools_tags": ["ComfyUI", "After Effects", "Revenue Share"],
                "base_likes": 35,
                "base_comments": 10,
                "delta_hours": 11,
            },
            {
                "author": nisha,
                "post_type": "collaboration",
                "title": "Sound Designer Wanted for Generative Nature Series",
                "content": "Working on an 8-part meditative video series featuring bioluminescent deep-sea organisms generated via Flux 1.1 + Kling. Looking for an ambient sound designer to create immersive binaural soundscapes.",
                "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1000&q=80",
                "tools_tags": ["Binaural Audio", "Sound Design", "Kling AI"],
                "base_likes": 28,
                "base_comments": 8,
                "delta_hours": 22,
            },

            # ── OFFERING SERVICES (2 posts) ─────────────────────────────────
            {
                "author": rohan,
                "post_type": "offering_services",
                "title": "Open for Commissions: AI Brand Visual Systems & Identity",
                "content": "Taking 2 new enterprise brand identity projects for next month. What we deliver:\n\n1. Generative visual identity book (200+ pages)\n2. Custom LoRA checkpoint fine-tuned on your exact brand colors and typography\n3. 50+ ready-to-deploy social media assets\n\nPackages start at ₹35,000. View our verified CODE XERO portfolio or send an inquiry.",
                "image_url": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=1000&q=80",
                "tools_tags": ["Brand Identity", "LoRA Fine-tuning", "ComfyUI"],
                "base_likes": 39,
                "base_comments": 5,
                "delta_hours": 13,
            },
            {
                "author": anika,
                "post_type": "offering_services",
                "title": "Cinematic AI Video Directing & Prompt Consulting",
                "content": "Offering direct consultation and creative direction for commercial production houses looking to integrate Gen-3, Kling, and Sora into their existing VFX pipelines. Fixed daily rate or milestone-based engagement.",
                "image_url": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=1000&q=80",
                "tools_tags": ["Consulting", "Runway Gen-3", "Sora Enterprise"],
                "base_likes": 44,
                "base_comments": 7,
                "delta_hours": 24,
            },

            # ── LOOKING FOR CREATOR (2 posts) ───────────────────────────────
            {
                "author": dev,
                "post_type": "looking_for_creator",
                "title": "Seeking 3D Character Rigger with Unreal Engine 5 Skills",
                "content": "Our studio is creating an interactive fashion avatar. We have generated the character faces and high-poly clothing in Marvelous Designer. Need a specialist to rig the skeletal hierarchy in UE5 with live facial capture compatibility.\n\nProject budget: ₹55,000. Timeline: 2 weeks.",
                "image_url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=1000&q=80",
                "tools_tags": ["Unreal Engine 5", "Rigging", "Marvelous Designer"],
                "base_likes": 22,
                "base_comments": 6,
                "delta_hours": 15,
            },
            {
                "author": meera,
                "post_type": "looking_for_creator",
                "title": "Looking for Colorist Specialized in Warm Film Emulation",
                "content": "Looking for a colorist who knows DaVinci Resolve + Dehancer inside out to give 18 AI video clips an authentic 16mm Kodak 500T grain and halation look. Budget: ₹20,000. Quick 3-day turnaround.",
                "image_url": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1000&q=80",
                "tools_tags": ["DaVinci Resolve", "Color Grading", "Film Emulation"],
                "base_likes": 26,
                "base_comments": 4,
                "delta_hours": 28,
            },
        ]

        # Step 4: Insert posts with realistic timestamps
        created_posts = []
        for p in posts_data:
            created_at = now - timedelta(hours=p["delta_hours"])
            post = CommunityPost(
                author_id=p["author"].id,
                post_type=p["post_type"],
                title=p["title"],
                content=p["content"],
                image_url=p["image_url"],
                tools_tags=p["tools_tags"],
                base_likes=p["base_likes"],
                base_comments=p["base_comments"],
                created_at=created_at,
            )
            db.add(post)
            created_posts.append(post)

        db.commit()
        for p in created_posts:
            db.refresh(p)

        print(f"Successfully seeded {len(created_posts)} Community 2.0 posts.")

        # Step 5: Add sample comments
        sample_comments = [
            (created_posts[0], meera, "The lighting falloff in Octane is incredible Aarav. Did you use custom IES profiles?"),
            (created_posts[0], aarav, "Thanks Meera! Yes, custom 32-bit studio softbox IES profiles paired with warm rim lights."),
            (created_posts[1], aarav, "The fabric draping consistency is mindblowing Meera. Great work!"),
            (created_posts[6], kabir, "Just sent our studio portfolio for the luxury EV campaign Elena!"),
            (created_posts[6], priya, "Proposal submitted via CODE XERO. We have automotive commercial experience."),
            (created_posts[12], aarav, "DM sent with our chronograph watch render gallery. Ready to start immediately."),
            (created_posts[15], dev, "Interested in collaborating Arjun. Check my profile for motion reels."),
        ]

        for post, commenter, text in sample_comments:
            comment = PostComment(
                post_id=post.id,
                user_id=commenter.id,
                content=text,
                created_at=post.created_at + timedelta(minutes=random.randint(15, 90)),
            )
            db.add(comment)

        db.commit()
        print(f"Successfully added {len(sample_comments)} realistic comments.")

        # Summary
        types_count = {}
        for p in created_posts:
            types_count[p.post_type] = types_count.get(p.post_type, 0) + 1
        print("Category distribution:", types_count)

    except Exception as e:
        db.rollback()
        print("Migration failed:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_community_posts()
