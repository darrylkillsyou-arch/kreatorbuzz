import React, { useState } from 'react';
import type { Revision, Milestone } from '../../types';
import { api } from '../../lib/api';

interface RevisionFlowPanelProps {
  revisions: Revision[];
  milestones: Milestone[];
  workspaceId: string;
  isRecruiter: boolean;
  isCreator: boolean;
  onRequestRevisionClick: () => void;
  onRefresh: () => void;
}

export const RevisionFlowPanel: React.FC<RevisionFlowPanelProps> = ({
  revisions,
  milestones,
  workspaceId,
  isRecruiter,
  isCreator,
  onRequestRevisionClick,
  onRefresh,
}) => {
  const [activeRevId, setActiveRevId] = useState<number | null>(null);
  const [responseNotes, setResponseNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'requested':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-label-xs font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            Revision Requested
          </span>
        );
      case 'in_progress':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-label-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            In Progress
          </span>
        );
      case 'submitted':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-label-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center gap-1">
            <span className="material-symbols-outlined text-[13px]">upload</span>
            Revised Version Submitted
          </span>
        );
      case 'approved':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-label-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
            <span className="material-symbols-outlined text-[13px]">check_circle</span>
            Revision Approved
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-label-xs font-semibold bg-surface-container-high text-on-surface-variant">
            {status}
          </span>
        );
    }
  };

  const handleStartRevision = async (revId: number) => {
    setActionError(null);
    setIsSubmitting(true);
    try {
      await api.workspaces.updateRevisionStatus(
        workspaceId,
        revId,
        'in_progress',
        responseNotes.trim() || undefined
      );
      setActiveRevId(null);
      setResponseNotes('');
      onRefresh();
    } catch (err: any) {
      setActionError(err.message || 'Failed to start revision');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApproveRevision = async (revId: number) => {
    setActionError(null);
    setIsSubmitting(true);
    try {
      await api.workspaces.updateRevisionStatus(workspaceId, revId, 'approved');
      onRefresh();
    } catch (err: any) {
      setActionError(err.message || 'Failed to approve revision');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-surface-container-low rounded-2xl p-6 border border-surface-container-high/60 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-surface-container-high flex-wrap gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-amber-500">rule</span>
            <h3 className="font-title-md text-title-md text-on-surface">Structured Revision Requests</h3>
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
            Canonical revision workflow: Requested → In Progress → Submitted → Approved
          </p>
        </div>

        {isRecruiter && (
          <button
            onClick={onRequestRevisionClick}
            className="px-4 py-2 rounded-full bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md flex items-center gap-1.5 transition-colors cursor-pointer border border-surface-container-highest"
          >
            <span className="material-symbols-outlined text-[18px]">add_circle</span>
            <span>Request New Revision</span>
          </button>
        )}
      </div>

      {actionError && (
        <div className="p-3 bg-error-container text-on-error-container rounded-xl text-body-sm flex items-center justify-between">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="font-bold ml-2">✕</button>
        </div>
      )}

      {(!revisions || revisions.length === 0) ? (
        <div className="p-8 text-center bg-surface-container rounded-xl border border-surface-container-high/60">
          <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-2">task_alt</span>
          <p className="text-body-md text-on-surface-variant">No revision requests active.</p>
          <p className="text-label-sm text-on-surface-variant/70 mt-1">
            Deliverables are currently aligned with the confirmed brief.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {revisions.map((rev) => {
            const milestone = milestones.find((m) => Number(m.id) === rev.milestone_id);
            const canStart = isCreator && rev.status === 'requested';
            const canApprove = isRecruiter && rev.status !== 'approved';

            return (
              <div
                key={rev.id}
                className="bg-surface-container rounded-xl p-4 border border-surface-container-high space-y-3"
              >
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-2 flex-wrap">
                    {getStatusBadge(rev.status)}
                    {milestone && (
                      <span className="px-2 py-0.5 bg-surface-container-high text-on-surface-variant rounded-md font-label-xs">
                        Milestone: {milestone.title}
                      </span>
                    )}
                  </div>
                  <span className="font-label-xs text-on-surface-variant">{rev.created_at || 'Recently'}</span>
                </div>

                {/* Description */}
                <div className="text-body-sm text-on-surface bg-surface-container-low p-3 rounded-lg border border-surface-container-high/60">
                  <span className="font-semibold text-on-surface-variant block mb-1 text-xs">
                    Recruiter Request ({rev.requester?.full_name || 'Recruiter'}):
                  </span>
                  <p className="leading-relaxed">"{rev.description}"</p>
                </div>

                {/* Creator Response Note */}
                {rev.response_notes && (
                  <div className="text-body-sm text-on-surface bg-blue-500/5 p-3 rounded-lg border border-blue-500/20">
                    <span className="font-semibold text-blue-400 block mb-1 text-xs">
                      Creator Response:
                    </span>
                    <p className="italic">"{rev.response_notes}"</p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="pt-2 flex items-center justify-between gap-2 flex-wrap border-t border-surface-container-high/60">
                  <span className="text-label-xs text-on-surface-variant">
                    Revision ID: #{rev.id}
                  </span>

                  <div className="flex items-center gap-2">
                    {canStart && (
                      <button
                        disabled={isSubmitting}
                        onClick={() => {
                          setActiveRevId(activeRevId === rev.id ? null : rev.id);
                          setResponseNotes('');
                        }}
                        className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-label-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[14px]">play_arrow</span>
                        <span>Start Working on Revision</span>
                      </button>
                    )}

                    {canApprove && (
                      <button
                        disabled={isSubmitting}
                        onClick={() => handleApproveRevision(rev.id)}
                        className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-label-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[14px]">check</span>
                        <span>Approve Revision</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Inline Start Response Box for Creator */}
                {activeRevId === rev.id && (
                  <div className="p-3 bg-surface-container-low rounded-xl border border-surface-container-high space-y-2">
                    <label className="font-label-xs text-on-surface font-semibold block">
                      Optional Note to Recruiter (e.g. what adjustments you are preparing):
                    </label>
                    <input
                      type="text"
                      value={responseNotes}
                      onChange={(e) => setResponseNotes(e.target.value)}
                      placeholder="e.g. Working on color grading and audio pacing now..."
                      className="w-full px-3 py-1.5 text-xs bg-surface-container rounded-lg border border-surface-container-high text-on-surface focus:outline-hidden focus:border-primary"
                    />
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => setActiveRevId(null)}
                        className="px-2.5 py-1 text-xs text-on-surface-variant hover:text-on-surface font-medium cursor-pointer"
                      >
                        Cancel
                      </button>
                      <button
                        disabled={isSubmitting}
                        onClick={() => handleStartRevision(rev.id)}
                        className="px-3 py-1 text-xs bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50 cursor-pointer"
                      >
                        {isSubmitting ? 'Updating...' : 'Confirm In Progress'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
