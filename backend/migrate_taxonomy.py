"""Taxonomy migration script for CODE XERO.
Maps all 102 creator profiles into the clean 9 Core Categories, Sub-specializations, and Style Tags.
"""

import sqlite3
import json

TAXONOMY_RULES = {
    "AI Video": {
        "sub_specializations": ["Cinematic Video", "Commercial Ads", "Short-form & Reels", "VFX & Compositing", "Music Videos", "Documentary Style"],
        "styles": ["Cinematic", "Photorealistic", "Dramatic", "Hyperreal", "Luxury"]
    },
    "AI Images": {
        "sub_specializations": ["Portrait Photography", "Editorial Stills", "Product Imagery", "Concept Art", "Digital Art & Matte Painting", "Photo Retouching"],
        "styles": ["Editorial", "Hyperreal", "Photorealistic", "Surreal", "Minimal"]
    },
    "3D & CGI": {
        "sub_specializations": ["Product Rendering", "Architectural Visualization", "Character Modeling", "Spatial & Motion CGI", "Hard Surface & Industrial"],
        "styles": ["Hyperreal", "Futuristic", "Clean Commercial", "Photorealistic", "Surreal"]
    },
    "Product Advertising": {
        "sub_specializations": ["Commercial Campaigns", "E-commerce Creatives", "Luxury Product Ads", "Packaging & Brand Ads", "FMCG & Beauty Ads"],
        "styles": ["Clean Commercial", "Luxury", "Bold", "Minimal", "Photorealistic"]
    },
    "Fashion": {
        "sub_specializations": ["Editorial Fashion", "Haute Couture & Runway", "Lookbook Campaigns", "Bridal & Indian Couture", "Virtual Models & Styling", "Textile & Pattern AI"],
        "styles": ["High Fashion", "Luxury", "Editorial", "Warm", "Surreal"]
    },
    "Social Media": {
        "sub_specializations": ["Instagram Creatives & Grids", "Reels & Short Video", "TikTok & Viral Clips", "Content Strategy & Posts", "Meme & Community Marketing"],
        "styles": ["Bold", "Playful", "Clean Commercial", "Vibrant", "Minimal"]
    },
    "Animation & Motion": {
        "sub_specializations": ["Motion Graphics", "2D Animation", "3D Animation", "Explainer Videos", "Anime & Illustration", "Logo Animation & Typography"],
        "styles": ["Kinetic", "Playful", "Bold", "Futuristic", "Minimal"]
    },
    "Branding & Design": {
        "sub_specializations": ["Brand Identity & Logos", "Packaging Design", "Custom Typography", "Print & Editorial Design", "UI/UX & App Graphics", "Infographics & Data Viz"],
        "styles": ["Minimal", "Bold", "Clean Commercial", "Luxury", "Futuristic"]
    },
    "Audio & Voice": {
        "sub_specializations": ["AI Voice & Voice-over", "Sonic Branding & Jingles", "Film & Game Sound Design", "Podcast Production", "Soundtrack & Instrumental Music"],
        "styles": ["Cinematic", "Minimal", "Futuristic", "Warm", "Bold"]
    }
}

def determine_creator_taxonomy(cid, name, spec, skills):
    s = spec.lower()
    sk = [item.lower() for item in skills]
    sk_text = " ".join(sk)
    
    # 1. Determine Core Category by ID range and spec keywords
    if cid in range(1, 17):
        core = "AI Video"
    elif cid in range(17, 32) or cid in (101, 102):
        core = "AI Images"
    elif cid in range(32, 42) or cid in (93, 94):
        core = "3D & CGI"
    elif cid in range(42, 52):
        core = "Product Advertising"
    elif cid in range(52, 60) or cid in (95, 96):
        core = "Fashion"
    elif cid in range(60, 68) or cid in (97, 98):
        core = "Social Media"
    elif cid in range(68, 76) or cid == 99:
        core = "Animation & Motion"
    elif cid in range(76, 84) or cid == 100:
        core = "Branding & Design"
    elif cid in range(84, 93):
        core = "Audio & Voice"
    else:
        # Fallback by content
        if "video" in s or "cinematic" in s or "film" in s: core = "AI Video"
        elif "image" in s or "photo" in s: core = "AI Images"
        elif "3d" in s or "cgi" in s: core = "3D & CGI"
        elif "fashion" in s: core = "Fashion"
        elif "social" in s or "reels" in s: core = "Social Media"
        elif "audio" in s or "voice" in s: core = "Audio & Voice"
        elif "animation" in s: core = "Animation & Motion"
        elif "graphic" in s or "design" in s: core = "Branding & Design"
        else: core = "Product Advertising"

    # 2. Extract Sub-specializations based on core category and skills/spec
    sub_specs = []
    if core == "AI Video":
        if "automotive" in s or "car" in s: sub_specs.append("Commercial Ads")
        if "fashion film" in s or "fashion" in s: sub_specs.append("Cinematic Video")
        if "vfx" in s or "visual effects" in sk_text: sub_specs.append("VFX & Compositing")
        if "reels" in s or "short" in s or "shorts" in s: sub_specs.append("Short-form & Reels")
        if "commercial" in s or "ad" in s or "brand" in s: sub_specs.append("Commercial Ads")
        if "music" in s: sub_specs.append("Music Videos")
        if "documentary" in s or "explainer" in s or "educational" in s: sub_specs.append("Documentary Style")
        if "cinematic" in s or not sub_specs: sub_specs.append("Cinematic Video")

    elif core == "AI Images":
        if "portrait" in sk_text or "headshot" in sk_text or "photo retouching" in s: sub_specs.append("Portrait Photography")
        if "editorial" in s or "editorial" in sk_text: sub_specs.append("Editorial Stills")
        if "product" in s or "product" in sk_text or "still life" in sk_text or "commercial" in s: sub_specs.append("Product Imagery")
        if "concept" in s or "concept" in sk_text or "illustration" in s: sub_specs.append("Concept Art")
        if "digital art" in s or "manipulation" in s or "surreal" in sk_text or "print" in s: sub_specs.append("Digital Art & Matte Painting")
        if "retouching" in s or "enhancement" in s or "editing" in s or not sub_specs: sub_specs.append("Photo Retouching")

    elif core == "3D & CGI":
        if "architectural" in s or "interior" in sk_text or "spatial" in s: sub_specs.append("Architectural Visualization")
        if "character" in s or "game" in s: sub_specs.append("Character Modeling")
        if "motion" in s or "animation" in s or "storytelling" in s: sub_specs.append("Spatial & Motion CGI")
        if "product" in s or "jewelry" in s: sub_specs.append("Product Rendering")
        if not sub_specs: sub_specs.append("Product Rendering")

    elif core == "Product Advertising":
        if "ecommerce" in s or "amazon" in sk_text or "listings" in sk_text: sub_specs.append("E-commerce Creatives")
        if "luxury" in s or "brand" in s or "360" in s: sub_specs.append("Commercial Campaigns")
        if "beauty" in s or "skincare" in sk_text or "personal care" in s: sub_specs.append("FMCG & Beauty Ads")
        if "packaging" in sk_text or "identity" in sk_text: sub_specs.append("Packaging & Brand Ads")
        if not sub_specs: sub_specs.append("Commercial Campaigns")

    elif core == "Fashion":
        if "editorial" in s or "street style" in s: sub_specs.append("Editorial Fashion")
        if "haute couture" in s or "runway" in sk_text: sub_specs.append("Haute Couture & Runway")
        if "bridal" in s or "indian" in s or "ethnic" in s: sub_specs.append("Bridal & Indian Couture")
        if "virtual" in s or "ai fashion" in s or "styling" in s: sub_specs.append("Virtual Models & Styling")
        if "textile" in s or "fabric" in s: sub_specs.append("Textile & Pattern AI")
        if "lookbook" in s or not sub_specs: sub_specs.append("Lookbook Campaigns")

    elif core == "Social Media":
        if "reels" in s or "short" in s: sub_specs.append("Reels & Short Video")
        if "tiktok" in sk_text or "viral" in s or "meme" in s: sub_specs.append("TikTok & Viral Clips")
        if "strategy" in s or "calendar" in sk_text or "community" in s: sub_specs.append("Content Strategy & Posts")
        if "ecommerce" in s or "shopping" in sk_text: sub_specs.append("Instagram Creatives & Grids")
        if not sub_specs: sub_specs.append("Instagram Creatives & Grids")

    elif core == "Animation & Motion":
        if "2d" in s or "character" in sk_text or "cartoon" in sk_text: sub_specs.append("2D Animation")
        if "3d" in s or "cinema 4d" in sk_text: sub_specs.append("3D Animation")
        if "explainer" in s or "corporate" in s: sub_specs.append("Explainer Videos")
        if "anime" in s or "manga" in sk_text: sub_specs.append("Anime & Illustration")
        if "logo" in sk_text or "typography" in s or "brand" in s: sub_specs.append("Logo Animation & Typography")
        if "motion graphics" in s or not sub_specs: sub_specs.append("Motion Graphics")

    elif core == "Branding & Design":
        if "packaging" in s or "label" in sk_text: sub_specs.append("Packaging Design")
        if "typography" in s or "lettering" in sk_text: sub_specs.append("Custom Typography")
        if "print" in s or "brochure" in sk_text: sub_specs.append("Print & Editorial Design")
        if "ui/ux" in s or "web" in sk_text or "app" in sk_text: sub_specs.append("UI/UX & App Graphics")
        if "infographic" in s or "data" in s: sub_specs.append("Infographics & Data Viz")
        if "brand identity" in s or "logo" in sk_text or not sub_specs: sub_specs.append("Brand Identity & Logos")

    elif core == "Audio & Voice":
        if "voice" in s or "dubbing" in sk_text or "narration" in sk_text: sub_specs.append("AI Voice & Voice-over")
        if "sonic" in s or "jingle" in s or "branding" in sk_text: sub_specs.append("Sonic Branding & Jingles")
        if "sound design" in s or "game" in sk_text or "film sound" in sk_text: sub_specs.append("Film & Game Sound Design")
        if "podcast" in s: sub_specs.append("Podcast Production")
        if "music" in s or "instrumental" in s or "soundtrack" in sk_text or not sub_specs: sub_specs.append("Soundtrack & Instrumental Music")

    # Dedup and pick top 2
    sub_specs = list(dict.fromkeys(sub_specs))[:2]

    # 3. Determine Style Tags
    styles = []
    if "cinematic" in s or "film" in s: styles.append("Cinematic")
    if "luxury" in s or "couture" in s: styles.append("Luxury")
    if "photorealistic" in s or "photography" in s or "retouching" in s: styles.append("Photorealistic")
    if "editorial" in s or "magazine" in sk_text: styles.append("Editorial")
    if "3d" in s or "cgi" in s or "unreal" in sk_text: styles.append("Hyperreal")
    if "sci-fi" in s or "futuristic" in sk_text: styles.append("Futuristic")
    if "minimal" in sk_text or "clean" in sk_text or "typography" in s: styles.append("Minimal")
    if "bold" in sk_text or "viral" in s or "anime" in s: styles.append("Bold")
    if "commercial" in s or "product" in s: styles.append("Clean Commercial")
    if "art" in s or "surreal" in sk_text: styles.append("Surreal")
    if "fashion" in s: styles.append("High Fashion")
    if "playful" in sk_text or "meme" in s or "cartoon" in sk_text: styles.append("Playful")

    # Fallback to category defaults if few
    for default_style in TAXONOMY_RULES.get(core, {}).get("styles", ["Cinematic", "Clean Commercial"]):
        if len(styles) < 3 and default_style not in styles:
            styles.append(default_style)

    styles = list(dict.fromkeys(styles))[:3]

    return core, sub_specs, styles


def run_migration():
    conn = sqlite3.connect('backend/maccall.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, display_name, specialization, skills FROM creator_profiles')
    rows = cursor.fetchall()
    
    print(f"Migrating {len(rows)} creators...")
    from collections import Counter
    cat_counter = Counter()

    for cid, name, spec, skills_json in rows:
        skills = json.loads(skills_json) if skills_json else []
        core, sub_specs, styles = determine_creator_taxonomy(cid, name, spec, skills)
        cat_counter[core] += 1
        
        cursor.execute('''
            UPDATE creator_profiles
            SET core_category = ?, sub_specializations = ?, style_tags = ?
            WHERE id = ?
        ''', (core, json.dumps(sub_specs), json.dumps(styles), cid))

    conn.commit()
    conn.close()

    print("\n=== MIGRATION COMPLETE ===")
    for cat, cnt in sorted(cat_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:25}: {cnt} creators")
    print(f"Total migrated: {sum(cat_counter.values())} / {len(rows)}")

if __name__ == '__main__':
    run_migration()
