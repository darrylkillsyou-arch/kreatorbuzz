import React from 'react';
import type { TrustBadgeItem, ReliabilityFlagsItem } from '../types';

interface TrustBadgesProps {
  badges?: TrustBadgeItem[];
  reliability?: ReliabilityFlagsItem;
  isRisingCreator?: boolean;
  risingReason?: string | null;
  compact?: boolean;
}

export const TrustBadges: React.FC<TrustBadgesProps> = ({
  badges = [],
  reliability,
  isRisingCreator,
  risingReason,
  compact = false,
}) => {
  const verifiedBadges = badges.filter((b) => b.verified);

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
        {isRisingCreator && (
          <span
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
            title={risingReason || 'Rising Creator: Evaluated on original portfolio and workflow quality'}
          >
            <span className="material-symbols-outlined text-[13px]">trending_up</span>
            Rising Talent
          </span>
        )}
        {verifiedBadges.slice(0, 3).map((b) => (
          <span
            key={b.id}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-surface-container text-on-surface-variant border border-outline-variant/25 font-medium"
            title={b.evidence}
          >
            <span className="material-symbols-outlined text-[12px] text-secondary">
              {b.icon || 'verified'}
            </span>
            {b.label}
          </span>
        ))}
        {reliability && (
          <span
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium ${
              reliability.status === 'Reliable'
                ? 'bg-secondary-container/20 text-secondary border border-secondary/30'
                : reliability.status === 'Minor Concern'
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
            }`}
          >
            <span className="material-symbols-outlined text-[12px]">
              {reliability.status === 'Reliable' ? 'check_circle' : 'warning'}
            </span>
            {reliability.status}
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-2 p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-on-surface uppercase tracking-wider text-[11px] flex items-center gap-1.5">
          <span className="material-symbols-outlined text-secondary text-[16px]">verified_user</span>
          Trust & Verification Record
        </span>
        {isRisingCreator && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-semibold text-[11px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <span className="material-symbols-outlined text-[13px]">trending_up</span>
            Rising Creator
          </span>
        )}
      </div>

      {isRisingCreator && risingReason && (
        <p className="text-[11px] text-emerald-400/90 italic bg-emerald-950/20 p-2 rounded border border-emerald-500/20">
          {risingReason}
        </p>
      )}

      {/* Grid of verified badges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
        {badges.map((b) => (
          <div
            key={b.id}
            className={`p-2 rounded-lg flex items-start gap-2 ${
              b.verified
                ? 'bg-surface-container/60 border border-secondary/20 text-on-surface'
                : 'bg-surface-container-lowest/40 opacity-50 text-on-surface-variant'
            }`}
          >
            <span
              className={`material-symbols-outlined text-[16px] shrink-0 mt-0.5 ${
                b.verified ? 'text-secondary' : 'text-on-surface-variant'
              }`}
            >
              {b.verified ? b.icon || 'verified' : 'radio_button_unchecked'}
            </span>
            <div className="min-w-0">
              <span className="font-semibold block text-[11px] truncate">{b.label}</span>
              <span className="text-[10px] text-on-surface-variant leading-tight block">
                {b.evidence}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Reliability Flags Footer */}
      {reliability && (
        <div className="pt-2 border-t border-surface-container flex flex-wrap items-center justify-between gap-2 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="text-on-surface-variant">Platform Record:</span>
            <span className="font-medium text-on-surface">
              {reliability.completed_projects} projects completed • {reliability.on_time_percentage}% on-time
            </span>
          </div>
          <span
            className={`font-semibold px-2 py-0.5 rounded ${
              reliability.status === 'Reliable'
                ? 'bg-secondary-container/30 text-secondary'
                : 'bg-amber-500/20 text-amber-300'
            }`}
          >
            {reliability.status}
          </span>
        </div>
      )}
    </div>
  );
};
