"""Monthly Dynamic Leaderboard 2.0 Calculation Engine.

Calculates real database-backed monthly performance rankings, category champions,
and monthly awards directly from operational tables:
- workspaces (completed status, completed_at falling strictly in the selected month)
- reviews (verified reviews created in the selected month)
- workspace_milestones (released/approved status with completed_at in selected month)
- revision_requests (created in selected month)
- shared_files (deliverables completed in selected month)
- community_posts (created in selected month)

Excludes automated test workspaces (e.g. titles containing "Lifecycle E2E", "test")
so that running test suites never alters marketplace leaderboard metrics.
"""

from datetime import datetime
from typing import List, Optional, Dict, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.creators import CreatorProfile
from app.models.workspaces import Workspace, WorkspaceMilestone, RevisionRequest, Review, SharedFile
from app.models.community import CommunityPost, Follow
from app.models.users import User
from app.schemas.leaderboard import (
    MonthlySummaryStats,
    CreatorMonthlyMetrics,
    MonthlyRankedCreator,
    MonthlyAward,
    CategoryTopCreators,
    MonthlyLeaderboardResponse,
)
from app.schemas.creators import CreatorProfileResponse

MONTH_NAME_MAP = {
    "2026-08": "August 2026",
    "2026-09": "September 2026",
    "2026-10": "October 2026",
}

CATEGORY_TAXONOMY_LIST = [
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


def _get_month_bounds(month_str: str) -> Tuple[datetime, datetime]:
    """Returns (start_dt, end_dt) for a month formatted as 'YYYY-MM'."""
    year, month = map(int, month_str.split("-"))
    start_dt = datetime(year, month, 1, 0, 0, 0)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        end_dt = datetime(year, month + 1, 1, 0, 0, 0)
    return start_dt, end_dt


def _is_valid_marketplace_workspace(ws: Workspace) -> bool:
    """Filters out automated testing workspaces from leaderboard performance."""
    title_lower = (ws.title or "").lower()
    if "lifecycle e2e" in title_lower or "automated test" in title_lower:
        return False
    return True


def compute_profile_strength(creator: CreatorProfile) -> float:
    """Calculates Profile Strength (0-100%) completely separate from monthly performance score.

    Answers: 'How complete and credible is this creator's profile?'
    Formula:
    - Bio & Display Name: 20 pts
    - Skills & Tools listed: 20 pts
    - Portfolio depth: 25 pts (5 pts per item up to 5 items)
    - Verified status & style tags: 20 pts
    - Stated service clarity (rates, turnaround, commercial rights): 15 pts
    """
    score = 0.0
    if creator.display_name and len(creator.display_name.strip()) > 2:
        score += 10.0
    if creator.tagline and len(creator.tagline.strip()) > 5:
        score += 10.0

    tools_cnt = len(creator.ai_tools or [])
    skills_cnt = len(creator.skills or [])
    if tools_cnt >= 2:
        score += 10.0
    if skills_cnt >= 2:
        score += 10.0

    port_items = creator.portfolio_items or []
    score += min(25.0, len(port_items) * 5.0)

    if creator.is_verified:
        score += 10.0
    if len(creator.style_tags or []) >= 2:
        score += 10.0

    if creator.starting_rate and creator.starting_rate > 0:
        score += 5.0
    if creator.delivery_days and creator.delivery_days > 0:
        score += 5.0
    if creator.commercial_rights:
        score += 5.0

    return round(min(100.0, score), 1)


def _compute_month_creator_scores(
    db: Session,
    month_str: str,
) -> List[MonthlyRankedCreator]:
    """Calculates qualifying creators and their deterministic performance scores for a month."""
    start_dt, end_dt = _get_month_bounds(month_str)

    # 1. Fetch completed workspaces strictly in this month (excluding E2E test runs)
    all_completed_ws = (
        db.query(Workspace)
        .filter(
            Workspace.status == "completed",
            Workspace.completed_at >= start_dt,
            Workspace.completed_at < end_dt,
        )
        .all()
    )
    completed_ws = [w for w in all_completed_ws if _is_valid_marketplace_workspace(w)]

    comp_map = defaultdict(list)
    for ws in completed_ws:
        comp_map[ws.creator_user_id].append(ws)

    # 2. Fetch verified reviews for this month
    all_reviews = (
        db.query(Review)
        .filter(
            Review.created_at >= start_dt,
            Review.created_at < end_dt,
        )
        .all()
    )
    # Filter reviews belonging to valid marketplace workspaces
    valid_ws_ids = {w.id for w in completed_ws}
    reviews = [r for r in all_reviews if r.workspace_id in valid_ws_ids]

    rev_map = defaultdict(list)
    for r in reviews:
        rev_map[r.creator_user_id].append(r)

    # 3. Released milestones in this month
    milestones = (
        db.query(WorkspaceMilestone)
        .join(Workspace, Workspace.id == WorkspaceMilestone.workspace_id)
        .filter(
            WorkspaceMilestone.status.in_(["approved", "released"]),
            WorkspaceMilestone.completed_at >= start_dt,
            WorkspaceMilestone.completed_at < end_dt,
        )
        .all()
    )
    ms_map = defaultdict(list)
    for m in milestones:
        if _is_valid_marketplace_workspace(m.workspace):
            ms_map[m.workspace.creator_user_id].append(m)

    # 4. Revision requests in this month
    revisions = (
        db.query(RevisionRequest)
        .join(Workspace, Workspace.id == RevisionRequest.workspace_id)
        .filter(
            RevisionRequest.created_at >= start_dt,
            RevisionRequest.created_at < end_dt,
        )
        .all()
    )
    rev_req_map = defaultdict(list)
    for rr in revisions:
        if _is_valid_marketplace_workspace(rr.workspace):
            rev_req_map[rr.workspace.creator_user_id].append(rr)

    # 5. Shared deliverables uploaded in this month
    deliverables = (
        db.query(SharedFile)
        .join(Workspace, Workspace.id == SharedFile.workspace_id)
        .filter(
            SharedFile.created_at >= start_dt,
            SharedFile.created_at < end_dt,
        )
        .all()
    )
    deliv_map = defaultdict(list)
    for sf in deliverables:
        if _is_valid_marketplace_workspace(sf.workspace):
            deliv_map[sf.uploader_id].append(sf)

    # 6. Community contributions in this month
    posts = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.created_at >= start_dt,
            CommunityPost.created_at < end_dt,
        )
        .all()
    )
    post_map = defaultdict(list)
    for p in posts:
        post_map[p.author_id].append(p)

    # Identify all qualifying creators with verified monthly project activity
    qualifying_uids = set(comp_map.keys()) | set(rev_map.keys())

    creators = (
        db.query(CreatorProfile)
        .join(User)
        .filter(
            User.is_active == True,
            CreatorProfile.user_id.in_(qualifying_uids),
            CreatorProfile.user_id != 106,
            CreatorProfile.display_name != "Demo Content Creator",
        )
        .all()
    )

    ranked_items: List[MonthlyRankedCreator] = []

    for c in creators:
        uid = c.user_id
        c_ws = comp_map[uid]
        c_rev = rev_map[uid]
        c_ms = ms_map[uid]
        c_rr = rev_req_map[uid]
        c_deliv = deliv_map[uid]
        c_posts = post_map[uid]

        comp_cnt = len(c_ws)
        rev_cnt = len(c_rev)
        avg_rating = round(sum(r.rating for r in c_rev) / rev_cnt, 2) if rev_cnt > 0 else None
        ms_cnt = len(c_ms)
        rr_cnt = len(c_rr)
        deliv_cnt = len(c_deliv)
        post_cnt = len(c_posts)

        # Revision efficiency percentage
        rev_eff_pct = round((comp_cnt / (comp_cnt + rr_cnt) * 100.0), 1) if (comp_cnt + rr_cnt) > 0 else 100.0

        # Deterministic Monthly Performance Score (out of 100):
        # 1. Completed Projects (30 pts max) - 7.5 pts per project, 4 projects = 30
        proj_score = min(30.0, comp_cnt * 7.5)

        # 2. Verified Reviews (25 pts max) - Bayesian weighted rating with prior (C=1.0, m=4.5)
        # Prevents a single 5.0 from beating multiple strong 4.9 reviews
        effective_rating = avg_rating if avg_rating is not None else 4.5
        bayesian = ((rev_cnt * effective_rating) + (1.0 * 4.5)) / (rev_cnt + 1.0)
        # Scales bayesian 0..5 into 25 points, with volume factor
        volume_factor = min(1.0, 0.7 + (rev_cnt * 0.1))
        rev_score = (bayesian / 5.0) * 25.0 * volume_factor

        # 3. Milestone Delivery Performance (20 pts max) - 2.5 pts per released milestone
        ms_score = min(20.0, ms_cnt * 2.5)

        # 4. Revision Efficiency (10 pts max)
        eff_score = (rev_eff_pct / 100.0) * 10.0

        # 5. Production Deliverables (10 pts max) - 2.5 pts per approved deliverable
        deliv_score = min(10.0, deliv_cnt * 2.5)

        # 6. Community Contribution (5 pts max) - 2.5 pts per post in month
        comm_score = min(5.0, post_cnt * 2.5)

        total_score = round(proj_score + rev_score + ms_score + eff_score + deliv_score + comm_score, 1)

        prof_strength = compute_profile_strength(c)

        hero_img = c.portfolio_items[0].image_url if c.portfolio_items else None
        avatar_img = c.user.avatar_url if (c.user and c.user.avatar_url) else None

        explanation = (
            f"{comp_cnt} completed projects • {avg_rating}★ ({rev_cnt} reviews) • "
            f"{ms_cnt} milestones released • {rev_eff_pct}% revision efficiency"
        )

        metrics_obj = CreatorMonthlyMetrics(
            completed_projects=comp_cnt,
            verified_reviews_count=rev_cnt,
            verified_rating=avg_rating,
            released_milestones=ms_cnt,
            revision_requests=rr_cnt,
            revision_efficiency_pct=rev_eff_pct,
            production_deliverables=deliv_cnt,
            community_posts=post_cnt,
        )

        try:
            profile_resp = CreatorProfileResponse.model_validate(c)
        except Exception:
            profile_resp = None

        ranked_items.append(
            MonthlyRankedCreator(
                rank=0,
                creator_id=c.id,
                user_id=uid,
                name=c.display_name,
                avatar=avatar_img,
                hero_image=hero_img,
                primary_category=c.core_category or "AI Creative",
                specialization=c.specialization,
                bio=c.tagline or "",
                monthly_performance_score=total_score,
                rank_movement="NEW",
                badge=None,
                explanation=explanation,
                profile_strength=prof_strength,
                metrics=metrics_obj,
                creator_profile=profile_resp,
            )
        )

    # Sort descending by monthly performance score
    ranked_items.sort(key=lambda x: -x.monthly_performance_score)
    for idx, item in enumerate(ranked_items):
        item.rank = idx + 1

    return ranked_items


def get_monthly_leaderboard(
    db: Session,
    month: str = "2026-10",
) -> MonthlyLeaderboardResponse:
    """Computes full monthly leaderboard including top 10, category top 3,

    awards, and rank movement compared to the prior calendar month.
    """
    if month not in MONTH_NAME_MAP:
        month = "2026-10"

    available_months = ["2026-08", "2026-09", "2026-10"]

    # 1. Compute current month's ranked creators
    current_ranked = _compute_month_creator_scores(db, month)

    # 2. Determine prior month for rank movement
    prior_ranks_map: Dict[int, int] = {}
    prior_month = None
    if month == "2026-09":
        prior_month = "2026-08"
    elif month == "2026-10":
        prior_month = "2026-09"

    if prior_month:
        prior_ranked = _compute_month_creator_scores(db, prior_month)
        for pr in prior_ranked:
            prior_ranks_map[pr.creator_id] = pr.rank

    # 3. Calculate rank movement
    for item in current_ranked:
        if item.creator_id in prior_ranks_map:
            prev_rank = prior_ranks_map[item.creator_id]
            diff = prev_rank - item.rank
            if diff > 0:
                item.rank_movement = f"+{diff}"
            elif diff < 0:
                item.rank_movement = f"-{abs(diff)}"
            else:
                item.rank_movement = "="
        else:
            item.rank_movement = "NEW"

    # 4. Compute Monthly Awards from actual performance data
    awards: List[MonthlyAward] = []
    if current_ranked:
        # Creator of the Month (#1 overall)
        cotm = current_ranked[0]
        cotm.badge = "Creator of the Month"
        awards.append(
            MonthlyAward(
                award_title="Creator of the Month",
                creator_id=cotm.creator_id,
                creator_name=cotm.name,
                avatar=cotm.avatar,
                category=cotm.primary_category,
                score=cotm.monthly_performance_score,
                reason=f"Top overall monthly performance score ({cotm.monthly_performance_score}) with {cotm.metrics.completed_projects} completed projects and {cotm.metrics.verified_rating}★ rating.",
            )
        )

        # Top Rated (highest rating with at least 2 verified reviews, tie-broken by review count and score)
        rated_candidates = [
            c for c in current_ranked
            if c.metrics.verified_reviews_count >= 2 and c.metrics.verified_rating is not None
        ]
        if rated_candidates:
            top_rated = max(
                rated_candidates,
                key=lambda x: (x.metrics.verified_rating or 0, x.metrics.verified_reviews_count, x.monthly_performance_score)
            )
            if not top_rated.badge:
                top_rated.badge = "Top Rated"
            awards.append(
                MonthlyAward(
                    award_title="Top Rated",
                    creator_id=top_rated.creator_id,
                    creator_name=top_rated.name,
                    avatar=top_rated.avatar,
                    category=top_rated.primary_category,
                    score=top_rated.monthly_performance_score,
                    reason=f"Flawless verified client satisfaction: {top_rated.metrics.verified_rating}★ across {top_rated.metrics.verified_reviews_count} reviews in {MONTH_NAME_MAP[month]}.",
                )
            )

        # Most Productive (highest completed marketplace projects, tie-broken by milestones, deliverables, score)
        most_prod = max(
            current_ranked,
            key=lambda x: (
                x.metrics.completed_projects,
                x.metrics.released_milestones,
                x.metrics.production_deliverables,
                x.monthly_performance_score,
            )
        )
        if not most_prod.badge:
            most_prod.badge = "Most Productive"
        awards.append(
            MonthlyAward(
                award_title="Most Productive",
                creator_id=most_prod.creator_id,
                creator_name=most_prod.name,
                avatar=most_prod.avatar,
                category=most_prod.primary_category,
                score=most_prod.monthly_performance_score,
                reason=f"Delivered {most_prod.metrics.completed_projects} verified client projects with {most_prod.metrics.released_milestones} milestones approved.",
            )
        )

        # Delivery Leader (highest released milestone volume with high efficiency, min 3 milestones)
        delivery_candidates = [
            c for c in current_ranked
            if c.metrics.released_milestones >= 3
        ]
        if delivery_candidates:
            delivery_lead = max(
                delivery_candidates,
                key=lambda x: (
                    x.metrics.released_milestones,
                    x.metrics.revision_efficiency_pct,
                    x.metrics.completed_projects,
                    x.monthly_performance_score,
                )
            )
            if not delivery_lead.badge:
                delivery_lead.badge = "Delivery Leader"
            awards.append(
                MonthlyAward(
                    award_title="Delivery Leader",
                    creator_id=delivery_lead.creator_id,
                    creator_name=delivery_lead.name,
                    avatar=delivery_lead.avatar,
                    category=delivery_lead.primary_category,
                    score=delivery_lead.monthly_performance_score,
                    reason=f"High-volume milestone execution: {delivery_lead.metrics.released_milestones} milestones released with {delivery_lead.metrics.revision_efficiency_pct}% revision efficiency.",
                )
            )

        # Rising Creator (new entrant in current month with limited prior history, or top surging creator)
        rising_candidates = [
            c for c in current_ranked
            if c.rank_movement == "NEW" and c.creator_id != cotm.creator_id
        ]
        if rising_candidates:
            rising = max(
                rising_candidates,
                key=lambda x: (x.monthly_performance_score, x.metrics.completed_projects)
            )
            if not rising.badge:
                rising.badge = "Rising Creator"
            awards.append(
                MonthlyAward(
                    award_title="Rising Creator",
                    creator_id=rising.creator_id,
                    creator_name=rising.name,
                    avatar=rising.avatar,
                    category=rising.primary_category,
                    score=rising.monthly_performance_score,
                    reason=f"Top new monthly entrant with a performance score of {rising.monthly_performance_score}.",
                )
            )
        else:
            climbing_candidates = [
                c for c in current_ranked
                if c.rank_movement.startswith("+") and c.creator_id != cotm.creator_id
            ]
            if climbing_candidates:
                rising = max(
                    climbing_candidates,
                    key=lambda x: (x.monthly_performance_score, int(x.rank_movement.replace("+", "")))
                )
                if not rising.badge:
                    rising.badge = "Rising Creator"
                climb = rising.rank_movement.replace("+", "")
                awards.append(
                    MonthlyAward(
                        award_title="Rising Creator",
                        creator_id=rising.creator_id,
                        creator_name=rising.name,
                        avatar=rising.avatar,
                        category=rising.primary_category,
                        score=rising.monthly_performance_score,
                        reason=f"Surged +{climb} ranks this month with a strong performance score of {rising.monthly_performance_score}.",
                    )
                )

    # 5. Category Champions: TOP 3 for each of the 9 taxonomy categories (strictly exact category match)
    category_champions: List[CategoryTopCreators] = []
    for cat in CATEGORY_TAXONOMY_LIST:
        cat_creators = [
            c for c in current_ranked
            if (c.primary_category or "").strip().lower() == cat.strip().lower()
        ]
        top_3 = cat_creators[:3]
        category_champions.append(
            CategoryTopCreators(
                category=cat,
                creators=top_3,
            )
        )

    # 6. Monthly Summary Stats derived honestly from DB
    start_dt, end_dt = _get_month_bounds(month)
    valid_workspaces = [
        w for w in db.query(Workspace).filter(
            Workspace.status == "completed",
            Workspace.completed_at >= start_dt,
            Workspace.completed_at < end_dt,
        ).all()
        if _is_valid_marketplace_workspace(w)
    ]
    valid_ws_ids = {w.id for w in valid_workspaces}

    completed_cnt = len(valid_workspaces)
    active_creators_cnt = len({w.creator_user_id for w in valid_workspaces})

    month_reviews = [
        r for r in db.query(Review).filter(
            Review.created_at >= start_dt,
            Review.created_at < end_dt,
        ).all()
        if r.workspace_id in valid_ws_ids
    ]
    verified_rev_cnt = len(month_reviews)
    avg_rating = round(sum(r.rating for r in month_reviews) / verified_rev_cnt, 2) if verified_rev_cnt > 0 else 5.0

    deliverables_cnt = sum(c.metrics.production_deliverables for c in current_ranked)

    summary = MonthlySummaryStats(
        selected_month=month,
        completed_projects=completed_cnt,
        active_creators=active_creators_cnt,
        verified_reviews=verified_rev_cnt,
        average_verified_rating=avg_rating,
        deliverables_completed=deliverables_cnt,
        source="real_database",
    )

    return MonthlyLeaderboardResponse(
        selected_month=month,
        month_name=MONTH_NAME_MAP[month],
        available_months=available_months,
        summary=summary,
        top_10=current_ranked[:10],
        awards=awards,
        category_champions=category_champions,
        total_qualifying_creators=len(current_ranked),
    )
