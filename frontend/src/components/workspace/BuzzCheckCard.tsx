import React, { useState } from 'react';
import type { BuzzCheckResult } from '../../types';

interface BuzzCheckCardProps {
  buzzCheck: BuzzCheckResult;
  version: number;
  filename: string;
}

export const BuzzCheckCard: React.FC<BuzzCheckCardProps> = ({
  buzzCheck,
  version,
  filename,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const { overall_status, readiness_score, check_details, warnings, suggested_fixes } = buzzCheck;

  // Status-dependent styling
  const statusConfig = {
    ready: {
      label: 'Delivery Ready',
      badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: 'check_circle',
      iconColor: 'text-emerald-400',
      accentBorder: 'border-emerald-500/30',
      scoreColor: 'text-emerald-400',
      barColor: 'bg-emerald-500',
    },
    needs_attention: {
      label: 'Needs Attention',
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: 'warning',
      iconColor: 'text-amber-400',
      accentBorder: 'border-amber-500/30',
      scoreColor: 'text-amber-400',
      barColor: 'bg-amber-500',
    },
    blocked: {
      label: 'Delivery Blocked',
      badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      icon: 'error',
      iconColor: 'text-rose-400',
      accentBorder: 'border-rose-500/30',
      scoreColor: 'text-rose-400',
      barColor: 'bg-rose-500',
    },
  }[overall_status] || {
    label: 'Needs Attention',
    badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    icon: 'warning',
    iconColor: 'text-amber-400',
    accentBorder: 'border-amber-500/30',
    scoreColor: 'text-amber-400',
    barColor: 'bg-amber-500',
  };

  const passedCount = check_details.filter((c) => c.status === 'passed').length;
  const totalCount = check_details.length;

  return (
    <div className={`mt-3 rounded-xl border ${statusConfig.accentBorder} bg-surface-container-low/70 overflow-hidden`}>
      {/* Header Bar */}
      <div className="p-3 flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[18px] text-primary">verified</span>
            <span className="font-label-sm font-bold text-on-surface tracking-wide">
              BUZZ CHECK
            </span>
          </div>

          {/* Status Badge */}
          <span className={`px-2 py-0.5 rounded-full font-label-xs font-semibold border flex items-center gap-1 ${statusConfig.badgeClass}`}>
            <span className="material-symbols-outlined text-[13px]">{statusConfig.icon}</span>
            {statusConfig.label}
          </span>

          <span className="text-label-xs text-on-surface-variant hidden sm:inline">
            for V{version} ({filename})
          </span>
        </div>

        {/* Readiness Score & Toggle Button */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-label-xs text-on-surface-variant font-medium">Readiness:</span>
            <span className={`font-title-sm font-bold text-sm ${statusConfig.scoreColor}`}>
              {readiness_score}%
            </span>
          </div>

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-2 py-1 text-label-xs text-on-surface-variant hover:text-on-surface bg-surface-container rounded-md hover:bg-surface-container-high transition-colors flex items-center gap-1 cursor-pointer"
          >
            <span>{isExpanded ? 'Hide Details' : 'View Spec Checks'}</span>
            <span className="material-symbols-outlined text-[14px]">
              {isExpanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1 w-full bg-surface-container-high overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${statusConfig.barColor}`}
          style={{ width: `${readiness_score}%` }}
        />
      </div>

      {/* Brief Summary Bar (always visible) */}
      <div className="px-3 py-2 bg-surface-container/30 border-t border-surface-container-high/40 flex items-center justify-between text-label-xs text-on-surface-variant flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <span>
            Passed: <strong className="text-on-surface">{passedCount}/{totalCount}</strong> checks
          </span>
          {warnings.length > 0 && (
            <span className="text-amber-400 flex items-center gap-1">
              <span className="material-symbols-outlined text-[12px]">warning</span>
              {warnings.length} {warnings.length === 1 ? 'warning' : 'warnings'}
            </span>
          )}
          {suggested_fixes.length > 0 && (
            <span className="text-rose-400 flex items-center gap-1">
              <span className="material-symbols-outlined text-[12px]">build</span>
              {suggested_fixes.length} suggested {suggested_fixes.length === 1 ? 'fix' : 'fixes'}
            </span>
          )}
        </div>
        <span className="text-[11px] text-on-surface-variant/70">
          Source: Confirmed Brief Spec
        </span>
      </div>

      {/* Expanded Details Section */}
      {isExpanded && (
        <div className="p-3 border-t border-surface-container-high/60 space-y-3 bg-surface-container/20">
          {/* Checks List */}
          {check_details.length > 0 ? (
            <div className="space-y-1.5">
              <span className="font-label-xs font-semibold text-on-surface-variant uppercase tracking-wider block mb-1">
                Automated Spec Validation
              </span>
              {check_details.map((check, idx) => {
                const isPassed = check.status === 'passed';
                const isFailed = check.status === 'failed';

                return (
                  <div
                    key={`${check.name}-${idx}`}
                    className="flex items-start gap-2.5 p-2 rounded-lg bg-surface-container-low border border-surface-container-high/40 text-xs"
                  >
                    <span
                      className={`material-symbols-outlined text-[16px] mt-0.5 shrink-0 ${
                        isPassed
                          ? 'text-emerald-400'
                          : isFailed
                          ? 'text-rose-400'
                          : 'text-amber-400'
                      }`}
                    >
                      {isPassed ? 'check_circle' : isFailed ? 'cancel' : 'help'}
                    </span>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <strong className="text-on-surface font-medium">{check.label}</strong>
                        <span
                          className={`font-label-xs uppercase tracking-wide font-semibold ${
                            isPassed
                              ? 'text-emerald-400'
                              : isFailed
                              ? 'text-rose-400'
                              : 'text-amber-400'
                          }`}
                        >
                          {isPassed ? 'Passed' : isFailed ? 'Failed' : 'Manual Verification'}
                        </span>
                      </div>
                      <p className="text-on-surface-variant mt-0.5">{check.detail}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-on-surface-variant italic">
              No specific brief requirements configured for automated checks. Deliverable accepted as compliant.
            </p>
          )}

          {/* Warnings Section */}
          {warnings.length > 0 && (
            <div className="p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/20 text-xs">
              <div className="flex items-center gap-1.5 text-amber-400 font-semibold mb-1">
                <span className="material-symbols-outlined text-[14px]">warning</span>
                <span>Delivery Advisories</span>
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-on-surface-variant pl-1">
                {warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggested Fixes Section */}
          {suggested_fixes.length > 0 && (
            <div className="p-2.5 rounded-lg bg-rose-500/5 border border-rose-500/20 text-xs">
              <div className="flex items-center gap-1.5 text-rose-400 font-semibold mb-1">
                <span className="material-symbols-outlined text-[14px]">build</span>
                <span>Suggested Remediation</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-on-surface pl-1">
                {suggested_fixes.map((fix, i) => (
                  <li key={i} className="font-medium text-rose-200">
                    {fix}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
