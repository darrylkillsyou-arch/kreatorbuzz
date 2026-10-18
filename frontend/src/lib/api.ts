import type { Creator, Brief, CommunityPost, PostCommentItem, Workspace, User, Proposal, AppNotification, RecommendedCreator, XeroChatResponse } from '../types';

import { INITIAL_CREATORS, INITIAL_WORKSPACES, LEADERBOARD_STATS } from './mockData';
import { getCreatorAvatar, getCreatorHeroImage } from './creatorImages';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('codexero_token') || localStorage.getItem('maccall_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const data = await res.json();
      if (data && data.detail) {
        errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default errorMsg
    }
    throw new Error(errorMsg);
  }

  return await res.json();
}

// Local in-memory state for smooth client interactions when offline
let creatorsStore = [...INITIAL_CREATORS];
let workspacesStore = [...INITIAL_WORKSPACES];
let briefsStore: Brief[] = [
  {
    id: 'brief-aethelgard',
    title: 'Hyper-Luxury Kinetic Runway & Automotive Launch',
    prompt: 'I need a cinematic 30-second futuristic product launch video for a luxury automotive and fashion brand. Neo-brutalist architecture, dusk illumination with reflective wet concrete, high-fashion sculptural silhouettes walking alongside a bespoke electrified concept car.',
    objective: 'Brand Awareness & Product Reveal',
    content_type: '4K Cinematic AI Video',
    aesthetic: 'Neo-Brutalist Architectural Luxury with Volumetric Lighting',
    aesthetic_desc: 'Monolithic raw concrete structures, reflective rain-swept pavings, sculptural metallic gowns, warm amber kinetic illumination accents against midnight twilight.',
    style_tags: ['#VolumetricLighting', '#HauteCoutureRunway', '#ConceptAutomotive'],
    distribution_channels: ['Digital Billboard (32:9)', 'Instagram Reels (9:16)', 'YouTube & Web (16:9)'],
    deliverables: ['1x 30s Master Cut (ProRes 4444 + 4K MP4)', '3x 10s Social Platform Cuts (9:16 + 1:1)', 'Raw Latent Seeds & Styleframes'],
    budget_range: '$4,000 – $6,500 USD',
    sla_timeline: '5 Business Days',
    license_terms: 'Full Commercial & Raw Weight Provenance',
    escrow_amount: 4400,
    status: 'In Production'
  }
];

export function normalizeCreator(raw: any): Creator {
  if (!raw) return INITIAL_CREATORS[0];
  const portItem = raw.portfolio_items?.[0] || raw.featured_works?.[0];
  const name = raw.display_name || raw.name || raw.user?.full_name || 'Content Creator';
  const profileId = raw.profile_id != null ? String(raw.profile_id) : (raw.id != null ? String(raw.id) : undefined);
  const userId = raw.user_id != null ? String(raw.user_id) : (raw.user?.id != null ? String(raw.user.id) : undefined);
  const idStr = String(profileId || raw.id || userId || name);
  const spec = raw.specialization || raw.tagline || 'Content Creator';
  const avatar = raw.avatar || raw.user?.avatar_url || raw.avatar_url || getCreatorAvatar(idStr, name);
  const heroImage = raw.hero_image || portItem?.image_url || portItem?.image || getCreatorHeroImage(idStr, spec, raw.category);

  return {
    id: idStr,
    profile_id: profileId,
    user_id: userId,
    name,
    avatar,
    specialization: spec,
    location: raw.location || raw.user?.location || 'Milan / Paris',
    tier: raw.tier || (raw.is_verified ? 'Verified Master' : 'Creator'),
    is_verified: raw.is_verified ?? true,
    rating: raw.rating ?? 5.0,
    rate_per_day: raw.starting_rate || raw.rate_per_day || 1500,
    sla_index: raw.sla_score || raw.sla_index || 99.0,
    commissions_count: raw.total_briefs || raw.commissions_count || 30,
    on_time_rate: raw.on_time_percentage || raw.on_time_rate || 99.0,
    compatibility_score: raw.compatibility_score ?? raw.match_score ?? undefined,
    velocity_days: raw.velocity_days || (raw.delivery_days ? `${raw.delivery_days} Days Turnaround` : '4–6 Days Turnaround'),
    licensing: raw.licensing || (raw.commercial_rights ? 'Full Commercial' : 'Standard License'),
    tools_and_pipeline: Array.isArray(raw.ai_tools) ? raw.ai_tools : (Array.isArray(raw.tools_and_pipeline) ? raw.tools_and_pipeline : ['Runway Gen-3', 'Sora']),
    core_category: raw.core_category || raw.hero_category || undefined,
    sub_specializations: Array.isArray(raw.sub_specializations) ? raw.sub_specializations : [],
    style_tags: Array.isArray(raw.style_tags) ? raw.style_tags : [],
    hero_image: heroImage,
    hero_title: raw.hero_title || portItem?.title || `${name}: Editorial Showcase`,
    hero_category: raw.core_category || raw.hero_category || portItem?.category || spec.split('•')[0].trim(),
    bio: raw.bio || raw.user?.bio || raw.tagline || '',
    prompt_architecture: raw.prompt_architecture || 'Multi-pass latent upscaling with custom seed pinning.',
    featured_works: raw.featured_works || raw.portfolio_items?.map((p: any) => ({ title: p.title, image: p.image_url || p.image, tag: p.category })) || []
  };
}

export function formatRelativeTime(dateString?: string): string {
  if (!dateString) return 'Recently';
  try {
    const d = new Date(dateString);
    const now = new Date();
    const diffSecs = Math.floor((now.getTime() - d.getTime()) / 1000);
    if (diffSecs < 60) return 'Just now';
    const diffMins = Math.floor(diffSecs / 60);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
  } catch {
    return 'Recently';
  }
}

export function normalizeCommunityPost(raw: any): CommunityPost {
  if (!raw) {
    return {
      id: '0',
      author_id: '0',
      author_name: 'Unknown',
      author_title: 'Content Creator',
      author_location: 'Global',
      title: '',
      body: '',
      time_ago: 'Recently',
      likes_count: 0,
      comments_count: 0,
      is_liked: false,
      post_type: 'Showcase',
      pipeline_badges: [],
      comments: []
    };
  }
  const authorName = raw.author_name || raw.author?.full_name || 'Content Creator';
  const isBrand = raw.author?.role === 'brand';
  const authorRole = isBrand ? 'Recruiter' : (raw.author_badge || 'Content Creator');
  const postTypeMap: Record<string, CommunityPost['post_type']> = {
    showcase: 'Showcase',
    achievement: 'Showcase',
    creator_request: 'Looking For Creator',
    looking_for_creator: 'Looking For Creator',
    service: 'Offering Services',
    offering_services: 'Offering Services',
    offer: 'Offering Services',
    collaboration: 'Collaboration',
    collab: 'Collaboration',
    open_brief: 'Hiring',
    hiring: 'Hiring',
    announcement: 'Announcement',
    urgent_requirement: 'Urgent Requirement',
    urgent: 'Urgent Requirement',
  };
  const normalizedType = postTypeMap[String(raw.post_type).toLowerCase()] || (raw.post_type as CommunityPost['post_type']) || 'Showcase';

  const rawComments = Array.isArray(raw.comments) ? raw.comments : [];
  const comments = rawComments.map((c: any) => ({
    id: c.id,
    post_id: c.post_id,
    user_id: c.user_id,
    content: c.content,
    created_at: formatRelativeTime(c.created_at),
    user_name: c.user?.full_name || (c.user?.role === 'brand' ? 'Recruiter' : 'Content Creator'),
    user_role: c.user?.role === 'brand' ? 'Recruiter' : 'Content Creator',
    user_avatar: c.user?.avatar_url,
  }));

  const creatorId = raw.creator_profile_id
    ? String(raw.creator_profile_id)
    : (!isBrand ? String(raw.author_id || raw.author?.id || '') : undefined);

  return {
    id: String(raw.id),
    author_id: String(raw.author_id || raw.author?.id || 'author-1'),
    author_name: authorName,
    author_avatar: raw.author_avatar || raw.author?.avatar_url,
    author_initial: (authorName[0] || 'M').toUpperCase(),
    author_title: isBrand ? 'Recruiting Team' : 'Content Creator',
    author_location: raw.author_location || raw.author?.location || 'Global',
    author_badge: authorRole,
    badge_class: isBrand ? 'bg-primary text-on-primary' : 'bg-secondary-fixed text-on-secondary-fixed',
    time_ago: raw.created_at ? formatRelativeTime(raw.created_at) : (raw.time_ago || 'Recently'),
    title: raw.title || 'New post',
    body: raw.body || raw.content || '',
    post_type: normalizedType,
    pipeline_badges: Array.isArray(raw.pipeline_badges) ? raw.pipeline_badges : (Array.isArray(raw.tools_tags) ? raw.tools_tags : ['Midjourney v6', 'Runway Gen-3']),
    media_url: raw.media_url || raw.image_url,
    media_caption: raw.media_caption || raw.title,
    prompt_notes: raw.prompt_notes || undefined,
    likes_count: raw.likes_count ?? raw.like_count ?? 0,
    comments_count: raw.comments_count ?? raw.comment_count ?? comments.length,
    is_liked: Boolean(raw.is_liked_by_me ?? raw.is_liked),
    is_hireable: raw.is_hireable ?? !isBrand,
    is_following_author: Boolean(raw.is_following_author),
    creator_id: creatorId || undefined,
    comments,
  };
}

export function normalizeWorkspace(raw: any): Workspace {
  if (!raw) return INITIAL_WORKSPACES[0];

  const creatorUser = raw.creator_user;
  const brandUser = raw.brand_user;
  const creatorName = creatorUser?.full_name || 'Content Creator';
  const creatorId = String(raw.creator_user_id || creatorUser?.id || 'creator');
  const creatorAvatar = creatorUser?.avatar_url || getCreatorAvatar(creatorId, creatorName);

  const rawMilestones = Array.isArray(raw.milestones) ? raw.milestones : [];
  const milestones = rawMilestones.map((m: any, idx: number) => ({
    id: String(m.id || `m-${idx}`),
    step_number: idx + 1,
    title: m.title || `Milestone ${idx + 1}`,
    description: m.description || '',
    status: (m.status === 'completed' || m.status === 'released'
      ? 'completed'
      : m.status === 'in_progress' || m.status === 'approved'
      ? 'in_progress'
      : 'pending') as 'completed' | 'in_progress' | 'pending',
    amount: Number(m.amount || 0),
    payout_percentage: rawMilestones.length > 0 ? Math.round(100 / rawMilestones.length) : 100,
    completion_date: m.completed_at || undefined,
  }));

  if (milestones.length === 0) {
    milestones.push({
      id: `m-init-${raw.id}`,
      step_number: 1,
      title: 'Project Setup & Kickoff',
      description: 'Initial scope, requirements, and deliverables setup.',
      status: 'in_progress',
      amount: 0,
      payout_percentage: 100,
    });
  }

  const rawMessages = Array.isArray(raw.messages) ? raw.messages : [];
  const messages = rawMessages.map((msg: any) => {
    const isBrand = msg.sender_id === raw.brand_user_id;
    return {
      id: String(msg.id),
      sender_id: String(msg.sender_id),
      sender_name: msg.sender?.full_name || (isBrand ? 'Recruiter' : creatorName),
      sender_avatar: msg.sender?.avatar_url,
      sender_role: (msg.sender?.role === 'brand' || isBrand ? 'brand' : msg.sender?.role === 'system' ? 'system' : 'creator') as 'brand' | 'creator' | 'system',
      content: msg.content || '',
      created_at: msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recently',
    };
  });

  const totalBudget = milestones.reduce((sum: number, m: any) => sum + (m.amount || 0), 0);

  const rawRevisions = Array.isArray(raw.revisions) ? raw.revisions : [];
  const revisions = rawRevisions.map((r: any) => ({
    id: r.id,
    milestone_id: r.milestone_id ?? null,
    workspace_id: r.workspace_id,
    requester_id: r.requester_id,
    description: r.description,
    status: r.status || 'open',
    created_at: r.created_at ? new Date(r.created_at).toLocaleString('en-IN') : '',
    requester: r.requester ? { id: r.requester.id, full_name: r.requester.full_name, email: r.requester.email } : undefined,
  }));

  const creatorObj: Creator = {
    id: creatorId,
    name: creatorName,
    avatar: creatorAvatar,
    specialization: creatorUser?.specialization || 'AI Content Specialist',
    location: 'Global',
    tier: 'Verified Creator',
    is_verified: true,
    rate_per_day: totalBudget || 50000,
    sla_index: 99.0,
    commissions_count: 24,
    on_time_rate: 98.5,
    tools_and_pipeline: ['Midjourney v6', 'Runway Gen-3', 'ComfyUI'],
    hero_image: creatorAvatar,
    featured_works: [],
  };

  return {
    id: String(raw.id),
    brief_id: String(raw.brief_id || ''),
    brief_ref: raw.brief_id ? `MC-${raw.brief_id}` : `MC-${1000 + Number(raw.id)}`,
    title: raw.title || 'Project Workspace',
    description: raw.description || raw.brief?.description || `Collaboration workspace for ${raw.title}`,
    brand_id: String(raw.brand_user_id || 'brand'),
    brand_name: brandUser?.full_name || brandUser?.company || 'Recruiter',
    creator: creatorObj,
    total_budget: totalBudget,
    milestones,
    deliverables: Array.isArray(raw.files) ? raw.files.map((f: any) => ({
      id: String(f.id),
      milestone_id: f.milestone_id ?? null,
      title: f.filename,
      type: f.file_type || 'Asset',
      resolution: 'Original',
      file_size: f.file_size || 'Unknown',
      mime_type: f.mime_type,
      version: f.version || 1,
      url: f.download_url || `/api/workspaces/${raw.id}/files/${f.id}/download`,
      status: f.status || 'submitted',
      created_at: f.created_at ? new Date(f.created_at).toLocaleString('en-IN') : '',
      uploader_id: f.uploader_id,
      uploader_name: f.uploader?.full_name || (f.uploader_id === raw.creator_user_id ? creatorName : brandUser?.full_name || 'Team'),
    })) : [],
    messages,
    revisions,
    review: raw.review ? {
      id: raw.review.id,
      workspace_id: raw.review.workspace_id,
      recruiter_user_id: raw.review.recruiter_user_id,
      creator_user_id: raw.review.creator_user_id,
      rating: raw.review.rating,
      comment: raw.review.comment,
      created_at: raw.review.created_at ? new Date(raw.review.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }) : '',
      recruiter: raw.review.recruiter,
    } : null,
    unread_count: 0,
    status: raw.status || 'discovery',
    stage_tag: raw.status === 'completed' ? 'Completed' : (raw.status === 'delivered' ? 'Delivered' : 'Production (Active)'),
    category_tag: raw.brief?.content_type || 'AI Commission',
    created_at: raw.created_at ? new Date(raw.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recently',
    completed_at: raw.completed_at ? new Date(raw.completed_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }) : null,
  };
}

export const api = {
  auth: {
    login: async (email: string, _pass: string): Promise<{ token: string; user: User }> => {
      const res = await request<{ access_token: string; token_type: string; user: any }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: email.trim().toLowerCase(), password: _pass }),
      });
      const token = res.access_token;
      const rawUser = res.user;
      const user: User = {
        id: String(rawUser.id),
        email: rawUser.email,
        name: rawUser.full_name || rawUser.name || 'User',
        role: rawUser.role,
        avatar_url: rawUser.avatar_url,
      };
      localStorage.setItem('codexero_token', token);
      localStorage.setItem('codexero_user', JSON.stringify(user));
      localStorage.setItem('maccall_token', token);
      localStorage.setItem('maccall_user', JSON.stringify(user));
      return { token, user };
    },
    register: async (data: { email: string; name: string; role: 'brand' | 'creator'; company?: string; password?: string }): Promise<{ token: string; user: User }> => {
      const res = await request<{ access_token: string; token_type: string; user: any }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: data.email.trim().toLowerCase(),
          password: data.password || 'demo1234',
          full_name: data.name,
          role: data.role,
        }),
      });
      const token = res.access_token;
      const rawUser = res.user;
      const user: User = {
        id: String(rawUser.id),
        email: rawUser.email,
        name: rawUser.full_name || rawUser.name || 'User',
        role: rawUser.role,
        avatar_url: rawUser.avatar_url,
        company: data.company,
      };
      localStorage.setItem('codexero_token', token);
      localStorage.setItem('codexero_user', JSON.stringify(user));
      localStorage.setItem('maccall_token', token);
      localStorage.setItem('maccall_user', JSON.stringify(user));
      return { token, user };
    },
    getMe: async (): Promise<User> => {
      const raw = await request<any>('/auth/me');
      const user: User = {
        id: String(raw.id),
        email: raw.email,
        name: raw.full_name || raw.name || 'User',
        role: raw.role,
        avatar_url: raw.avatar_url,
      };
      localStorage.setItem('codexero_user', JSON.stringify(user));
      localStorage.setItem('maccall_user', JSON.stringify(user));
      return user;
    }
  },

  creators: {
    list: async (params?: { category?: string; query?: string; specialization?: string; style?: string; tools?: string; limit?: number; skip?: number }): Promise<Creator[]> => {
      try {
        const queryObj: Record<string, string> = {};
        if (params?.category && params.category !== 'All' && params.category !== 'All Specialties') {
          queryObj.category = params.category;
        }
        if (params?.query) {
          queryObj.query = params.query;
        }
        if (params?.specialization && params.specialization !== 'All Specializations') {
          queryObj.specialization = params.specialization;
        }
        if (params?.style && params.style !== 'All Styles') {
          queryObj.style = params.style;
        }
        if (params?.tools && params.tools !== 'All Tools') {
          queryObj.tools = params.tools;
        }
        if (params?.limit !== undefined) {
          queryObj.limit = String(params.limit);
        } else {
          queryObj.limit = '200';
        }
        if (params?.skip !== undefined) {
          queryObj.skip = String(params.skip);
        }
        const qs = new URLSearchParams(queryObj).toString();
        const data = await request<any[]>(`/creators${qs ? `?${qs}` : ''}`);
        return data.map(normalizeCreator);
      } catch {
        let result = creatorsStore;
        if (params?.category && params.category !== 'All' && params.category !== 'All Specialties') {
          const cat = params.category.toLowerCase().trim();
          result = result.filter(c => {
            const text = `${c.specialization} ${c.hero_category || ''} ${c.bio || ''} ${c.tools_and_pipeline.join(' ')}`.toLowerCase();
            if (cat.includes('video')) return text.includes('video') || text.includes('cinematic') || text.includes('film') || text.includes('vfx');
            if (cat.includes('image')) return text.includes('image') || text.includes('photo') || text.includes('still') || text.includes('portrait');
            if (cat.includes('fashion')) return text.includes('fashion') || text.includes('couture') || text.includes('textile') || text.includes('lookbook') || text.includes('style');
            if (cat.includes('3d') || cat.includes('cgi')) return text.includes('3d') || text.includes('cgi') || text.includes('spatial') || text.includes('render') || text.includes('blender');
            if (cat.includes('product')) return text.includes('product') || text.includes('ad') || text.includes('commercial') || text.includes('campaign');
            if (cat.includes('social')) return text.includes('social') || text.includes('reels') || text.includes('instagram') || text.includes('tiktok') || text.includes('content');
            if (cat.includes('animation')) return text.includes('animation') || text.includes('animated') || text.includes('motion') || text.includes('kinetic');
            if (cat.includes('graphic')) return text.includes('graphic') || text.includes('design') || text.includes('typography') || text.includes('branding') || text.includes('logo');
            if (cat.includes('audio') || cat.includes('voice')) return text.includes('audio') || text.includes('voice') || text.includes('sound') || text.includes('music') || text.includes('sonic');
            return text.includes(cat);
          });
        }
        if (params?.query && params.query.trim()) {
          const raw = params.query.toLowerCase().trim();
          const stopwords = ["find", "search", "looking", "for", "a", "an", "the", "in", "with", "me", "creator", "creators", "director", "directors"];
          const tokens = raw.split(/[\s,]+/).filter(w => !stopwords.includes(w) && w.length > 1);
          if (tokens.length > 0) {
            result = result.filter(c => {
              const text = `${c.name} ${c.specialization} ${c.location} ${c.hero_category || ''} ${c.tools_and_pipeline.join(' ')} ${c.bio || ''}`.toLowerCase();
              return tokens.some(t => {
                if (t === 'video') return text.includes('video') || text.includes('cinematic') || text.includes('film');
                if (t === 'image' || t === 'generation') return text.includes('image') || text.includes('photo') || text.includes('generative') || text.includes('midjourney');
                if (t === '3d') return text.includes('3d') || text.includes('cgi') || text.includes('render');
                if (t === 'fashion') return text.includes('fashion') || text.includes('couture') || text.includes('style');
                return text.includes(t);
              });
            });
          }
        }
        return result;
      }
    },
    getById: async (id: string): Promise<Creator> => {
      try {
        const data = await request<any>(`/creators/${id}`);
        return normalizeCreator(data);
      } catch {
        const found = creatorsStore.find(c => c.id === id);
        if (!found) return INITIAL_CREATORS[0];
        return found;
      }
    },
    getPortfolio: async (id: string) => {
      try {
        return await request<any>(`/creators/${id}/portfolio`);
      } catch {
        const c = creatorsStore.find(x => x.id === id);
        return c?.featured_works || [];
      }
    }
  },

  briefs: {
    create: async (data: Partial<Brief>): Promise<Brief> => {
      // Map frontend Brief shape to backend BriefCreate shape
      const payload = {
        title: data.title || 'Untitled Project',
        description: (data as any).prompt || data.objective || data.title || 'AI-generated project brief',
        prompt_text: (data as any).prompt || '',
        content_type: data.content_type || 'video',
        style: data.aesthetic || (data as any).style || '',
        target_audience: data.objective || '',
        platform: data.distribution_channels || [],
        duration: data.duration || '30 seconds',
        aspect_ratio: data.aspect_ratio || '9:16',
        deliverables: data.deliverables || [],
        tools_suggested: (data as any).tools_suggested || [],
        budget_min: (data as any).budget_min || 1000,
        budget_max: (data as any).budget_max || 5000,
        deadline: null,
        commercial_rights_required: true,
        status: 'published',
      };
      return await request<Brief>('/briefs', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    list: async (): Promise<Brief[]> => {
      try {
        return await request<Brief[]>('/briefs');
      } catch {
        return briefsStore;
      }
    },
    getById: async (id: string): Promise<Brief> => {
      try {
        return await request<Brief>(`/briefs/${id}`);
      } catch {
        const b = briefsStore.find(x => x.id === id);
        if (!b) throw new Error('Brief not found');
        return b;
      }
    },
    update: async (id: string, data: Partial<Brief>): Promise<Brief> => {
      try {
        return await request<Brief>(`/briefs/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data),
        });
      } catch {
        const idx = briefsStore.findIndex(b => b.id === id);
        if (idx !== -1) {
          briefsStore[idx] = { ...briefsStore[idx], ...data };
          return briefsStore[idx];
        }
        throw new Error('Brief not found');
      }
    },
    generate: async (payload: { prompt: string; style_tags?: string[]; duration?: string; aspect_ratio?: string }): Promise<any> => {
      // No try/catch fallback — errors propagate to the UI for display
      return await request<any>('/briefs/generate', {
        method: 'POST',
        body: JSON.stringify({ prompt: payload.prompt, additional_notes: '' }),
      });
    },
    recommendCreators: async (params: {
      category?: string;
      content_type?: string;
      style?: string;
      tools_suggested?: string[];
      budget?: number;
      budget_min?: number;
      budget_max?: number;
      timeline_days?: number;
      description?: string;
    }): Promise<RecommendedCreator[]> => {
      const res = await request<{
        recommended_category: string;
        total_matches: number;
        creators: Array<{
          creator: any;
          match_score: number;
          recommendation_reason: string;
          match_reasons: string[];
        }>;
      }>('/briefs/recommend-creators', {
        method: 'POST',
        body: JSON.stringify(params),
      });

      return (res.creators || []).map((item) => ({
        creator: normalizeCreator({ ...item.creator, compatibility_score: item.match_score }),
        match_score: item.match_score,
        recommendation_reason: item.recommendation_reason,
        match_reasons: item.match_reasons || [],
      }));
    },
    matchCreators: async (_briefId: string): Promise<Creator[]> => {
      try {
        const res = await request<any>(`/briefs/${_briefId}/match-creators`, { method: 'POST' });
        if (res?.matches && Array.isArray(res.matches)) {
          return res.matches.map((m: any) => normalizeCreator(m.creator));
        }
        return await api.creators.list();
      } catch {
        const all = await api.creators.list().catch(() => creatorsStore);
        return all.slice(0, 3);
      }
    }
  },

  xero: {
    chat: async (params: { message: string; session_id?: string }): Promise<XeroChatResponse> => {
      const res = await request<any>('/xero/chat', {
        method: 'POST',
        body: JSON.stringify(params),
      });

      return {
        ...res,
        recommended_creators: (res.recommended_creators || []).map((item: any) => ({
          creator: normalizeCreator({ ...item.creator, compatibility_score: item.match_score }),
          match_score: item.match_score,
          recommendation_reason: item.recommendation_reason,
          match_reasons: item.match_reasons || [],
        })),
      };
    },
    getSession: async (sessionId: string): Promise<XeroChatResponse> => {
      const res = await request<any>(`/xero/sessions/${sessionId}`);
      return {
        ...res,
        recommended_creators: (res.recommended_creators || []).map((item: any) => ({
          creator: normalizeCreator({ ...item.creator, compatibility_score: item.match_score }),
          match_score: item.match_score,
          recommendation_reason: item.recommendation_reason,
          match_reasons: item.match_reasons || [],
        })),
      };
    },
    saveBrief: async (sessionId: string, titleOverride?: string): Promise<Brief> => {
      return await request<Brief>('/xero/save-brief', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, title_override: titleOverride }),
      });
    },
  },


  community: {
    getPosts: async (postType?: string): Promise<CommunityPost[]> => {
      const qs = postType && postType !== 'All' ? `?post_type=${encodeURIComponent(postType)}` : '';
      const data = await request<any[]>(`/community/posts${qs}`);
      return data.map(normalizeCommunityPost);
    },
    createPost: async (data: {
      title?: string;
      body: string;
      post_type?: string;
      pipeline_badges?: string[];
      media_url?: string;
    }): Promise<CommunityPost> => {
      const postTypeMap: Record<string, string> = {
        'Showcase': 'showcase',
        'Hiring': 'hiring',
        'Offering Services': 'offering_services',
        'Looking For Creator': 'looking_for_creator',
        'Collaboration': 'collaboration',
        'Announcement': 'announcement',
        'Urgent Requirement': 'urgent_requirement',
        // Legacy fallbacks
        'Looking for creator': 'looking_for_creator',
        'Offering service': 'offering_services',
        'Open brief': 'hiring',
      };
      const typeKey = data.post_type || 'Showcase';
      const backendType = postTypeMap[typeKey] || typeKey.toLowerCase().replace(/\s+/g, '_');

      const payload = {
        title: data.title || (data.body.length > 50 ? data.body.slice(0, 47) + '...' : data.body) || 'Community Update',
        content: data.body,
        post_type: backendType,
        image_url: data.media_url || null,
        tools_tags: data.pipeline_badges || ['Midjourney v6', 'Runway Gen-3'],
      };
      const res = await request<any>('/community/posts', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      return normalizeCommunityPost(res);
    },
    likePost: async (id: string): Promise<{ success: boolean; likes_count: number; liked: boolean }> => {
      const res = await request<{ post_id: number; user_id: number; liked: boolean; likes_count: number }>(
        `/community/posts/${id}/like`,
        { method: 'POST' }
      );
      return { success: true, likes_count: res.likes_count, liked: res.liked };
    },
    commentOnPost: async (id: string, content: string): Promise<PostCommentItem> => {
      const res = await request<any>(`/community/posts/${id}/comment`, {
        method: 'POST',
        body: JSON.stringify({ content: content.trim() }),
      });
      return {
        id: res.id,
        post_id: res.post_id,
        user_id: res.user_id,
        content: res.content,
        created_at: formatRelativeTime(res.created_at),
        user_name: res.user?.full_name || 'User',
        user_role: res.user?.role === 'brand' ? 'Recruiter' : 'Content Creator',
        user_avatar: res.user?.avatar_url,
      };
    },
    getComments: async (id: string): Promise<PostCommentItem[]> => {
      const data = await request<any[]>(`/community/posts/${id}/comments`);
      return data.map((c: any) => ({
        id: c.id,
        post_id: c.post_id,
        user_id: c.user_id,
        content: c.content,
        created_at: formatRelativeTime(c.created_at),
        user_name: c.user?.full_name || 'User',
        user_role: c.user?.role === 'brand' ? 'Recruiter' : 'Content Creator',
        user_avatar: c.user?.avatar_url,
      }));
    },
    followUser: async (id: string): Promise<{ success: boolean; following: boolean; follower_count?: number }> => {
      const res = await request<any>(`/community/follow/${id}`, { method: 'POST' });
      return { success: true, following: res.following, follower_count: res.follower_count };
    },
    getFollowStatus: async (userId: string): Promise<{ user_id: number; follower_count: number; following_count: number; is_following: boolean }> => {
      return await request<any>(`/community/followers/${userId}`);
    },
    getMyFollowing: async (): Promise<number[]> => {
      return await request<number[]>('/community/following');
    },
  },

  workspaces: {
    list: async (): Promise<Workspace[]> => {
      try {
        const raw = await request<any[]>('/workspaces');
        return raw.map(normalizeWorkspace);
      } catch {
        // A new account must not see fake/default workspaces
        return [];
      }
    },
    getById: async (id: string): Promise<Workspace> => {
      try {
        const raw = await request<any>(`/workspaces/${id}`);
        return normalizeWorkspace(raw);
      } catch {
        const ws = workspacesStore.find(w => w.id === id);
        if (!ws) return workspacesStore[0];
        return ws;
      }
    },
    sendMessage: async (id: string, content: string, attachments?: any[]): Promise<any> => {
      try {
        return await request<any>(`/workspaces/${id}/messages`, {
          method: 'POST',
          body: JSON.stringify({ content, attachments })
        });
      } catch {
        const ws = workspacesStore.find(w => w.id === id);
        if (ws) {
          const msg = {
            id: 'msg-' + Date.now(),
            sender_id: 'current-user',
            sender_name: 'Recruiter',
            sender_role: 'brand' as const,
            content,
            created_at: 'Just now'
          };
          ws.messages.push(msg);
          return msg;
        }
      }
    },
    getMessages: async (id: string) => {
      try {
        return await request<any[]>(`/workspaces/${id}/messages`);
      } catch {
        const ws = workspacesStore.find(w => w.id === id);
        return ws?.messages || [];
      }
    },
    updateMilestone: async (workspaceId: string, milestoneId: string, status: 'completed' | 'in_progress' | 'pending' | 'released') => {
      const backendStatus = status === 'completed' ? 'released' : status;
      return await request<any>(`/workspaces/${workspaceId}/milestones/${milestoneId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: backendStatus })
      });
    },
    requestRevision: async (workspaceId: string, milestoneId: string | null, notes: string) => {
      return await request<any>(`/workspaces/${workspaceId}/revision-requests`, {
        method: 'POST',
        body: JSON.stringify({ milestone_id: milestoneId ? Number(milestoneId) : null, description: notes })
      });
    },
    uploadDeliverable: async (workspaceId: string, formData: FormData): Promise<any> => {
      const response = await fetch(`/api/workspaces/${workspaceId}/deliverables`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
        },
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(errData.detail || 'Failed to upload deliverable');
      }
      return await response.json();
    },
    completeProject: async (workspaceId: string): Promise<Workspace> => {
      const res = await request<any>(`/workspaces/${workspaceId}/complete`, {
        method: 'POST',
      });
      return normalizeWorkspace(res);
    },
    submitReview: async (workspaceId: string, rating: number, comment: string): Promise<any> => {
      return await request<any>(`/workspaces/${workspaceId}/review`, {
        method: 'POST',
        body: JSON.stringify({ rating, comment }),
      });
    },
    getCreatorReviews: async (creatorId: string): Promise<any[]> => {
      return await request<any[]>(`/workspaces/creators/${creatorId}/reviews`);
    },
  },

  shortlist: {
    add: async (creatorId: string, creatorUserId?: string) => {
      const numId = Number(creatorId);
      const numUserId = creatorUserId ? Number(creatorUserId) : undefined;
      return await request<any>('/shortlist', {
        method: 'POST',
        body: JSON.stringify({
          creator_id: creatorId,
          creator_profile_id: !isNaN(numId) ? numId : undefined,
          creator_user_id: numUserId,
        }),
      });
    },
    list: async (): Promise<Creator[]> => {
      const res = await request<any[]>('/shortlist');
      if (!Array.isArray(res)) return [];
      return res.map((item) => {
        const rawProfile = item.creator_profile || {};
        const rawUser = item.creator_user || {};
        const profileId = rawProfile.id != null ? String(rawProfile.id) : undefined;
        const userId = item.creator_user_id != null ? String(item.creator_user_id) : (rawUser.id != null ? String(rawUser.id) : undefined);
        const resolvedId = String(profileId || userId || item.id);
        const resolvedName = rawProfile.display_name || rawUser.full_name || 'Content Creator';
        return normalizeCreator({
          ...rawProfile,
          id: resolvedId,
          profile_id: profileId,
          user_id: userId,
          name: resolvedName,
          display_name: resolvedName,
          avatar: rawUser.avatar_url || rawProfile.avatar,
          rating: rawProfile.rating ?? 5.0,
          starting_rate: rawProfile.starting_rate || 1500,
          rate_per_day: rawProfile.starting_rate || 1500,
          specialization: rawProfile.specialization || rawProfile.tagline || 'AI Director & Artist',
          location: rawUser.location || 'Global',
        });
      });
    },
    remove: async (creatorId: string) => {
      return await request<any>(`/shortlist/${encodeURIComponent(creatorId)}`, {
        method: 'DELETE',
      });
    },
    hire: async (creatorId: string, briefId?: string) => {
      return await request<any>('/shortlist/hire', {
        method: 'POST',
        body: JSON.stringify({ creator_id: creatorId, brief_id: briefId }),
      });
    }
  },

  leaderboard: {
    get: async (params?: { month?: string }) => {
      const q = new URLSearchParams();
      if (params?.month) {
        q.append('month', params.month);
      }
      const qs = q.toString() ? `?${q.toString()}` : '';
      return request<any>(`/leaderboard${qs}`);
    },
    getSummary: async (month?: string) => {
      const qs = month ? `?month=${encodeURIComponent(month)}` : '';
      return request<any>(`/leaderboard/summary${qs}`);
    },
  },

  search: {
    searchCreators: async (query: string, filters?: any) => {
      return api.creators.list({ query, ...filters });
    }
  },

  proposals: {
    send: async (data: {
      creator_id?: string;
      creator_user_id?: number;
      creator_profile_id?: number;
      project_title: string;
      project_requirement: string;
      budget_in_rupees: number;
      deadline: string;
    }): Promise<Proposal> => {
      return await request<Proposal>('/proposals', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    list: async (): Promise<Proposal[]> => {
      return await request<Proposal[]>('/proposals');
    },
    accept: async (proposalId: number): Promise<Proposal> => {
      return await request<Proposal>(`/proposals/${proposalId}/accept`, {
        method: 'POST',
      });
    },
    decline: async (proposalId: number): Promise<Proposal> => {
      return await request<Proposal>(`/proposals/${proposalId}/decline`, {
        method: 'POST',
      });
    },
  },

  notifications: {
    list: async (): Promise<AppNotification[]> => {
      try {
        return await request<AppNotification[]>('/notifications');
      } catch {
        return [];
      }
    },
    markRead: async (id: number): Promise<any> => {
      try {
        return await request<any>(`/notifications/${id}/read`, { method: 'POST' });
      } catch {
        return { success: true };
      }
    },
    markAllRead: async (): Promise<any> => {
      try {
        return await request<any>('/notifications/mark-all-read', { method: 'POST' });
      } catch {
        return { success: true };
      }
    },
  },
};
