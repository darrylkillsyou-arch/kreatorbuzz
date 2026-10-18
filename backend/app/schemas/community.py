from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.users import UserResponse


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    post_type: str = "showcase"
    title: str
    content: str
    image_url: Optional[str] = None
    tools_tags: List[str] = []


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    author: Optional[UserResponse] = None
    creator_profile_id: Optional[int] = None
    likes_count: int = 0
    comments_count: int = 0
    is_liked_by_me: bool = False
    is_saved_by_me: bool = False
    is_following_author: bool = False
    comments: List[CommentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class LikeResponse(BaseModel):
    post_id: int
    user_id: int
    liked: bool
    likes_count: int


class FollowResponse(BaseModel):
    follower_id: int
    following_id: int
    following: bool
    follower_count: int = 0


class FollowerStatsResponse(BaseModel):
    user_id: int
    follower_count: int
    following_count: int
    is_following: bool
