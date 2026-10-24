import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import type {
  Creator,
  RecommendedCreator,
  XeroProjectPlan,
  XeroChatMessage,
  CreatorComparisonResult,
  BlindArenaData,
  CreatorCompareCardData,
} from '../types';
import { ProposalModal } from '../components/ProposalModal';
import { CreatorAvatar } from '../components/CreatorAvatar';
import { CreatorComparisonModal } from '../components/CreatorComparisonModal';
import { BlindArenaModal } from '../components/BlindArenaModal';

function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export const BriefsPage: React.FC = () => {
  const { user } = useAuth();
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Session & Conversation State
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem('xero_session_id') || '';
  });
  const [messages, setMessages] = useState<XeroChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [thinkingStage, setThinkingStage] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState('');

  // Structured Plan & Recommendations
  const [plan, setPlan] = useState<XeroProjectPlan | null>(null);
  const [followUps, setFollowUps] = useState<string[]>([]);
  const [recommendedCreators, setRecommendedCreators] = useState<RecommendedCreator[]>([]);
  const [totalMatches, setTotalMatches] = useState<number>(0);
  const [scopeWarning, setScopeWarning] = useState<string | null>(null);

  // Proposal / Hiring Modal
  const [proposalTarget, setProposalTarget] = useState<Creator | null>(null);

  // Save Brief State
  const [isSavingBrief, setIsSavingBrief] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [savedBriefId, setSavedBriefId] = useState<string | number | null>(null);

  // Phase 3: Creator Comparison & Blind Arena State
  const [selectedCreatorIds, setSelectedCreatorIds] = useState<number[]>([]);
  const [comparisonData, setComparisonData] = useState<CreatorComparisonResult | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [blindArenaData, setBlindArenaData] = useState<BlindArenaData | null>(null);
  const [isLoadingBlindArena, setIsLoadingBlindArena] = useState(false);

  const toggleSelectCreator = (id: number) => {
    setSelectedCreatorIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((cid) => cid !== id);
      }
      if (prev.length >= 3) {
        return [...prev.slice(1), id];
      }
      return [...prev, id];
    });
  };

  const handleOpenComparison = async () => {
    if (selectedCreatorIds.length < 2) return;
    setIsComparing(true);
    try {
      const res = await api.comparison.compare({
        creator_ids: selectedCreatorIds,
        target_category: plan?.core_category,
        budget: plan?.budget,
        timeline_days: plan?.timeline_days,
      });
      setComparisonData(res);
    } catch (err) {
      console.error('Failed to compare creators', err);
    } finally {
      setIsComparing(false);
    }
  };

  const handleOpenBlindArena = async () => {
    const idsToUse =
      selectedCreatorIds.length >= 2
        ? selectedCreatorIds
        : recommendedCreators
            .map((item) => Number(item.creator.id))
            .filter(Boolean)
            .slice(0, 3);

    if (idsToUse.length < 2) return;
    setIsLoadingBlindArena(true);
    try {
      const res = await api.comparison.createBlindArena({
        creator_ids: idsToUse,
        target_category: plan?.core_category,
        budget: plan?.budget,
        timeline_days: plan?.timeline_days,
      });
      setBlindArenaData(res);
    } catch (err) {
      console.error('Failed to open Blind Arena', err);
    } finally {
      setIsLoadingBlindArena(false);
    }
  };

  const handleHireFromModal = (card: CreatorCompareCardData) => {
    const mapped: Creator = {
      id: String(card.creator_id),
      profile_id: String(card.creator_id),
      user_id: String(card.user_id),
      name: card.display_name,
      avatar: card.avatar_url || '',
      specialization: card.specialization,
      location: 'Mumbai, IN',
      tier: 'Tier 1 Director',
      is_verified: true,
      rating: card.rating,
      rate_per_day: card.starting_rate,
      sla_index: card.sla_score,
      commissions_count: card.reliability.completed_projects,
      on_time_rate: card.reliability.on_time_percentage,
      tools_and_pipeline: card.ai_tools,
      hero_image: card.portfolio_samples[0]?.image_url || '',
    };
    setProposalTarget(mapped);
    setComparisonData(null);
    setBlindArenaData(null);
  };

  // Initial load: restore existing session if available
  useEffect(() => {
    if (sessionId) {
      api.xero
        .getSession(sessionId)
        .then((res) => {
          if (res.plan) {
            setPlan(res.plan);
            setRecommendedCreators(res.recommended_creators || []);
            setTotalMatches(res.total_matching_creators || 0);
            setScopeWarning(res.scope_warning || null);
          }
        })
        .catch(() => {
          // If session expired or invalid, clear it
          localStorage.removeItem('xero_session_id');
          setSessionId('');
        });
    }
  }, [sessionId]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinkingStage]);

  // Send message to Xero AI 2.0 copilot
  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isSending) return;

    setInputMessage('');
    setErrorMsg('');
    setIsSending(true);

    // Optimistically append user message to local chat
    const userMsg: XeroChatMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);

    // Progressive thinking status sequence
    setThinkingStage('Understanding your creative intent...');
    const stageTimer1 = setTimeout(() => {
      setThinkingStage('Structuring deliverables, budget & milestones...');
    }, 450);
    const stageTimer2 = setTimeout(() => {
      setThinkingStage('Matching verified creators from database...');
    }, 900);

    try {
      const res = await api.xero.chat({
        message: text,
        session_id: sessionId || undefined,
      });

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      setThinkingStage('');

      // Save/persist session
      if (res.session_id) {
        setSessionId(res.session_id);
        localStorage.setItem('xero_session_id', res.session_id);
      }

      // Add assistant response
      const assistantMsg: XeroChatMessage = {
        role: 'assistant',
        content: res.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Update project plan and creators if returned
      if (res.plan) {
        setPlan(res.plan);
      }
      setFollowUps(res.follow_up_questions || []);
      setRecommendedCreators(res.recommended_creators || []);
      setTotalMatches(res.total_matching_creators || 0);
      setScopeWarning(res.scope_warning || null);
    } catch (err: any) {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      setThinkingStage('');
      setErrorMsg(err.message || 'Failed to communicate with Xero AI Copilot.');
    } finally {
      setIsSending(false);
    }
  };

  // Quick follow-up chip click
  const handleFollowUpClick = (chipText: string) => {
    handleSendMessage(chipText);
  };

  // Quick refinement buttons
  const handleRefinementAction = (actionText: string) => {
    handleSendMessage(actionText);
  };

  // Save current project plan to real Brief record
  const handleSaveBrief = async () => {
    if (!sessionId || !plan) return;
    if (!user) {
      setErrorMsg('You must be signed in to save a project brief.');
      return;
    }
    setIsSavingBrief(true);
    setErrorMsg('');
    try {
      const saved = await api.xero.saveBrief(sessionId);
      setSavedBriefId(saved.id);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4500);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save project brief.');
    } finally {
      setIsSavingBrief(false);
    }
  };

  // Reset entire session
  const handleResetSession = () => {
    localStorage.removeItem('xero_session_id');
    setSessionId('');
    setMessages([]);
    setPlan(null);
    setFollowUps([]);
    setRecommendedCreators([]);
    setScopeWarning(null);
    setErrorMsg('');
    setSavedBriefId(null);
  };

  return (
    <div className="relative w-full px-gutter py-space-xl overflow-hidden min-h-[calc(100vh-80px)]">
      <div className="max-w-6xl mx-auto flex flex-col gap-space-lg relative z-10">
        
        {/* Toast Notification */}
        {saveSuccess && (
          <div className="fixed top-6 right-6 z-50 bg-secondary text-on-secondary px-space-lg py-space-sm rounded-xl shadow-lg flex items-center gap-2 animate-fade-in border border-outline-variant/30">
            <span className="material-symbols-outlined text-[20px]">check_circle</span>
            <span className="font-label-lg text-label-lg">
              Project Brief saved to database #{savedBriefId}!
            </span>
          </div>
        )}

        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pb-space-md border-b border-surface-container-high">
          <div className="max-w-2xl space-y-space-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
              <span className="font-label-sm text-label-sm uppercase tracking-widest text-secondary font-semibold">
                Xero AI 2.0 • Creative Project Copilot
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
              Turn your creative vision into an execution blueprint.
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">
              Converse naturally with Xero to architect deliverables, refine scope, allocate budgets in ₹, and match verified Tier-1 AI creators.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {plan && (
              <button
                type="button"
                onClick={handleResetSession}
                className="px-4 py-2 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface-variant hover:text-on-surface font-label-md transition-colors flex items-center gap-1.5 cursor-pointer border border-outline-variant/30 text-[13px]"
              >
                <span className="material-symbols-outlined text-[16px]">restart_alt</span>
                <span>New Project</span>
              </button>
            )}
            <div className="flex items-center gap-space-xs bg-surface-container-low px-space-md py-space-xs rounded-full border border-outline-variant/30">
              <span className="material-symbols-outlined text-secondary text-[18px]">auto_awesome</span>
              <span className="font-label-md text-label-md text-on-surface font-medium">Copilot Active</span>
            </div>
          </div>
        </div>

        {/* Scope Warning Alert Banner */}
        {scopeWarning && (
          <div className="p-space-md bg-amber-500/10 border border-amber-500/30 rounded-xl text-on-surface flex items-start gap-3 animate-fade-in shadow-sm">
            <span className="material-symbols-outlined text-amber-500 text-[22px] shrink-0 mt-0.5">warning</span>
            <div className="space-y-1">
              <h4 className="font-label-lg font-semibold text-amber-500">Scope & Budget Grounding Notice</h4>
              <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">{scopeWarning}</p>
            </div>
          </div>
        )}

        {/* Main 2-Column Responsive Layout: Left = Conversation & Composer, Right = Structured Project Card */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">

          {/* LEFT COLUMN: Conversation Copilot & Composer (5 cols on large screens or full if no plan) */}
          <div className={`${plan ? 'lg:col-span-5' : 'lg:col-span-12 max-w-3xl mx-auto w-full'} flex flex-col gap-space-md`}>
            
            {/* Conversation Window Card */}
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 shadow-sm flex flex-col h-[520px] overflow-hidden">
              
              {/* Card Header */}
              <div className="px-space-lg py-3 border-b border-surface-container flex items-center justify-between bg-surface-container-low/50">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[20px]">forum</span>
                  <span className="font-label-md font-semibold text-on-surface">Creative Conversation</span>
                </div>
                {sessionId && (
                  <span className="font-label-sm text-[11px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full font-mono">
                    {sessionId.slice(0, 14)}...
                  </span>
                )}
              </div>

              {/* Chat Message Stream */}
              <div className="flex-1 p-space-md overflow-y-auto space-y-3.5">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center p-space-lg text-on-surface-variant space-y-2">
                    <span className="material-symbols-outlined text-[36px] text-secondary/60">smart_toy</span>
                    <h3 className="font-headline-sm text-headline-sm text-on-surface">Tell KreatorBuzz about your creative vision</h3>
                    <p className="font-body-sm text-body-sm max-w-sm">
                      Describe your brand, style, budget, and desired outputs. KreatorBuzz Copilot asks follow-up questions only when needed and creates a complete project blueprint.
                    </p>
                    <div className="pt-2 flex flex-wrap gap-1.5 justify-center max-w-md">
                      {[
                        'Luxury perfume Instagram ad around ₹60,000',
                        'Hyperreal futuristic sneaker CGI campaign',
                        '3 Instagram reels for a skincare brand, ₹25k budget',
                        'Need AI voiceover & sound design for a 30s ad',
                      ].map((sample, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => handleSendMessage(sample)}
                          className="px-2.5 py-1 rounded-full bg-surface-container text-xs text-on-surface hover:bg-surface-container-high transition-colors text-left"
                        >
                          "{sample}"
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map((m, idx) => {
                    const isUser = m.role === 'user';
                    return (
                      <div
                        key={idx}
                        className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} gap-1`}
                      >
                        <div
                          className={`max-w-[88%] p-3.5 rounded-2xl text-[13px] leading-relaxed shadow-sm ${
                            isUser
                              ? 'bg-primary text-on-primary rounded-br-none'
                              : 'bg-surface-container-low text-on-surface border border-outline-variant/30 rounded-bl-none'
                          }`}
                        >
                          {m.content}
                        </div>
                        {m.timestamp && (
                          <span className="text-[10px] text-on-surface-variant px-1 font-mono">
                            {m.timestamp}
                          </span>
                        )}
                      </div>
                    );
                  })
                )}

                {/* Animated Progressive Thinking Indicator */}
                {isSending && thinkingStage && (
                  <div className="flex items-center gap-2.5 p-3 rounded-2xl bg-surface-container-low/70 border border-secondary/20 text-on-surface-variant animate-pulse max-w-[85%]">
                    <span className="material-symbols-outlined text-secondary text-[18px] animate-spin">
                      progress_activity
                    </span>
                    <span className="text-xs font-medium text-secondary">{thinkingStage}</span>
                  </div>
                )}

                <div ref={chatBottomRef} />
              </div>

              {/* Follow-up Questions Chips */}
              {followUps.length > 0 && !isSending && (
                <div className="p-space-sm bg-surface-container-low border-t border-surface-container flex flex-col gap-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-secondary px-1">
                    Suggested Next Clarifications
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {followUps.map((q, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleFollowUpClick(q)}
                        className="px-2.5 py-1 text-xs rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface transition-all text-left border border-outline-variant/30"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Refinements Bar (shown once a plan exists) */}
              {plan && !isSending && (
                <div className="p-2 bg-surface-container-low border-t border-surface-container flex items-center gap-1.5 overflow-x-auto no-scrollbar">
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant shrink-0 px-1">Refine:</span>
                  {[
                    'Make it cheaper',
                    'Make it more premium',
                    'Reduce timeline to 5 days',
                    'Make it more cinematic',
                    'Change it to still images',
                    'Show different creators',
                  ].map((act, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleRefinementAction(act)}
                      className="px-2 py-0.5 rounded-full bg-surface-container hover:bg-surface-container-high text-[11px] text-on-surface shrink-0 border border-outline-variant/20 transition-colors"
                    >
                      {act}
                    </button>
                  ))}
                </div>
              )}

              {/* Chat Input Box */}
              <div className="p-space-sm bg-surface-container-lowest border-t border-surface-container flex items-center gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder={
                    plan
                      ? 'Ask Copilot to refine: "Make it cheaper", "Add 2 reels", "Change timeline to 5 days"...'
                      : 'Describe your campaign: luxury perfume ad, sneaker 3D CGI, skincare reels...'
                  }
                  disabled={isSending}
                  className="flex-1 bg-surface-container-low text-on-surface text-sm rounded-full px-4 py-2.5 focus:outline-none focus:ring-1 focus:ring-secondary/50 border border-outline-variant/20 disabled:opacity-50"
                />
                <button
                  type="button"
                  onClick={() => handleSendMessage()}
                  disabled={isSending || !inputMessage.trim()}
                  className="w-10 h-10 rounded-full bg-primary hover:bg-primary-container text-on-primary flex items-center justify-center shrink-0 transition-all disabled:opacity-50 shadow-sm cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">send</span>
                </button>
              </div>
            </div>

            {errorMsg && (
              <div className="p-3 bg-error-container/40 text-on-error-container rounded-xl text-xs border border-error/20 flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">error</span>
                <span>{errorMsg}</span>
              </div>
            )}
          </div>

          {/* RIGHT COLUMN: Interactive Structured Project Plan & Matched Creators (7 cols) */}
          {plan && (
            <div className="lg:col-span-7 flex flex-col gap-space-lg animate-fade-in">

              {/* Project Card Master */}
              <div className="bg-surface-container-lowest rounded-2xl p-space-lg shadow-sm border border-outline-variant/30 flex flex-col gap-space-md">
                
                {/* Header with Title and Actions */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-space-sm border-b border-surface-container gap-2">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-label-sm text-xs bg-secondary-container/40 text-secondary px-2.5 py-0.5 rounded-full font-semibold">
                        {plan.core_category}
                      </span>
                      <span className="text-on-surface-variant text-xs">• {plan.content_format.toUpperCase()}</span>
                    </div>
                    <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                      {plan.project_title}
                    </h2>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={handleSaveBrief}
                      disabled={isSavingBrief}
                      className="px-4 py-2 rounded-full bg-primary hover:bg-primary-container text-on-primary font-label-md text-xs transition-all shadow-sm flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                    >
                      <span className="material-symbols-outlined text-[16px]">bookmark_add</span>
                      <span>{isSavingBrief ? 'Saving...' : 'Save as Brief'}</span>
                    </button>
                  </div>
                </div>

                {/* Summary & Objective */}
                <div className="p-3.5 bg-surface-container-low/60 rounded-xl space-y-1.5 text-xs leading-relaxed border border-outline-variant/15">
                  <p className="text-on-surface font-medium">{plan.summary}</p>
                  <p className="text-on-surface-variant">
                    <span className="font-semibold text-on-surface">Creative Direction:</span> {plan.creative_direction}
                  </p>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  <div className="p-3 rounded-xl bg-surface-container text-center">
                    <span className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Budget</span>
                    <p className="font-headline-sm font-bold text-secondary text-base mt-0.5">
                      {formatINR(plan.budget)}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-surface-container text-center">
                    <span className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Timeline</span>
                    <p className="font-headline-sm font-bold text-on-surface text-base mt-0.5">
                      {plan.timeline_days} Days
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-surface-container text-center">
                    <span className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Platforms</span>
                    <p className="font-label-md font-medium text-on-surface text-xs mt-1 truncate" title={plan.platforms.join(', ')}>
                      {plan.platforms.join(', ')}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-surface-container text-center">
                    <span className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Specialization</span>
                    <p className="font-label-md font-medium text-on-surface text-xs mt-1 truncate" title={plan.specializations.join(', ')}>
                      {plan.specializations[0] || plan.core_category}
                    </p>
                  </div>
                </div>

                {/* Deliverables List */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-label-sm uppercase tracking-wider font-semibold text-on-surface-variant text-xs">
                      Deliverables ({plan.deliverables.length})
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {plan.deliverables.map((deliv, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-surface-container-low border border-outline-variant/20 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[16px] text-secondary">
                            {deliv.type === 'video' ? 'movie' : deliv.type === 'image' ? 'image' : 'mic'}
                          </span>
                          <span className="font-medium text-on-surface">{deliv.name}</span>
                        </div>
                        <span className="font-label-sm text-[11px] bg-surface-container px-2 py-0.5 rounded-full text-on-surface-variant font-mono">
                          x{deliv.quantity}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Budget Breakdown & Production Milestones Accordion Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  
                  {/* Budget Allocation */}
                  <div className="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/20 space-y-2">
                    <span className="font-label-sm uppercase tracking-wider font-semibold text-secondary text-[11px] flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[15px]">account_balance_wallet</span>
                      Budget Allocation (₹)
                    </span>
                    <div className="space-y-1.5">
                      {plan.budget_breakdown.map((b, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs">
                          <span className="text-on-surface-variant truncate pr-2">{b.item}</span>
                          <span className="font-medium font-mono text-on-surface shrink-0">
                            ₹{b.amount.toLocaleString('en-IN')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Production Milestones */}
                  <div className="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/20 space-y-2">
                    <span className="font-label-sm uppercase tracking-wider font-semibold text-secondary text-[11px] flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[15px]">flag</span>
                      Production Milestones
                    </span>
                    <div className="space-y-1.5">
                      {plan.milestones.map((m) => (
                        <div key={m.step} className="flex items-start gap-2 text-xs">
                          <span className="w-4 h-4 rounded-full bg-secondary-container/50 text-secondary text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                            {m.step}
                          </span>
                          <div className="flex-1 min-w-0">
                            <span className="font-medium text-on-surface block truncate">{m.title}</span>
                            <span className="text-[10px] text-on-surface-variant">{m.duration_days} days</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Tools & Style Direction Tags */}
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider">Aesthetic:</span>
                  {plan.style_direction.map((s, idx) => (
                    <span key={idx} className="text-xs bg-surface-container px-2.5 py-0.5 rounded-full text-on-surface">
                      #{s.replace(/\s+/g, '')}
                    </span>
                  ))}
                  <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider ml-2">Tools:</span>
                  {plan.preferred_tools.map((t, idx) => (
                    <span key={idx} className="text-xs bg-secondary-container/20 text-secondary px-2.5 py-0.5 rounded-full font-medium">
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              {/* Matched Creators Section */}
              <div className="bg-surface-container-lowest rounded-2xl p-space-lg shadow-sm border border-outline-variant/30 flex flex-col gap-space-md">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-space-xs border-b border-surface-container">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-[20px]">verified</span>
                    <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                      Matched AI Creators ({totalMatches} candidates ranked)
                    </h3>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Enter Blind Arena Action */}
                    <button
                      type="button"
                      disabled={isLoadingBlindArena || recommendedCreators.length < 2}
                      onClick={handleOpenBlindArena}
                      className="px-3.5 py-1.5 rounded-full text-xs font-bold bg-secondary-container/30 hover:bg-secondary-container/50 text-secondary border border-secondary/40 flex items-center gap-1.5 cursor-pointer shadow-sm transition-all"
                      title="Anonymize profiles to evaluate purely on craft and portfolio evidence"
                    >
                      <span className="material-symbols-outlined text-[16px]">visibility_off</span>
                      <span>{isLoadingBlindArena ? 'Opening Arena...' : 'Enter Blind Arena'}</span>
                    </button>

                    {/* Compare Button */}
                    {selectedCreatorIds.length >= 2 && (
                      <button
                        type="button"
                        disabled={isComparing}
                        onClick={handleOpenComparison}
                        className="px-3.5 py-1.5 rounded-full text-xs font-bold bg-primary hover:bg-primary-container text-on-primary flex items-center gap-1.5 cursor-pointer shadow-sm transition-all"
                      >
                        <span className="material-symbols-outlined text-[16px]">compare_arrows</span>
                        <span>{isComparing ? 'Comparing...' : `Compare (${selectedCreatorIds.length})`}</span>
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => handleSendMessage('Show different creators')}
                      className="text-xs text-secondary hover:underline flex items-center gap-1 font-semibold cursor-pointer ml-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">sync</span>
                      <span>Next 3</span>
                    </button>
                  </div>
                </div>

                {/* Subtitle / Selection helper note */}
                {recommendedCreators.length > 0 && (
                  <div className="flex items-center justify-between text-[11px] text-on-surface-variant px-1">
                    <span>Select 2 or 3 creators to compare side-by-side with difference insights.</span>
                    {selectedCreatorIds.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setSelectedCreatorIds([])}
                        className="text-secondary hover:underline cursor-pointer"
                      >
                        Clear selection ({selectedCreatorIds.length})
                      </button>
                    )}
                  </div>
                )}

                {recommendedCreators.length === 0 ? (
                  <p className="text-xs text-on-surface-variant py-4 text-center">
                    No matching creators found for this specific budget and category combination.
                  </p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {recommendedCreators.map((item, idx) => {
                      const c = item.creator;
                      const cid = Number(c.id);
                      const isSelected = selectedCreatorIds.includes(cid);

                      return (
                        <div
                          key={c.id || idx}
                          className={`p-3.5 rounded-xl border flex flex-col justify-between gap-3 transition-all shadow-sm ${
                            isSelected
                              ? 'bg-surface-container-low border-secondary/60 ring-1 ring-secondary/40'
                              : 'bg-surface-container-low border-outline-variant/30 hover:border-secondary/40'
                          }`}
                        >
                          <div className="space-y-2">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <CreatorAvatar
                                  src={c.avatar}
                                  name={c.name}
                                  size="md"
                                />
                                <div>
                                  <h4 className="font-label-lg font-bold text-on-surface text-xs truncate max-w-[120px]">
                                    {c.name}
                                  </h4>
                                  <p className="text-[11px] text-on-surface-variant truncate max-w-[120px]">
                                    {c.specialization}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center gap-1.5 shrink-0">
                                <span className="text-[11px] bg-secondary-container/40 text-secondary font-bold px-2 py-0.5 rounded-full">
                                  {item.match_score}%
                                </span>
                                <button
                                  type="button"
                                  onClick={() => toggleSelectCreator(cid)}
                                  className={`w-6 h-6 rounded-md flex items-center justify-center transition-colors cursor-pointer ${
                                    isSelected
                                      ? 'bg-secondary text-on-secondary'
                                      : 'bg-surface-container hover:bg-surface-container-high text-on-surface-variant'
                                  }`}
                                  title={isSelected ? 'Deselect from comparison' : 'Select to compare (max 3)'}
                                >
                                  <span className="material-symbols-outlined text-[15px]">
                                    {isSelected ? 'check' : 'add'}
                                  </span>
                                </button>
                              </div>
                            </div>

                            {/* Rate in ₹ */}
                            <div className="flex items-center justify-between py-1 px-2 rounded bg-surface-container text-[11px]">
                              <span className="text-on-surface-variant">Day Rate</span>
                              <span className="font-bold text-secondary">
                                ₹{c.rate_per_day ? c.rate_per_day.toLocaleString('en-IN') : '25,000'}
                              </span>
                            </div>

                            {/* Recommendation Grounded Reason */}
                            <div className="p-2 rounded bg-secondary-container/10 border border-secondary/20 text-[11px] leading-snug text-on-surface italic">
                              "{item.recommendation_reason}"
                            </div>
                          </div>

                          {/* Action Buttons: Hire Creator reuses existing ProposalModal */}
                          <div className="grid grid-cols-2 gap-1.5 pt-2 border-t border-surface-container text-xs">
                            <Link
                              to={`/creators/${c.id}?match=${item.match_score}`}
                              className="py-1.5 text-center rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-medium transition-colors"
                            >
                              Profile
                            </Link>
                            <button
                              type="button"
                              onClick={() => setProposalTarget(c)}
                              className="py-1.5 rounded-full bg-primary hover:bg-primary-container text-on-primary font-medium text-center transition-all cursor-pointer shadow-sm"
                            >
                              Hire
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

        {/* Existing Working ProposalModal (Strict Creator Routing Guaranteed) */}
        {proposalTarget && (
          <ProposalModal
            creator={proposalTarget}
            onClose={() => setProposalTarget(null)}
          />
        )}

        {/* Creator Comparison Modal */}
        {comparisonData && (
          <CreatorComparisonModal
            candidates={comparisonData.candidates}
            differences={comparisonData.difference_explanations}
            summaryVerdict={comparisonData.summary_verdict}
            briefId={savedBriefId ? Number(savedBriefId) : undefined}
            onClose={() => setComparisonData(null)}
            onHire={handleHireFromModal}
          />
        )}

        {/* Blind Arena Modal */}
        {blindArenaData && (
          <BlindArenaModal
            candidates={blindArenaData.candidates}
            tagline={blindArenaData.tagline}
            briefId={savedBriefId ? Number(savedBriefId) : undefined}
            onClose={() => setBlindArenaData(null)}
            onHire={handleHireFromModal}
          />
        )}
      </div>
    </div>
  );
};
