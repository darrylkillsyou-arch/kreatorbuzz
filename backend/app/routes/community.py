"""Community feed, social engagement, likes, and comments."""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.creators import CreatorProfile
from app.models.community import CommunityPost, PostLike, PostComment, Follow, SavedPost
from app.schemas.community import (
    PostCreate,
    PostResponse,
    CommentCreate,
    CommentResponse,
    LikeResponse,
    FollowResponse,
    FollowerStatsResponse,
)
from app.dependencies import get_current_user, get_optional_current_user

router = APIRouter(prefix="/community", tags=["community"])


def _get_creator_profile_id(user_id: int, db: Session) -> Optional[int]:
    prof = db.query(CreatorProfile.id).filter(CreatorProfile.user_id == user_id).first()
    return prof[0] if prof else None


@router.get("/posts", response_model=List[PostResponse])
def list_posts(
    skip: int = 0,
    limit: int = 50,
    post_type: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Lists community feed posts with engagement statistics and current user status."""
    query = db.query(CommunityPost)
    if post_type and post_type.lower() != "all":
        clean = post_type.lower().strip().replace(" ", "_")
        # Map common synonyms
        if "urgent" in clean:
            query = query.filter(CommunityPost.post_type.ilike("%urgent%"))
        elif "hiring" in clean:
            query = query.filter(
                (CommunityPost.post_type.ilike("%hiring%")) |
                (CommunityPost.post_type.ilike("%open_brief%")) |
                (CommunityPost.post_type.ilike("%brief%"))
            )
        elif "announcement" in clean:
            query = query.filter(CommunityPost.post_type.ilike("%announcement%"))
        elif "creator" in clean or "looking" in clean:
            query = query.filter(
                (CommunityPost.post_type.ilike("%creator%")) |
                (CommunityPost.post_type.ilike("%looking%"))
            )
        elif "service" in clean or "offer" in clean:
            query = query.filter(
                (CommunityPost.post_type.ilike("%service%")) |
                (CommunityPost.post_type.ilike("%offer%"))
            )
        elif "collab" in clean:
            query = query.filter(CommunityPost.post_type.ilike("%collab%"))
        elif "showcase" in clean:
            query = query.filter(
                (CommunityPost.post_type.ilike("%showcase%")) |
                (CommunityPost.post_type.ilike("%achievement%"))
            )
        else:
            query = query.filter(CommunityPost.post_type.ilike(f"%{clean}%"))

    posts = query.order_by(CommunityPost.created_at.desc()).offset(skip).limit(limit).all()

    my_likes = set()
    my_saved = set()
    my_follows = set()
    if current_user:
        user_likes = db.query(PostLike.post_id).filter(PostLike.user_id == current_user.id).all()
        my_likes = {ul[0] for ul in user_likes}
        user_saved = db.query(SavedPost.post_id).filter(SavedPost.user_id == current_user.id).all()
        my_saved = {us[0] for us in user_saved}
        user_follows = db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()
        my_follows = {uf[0] for uf in user_follows}

    # Pre-fetch creator profile IDs for authors
    author_ids = list({p.author_id for p in posts})
    profiles = db.query(CreatorProfile.id, CreatorProfile.user_id).filter(CreatorProfile.user_id.in_(author_ids)).all() if author_ids else []
    creator_profile_map = {prof.user_id: prof.id for prof in profiles}

    results = []
    for p in posts:
        # Load comments with user info
        comments_data = []
        for c in p.comments:
            c_resp = CommentResponse(
                id=c.id,
                post_id=c.post_id,
                user_id=c.user_id,
                content=c.content,
                created_at=c.created_at,
                user=c.user,
            )
            comments_data.append(c_resp)

        resp = PostResponse(
            id=p.id,
            author_id=p.author_id,
            post_type=p.post_type,
            title=p.title,
            content=p.content,
            image_url=p.image_url,
            tools_tags=p.tools_tags or [],
            created_at=p.created_at,
            author=p.author,
            creator_profile_id=creator_profile_map.get(p.author_id),
            likes_count=len(p.likes),
            comments_count=len(p.comments),
            is_liked_by_me=p.id in my_likes,
            is_saved_by_me=p.id in my_saved,
            is_following_author=p.author_id in my_follows,
            comments=comments_data,
        )
        results.append(resp)
    return results


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publishes a new community post."""
    # Prevent accidental rapid duplicate posts (within 10s from same author with same title/content)
    cutoff = datetime.utcnow() - timedelta(seconds=10)
    recent = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.author_id == current_user.id,
            CommunityPost.title == post_in.title,
            CommunityPost.content == post_in.content,
            CommunityPost.created_at >= cutoff,
        )
        .first()
    )
    if recent:
        creator_prof_id = _get_creator_profile_id(current_user.id, db)
        return PostResponse(
            id=recent.id,
            author_id=recent.author_id,
            post_type=recent.post_type,
            title=recent.title,
            content=recent.content,
            image_url=recent.image_url,
            tools_tags=recent.tools_tags or [],
            created_at=recent.created_at,
            author=current_user,
            creator_profile_id=creator_prof_id,
            likes_count=len(recent.likes),
            comments_count=len(recent.comments),
            is_liked_by_me=False,
            is_saved_by_me=False,
            comments=[],
        )

    post = CommunityPost(
        author_id=current_user.id,
        post_type=post_in.post_type.lower().replace(" ", "_"),
        title=post_in.title,
        content=post_in.content,
        image_url=post_in.image_url,
        tools_tags=post_in.tools_tags,
        base_likes=0,
        base_comments=0,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    creator_prof_id = _get_creator_profile_id(current_user.id, db)

    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        post_type=post.post_type,
        title=post.title,
        content=post.content,
        image_url=post.image_url,
        tools_tags=post.tools_tags or [],
        created_at=post.created_at,
        author=current_user,
        creator_profile_id=creator_prof_id,
        likes_count=0,
        comments_count=0,
        is_liked_by_me=False,
        is_saved_by_me=False,
        comments=[],
    )


@router.post("/posts/{post_id}/like", response_model=LikeResponse)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggles like on a post (like/unlike)."""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        liked = False
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(like)
        db.commit()
        liked = True

    total_likes = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    return LikeResponse(post_id=post_id, user_id=current_user.id, liked=liked, likes_count=total_likes)


@router.delete("/posts/{post_id}/like", response_model=LikeResponse)
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unlikes a previously liked post."""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()

    total_likes = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    return LikeResponse(post_id=post_id, user_id=current_user.id, liked=False, likes_count=total_likes)


@router.post("/posts/{post_id}/comment", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def comment_on_post(
    post_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a comment to a community post."""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if not comment_in.content or not comment_in.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content cannot be empty")

    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_in.content.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at,
        user=current_user,
    )


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    """Retrieves all comments for a community post."""
    comments = db.query(PostComment).filter(PostComment.post_id == post_id).order_by(PostComment.created_at.asc()).all()
    return [
        CommentResponse(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            content=c.content,
            created_at=c.created_at,
            user=c.user,
        )
        for c in comments
    ]


@router.post("/follow/{target_user_id}", response_model=FollowResponse)
def toggle_follow_user(
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Follows or unfollows another creator or brand."""
    if current_user.id == target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target_user_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        cnt = db.query(Follow).filter(Follow.following_id == target_user_id).count()
        return FollowResponse(follower_id=current_user.id, following_id=target_user_id, following=False, follower_count=cnt)
    else:
        new_follow = Follow(follower_id=current_user.id, following_id=target_user_id)
        db.add(new_follow)
        db.commit()
        cnt = db.query(Follow).filter(Follow.following_id == target_user_id).count()
        return FollowResponse(follower_id=current_user.id, following_id=target_user_id, following=True, follower_count=cnt)


@router.get("/following", response_model=List[int])
def get_my_following(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns list of user IDs that the current user follows."""
    follows = db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()
    return [f[0] for f in follows]


@router.get("/followers/{user_id}", response_model=FollowerStatsResponse)
def get_followers_count(
    user_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Returns follower count and whether current user follows this user."""
    follower_count = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    is_following = False
    if current_user:
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id
        ).first() is not None
    return FollowerStatsResponse(
        user_id=user_id,
        follower_count=follower_count,
        following_count=following_count,
        is_following=is_following,
    )

