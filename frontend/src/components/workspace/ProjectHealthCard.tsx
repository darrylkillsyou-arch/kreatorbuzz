import React, { useState } from 'react';
import type { ProjectHealth } from '../../types';

interface ProjectHealthCardProps {
  health: ProjectHealth;
  isRecruiter: boolean;
  onOpenRescueModal: (action: 'adjust_plan' | 'replacement') => void;
  onContinueWithCreator?: () => void;
}

export const ProjectHealthCard: React.FC<ProjectHealthCardProps> = ({
  health,
  isRecruiter,
  onOpenRescueModal,
  onContinueWithCreator,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const { health_score, health_status, reasons, adjust_plan_suggestions, protected_budget } = health;

  const statusConfig = {
    'ON TRACK': {
      label: 'On Track',
      badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: 'verified',
      iconColor: 'text-emerald-400',
      accentBorder: 'border-emerald-500/30',
      scoreColor: 'text-emerald-400',
      barColor: 'bg-emerald-500',
      summary: 'Project milestones and communication are proceeding normally.',
    },
    'AT RISK': {
      label: 'At Risk',
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: 'warning',
      iconColor: 'text-amber-400',
      accentBorder: 'border-amber-500/30',
      scoreColor: 'text-amber-400',
      barColor: 'bg-amber-500',
      summary: 'Delays or revision stalls detected. Plan adjustment recommended.',
    },
    'RESCUE RECOMMENDED': {
      label: 'Rescue Recommended',
      badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      icon: 'health_and_safety',
      iconColor: 'text-rose-400',
      accentBorder: 'border-rose-500/30',
      scoreColor: 'text-rose-400',
      barColor: 'bg-rose-500',
      summary: 'Critical milestones overdue or delivery stalled. Immediate recovery options available.',
    },
  }[health_status] || {
    label: health_status,
    badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    icon: 'info',
    iconColor: 'text-amber-400',
    accentBorder: 'border-amber-500/30',
    scoreColor: 'text-amber-400',
    barColor: 'bg-amber-500',
    summary: 'Evaluating project health status.',
  };

  const isSevere = health_status === 'AT RISK' || health_status === 'RESCUE RECOMMENDED';

  return (
    <div
      className={`rounded-xl border ${statusConfig.accentBorder} bg-surface-container-low/70 overflow-hidden shadow-sm backdrop-blur-sm transition-all duration-300`}
    >
      {/* Header Bar */}
      <div className="p-3.5 flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <div
            className={`w-9 h-9 rounded-lg flex items-center justify-center ${
              health_status === 'ON TRACK'
                ? 'bg-emerald-500/10 text-emerald-400'
                : health_status === 'AT RISK'
                ? 'bg-amber-500/10 text-amber-400'
                : 'bg-rose-500/10 text-rose-400'
            }`}
          >
            <span className="material-symbols-outlined text-[20px]">{statusConfig.icon}</span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-body-sm font-semibold text-on-surface">Project Health</span>
              <span
                className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${statusConfig.badgeClass}`}
              >
                {statusConfig.label}
              </span>
            </div>
            <p className="text-label-xs text-on-surface-variant line-clamp-1">{statusConfig.summary}</p>
          </div>
        </div>

        {/* Right side: Score & Toggle */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="flex items-baseline gap-1 justify-end">
              <span className={`text-title-md font-bold tracking-tight ${statusConfig.scoreColor}`}>
                {health_score}
              </span>
              <span className="text-label-xs text-on-surface-variant font-mono">/100</span>
            </div>
            <span className="text-[10px] text-on-surface-variant/70 uppercase tracking-wider block">
              Health Score
            </span>
          </div>

          <button
            type="button"
            onClick={() => setIsExpanded(prev => !prev)}
            className="p-1.5 rounded-md hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
            aria-label={isExpanded ? 'Collapse health details' : 'Expand health details'}
          >
            <span className="material-symbols-outlined text-[18px]">
              {isExpanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1 w-full bg-surface-container-high overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${statusConfig.barColor}`}
          style={{ width: `${Math.max(5, health_score)}%` }}
        />
      </div>

      {/* Protected Budget & Risk Highlight Bar */}
      <div className="px-3.5 py-2 bg-surface-container/30 border-t border-surface-container-high/40 flex items-center justify-between text-label-xs text-on-surface-variant flex-wrap gap-2">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[14px] text-primary">shield</span>
            <span>
              Protected Balance:{' '}
              <strong className="text-on-surface font-mono">
                ₹{protected_budget.remaining_protected_balance.toLocaleString('en-IN')}
              </strong>
            </span>
          </div>
          <div className="text-[11px] text-on-surface-variant/70">
            Earned: ₹{protected_budget.approved_amount.toLocaleString('en-IN')} / Total: ₹
            {protected_budget.total_budget.toLocaleString('en-IN')}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-surface-container-high/60 text-on-surface-variant">
            {protected_budget.disclaimer}
          </span>
        </div>
      </div>

      {/* Recruiter Action Strip (visible if At Risk or Rescue Recommended) */}
      {isSevere && isRecruiter && (
        <div className="px-3.5 py-2.5 bg-surface-container/60 border-t border-surface-container-high/60 flex items-center justify-between gap-3 flex-wrap">
          <div className="text-label-xs text-on-surface">
            <strong className="text-primary font-medium">Recruiter Controls:</strong> Choose a recovery strategy
            without forfeiting completed work.
          </div>
          <div className="flex items-center gap-2">
            {onContinueWithCreator && (
              <button
                type="button"
                onClick={onContinueWithCreator}
                className="px-2.5 py-1 text-label-xs rounded-md border border-surface-container-highest hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
              >
                Continue with Creator
              </button>
            )}
            <button
              type="button"
              onClick={() => onOpenRescueModal('adjust_plan')}
              className="px-2.5 py-1 text-label-xs rounded-md bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium transition-colors"
            >
              Adjust Plan
            </button>
            <button
              type="button"
              onClick={() => onOpenRescueModal('replacement')}
              className="px-2.5 py-1 text-label-xs rounded-md bg-primary hover:bg-primary/90 text-on-primary font-medium transition-colors shadow-sm"
            >
              Find Replacement
            </button>
          </div>
        </div>
      )}

      {/* Expanded Breakdown */}
      {isExpanded && (
        <div className="p-3.5 border-t border-surface-container-high/60 space-y-3 bg-surface-container/20">
          {/* Reasons List */}
          <div>
            <h5 className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
              Explainable Risk Factors
            </h5>
            {reasons.length === 0 ? (
              <p className="text-label-xs text-emerald-400 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[14px]">check_circle</span>
                All milestones, communication, and deliveries are on track.
              </p>
            ) : (
              <ul className="space-y-1">
                {reasons.map((reason, idx) => (
                  <li key={idx} className="text-label-xs text-on-surface flex items-start gap-1.5">
                    <span className="material-symbols-outlined text-[13px] text-amber-400 mt-0.5">
                      info
                    </span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Suggestions */}
          {adjust_plan_suggestions.length > 0 && (
            <div>
              <h5 className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
                Suggested Plan Adjustments
              </h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                {adjust_plan_suggestions.map((sug, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-surface-container-low border border-surface-container-high/50 text-label-xs text-on-surface-variant flex items-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-[14px] text-primary">lightbulb</span>
                    <span>{sug}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Protected Budget Card Explainer */}
          <div className="p-2.5 rounded-lg bg-surface-container-low border border-surface-container-high text-label-xs text-on-surface-variant space-y-1">
            <div className="flex items-center justify-between font-medium text-on-surface">
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] text-primary">verified_user</span>
                Protected Budget Breakdown
              </span>
              <span className="text-[10px] font-mono text-primary">KreatorBuzz Safety Net</span>
            </div>
            <p className="text-[11px] text-on-surface-variant/80">
              Approved milestones remain with the current creator for completed work. If a replacement is initiated,
              only the remaining protected balance (₹
              {protected_budget.remaining_protected_balance.toLocaleString('en-IN')}) is transferred to the new creator.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
