import React from 'react';
import type { RecruiterTrustData } from '../types';

interface RecruiterTrustBadgeProps {
  data: RecruiterTrustData;
  compact?: boolean;
}

export const RecruiterTrustBadge: React.FC<RecruiterTrustBadgeProps> = ({ data, compact = false }) => {
  if (compact) {
    return (
      <span
        className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-secondary-container/20 text-secondary border border-secondary/30"
        title={`${data.projects_completed} of ${data.projects_commissioned} commissions completed (${data.completion_rate_pct}% completion rate)`}
      >
        <span className="material-symbols-outlined text-[13px]">domain_verification</span>
        {data.trust_status}
      </span>
    );
  }

  return (
    <div className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-semibold text-on-surface">
          <span className="material-symbols-outlined text-secondary text-[16px]">domain_verification</span>
          <span>Recruiter Reliability Status</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-secondary-container/30 text-secondary font-bold text-[11px]">
          {data.trust_status}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
        <div className="p-2 rounded bg-surface-container text-center">
          <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Projects</span>
          <span className="font-bold text-on-surface text-xs mt-0.5 block">{data.projects_completed} Completed</span>
        </div>
        <div className="p-2 rounded bg-surface-container text-center">
          <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Completion</span>
          <span className="font-bold text-secondary text-xs mt-0.5 block">{data.completion_rate_pct}%</span>
        </div>
        <div className="p-2 rounded bg-surface-container text-center">
          <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Disputes</span>
          <span className="font-bold text-on-surface text-xs mt-0.5 block">{data.dispute_count} Open</span>
        </div>
        <div className="p-2 rounded bg-surface-container text-center">
          <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Response</span>
          <span className="font-bold text-on-surface text-xs mt-0.5 block">{data.response_behavior}</span>
        </div>
      </div>
    </div>
  );
};
