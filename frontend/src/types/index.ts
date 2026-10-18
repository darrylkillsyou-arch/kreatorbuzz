export interface User {
  id: string;
  email: string;
  name: string;
  role: 'brand' | 'creator';
  avatar_url?: string;
  company?: string;
  specialization?: string;
}

export interface Creator {
  id: string;
  profile_id?: string;
  user_id?: string;
  name: string;
  avatar: string;
  specialization: string;
  location: string;
  tier: string;
  is_verified: boolean;
  rating?: number;
  rate_per_day: number;
  sla_index: number;
  commissions_count: number;
  on_time_rate: number;
  compatibility_score?: number;
  velocity_days?: string;
  licensing?: string;
  tools_and_pipeline: string[];
  core_category?: string;
  sub_specializations?: string[];
  style_tags?: string[];
  hero_image: string;
  hero_title?: string;
  hero_category?: string;
  bio?: string;
  prompt_architecture?: string;
  featured_works?: Array<{
    title: string;
    image: string;
    aspect?: string;
    tag?: string;
  }>;
}

export interface RecommendedCreator {
  creator: Creator;
  match_score: number;
  recommendation_reason: string;
  match_reasons: string[];
}

export interface Brief {
  id: string;
  title: string;
  prompt?: string;
  objective?: string;
  content_type?: string;
  aesthetic?: string;
  aesthetic_desc?: string;
  style_tags: string[];
  distribution_channels?: string[];
  deliverables?: string[];
  aspect_ratio?: string;
  duration?: string;
  budget_range?: string;
  sla_timeline?: string;
  license_terms?: string;
  escrow_amount?: number;
  status?: string;
  created_at?: string;
}


export interface PostCommentItem {
  id: number;
  post_id: number;
  user_id: number;
  content: string;
  created_at: string;
  user_name: string;
  user_role?: string;
  user_avatar?: string;
}

export interface CommunityPost {
  id: string;
  author_id: string;
  author_name: string;
  author_avatar?: string;
  author_initial?: string;
  author_title: string;
  author_location: string;
  author_badge?: string;
  badge_class?: string;
  time_ago: string;
  title: string;
  body: string;
  post_type: 'Showcase' | 'Hiring' | 'Offering Services' | 'Looking For Creator' | 'Collaboration' | 'Announcement' | 'Urgent Requirement' | 'Looking for creator' | 'Offering service' | 'Open brief';
  pipeline_badges: string[];
  media_url?: string;
  media_caption?: string;
  prompt_notes?: string;
  likes_count: number;
  comments_count: number;
  is_liked?: boolean;
  is_hireable?: boolean;
  is_following_author?: boolean;
  creator_id?: string;
  comments?: PostCommentItem[];
}

export interface Milestone {
  id: string;
  step_number: number;
  title: string;
  description: string;
  status: 'completed' | 'in_progress' | 'pending';
  amount: number;
  payout_percentage: number;
  completion_date?: string;
}

export interface WorkspaceMessage {
  id: string;
  sender_id: string;
  sender_name: string;
  sender_avatar?: string;
  sender_role: 'brand' | 'creator' | 'system';
  content: string;
  created_at: string;
  attachments?: Array<{
    name: string;
    url: string;
    type: string;
  }>;
}

export interface WorkspaceDeliverable {
  id: string;
  milestone_id?: number | null;
  title: string;
  type: string;
  resolution: string;
  file_size: string;
  mime_type?: string;
  version: number;
  url: string;
  status: string;
  created_at?: string;
  uploader_id?: number;
  uploader_name?: string;
}

export interface WorkspaceReview {
  id: number;
  workspace_id: number;
  recruiter_user_id: number;
  creator_user_id: number;
  rating: number;
  comment: string;
  created_at: string;
  recruiter?: { id: number; full_name?: string; email?: string };
}

export interface Revision {
  id: number;
  milestone_id: number | null;
  workspace_id: number;
  requester_id: number;
  description: string;
  status: string;
  created_at: string;
  requester?: { id: number; full_name?: string; email?: string };
}

export interface Workspace {
  id: string;
  brief_id: string;
  brief_ref: string;
  title: string;
  description: string;
  status: string; // discovery, production, review, delivered, completed
  brand_id: string;
  brand_name: string;
  creator: Creator;
  total_budget: number;
  milestones: Milestone[];
  deliverables: WorkspaceDeliverable[];
  messages: WorkspaceMessage[];
  revisions: Revision[];
  review?: WorkspaceReview | null;
  unread_count: number;
  stage_tag: string;
  category_tag: string;
  created_at: string;
  completed_at?: string | null;
}

export interface MonthlySummaryStats {
  selected_month: string;
  completed_projects: number;
  active_creators: number;
  verified_reviews: number;
  average_verified_rating: number;
  deliverables_completed: number;
  source: string;
}

export interface CreatorMonthlyMetrics {
  completed_projects: number;
  verified_reviews_count: number;
  verified_rating?: number | null;
  released_milestones: number;
  revision_requests: number;
  revision_efficiency_pct: number;
  production_deliverables: number;
  community_posts: number;
}

export interface MonthlyRankedCreator {
  rank: number;
  creator_id: number;
  user_id: number;
  name: string;
  avatar?: string | null;
  hero_image?: string | null;
  primary_category: string;
  specialization: string;
  bio?: string | null;
  monthly_performance_score: number;
  rank_movement: string; // "+2", "-1", "=", or "NEW"
  badge?: string | null;
  explanation: string;
  profile_strength: number;
  metrics: CreatorMonthlyMetrics;
  creator_profile?: any;
}

export interface MonthlyAward {
  award_title: string;
  creator_id: number;
  creator_name: string;
  avatar?: string | null;
  category: string;
  score: number;
  reason: string;
}

export interface CategoryTopCreators {
  category: string;
  creators: MonthlyRankedCreator[];
}

export interface MonthlyLeaderboardData {
  selected_month: string;
  month_name: string;
  available_months: string[];
  summary: MonthlySummaryStats;
  top_10: MonthlyRankedCreator[];
  awards: MonthlyAward[];
  category_champions: CategoryTopCreators[];
  total_qualifying_creators: number;
}

// Backward compatibility aliases
export type LeaderboardStats = MonthlySummaryStats;
export type RankedCreator = MonthlyRankedCreator;
export type DynamicLeaderboardData = MonthlyLeaderboardData;

export interface Proposal {
  id: number;
  brand_user_id: number;
  creator_user_id: number;
  workspace_id?: number | null;
  project_title: string;
  project_requirement: string;
  budget_in_rupees: number;
  deadline: string;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
  recruiter_name?: string;
  creator_name?: string;
  creator_avatar?: string;
}

export interface AppNotification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  link?: string | null;
  type: string;
  is_read: boolean;
  created_at: string;
}

export interface XeroDeliverableItem {
  name: string;
  type: string;
  quantity: number;
  duration_seconds?: number | null;
  aspect_ratio?: string | null;
}

export interface XeroBudgetBreakdownItem {
  item: string;
  amount: number;
  percentage?: number | null;
}

export interface XeroMilestoneItem {
  step: number;
  title: string;
  description: string;
  duration_days: number;
  deliverable_ids?: string[];
}

export interface XeroProjectPlan {
  project_title: string;
  summary: string;
  objective: string;
  target_audience: string;
  creative_direction: string;
  core_category: string;
  specializations: string[];
  content_format: string;
  deliverables: XeroDeliverableItem[];
  duration?: string | null;
  platforms: string[];
  timeline_days: number;
  budget: number;
  budget_breakdown: XeroBudgetBreakdownItem[];
  milestones: XeroMilestoneItem[];
  preferred_tools: string[];
  style_direction: string[];
  risks_and_production_notes: string[];
  creator_requirements: string[];
  scope_warning?: string | null;
}

export interface XeroChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface XeroChatResponse {
  session_id: string;
  message: string;
  plan?: XeroProjectPlan | null;
  follow_up_questions: string[];
  recommended_creators: RecommendedCreator[];
  total_matching_creators: number;
  creator_offset: number;
  ai_provider_used: string;
  scope_warning?: string | null;
}

