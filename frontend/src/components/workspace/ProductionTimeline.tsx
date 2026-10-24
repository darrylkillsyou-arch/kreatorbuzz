import React from 'react';
import type { ProductionTimelineItem } from '../../types';

interface ProductionTimelineProps {
  items: ProductionTimelineItem[];
  workspaceId?: string;
}

export const ProductionTimeline: React.FC<ProductionTimelineProps> = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <div className="p-8 text-center bg-surface-container-low rounded-2xl border border-surface-container-high/60">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-2">timeline</span>
        <p className="text-body-md text-on-surface-variant">No production timeline events recorded yet.</p>
        <p className="text-label-sm text-on-surface-variant/70 mt-1">Upload a deliverable or request a revision to begin the collaboration history.</p>
      </div>
    );
  }

  // Display newest events first for active workflow monitoring, or chronological
  const sortedItems = [...items].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="bg-surface-container-low rounded-2xl p-6 border border-surface-container-high/60">
      <div className="flex items-center justify-between mb-6 pb-3 border-b border-surface-container-high">
        <div>
          <h3 className="font-title-md text-title-md text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">history_toggle_off</span>
            Production & Version Timeline
          </h3>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
            Immutable version log tracking uploads, recruiter revisions, and approvals
          </p>
        </div>
        <span className="px-3 py-1 bg-surface-container-high rounded-full font-label-sm text-label-sm text-on-surface-variant">
          {items.length} {items.length === 1 ? 'event' : 'events'}
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-3 before:bottom-3 before:w-[2px] before:bg-surface-container-high">
        {sortedItems.map((item) => {
          const isUpload = item.item_type === 'version_upload';
          const isBuzzCheck = item.item_type === 'buzz_check';
          const isApproved = item.status === 'approved' || item.status === 'completed' || (isBuzzCheck && item.buzz_overall_status === 'ready');
          const isBlocked = isBuzzCheck && item.buzz_overall_status === 'blocked';

          return (
            <div key={item.id} className="relative group">
              {/* Timeline marker node */}
              <div
                className={`absolute -left-[27px] top-1.5 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all shadow-sm ${
                  isApproved
                    ? 'bg-emerald-500 text-white ring-4 ring-emerald-500/20'
                    : isBlocked
                    ? 'bg-rose-500 text-white ring-4 ring-rose-500/20'
                    : isUpload
                    ? 'bg-primary text-on-primary ring-4 ring-primary/20'
                    : isBuzzCheck
                    ? 'bg-amber-500 text-white ring-4 ring-amber-500/20'
                    : 'bg-amber-500 text-white ring-4 ring-amber-500/20'
                }`}
              >
                {isUpload ? (
                  <span>V{item.version || 1}</span>
                ) : isBuzzCheck ? (
                  <span className="material-symbols-outlined text-[14px]">verified</span>
                ) : (
                  <span className="material-symbols-outlined text-[14px]">sync</span>
                )}
              </div>

              {/* Event Card */}
              <div className="bg-surface-container rounded-xl p-4 border border-surface-container-high/80 hover:border-surface-container-highest transition-all shadow-xs">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 text-label-xs font-semibold rounded-md ${
                        isUpload
                          ? 'bg-primary/10 text-primary border border-primary/20'
                          : isBuzzCheck
                          ? isApproved
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : isBlocked
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                      }`}
                    >
                      {isUpload
                        ? `Deliverable Upload (v${item.version || 1})`
                        : isBuzzCheck
                        ? `Buzz Check — ${item.buzz_overall_status === 'ready' ? 'Ready' : item.buzz_overall_status === 'blocked' ? 'Blocked' : 'Needs Attention'}`
                        : 'Revision Request'}
                    </span>
                    {item.milestone_title && (
                      <span className="font-label-xs text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded-md">
                        {item.milestone_title}
                      </span>
                    )}
                  </div>

                  <span className="font-label-xs text-on-surface-variant">
                    {new Date(item.created_at).toLocaleString('en-IN', {
                      dateStyle: 'medium',
                      timeStyle: 'short',
                    })}
                  </span>
                </div>

                {/* Body Details */}
                <div className="mt-3 text-body-sm text-on-surface">
                  {isUpload ? (
                    <div>
                      <div className="flex items-center justify-between gap-2 flex-wrap">
                        <div className="font-medium text-on-surface flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-[18px] text-primary">description</span>
                          <span>{item.filename || 'Deliverable File'}</span>
                        </div>
                        {item.download_url && (
                          <a
                            href={item.download_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-primary hover:underline font-label-sm"
                          >
                            <span className="material-symbols-outlined text-[16px]">download</span>
                            Download Asset
                          </a>
                        )}
                      </div>

                      {item.creator_note && (
                        <div className="mt-2 text-xs bg-surface-container-low p-2.5 rounded-lg border border-surface-container-high">
                          <span className="font-semibold text-on-surface-variant block mb-0.5">Creator Note:</span>
                          <p className="text-on-surface italic">"{item.creator_note}"</p>
                        </div>
                      )}

                      {item.client_feedback && (
                        <div className="mt-2 text-xs bg-primary/5 p-2.5 rounded-lg border border-primary/20">
                          <span className="font-semibold text-primary block mb-0.5">Recruiter Feedback:</span>
                          <p className="text-on-surface">"{item.client_feedback}"</p>
                        </div>
                      )}
                    </div>
                  ) : isBuzzCheck ? (
                    <div>
                      <div className="flex items-center justify-between gap-2 flex-wrap">
                        <div className="font-medium text-on-surface flex items-center gap-1.5 text-xs">
                          <span className="material-symbols-outlined text-[18px] text-primary">analytics</span>
                          <span>Automated Delivery Readiness for <strong>{item.filename || `Version ${item.version}`}</strong></span>
                        </div>
                        {item.buzz_readiness_score !== null && item.buzz_readiness_score !== undefined && (
                          <span className={`font-title-sm font-bold text-xs px-2 py-0.5 rounded-full ${
                            item.buzz_readiness_score >= 90
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : item.buzz_readiness_score >= 60
                              ? 'bg-amber-500/10 text-amber-400'
                              : 'bg-rose-500/10 text-rose-400'
                          }`}>
                            Score: {item.buzz_readiness_score}%
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-on-surface-variant text-xs">
                        Brief spec compliance evaluated automatically upon deliverable upload.
                      </p>
                    </div>
                  ) : (
                    <div>
                      <div className="font-medium text-amber-500 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[18px]">edit_note</span>
                        <span>Revision Instructions:</span>
                      </div>
                      <p className="mt-1 text-on-surface text-xs bg-surface-container-low p-2.5 rounded-lg border border-surface-container-high">
                        "{item.revision_description}"
                      </p>

                      {item.revision_response && (
                        <div className="mt-2 text-xs bg-emerald-500/5 p-2.5 rounded-lg border border-emerald-500/20">
                          <span className="font-semibold text-emerald-500 block mb-0.5">Creator Response Note:</span>
                          <p className="text-on-surface">"{item.revision_response}"</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Footer status & actor */}
                <div className="mt-3 pt-2.5 border-t border-surface-container-high/60 flex items-center justify-between text-label-xs text-on-surface-variant">
                  <span>
                    By <strong className="text-on-surface">{item.actor_name || 'Participant'}</strong> ({item.actor_role === 'creator' ? 'Creator' : item.actor_role === 'system' ? 'Automated System' : 'Recruiter'})
                  </span>
                  <span className="capitalize font-medium px-2 py-0.5 rounded-full bg-surface-container-high">
                    Status: {item.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
