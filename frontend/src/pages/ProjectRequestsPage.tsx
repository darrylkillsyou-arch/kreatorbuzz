import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import type { Proposal } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const ProjectRequestsPage: React.FC = () => {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<{ id: number; message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    setIsLoading(true);
    try {
      const data = await api.proposals.list();
      setProposals(data);
    } catch {
      setProposals([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccept = async (proposal: Proposal) => {
    setActionLoadingId(proposal.id);
    setFeedback(null);
    try {
      const updated = await api.proposals.accept(proposal.id);
      setProposals((prev) => prev.map((p) => (p.id === proposal.id ? updated : p)));
      setFeedback({
        id: proposal.id,
        message: 'Proposal accepted! Workspace has been created.',
        type: 'success',
      });
      // Optionally redirect to the newly created workspace
      if (updated.workspace_id) {
        setTimeout(() => {
          navigate(`/workspaces?id=${updated.workspace_id}`);
        }, 1200);
      }
    } catch (err: any) {
      setFeedback({
        id: proposal.id,
        message: err.message || 'Failed to accept proposal.',
        type: 'error',
      });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDecline = async (proposal: Proposal) => {
    setActionLoadingId(proposal.id);
    setFeedback(null);
    try {
      const updated = await api.proposals.decline(proposal.id);
      setProposals((prev) => prev.map((p) => (p.id === proposal.id ? updated : p)));
      setFeedback({
        id: proposal.id,
        message: 'Proposal declined. Recruiter has been notified.',
        type: 'success',
      });
    } catch (err: any) {
      setFeedback({
        id: proposal.id,
        message: err.message || 'Failed to decline proposal.',
        type: 'error',
      });
    } finally {
      setActionLoadingId(null);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading incoming project requests..." />;
  }

  // Filter proposals relevant to the creator
  const pendingProposals = proposals.filter((p) => p.status === 'pending');
  const pastProposals = proposals.filter((p) => p.status !== 'pending');

  return (
    <div className="max-w-7xl mx-auto px-gutter py-space-xl w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md mb-space-xl">
        <div className="space-y-space-xs">
          <div className="flex items-center gap-space-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold">
              Creator Inquiries
            </span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
            Project Requests & Proposals
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Review incoming hiring proposals from recruiters, accept projects to open collaboration workspaces, or decline.
          </p>
        </div>

        <div className="flex items-center gap-space-sm">
          <Link
            to="/workspaces"
            className="px-space-md py-2.5 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">folder</span>
            <span>View Workspaces</span>
          </Link>
        </div>
      </div>

      {/* Pending Proposals Section */}
      <div className="space-y-space-md mb-space-xl">
        <div className="flex items-center justify-between pb-space-xs border-b border-outline-variant/30">
          <h2 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
            <span>Pending Requests</span>
            {pendingProposals.length > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-xs font-semibold">
                {pendingProposals.length} New
              </span>
            )}
          </h2>
        </div>

        {pendingProposals.length === 0 ? (
          <div className="bg-surface-container-low rounded-2xl p-space-xl text-center border border-outline-variant/30 space-y-3">
            <div className="w-12 h-12 rounded-full bg-surface-container-high text-on-surface-variant mx-auto flex items-center justify-center">
              <span className="material-symbols-outlined text-[24px]">inbox</span>
            </div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface">No pending project requests</h3>
            <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto">
              When recruiters discover your profile and click Hire Creator, their proposal details and budget will appear right here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-space-md">
            {pendingProposals.map((proposal) => (
              <div
                key={proposal.id}
                className="bg-surface-container-low rounded-2xl p-space-lg border border-outline-variant/40 shadow-sm flex flex-col md:flex-row justify-between gap-space-lg group hover:border-outline-variant transition-all"
              >
                <div className="space-y-3 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="px-2.5 py-0.5 rounded-full bg-secondary/15 text-secondary font-label-sm text-xs uppercase tracking-wider font-semibold">
                      Pending Approval
                    </span>
                    <span className="font-label-sm text-on-surface-variant text-xs">
                      Received {new Date(proposal.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-headline-md text-headline-md text-on-surface font-semibold tracking-tight">
                      {proposal.project_title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1 text-on-surface-variant font-label-md">
                      <span className="material-symbols-outlined text-[16px] text-secondary">business</span>
                      <span>From: <strong className="text-on-surface font-semibold">{proposal.recruiter_name || 'Recruiter'}</strong></span>
                    </div>
                  </div>

                  <div className="bg-surface-container/60 rounded-xl p-space-md border border-outline-variant/20">
                    <span className="font-label-sm text-[11px] uppercase tracking-wider text-on-surface-variant block font-semibold mb-1">
                      Project Requirement
                    </span>
                    <p className="font-body-md text-body-md text-on-surface leading-relaxed whitespace-pre-line">
                      {proposal.project_requirement}
                    </p>
                  </div>

                  {/* Budget & Deadline telemetry */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1">
                    <div className="bg-surface-container rounded-lg p-3">
                      <span className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant block">
                        Offered Budget
                      </span>
                      <span className="font-headline-sm text-[18px] text-secondary font-bold block mt-0.5">
                        ₹{Number(proposal.budget_in_rupees).toLocaleString('en-IN')}
                      </span>
                    </div>

                    <div className="bg-surface-container rounded-lg p-3">
                      <span className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant block">
                        Target Deadline
                      </span>
                      <span className="font-headline-sm text-[16px] text-on-surface font-semibold block mt-0.5">
                        {proposal.deadline}
                      </span>
                    </div>

                    <div className="bg-surface-container rounded-lg p-3 col-span-2 sm:col-span-1">
                      <span className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant block">
                        Workspace
                      </span>
                      <span className="font-body-sm text-xs text-on-surface-variant block mt-1">
                        Auto-created upon acceptance
                      </span>
                    </div>
                  </div>

                  {feedback && feedback.id === proposal.id && (
                    <div
                      className={`p-3 rounded-lg text-body-sm ${
                        feedback.type === 'success'
                          ? 'bg-secondary-container/40 text-on-secondary-container'
                          : 'bg-error-container/40 text-on-error-container'
                      }`}
                    >
                      {feedback.message}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex md:flex-col justify-end gap-space-sm flex-shrink-0 pt-space-xs md:pt-0 border-t md:border-t-0 md:border-l border-outline-variant/30 md:pl-space-lg">
                  <button
                    type="button"
                    disabled={actionLoadingId === proposal.id}
                    onClick={() => handleAccept(proposal)}
                    className="flex-1 md:flex-initial px-space-lg py-2.5 rounded-full bg-primary text-on-primary font-label-lg hover:bg-primary-container hover:text-on-surface transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[18px]">check</span>
                    <span>{actionLoadingId === proposal.id ? 'Accepting...' : 'Accept'}</span>
                  </button>

                  <button
                    type="button"
                    disabled={actionLoadingId === proposal.id}
                    onClick={() => handleDecline(proposal)}
                    className="flex-1 md:flex-initial px-space-lg py-2.5 rounded-full bg-surface-container hover:bg-error-container hover:text-on-error-container text-on-surface font-label-lg transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[18px]">close</span>
                    <span>Decline</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Past Proposals History */}
      {pastProposals.length > 0 && (
        <div className="space-y-space-md">
          <div className="pb-space-xs border-b border-outline-variant/30">
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Past Requests History
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-space-sm">
            {pastProposals.map((proposal) => (
              <div
                key={proposal.id}
                className="bg-surface-container-low rounded-xl p-space-md border border-outline-variant/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-space-md"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-headline-sm text-headline-sm text-on-surface font-medium">
                      {proposal.project_title}
                    </h4>
                    <span
                      className={`px-2 py-0.5 rounded-full font-label-sm text-[10px] uppercase font-bold tracking-wider ${
                        proposal.status === 'accepted'
                          ? 'bg-secondary/20 text-secondary'
                          : 'bg-surface-container-high text-on-surface-variant'
                      }`}
                    >
                      {proposal.status}
                    </span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
                    Recruiter: {proposal.recruiter_name} • Budget: ₹{Number(proposal.budget_in_rupees).toLocaleString('en-IN')}
                  </p>
                </div>

                {proposal.status === 'accepted' && proposal.workspace_id && (
                  <Link
                    to={`/workspaces?id=${proposal.workspace_id}`}
                    className="px-space-md py-1.5 rounded-full bg-secondary/15 hover:bg-secondary/25 text-secondary font-label-md transition-colors flex items-center gap-1.5"
                  >
                    <span>Open Workspace</span>
                    <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
