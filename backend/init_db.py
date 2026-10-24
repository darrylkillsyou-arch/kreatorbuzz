"""Idempotent database initialization script for KreatorBuzz.

Creates all tables defined in SQLAlchemy Base metadata and seeds baseline
marketplace records (users, creators, briefs, community posts, workspaces)
if the database is unpopulated. Never drops tables. Never wipes data.
"""

import sys
import logging
from sqlalchemy import inspect
from app.database import engine, Base, SessionLocal
import app.models  # Register all models with Base metadata
from app.models.users import User
from app.models.creators import CreatorProfile
from app.dependencies import get_password_hash

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_db")


def init_database():
    """Initializes schema and baseline data."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    logger.info("Database tables present (%d): %s", len(existing_tables), ", ".join(sorted(existing_tables)))

    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        logger.info("Current user count: %d", user_count)

        if user_count == 0:
            logger.info("Database is empty. Populating baseline marketplace data...")
            try:
                from app.seed import seed_database
                seed_database(db=db)
                logger.info("Baseline data populated successfully.")
            except Exception as e:
                db.rollback()
                logger.error("Failed to populate baseline data: %s", e)
                raise

        # Ensure demo accounts exist and are active
        demo_accounts = [
            ("recruiter@codexero.com", "Demo Recruiter", "brand", "Demo@123", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"),
            ("creator@codexero.com", "Demo Content Creator", "creator", "Demo@123", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"),
            ("cleanrecruiter@codexero.com", "Clean Recruiter", "brand", "Demo@123", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80"),
            ("cleancreator@codexero.com", "Clean Content Creator", "creator", "Demo@123", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"),
        ]

        for email, name, role, pwd, avatar in demo_accounts:
            existing = db.query(User).filter(User.email == email.lower()).first()
            if not existing:
                u = User(
                    email=email.lower(),
                    password_hash=get_password_hash(pwd),
                    full_name=name,
                    role=role,
                    avatar_url=avatar,
                    bio=f"{role.capitalize()} account on KreatorBuzz.",
                    location="Mumbai / London",
                    is_active=True,
                )
                db.add(u)
                db.commit()
                db.refresh(u)
                logger.info("Created demo user: %s (%s)", email, role)
            else:
                existing.is_active = True
                existing.password_hash = get_password_hash(pwd)
                db.commit()
                u = existing

            if role == "creator":
                prof = db.query(CreatorProfile).filter(CreatorProfile.user_id == u.id).first()
                if not prof:
                    prof = CreatorProfile(
                        user_id=u.id,
                        display_name=u.full_name,
                        tagline="AI Visual Artist & Cinema Director",
                        specialization="Cinematic Video & Luxury",
                        skills=["Prompt Engineering", "Visual Direction", "Post-Production"],
                        ai_tools=["Midjourney v6", "Runway Gen-3", "ComfyUI"],
                        starting_rate=500.0,
                        delivery_days=7,
                        commercial_rights=True,
                        availability_status="available",
                        rating=5.0,
                        sla_score=99.0,
                        on_time_percentage=100.0,
                        location=u.location,
                        core_category="AI Video",
                        sub_specializations=["Cinematic Video", "Luxury & Editorial"],
                        style_tags=["Cinematic", "Luxury"],
                    )
                    db.add(prof)
                    db.commit()
                    logger.info("Created creator profile for: %s", email)

        final_users = db.query(User).count()
        final_creators = db.query(CreatorProfile).count()
        logger.info("Initialization complete: %d users, %d creator profiles.", final_users, final_creators)

    finally:
        db.close()


if __name__ == "__main__":
    init_database()
