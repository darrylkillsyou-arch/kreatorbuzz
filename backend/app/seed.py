"""Seed database with realistic demo accounts, creators, portfolio, briefs, community feed, and workspaces."""

import logging
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.users import User
from app.models.creators import CreatorProfile, PortfolioItem, CreatorAchievement, Verification
from app.models.briefs import Brief
from app.models.community import CommunityPost, PostLike, PostComment, Follow, SavedPost
from app.models.workspaces import (
    Workspace,
    WorkspaceMember,
    WorkspaceMessage,
    WorkspaceMilestone,
    SharedFile,
    RevisionRequest,
)
from app.models.shortlist import Shortlist
from app.models.leaderboard import LeaderboardEntry
from app.dependencies import get_password_hash
from app.services.encryption import encrypt_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def seed_database(db=None):
    """Seeds the database with full demo dataset."""
    logger.info("Seeding database baseline records...")
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    try:
        # 1. Create Core Users
        demo_pw = get_password_hash("demo1234")

        brand_user = User(
            email="brand@maccall.demo",
            password_hash=demo_pw,
            full_name="Elena Vance (Maison Lumina)",
            role="brand",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            bio="Creative Director at Maison Lumina. Commissioning next-generation AI cinema and generative runway campaigns.",
            location="Paris / Milan",
            is_active=True,
        )

        creator_user = User(
            email="creator@maccall.demo",
            password_hash=demo_pw,
            full_name="Aarav Studio",
            role="creator",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            bio="Award-winning AI Cinema Director. Specializing in kinetic runway films, photoreal hypercars, and luxury synthetic aesthetics.",
            location="Paris / Milan Sync",
            is_active=True,
        )

        admin_user = User(
            email="admin@maccall.demo",
            password_hash=demo_pw,
            full_name="Maccall Editorial Admin",
            role="admin",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            bio="Head of Curation and Director Verification at Maccall AI Creator Marketplace.",
            location="Zurich / London",
            is_active=True,
        )

        alexandra_user = User(
            email="alexandra@monolith.studio",
            password_hash=demo_pw,
            full_name="Alexandra Vance",
            role="brand",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            bio="Creative Director at Monolith Heritage Studio. Commissioning next-generation AI cinema.",
            location="London / New York",
            is_active=True,
        )

        recruiter_user = User(
            email="recruiter@codexero.com",
            password_hash=demo_pw,
            full_name="Demo Recruiter",
            role="brand",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            bio="Head of Creative Production at Monolith Creative. Commissioning next-generation AI cinema.",
            location="Mumbai / London",
            is_active=True,
        )

        creator_user_codexero = User(
            email="creator@codexero.com",
            password_hash=demo_pw,
            full_name="Demo Content Creator",
            role="creator",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            bio="Award-winning AI Cinema Director. Specializing in kinetic runway films, photoreal hypercars, and luxury synthetic aesthetics.",
            location="Paris / Milan",
            is_active=True,
        )

        clean_recruiter = User(
            email="cleanrecruiter@codexero.com",
            password_hash=demo_pw,
            full_name="Clean Recruiter",
            role="brand",
            avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80",
            bio="Clean brand account for testing fresh onboarding.",
            location="Bangalore",
            is_active=True,
        )

        clean_creator = User(
            email="cleancreator@codexero.com",
            password_hash=demo_pw,
            full_name="Clean Content Creator",
            role="creator",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            bio="Clean creator account for testing fresh workspace collaborations.",
            location="Delhi",
            is_active=True,
        )

        db.add_all([
            brand_user, creator_user, admin_user, alexandra_user,
            recruiter_user, creator_user_codexero, clean_recruiter, clean_creator
        ])
        db.commit()
        db.refresh(brand_user)
        db.refresh(creator_user)
        db.refresh(admin_user)
        db.refresh(alexandra_user)
        db.refresh(recruiter_user)
        db.refresh(creator_user_codexero)
        db.refresh(clean_recruiter)
        db.refresh(clean_creator)

        # 2. Additional Creator Users â€” 87 creators covering all 9 categories with INR pricing
        # Tuple: (name, email, specialization, avatar_url, location, ai_tools, skills, starting_rate_inr, delivery_days, rating, briefs_count, sla_score)
        creators_meta = [
            # AI Videos
            ("Meera Atelier", "meera@atelier.demo", "Cinematic Video & Fashion Film", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Runway Gen-3", "Midjourney v6", "ComfyUI", "DaVinci Resolve"], ["AI Video Production", "Fashion Film Direction", "Color Grading"], 55000.0, 5, 4.95, 42, 99.2),
            ("Kabir Motion", "kabir@motion.demo", "Sci-Fi Cinematic Video & VFX", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80", "Mumbai / Berlin", ["Runway Gen-3", "Luma Dream Machine", "Unreal Engine 5", "Premiere Pro"], ["VFX Supervision", "Cinematic Camera Control", "Color Grading"], 75000.0, 6, 4.92, 38, 98.5),
            ("Priya Cinematic", "priya@cinematic.demo", "Cinematic Video & Brand Films", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=300&q=80", "Delhi / Mumbai", ["Sora", "Runway Gen-3", "ComfyUI", "Premiere Pro"], ["Brand Films", "Corporate Videos", "Cinematic Storytelling"], 45000.0, 4, 4.88, 31, 98.7),
            ("Arjun Reel", "arjun@reel.demo", "Short Video & Social Media Reels", "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Kling AI", "Runway Gen-3", "CapCut AI"], ["Instagram Reels", "TikTok Video", "YouTube Shorts"], 25000.0, 3, 4.79, 58, 97.5),
            ("Rohan VFX", "rohan@vfx.demo", "VFX Video Production & Compositing", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80", "Chennai / Hyderabad", ["After Effects", "Runway Gen-3", "Nuke", "DaVinci Resolve"], ["Visual Effects", "Compositing", "Motion Tracking"], 60000.0, 7, 4.84, 27, 98.0),
            ("Nisha Films", "nisha@films.demo", "Cinematic Video & Documentary Style", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80", "Kolkata", ["Luma Dream Machine", "Runway Gen-3", "Premiere Pro"], ["Documentary Video", "Interview Films", "Brand Stories"], 30000.0, 5, 4.82, 19, 97.9),
            ("Dev Motion", "dev@motion.demo", "Product Video & Commercial Ads", "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80", "Pune", ["Runway Gen-3", "Kling AI", "ComfyUI", "Topaz AI"], ["Product Video Ads", "E-commerce Videos", "Commercial Films"], 40000.0, 4, 4.86, 34, 98.3),
            ("Anika Cinema", "anika@cinema.demo", "Luxury Cinematic Video Production", "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=300&q=80", "Hyderabad / London", ["Sora", "Runway Gen-3", "DaVinci Resolve", "Midjourney v6"], ["Luxury Brand Films", "High-end Cinematography", "Color Science"], 85000.0, 7, 4.96, 23, 99.5),
            ("Vivek Director", "vivek@director.demo", "Cinematic Film & Music Video Production", "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Runway Gen-3", "Midjourney v6", "ComfyUI", "Ableton"], ["Music Videos", "Short Films", "Narrative Cinema"], 50000.0, 6, 4.90, 29, 98.6),
            ("Deepa Shorts", "deepa@shorts.demo", "Short-form Video & Reels Creation", "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Kling AI", "CapCut AI", "Runway Gen-3"], ["Reels Production", "Story Videos", "Viral Short Content"], 20000.0, 2, 4.75, 71, 97.1),
            ("Rahul Cineworks", "rahul@cineworks.demo", "Cinematic Commercial Video & Brand Films", "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=300&q=80", "Ahmedabad / Mumbai", ["Sora", "Runway Gen-3", "Topaz Video AI", "Premiere Pro"], ["TV Commercials", "Brand Films", "Event Videos"], 65000.0, 5, 4.91, 26, 98.8),
            ("Tanya Reel Studio", "tanya@reel.demo", "AI Video & Social Content Production", "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=300&q=80", "Delhi", ["Kling AI", "Runway Gen-3", "ComfyUI"], ["Social Media Video", "Video Scripting", "Reels Direction"], 28000.0, 3, 4.80, 45, 97.6),
            ("Surya Films", "surya@films.demo", "Cinematic Video & Wedding Films", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80", "Coimbatore", ["Runway Gen-3", "DaVinci Resolve", "Premiere Pro"], ["Wedding Films", "Event Coverage", "Cinematic Albums"], 35000.0, 5, 4.83, 37, 98.1),
            ("Varun VFX", "varun@vfx.demo", "Cinematic VFX & Film Production", "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Runway Gen-3", "After Effects", "Nuke", "Unreal Engine 5"], ["VFX Film Production", "Green Screen Compositing", "CGI Integration"], 70000.0, 8, 4.88, 22, 98.4),
            ("Lakshmi Video", "lakshmi@video.demo", "Educational & Explainer Video Production", "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?auto=format&fit=crop&w=300&q=80", "Trivandrum", ["Runway Gen-3", "Canva AI", "CapCut AI"], ["Explainer Videos", "Tutorial Content", "Educational Films"], 18000.0, 3, 4.77, 52, 97.3),

            # AI Images
            ("Aurelia Image Studio", "aurelia@image.demo", "AI Image Generation & Photo Retouching", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80", "Delhi", ["Midjourney v6", "Flux.1", "Stable Diffusion", "Magnific AI"], ["AI Portrait Photography", "Editorial Stills", "Image Retouching"], 25000.0, 3, 4.93, 61, 99.4),
            ("Preethi Pixels", "preethi@pixels.demo", "AI Image Creation & Digital Photography", "https://images.unsplash.com/photo-1463453091185-61582044d556?auto=format&fit=crop&w=300&q=80", "Chennai", ["Midjourney v6", "ComfyUI", "Photoshop Generative", "Topaz Gigapixel"], ["Product Still Photography", "Lifestyle Images", "Portrait Retouching"], 20000.0, 2, 4.87, 48, 98.8),
            ("Rajan Photo AI", "rajan@photo.demo", "AI Image Generation & Photo Enhancement", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Flux.1", "Midjourney v6", "Adobe Firefly", "Lightroom AI"], ["Real Estate Photography", "Architecture Stills", "Aerial Imagery"], 30000.0, 3, 4.85, 39, 98.5),
            ("Sarita Visuals", "sarita@visuals.demo", "Generative Image Art & Photo Manipulation", "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Stable Diffusion XL", "Flux.1", "ComfyUI", "Magnific AI"], ["Digital Art Creation", "Photo Manipulation", "Concept Art"], 22000.0, 2, 4.89, 53, 99.0),
            ("Karthik Pixels", "karthik@pixels.demo", "AI Photo Editing & Image Generation", "https://images.unsplash.com/photo-1521119989659-a83eee488004?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Midjourney v6", "Photoshop AI", "Topaz Gigapixel", "Adobe Firefly"], ["Event Photography AI", "Corporate Headshots", "Still Life"], 15000.0, 2, 4.80, 67, 98.2),
            ("Asha Image Works", "asha@imageWorks.demo", "Editorial Image Photography & AI Editing", "https://images.unsplash.com/photo-1496346236851-c1a786571e98?auto=format&fit=crop&w=300&q=80", "Jaipur", ["Flux.1", "Midjourney v6", "Lightroom AI"], ["Fashion Editorial Images", "Beauty Retouching", "Magazine Stills"], 28000.0, 3, 4.91, 44, 99.1),
            ("Naveen Image Studio", "naveen@img.demo", "AI Image Generation & Brand Imagery", "https://images.unsplash.com/photo-1564564244660-5d73c057f2d2?auto=format&fit=crop&w=300&q=80", "Pune", ["DALL-E 3", "Midjourney v6", "Stable Diffusion", "Firefly"], ["Brand Imagery", "Social Media Images", "Product Photography"], 18000.0, 2, 4.82, 55, 98.4),
            ("Anjali Photo Lab", "anjali@photo.demo", "AI Photography & Image Retouching", "https://images.unsplash.com/photo-1548544149-4ab5a7b1b48e?auto=format&fit=crop&w=300&q=80", "Bhopal", ["Midjourney v6", "Adobe Firefly", "Lightroom AI", "Photoshop AI"], ["Wedding Photo Editing", "Portrait Photography", "Event Images"], 12000.0, 2, 4.76, 72, 97.4),
            ("Sathish Concept Art", "sathish@concept.demo", "AI Concept Art & Image Illustration", "https://images.unsplash.com/photo-1566492031773-4f4e44671857?auto=format&fit=crop&w=300&q=80", "Mysore", ["Midjourney v6", "Flux.1", "ComfyUI", "Stable Diffusion XL"], ["Concept Art", "Book Illustrations", "Character Design Images"], 32000.0, 3, 4.90, 36, 99.0),
            ("Vinita Studio", "vinita@studio.demo", "AI Image Art & Print Design", "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?auto=format&fit=crop&w=300&q=80", "Nagpur", ["Midjourney v6", "Adobe Firefly", "Canva AI"], ["Print Design Images", "Packaging Visuals", "Marketing Imagery"], 16000.0, 2, 4.79, 49, 97.8),
            ("Girish Photo Tech", "girish@photo.demo", "Commercial Photography & AI Enhancement", "https://images.unsplash.com/photo-1488161628813-04466f872be2?auto=format&fit=crop&w=300&q=80", "Surat", ["Topaz Gigapixel", "Midjourney v6", "Lightroom AI"], ["Commercial Product Photos", "E-commerce Images", "Catalogue Photography"], 20000.0, 2, 4.83, 58, 98.3),
            ("Meena Digital Art", "meena@digital.demo", "AI Digital Art & Image Composition", "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?auto=format&fit=crop&w=300&q=80", "Kochi", ["Stable Diffusion XL", "ComfyUI", "Flux.1", "Midjourney v6"], ["Digital Art", "Photo Compositing", "Surreal Art"], 24000.0, 3, 4.86, 41, 98.6),
            ("Hari AI Visuals", "hari@visuals.demo", "Photorealistic AI Image Generation", "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=300&q=80", "Lucknow", ["Flux.1 Pro", "Midjourney v6", "Magnific AI", "Topaz Gigapixel"], ["Photorealistic AI Images", "Product Visualization", "Lifestyle Photography"], 35000.0, 3, 4.92, 33, 99.2),
            ("Priya Image Lab", "priya@imglab.demo", "AI Image Processing & Creative Photography", "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=300&q=80", "Indore", ["Midjourney v6", "Adobe Firefly", "Photoshop AI"], ["Creative Photography", "Social Image Content", "Brand Photo Shoots"], 17000.0, 2, 4.81, 62, 97.9),
            ("Arun Photo Pro", "arun@photopro.demo", "Photography AI Enhancement & Editing", "https://images.unsplash.com/photo-1472099645-95d2f359f400?auto=format&fit=crop&w=300&q=80", "Chandigarh", ["Lightroom AI", "Topaz Photo AI", "Midjourney v6", "Adobe Firefly"], ["Professional Photo Editing", "Photo Restoration", "Color Grading"], 14000.0, 2, 4.78, 68, 97.5),

            # 3D & CGI
            ("Elysian 3D Works", "elysian@3d.demo", "3D CGI & Spatial Art Creation", "https://images.unsplash.com/photo-1599566150163-29194dcaad36?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Blender AI", "Cinema 4D", "Octane Render", "ComfyUI Flux"], ["3D Product Renders", "Architectural Visualization", "CGI Art"], 60000.0, 7, 4.96, 29, 99.0),
            ("Tara 3D Render", "tara@3drender.demo", "3D CGI Rendering & Architectural Visualization", "https://images.unsplash.com/photo-1531927935-9b2e3d6f5c51?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Blender", "3ds Max", "V-Ray", "Corona Renderer"], ["Interior Design 3D", "Architectural Renders", "Product 3D Modeling"], 50000.0, 6, 4.93, 35, 98.9),
            ("Sebastian 3D Studio", "sebastian@3d.demo", "Product 3D Modeling & CGI Animation", "https://images.unsplash.com/photo-1607746882042-944635dfe10e?auto=format&fit=crop&w=300&q=80", "Pune", ["Cinema 4D", "Houdini AI", "Unreal Engine 5", "Redshift"], ["Industrial 3D Renders", "Hard Surface CGI", "3D Product Animation"], 70000.0, 8, 4.91, 22, 98.1),
            ("Riya CGI Lab", "riya@cgi.demo", "3D CGI & Visual Storytelling", "https://images.unsplash.com/photo-1614289688-d11a74002154?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Blender AI", "Midjourney v6", "ComfyUI", "After Effects"], ["Motion Graphics 3D", "CGI Storytelling", "Character Render"], 45000.0, 5, 4.87, 28, 98.3),
            ("Amit CGI Works", "amit@cgi.demo", "3D Product CGI & Visualization", "https://images.unsplash.com/photo-1584917865-7d96e8f9e5f8?auto=format&fit=crop&w=300&q=80", "Delhi", ["3ds Max", "V-Ray", "Cinema 4D", "Substance Painter"], ["3D Product Visualization", "Packaging 3D", "Furniture Renders"], 40000.0, 5, 4.85, 33, 98.0),
            ("Sneha 3D Art", "sneha@3dart.demo", "3D Character Modeling & CGI", "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=300&q=80", "Chennai", ["ZBrush", "Blender", "Substance 3D", "Marvelous Designer"], ["Character 3D Modeling", "Game Asset Creation", "Stylized CGI"], 55000.0, 7, 4.89, 18, 98.5),
            ("Mohan Render Studio", "mohan@render.demo", "Architectural 3D CGI & Spatial Rendering", "https://images.unsplash.com/photo-1566753323237-a9c63db3baa8?auto=format&fit=crop&w=300&q=80", "Jaipur", ["3ds Max", "V-Ray", "SketchUp", "Enscape"], ["Architectural Visualization", "Interior Design Renders", "Urban Planning 3D"], 35000.0, 4, 4.82, 41, 97.8),
            ("Kriti 3D Motion", "kriti@3dmotion.demo", "3D Motion Graphics & CGI Advertising", "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Cinema 4D", "After Effects", "Redshift", "Blender"], ["3D Motion Advertising", "Logo Animation 3D", "Brand CGI"], 48000.0, 6, 4.88, 25, 98.4),
            ("Praveen 3D Studio", "praveen@3dstudio.demo", "Jewelry & Product 3D CGI", "https://images.unsplash.com/photo-1603415526960-f7e0328c6343?auto=format&fit=crop&w=300&q=80", "Surat", ["KeyShot", "Blender", "Cinema 4D", "Substance Painter"], ["Jewelry 3D Rendering", "Product 3D CGI", "Gemstone Visualization"], 38000.0, 4, 4.84, 46, 98.1),
            ("Lalitha CGI", "lalitha@cgi.demo", "Environmental 3D CGI & Game Asset Design", "https://images.unsplash.com/photo-1595152772835-219674b2a163?auto=format&fit=crop&w=300&q=80", "Coimbatore", ["Unreal Engine 5", "Blender", "Houdini", "Substance Painter"], ["Environment Design 3D", "Game Asset CGI", "World Building"], 52000.0, 6, 4.90, 21, 98.7),

            # Product Ads
            ("Vespera Campaign Lab", "vespera@campaign.demo", "Product Ads & Brand Campaigns", "https://images.unsplash.com/photo-1474176857210-7287d38d27c6?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Runway Gen-3", "Midjourney v6", "Photoshop AI", "DaVinci Resolve"], ["Product Ad Films", "Brand Campaign Direction", "Commercial Production"], 80000.0, 6, 4.94, 61, 98.9),
            ("Megha Product Ads", "megha@productads.demo", "E-commerce Product Advertising", "https://images.unsplash.com/photo-1476234251651-f353703a034d?auto=format&fit=crop&w=300&q=80", "Delhi", ["Adobe Firefly", "Midjourney v6", "Photoshop AI", "Canva AI"], ["Amazon Product Ads", "Flipkart Listings", "E-commerce Campaigns"], 22000.0, 3, 4.85, 74, 98.5),
            ("Rajesh Ad Works", "rajesh@adworks.demo", "Brand Product Commercial Advertising", "https://images.unsplash.com/photo-1534528741775-53994a69daea?auto=format&fit=crop&w=300&q=80", "Ahmedabad", ["Runway Gen-3", "ComfyUI", "Premiere Pro"], ["TV Commercial Production", "Digital Product Ads", "Brand Advertising"], 55000.0, 5, 4.88, 33, 98.6),
            ("Smita Campaign", "smita@campaign.demo", "Social Media Product Advertising", "https://images.unsplash.com/photo-1517841905240-472988babdf8?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Kling AI", "Midjourney v6", "CapCut AI"], ["Instagram Product Ads", "Facebook Campaigns", "Google Display Ads"], 28000.0, 3, 4.81, 59, 97.9),
            ("Nikhil Ad Studio", "nikhil@adstudio.demo", "Product Brand Advertising & Marketing Visuals", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1c?auto=format&fit=crop&w=300&q=80", "Pune", ["DALL-E 3", "Midjourney v6", "Stable Diffusion", "Photoshop AI"], ["Packaging Ad Design", "Marketing Materials", "Brand Identity Ads"], 35000.0, 4, 4.83, 42, 98.2),
            ("Shalini Ads", "shalini@ads.demo", "Fashion Product Ads & Lookbook Campaigns", "https://images.unsplash.com/photo-1573496359142-b8d87734a5a1?auto=format&fit=crop&w=300&q=80", "Chennai", ["Midjourney v6", "Flux.1", "Magnific AI", "Adobe Firefly"], ["Fashion Ad Campaigns", "Lifestyle Product Ads", "Lookbook Photography Ads"], 40000.0, 4, 4.89, 38, 98.7),
            ("Tarun Product Films", "tarun@productfilms.demo", "Product Commercial Video Advertising", "https://images.unsplash.com/photo-1544005313-94ddf0286df1?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Runway Gen-3", "Kling AI", "DaVinci Resolve", "After Effects"], ["Product Demo Videos", "Unboxing Film Production", "Explainer Ad Films"], 48000.0, 5, 4.86, 27, 98.3),
            ("Deepika Brand Ads", "deepika@brandads.demo", "Consumer Product Brand Campaign", "https://images.unsplash.com/photo-1500648767791-00dcc994a43d?auto=format&fit=crop&w=300&q=80", "Kolkata", ["Midjourney v6", "Adobe Firefly", "Stable Diffusion XL"], ["FMCG Brand Campaigns", "Consumer Product Ads", "Retail Marketing"], 25000.0, 3, 4.78, 51, 97.6),
            ("Mohandas Ad Agency", "mohandas@ads.demo", "360-Degree Product Brand Advertising", "https://images.unsplash.com/photo-1522075469751-3a6694fb2f60?auto=format&fit=crop&w=300&q=80", "Coimbatore", ["Runway Gen-3", "ComfyUI", "Midjourney v6"], ["Integrated Marketing Campaigns", "Multi-platform Product Ads", "Digital Marketing"], 62000.0, 6, 4.91, 23, 98.9),
            ("Prabhavathi Product", "prabha@product.demo", "Beauty & Personal Care Product Advertising", "https://images.unsplash.com/photo-1524504388940-b1c1722653e0?auto=format&fit=crop&w=300&q=80", "Lucknow", ["Adobe Firefly", "Midjourney v6", "Canva AI", "Photoshop AI"], ["Beauty Product Ads", "Skincare Campaign Images", "Cosmetics Advertising"], 20000.0, 2, 4.80, 65, 97.8),

            # Fashion
            ("Nadine Fashion Lab", "nadine@fashion.demo", "Fashion Photography & Lookbook Design", "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7d?auto=format&fit=crop&w=300&q=80", "Delhi / Mumbai", ["Midjourney v6", "Flux Schnell", "Photoshop Generative", "Magnific AI"], ["Fashion Photography", "Lookbook Design", "Textile Visual Art"], 50000.0, 4, 4.88, 31, 99.1),
            ("Theo Fashion Studio", "theo@fashion.demo", "Haute Couture Fashion Film & Styling", "https://images.unsplash.com/photo-1580489944761-15a19d654955?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Kling AI", "Runway Gen-3", "Marvelous Designer", "Flux.1"], ["Runway Choreography", "Fashion Film Direction", "Couture Styling"], 65000.0, 7, 4.93, 24, 97.9),
            ("Sunita Style", "sunita@style.demo", "Fashion Editorial & Street Style Photography", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c5?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Midjourney v6", "Adobe Firefly", "Lightroom AI"], ["Street Style Photography", "Fashion Editorial Stills", "Instagram Fashion Content"], 28000.0, 3, 4.83, 47, 98.2),
            ("Kavitha Couture", "kavitha@couture.demo", "Indian Couture & Bridal Fashion Imagery", "https://images.unsplash.com/photo-1492562080023-ab3db95bfbcd?auto=format&fit=crop&w=300&q=80", "Jaipur", ["Flux.1", "Midjourney v6", "Photoshop AI"], ["Bridal Fashion Photography", "Indian Couture Editorial", "Wedding Fashion Content"], 35000.0, 4, 4.87, 38, 98.4),
            ("Usha Textile Art", "usha@textile.demo", "Fashion Textile & Fabric Visual Design", "https://images.unsplash.com/photo-1501196354995-cbb51c65aae9?auto=format&fit=crop&w=300&q=80", "Surat", ["Stable Diffusion XL", "Flux.1", "ComfyUI"], ["Textile Pattern Design", "Fabric Visualization", "Fashion Textile Art"], 22000.0, 3, 4.79, 53, 97.7),
            ("Ritu Fashion Works", "ritu@fashion.demo", "Fashion Brand Campaigns & Lookbooks", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe6?auto=format&fit=crop&w=300&q=80", "Delhi", ["Midjourney v6", "DALL-E 3", "Adobe Firefly"], ["Fashion Brand Campaign", "Product Lookbook", "Retail Fashion Content"], 32000.0, 4, 4.84, 42, 98.0),
            ("Chandra Style Studio", "chandra@style.demo", "Ethnic & Contemporary Fashion Production", "https://images.unsplash.com/photo-1463453091185-61582044d555?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Midjourney v6", "Flux.1", "Lightroom AI"], ["Ethnic Fashion Photography", "Lifestyle Fashion Content", "Catalogue Shoots"], 25000.0, 3, 4.81, 49, 97.8),
            ("Rekha Fashion AI", "rekha@fashion.demo", "AI Fashion Design & Virtual Styling", "https://images.unsplash.com/photo-1494790108377-be9c29b2932f?auto=format&fit=crop&w=300&q=80", "Chennai", ["Stable Diffusion XL", "Midjourney v6", "ComfyUI", "Magnific AI"], ["Virtual Fashion Design", "AI Outfit Generation", "Digital Wardrobe Styling"], 40000.0, 4, 4.90, 29, 98.8),

            # Social Media
            ("Sana Social Media", "sana@social.demo", "Social Media Content & Digital Marketing", "https://images.unsplash.com/photo-1488426862026-3ee34a7d66de?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Canva AI", "Midjourney v6", "CapCut AI", "Adobe Express"], ["Instagram Content", "LinkedIn Posts", "YouTube Channel"], 15000.0, 2, 4.85, 89, 98.7),
            ("Akash Social Lab", "akash@social.demo", "Social Media Strategy & Content Creation", "https://images.unsplash.com/photo-1521119989659-a83eee488003?auto=format&fit=crop&w=300&q=80", "Delhi", ["Canva AI", "Kling AI", "Adobe Firefly", "CapCut AI"], ["Social Media Strategy", "Content Calendar", "Brand Social Content"], 20000.0, 2, 4.82, 73, 98.2),
            ("Divya Reels Studio", "divya@reels.demo", "Instagram Reels & Social Content Production", "https://images.unsplash.com/photo-1496346236851-c1a786571e97?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Kling AI", "Runway Gen-3", "CapCut AI"], ["Instagram Reels Production", "TikTok Content", "Story Content Creation"], 12000.0, 1, 4.78, 95, 97.5),
            ("Shanthi Social", "shanthi@social.demo", "Social Media & Community Management Content", "https://images.unsplash.com/photo-1564564244660-5d73c057f2d1?auto=format&fit=crop&w=300&q=80", "Chennai", ["Canva AI", "Adobe Firefly", "Midjourney v6"], ["Community Social Posts", "Brand Social Engagement", "Campaign Social Content"], 14000.0, 2, 4.80, 82, 97.9),
            ("Vishal Content Hub", "vishal@content.demo", "Social Media Content & Meme Marketing", "https://images.unsplash.com/photo-1548544149-4ab5a7b1b48d?auto=format&fit=crop&w=300&q=80", "Pune", ["DALL-E 3", "Canva AI", "CapCut AI"], ["Viral Social Content", "Meme Marketing", "Engagement Posts"], 10000.0, 1, 4.75, 107, 97.1),
            ("Nisha Digital", "nisha@digital.demo", "Digital Social Media & Influencer Content", "https://images.unsplash.com/photo-1566492031773-4f4e44671856?auto=format&fit=crop&w=300&q=80", "Kolkata", ["Midjourney v6", "Canva AI", "CapCut AI", "Adobe Express"], ["Influencer Content", "Social Brand Campaigns", "YouTube Content"], 16000.0, 2, 4.79, 76, 97.7),
            ("Pooja Social Works", "pooja@social.demo", "E-commerce Social Media Content", "https://images.unsplash.com/photo-1547425260-76bcadfb4f2b?auto=format&fit=crop&w=300&q=80", "Ahmedabad", ["Canva AI", "Adobe Firefly", "CapCut AI"], ["E-commerce Social Posts", "Product Social Content", "Shopping Campaign Posts"], 13000.0, 1, 4.77, 88, 97.4),
            ("Yusuf Content Creator", "yusuf@content.demo", "Long-form Social Content & YouTube Production", "https://images.unsplash.com/photo-1488161628813-04466f872be1?auto=format&fit=crop&w=300&q=80", "Lucknow", ["Runway Gen-3", "DaVinci Resolve", "Canva AI"], ["YouTube Video Production", "Podcast Content", "Long-form Social Media"], 25000.0, 3, 4.83, 54, 98.1),

            # Animation
            ("Valeria Animation Studio", "valeria@animation.demo", "2D & 3D Animation Production", "https://images.unsplash.com/photo-1567532939604-b6b5b0db2603?auto=format&fit=crop&w=300&q=80", "Mumbai", ["After Effects", "Cinema 4D", "Blender", "Runway Gen-3"], ["2D Character Animation", "Motion Graphics", "Animated Commercials"], 55000.0, 6, 4.90, 27, 98.7),
            ("Rohan Animation Lab", "rohan@anim.demo", "Motion Graphics & Kinetic Animation", "https://images.unsplash.com/photo-1551836022-d5d88e9218de?auto=format&fit=crop&w=300&q=80", "Delhi", ["After Effects", "Cinema 4D", "Houdini AI"], ["Logo Animation", "Explainer Animations", "Infographic Motion"], 40000.0, 5, 4.86, 34, 98.3),
            ("Bhavana Motion Art", "bhavana@motion.demo", "Animated Storytelling & Character Animation", "https://images.unsplash.com/photo-1531746020798-e6953c6e8e03?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Blender", "After Effects", "Toon Boom Harmony"], ["Character Animation", "Animated Short Films", "Cartoon Series"], 48000.0, 6, 4.88, 22, 98.5),
            ("Suresh Motion Studio", "suresh@motion.demo", "Corporate Animation & Explainer Videos", "https://images.unsplash.com/photo-1472099645-95d2f359f401?auto=format&fit=crop&w=300&q=80", "Chennai", ["After Effects", "Cinema 4D", "Canva AI"], ["Corporate Animated Presentations", "Explainer Video Animation", "Training Animations"], 30000.0, 4, 4.81, 48, 97.8),
            ("Kaveri Anime Studio", "kaveri@anime.demo", "Anime Style Animation & Illustration", "https://images.unsplash.com/photo-1599566150163-29194dcaad35?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Blender", "Stable Diffusion XL", "After Effects", "Clip Studio Paint"], ["Anime Animation", "Manga Illustration", "2D Character Design"], 35000.0, 5, 4.87, 31, 98.4),
            ("Nilesh Motion Design", "nilesh@motion.demo", "Motion Design & Animated Brand Identities", "https://images.unsplash.com/photo-1531927935-9b2e3d6f5c50?auto=format&fit=crop&w=300&q=80", "Pune", ["After Effects", "Cinema 4D", "Runway Gen-3"], ["Animated Brand Logos", "Motion Brand Identity", "Dynamic Typography"], 42000.0, 5, 4.84, 37, 98.1),
            ("Teena Animation Works", "teena@animation.demo", "UI Motion & App Animation Design", "https://images.unsplash.com/photo-1607746882042-944635dfe10d?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Rive", "After Effects", "Principle", "Lottie"], ["App UI Animation", "Micro-interaction Design", "Loading Animation"], 32000.0, 4, 4.82, 45, 97.9),
            ("Gopi Animation Lab", "gopi@animation.demo", "2D Kinetic Typography & Motion Animation", "https://images.unsplash.com/photo-1614289688-d11a74002153?auto=format&fit=crop&w=300&q=80", "Kolkata", ["After Effects", "Adobe Animate", "Canva AI"], ["Kinetic Typography Animation", "Lyric Video Animation", "Video Title Sequences"], 22000.0, 3, 4.78, 56, 97.5),

            # Graphic Design
            ("Julian Design Studio", "julian@design.demo", "Graphic Design & Brand Identity Visual Creation", "https://images.unsplash.com/photo-1584917865-7d96e8f9e5f7?auto=format&fit=crop&w=300&q=80", "Delhi", ["Adobe Illustrator", "Midjourney v6", "Photoshop AI", "Canva AI"], ["Brand Identity Design", "Logo Design", "Visual Communication"], 30000.0, 3, 4.91, 58, 99.1),
            ("Swati Design Lab", "swati@design.demo", "Graphic Design & Print Production", "https://images.unsplash.com/photo-1612349317150-e413f6a5b16c?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Adobe InDesign", "Photoshop AI", "Illustrator", "Canva AI"], ["Print Design", "Brochure Design", "Corporate Identity"], 22000.0, 3, 4.85, 47, 98.3),
            ("Prakash Typography", "prakash@typography.demo", "Typography Design & Graphic Art", "https://images.unsplash.com/photo-1566753323237-a9c63db3baa7?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Adobe Illustrator", "Midjourney v6", "Photoshop AI"], ["Custom Typography", "Type Design", "Lettering Art"], 25000.0, 3, 4.88, 39, 98.6),
            ("Meera Visual Design", "meera@visual.demo", "Graphic Design & UI/UX Visual Creation", "https://images.unsplash.com/photo-1560250097-0b93528c3119?auto=format&fit=crop&w=300&q=80", "Chennai", ["Figma AI", "Adobe Illustrator", "Midjourney v6", "Canva AI"], ["UI Visual Design", "App Graphics", "Web Design Visuals"], 28000.0, 3, 4.83, 52, 98.0),
            ("Arjun Graphics", "arjun@graphics.demo", "Illustration & Graphic Design for Brands", "https://images.unsplash.com/photo-1603415526960-f7e0328c6342?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["Adobe Illustrator", "Procreate AI", "Midjourney v6"], ["Brand Illustration", "Icon Design", "Editorial Graphics"], 18000.0, 2, 4.79, 64, 97.6),
            ("Nandita Design Art", "nandita@design.demo", "Packaging Design & Graphic Brand Identity", "https://images.unsplash.com/photo-1595152772835-219674b2a162?auto=format&fit=crop&w=300&q=80", "Pune", ["Adobe Illustrator", "Photoshop AI", "Canva AI", "Midjourney v6"], ["Packaging Design", "Product Label Design", "Brand Visual Identity"], 24000.0, 3, 4.82, 44, 97.9),
            ("Vivek Graphic Works", "vivek@graphic.demo", "Social Media Graphic Design & Creatives", "https://images.unsplash.com/photo-1474176857210-7287d38d27c5?auto=format&fit=crop&w=300&q=80", "Ahmedabad", ["Canva AI", "Adobe Illustrator", "Photoshop AI"], ["Social Media Graphics", "Digital Advertising Design", "Marketing Design"], 14000.0, 2, 4.77, 78, 97.4),
            ("Uma Design Studio", "uma@design.demo", "Infographic & Data Visualization Design", "https://images.unsplash.com/photo-1476234251651-f353703a034c?auto=format&fit=crop&w=300&q=80", "Jaipur", ["Adobe Illustrator", "Canva AI", "Flourish AI", "Datawrapper"], ["Infographic Design", "Data Visualization", "Report Design"], 20000.0, 2, 4.81, 55, 97.8),

            # Audio & Voice
            ("Sana AI Sound Lab", "sana@aisound.demo", "Generative Audio & Sonic Brand Identity", "https://images.unsplash.com/photo-1527980965255-d3b416303d12?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Suno v3", "Udio", "ElevenLabs", "Ableton Live"], ["Sonic Branding", "AI Music Composition", "Brand Sound Identity"], 40000.0, 3, 4.89, 56, 99.6),
            ("Rohit Voice Studio", "rohit@voice.demo", "Professional Voice-over & AI Voice Production", "https://images.unsplash.com/photo-1543610892-0b1f7e6d8ac1?auto=format&fit=crop&w=300&q=80", "Delhi", ["ElevenLabs", "Murf AI", "Adobe Audition", "Pro Tools"], ["Professional Voice-over", "AI Dubbing", "Audiobook Narration"], 20000.0, 2, 4.87, 83, 99.1),
            ("Priya Music AI", "priya@music.demo", "AI Music Composition & Jingle Production", "https://images.unsplash.com/photo-1507152832244-10d45c7eda57?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Suno v3", "Udio", "Ableton Live", "Logic Pro"], ["Jingle Production", "Background Music", "Brand Music"], 30000.0, 3, 4.85, 41, 98.8),
            ("Arjun Sound Design", "arjun@sound.demo", "Audio Production & Sound Design for Media", "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=300&q=80", "Chennai", ["Pro Tools", "Logic Pro", "ElevenLabs", "Suno v3"], ["Film Sound Design", "Game Audio", "Podcast Production"], 35000.0, 4, 4.88, 35, 98.5),
            ("Kavitha Voice AI", "kavitha@voice.demo", "AI Voice Synthesis & Audio Localization", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe5?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["ElevenLabs", "Murf AI", "Google TTS AI", "Adobe Podcast AI"], ["Multilingual Voice-over", "AI Voice Cloning", "Audio Localization"], 25000.0, 2, 4.82, 67, 98.2),
            ("Vinay Podcast Studio", "vinay@podcast.demo", "Podcast Production & Audio Branding", "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=300&q=80", "Pune", ["Adobe Podcast AI", "Descript AI", "Auphonic", "Logic Pro"], ["Podcast Production", "Audio Branding", "Interview Recording & Editing"], 18000.0, 2, 4.79, 71, 97.8),
            ("Meena Music Works", "meena@music.demo", "Instrumental AI Music & Soundtrack Creation", "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=300&q=80", "Kochi", ["Suno v3", "Udio", "Ableton Live", "FL Studio AI"], ["Instrumental Soundtracks", "Film Background Music", "Video Game OST"], 28000.0, 3, 4.84, 48, 98.0),
            ("Suresh Audio Works", "suresh@audio.demo", "Commercial Audio Mixing & Sound Engineering", "https://images.unsplash.com/photo-1586297135537-94bc9ba060aa?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Pro Tools", "Dolby Atmos Tools", "Logic Pro", "Adobe Audition"], ["Commercial Sound Mixing", "Spatial Audio Production", "Mastering Services"], 45000.0, 4, 4.91, 29, 99.0),
            ("Tanvi Sonic Lab", "tanvi@sonic.demo", "Audio & Voice AI Synthesis", "https://images.unsplash.com/photo-1517841905240-472988babdf7?auto=format&fit=crop&w=300&q=80", "Delhi", ["ElevenLabs", "Suno v3", "Logic Pro"], ["AI Voice Acting", "Podcast Audio Mix", "Sound Branding"], 22000.0, 2, 4.86, 44, 98.4),
            ("Vikram 3D Studio", "vikram@3d.demo", "3D & CGI Spatial Visualization", "https://images.unsplash.com/photo-1492562080023-ab3db95bfbcc?auto=format&fit=crop&w=300&q=80", "Bangalore", ["Blender", "Unreal Engine 5", "Cinema 4D"], ["3D Hard Surface", "Spatial VFX", "Product CGI"], 54000.0, 5, 4.89, 31, 98.6),
            ("Kiran CGI Lab", "kiran@cgi.demo", "3D & CGI Architectural Rendering", "https://images.unsplash.com/photo-1534528741775-53994a69dae9?auto=format&fit=crop&w=300&q=80", "Mumbai", ["3ds Max", "V-Ray", "Blender AI"], ["Architectural CGI", "Interior Spatial 3D", "Photoreal CGI"], 42000.0, 4, 4.83, 39, 98.0),
            ("Isha Fashion Design", "isha@fashion.demo", "Fashion Lookbooks & Digital Haute Couture", "https://images.unsplash.com/photo-1522075469751-3a6694fb2f5f?auto=format&fit=crop&w=300&q=80", "Delhi", ["Midjourney v6", "Flux.1", "Photoshop AI"], ["Haute Couture Editorial", "Runway AI Visuals", "Garment Stills"], 48000.0, 4, 4.91, 35, 98.8),
            ("Maya Couture Studio", "maya@couture.demo", "Fashion Lookbooks & Textile AI", "https://images.unsplash.com/photo-1517841905240-472988babdf6?auto=format&fit=crop&w=300&q=80", "Jaipur", ["Flux.1 Pro", "Midjourney v6", "ComfyUI"], ["Textile Synthesis", "Ethnic Bridal Fashion", "Couture Design"], 36000.0, 3, 4.85, 40, 98.2),
            ("Rohit Social Studio", "rohit@social.demo", "Social Media Viral Video & Reels", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c4?auto=format&fit=crop&w=300&q=80", "Bangalore", ["CapCut AI", "Runway Gen-3", "Canva AI"], ["Instagram Reels", "Viral TikTok Content", "Short Clips"], 18000.0, 2, 4.81, 75, 97.9),
            ("Ananya Social Media", "ananya@social.demo", "Social Media Content Strategy & Posts", "https://images.unsplash.com/photo-1524504388940-b1c1722653df?auto=format&fit=crop&w=300&q=80", "Mumbai", ["Canva AI", "Midjourney v6", "CapCut AI"], ["Brand Social Strategy", "Instagram Grid Design", "Short Stories"], 15000.0, 2, 4.79, 84, 97.6),
            ("Devansh Animation", "devansh@anim.demo", "Animation & Motion Graphics", "https://images.unsplash.com/photo-1500648767791-00dcc994a43c?auto=format&fit=crop&w=300&q=80", "Hyderabad", ["After Effects", "Cinema 4D", "Blender"], ["2D Explainer Animation", "Motion Logo Design", "Animated Ads"], 38000.0, 4, 4.86, 32, 98.3),
            ("Simran Graphic Art", "simran@graphics.demo", "Graphic Design & Packaging Art", "https://images.unsplash.com/photo-1580489944761-15a19d654954?auto=format&fit=crop&w=300&q=80", "Delhi", ["Adobe Illustrator", "Photoshop AI", "Canva AI"], ["Brand Graphics", "Package Artwork", "Visual Identity"], 26000.0, 3, 4.84, 49, 98.1),
        ]

        creator_entities = []

        # Aarav Studio profile (demo creator user)
        aarav_prof = CreatorProfile(
            user_id=creator_user.id,
            display_name="Aarav Studio",
            tagline="Premier AI Cinema Director & Kinetic Worldbuilder",
            specialization="Cinematic Video & Luxury Automotive",
            skills=["Kinetic Runway Direction", "Photoreal Hypercar Rendering", "Color Grading & Lighting", "Commercial Sound Mix"],
            ai_tools=["Midjourney v6", "Runway Gen-3", "ComfyUI Flux", "Sora", "DaVinci Resolve"],
            starting_rate=75000.0,
            delivery_days=6,
            commercial_rights=True,
            availability_status="available",
            rating=4.98,
            total_briefs=48,
            sla_score=99.5,
            on_time_percentage=100.0,
            is_verified=True,
            location="Paris / Milan Sync",
        )
        db.add(aarav_prof)
        creator_entities.append(aarav_prof)

        DIVERSE_AVATARS = [
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/0.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/0.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/1.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/1.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/2.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/2.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/3.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/3.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/4.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/4.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/5.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/5.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/6.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/6.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/7.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/7.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/8.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/8.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/9.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/9.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/10.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/10.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/11.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/11.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/12.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/12.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/13.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/13.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/14.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/14.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/15.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/15.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/16.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/16.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/17.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/17.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/18.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/18.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/19.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/19.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/20.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/20.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/21.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/21.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/22.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/22.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/23.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/23.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/24.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/24.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/25.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/25.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/26.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/26.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/27.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/27.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/28.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/28.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/29.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/29.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/30.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/30.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/31.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/31.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/32.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/32.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/33.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/33.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/34.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/34.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/35.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/35.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/36.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/36.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/37.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/37.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/38.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/38.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/39.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/39.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/40.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/40.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/41.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/41.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/42.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/42.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/43.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/43.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/44.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/44.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/45.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/45.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/46.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/46.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/47.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/47.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/48.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/48.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/49.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/49.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/50.jpg',
            'https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/male/512/50.jpg',
        ]

        for i, (name, email, spec, original_avatar, loc, tools, skills, rate, days, rating, briefs_count, sla) in enumerate(creators_meta):
            assigned_avatar = DIVERSE_AVATARS[i % len(DIVERSE_AVATARS)]
            u = User(
                email=email,
                password_hash=demo_pw,
                full_name=name,
                role="creator",
                avatar_url=assigned_avatar,
                bio=f"Senior generative director specializing in {spec.lower()}. Trusted partner for international maisons and agency producers.",
                location=loc,
                is_active=True,
            )
            db.add(u)
            db.flush()

            prof = CreatorProfile(
                user_id=u.id,
                display_name=name,
                tagline=f"Master AI Director — {spec}",
                specialization=spec,
                skills=skills,
                ai_tools=tools,
                starting_rate=rate,
                delivery_days=days,
                commercial_rights=True,
                availability_status="available",
                rating=rating,
                total_briefs=briefs_count,
                sla_score=sla,
                on_time_percentage=99.0,
                is_verified=True,
                location=loc,
            )
            db.add(prof)
            creator_entities.append(prof)

        db.commit()

        # 3. Creator Verifications and Achievements
        verif_types = ["identity", "tools", "portfolio", "workflow", "past_work", "commercial_rights"]
        for c in creator_entities:
            for v_type in verif_types:
                db.add(Verification(
                    creator_id=c.id,
                    verification_type=v_type,
                    status="verified",
                    details=f"Verified {v_type} provenance through Maccall Tier-1 standards protocol.",
                ))
            db.add(CreatorAchievement(
                creator_id=c.id,
                title="Tier-1 Verified Director",
                description="Completed rigorous multi-factor authentication and commercial portfolio audit.",
                badge_type="verified",
            ))
            if c.rating >= 4.95:
                db.add(CreatorAchievement(
                    creator_id=c.id,
                    title="Master of the Cycle 2026",
                    description="Awarded for delivering exceptional creative fidelity and 100% SLA compliance.",
                    badge_type="award",
                ))

        # 4. Category Portfolio Thumbnails library
        CAT_PORTFOLIO_LIBRARY = {
            "video": [
                ("Aethelgard 2026: Hyper-Luxury Runway", "Commercial generative automotive film marrying couture and kinetic aerodynamics.", "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80"),
                ("Veloce GT Synthetic Reveal", "Hyper-photorealistic commercial showcase for next-gen electric hypercar.", "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80"),
                ("Chronos Horizon: Orbital VFX Sequence", "Anamorphic sci-fi cinematic sequence with volumetric nebulae and ships.", "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80"),
                ("Neo-Tokyo 2099 Commercial", "High-octane neon night race across a futuristic vertical metropolis.", "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=1200&q=80"),
                ("L'Ã‰ternitÃ©: 35mm French Riviera Film", "Warm vintage film grain commercial capturing summer yachting elegance.", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"),
                ("The Last Artisan: Generative Documentary", "Emotive documentary series capturing traditional woodcarving with AI camera.", "https://images.unsplash.com/photo-1452860606245-08befc0ff44b?auto=format&fit=crop&w=1200&q=80"),
            ],
            "image": [
                ("Aura Lumina: Resort Stills", "Synthetic photography exploring translucent glass-woven garments.", "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80"),
                ("Solitude Noir: Monograph Stills", "Monochrome film emulation with organic grain microstructure preservation.", "https://images.unsplash.com/photo-1481349518771-20055b2a7b24?auto=format&fit=crop&w=1200&q=80"),
                ("Prismatic Highlands: Fine Art Photography", "Aerial volcanic topography captured with hyper-real generative resolution.", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80"),
                ("Alpine Aurora: Generative Landscape", "Nordic glacial aesthetic studies with dynamic volumetric light.", "https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&w=1200&q=80"),
                ("Floral Geometry: Macro Biology", "Ultra-macro botany study with prismatic light diffusion.", "https://images.unsplash.com/photo-1518895949257-7621c3c786d7?auto=format&fit=crop&w=1200&q=80"),
            ],
            "3d": [
                ("Celestial Polyphony 3D", "Procedural crystal flora reacting to synthetic soundwaves in real-time.", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"),
                ("Void & Mirage XR Pavilion", "Interactive virtual architectural installation for Venice Biennale AI Pavilion.", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"),
                ("Kinetix Chrono Watch Reveal", "Exploded mechanical watch render featuring hyper-detailed titanium gears.", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1200&q=80"),
                ("Apple Vision Pro: Mirage Sanctum", "Volumetric gaussian splatting experience featuring floating zen gardens.", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80"),
                ("Cybernetic Hard Surface Monolith", "Procedural industrial design with photoreal dielectric roughness.", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80"),
            ],
            "product": [
                ("Equinox Global Launch Campaign", "Multimodal campaign spanning 12 autonomous video outputs and 40 social stills.", "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80"),
                ("L'Or Brut: Prismatic Diamond Macro", "Ultra-macro 8K diamond facet reflection with spectral dispersion.", "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=1200&q=80"),
                ("Bespoke Timepiece Macro Showcase", "Zero-gravity fluid viscosity conditioning with anisotropic brushed metal.", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80"),
                ("Artisan Perfume Glass Refraction", "Liquid caustic reflections through hand-blown luxury crystal flacons.", "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80"),
                ("Aero Minimalist Footwear Commercial", "Dynamic kinetic particle simulation highlighting ergonomic mesh.", "https://images.unsplash.com/photo-1542744173-8659-43-d2-a7f3?auto=format&fit=crop&w=1200&q=80"),
            ],
            "fashion": [
                ("Maison Obsidian: Cybernetic Silk", "Digital haute couture collection film with procedural cloth aerodynamics.", "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1200&q=80"),
                ("Komorebi Silk Campaign", "Editorial stills capturing dynamic dappled sunlight across digital organza.", "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=80"),
                ("Fluid Motion: Cyber Couture 2026", "Zero-gravity fabric simulation moving through luminous liquid light.", "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=1200&q=80"),
                ("Eclipse 2026: Noir Runway", "Monochrome runway film featuring rain-slicked concrete and neon accents.", "https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?auto=format&fit=crop&w=1200&q=80"),
                ("Velvet & Algorithm Lookbook", "Autumn capsule collection rendering with rich burgundy velvets.", "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=80"),
            ],
            "social": [
                ("Viral Horizon: Short-Form Reel Suite", "High-velocity dynamic motion clips optimized for social virality.", "https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=1200&q=80"),
                ("Pulse Velocity: Dynamic Motion Grid", "Vibrant kinetic typography and micro-interactions for digital campaigns.", "https://images.unsplash.com/photo-1516251193007-45ef944ab0c6?auto=format&fit=crop&w=1200&q=80"),
                ("Urban Kinetic: Community Stories", "Lifestyle storytelling vignettes with authentic natural light grading.", "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80"),
            ],
            "animation": [
                ("Mythos Neon: 2D Kinetic Sequence", "Cyberpunk vector animation blending traditional cel art with procedural physics.", "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1200&q=80"),
                ("Hyper-Kinetic Character Odyssey", "Dynamic character keyframes with emotional expression synthesis.", "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1200&q=80"),
                ("Prismatic Fluid Motion Graphics", "Complex fluid particle simulations rendered for title sequences.", "https://images.unsplash.com/photo-1563089145-599997674d42?auto=format&fit=crop&w=1200&q=80"),
            ],
            "design": [
                ("Swiss Typographic Architecture", "Rigorous grid systems and generative typography for spatial exhibits.", "https://images.unsplash.com/photo-1558655686-d3c0b1f8b18a?auto=format&fit=crop&w=1200&q=80"),
                ("Minimalist Identity & Monograph", "Editorial monograph design with bespoke layout and color harmony.", "https://images.unsplash.com/photo-1561986635-1-99b5a8-7ee5?auto=format&fit=crop&w=1200&q=80"),
                ("Bespoke Brand System & Collateral", "Comprehensive visual language system across print, digital and spatial.", "https://images.unsplash.com/photo-1541462608143-67571c6738dd?auto=format&fit=crop&w=1200&q=80"),
            ],
            "audio": [
                ("Resonance Suite #4 (Spatial Binaural)", "Generative neoclassical soundtrack synchronized to architectural lighting.", "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80"),
                ("Atelier Sonic Identity 2026", "Signature sonic mnemonic brand suite for luxury fragrance house.", "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=1200&q=80"),
                ("Harmonic Frequency Synthesis", "Adaptive spatial sound design with real-time reactive audio stems.", "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1200&q=80"),
            ],
        }

        # Seed 1-2 category-appropriate portfolio pieces for every single creator
        for c in creator_entities:
            spec_str = (c.specialization or "").lower()
            cat_key = "image"
            if any(k in spec_str for k in ["video", "cinematic", "film", "vfx"]):
                cat_key = "video"
            elif any(k in spec_str for k in ["3d", "cgi", "spatial", "render"]):
                cat_key = "3d"
            elif any(k in spec_str for k in ["product", "commercial", "ad", "campaign"]):
                cat_key = "product"
            elif any(k in spec_str for k in ["fashion", "couture", "textile", "lookbook"]):
                cat_key = "fashion"
            elif any(k in spec_str for k in ["social", "reels", "tiktok"]):
                cat_key = "social"
            elif any(k in spec_str for k in ["animation", "motion", "kinetic", "anime"]):
                cat_key = "animation"
            elif any(k in spec_str for k in ["graphic", "design", "typography"]):
                cat_key = "design"
            elif any(k in spec_str for k in ["audio", "sound", "voice", "music", "sonic"]):
                cat_key = "audio"

            items = CAT_PORTFOLIO_LIBRARY.get(cat_key, CAT_PORTFOLIO_LIBRARY["image"])
            item_choice = items[c.id % len(items)]

            db.add(PortfolioItem(
                creator_id=c.id,
                title=f"{c.display_name}: {item_choice[0]}",
                description=item_choice[1],
                image_url=item_choice[2],
                category=cat_key,
                tools_used=c.ai_tools or ["Midjourney v6", "Runway Gen-3"],
            ))

        db.commit()

        # 5. Briefs (5 rich creative briefs)
        briefs_seed = [
            Brief(
                brand_user_id=brand_user.id,
                title="Aethelgard 2026 Hypercar Global Video Reveal",
                description="High-concept 30-second commercial marrying kinetic hypercar aerodynamics with cyber-couture fashion models. Needs 4K master ProRes and clean plates.",
                prompt_text="Create a luxury kinetic runway commercial for an electric hypercar in Paris at night with rain reflections, moody anamorphic lighting, and high-fashion cyber couture.",
                content_type="video",
                style="Warm Editorial Luxury, Cinematic 35mm",
                target_audience="Ultra-high-net-worth automotive enthusiasts and luxury design collectors",
                platform=["Instagram Reels", "YouTube", "Website"],
                duration="30 seconds",
                aspect_ratio="16:9",
                deliverables=["4K ProRes Master", "9:16 Social Cutdowns", "Clean Plate", "Sound Mix"],
                tools_suggested=["Midjourney v6", "Runway Gen-3", "ComfyUI", "DaVinci Resolve"],
                budget_min=4500.0,
                budget_max=9000.0,
                deadline=datetime.utcnow() + timedelta(days=21),
                commercial_rights_required=True,
                status="published",
                visual_reference_url="https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80",
            ),
            Brief(
                brand_user_id=brand_user.id,
                title="Maison Lumina: L'Or Ã‰thÃ©rÃ© Perfume Launch",
                description="Sensory macro video capturing golden liquid particles swirling into a crystal bottle silhouette with warm editorial tones.",
                prompt_text="Produce a macro commercial for a luxury perfume bottle surrounded by floating gold leaf flakes and morning sunlight in Tuscany.",
                content_type="video",
                style="Warm Editorial Luxury",
                target_audience="Luxury fragrance buyers and fashion connoisseurs aged 25-45",
                platform=["Instagram Reels", "TikTok"],
                duration="15 seconds",
                aspect_ratio="9:16",
                deliverables=["4K Master 9:16", "Raw Stems", "Color LUTs"],
                tools_suggested=["ComfyUI Flux", "Runway Gen-3", "Topaz AI"],
                budget_min=2500.0,
                budget_max=5000.0,
                deadline=datetime.utcnow() + timedelta(days=14),
                commercial_rights_required=True,
                status="in_progress",
                visual_reference_url="https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
            ),
            Brief(
                brand_user_id=brand_user.id,
                title="Spatial Computing Pavilion: Vision Pro XR Stills & 3D",
                description="10 volumetric spatial art pieces depicting generative biodomes and futuristic crystalline sanctuaries.",
                prompt_text="Generate 3D spatial environments for XR headsets featuring biophilic architecture, ambient light, and floating botanical forms.",
                content_type="3d",
                style="Ethereal Surrealism, Sci-Fi",
                target_audience="Spatial computing designers and tech innovators",
                platform=["Apple Vision Pro", "Web Campaign"],
                duration="Spatial Assets",
                aspect_ratio="1:1",
                deliverables=["USDZ Spatial Models", "8K Panoramas", "Depth Maps"],
                tools_suggested=["Unreal Engine 5 AI", "Spline AI", "ComfyUI"],
                budget_min=3500.0,
                budget_max=7000.0,
                deadline=datetime.utcnow() + timedelta(days=30),
                commercial_rights_required=True,
                status="published",
                visual_reference_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            ),
            Brief(
                brand_user_id=brand_user.id,
                title="Apex Runner: Cyberpunk Sneaker Drop Visuals",
                description="Fast-paced kinetic animation showcasing parametric sneaker sole compression and dynamic neon energy trails.",
                prompt_text="High energy sneaker commercial in Tokyo Shibuya cyberpunk setting with rain, reflections, and glitch typography.",
                content_type="video",
                style="Sci-Fi Cyberpunk",
                target_audience="Sneakerheads, Gen Z streetwear enthusiasts",
                platform=["TikTok", "Instagram Reels"],
                duration="20 seconds",
                aspect_ratio="9:16",
                deliverables=["4K Video", "Sound Design Track", "Story Stills"],
                tools_suggested=["Kling AI", "Runway Gen-3", "Cinema 4D"],
                budget_min=2000.0,
                budget_max=4000.0,
                deadline=datetime.utcnow() + timedelta(days=10),
                commercial_rights_required=True,
                status="published",
                visual_reference_url="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=1200&q=80",
            ),
            Brief(
                brand_user_id=brand_user.id,
                title="Nocturne Maison: Ambient Sonic Identity",
                description="Full generative audio identity package including 3 dynamic soundtrack movements, UX sound mnemonics, and spatial audio stem mix.",
                prompt_text="Compose an elegant warm neoclassical ambient sonic identity for a luxury hotel and boutique group.",
                content_type="audio",
                style="Minimal Organic",
                target_audience="Luxury hospitality guests",
                platform=["Website", "In-Store Audio", "App"],
                duration="3 movements (3 min each)",
                aspect_ratio="N/A",
                deliverables=["Lossless 24-bit WAV Master", "Stems", "Dolby Atmos Mix"],
                tools_suggested=["Suno v3", "ElevenLabs", "Ableton Live"],
                budget_min=1800.0,
                budget_max=3500.0,
                deadline=datetime.utcnow() + timedelta(days=18),
                commercial_rights_required=True,
                status="draft",
                visual_reference_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80",
            ),
        ]
        db.add_all(briefs_seed)
        db.commit()
        for b in briefs_seed:
            db.refresh(b)

        # 6. Workspaces (5 active workspaces with encrypted messages & milestones)
        ws_configs = [
            ("Aethelgard 2026 Hypercar Commercial", creator_entities[0].user_id, briefs_seed[0].id, "production"),
            ("L'Or Ã‰thÃ©rÃ© Fragrance Campaign", creator_entities[1].user_id, briefs_seed[1].id, "review"),
            ("Chronos VFX Title Sequence", creator_entities[2].user_id, briefs_seed[3].id, "brief_approved"),
            ("Nocturne Ambient Sound Branding", creator_entities[3].user_id, briefs_seed[4].id, "discovery"),
            ("Spatial XR Pavilion Development", creator_entities[4].user_id, briefs_seed[2].id, "delivered"),
        ]

        for title, c_uid, b_id, status in ws_configs:
            ws = Workspace(
                brief_id=b_id,
                brand_user_id=brand_user.id,
                creator_user_id=c_uid,
                title=title,
                status=status,
            )
            db.add(ws)
            db.flush()

            # Workspace Members
            db.add(WorkspaceMember(workspace_id=ws.id, user_id=brand_user.id, role="brand"))
            db.add(WorkspaceMember(workspace_id=ws.id, user_id=c_uid, role="creator"))

            # Milestones
            m1 = WorkspaceMilestone(
                workspace_id=ws.id,
                title="Concept Frames & Aesthetic Alignment",
                description="Exploration of key lighting, textures, and prompt seeds.",
                amount=1200.0,
                status="released" if status in ["production", "review", "delivered"] else "approved",
                completed_at=datetime.utcnow() - timedelta(days=3) if status in ["production", "review", "delivered"] else None,
            )
            m2 = WorkspaceMilestone(
                workspace_id=ws.id,
                title="4K Motion Synthesis & Cut Pass",
                description="Generation of dynamic scenes and initial rhythm synchronization.",
                amount=2000.0,
                status="released" if status in ["review", "delivered"] else ("in_review" if status == "production" else "pending"),
            )
            m3 = WorkspaceMilestone(
                workspace_id=ws.id,
                title="Final Mastering, Color Grading & Audio Stem Delivery",
                description="ProRes 4444 master output and commercial license grant.",
                amount=1800.0,
                status="released" if status == "delivered" else "pending",
            )
            db.add_all([m1, m2, m3])
            db.flush()

            # Messages (Encrypted at rest!)
            msg1 = WorkspaceMessage(
                workspace_id=ws.id,
                sender_id=brand_user.id,
                encrypted_content=encrypt_message("Hello! We are thrilled to kick off this collaboration. The brand guidelines and visual references are ready."),
                created_at=datetime.utcnow() - timedelta(days=5),
            )
            msg2 = WorkspaceMessage(
                workspace_id=ws.id,
                sender_id=c_uid,
                encrypted_content=encrypt_message("Excited to work together on this! I have prepared the initial concept frames and lighting direction."),
                created_at=datetime.utcnow() - timedelta(days=4),
            )
            msg3 = WorkspaceMessage(
                workspace_id=ws.id,
                sender_id=brand_user.id,
                encrypted_content=encrypt_message("The first look is phenomenal. Let's proceed to the second milestone for full motion synthesis."),
                created_at=datetime.utcnow() - timedelta(days=2),
            )
            db.add_all([msg1, msg2, msg3])

            # Shared Files
            db.add(SharedFile(
                workspace_id=ws.id,
                uploader_id=brand_user.id,
                filename="Maison_Brand_Guidelines_2026.pdf",
                file_size="18.4 MB",
                file_type="document",
                description="Core palette, typography, and mood references.",
            ))
            db.add(SharedFile(
                workspace_id=ws.id,
                uploader_id=c_uid,
                filename="Style_Frames_Pass_01.zip",
                file_size="84.2 MB",
                file_type="zip",
                description="High-res 4K Midjourney/Flux concept renders.",
            ))

            # Revision request if in review
            if status == "review":
                db.add(RevisionRequest(
                    workspace_id=ws.id,
                    milestone_id=m2.id,
                    requester_id=brand_user.id,
                    description="Could we soften the anamorphic blue flare around second 0:18 and increase warmth on the car bodywork?",
                    status="open",
                ))

        db.commit()

        # 7. Shortlist entries for brand user
        db.add(Shortlist(
            brand_user_id=brand_user.id,
            creator_user_id=creator_entities[0].user_id,
            brief_id=briefs_seed[0].id,
        ))
        db.add(Shortlist(
            brand_user_id=brand_user.id,
            creator_user_id=creator_entities[1].user_id,
            brief_id=briefs_seed[1].id,
        ))
        db.add(Shortlist(
            brand_user_id=brand_user.id,
            creator_user_id=creator_entities[2].user_id,
            brief_id=briefs_seed[2].id,
        ))
        db.commit()

        # 8. Community Posts (14+ posts with likes and comments)
        post_seeds = [
            (creator_entities[0].user_id, "showcase", "Aethelgard 2026: Anamorphic Light Studies", "Behind the scenes on our latest kinetic runway showcase. Combining ComfyUI Flux with Runway Gen-3 camera tracking for crisp automotive reflections.", "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80", ["Midjourney v6", "Runway Gen-3", "ComfyUI"]),
            (creator_entities[1].user_id, "showcase", "Synthetic Silk & Translucent Glass Couture", "Exploring light refraction through procedurally simulated glass textiles. All assets rendered in 4K with custom LoRA fine-tuning.", "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80", ["Flux.1", "Midjourney v6", "ComfyUI"]),
            (creator_entities[2].user_id, "achievement", "Winner: Best Sci-Fi Commercial Direction 2026", "Honored to receive the Tier-1 Director distinction on Maccall! Shoutout to our clients for pushing the envelope on generative visual storytelling.", "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80", ["Runway Gen-3", "Unreal Engine 5"]),
            (creator_entities[3].user_id, "service", "Sonic Branding & Spatial Audio Commissions Open", "Accepting 2 new maison partnerships for Spring 2026. Custom AI generative scores, voice clones, and binaural soundscapes.", "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80", ["Suno v3", "Udio", "ElevenLabs"]),
            (creator_entities[4].user_id, "collaboration", "Looking for 3D Fashion Director for XR Installation", "Building an interactive virtual showroom for an international couture brand. Need an expert in Marvelous Designer + Flux.", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80", ["Spline", "ComfyUI", "Blender AI"]),
            (creator_entities[5].user_id, "open_brief", "Autonomous Multimodal Campaign Workflow Guide", "Just published our internal benchmark on coordinating LLM prompt architectures with multi-model video generation pipelines.", "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80", ["Claude 3.5", "Runway Gen-3", "Midjourney v6"]),
            (creator_entities[6].user_id, "showcase", "35mm Film Grain Emulation in Modern AI Cinema", "Techniques for achieving authentic Kodak 5219 grain and halation on synthetic footage without losing resolution.", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80", ["Topaz Video AI", "DaVinci Resolve", "Midjourney"]),
            (creator_entities[7].user_id, "showcase", "Kinetix Chrono: Hard Surface 3D Animation", "Exploded watch movement rendered with procedural titanium shaders and photoreal studio lighting.", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1200&q=80", ["Houdini AI", "Cinema 4D"]),
            (creator_entities[8].user_id, "showcase", "Minimalist Nordic Villa: Volcanic Architectural Series", "Studies in concrete texture, overcast diffuse lighting, and organic geometry.", "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80", ["Flux Schnell", "Rhino 3D"]),
            (creator_entities[9].user_id, "showcase", "Fluid Dynamics & Zero-G Fashion Simulation", "Simulating 10,000 liquid particles interacting with velvet cloth geometry in Kling AI.", "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=1200&q=80", ["Kling AI", "Marvelous Designer"]),
            (creator_entities[10].user_id, "showcase", "Prismatic Gemstone Dispersion at 8K", "Macro photography studies in diamond internal reflection and chromatic dispersion.", "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=1200&q=80", ["ComfyUI", "Topaz Gigapixel"]),
            (creator_entities[11].user_id, "showcase", "The Last Artisan: AI Documentary Stills", "Preserving human craft traditions through respectful and hyper-detailed generative cinema.", "https://images.unsplash.com/photo-1452860606245-08befc0ff44b?auto=format&fit=crop&w=1200&q=80", ["Luma Dream Machine", "Midjourney v6"]),
            (creator_entities[12].user_id, "showcase", "Volumetric Sanctum on Apple Vision Pro", "Real-time gaussian splatting rendering inside spatial computing headsets.", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80", ["Unreal Engine 5 AI", "Spline AI"]),
            (brand_user.id, "creator_request", "Seeking High-End Haute Couture Director for Autumn Campaign", "Maison Lumina is accepting creator submissions for our flagship international Fall campaign. Apply with your portfolio.", "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1200&q=80", ["Midjourney v6", "Flux.1", "Runway Gen-3"]),
        ]

        posts_added = []
        for author_id, p_type, p_title, p_content, p_img, p_tags in post_seeds:
            post = CommunityPost(
                author_id=author_id,
                post_type=p_type,
                title=p_title,
                content=p_content,
                image_url=p_img,
                tools_tags=p_tags,
            )
            db.add(post)
            posts_added.append(post)
        db.commit()

        for p in posts_added:
            db.refresh(p)
            # Add sample likes
            db.add(PostLike(post_id=p.id, user_id=brand_user.id))
            db.add(PostLike(post_id=p.id, user_id=creator_user.id))
            # Add comments
            db.add(PostComment(
                post_id=p.id,
                user_id=brand_user.id,
                content="The level of detail and aesthetic coherence here is sublime.",
            ))
            db.add(PostComment(
                post_id=p.id,
                user_id=creator_user.id,
                content="Incredible motion flow! Would love to compare workflows on this.",
            ))
        db.commit()

        # 9. Leaderboard Entries
        leaderboard_data = [
            (creator_entities[0].id, "creator_of_week", 99.8),
            (creator_entities[1].id, "creator_of_week", 98.6),
            (creator_entities[6].id, "creator_of_week", 97.9),
            (creator_entities[0].id, "most_trusted", 100.0),
            (creator_entities[5].id, "most_trusted", 99.4),
            (creator_entities[3].id, "most_trusted", 99.1),
            (creator_entities[0].id, "best_ai_video", 99.9),
            (creator_entities[2].id, "best_ai_video", 98.7),
            (creator_entities[9].id, "best_ai_video", 97.5),
            (creator_entities[5].id, "most_helpful", 98.9),
            (creator_entities[8].id, "most_helpful", 96.5),
            (creator_entities[12].id, "rising", 99.2),
            (creator_entities[7].id, "rising", 98.1),
            (creator_entities[11].id, "rising", 96.8),
        ]

        for cid, cat, score in leaderboard_data:
            db.add(LeaderboardEntry(
                creator_id=cid,
                category=cat,
                score=score,
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow() + timedelta(days=7),
            ))
        db.commit()

        # Follow relationships
        db.add(Follow(follower_id=brand_user.id, following_id=creator_user.id))
        db.add(Follow(follower_id=creator_user.id, following_id=brand_user.id))
        db.add(Follow(follower_id=brand_user.id, following_id=creator_entities[1].user_id))
        db.commit()

        logger.info("Database successfully seeded with realistic demo data!")
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    seed_database()
