"""
Phase 2A: Licensing Migration and Backfill Script.

SAFE TO RUN on existing databases:
- Does NOT drop or wipe any tables
- Creates new tables if they don't exist (via create_all)
- Backfills default CreatorLicensing rows for existing creators that don't have one
- Does NOT change existing creator data or behavior

Usage:
  cd backend
  python migrate_licensing.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal, Base
import app.models  # registers all models with Base metadata


def run_migration():
    print("[MIGRATE] Phase 2A Licensing Migration")
    print("[MIGRATE] Creating new tables if they don't exist...")

    # This is safe - create_all only creates tables that don't exist
    Base.metadata.create_all(bind=engine)
    print("[MIGRATE] Tables created/verified successfully.")

    db = SessionLocal()
    try:
        from app.models.creators import CreatorProfile
        from app.models.licensing import CreatorLicensing

        creators = db.query(CreatorProfile).all()
        print(f"[MIGRATE] Found {len(creators)} existing creator profiles.")

        backfilled = 0
        for creator in creators:
            existing_lic = db.query(CreatorLicensing).filter(
                CreatorLicensing.creator_profile_id == creator.id
            ).first()

            if not existing_lic:
                # Infer defaults from existing data
                commercial = getattr(creator, "commercial_rights", True)

                default_lic = CreatorLicensing(
                    creator_profile_id=creator.id,
                    commercial_use=commercial,
                    usage_types=["paid_ads", "organic_social"],  # safe defaults
                    territories=["india"],  # conservative default
                    max_duration_months=12,  # 1 year default
                    platforms=[],  # no assumptions about platforms
                    additional_notes="Auto-backfilled with sensible defaults. Please update.",
                )
                db.add(default_lic)
                backfilled += 1

        if backfilled > 0:
            db.commit()
            print(f"[MIGRATE] Backfilled {backfilled} creator licensing records with sensible defaults.")
        else:
            print("[MIGRATE] All creator profiles already have licensing records.")

        print("[MIGRATE] Migration complete. Existing data untouched.")

    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
