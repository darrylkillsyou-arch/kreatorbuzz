import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import type { Workspace, Milestone } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const WorkspacesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWs, setSelectedWs] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'deliverables' | 'chat' | 'assets' | 'legal'>('deliverables');
  const [chatMessage, setChatMessage] = useState('');
  const [revisionNotes, setRevisionNotes] = useState('');
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [targetMilestoneForRevision, setTargetMilestoneForRevision] = useState<Milestone | null>(null);

  // Deliverable Upload State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadMilestoneId, setUploadMilestoneId] = useState<string>('');
  const [uploadDescription, setUploadDescription] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Review State
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewRating, setReviewRating] = useState<number>(5);
  const [reviewComment, setReviewComment] = useState<string>('');
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);

  // Completion State
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    setIsLoading(true);
    try {
      const list = await api.workspaces.list();
      setWorkspaces(list);
      const queryId = searchParams.get('id');
      const current = queryId ? list.find((w) => w.id === queryId) || list[0] : list[0];
      setSelectedWs(current || null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !selectedWs) return;
    await api.workspaces.sendMessage(selectedWs.id, chatMessage);
    const updated = await api.workspaces.getById(selectedWs.id);
    setSelectedWs(updated);
    setChatMessage('');
  };

  const handleApproveMilestone = async (milestoneId: string) => {
    if (!selectedWs) return;
    try {
      await api.workspaces.updateMilestone(selectedWs.id, milestoneId, 'completed');
      const updated = await api.workspaces.getById(selectedWs.id);
      setSelectedWs(updated);
      alert('Milestone approved. Escrow tranche released to creator.');
    } catch (err: any) {
      alert(`Failed to approve milestone: ${err.message || 'Unknown error'}`);
    }
  };

  const handleRequestRevision = async () => {
    if (!selectedWs || !revisionNotes.trim()) return;
    try {
      await api.workspaces.requestRevision(
        selectedWs.id,
        targetMilestoneForRevision?.id ?? null,
        revisionNotes.trim()
      );
      const updated = await api.workspaces.getById(selectedWs.id);
      setSelectedWs(updated);
      setShowRevisionModal(false);
      setRevisionNotes('');
      setTargetMilestoneForRevision(null);
      alert('Revision request submitted and creator has been notified.');
    } catch (err: any) {
      alert(`Failed to submit revision request: ${err.message || 'Unknown error'}`);
    }
  };

  const handleUploadDeliverable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWs || !uploadFile) {
      setUploadError('Please select a file to upload.');
      return;
    }
    setIsUploading(true);
    setUploadError(null);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      if (uploadMilestoneId) {
        formData.append('milestone_id', uploadMilestoneId);
      }
      if (uploadDescription.trim()) {
        formData.append('description', uploadDescription.trim());
      }

      await api.workspaces.uploadDeliverable(selectedWs.id, formData);
      const updated = await api.workspaces.getById(selectedWs.id);
      setSelectedWs(updated);
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadDescription('');
      setUploadMilestoneId('');
      alert('Deliverable uploaded successfully.');
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload deliverable.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleCompleteProject = async () => {
    if (!selectedWs) return;
    if (!confirm('Are you sure you want to mark this project as fully completed?')) return;
    setIsCompleting(true);
    try {
      const updated = await api.workspaces.completeProject(selectedWs.id);
      setSelectedWs(updated);
      // update list
      setWorkspaces((prev) => prev.map((w) => (w.id === updated.id ? updated : w)));
      alert('Project marked as completed! You can now leave a verified creator review.');
    } catch (err: any) {
      alert(`Cannot complete project: ${err.message || 'Unknown error'}`);
    } finally {
      setIsCompleting(false);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWs) return;
    setIsSubmittingReview(true);
    setReviewError(null);
    try {
      await api.workspaces.submitReview(selectedWs.id, reviewRating, reviewComment.trim());
      const updated = await api.workspaces.getById(selectedWs.id);
      setSelectedWs(updated);
      setShowReviewModal(false);
      setReviewComment('');
      alert('Verified review submitted successfully! It is now permanently linked to the creator profile.');
    } catch (err: any) {
      setReviewError(err.message || 'Failed to submit review.');
    } finally {
      setIsSubmittingReview(false);
    }
  };

  const { user } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Opening project workspaces..." />;
  }

  if (workspaces.length === 0 || !selectedWs) {
    return (
      <div className="max-w-7xl mx-auto w-full px-gutter py-space-xl">
        <div className="space-y-space-xs mb-space-xl">
          <div className="flex items-center gap-space-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold">
              Project Workspaces
            </span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
            Workspaces
          </h1>
        </div>

        <div className="bg-surface-container-low rounded-2xl p-space-xl text-center border border-outline-variant/30 max-w-xl mx-auto space-y-4 shadow-sm">
          <div className="w-14 h-14 rounded-full bg-surface-container-high text-secondary mx-auto flex items-center justify-center">
            <span className="material-symbols-outlined text-[28px]">workspaces</span>
          </div>
          <h2 className="font-headline-md text-headline-md text-on-surface">No active workspaces yet</h2>
          <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
            {user?.role === 'creator'
              ? 'When a recruiter sends you a project proposal and you accept it, your private collaboration workspace will automatically be created here.'
              : 'When you hire a creator and they accept your proposal, a dedicated workspace with milestones and secure messaging will automatically be created here.'}
          </p>
          <div className="pt-2 flex flex-wrap items-center justify-center gap-space-sm">
            {user?.role === 'creator' ? (
              <Link
                to="/requests"
                className="px-space-lg py-2.5 rounded-full bg-primary text-on-primary font-label-lg hover:bg-primary-container hover:text-on-surface transition-all shadow-sm"
              >
                View Project Requests
              </Link>
            ) : (
              <Link
                to="/discover"
                className="px-space-lg py-2.5 rounded-full bg-primary text-on-primary font-label-lg hover:bg-primary-container hover:text-on-surface transition-all shadow-sm"
              >
                Explore Creators
              </Link>
            )}
          </div>
        </div>
      </div>
    );
  }

  const completedCount = selectedWs.milestones.filter((m) => m.status === 'completed').length;
  const progressPercent = Math.round((completedCount / (selectedWs.milestones.length || 1)) * 100);
  const allMilestonesApproved = selectedWs.milestones.length > 0 && completedCount === selectedWs.milestones.length;

  return (
    <div className="flex flex-col w-full">
      {/* Context Header */}
      <section className="max-w-7xl mx-auto w-full px-gutter pt-space-lg pb-space-md">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pb-space-md">
          <div className="space-y-space-xs max-w-2xl">
            <div className="flex items-center gap-space-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold">
                Project Workspaces
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
              Recruiter & Creator Workspaces
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Manage production rooms, milestone reviews, approvals, and usage rights in one place.
            </p>
          </div>
          <div className="flex items-center gap-space-sm flex-shrink-0">
            {user?.role === 'creator' && (
              <Link
                to="/requests"
                className="px-space-md py-2.5 rounded-full bg-secondary/15 text-secondary hover:bg-secondary/25 transition-colors flex items-center gap-space-xs shadow-sm font-label-lg"
              >
                <span className="material-symbols-outlined text-[18px]">inbox</span>
                <span>Project Requests</span>
              </Link>
            )}
            <button className="px-space-md py-2.5 rounded-full bg-surface-container-high text-on-surface font-label-lg text-label-lg hover:bg-surface-container-highest transition-colors flex items-center gap-space-xs shadow-sm cursor-pointer">
              <span className="material-symbols-outlined text-[18px]">tune</span>
              <span>Room Settings</span>
            </button>
            <button
              onClick={() => alert('To open a new production room, generate a brief or hire a creator.')}
              className="px-space-md py-2.5 rounded-full bg-primary text-on-primary font-label-lg text-label-lg hover:bg-primary-container hover:text-on-surface transition-all flex items-center gap-space-xs shadow-sm cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              <span>New workspace</span>
            </button>
          </div>
        </div>
      </section>

      {/* Two-Column Split */}
      <section className="max-w-7xl mx-auto w-full px-gutter pb-space-xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter items-start">
          {/* Left Column: Sidebar */}
          <aside className="lg:col-span-4 flex flex-col gap-space-md">
            <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-outline-variant/30">
              <div className="flex items-center justify-between pb-space-sm mb-space-sm border-b border-surface-container-high">
                <div className="flex items-center gap-space-xs">
                  <span className="font-label-md text-label-md uppercase tracking-wider text-on-surface font-semibold">
                    Active Production Rooms
                  </span>
                  <span className="bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm px-2 py-0.5 rounded-full">
                    {workspaces.length}
                  </span>
                </div>
              </div>

              <div className="space-y-space-xs">
                {workspaces.map((ws) => {
                  const isSelected = ws.id === selectedWs.id;
                  return (
                    <div
                      key={ws.id}
                      onClick={() => setSelectedWs(ws)}
                      className={`group relative p-space-md rounded-lg cursor-pointer transition-all border ${
                        isSelected
                          ? 'bg-surface-container-lowest shadow-sm border-secondary/40'
                          : 'bg-surface-container hover:bg-surface-container-high border-transparent'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-space-xs mb-space-xs">
                        <span className="font-label-sm text-label-sm text-secondary uppercase tracking-widest font-semibold truncate">
                          {ws.category_tag}
                        </span>
                        {ws.unread_count > 0 && (
                          <span className="inline-flex items-center gap-1 text-[11px] font-label-sm font-semibold text-on-surface bg-secondary-fixed/40 px-2 py-0.5 rounded-full">
                            {ws.unread_count} unread
                          </span>
                        )}
                      </div>
                      <h2 className="font-headline-sm text-headline-sm text-on-surface leading-snug group-hover:text-secondary transition-colors">
                        {ws.creator.name}
                      </h2>
                      <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 truncate">
                        {ws.title}
                      </p>
                      <div className="mt-space-sm pt-space-xs flex items-center justify-between">
                        <span className="inline-flex items-center gap-1.5 text-on-surface font-label-sm text-label-sm bg-surface-container-high px-2.5 py-1 rounded-full">
                          <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
                          {ws.stage_tag}
                        </span>
                        <span className="font-label-sm text-label-sm text-on-surface-variant font-semibold">
                          ₹{ws.total_budget.toLocaleString('en-IN')} Total
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Escrow Guarantee Widget */}
            <div className="bg-surface-container rounded-xl p-space-md space-y-space-xs border border-outline-variant/30">
              <div className="flex items-center gap-space-xs text-secondary">
                <span className="material-symbols-outlined text-[20px]">verified_user</span>
                <span className="font-label-md text-label-md uppercase tracking-wider text-on-surface font-semibold">
                  Smart Escrow Protection
                </span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                Client funds stay in CODE XERO escrow. Payments release only after you approve each milestone.
              </p>
            </div>
          </aside>

          {/* Right Column: Room Details */}
          <main className="lg:col-span-8 flex flex-col gap-space-md">
            {/* Project Header Banner Card */}
            <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-outline-variant/30">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-space-md">
                <div className="space-y-space-xs">
                  <div className="flex items-center gap-space-xs flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full bg-secondary-fixed/50 text-on-secondary-fixed text-label-sm font-label-sm uppercase tracking-wide">
                      Project #{selectedWs.brief_ref}
                    </span>
                    <span className="text-on-surface-variant font-label-sm text-label-sm">
                      Initiated {selectedWs.created_at}
                    </span>
                  </div>
                  <h2 className="font-display text-[32px] md:text-display text-on-surface tracking-tight leading-tight">
                    {selectedWs.title}
                  </h2>
                  <p className="font-body-md text-body-md text-on-surface-variant max-w-xl">
                    {selectedWs.description}
                  </p>
                </div>

                {/* Creator Mini Card */}
                <div className="bg-surface-container-lowest p-space-md rounded-xl flex items-center gap-space-sm shadow-sm flex-shrink-0 border border-outline-variant/20">
                  <div className="relative w-12 h-12 rounded-full overflow-hidden bg-surface-container-high flex-shrink-0">
                    <img
                      className="w-full h-full object-cover"
                      alt={selectedWs.creator.name}
                      src={selectedWs.creator.avatar || selectedWs.creator.hero_image}
                    />
                  </div>
                  <div>
                    <div className="flex items-center gap-1">
                      <span className="font-label-lg text-label-lg text-on-surface font-semibold">
                        {selectedWs.creator.name}
                      </span>
                      <span className="material-symbols-outlined text-[16px] text-secondary">verified</span>
                    </div>
                    <span className="font-body-sm text-body-sm text-on-surface-variant block">
                      Lead Content Creator
                    </span>
                    <button
                      onClick={() => setActiveTab('chat')}
                      className="mt-1 font-label-sm text-label-sm text-secondary hover:text-on-surface uppercase tracking-wider transition-colors flex items-center gap-0.5 cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[14px]">forum</span>
                      <span>Direct Message</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Project Status & Completion Controls Banner */}
              {selectedWs.status === 'completed' ? (
                <div className="mt-space-md p-space-md bg-secondary-fixed/30 rounded-xl border border-secondary/40 flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
                  <div className="flex items-center gap-space-sm">
                    <div className="w-10 h-10 rounded-full bg-secondary text-on-secondary flex items-center justify-center flex-shrink-0">
                      <span className="material-symbols-outlined text-[24px]">verified</span>
                    </div>
                    <div>
                      <h3 className="font-headline-sm text-headline-sm text-on-surface">Project Successfully Completed</h3>
                      <p className="font-body-sm text-body-sm text-on-surface-variant">
                        All milestones approved and escrow released. Completed on {selectedWs.completed_at || 'Recently'}.
                      </p>
                    </div>
                  </div>
                  {user?.role === 'brand' && !selectedWs.review && (
                    <button
                      onClick={() => setShowReviewModal(true)}
                      className="px-space-md py-2 rounded-full bg-primary text-on-primary font-label-md hover:bg-primary-container hover:text-on-surface transition-all flex items-center gap-1.5 shadow-sm flex-shrink-0 cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[18px]">rate_review</span>
                      <span>Leave Creator Review</span>
                    </button>
                  )}
                  {selectedWs.review && (
                    <div className="px-3 py-1.5 rounded-full bg-surface-container font-label-sm text-secondary font-semibold flex items-center gap-1 flex-shrink-0">
                      <span className="material-symbols-outlined text-[16px]">star</span>
                      <span>Reviewed: {selectedWs.review.rating}★</span>
                    </div>
                  )}
                </div>
              ) : (
                allMilestonesApproved && (
                  <div className="mt-space-md p-space-md bg-primary-fixed/20 rounded-xl border border-primary/30 flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
                    <div>
                      <h4 className="font-headline-sm text-[16px] text-on-surface">All Milestones Approved</h4>
                      <p className="font-body-sm text-body-sm text-on-surface-variant">
                        All deliverables and payments have been released. Ready to close this collaboration.
                      </p>
                    </div>
                    {user?.role === 'brand' && (
                      <button
                        onClick={handleCompleteProject}
                        disabled={isCompleting}
                        className="px-space-md py-2 rounded-full bg-primary text-on-primary font-label-md hover:bg-primary-container transition-all flex items-center gap-1.5 shadow-sm flex-shrink-0 cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[18px]">check_circle</span>
                        <span>{isCompleting ? 'Completing...' : 'Mark Project Completed'}</span>
                      </button>
                    )}
                  </div>
                )
              )}

              {/* Escrow Milestone Progress Stepper */}
              <div className="mt-space-lg pt-space-md bg-surface-container-high/40 -mx-space-lg -mb-space-lg p-space-lg rounded-b-xl border-t border-outline-variant/20">
                <div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-space-xs">
                  <span className="text-on-surface font-semibold">Escrow Milestone Progress</span>
                  <span>Overall: {progressPercent}% Fulfilled</span>
                </div>
                <div className="grid grid-cols-4 gap-2 pt-space-xs">
                  {selectedWs.milestones.map((m, idx) => (
                    <div key={m.id} className="flex flex-col gap-1.5">
                      <div
                        className={`h-1.5 w-full rounded-full ${
                          m.status === 'completed'
                            ? 'bg-primary'
                            : m.status === 'in_progress'
                            ? 'bg-secondary animate-pulse'
                            : 'bg-surface-container-highest'
                        }`}
                      />
                      <span className="font-label-sm text-[10px] text-on-surface truncate">
                        Step {idx + 1}: {m.title.split(' ')[0]}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Workspace Tabs Navigation & Actions */}
            <div className="flex items-center justify-between border-b border-surface-container-high pb-2 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                {[
                  { id: 'deliverables', label: 'Milestone Deliverables' },
                  { id: 'chat', label: 'Room Chat' },
                  { id: 'assets', label: `Shared Files (${selectedWs.deliverables.length})` },
                  { id: 'legal', label: 'Usage Rights' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`px-4 py-2 font-label-md text-label-md rounded-full transition-colors cursor-pointer ${
                      activeTab === tab.id
                        ? 'bg-primary text-on-primary'
                        : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Upload Deliverable button for Creator */}
              {user?.role === 'creator' && selectedWs.status !== 'completed' && (
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="px-4 py-2 rounded-full bg-secondary text-on-secondary font-label-md hover:bg-secondary/90 transition-all flex items-center gap-1.5 shadow-sm cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">cloud_upload</span>
                  <span>Upload Deliverable</span>
                </button>
              )}
            </div>

            {/* Tab: Deliverables */}
            {activeTab === 'deliverables' && (
              <div className="space-y-space-md">
                {selectedWs.milestones.map((milestone) => {
                  const milestoneFiles = selectedWs.deliverables.filter(
                    (d) => String(d.milestone_id) === String(milestone.id)
                  );
                  return (
                    <div
                      key={milestone.id}
                      className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 flex flex-col gap-space-sm shadow-sm"
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span
                              className={`w-2.5 h-2.5 rounded-full ${
                                milestone.status === 'completed'
                                  ? 'bg-secondary'
                                  : milestone.status === 'in_progress'
                                  ? 'bg-secondary-container animate-pulse'
                                  : 'bg-outline'
                              }`}
                            />
                            <span className="font-label-sm text-label-sm uppercase text-secondary font-semibold">
                              Milestone #{milestone.step_number}
                            </span>
                            <span className="font-label-sm text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full">
                              ₹{Number(milestone.amount).toLocaleString('en-IN')} ({milestone.payout_percentage}%)
                            </span>
                          </div>
                          <h3 className="font-headline-sm text-[19px] text-on-surface">
                            {milestone.title}
                          </h3>
                          <p className="font-body-sm text-body-sm text-on-surface-variant">
                            {milestone.description}
                          </p>
                        </div>

                        <div className="flex items-center gap-2 flex-shrink-0">
                          {milestone.status === 'completed' ? (
                            <span className="inline-flex items-center gap-1 text-secondary font-label-md bg-secondary-fixed/40 px-3 py-1 rounded-full">
                              <span className="material-symbols-outlined text-[16px]">check</span>
                              Approved & Escrow Released
                            </span>
                          ) : milestone.status === 'in_progress' ? (
                            <>
                              <button
                                onClick={() => { setTargetMilestoneForRevision(milestone); setShowRevisionModal(true); }}
                                className="px-3 py-1.5 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-sm cursor-pointer"
                              >
                                Request Revision
                              </button>
                              <button
                                onClick={() => handleApproveMilestone(milestone.id)}
                                className="px-4 py-1.5 rounded-full bg-primary text-on-primary font-label-sm hover:bg-primary-container hover:text-on-surface transition-all cursor-pointer shadow-sm"
                              >
                                Approve & Release Funds
                              </button>
                            </>
                          ) : (
                            <span className="text-on-surface-variant font-label-sm uppercase">Pending</span>
                          )}
                        </div>
                      </div>

                      {/* Submitted Deliverables for this Milestone */}
                      {milestoneFiles.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-surface-container-high space-y-2">
                          <span className="font-label-sm text-[11px] text-on-surface-variant uppercase font-semibold block">
                            Milestone Deliverable Files ({milestoneFiles.length}):
                          </span>
                          <div className="grid grid-cols-1 gap-2">
                            {milestoneFiles.map((file) => (
                              <div
                                key={file.id}
                                className="flex items-center justify-between p-2.5 rounded-lg bg-surface-container-low border border-outline-variant/20 hover:border-secondary/40 transition-all"
                              >
                                <div className="flex items-center gap-2.5">
                                  <span className="material-symbols-outlined text-[20px] text-secondary">
                                    {file.type === 'image' ? 'image' : file.type === 'video' ? 'movie' : file.type === 'zip' ? 'folder_zip' : 'description'}
                                  </span>
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <span className="font-label-md text-on-surface font-medium">{file.title}</span>
                                      <span className="px-2 py-0.2 rounded-full bg-secondary-fixed/50 text-[10px] text-on-secondary-fixed font-semibold uppercase">
                                        v{file.version}
                                      </span>
                                    </div>
                                    <span className="font-body-sm text-[11px] text-on-surface-variant block">
                                      {file.file_size} · Uploaded by {file.uploader_name} {file.created_at ? `(${file.created_at})` : ''}
                                    </span>
                                  </div>
                                </div>

                                <a
                                  href={file.url}
                                  download={file.title}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="px-3 py-1 rounded-full bg-surface-container-high text-on-surface font-label-sm hover:bg-secondary hover:text-on-secondary transition-all flex items-center gap-1 shadow-sm"
                                >
                                  <span className="material-symbols-outlined text-[16px]">download</span>
                                  <span>Download</span>
                                </a>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Open Revision Requests — shown in Deliverables tab */}
            {activeTab === 'deliverables' && selectedWs.revisions && selectedWs.revisions.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">Revision Requests</h4>
                {selectedWs.revisions.map((rev) => {
                  const linkedMilestone = selectedWs.milestones.find((m) => String(m.id) === String(rev.milestone_id));
                  return (
                    <div key={rev.id} className="bg-surface-container-low rounded-xl p-space-sm border border-outline-variant/30 flex flex-col gap-1">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[16px] text-error">edit_note</span>
                          <span className="font-label-sm text-label-sm text-on-surface font-semibold">
                            {linkedMilestone ? `Revision on: ${linkedMilestone.title}` : 'Workspace Revision'}
                          </span>
                        </div>
                        <span className={`font-label-sm px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                          rev.status === 'open' ? 'bg-error/10 text-error' :
                          rev.status === 'addressed' ? 'bg-secondary-fixed/30 text-secondary' :
                          'bg-surface-container-high text-on-surface-variant'
                        }`}>{rev.status.toUpperCase()}</span>
                      </div>
                      <p className="font-body-sm text-body-sm text-on-surface leading-snug">{rev.description}</p>
                      <span className="font-body-sm text-[10px] text-on-surface-variant">
                        {rev.requester?.full_name || 'Requester'} · {rev.created_at}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Tab: Chat */}
            {activeTab === 'chat' && (
              <div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 space-y-space-md shadow-sm">
                <div className="space-y-space-sm max-h-96 overflow-y-auto pr-2">
                  {selectedWs.messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`p-space-sm rounded-lg max-w-xl ${
                        msg.sender_role === 'system'
                          ? 'bg-surface-container mx-auto text-center'
                          : msg.sender_role === 'brand'
                          ? 'bg-surface-container-high ml-auto'
                          : 'bg-surface border border-outline-variant/30'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="font-label-sm text-on-surface font-semibold">{msg.sender_name}</span>
                        <span className="font-body-sm text-[10px] text-on-surface-variant">{msg.created_at}</span>
                      </div>
                      <p className="font-body-sm text-body-sm text-on-surface">{msg.content}</p>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2 pt-2 border-t border-surface-container">
                  <input
                    type="text"
                    placeholder="Write a message to the creator..."
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1 bg-surface-container-low text-on-surface px-4 py-2 rounded-full border border-outline-variant/30 focus:outline-none focus:border-secondary"
                  />
                  <button
                    onClick={handleSendMessage}
                    className="px-5 py-2 bg-primary text-on-primary font-label-md rounded-full hover:bg-primary-container transition-all cursor-pointer shadow-sm"
                  >
                    Send
                  </button>
                </div>
              </div>
            )}

            {/* Tab: Assets */}
            {activeTab === 'assets' && (
              <div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 space-y-space-sm shadow-sm">
                <div className="flex items-center justify-between">
                  <h3 className="font-headline-sm text-headline-sm text-on-surface">Verified Deliverables & Files</h3>
                  {user?.role === 'creator' && selectedWs.status !== 'completed' && (
                    <button
                      onClick={() => setShowUploadModal(true)}
                      className="px-3 py-1.5 rounded-full bg-secondary text-on-secondary font-label-sm hover:bg-secondary/90 transition-all flex items-center gap-1 shadow-sm cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[16px]">upload_file</span>
                      <span>Upload File</span>
                    </button>
                  )}
                </div>

                {selectedWs.deliverables.length === 0 ? (
                  <p className="font-body-sm text-body-sm text-on-surface-variant py-4 text-center">
                    No deliverables have been submitted in this workspace yet.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {selectedWs.deliverables.map((del) => (
                      <div
                        key={del.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-surface-container-low border border-outline-variant/20 hover:border-secondary/40 transition-all"
                      >
                        <div className="flex items-center gap-3">
                          <span className="material-symbols-outlined text-[24px] text-secondary">
                            {del.type === 'image' ? 'image' : del.type === 'video' ? 'movie' : del.type === 'zip' ? 'folder_zip' : 'description'}
                          </span>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-label-md text-on-surface block font-medium">{del.title}</span>
                              <span className="px-2 py-0.2 rounded-full bg-secondary-fixed/50 text-[10px] text-on-secondary-fixed font-semibold uppercase">
                                v{del.version}
                              </span>
                              {del.status === 'demo' && (
                                <span className="px-2 py-0.2 rounded-full bg-surface-container-high text-[10px] text-on-surface-variant font-semibold uppercase">
                                  Demo Asset
                                </span>
                              )}
                            </div>
                            <span className="font-body-sm text-[12px] text-on-surface-variant">
                              {del.file_size} · Uploaded by {del.uploader_name} {del.created_at ? `(${del.created_at})` : ''}
                            </span>
                          </div>
                        </div>

                        {del.status !== 'demo' ? (
                          <a
                            href={del.url}
                            download={del.title}
                            target="_blank"
                            rel="noreferrer"
                            className="px-3 py-1 rounded-full bg-surface-container-high text-on-surface font-label-sm hover:bg-secondary hover:text-on-secondary transition-all flex items-center gap-1 shadow-sm"
                          >
                            <span className="material-symbols-outlined text-[16px]">download</span>
                            <span>Download</span>
                          </a>
                        ) : (
                          <span className="font-label-sm text-xs text-on-surface-variant bg-surface-container px-2.5 py-1 rounded-full">
                            Placeholder Preview
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab: Legal */}
            {activeTab === 'legal' && (
              <div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 space-y-space-sm shadow-sm">
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Usage Rights</h3>
                <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
                  After the final escrow payment is released, commercial usage rights transfer to {selectedWs.brand_name}. Project files remain stored securely in the CODE XERO archive.
                </p>
              </div>
            )}
          </main>
        </div>
      </section>

      {/* Revision Request Modal */}
      {showRevisionModal && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest max-w-lg w-full rounded-2xl p-space-lg shadow-2xl border border-outline-variant/30 space-y-space-md">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">Request Milestone Revision</h3>
            {targetMilestoneForRevision && (
              <p className="font-label-sm text-label-sm text-secondary bg-secondary-fixed/20 px-3 py-1.5 rounded-lg">
                Milestone: {targetMilestoneForRevision.title}
              </p>
            )}
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Describe the specific adjustments needed for the creator.
            </p>
            <textarea
              rows={4}
              value={revisionNotes}
              onChange={(e) => setRevisionNotes(e.target.value)}
              placeholder="e.g., Please tone down the rim lighting intensity on the car windshield between 0:08 and 0:14..."
              className="w-full bg-surface text-on-surface p-space-sm rounded-lg border border-outline-variant focus:outline-none focus:border-secondary text-body-sm"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setShowRevisionModal(false); setRevisionNotes(''); setTargetMilestoneForRevision(null); }}
                className="px-4 py-2 rounded-full bg-surface-container text-on-surface font-label-md"
              >
                Cancel
              </button>
              <button
                onClick={handleRequestRevision}
                className="px-5 py-2 rounded-full bg-primary text-on-primary font-label-md hover:bg-primary-container"
              >
                Submit Request
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Deliverable Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest max-w-lg w-full rounded-2xl p-space-lg shadow-2xl border border-outline-variant/30 space-y-space-md">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Upload Project Deliverable</h3>
              <button
                onClick={() => { setShowUploadModal(false); setUploadError(null); setUploadFile(null); }}
                className="text-on-surface-variant hover:text-on-surface"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Submit an image, video, document, or archive asset to this workspace. Supported formats: JPG, PNG, WEBP, PDF, MP4, MOV, ZIP (max 50 MB).
            </p>

            {uploadError && (
              <div className="p-3 bg-error/10 border border-error/30 rounded-lg text-error text-body-sm">
                {uploadError}
              </div>
            )}

            <form onSubmit={handleUploadDeliverable} className="space-y-4">
              <div>
                <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold mb-1">
                  Target Milestone (Optional)
                </label>
                <select
                  value={uploadMilestoneId}
                  onChange={(e) => setUploadMilestoneId(e.target.value)}
                  className="w-full bg-surface text-on-surface p-2.5 rounded-lg border border-outline-variant focus:outline-none focus:border-secondary text-body-sm"
                >
                  <option value="">General Project Deliverable</option>
                  {selectedWs.milestones.map((m) => (
                    <option key={m.id} value={m.id}>
                      Milestone #{m.step_number}: {m.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold mb-1">
                  Select File
                </label>
                <input
                  type="file"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setUploadFile(e.target.files[0]);
                      setUploadError(null);
                    }
                  }}
                  accept=".jpg,.jpeg,.png,.webp,.pdf,.mp4,.mov,.zip"
                  className="w-full text-body-sm text-on-surface file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-label-sm file:bg-primary file:text-on-primary hover:file:bg-primary-container cursor-pointer"
                />
              </div>

              <div>
                <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold mb-1">
                  Deliverable Notes / Version Remarks
                </label>
                <textarea
                  rows={3}
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  placeholder="e.g., Final 4K color-graded master render with ProRes export settings..."
                  className="w-full bg-surface text-on-surface p-2.5 rounded-lg border border-outline-variant focus:outline-none focus:border-secondary text-body-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => { setShowUploadModal(false); setUploadError(null); setUploadFile(null); }}
                  className="px-4 py-2 rounded-full bg-surface-container text-on-surface font-label-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading || !uploadFile}
                  className="px-5 py-2 rounded-full bg-primary text-on-primary font-label-md hover:bg-primary-container disabled:opacity-50 cursor-pointer shadow-sm"
                >
                  {isUploading ? 'Uploading...' : 'Upload Asset'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Leave Creator Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest max-w-lg w-full rounded-2xl p-space-lg shadow-2xl border border-outline-variant/30 space-y-space-md">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Leave Verified Creator Review</h3>
              <button
                onClick={() => { setShowReviewModal(false); setReviewError(null); }}
                className="text-on-surface-variant hover:text-on-surface"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Share your verified project feedback for <strong>{selectedWs.creator.name}</strong>. This review will be permanently displayed on their public creator profile.
            </p>

            {reviewError && (
              <div className="p-3 bg-error/10 border border-error/30 rounded-lg text-error text-body-sm">
                {reviewError}
              </div>
            )}

            <form onSubmit={handleSubmitReview} className="space-y-4">
              <div>
                <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold mb-2">
                  Overall Rating
                </label>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setReviewRating(star)}
                      className={`text-[28px] transition-colors cursor-pointer ${
                        star <= reviewRating ? 'text-secondary' : 'text-surface-container-highest'
                      }`}
                    >
                      ★
                    </button>
                  ))}
                  <span className="ml-2 font-label-md font-semibold text-on-surface">
                    {reviewRating} out of 5 Stars
                  </span>
                </div>
              </div>

              <div>
                <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold mb-1">
                  Written Feedback
                </label>
                <textarea
                  rows={4}
                  required
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="e.g., Exceptional creative execution! The kinetic cuts and prompt consistency exceeded our campaign standards..."
                  className="w-full bg-surface text-on-surface p-2.5 rounded-lg border border-outline-variant focus:outline-none focus:border-secondary text-body-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => { setShowReviewModal(false); setReviewError(null); }}
                  className="px-4 py-2 rounded-full bg-surface-container text-on-surface font-label-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingReview || reviewComment.trim().length < 5}
                  className="px-5 py-2 rounded-full bg-primary text-on-primary font-label-md hover:bg-primary-container disabled:opacity-50 cursor-pointer shadow-sm"
                >
                  {isSubmittingReview ? 'Submitting...' : 'Post Verified Review'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
