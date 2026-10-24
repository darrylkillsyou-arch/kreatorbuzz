import React, { useState } from 'react';
import type { WorkspaceDeliverable, Milestone } from '../../types';
import { api } from '../../lib/api';
import { BuzzCheckCard } from './BuzzCheckCard';

interface DeliverableVersionHistoryProps {
  deliverables: WorkspaceDeliverable[];
  milestones: Milestone[];
  workspaceId: string;
  isRecruiter: boolean;
  onRefresh: () => void;
}

export const DeliverableVersionHistory: React.FC<DeliverableVersionHistoryProps> = ({
  deliverables,
  milestones,
  workspaceId,
  isRecruiter,
  onRefresh,
}) => {
  const [feedbackFileId, setFeedbackFileId] = useState<string | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  if (!deliverables || deliverables.length === 0) {
    return (
      <div className="p-8 text-center bg-surface-container-low rounded-2xl border border-surface-container-high/60">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-2">upload_file</span>
        <p className="text-body-md text-on-surface-variant">No deliverable versions uploaded yet.</p>
        <p className="text-label-sm text-on-surface-variant/70 mt-1">
          When the creator uploads deliverables, each version (V1, V2, etc.) is preserved with an immutable audit log.
        </p>
      </div>
    );
  }

  // Group deliverables by milestone
  const msMap = new Map<number | null, WorkspaceDeliverable[]>();
  for (const d of deliverables) {
    const key = d.milestone_id ?? null;
    if (!msMap.has(key)) msMap.set(key, []);
    msMap.get(key)!.push(d);
  }

  const handleApprove = async (fileId: string) => {
    setActionError(null);
    setIsSubmitting(true);
    try {
      await api.workspaces.submitDeliverableFeedback(workspaceId, fileId, {
        status: 'approved',
      });
      onRefresh();
    } catch (err: any) {
      setActionError(err.message || 'Failed to approve deliverable');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSendFeedback = async (fileId: string) => {
    if (!feedbackText.trim()) return;
    setActionError(null);
    setIsSubmitting(true);
    try {
      await api.workspaces.submitDeliverableFeedback(workspaceId, fileId, {
        client_feedback: feedbackText.trim(),
        status: 'feedback_given',
      });
      setFeedbackText('');
      setFeedbackFileId(null);
      onRefresh();
    } catch (err: any) {
      setActionError(err.message || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {actionError && (
        <div className="p-3 bg-error-container text-on-error-container rounded-xl text-body-sm flex items-center justify-between">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="font-bold ml-2">✕</button>
        </div>
      )}

      {Array.from(msMap.entries()).map(([msId, files]) => {
        const milestone = milestones.find((m) => String(m.id) === String(msId));
        const milestoneTitle = milestone ? milestone.title : 'General / Kickoff Deliverables';

        // Sort versions descending (V3, V2, V1)
        const sortedFiles = [...files].sort((a, b) => (b.version || 1) - (a.version || 1));

        return (
          <div key={String(msId)} className="bg-surface-container-low rounded-2xl p-6 border border-surface-container-high/60">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-surface-container-high flex-wrap gap-2">
              <div>
                <span className="font-label-xs text-primary font-semibold uppercase tracking-wider block">Milestone Deliverable Track</span>
                <h4 className="font-title-sm text-title-sm text-on-surface font-semibold">{milestoneTitle}</h4>
              </div>
              <span className="px-2.5 py-0.5 bg-surface-container-high rounded-full font-label-xs text-on-surface-variant">
                {sortedFiles.length} {sortedFiles.length === 1 ? 'version' : 'versions'}
              </span>
            </div>

            <div className="space-y-4">
              {sortedFiles.map((file) => {
                const isCurrent = file.is_current ?? (file.version === sortedFiles[0].version);
                const isApproved = file.status === 'approved';

                return (
                  <div
                    key={file.id}
                    className={`rounded-xl p-4 transition-all border ${
                      isCurrent
                        ? 'bg-surface-container border-primary/40 ring-1 ring-primary/20'
                        : 'bg-surface-container/60 border-surface-container-high opacity-85 hover:opacity-100'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 flex-wrap">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        {/* Version Badge */}
                        <span className="px-2.5 py-1 bg-surface-container-highest font-bold text-xs rounded-md text-on-surface">
                          V{file.version || 1}
                        </span>

                        {/* Current vs Previous Tag */}
                        {isCurrent ? (
                          <span className="px-2 py-0.5 bg-primary/10 text-primary font-semibold text-label-xs rounded-full border border-primary/30 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                            Current Version
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 bg-surface-container-high text-on-surface-variant font-label-xs rounded-full">
                            Previous Version
                          </span>
                        )}

                        {/* Approved Badge */}
                        {isApproved && (
                          <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 font-semibold text-label-xs rounded-full border border-emerald-500/30 flex items-center gap-1">
                            <span className="material-symbols-outlined text-[14px]">check_circle</span>
                            Approved
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="font-label-xs text-on-surface-variant">{file.file_size}</span>
                        <a
                          href={file.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1 bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded-lg font-label-xs font-medium flex items-center gap-1 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[14px]">download</span>
                          Download
                        </a>
                      </div>
                    </div>

                    {/* File Meta */}
                    <div className="mt-3 flex items-center gap-2 font-medium text-body-sm text-on-surface">
                      <span className="material-symbols-outlined text-[18px] text-primary">attachment</span>
                      <span>{file.title}</span>
                      <span className="font-label-xs text-on-surface-variant font-normal">
                        • Uploaded by {file.uploader_name || 'Creator'} on {file.created_at || 'Recently'}
                      </span>
                    </div>

                    {/* Creator Note */}
                    {file.description && (
                      <div className="mt-2.5 text-xs bg-surface-container-low p-2.5 rounded-lg border border-surface-container-high">
                        <span className="font-semibold text-on-surface-variant block mb-0.5">Creator Note:</span>
                        <p className="text-on-surface italic">"{file.description}"</p>
                      </div>
                    )}

                    {/* Recruiter Feedback */}
                    {file.client_feedback && (
                      <div className="mt-2.5 text-xs bg-primary/5 p-2.5 rounded-lg border border-primary/20">
                        <span className="font-semibold text-primary block mb-0.5">Recruiter Feedback:</span>
                        <p className="text-on-surface">"{file.client_feedback}"</p>
                      </div>
                    )}

                    {/* Buzz Check Result */}
                    {file.buzz_check && (
                      <BuzzCheckCard
                        buzzCheck={file.buzz_check}
                        version={file.version || 1}
                        filename={file.title}
                      />
                    )}

                    {/* Recruiter Actions */}
                    {isRecruiter && (
                      <div className="mt-3 pt-3 border-t border-surface-container-high/60 flex items-center justify-between gap-2 flex-wrap">
                        <div className="flex items-center gap-2">
                          <button
                            disabled={isSubmitting}
                            onClick={() => {
                              setFeedbackFileId(feedbackFileId === file.id ? null : file.id);
                              setFeedbackText(file.client_feedback || '');
                            }}
                            className="px-3 py-1 rounded-lg bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-xs font-medium flex items-center gap-1 transition-colors cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-[14px]">rate_review</span>
                            <span>{file.client_feedback ? 'Update Feedback' : 'Leave Version Feedback'}</span>
                          </button>
                        </div>

                        {!isApproved && (
                          <button
                            disabled={isSubmitting}
                            onClick={() => handleApprove(file.id)}
                            className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-label-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-[14px]">done_all</span>
                            <span>Approve Version</span>
                          </button>
                        )}
                      </div>
                    )}

                    {/* Inline Feedback Box for Recruiter */}
                    {feedbackFileId === file.id && (
                      <div className="mt-3 p-3 bg-surface-container-low rounded-xl border border-surface-container-high">
                        <label className="font-label-xs text-on-surface font-semibold block mb-1">
                          Feedback for V{file.version || 1}:
                        </label>
                        <textarea
                          rows={2}
                          value={feedbackText}
                          onChange={(e) => setFeedbackText(e.target.value)}
                          placeholder="e.g. Lighting looks great, but shorten opening hook by 1 second."
                          className="w-full px-3 py-2 text-xs bg-surface-container rounded-lg border border-surface-container-high text-on-surface focus:outline-hidden focus:border-primary"
                        />
                        <div className="mt-2 flex items-center justify-end gap-2">
                          <button
                            onClick={() => setFeedbackFileId(null)}
                            className="px-2.5 py-1 text-xs text-on-surface-variant hover:text-on-surface font-medium cursor-pointer"
                          >
                            Cancel
                          </button>
                          <button
                            disabled={isSubmitting || !feedbackText.trim()}
                            onClick={() => handleSendFeedback(file.id)}
                            className="px-3 py-1 text-xs bg-primary text-on-primary font-semibold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 cursor-pointer"
                          >
                            {isSubmitting ? 'Saving...' : 'Submit Feedback'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};
