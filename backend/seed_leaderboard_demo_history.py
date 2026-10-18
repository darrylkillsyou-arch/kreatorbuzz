"""Dedicated Idempotent Seeder for Curated Monthly Marketplace Demo History.

Seeds authentic completed projects, milestones, deliverables, revision requests,
and verified client reviews for:
- August 2026 (approx 15 completed projects)
- September 2026 (approx 18 completed projects)
- October 2026 (approx 22 completed projects)

Across 19 existing creators covering all 9 marketplace taxonomy categories:
- AI Video: Priya Cinematic (UID 6), Aarav Studio (UID 2), Meera Atelier (UID 4)
- 3D & CGI: Elysian 3D Works (UID 34), Tara 3D Render (UID 35)
- AI Images: Aurelia Image Studio (UID 19), Preethi Pixels (UID 20)
- Fashion: Isha Fashion Design (UID 97), Nadine Fashion Lab (UID 54)
- Product Advertising: Vespera Campaign Lab (UID 44), Megha Product Ads (UID 45)
- Social Media: Sana Social Media (UID 62), Akash Social Lab (UID 63)
- Animation & Motion: Valeria Animation Studio (UID 70), Rohan Animation Lab (UID 71)
- Branding & Design: Julian Design Studio (UID 78), Swati Design Lab (UID 79)
- Audio & Voice: Sana AI Sound Lab (UID 86), Rohit Voice Studio (UID 87)

Guarantees:
1. Idempotent: Can be run multiple times safely.
2. Isolated from QA tests: Automated test workspaces contain "Lifecycle E2E" or "test"
   and are cleanly excluded by the leaderboard engine.
3. No fake data destruction: Never runs unconditional table deletions.
"""

from datetime import datetime
from app.database import SessionLocal
from app.models.workspaces import Workspace, WorkspaceMilestone, SharedFile, RevisionRequest, Review
from app.models.creators import CreatorProfile
from app.models.users import User

# Brand / recruiter user IDs commissioning the work:
# UID 1: brand@maccall.demo (Maison Lumina / Monolith)
# UID 104: alexandra@monolith.studio
# UID 105: recruiter@codexero.com
# UID 107: cleanrecruiter@codexero.com

DEMO_DATASET = [
    # ==========================================
    # AUGUST 2026 (15 completed projects)
    # ==========================================
    # Elysian #1 (3 projects, all 5★), Isha #8 (1 project), Priya #4 (2 projects), etc.
    {
        "month": "2026-08",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI)
        "brand_uid": 1,
        "title": "Aura Chronograph 3D Packshot & Caustic Visuals",
        "created_at": datetime(2026, 8, 2, 10, 0),
        "completed_at": datetime(2026, 8, 12, 16, 30),
        "milestones": [
            ("Hard Surface CAD Ingestion & Shader Setup", 25000, datetime(2026, 8, 5, 14, 0)),
            ("Photorealistic Glass Caustics & Macro Detail", 30000, datetime(2026, 8, 9, 11, 0)),
            ("4K Transparent PNGs & Master Turnaround", 25000, datetime(2026, 8, 12, 16, 0)),
        ],
        "deliverables": [("aura_chronograph_turnaround_4k.mp4", "video"), ("caustic_macro_01.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "The CGI quality was impeccable and materials looked stunning. Communication was seamless from start to finish.",
    },
    {
        "month": "2026-08",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI)
        "brand_uid": 104,
        "title": "Cosmetic Glass Dropper Fluid Simulation",
        "created_at": datetime(2026, 8, 10, 11, 0),
        "completed_at": datetime(2026, 8, 20, 15, 0),
        "milestones": [
            ("Viscous Fluid Dynamics & Bottle Geometry", 20000, datetime(2026, 8, 14, 12, 0)),
            ("Subsurface Scattering & Amber Fluid Pass", 25000, datetime(2026, 8, 17, 18, 0)),
            ("Final Retouched Editorial Still Renders", 20000, datetime(2026, 8, 20, 14, 30)),
        ],
        "deliverables": [("dropper_fluid_render_01.png", "image"), ("dropper_motion_pass.mp4", "video")],
        "revisions": 1,
        "revision_desc": "Please slightly reduce the surface tension on the droplet tip in frame 40.",
        "rating": 5,
        "review": "Fast revision turnaround and high visual realism. Outstanding product packshots.",
    },
    {
        "month": "2026-08",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI)
        "brand_uid": 105,
        "title": "Minimalist Architectural Pavilion Visualization",
        "created_at": datetime(2026, 8, 16, 9, 30),
        "completed_at": datetime(2026, 8, 26, 17, 0),
        "milestones": [
            ("Parametric Geometry & Daylight Studies", 30000, datetime(2026, 8, 20, 15, 0)),
            ("Material Texture Realism & Landscape Integration", 30000, datetime(2026, 8, 23, 11, 0)),
            ("Ultra-High Resolution Portfolio Deliverables", 25000, datetime(2026, 8, 26, 16, 0)),
        ],
        "deliverables": [("pavilion_daylight_pass.png", "image"), ("pavilion_night_ambient.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Elysian transformed our architectural sketches into museum-grade visualizations. Highly recommended.",
    },
    {
        "month": "2026-08",
        "creator_uid": 6, # Priya Cinematic (AI Video)
        "brand_uid": 1,
        "title": "Nocturne Luxury Perfume Cinematic Teaser",
        "created_at": datetime(2026, 8, 4, 14, 0),
        "completed_at": datetime(2026, 8, 15, 18, 0),
        "milestones": [
            ("Moodboard & Generative Visual Direction", 25000, datetime(2026, 8, 8, 11, 0)),
            ("Camera Motion Generation in Runway Gen-3", 35000, datetime(2026, 8, 12, 16, 0)),
            ("Master Color Grade & Sound Design Alignment", 25000, datetime(2026, 8, 15, 17, 30)),
        ],
        "deliverables": [("nocturne_teaser_30s.mp4", "video"), ("style_frames_grid.png", "image")],
        "revisions": 1,
        "revision_desc": "Can we make the amber lighting in the second scene slightly warmer?",
        "rating": 5,
        "review": "Priya understood the cinematic direction quickly and the first cut was very strong.",
    },
    {
        "month": "2026-08",
        "creator_uid": 6, # Priya Cinematic (AI Video)
        "brand_uid": 105,
        "title": "High-Speed Automotive Reveal Clip",
        "created_at": datetime(2026, 8, 18, 10, 0),
        "completed_at": datetime(2026, 8, 28, 19, 0),
        "milestones": [
            ("Track Direction & Vehicle Consistency Frames", 30000, datetime(2026, 8, 22, 14, 0)),
            ("Volumetric Fog & Headlight Beam Synthesis", 30000, datetime(2026, 8, 25, 17, 0)),
            ("4K Master Delivery & Vertical Cutdowns", 25000, datetime(2026, 8, 28, 18, 30)),
        ],
        "deliverables": [("automotive_hero_4k.mp4", "video")],
        "revisions": 0,
        "rating": 4,
        "review": "Impressive vehicle reflection fidelity. Pacing was brisk and professional.",
    },
    {
        "month": "2026-08",
        "creator_uid": 2, # Aarav Studio (AI Video)
        "brand_uid": 104,
        "title": "Futuristic Fintech App Interface Launch Reel",
        "created_at": datetime(2026, 8, 3, 11, 0),
        "completed_at": datetime(2026, 8, 14, 15, 0),
        "milestones": [
            ("UI Spatial Kinetic Concepts", 25000, datetime(2026, 8, 7, 12, 0)),
            ("3D Card Float & Holographic Physics", 30000, datetime(2026, 8, 11, 16, 0)),
            ("Full Commercial Cutdown Package", 25000, datetime(2026, 8, 14, 14, 0)),
        ],
        "deliverables": [("fintech_reel_master.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Aarav delivered exactly what was promised on time. Clean modern motion.",
    },
    {
        "month": "2026-08",
        "creator_uid": 2, # Aarav Studio (AI Video)
        "brand_uid": 1,
        "title": "Urban Neo-Tokyo Cinematic Title Sequence",
        "created_at": datetime(2026, 8, 15, 12, 0),
        "completed_at": datetime(2026, 8, 27, 16, 0),
        "milestones": [
            ("Atmospheric Rain & Neon Reflections", 25000, datetime(2026, 8, 20, 11, 0)),
            ("Camera Tracking & Typographic Compositing", 30000, datetime(2026, 8, 24, 15, 0)),
            ("Final 4K ProRes Export", 25000, datetime(2026, 8, 27, 15, 30)),
        ],
        "deliverables": [("neo_tokyo_title_sequence.mp4", "video")],
        "revisions": 1,
        "revision_desc": "Adjust typographic kerning on main title slate.",
        "rating": 5,
        "review": "Excellent volumetric bloom and aesthetic consistency across all frames.",
    },
    {
        "month": "2026-08",
        "creator_uid": 4, # Meera Atelier (AI Video)
        "brand_uid": 105,
        "title": "Maison Spring Haute Couture AI Film",
        "created_at": datetime(2026, 8, 5, 9, 0),
        "completed_at": datetime(2026, 8, 17, 14, 0),
        "milestones": [
            ("LoRA Textile Fabric Draping Exploration", 30000, datetime(2026, 8, 9, 14, 0)),
            ("Virtual Runway Model Motion Synthesis", 35000, datetime(2026, 8, 14, 12, 0)),
            ("Editorial Grade Delivery", 25000, datetime(2026, 8, 17, 13, 30)),
        ],
        "deliverables": [("haute_couture_film.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Meera is unmatched in fashion AI aesthetics. The textile flow looked genuine.",
    },
    {
        "month": "2026-08",
        "creator_uid": 44, # Vespera Campaign Lab (Product Advertising)
        "brand_uid": 104,
        "title": "Botanical D2C Skincare Commercial Stills & Loops",
        "created_at": datetime(2026, 8, 8, 10, 0),
        "completed_at": datetime(2026, 8, 19, 16, 0),
        "milestones": [
            ("Natural Morning Sunlight Concepting", 20000, datetime(2026, 8, 12, 11, 0)),
            ("Ingredient Composition & Water Droplets", 25000, datetime(2026, 8, 16, 14, 0)),
            ("Full Multi-Channel Asset Export", 20000, datetime(2026, 8, 19, 15, 30)),
        ],
        "deliverables": [("skincare_editorial_01.png", "image"), ("skincare_loop.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Fresh dewy aesthetic, completely aligned with our clean beauty brand guidelines.",
    },
    {
        "month": "2026-08",
        "creator_uid": 19, # Aurelia Image Studio (AI Images)
        "brand_uid": 1,
        "title": "Nordic Architectural Living Concept Series",
        "created_at": datetime(2026, 8, 11, 14, 0),
        "completed_at": datetime(2026, 8, 22, 17, 0),
        "milestones": [
            ("Minimalist Scandinavian Interior Framing", 15000, datetime(2026, 8, 15, 12, 0)),
            ("Natural Wood Texture & Caustic Lighting Pass", 20000, datetime(2026, 8, 19, 16, 0)),
            ("Final High-DPI Print Ready Images", 15000, datetime(2026, 8, 22, 16, 30)),
        ],
        "deliverables": [("nordic_interior_01.png", "image"), ("nordic_interior_02.png", "image")],
        "revisions": 0,
        "rating": 4,
        "review": "Clean Scandinavian lighting and composition. Very cooperative during revisions.",
    },
    {
        "month": "2026-08",
        "creator_uid": 97, # Isha Fashion Design (Fashion)
        "brand_uid": 107,
        "title": "Bridal Couture Generative Lookbook Pass",
        "created_at": datetime(2026, 8, 14, 10, 0),
        "completed_at": datetime(2026, 8, 25, 18, 0),
        "milestones": [
            ("Intricate Zari Embroidery Style Reference", 20000, datetime(2026, 8, 18, 11, 0)),
            ("Regal Portrait Composition & Jewelry Accents", 25000, datetime(2026, 8, 22, 15, 0)),
            ("Lookbook PDF & 4K PNG Master Deliverables", 20000, datetime(2026, 8, 25, 17, 30)),
        ],
        "deliverables": [("bridal_couture_editorial.png", "image")],
        "revisions": 1,
        "revision_desc": "Fine-tune fabric contrast on the red dupatta fold.",
        "rating": 4,
        "review": "Intricate embroidery details were very realistic. Good communication throughout.",
    },
    {
        "month": "2026-08",
        "creator_uid": 62, # Sana Social Media (Social Media)
        "brand_uid": 105,
        "title": "D2C Protein Brand Viral Reels Package",
        "created_at": datetime(2026, 8, 6, 12, 0),
        "completed_at": datetime(2026, 8, 16, 15, 0),
        "milestones": [
            ("Hook Exploration & Motion Pacing", 15000, datetime(2026, 8, 10, 14, 0)),
            ("Visual Sound Design & Kinetic Captions", 20000, datetime(2026, 8, 13, 16, 0)),
            ("Final 5x 9:16 Social Video Formats", 15000, datetime(2026, 8, 16, 14, 30)),
        ],
        "deliverables": [("social_reels_pack.zip", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "High engagement hooks and prompt delivery. Perfect for our Instagram launch.",
    },
    {
        "month": "2026-08",
        "creator_uid": 70, # Valeria Animation Studio (Animation & Motion)
        "brand_uid": 1,
        "title": "Abstract Brand Ident 3D Kinetic Typography",
        "created_at": datetime(2026, 8, 9, 10, 0),
        "completed_at": datetime(2026, 8, 21, 16, 0),
        "milestones": [
            ("Kinetic Glyph Deformation Rigging", 20000, datetime(2026, 8, 14, 12, 0)),
            ("Sound Synchronization & Spring Physics", 25000, datetime(2026, 8, 18, 15, 0)),
            ("Lossless ProRes Alpha Channel Export", 20000, datetime(2026, 8, 21, 15, 30)),
        ],
        "deliverables": [("brand_ident_typography.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Valeria's animation curves and kinetic rhythm gave our brand ident real energy.",
    },
    {
        "month": "2026-08",
        "creator_uid": 78, # Julian Design Studio (Branding & Design)
        "brand_uid": 104,
        "title": "Luxury Hotel Brand Identity System",
        "created_at": datetime(2026, 8, 7, 11, 0),
        "completed_at": datetime(2026, 8, 18, 17, 0),
        "milestones": [
            ("Custom Serif Typography & Crest Direction", 25000, datetime(2026, 8, 11, 14, 0)),
            ("Stationery Mockups & Generative Marble Textures", 30000, datetime(2026, 8, 15, 16, 0)),
            ("Complete Brand Guidelines Manual (PDF)", 25000, datetime(2026, 8, 18, 16, 30)),
        ],
        "deliverables": [("brand_guidelines_manual.pdf", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Julian crafted a timeless luxury mark. Excellent presentation materials.",
    },
    {
        "month": "2026-08",
        "creator_uid": 86, # Sana AI Sound Lab (Audio & Voice)
        "brand_uid": 1,
        "title": "Sonic Logo & Spatial Audio Branding Suite",
        "created_at": datetime(2026, 8, 12, 14, 0),
        "completed_at": datetime(2026, 8, 23, 16, 0),
        "milestones": [
            ("Frequency Exploration & Harmonic Palettes", 15000, datetime(2026, 8, 16, 12, 0)),
            ("Binaural Mnemonic Synthesis", 20000, datetime(2026, 8, 20, 15, 0)),
            ("Multi-Stem Audio Delivery Package", 15000, datetime(2026, 8, 23, 15, 30)),
        ],
        "deliverables": [("sonic_branding_stems.zip", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Sana delivered an evocative 3-second mnemonic that resonated with our stakeholders immediately.",
    },

    # ==========================================
    # SEPTEMBER 2026 (18 completed projects)
    # ==========================================
    # Elysian holds strong, Isha surges to #2, Priya steady at #3, Aarav & Meera active
    {
        "month": "2026-09",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI)
        "brand_uid": 1,
        "title": "Cybernetic Sneaker Modular 3D CGI Commercial",
        "created_at": datetime(2026, 9, 1, 10, 0),
        "completed_at": datetime(2026, 9, 11, 16, 0),
        "milestones": [
            ("Lacing Mesh & Midsole Displacement Mapping", 30000, datetime(2026, 9, 5, 12, 0)),
            ("Exploded Isometric View & Holographic Lighting", 35000, datetime(2026, 9, 8, 15, 0)),
            ("Master 60fps 4K Product Turnaround Delivery", 30000, datetime(2026, 9, 11, 15, 30)),
        ],
        "deliverables": [("sneaker_cgi_turnaround.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Elysian continues to deliver top-tier 3D CGI work. Clean, photorealistic textures.",
    },
    {
        "month": "2026-09",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI)
        "brand_uid": 104,
        "title": "Luxury Champagne Flute Caustic Packshot",
        "created_at": datetime(2026, 9, 10, 11, 0),
        "completed_at": datetime(2026, 9, 21, 17, 0),
        "milestones": [
            ("Glass Refraction & Sparkling Liquid Micro-Bubbles", 25000, datetime(2026, 9, 14, 14, 0)),
            ("Gold Foil Emboss & Label Lighting Studies", 25000, datetime(2026, 9, 18, 16, 0)),
            ("Final High-DPI Packshot Assets", 20000, datetime(2026, 9, 21, 16, 30)),
        ],
        "deliverables": [("champagne_packshot_render.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "The glass caustics were photorealistic down to the label texture reflections.",
    },
    {
        "month": "2026-09",
        "creator_uid": 97, # Isha Fashion Design (Fashion) - SURGE TO #2
        "brand_uid": 1,
        "title": "Milan Fashion Week Virtual Model Lookbook",
        "created_at": datetime(2026, 9, 2, 9, 0),
        "completed_at": datetime(2026, 9, 12, 15, 0),
        "milestones": [
            ("Haute Couture Silhouette Generation", 25000, datetime(2026, 9, 6, 11, 0)),
            ("Editorial Lighting & Studio Runway Backdrop", 30000, datetime(2026, 9, 9, 15, 0)),
            ("Complete 12-Look Digital Lookbook", 25000, datetime(2026, 9, 12, 14, 30)),
        ],
        "deliverables": [("milan_lookbook_master.pdf", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Isha's runway models had consistent facial features and exquisite drape aesthetics.",
    },
    {
        "month": "2026-09",
        "creator_uid": 97, # Isha Fashion Design (Fashion)
        "brand_uid": 105,
        "title": "Silk Saree Generative Print Architecture",
        "created_at": datetime(2026, 9, 11, 10, 0),
        "completed_at": datetime(2026, 9, 20, 16, 0),
        "milestones": [
            ("Floral Motif Mathematical LoRA Training", 20000, datetime(2026, 9, 14, 12, 0)),
            ("Border Gold Zari Weave Simulation", 25000, datetime(2026, 9, 17, 16, 0)),
            ("High-Res Print Production Files", 20000, datetime(2026, 9, 20, 15, 30)),
        ],
        "deliverables": [("silk_saree_print_ready.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Remarkable attention to Indian traditional textile details. Delivered ahead of schedule.",
    },
    {
        "month": "2026-09",
        "creator_uid": 97, # Isha Fashion Design (Fashion)
        "brand_uid": 107,
        "title": "Autumn Cashmere Trench Coat Campaign Stills",
        "created_at": datetime(2026, 9, 18, 11, 0),
        "completed_at": datetime(2026, 9, 28, 17, 0),
        "milestones": [
            ("Outdoor Autumnal Fog & Wet Pavement Mood", 20000, datetime(2026, 9, 22, 14, 0)),
            ("Heavy Wool Textile Realistic Texture Pass", 25000, datetime(2026, 9, 25, 16, 0)),
            ("Editorial Deliverables Package", 20000, datetime(2026, 9, 28, 16, 30)),
        ],
        "deliverables": [("cashmere_trench_campaign.png", "image")],
        "revisions": 1,
        "revision_desc": "Please adjust the warmth on the trench coat camel tone.",
        "rating": 5,
        "review": "Isha adapted our color notes immediately and the final assets are stunning.",
    },
    {
        "month": "2026-09",
        "creator_uid": 6, # Priya Cinematic (AI Video) - SOLID #3
        "brand_uid": 1,
        "title": "Cinematic Swiss Alps Hotel Architecture Video",
        "created_at": datetime(2026, 9, 3, 10, 0),
        "completed_at": datetime(2026, 9, 14, 16, 0),
        "milestones": [
            ("Drone Flyover Camera Paths in Gen-3", 30000, datetime(2026, 9, 7, 12, 0)),
            ("Timber Interior Caustic Fireplace Lighting", 35000, datetime(2026, 9, 11, 15, 0)),
            ("Final 4K Master with Spatial Soundtrack", 30000, datetime(2026, 9, 14, 15, 30)),
        ],
        "deliverables": [("swiss_alps_hotel_reveal.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Priya delivered cinematic drone pans that looked completely authentic.",
    },
    {
        "month": "2026-09",
        "creator_uid": 6, # Priya Cinematic (AI Video)
        "brand_uid": 104,
        "title": "Jewelry Macro Diamond Sparkle Motion Vignettes",
        "created_at": datetime(2026, 9, 12, 11, 0),
        "completed_at": datetime(2026, 9, 23, 17, 0),
        "milestones": [
            ("Prismatic Rainbow Light Dispersion Generation", 25000, datetime(2026, 9, 16, 14, 0)),
            ("Slow Pan Motion Synthesis & Defocus Pass", 30000, datetime(2026, 9, 20, 16, 0)),
            ("Social Media 9:16 & 1:1 Delivery Formats", 20000, datetime(2026, 9, 23, 16, 30)),
        ],
        "deliverables": [("diamond_sparkle_vignette.mp4", "video")],
        "revisions": 1,
        "revision_desc": "Slightly reduce sparkle flare intensity on the center cut diamond.",
        "rating": 5,
        "review": "Turnaround on the flare tweak was within 4 hours. World class quality.",
    },
    {
        "month": "2026-09",
        "creator_uid": 2, # Aarav Studio (AI Video)
        "brand_uid": 105,
        "title": "Electric Hypercar Desert Sunset Commercial",
        "created_at": datetime(2026, 9, 5, 10, 0),
        "completed_at": datetime(2026, 9, 16, 15, 0),
        "milestones": [
            ("Desert Dune Motion Blur & Golden Hour Light", 35000, datetime(2026, 9, 9, 12, 0)),
            ("Dynamic Car Body Reflections & Lens Flares", 35000, datetime(2026, 9, 13, 16, 0)),
            ("Master Commercial Export with Sound Stems", 30000, datetime(2026, 9, 16, 14, 30)),
        ],
        "deliverables": [("desert_hypercar_commercial.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Aarav proves time and time again why he is a benchmark in automotive AI video.",
    },
    {
        "month": "2026-09",
        "creator_uid": 4, # Meera Atelier (AI Video)
        "brand_uid": 1,
        "title": "Minimalist Paris Fashion Week Micro-Reels",
        "created_at": datetime(2026, 9, 8, 9, 0),
        "completed_at": datetime(2026, 9, 19, 16, 0),
        "milestones": [
            ("Atmospheric Parisian Street Backdrops", 25000, datetime(2026, 9, 12, 14, 0)),
            ("Model Walk Cycle Slow-Motion Generation", 30000, datetime(2026, 9, 16, 16, 0)),
            ("Vertical Reel Formats with Typography", 25000, datetime(2026, 9, 19, 15, 30)),
        ],
        "deliverables": [("paris_micro_reels_pack.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Meera's eye for color balance and couture pacing is phenomenal.",
    },
    {
        "month": "2026-09",
        "creator_uid": 44, # Vespera Campaign Lab (Product Advertising)
        "brand_uid": 104,
        "title": "Organic Coffee Packaging Commercial Renders",
        "created_at": datetime(2026, 9, 6, 10, 0),
        "completed_at": datetime(2026, 9, 17, 15, 0),
        "milestones": [
            ("Matte Kraft Paper & Foil Texture Studies", 20000, datetime(2026, 9, 10, 12, 0)),
            ("Roast Coffee Bean Macro Scatter Composition", 25000, datetime(2026, 9, 14, 15, 0)),
            ("Full E-Commerce Packshot Package", 20000, datetime(2026, 9, 17, 14, 30)),
        ],
        "deliverables": [("coffee_packshot_hero.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Vespera delivered clean, commercial-ready product images for our retail launch.",
    },
    {
        "month": "2026-09",
        "creator_uid": 45, # Megha Product Ads (Product Advertising)
        "brand_uid": 105,
        "title": "Smart Fitness Watch Lifestyle Ad Series",
        "created_at": datetime(2026, 9, 9, 11, 0),
        "completed_at": datetime(2026, 9, 20, 16, 0),
        "milestones": [
            ("Active Gym Environment Visual Direction", 20000, datetime(2026, 9, 13, 14, 0)),
            ("OLED Screen Graphic Glow & Wrist Macro", 25000, datetime(2026, 9, 17, 16, 0)),
            ("Multi-Platform Ad Creative Banners", 20000, datetime(2026, 9, 20, 15, 30)),
        ],
        "deliverables": [("fitness_watch_ad_set.png", "image")],
        "revisions": 1,
        "revision_desc": "Make the heart rate widget display on the watch face brighter.",
        "rating": 4,
        "review": "Solid advertising deliverables with crisp UI highlights.",
    },
    {
        "month": "2026-09",
        "creator_uid": 19, # Aurelia Image Studio (AI Images)
        "brand_uid": 1,
        "title": "High-Jewelry Editorial Campaign Series",
        "created_at": datetime(2026, 9, 4, 10, 0),
        "completed_at": datetime(2026, 9, 15, 16, 0),
        "milestones": [
            ("Velvet Backdrop & Warm Rimlight Framing", 20000, datetime(2026, 9, 8, 12, 0)),
            ("Gemstone Clarity & Metal Surface Retouching", 25000, datetime(2026, 9, 12, 15, 0)),
            ("Magazine Spread Ready Export Formats", 20000, datetime(2026, 9, 15, 15, 30)),
        ],
        "deliverables": [("high_jewelry_still_01.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Aurelia's lighting precision on diamond facets is extraordinary.",
    },
    {
        "month": "2026-09",
        "creator_uid": 20, # Preethi Pixels (AI Images)
        "brand_uid": 107,
        "title": "Bioluminescent Flora Concept Art Stills",
        "created_at": datetime(2026, 9, 13, 11, 0),
        "completed_at": datetime(2026, 9, 24, 17, 0),
        "milestones": [
            ("Surreal Botanical Macro Compositions", 15000, datetime(2026, 9, 17, 14, 0)),
            ("Neon Spore Volumetric Fog Synthesis", 20000, datetime(2026, 9, 21, 16, 0)),
            ("Final Ultra-Res Wall Art Exports", 15000, datetime(2026, 9, 24, 16, 30)),
        ],
        "deliverables": [("bioluminescent_flora_01.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Preethi has a wonderful imaginative eye for color palettes.",
    },
    {
        "month": "2026-09",
        "creator_uid": 35, # Tara 3D Render (3D & CGI)
        "brand_uid": 104,
        "title": "Solar Powered EV Charging Station Visualization",
        "created_at": datetime(2026, 9, 7, 10, 0),
        "completed_at": datetime(2026, 9, 18, 15, 0),
        "milestones": [
            ("Station Architecture & Canopy CAD Model", 25000, datetime(2026, 9, 11, 12, 0)),
            ("Dusk Environment & LED Strip Illumination", 30000, datetime(2026, 9, 15, 15, 0)),
            ("Pitch Deck Renderings Package", 20000, datetime(2026, 9, 18, 14, 30)),
        ],
        "deliverables": [("ev_station_dusk_render.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Tara delivered clean architectural perspectives on schedule.",
    },
    {
        "month": "2026-09",
        "creator_uid": 62, # Sana Social Media (Social Media)
        "brand_uid": 105,
        "title": "Fintech App Feature Reels Carousel",
        "created_at": datetime(2026, 9, 10, 12, 0),
        "completed_at": datetime(2026, 9, 21, 16, 0),
        "milestones": [
            ("Story Hook & On-Screen Typography", 15000, datetime(2026, 9, 14, 14, 0)),
            ("Short Clip Video Generation & SFX", 20000, datetime(2026, 9, 18, 16, 0)),
            ("Final Social Formats Delivery", 15000, datetime(2026, 9, 21, 15, 30)),
        ],
        "deliverables": [("fintech_reels_pack.zip", "document")],
        "revisions": 1,
        "revision_desc": "Speed up the intro hook by 0.5s.",
        "rating": 5,
        "review": "Fast social media editor with modern design instincts.",
    },
    {
        "month": "2026-09",
        "creator_uid": 70, # Valeria Animation Studio (Animation & Motion)
        "brand_uid": 1,
        "title": "Streaming Series 2D Cyberpunk Opening Titles",
        "created_at": datetime(2026, 9, 4, 11, 0),
        "completed_at": datetime(2026, 9, 16, 17, 0),
        "milestones": [
            ("Character Silhouettes & Neon Trace Animation", 25000, datetime(2026, 9, 8, 12, 0)),
            ("Parallax City Backgrounds & Glitch FX", 30000, datetime(2026, 9, 12, 16, 0)),
            ("ProRes 4444 Master Sequence Delivery", 25000, datetime(2026, 9, 16, 16, 30)),
        ],
        "deliverables": [("cyberpunk_opening_titles.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Stellar 2D animation timing and stylized visual polish.",
    },
    {
        "month": "2026-09",
        "creator_uid": 78, # Julian Design Studio (Branding & Design)
        "brand_uid": 104,
        "title": "EV Automotive Sub-Brand Visual Identity",
        "created_at": datetime(2026, 9, 6, 10, 0),
        "completed_at": datetime(2026, 9, 18, 16, 0),
        "milestones": [
            ("Aerodynamic Emblem & Wordmark Explorations", 30000, datetime(2026, 9, 10, 12, 0)),
            ("Digital UI System & Vehicle Cluster Typography", 35000, datetime(2026, 9, 14, 16, 0)),
            ("Complete Brand Guidelines Asset Export", 30000, datetime(2026, 9, 18, 15, 30)),
        ],
        "deliverables": [("ev_subbrand_guidelines.pdf", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Julian delivered a cohesive luxury automotive branding suite.",
    },
    {
        "month": "2026-09",
        "creator_uid": 86, # Sana AI Sound Lab (Audio & Voice)
        "brand_uid": 1,
        "title": "Atmospheric Sci-Fi Film Binaural Soundscape",
        "created_at": datetime(2026, 9, 11, 14, 0),
        "completed_at": datetime(2026, 9, 23, 17, 0),
        "milestones": [
            ("Deep Sub-Bass Drones & Organic Shimmer", 20000, datetime(2026, 9, 15, 12, 0)),
            ("Spatial Alien Wildlife Acoustic Design", 25000, datetime(2026, 9, 19, 15, 0)),
            ("Surround 5.1 & Stereo WAV Stem Master", 20000, datetime(2026, 9, 23, 16, 30)),
        ],
        "deliverables": [("scifi_soundscape_master.zip", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Rich spatial depth and immersive harmonic layers.",
    },

    # ==========================================
    # OCTOBER 2026 (22 completed projects)
    # ==========================================
    # Priya Cinematic surges to #1 (4 completed projects, flawless ratings)
    # Isha at #3, Elysian at #5, Aarav at #2, etc.
    {
        "month": "2026-10",
        "creator_uid": 6, # Priya Cinematic (AI Video) - SURGE TO #1
        "brand_uid": 1,
        "title": "L'Or Éthéré Fragrance Global Film Master",
        "created_at": datetime(2026, 10, 1, 9, 0),
        "completed_at": datetime(2026, 10, 8, 16, 0),
        "milestones": [
            ("Golden Caustic Mist & Model Alignment", 30000, datetime(2026, 10, 3, 12, 0)),
            ("Slow Pan Perfume Bottle Refraction In-Motion", 35000, datetime(2026, 10, 6, 15, 0)),
            ("4K Master Delivery with Commercial Stem Music", 30000, datetime(2026, 10, 8, 15, 30)),
        ],
        "deliverables": [("lor_ethere_film_master_4k.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Priya understood our luxury fragrance brief immediately. The film master was sublime.",
    },
    {
        "month": "2026-10",
        "creator_uid": 6, # Priya Cinematic (AI Video)
        "brand_uid": 104,
        "title": "Kinetic Typography & Abstract Spatial Audio Film",
        "created_at": datetime(2026, 10, 3, 10, 0),
        "completed_at": datetime(2026, 10, 10, 15, 0),
        "milestones": [
            ("Spectrogram Reactive Glyphs & Spatial Deform", 25000, datetime(2026, 10, 5, 12, 0)),
            ("ProRes 422 60fps Synthesis with ElevenLabs", 30000, datetime(2026, 10, 8, 16, 0)),
            ("Exhibition-Ready Loop Delivery", 25000, datetime(2026, 10, 10, 14, 30)),
        ],
        "deliverables": [("kinetic_typography_loop.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Priya's generative motion direction was world-class. Prompt fidelity was exceptional.",
    },
    {
        "month": "2026-10",
        "creator_uid": 6, # Priya Cinematic (AI Video)
        "brand_uid": 105,
        "title": "Bioluminescent Deep Sea Documentary Teaser",
        "created_at": datetime(2026, 10, 6, 11, 0),
        "completed_at": datetime(2026, 10, 13, 17, 0),
        "milestones": [
            ("Fluid Dynamics of Jellyfish Bioluminescence", 25000, datetime(2026, 10, 9, 14, 0)),
            ("Volumetric Water Shimmer & Micro-Organisms", 30000, datetime(2026, 10, 11, 16, 0)),
            ("Ultra-HD 4K Cinematic Cutdown Master", 25000, datetime(2026, 10, 13, 16, 30)),
        ],
        "deliverables": [("deep_sea_teaser.mp4", "video")],
        "revisions": 1,
        "revision_desc": "Make the bioluminescent pulses match the beat drop in second 14.",
        "rating": 5,
        "review": "Handled the timing refinement effortlessly. Pacing and color grading were top notch.",
    },
    {
        "month": "2026-10",
        "creator_uid": 6, # Priya Cinematic (AI Video)
        "brand_uid": 107,
        "title": "Monolith FinTech Futuristic Hero Video",
        "created_at": datetime(2026, 10, 8, 14, 0),
        "completed_at": datetime(2026, 10, 15, 18, 0),
        "milestones": [
            ("Glass Cards & Abstract Crypto Spatial Physics", 25000, datetime(2026, 10, 11, 12, 0)),
            ("Sora & Kling Generation with Clean Camera Pan", 30000, datetime(2026, 10, 13, 15, 0)),
            ("Final Social & Broadcast Package Export", 25000, datetime(2026, 10, 15, 17, 30)),
        ],
        "deliverables": [("monolith_fintech_hero.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "A tour-de-force in AI motion consistency. Delivered ahead of deadline.",
    },
    {
        "month": "2026-10",
        "creator_uid": 2, # Aarav Studio (AI Video) - SOLID #2
        "brand_uid": 1,
        "title": "Aethelgard Hypercar Global Video Reveal Master",
        "created_at": datetime(2026, 10, 2, 10, 0),
        "completed_at": datetime(2026, 10, 9, 16, 0),
        "milestones": [
            ("Hypercar Carbon Fiber Shaders in Octane", 35000, datetime(2026, 10, 4, 12, 0)),
            ("Topaz 4K Upscale & DaVinci Color Grading", 35000, datetime(2026, 10, 7, 15, 0)),
            ("Master Commercial Reveal Cut", 30000, datetime(2026, 10, 9, 15, 30)),
        ],
        "deliverables": [("aethelgard_reveal_cut.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Aarav is our studio's go-to AI automotive director. Photorealism at its finest.",
    },
    {
        "month": "2026-10",
        "creator_uid": 2, # Aarav Studio (AI Video)
        "brand_uid": 104,
        "title": "Luxury Chronograph Precision Timepiece Film",
        "created_at": datetime(2026, 10, 5, 11, 0),
        "completed_at": datetime(2026, 10, 12, 17, 0),
        "milestones": [
            ("Watch Movement Escapement Macro Animation", 25000, datetime(2026, 10, 7, 14, 0)),
            ("Sapphire Crystal Reflection Realism", 30000, datetime(2026, 10, 10, 16, 0)),
            ("Commercial Social Cut Package", 25000, datetime(2026, 10, 12, 16, 30)),
        ],
        "deliverables": [("chronograph_macro_film.mp4", "video")],
        "revisions": 1,
        "revision_desc": "Please ease the rotation speed of the tourbillon cage.",
        "rating": 5,
        "review": "Watch details were razor sharp. Great turnaround on the rotation adjustment.",
    },
    {
        "month": "2026-10",
        "creator_uid": 2, # Aarav Studio (AI Video)
        "brand_uid": 105,
        "title": "Architectural AI Video Drone Pass",
        "created_at": datetime(2026, 10, 9, 10, 0),
        "completed_at": datetime(2026, 10, 16, 18, 0),
        "milestones": [
            ("Modern Villa Cantilever Geometry Paths", 25000, datetime(2026, 10, 12, 12, 0)),
            ("Sunlight Caustics through Infinity Pool", 30000, datetime(2026, 10, 14, 15, 0)),
            ("4K Master Delivery", 25000, datetime(2026, 10, 16, 17, 30)),
        ],
        "deliverables": [("villa_cantilever_pass.mp4", "video")],
        "revisions": 0,
        "rating": 4,
        "review": "High quality architectural drone synthesis. Clean transitions.",
    },
    {
        "month": "2026-10",
        "creator_uid": 97, # Isha Fashion Design (Fashion) - SOLID #3
        "brand_uid": 1,
        "title": "Winter Haute Couture Velvet Editorial Series",
        "created_at": datetime(2026, 10, 1, 11, 0),
        "completed_at": datetime(2026, 10, 9, 15, 0),
        "milestones": [
            ("Crushed Velvet Deep Burgundy Fabric LoRA", 25000, datetime(2026, 10, 4, 12, 0)),
            ("Catwalk Lighting & Cold Mist Ambience", 30000, datetime(2026, 10, 7, 16, 0)),
            ("Full Editorial Print Files Delivery", 25000, datetime(2026, 10, 9, 14, 30)),
        ],
        "deliverables": [("burgundy_velvet_editorial.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Isha's velvet textile shaders are astonishingly tactile. Magnificent work.",
    },
    {
        "month": "2026-10",
        "creator_uid": 97, # Isha Fashion Design (Fashion)
        "brand_uid": 104,
        "title": "Jeweled Cape Bridal Editorial Spread",
        "created_at": datetime(2026, 10, 5, 10, 0),
        "completed_at": datetime(2026, 10, 13, 16, 0),
        "milestones": [
            ("Emerald & Pearl Intricate Embroidery Pass", 25000, datetime(2026, 10, 8, 14, 0)),
            ("High-Fashion Runway Posing & Lighting", 30000, datetime(2026, 10, 11, 16, 0)),
            ("Editorial Portfolio Ready Deliverables", 25000, datetime(2026, 10, 13, 15, 30)),
        ],
        "deliverables": [("jeweled_cape_spread.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Every single stitch and emerald accent came out crisp and authentic.",
    },
    {
        "month": "2026-10",
        "creator_uid": 97, # Isha Fashion Design (Fashion)
        "brand_uid": 105,
        "title": "Virtual Avatar Runway Motion Concept",
        "created_at": datetime(2026, 10, 8, 11, 0),
        "completed_at": datetime(2026, 10, 15, 17, 0),
        "milestones": [
            ("Motion Capture Posing in Marvelous Designer", 20000, datetime(2026, 10, 11, 12, 0)),
            ("Silk Fabric Dynamic Physics Simulation", 25000, datetime(2026, 10, 13, 15, 0)),
            ("Social Video Export Delivery", 20000, datetime(2026, 10, 15, 16, 30)),
        ],
        "deliverables": [("virtual_avatar_runway.mp4", "video")],
        "revisions": 1,
        "revision_desc": "Slow down the stride rhythm slightly at the turnaround marker.",
        "rating": 5,
        "review": "Superb collaboration. Adjusted the stride gracefully.",
    },
    {
        "month": "2026-10",
        "creator_uid": 4, # Meera Atelier (AI Video)
        "brand_uid": 104,
        "title": "Paris Creative Lab Autumn Launch Film",
        "created_at": datetime(2026, 10, 4, 10, 0),
        "completed_at": datetime(2026, 10, 11, 16, 0),
        "milestones": [
            ("Golden Hour Parisian River Seine Stills", 25000, datetime(2026, 10, 6, 12, 0)),
            ("Runway Gen-3 Runway Fluid Tracking", 30000, datetime(2026, 10, 9, 15, 0)),
            ("ProRes Master Export Delivery", 25000, datetime(2026, 10, 11, 15, 30)),
        ],
        "deliverables": [("paris_lab_launch_film.mp4", "video")],
        "revisions": 0,
        "rating": 5,
        "review": "Meera's signature warm film look gave our campaign an effortless European luxury mood.",
    },
    {
        "month": "2026-10",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI) - POSITION #5
        "brand_uid": 105,
        "title": "Minimalist High-Gloss Ceramic Packshots",
        "created_at": datetime(2026, 10, 7, 10, 0),
        "completed_at": datetime(2026, 10, 14, 17, 0),
        "milestones": [
            ("Ceramic Glaze Fresnel Reflectivity Pass", 20000, datetime(2026, 10, 9, 14, 0)),
            ("Softbox Lighting & Studio Shadow Gradient", 25000, datetime(2026, 10, 12, 16, 0)),
            ("Master 8K Transparent Render Delivery", 20000, datetime(2026, 10, 14, 16, 30)),
        ],
        "deliverables": [("ceramic_packshot_8k.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "The ceramic glaze reflections were pristine. Clean, minimal studio aesthetics.",
    },
    {
        "month": "2026-10",
        "creator_uid": 34, # Elysian 3D Works (3D & CGI)
        "brand_uid": 1,
        "title": "Architectural Concrete & Glass Spatial Pavilion",
        "created_at": datetime(2026, 10, 9, 11, 0),
        "completed_at": datetime(2026, 10, 16, 18, 0),
        "milestones": [
            ("Volumetric Sunset Sunlight Ray Tracing", 25000, datetime(2026, 10, 12, 12, 0)),
            ("Internal Concrete Texture Bump & Specularity", 25000, datetime(2026, 10, 14, 16, 0)),
            ("Ultra-HD Renders for Brand Keynote", 20000, datetime(2026, 10, 16, 17, 30)),
        ],
        "deliverables": [("concrete_pavilion_render.png", "image")],
        "revisions": 1,
        "revision_desc": "Make the internal recessed LED spotlights slightly softer.",
        "rating": 4,
        "review": "Great architectural mood and quick lighting modification.",
    },
    {
        "month": "2026-10",
        "creator_uid": 35, # Tara 3D Render (3D & CGI)
        "brand_uid": 107,
        "title": "Spatial Computing Vision Pro Environment Concept",
        "created_at": datetime(2026, 10, 6, 9, 0),
        "completed_at": datetime(2026, 10, 14, 16, 0),
        "milestones": [
            ("Equirectangular 360 Skybox Generation", 25000, datetime(2026, 10, 9, 12, 0)),
            ("Depth Map & Floating Spatial Glass Widgets", 30000, datetime(2026, 10, 12, 15, 0)),
            ("XR Ready Assets Delivery", 25000, datetime(2026, 10, 14, 15, 30)),
        ],
        "deliverables": [("spatial_environment_xr.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Tara executed a complex XR spatial backdrop with absolute spatial accuracy.",
    },
    {
        "month": "2026-10",
        "creator_uid": 44, # Vespera Campaign Lab (Product Advertising)
        "brand_uid": 1,
        "title": "Botanical Infusion Serum Multi-Angle Ad Suite",
        "created_at": datetime(2026, 10, 3, 11, 0),
        "completed_at": datetime(2026, 10, 11, 15, 0),
        "milestones": [
            ("Golden Honey & Chamomile Organic Elements", 20000, datetime(2026, 10, 6, 12, 0)),
            ("Hero Packaging Angle with Studio Reflection", 25000, datetime(2026, 10, 9, 16, 0)),
            ("Omni-Channel Social & E-comm Exports", 20000, datetime(2026, 10, 11, 14, 30)),
        ],
        "deliverables": [("botanical_serum_hero.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Vespera created a gorgeous organic visual suite that boosted our CTR immediately.",
    },
    {
        "month": "2026-10",
        "creator_uid": 45, # Megha Product Ads (Product Advertising)
        "brand_uid": 104,
        "title": "Luxury Matte Black Headphones Ad Campaign",
        "created_at": datetime(2026, 10, 7, 10, 0),
        "completed_at": datetime(2026, 10, 15, 16, 0),
        "milestones": [
            ("Micro-Texture Leather & Anodized Metal Pass", 20000, datetime(2026, 10, 10, 12, 0)),
            ("Exploded Driver Soundwave Hologram", 25000, datetime(2026, 10, 13, 15, 0)),
            ("Billboard & Social Format Deliverables", 20000, datetime(2026, 10, 15, 15, 30)),
        ],
        "deliverables": [("black_headphones_ad.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Crisp product renders with flawless edge lighting.",
    },
    {
        "month": "2026-10",
        "creator_uid": 19, # Aurelia Image Studio (AI Images)
        "brand_uid": 105,
        "title": "Surrealist Fine Jewelry Editorial Stills",
        "created_at": datetime(2026, 10, 4, 11, 0),
        "completed_at": datetime(2026, 10, 12, 17, 0),
        "milestones": [
            ("Sculptural Marble Hands & Gemstone Placement", 20000, datetime(2026, 10, 7, 14, 0)),
            ("Caustic Shadow Prisms & Soft Ambient Light", 25000, datetime(2026, 10, 10, 16, 0)),
            ("High-Resolution Retouched Master Delivery", 20000, datetime(2026, 10, 12, 16, 30)),
        ],
        "deliverables": [("surrealist_jewelry_still.png", "image")],
        "revisions": 0,
        "rating": 5,
        "review": "Aurelia has an uncanny ability to generate luxury stills that feel like analog photography.",
    },
    {
        "month": "2026-10",
        "creator_uid": 20, # Preethi Pixels (AI Images)
        "brand_uid": 1,
        "title": "Nordic Architectural Living Room Moodboards",
        "created_at": datetime(2026, 10, 6, 10, 0),
        "completed_at": datetime(2026, 10, 14, 16, 0),
        "milestones": [
            ("Raw Concrete & Light Oak Wood Balancing", 15000, datetime(2026, 10, 9, 12, 0)),
            ("Warm Afternoon Sunbeam Volumetrics", 20000, datetime(2026, 10, 12, 15, 0)),
            ("Client Presentation Print Ready Export", 15000, datetime(2026, 10, 14, 15, 30)),
        ],
        "deliverables": [("nordic_living_render.png", "image")],
        "revisions": 0,
        "rating": 4,
        "review": "Warm, peaceful compositions that perfectly captured the Nordic vibe.",
    },
    {
        "month": "2026-10",
        "creator_uid": 62, # Sana Social Media (Social Media)
        "brand_uid": 104,
        "title": "Beauty Brand Viral TikTok Hooks Series",
        "created_at": datetime(2026, 10, 5, 12, 0),
        "completed_at": datetime(2026, 10, 13, 16, 0),
        "milestones": [
            ("Sound-Synced Rapid Pacing Cuts", 15000, datetime(2026, 10, 8, 14, 0)),
            ("Dynamic Kinetic Caption Styling", 20000, datetime(2026, 10, 11, 16, 0)),
            ("Multi-Channel Social Exports Delivery", 15000, datetime(2026, 10, 13, 15, 30)),
        ],
        "deliverables": [("beauty_tiktok_hooks.zip", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Sana is a master of short-form social engagement. Highly responsive.",
    },
    {
        "month": "2026-10",
        "creator_uid": 70, # Valeria Animation Studio (Animation & Motion)
        "brand_uid": 105,
        "title": "FinTech Mobile App 3D Icon Micro-Animations",
        "created_at": datetime(2026, 10, 7, 10, 0),
        "completed_at": datetime(2026, 10, 15, 17, 0),
        "milestones": [
            ("Physics-Based Coin & Credit Card Motion", 20000, datetime(2026, 10, 10, 12, 0)),
            ("Lottie & JSON Vector Animation Export", 25000, datetime(2026, 10, 13, 16, 0)),
            ("Developer Handover Asset Bundle", 20000, datetime(2026, 10, 15, 16, 30)),
        ],
        "deliverables": [("lottie_icon_bundle.zip", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Silky smooth easing curves and super clean JSON assets.",
    },
    {
        "month": "2026-10",
        "creator_uid": 78, # Julian Design Studio (Branding & Design)
        "brand_uid": 1,
        "title": "Haute Horlogerie Exhibition Visual Identity",
        "created_at": datetime(2026, 10, 8, 11, 0),
        "completed_at": datetime(2026, 10, 16, 16, 0),
        "milestones": [
            ("Custom Geometric Typeface Exploration", 30000, datetime(2026, 10, 11, 14, 0)),
            ("Foil Stamping Print Pre-Press Specifications", 30000, datetime(2026, 10, 14, 16, 0)),
            ("Master Signage & Event Identity System", 25000, datetime(2026, 10, 16, 15, 30)),
        ],
        "deliverables": [("exhibition_identity_suite.pdf", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "Julian crafted an elevated visual system that commanded respect from all our partners.",
    },
    {
        "month": "2026-10",
        "creator_uid": 86, # Sana AI Sound Lab (Audio & Voice)
        "brand_uid": 107,
        "title": "Luxury Electric Yacht Cinematic Score Stem",
        "created_at": datetime(2026, 10, 9, 14, 0),
        "completed_at": datetime(2026, 10, 16, 17, 0),
        "milestones": [
            ("Orchestral Cello & Modern Synthesizer Blend", 20000, datetime(2026, 10, 12, 12, 0)),
            ("Water Hydrophone Spatial Texture Integration", 25000, datetime(2026, 10, 14, 16, 0)),
            ("24-bit 96kHz Lossless Stems Delivery", 20000, datetime(2026, 10, 16, 16, 30)),
        ],
        "deliverables": [("yacht_soundtrack_stems.zip", "document")],
        "revisions": 0,
        "rating": 5,
        "review": "An evocative audio masterpiece. Gave goosebumps to everyone in the preview room.",
    },
]


def seed_leaderboard_demo_history():
    """Idempotently seeds curated demo workspaces, milestones, deliverables, and reviews."""
    db = SessionLocal()
    try:
        created_workspaces = 0
        skipped_workspaces = 0

        for item in DEMO_DATASET:
            # Idempotency check by unique title + completed_at timestamp
            existing = db.query(Workspace).filter(
                Workspace.title == item["title"],
                Workspace.creator_user_id == item["creator_uid"],
            ).first()

            if existing:
                skipped_workspaces += 1
                continue

            # Create workspace
            ws = Workspace(
                creator_user_id=item["creator_uid"],
                brand_user_id=item["brand_uid"],
                title=item["title"],
                status="completed",
                created_at=item["created_at"],
                completed_at=item["completed_at"],
            )
            db.add(ws)
            db.commit()
            db.refresh(ws)

            # Create milestones (approved / released)
            for m_title, m_amt, m_comp in item["milestones"]:
                m = WorkspaceMilestone(
                    workspace_id=ws.id,
                    title=m_title,
                    amount=m_amt,
                    status="released",
                    completed_at=m_comp,
                )
                db.add(m)

            # Create deliverables
            for fname, ftype in item["deliverables"]:
                sf = SharedFile(
                    workspace_id=ws.id,
                    uploader_id=item["creator_uid"],
                    filename=fname,
                    stored_path=f"/demo/deliverables/{fname}",
                    file_type=ftype,
                    version=1,
                    status="approved",
                    created_at=item["completed_at"],
                )
                db.add(sf)

            # Create revisions if any
            if item.get("revisions", 0) > 0:
                rr = RevisionRequest(
                    workspace_id=ws.id,
                    requester_id=item["brand_uid"],
                    description=item.get("revision_desc", "Adjust minor visual accents"),
                    status="resolved",
                    created_at=item["created_at"],
                )
                db.add(rr)

            # Create verified review
            rev = Review(
                workspace_id=ws.id,
                recruiter_user_id=item["brand_uid"],
                creator_user_id=item["creator_uid"],
                rating=item["rating"],
                comment=item["review"],
                created_at=item["completed_at"],
            )
            db.add(rev)

            db.commit()
            created_workspaces += 1

        print(f"Seeding completed. Created: {created_workspaces}, Skipped existing: {skipped_workspaces}")

        # Summary check per month
        for m_str in ["2026-08", "2026-09", "2026-10"]:
            cnt = db.query(Workspace).filter(
                Workspace.status == "completed",
                Workspace.completed_at >= datetime.strptime(f"{m_str}-01", "%Y-%m-%d"),
                Workspace.completed_at <= (datetime(2026, 8, 31, 23, 59) if m_str == "2026-08" else (datetime(2026, 9, 30, 23, 59) if m_str == "2026-09" else datetime(2026, 10, 31, 23, 59)))
            ).count()
            print(f"Total completed workspaces for {m_str}: {cnt}")

    except Exception as e:
        db.rollback()
        print("Error during demo seeding:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_leaderboard_demo_history()
