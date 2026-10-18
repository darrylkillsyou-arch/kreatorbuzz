import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import type { CommunityPost, Creator, PostCommentItem } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { formatCompactNumber } from '../lib/formatters';

// ── Constants ──────────────────────────────────────────────────────────────────
const AVAILABLE_TOOLS = [
  'Midjourney v6', 'Runway Gen-3', 'Flux 1.1 Pro', 'Sora Enterprise',
  'ComfyUI', 'Kling AI', 'Stable Video', 'ElevenLabs',
];

const POST_CATEGORIES = [
  { label: 'Showcase', value: 'Showcase' },
  { label: 'Hiring', value: 'Hiring' },
  { label: 'Offering Services', value: 'Offering Services' },
  { label: 'Looking For Creator', value: 'Looking For Creator' },
  { label: 'Collaboration', value: 'Collaboration' },
  { label: 'Announcement', value: 'Announcement' },
  { label: 'Urgent Requirement', value: 'Urgent Requirement' },
] as const;

const FILTER_OPTIONS = [
  { label: 'All Posts', value: 'All' },
  { label: 'Showcase', value: 'Showcase' },
  { label: 'Hiring', value: 'Hiring' },
  { label: 'Offering Services', value: 'Offering Services' },
  { label: 'Looking For Creator', value: 'Looking For Creator' },
  { label: 'Collaboration', value: 'Collaboration' },
  { label: 'Announcement', value: 'Announcement' },
  { label: 'Urgent Requirement', value: 'Urgent Requirement' },
];

type PostCategory = typeof POST_CATEGORIES[number]['value'];

// ── Badge helpers ──────────────────────────────────────────────────────────────
function getCategoryBadgeClass(type: string): string {
  switch (type) {
    case 'Showcase': return 'bg-secondary/20 text-secondary border border-secondary/30';
    case 'Hiring': return 'bg-primary/20 text-primary border border-primary/30';
    case 'Offering Services': case 'Offering service': return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
    case 'Looking For Creator': case 'Looking for creator': return 'bg-sky-500/20 text-sky-300 border border-sky-500/30';
    case 'Collaboration': return 'bg-violet-500/20 text-violet-300 border border-violet-500/30';
    case 'Announcement': return 'bg-amber-500/20 text-amber-300 border border-amber-500/30';
    case 'Urgent Requirement': return 'bg-red-600 text-white border border-red-500';
    default: return 'bg-surface-container text-on-surface-variant border border-outline-variant/30';
  }
}

function getCategoryIcon(type: string): string {
  switch (type) {
    case 'Showcase': return 'auto_awesome';
    case 'Hiring': return 'work';
    case 'Offering Services': case 'Offering service': return 'sell';
    case 'Looking For Creator': case 'Looking for creator': return 'person_search';
    case 'Collaboration': return 'group';
    case 'Announcement': return 'campaign';
    case 'Urgent Requirement': return 'priority_high';
    default: return 'article';
  }
}

function isUrgent(type: string): boolean {
  return type === 'Urgent Requirement';
}

const deduplicatePosts = (postList: CommunityPost[]): CommunityPost[] => {
  const seen = new Set<string>();
  return postList.filter((post) => {
    if (!post?.id || seen.has(String(post.id))) return false;
    seen.add(String(post.id));
    return true;
  });
};

// ── Main Component ─────────────────────────────────────────────────────────────
export const CommunityPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [creators, setCreators] = useState<Creator[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [postContent, setPostContent] = useState('');
  const [postTitle, setPostTitle] = useState('');
  const [postCategory, setPostCategory] = useState<PostCategory>('Showcase');
  const [selectedTools, setSelectedTools] = useState<string[]>(['Midjourney v6', 'Runway Gen-3']);
  const [imageUrl, setImageUrl] = useState('');
  const [showToolPicker, setShowToolPicker] = useState(false);
  const [showImageInput, setShowImageInput] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>('All');
  const [showFilterBar, setShowFilterBar] = useState(false);
  const [commentInputs, setCommentInputs] = useState<Record<string, string>>({});
  const [showCommentBox, setShowCommentBox] = useState<Record<string, boolean>>({});
  const [postCommentsMap, setPostCommentsMap] = useState<Record<string, PostCommentItem[]>>({});
  const [loadingComments, setLoadingComments] = useState<Record<string, boolean>>({});
  const [followingMap, setFollowingMap] = useState<Record<string, boolean>>({});
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadCommunityData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [p, c] = await Promise.all([
        api.community.getPosts(activeFilter),
        api.creators.list({ limit: 6 }),
      ]);
      const deduped = deduplicatePosts(p);
      setPosts(deduped);
      setCreators(c);

      // Bootstrap following state from post data
      const initFollowing: Record<string, boolean> = {};
      deduped.forEach((post) => {
        if (post.is_following_author !== undefined) {
          initFollowing[post.author_id] = Boolean(post.is_following_author);
        }
      });
      setFollowingMap((prev) => ({ ...initFollowing, ...prev }));

      // Pre-populate existing comments
      const initialComments: Record<string, PostCommentItem[]> = {};
      p.forEach((post) => {
        if (post.comments && post.comments.length > 0) {
          initialComments[post.id] = post.comments;
        }
      });
      setPostCommentsMap((prev) => ({ ...prev, ...initialComments }));
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load community feed.');
    } finally {
      setIsLoading(false);
    }
  }, [activeFilter]);

  useEffect(() => { loadCommunityData(); }, [loadCommunityData]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleCreatePost = async () => {
    if (isSubmitting || !postContent.trim()) return;
    if (!user) { setErrorMessage('Please sign in to publish a post.'); return; }
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const newP = await api.community.createPost({
        title: postTitle.trim() || undefined,
        body: postContent.trim(),
        post_type: postCategory,
        pipeline_badges: selectedTools.length > 0 ? selectedTools : undefined,
        media_url: imageUrl.trim() || undefined,
      });
      setPosts((prev) => deduplicatePosts([newP, ...prev]));
      setPostContent('');
      setPostTitle('');
      setImageUrl('');
      setShowToolPicker(false);
      setShowImageInput(false);
      showToast('Post published to community feed!');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to publish post.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLike = async (postId: string) => {
    if (!user) { setErrorMessage('Please sign in to like posts.'); return; }
    try {
      const res = await api.community.likePost(postId);
      setPosts((prev) => prev.map((p) =>
        p.id === postId ? { ...p, is_liked: res.liked, likes_count: res.likes_count } : p
      ));
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to like post.');
    }
  };

  const handleFollow = async (authorId: string) => {
    if (!user) { setErrorMessage('Please sign in to follow creators.'); return; }
    if (authorId === user.id) { showToast('You cannot follow yourself.'); return; }
    const wasFollowing = followingMap[authorId] || false;
    // Optimistic update
    setFollowingMap((prev) => ({ ...prev, [authorId]: !wasFollowing }));
    try {
      const res = await api.community.followUser(authorId);
      setFollowingMap((prev) => ({ ...prev, [authorId]: res.following }));
      showToast(res.following ? 'Now following this creator!' : 'Unfollowed.');
    } catch (err: any) {
      // Revert on error
      setFollowingMap((prev) => ({ ...prev, [authorId]: wasFollowing }));
      setErrorMessage(err.message || 'Failed to update follow status.');
    }
  };

  const toggleCommentsBox = async (postId: string) => {
    const nextState = !showCommentBox[postId];
    setShowCommentBox((prev) => ({ ...prev, [postId]: nextState }));
    if (nextState && !postCommentsMap[postId]) {
      setLoadingComments((prev) => ({ ...prev, [postId]: true }));
      try {
        const comments = await api.community.getComments(postId);
        setPostCommentsMap((prev) => ({ ...prev, [postId]: comments }));
      } catch {
        setPostCommentsMap((prev) => ({ ...prev, [postId]: [] }));
      } finally {
        setLoadingComments((prev) => ({ ...prev, [postId]: false }));
      }
    }
  };

  const handleComment = async (postId: string) => {
    const text = commentInputs[postId];
    if (!text?.trim() || !user) { if (!user) setErrorMessage('Sign in to comment.'); return; }
    try {
      const newComment = await api.community.commentOnPost(postId, text.trim());
      setPostCommentsMap((prev) => ({ ...prev, [postId]: [...(prev[postId] || []), newComment] }));
      setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, comments_count: p.comments_count + 1 } : p));
      setCommentInputs((prev) => ({ ...prev, [postId]: '' }));
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to post comment.');
    }
  };

  const handleShare = (post: CommunityPost) => {
    const url = `${window.location.origin}/community#post-${post.id}`;
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(() => showToast('Link copied!')).catch(() => showToast(url));
    else showToast(url);
  };

  const toggleToolTag = (tool: string) =>
    setSelectedTools((prev) => prev.includes(tool) ? prev.filter((t) => t !== tool) : [...prev, tool]);

  return (
    <div className="flex flex-col w-full">
      {/* Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-secondary text-on-secondary px-5 py-3 rounded-full shadow-2xl font-label-md flex items-center gap-2 animate-fade-in border border-secondary-container">
          <span className="material-symbols-outlined text-[18px]">check_circle</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <section className="max-w-7xl mx-auto px-gutter w-full pt-space-lg pb-space-md">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pb-space-md">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-space-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
              <span className="font-label-sm text-label-sm uppercase tracking-widest text-secondary font-semibold">Creator Network</span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">The Creative AI Community</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">
              Show your work, post opportunities, find collaborators, and discover what's being built.
            </p>
          </div>
          <div className="flex items-center gap-space-sm shrink-0">
            <button
              onClick={() => setShowFilterBar(!showFilterBar)}
              className={`inline-flex items-center gap-2 px-space-md py-2.5 rounded-full font-label-lg text-label-lg transition-colors cursor-pointer ${showFilterBar || activeFilter !== 'All'
                  ? 'bg-secondary/20 text-secondary border border-secondary/40'
                  : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                }`}
              type="button"
            >
              <span className="material-symbols-outlined text-[18px]">tune</span>
              <span>Filter{activeFilter !== 'All' ? `: ${activeFilter}` : ''}</span>
            </button>
            <button
              onClick={() => document.getElementById('composer-textarea')?.focus()}
              className="inline-flex items-center gap-2 px-space-lg py-2.5 bg-primary text-on-primary hover:bg-primary-container hover:text-on-surface font-label-lg text-label-lg rounded-full transition-all shadow-sm cursor-pointer"
              type="button"
            >
              <span className="material-symbols-outlined text-[18px]">edit_square</span>
              <span>Create Post</span>
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        {showFilterBar && (
          <div className="pt-2 pb-4 flex items-center gap-2 flex-wrap animate-fade-in border-t border-outline-variant/20">
            <span className="font-label-sm text-on-surface-variant uppercase tracking-wider text-xs font-semibold mr-1">Filter:</span>
            {FILTER_OPTIONS.map((f) => (
              <button
                key={f.value}
                type="button"
                onClick={() => setActiveFilter(f.value)}
                className={`px-3 py-1 rounded-full font-label-sm text-xs tracking-wider transition-colors cursor-pointer ${activeFilter === f.value
                    ? 'bg-primary text-on-primary font-bold'
                    : 'bg-surface-container hover:bg-surface-container-high text-on-surface-variant'
                  }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        )}

        {/* Error Banner */}
        {errorMessage && (
          <div className="mb-4 p-3.5 bg-error-container/40 text-on-error-container rounded-xl text-body-sm border border-error/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[20px] text-error">error</span>
              <span>{errorMessage}</span>
            </div>
            <button onClick={() => setErrorMessage(null)} className="p-1 text-on-error-container hover:opacity-70">
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>
        )}
      </section>

      {/* Main Grid */}
      <div className="max-w-7xl mx-auto px-gutter w-full pb-space-xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">

          {/* Feed Column */}
          <div className="lg:col-span-8 flex flex-col gap-space-lg">

            {/* Composer */}
            <div className="bg-surface-container-low rounded-xl p-space-md md:p-space-lg shadow-sm border border-outline-variant/30">
              <div className="flex items-start gap-space-sm mb-space-sm">
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0 text-on-primary font-label-md font-bold">
                  {user ? (user.name ? user.name[0].toUpperCase() : 'U') : 'C'}
                </div>
                <div className="flex-1 space-y-2">
                  <input
                    type="text"
                    value={postTitle}
                    onChange={(e) => setPostTitle(e.target.value)}
                    placeholder="Post title (optional)..."
                    className="w-full bg-surface text-on-surface font-headline-sm text-[16px] px-3 py-1.5 rounded-lg placeholder:text-outline focus:outline-none focus:ring-1 focus:ring-secondary/50 border border-outline-variant/20"
                  />
                  <textarea
                    id="composer-textarea"
                    value={postContent}
                    onChange={(e) => setPostContent(e.target.value)}
                    className="w-full bg-surface text-on-surface font-body-md text-body-md p-space-sm rounded-lg resize-none placeholder:text-outline focus:outline-none focus:ring-1 focus:ring-secondary/50 shadow-inner border border-outline-variant/20"
                    placeholder="Share your work, post an opportunity, or find collaborators..."
                    rows={3}
                  />
                </div>
              </div>

              {/* Category Chips */}
              <div className="flex items-center gap-1.5 flex-wrap pt-1 pb-space-sm">
                {POST_CATEGORIES.map((cat) => (<button
                  key={cat.value}
                  onClick={() => setPostCategory(cat.value)}
                  className={`px-space-sm py-1 font-label-sm text-label-sm uppercase tracking-wider rounded-full transition-colors cursor-pointer text-xs ${postCategory === cat.value
                      ? 'bg-primary text-on-primary font-semibold'
                      : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                    }`}
                  type="button"
                >
                  {cat.label}
                </button>
                ))}
              </div>

              {/* Tool Picker */}
              {showToolPicker && (
                <div className="p-3 bg-surface rounded-lg mb-space-sm border border-outline-variant/20 space-y-2 animate-fade-in">
                  <span className="font-label-sm text-xs uppercase tracking-wider text-on-surface-variant block font-semibold">Tag AI Models & Tools:</span>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {AVAILABLE_TOOLS.map((tool) => (
                      <button key={tool} type="button" onClick={() => toggleToolTag(tool)}
                        className={`px-2.5 py-1 rounded-full font-label-sm text-xs transition-colors cursor-pointer ${selectedTools.includes(tool) ? 'bg-secondary text-on-secondary font-semibold' : 'bg-surface-container-high text-on-surface hover:bg-surface-container-highest'
                          }`}
                      >
                        {selectedTools.includes(tool) ? '✓ ' : '+ '}{tool}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Image URL */}
              {showImageInput && (
                <div className="p-3 bg-surface rounded-lg mb-space-sm border border-outline-variant/20 space-y-2 animate-fade-in">
                  <span className="font-label-sm text-xs uppercase tracking-wider text-on-surface-variant block font-semibold">Attach Image URL:</span>
                  <input
                    type="url" value={imageUrl} onChange={(e) => setImageUrl(e.target.value)}
                    placeholder="https://images.unsplash.com/..."
                    className="w-full bg-surface-container text-on-surface text-body-sm px-3 py-1.5 rounded-lg border border-outline-variant/30 focus:outline-none focus:border-secondary"
                  />
                  {imageUrl && (
                    <div className="w-24 h-24 rounded-lg overflow-hidden border border-outline-variant/30 mt-1">
                      <img src={imageUrl} alt="Preview" className="w-full h-full object-cover" />
                    </div>
                  )}
                </div>
              )}

              {/* Actions Bar */}
              <div className="flex items-center justify-between pt-space-xs border-t border-surface-container-highest/60">
                <div className="flex items-center gap-space-xs">
                  <button
                    onClick={() => setShowImageInput(!showImageInput)}
                    className={`flex items-center gap-1.5 px-space-sm py-1.5 rounded-lg font-label-md text-label-md transition-colors cursor-pointer ${showImageInput || imageUrl ? 'bg-secondary/15 text-secondary' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
                      }`}
                    type="button"
                  >
                    <span className="material-symbols-outlined text-[18px]">add_photo_alternate</span>
                    <span className="hidden sm:inline">Attach Image</span>
                  </button>
                  <button
                    onClick={() => setShowToolPicker(!showToolPicker)}
                    className={`flex items-center gap-1.5 px-space-sm py-1.5 rounded-lg font-label-md text-label-md transition-colors cursor-pointer ${showToolPicker ? 'bg-secondary/15 text-secondary' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
                      }`}
                    type="button"
                  >
                    <span className="material-symbols-outlined text-[18px]">neurology</span>
                    <span className="hidden sm:inline">Tag Models ({selectedTools.length})</span>
                  </button>
                </div>
                <button
                  onClick={handleCreatePost}
                  disabled={isSubmitting || !postContent.trim()}
                  className="px-space-md py-2 bg-primary text-on-primary font-label-md text-label-md rounded-full hover:bg-primary-container hover:text-on-surface transition-all cursor-pointer shadow-sm disabled:opacity-50"
                  type="button"
                >
                  {isSubmitting ? 'Publishing...' : 'Publish'}
                </button>
              </div>
            </div>

            {/* Posts Stream */}
            {isLoading ? (
              <LoadingSpinner message="Loading community feed..." />
            ) : posts.length === 0 ? (
              <div className="bg-surface-container-low rounded-xl p-space-xl text-center border border-outline-variant/30 space-y-3">
                <div className="w-12 h-12 rounded-full bg-surface-container-high text-on-surface-variant mx-auto flex items-center justify-center">
                  <span className="material-symbols-outlined text-[24px]">forum</span>
                </div>
                <h3 className="font-headline-sm text-headline-sm text-on-surface">No posts for this filter</h3>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto">
                  {activeFilter !== 'All' ? `No ${activeFilter} posts yet. ` : ''}Be the first to share with the community.
                </p>
                {activeFilter !== 'All' && (
                  <button onClick={() => setActiveFilter('All')} className="text-secondary font-label-md text-sm hover:underline cursor-pointer" type="button">View all posts</button>
                )}
              </div>
            ) : (
              posts.map((post) => {
                const currentComments = postCommentsMap[post.id] || post.comments || [];
                const creatorProfilePath = post.creator_id ? `/creators/${post.creator_id}` : null;
                const urgent = isUrgent(post.post_type);
                const isOwnPost = user && post.author_id === user.id;
                const isFollowing = followingMap[post.author_id] ?? post.is_following_author ?? false;

                return (
                  <article
                    key={post.id}
                    id={`post-${post.id}`}
                    className={`bg-surface-container-low rounded-xl p-space-md md:p-space-lg shadow-sm flex flex-col gap-space-md transition-all hover:border-outline-variant border ${urgent ? 'border-l-4 border-l-red-500 border-outline-variant/30' : 'border-outline-variant/30'
                      }`}
                  >
                    {/* Urgent Banner */}
                    {urgent && (
                      <div className="flex items-center gap-2 -mt-1 -mx-1 px-3 py-1.5 bg-red-600/10 rounded-t-lg border-b border-red-500/20">
                        <span className="material-symbols-outlined text-red-400 text-[16px] animate-pulse">priority_high</span>
                        <span className="font-label-sm text-xs text-red-400 font-semibold uppercase tracking-wider">Urgent Requirement</span>
                      </div>
                    )}

                    {/* Author Header */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-3 min-w-0">
                        {creatorProfilePath ? (
                          <Link to={creatorProfilePath} className="group shrink-0">
                            <div className="w-11 h-11 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center font-headline-sm overflow-hidden group-hover:scale-105 transition-transform">
                              {post.author_avatar
                                ? <img src={post.author_avatar} alt={post.author_name} className="w-full h-full object-cover" loading="lazy" />
                                : <span className="font-semibold">{post.author_initial || post.author_name?.[0] || 'C'}</span>
                              }
                            </div>
                          </Link>
                        ) : (
                          <div className="w-11 h-11 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center font-headline-sm overflow-hidden shrink-0">
                            {post.author_avatar
                              ? <img src={post.author_avatar} alt={post.author_name} className="w-full h-full object-cover" loading="lazy" />
                              : <span className="font-semibold">{post.author_initial || post.author_name?.[0] || 'U'}</span>
                            }
                          </div>
                        )}

                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            {creatorProfilePath ? (
                              <Link to={creatorProfilePath} className="font-semibold text-on-surface hover:text-secondary transition-colors text-[15px] truncate">
                                {post.author_name}
                              </Link>
                            ) : (
                              <span className="font-semibold text-on-surface text-[15px] truncate">{post.author_name}</span>
                            )}
                            {post.author_badge && (
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full font-label-sm text-[10px] uppercase tracking-wider font-semibold ${post.badge_class || 'bg-secondary-fixed text-on-secondary-fixed'
                                }`}>
                                {post.author_badge}
                              </span>
                            )}
                          </div>
                          <p className="font-body-sm text-xs text-on-surface-variant mt-0.5 truncate">
                            {post.author_title} · {post.time_ago}
                          </p>
                        </div>
                      </div>

                      {/* Right: Category Badge + Follow + Share */}
                      <div className="flex items-center gap-2 shrink-0">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-label-sm text-[10px] uppercase tracking-wider font-semibold ${getCategoryBadgeClass(post.post_type)
                          }`}>
                          <span className="material-symbols-outlined text-[11px]">{getCategoryIcon(post.post_type)}</span>
                          {post.post_type}
                        </span>

                        {/* Follow Button */}
                        {!isOwnPost && user && (
                          <button
                            onClick={() => handleFollow(post.author_id)}
                            className={`px-3 py-1 rounded-full font-label-sm text-xs transition-all cursor-pointer font-semibold ${isFollowing
                                ? 'bg-secondary/20 text-secondary border border-secondary/30 hover:bg-error/10 hover:text-error hover:border-error/30'
                                : 'bg-surface-container hover:bg-secondary/15 text-on-surface-variant hover:text-secondary border border-outline-variant/30'
                              }`}
                            type="button"
                          >
                            {isFollowing ? 'Following' : 'Follow'}
                          </button>
                        )}

                        <button
                          onClick={() => handleShare(post)}
                          title="Share"
                          className="text-on-surface-variant hover:text-on-surface p-1.5 rounded-full hover:bg-surface-container cursor-pointer transition-colors"
                          type="button"
                        >
                          <span className="material-symbols-outlined text-[18px]">share</span>
                        </button>
                      </div>
                    </div>

                    {/* Body */}
                    <div className="space-y-space-xs">
                      {post.title && post.title !== post.body && (
                        <h2 className="font-headline-md text-headline-md text-on-surface font-semibold">{post.title}</h2>
                      )}
                      <p className="font-body-md text-body-md text-on-surface leading-relaxed whitespace-pre-line">{post.body}</p>
                    </div>

                    {/* Pipeline Badges */}
                    {post.pipeline_badges && post.pipeline_badges.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5">
                        {post.pipeline_badges.map((badge, idx) => (
                          <span key={idx} className="px-2.5 py-0.5 bg-surface-container-high text-on-surface font-label-sm text-xs uppercase tracking-wider rounded-md">
                            {badge}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Post Media (distinct from avatar) */}
                    {post.media_url && (
                      <div className="w-full rounded-xl overflow-hidden bg-surface-container shadow-inner max-h-[480px]">
                        <img
                          alt={post.media_caption || post.title}
                          className="w-full h-auto max-h-[480px] object-cover hover:scale-[1.01] transition-transform duration-500"
                          src={post.media_url}
                          loading="lazy"
                          onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                        />
                      </div>
                    )}

                    {/* Interaction Bar */}
                    <div className="flex items-center justify-between pt-space-xs border-t border-surface-container-highest/60">
                      <div className="flex items-center gap-space-md">
                        <button
                          onClick={() => handleLike(post.id)}
                          className={`inline-flex items-center gap-1.5 transition-colors font-label-md text-label-md cursor-pointer ${post.is_liked ? 'text-secondary font-semibold' : 'text-on-surface-variant hover:text-secondary'
                            }`}
                          type="button"
                          title={`${post.likes_count} likes`}
                        >
                          <span className="material-symbols-outlined text-[20px]" style={post.is_liked ? { fontVariationSettings: "'FILL' 1" } : {}}>favorite</span>
                          <span>{formatCompactNumber(post.likes_count)}</span>
                        </button>

                        <button
                          onClick={() => toggleCommentsBox(post.id)}
                          className="inline-flex items-center gap-1.5 text-on-surface-variant hover:text-on-surface transition-colors font-label-md text-label-md cursor-pointer"
                          type="button"
                          title={`${post.comments_count} comments`}
                        >
                          <span className="material-symbols-outlined text-[20px]">chat_bubble</span>
                          <span>{formatCompactNumber(post.comments_count)} comments</span>
                        </button>
                      </div>

                      <div className="flex items-center gap-space-xs">
                        {creatorProfilePath && (
                          <Link to={creatorProfilePath} className="px-space-md py-1.5 bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-xs rounded-full transition-colors font-semibold">
                            View Profile
                          </Link>
                        )}
                        {(post.post_type === 'Hiring' || post.post_type === 'Looking For Creator' || post.post_type === 'Urgent Requirement') && (
                          <Link to="/briefs" className="px-space-md py-1.5 bg-primary text-on-primary hover:bg-primary-container hover:text-on-surface font-label-md text-xs rounded-full transition-all shadow-sm">
                            Create Proposal
                          </Link>
                        )}
                        {(post.post_type === 'Showcase' || post.post_type === 'Offering Services' || post.post_type === 'Offering service') && creatorProfilePath && (
                          <Link to={creatorProfilePath} className="px-space-md py-1.5 bg-primary text-on-primary hover:bg-primary-container hover:text-on-surface font-label-md text-xs rounded-full transition-all shadow-sm">
                            Hire Creator
                          </Link>
                        )}
                      </div>
                    </div>

                    {/* Comments Section */}
                    {showCommentBox[post.id] && (
                      <div className="pt-space-xs space-y-space-sm border-t border-outline-variant/20 animate-fade-in">
                        {loadingComments[post.id] ? (
                          <p className="text-body-sm text-on-surface-variant text-xs py-2">Loading comments...</p>
                        ) : currentComments.length > 0 ? (
                          <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                            {currentComments.map((c) => (
                              <div key={c.id} className="bg-surface p-2.5 rounded-lg border border-outline-variant/20 flex items-start gap-2.5">
                                <div className="w-7 h-7 rounded-full bg-secondary/15 text-secondary flex items-center justify-center shrink-0 font-label-sm font-bold text-xs">
                                  {c.user_avatar
                                    ? <img src={c.user_avatar} alt={c.user_name} className="w-full h-full rounded-full object-cover" />
                                    : c.user_name ? c.user_name[0].toUpperCase() : 'U'
                                  }
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center justify-between gap-2">
                                    <div className="flex items-center gap-1.5 truncate">
                                      <span className="font-label-sm font-semibold text-on-surface text-xs truncate">{c.user_name}</span>
                                      {c.user_role && (
                                        <span className="px-1.5 rounded font-label-sm text-[9px] bg-surface-container text-on-surface-variant uppercase">{c.user_role}</span>
                                      )}
                                    </div>
                                    <span className="font-label-sm text-[10px] text-on-surface-variant shrink-0">{c.created_at}</span>
                                  </div>
                                  <p className="font-body-sm text-body-sm text-on-surface mt-1 leading-relaxed">{c.content}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-body-sm text-on-surface-variant text-xs py-1 italic">No comments yet. Be the first!</p>
                        )}
                        <div className="flex gap-2 pt-1">
                          <input
                            type="text"
                            placeholder={user ? 'Write a comment...' : 'Sign in to comment...'}
                            disabled={!user}
                            value={commentInputs[post.id] || ''}
                            onChange={(e) => setCommentInputs({ ...commentInputs, [post.id]: e.target.value })}
                            onKeyDown={(e) => e.key === 'Enter' && handleComment(post.id)}
                            className="flex-1 bg-surface text-on-surface text-body-sm px-3.5 py-2 rounded-lg border border-outline-variant focus:outline-none focus:border-secondary disabled:opacity-60"
                          />
                          <button
                            onClick={() => handleComment(post.id)}
                            disabled={!user || !commentInputs[post.id]?.trim()}
                            className="px-4 py-2 bg-primary text-on-primary font-label-sm text-xs rounded-lg hover:bg-primary-container hover:text-on-surface transition-colors cursor-pointer disabled:opacity-50"
                          >
                            Post
                          </button>
                        </div>
                      </div>
                    )}
                  </article>
                );
              })
            )}
          </div>

          {/* Sidebar */}
          <aside className="lg:col-span-4 flex flex-col gap-space-lg">
            {/* Featured Creators */}
            <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-outline-variant/30">
              <div className="flex items-center justify-between pb-space-sm border-b border-surface-container-high mb-space-sm">
                <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold">Featured Creators</span>
                <Link to="/leaderboard" className="font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface">Rankings →</Link>
              </div>
              <div className="space-y-space-sm">
                {creators.slice(0, 5).map((creator) => {
                  const creatorUserId = creator.user_id || creator.id;
                  const isCreatorFollowed = followingMap[creatorUserId] ?? false;
                  return (
                    <div key={creator.id} className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5 truncate">
                        <img
                          alt={creator.name}
                          className="w-9 h-9 rounded-full object-cover bg-surface-container shrink-0"
                          src={creator.avatar}
                          loading="lazy"
                          onError={(e) => { (e.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/initials/svg?seed=${creator.name}`; }}
                        />
                        <div className="truncate">
                          <h4 className="font-label-md text-label-md text-on-surface truncate font-semibold">{creator.name}</h4>
                          <span className="font-body-sm text-xs text-on-surface-variant block truncate">{creator.specialization.split('•')[0]}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <button
                          onClick={() => navigate(`/creators/${creator.id}`)}
                          className="p-1.5 bg-surface-container hover:bg-surface-container-high rounded-full font-label-sm text-xs text-on-surface cursor-pointer"
                          title="View profile"
                        >
                          <span className="material-symbols-outlined text-[14px]">person</span>
                        </button>
                        {user && creatorUserId !== user.id && (
                          <button
                            onClick={() => handleFollow(creatorUserId)}
                            className={`px-2.5 py-1 rounded-full font-label-sm text-[11px] transition-all cursor-pointer font-semibold ${isCreatorFollowed
                                ? 'bg-secondary/20 text-secondary border border-secondary/30'
                                : 'bg-surface-container hover:bg-secondary/15 text-on-surface-variant hover:text-secondary border border-outline-variant/30'
                              }`}
                          >
                            {isCreatorFollowed ? '✓' : '+'} {isCreatorFollowed ? 'Following' : 'Follow'}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* AI Tools in Demand */}
            <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-outline-variant/30">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold block mb-space-sm">AI Tools in Demand</span>
              <div className="space-y-2">
                {[
                  { name: 'Sora Enterprise v2', use: 'Commercial Video', count: '48% of briefs' },
                  { name: 'Runway Gen-3 Alpha', use: 'Kinetic Motion', count: '32% of briefs' },
                  { name: 'Flux 1.1 Pro Ultra', use: 'Fashion Images', count: '20% of briefs' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-surface border border-outline-variant/20">
                  <div>
                    <span className="font-label-md text-on-surface block font-medium">{item.name}</span>
                    <span className="font-body-sm text-[11px] text-on-surface-variant">{item.use}</span>
                  </div>
                  <span className="font-label-sm text-[10px] text-secondary font-semibold">{item.count}</span>
                </div>
                ))}
              </div>
            </div>

            {/* Community Highlight */}
            <div className="bg-surface-container rounded-xl p-space-md space-y-space-xs border border-secondary/20">
              <span className="font-label-sm text-label-sm text-secondary uppercase tracking-widest font-semibold block">Community Highlight</span>
              <h4 className="font-headline-sm text-headline-sm text-on-surface">Build in Public. Get Hired Faster.</h4>
              <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                Recruiters on CODE XERO actively browse community posts. Showing your workflow, tools, and results gets you hired directly — without a cold DM.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};
