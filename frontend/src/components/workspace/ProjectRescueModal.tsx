import React, { useState, useEffect } from 'react';
import type { ProjectHealth, RescueReplacementDetails, ReplacementCandidate } from '../../types';
import { api } from '../../lib/api';

interface ProjectRescueModalProps {
  workspaceId: string;
  initialTab?: 'adjust_plan' | 'replacement';
  health: ProjectHealth;
  isOpen: boolean;
  onClose: () => void;
  onActionComplete: () => void;
}

export const ProjectRescueModal: React.FC<ProjectRescueModalProps> = ({
  workspaceId,
  initialTab = 'adjust_plan',
  health,
  isOpen,
  onClose,
  onActionComplete,
}) => {
  const [activeTab, setActiveTab] = useState<'adjust_plan' | 'replacement'>(initialTab);
  const [rescueDetails, setRescueDetails] = useState<RescueReplacementDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notes, setNotes] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<ReplacementCandidate | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  useEffect(() => {
    if (isOpen && activeTab === 'replacement' && !rescueDetails) {
      loadRescueDetails();
    }
  }, [isOpen, activeTab]);

  const loadRescueDetails = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const details = await api.workspaces.getRescueDetails(workspaceId);
      setRescueDetails(details);
      if (details.replacement_candidates && details.replacement_candidates.length > 0) {
        setSelectedCandidate(details.replacement_candidates[0]);
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to load replacement options.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const handleAdjustPlanSubmit = async () => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await api.workspaces.submitRescueAction(workspaceId, {
        action: 'adjust_plan',
        notes: notes.trim() || 'Plan adjusted based on project health recommendations.',
      });
      setSuccessMessage('Project plan recovery action logged. Timeline and team alerted.');
      setTimeout(() => {
        onActionComplete();
        onClose();
      }, 1200);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to submit plan adjustment.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReplacementSubmit = async () => {
    if (!selectedCandidate) return;
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await api.workspaces.submitRescueAction(workspaceId, {
        action: 'initiate_replacement',
        notes: notes.trim() || `Initiated handoff to replacement creator: ${selectedCandidate.name}`,
        replacement_creator_id: selectedCandidate.creator_id,
      });
      setSuccessMessage(`Handoff Pack prepared for ${selectedCandidate.name}. Recruiter decision registered.`);
      setTimeout(() => {
        onActionComplete();
        onClose();
      }, 1400);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to initiate replacement.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface border border-surface-container-highest rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="p-4 border-b border-surface-container-high flex items-center justify-between bg-surface-container-low">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-[20px]">health_and_safety</span>
            </div>
            <div>
              <h3 className="text-title-sm font-bold text-on-surface">Project Rescue & Recovery</h3>
              <p className="text-label-xs text-on-surface-variant">
                Human-directed risk mitigation — protected budget & verified handoff
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-surface-container-high bg-surface-container/30 px-4">
          <button
            type="button"
            onClick={() => setActiveTab('adjust_plan')}
            className={`px-4 py-2.5 text-label-sm font-medium border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'adjust_plan'
                ? 'border-primary text-primary bg-primary/5'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">tune</span>
            Option A: Adjust Plan
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab('replacement');
              if (!rescueDetails) loadRescueDetails();
            }}
            className={`px-4 py-2.5 text-label-sm font-medium border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'replacement'
                ? 'border-primary text-primary bg-primary/5'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">person_swap</span>
            Option B: Match Replacement Creator
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 overflow-y-auto space-y-4 flex-1">
          {successMessage && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-label-sm flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">check_circle</span>
              <span>{successMessage}</span>
            </div>
          )}

          {errorMessage && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-label-sm flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">error</span>
              <span>{errorMessage}</span>
            </div>
          )}

          {activeTab === 'adjust_plan' && (
            <div className="space-y-4">
              <div className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/20 text-label-xs text-on-surface space-y-1">
                <span className="font-semibold text-amber-400 flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[16px]">info</span>
                  Current Project Health: {health.health_score}/100 ({health.health_status})
                </span>
                <p className="text-on-surface-variant">
                  Adjusting the plan gives the current creator revised expectations while preserving momentum.
                </p>
              </div>

              <div>
                <label className="block text-label-xs font-semibold uppercase tracking-wider text-on-surface-variant mb-2">
                  Recommended Adjustments
                </label>
                <div className="space-y-2">
                  {health.adjust_plan_suggestions.map((sug, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-surface-container-low border border-surface-container-high flex items-start gap-2.5 text-label-sm text-on-surface"
                    >
                      <span className="material-symbols-outlined text-[18px] text-primary mt-0.5">
                        check_box
                      </span>
                      <div>
                        <span>{sug}</span>
                        <p className="text-[11px] text-on-surface-variant/70 mt-0.5">
                          Applies dynamically to upcoming milestone deadlines and review gates.
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-label-xs font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Recruiter Instructions / Notes (Optional)
                </label>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="e.g., Extended deadline by 3 days. Prioritizing final render over second revision pass."
                  className="w-full rounded-lg bg-surface-container-low border border-surface-container-high p-3 text-body-sm text-on-surface placeholder:text-on-surface-variant/50 focus:outline-none focus:border-primary"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-label-sm rounded-lg border border-surface-container-highest hover:bg-surface-container text-on-surface-variant"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={handleAdjustPlanSubmit}
                  className="px-4 py-2 text-label-sm rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-semibold shadow-sm transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? 'Applying Plan...' : 'Apply Adjusted Plan'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'replacement' && (
            <div className="space-y-4">
              {isLoading ? (
                <div className="py-12 text-center text-label-sm text-on-surface-variant">
                  <span className="material-symbols-outlined animate-spin text-[28px] text-primary block mx-auto mb-2">
                    progress_activity
                  </span>
                  Matching qualified replacement creators and preparing Handoff Pack...
                </div>
              ) : rescueDetails ? (
                <>
                  {/* Protected Budget Simulation Pill */}
                  <div className="p-3.5 rounded-xl bg-surface-container-low border border-surface-container-high grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block">
                        Total Project Budget
                      </span>
                      <span className="text-body-md font-bold text-on-surface font-mono">
                        ₹{rescueDetails.health.protected_budget.total_budget.toLocaleString('en-IN')}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block">
                        Retained by Current Creator
                      </span>
                      <span className="text-body-md font-bold text-emerald-400 font-mono">
                        ₹{rescueDetails.health.protected_budget.approved_amount.toLocaleString('en-IN')}
                      </span>
                      <span className="text-[10px] text-on-surface-variant/60 block">
                        (Approved Milestones)
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block">
                        Available for Replacement
                      </span>
                      <span className="text-body-md font-bold text-primary font-mono">
                        ₹
                        {rescueDetails.health.protected_budget.remaining_protected_balance.toLocaleString(
                          'en-IN'
                        )}
                      </span>
                    </div>
                    <div className="sm:col-span-3 text-[10px] font-mono text-on-surface-variant/70 border-t border-surface-container-high pt-2">
                      {rescueDetails.health.protected_budget.disclaimer}
                    </div>
                  </div>

                  {/* Project Handoff Pack Summary */}
                  <div className="p-3 rounded-lg bg-surface-container/40 border border-surface-container-high text-label-xs space-y-1.5">
                    <div className="flex items-center justify-between text-on-surface font-semibold">
                      <span className="flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[16px] text-primary">
                          folder_shared
                        </span>
                        Project Handoff Pack Ready
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                        Zero-Restart Assurance
                      </span>
                    </div>
                    <p className="text-on-surface-variant">
                      The replacement creator will immediately receive all {rescueDetails.handoff_pack.deliverable_history.length} uploaded deliverable versions, agreed licensing parameters, and recruiter feedback.
                    </p>
                    <div className="grid grid-cols-2 gap-2 pt-1 text-[11px] text-on-surface-variant">
                      <div>
                        Remaining Scope: <strong className="text-on-surface">{rescueDetails.handoff_pack.remaining_scope}</strong>
                      </div>
                      <div>
                        Deadline: <strong className="text-on-surface">{rescueDetails.handoff_pack.remaining_deadline}</strong>
                      </div>
                    </div>
                  </div>

                  {/* Replacement Candidate Selection */}
                  <div>
                    <label className="block text-label-xs font-semibold uppercase tracking-wider text-on-surface-variant mb-2">
                      Top Replacement Creators (Current Creator Excluded)
                    </label>

                    {rescueDetails.replacement_candidates.length === 0 ? (
                      <div className="p-4 rounded-lg bg-surface-container-low border border-surface-container-high text-center text-label-sm text-on-surface-variant">
                        No replacement creators currently available in this category.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {rescueDetails.replacement_candidates.map(candidate => {
                          const isSelected = selectedCandidate?.creator_id === candidate.creator_id;
                          return (
                            <div
                              key={candidate.creator_id}
                              onClick={() => setSelectedCandidate(candidate)}
                              className={`p-3 rounded-xl border cursor-pointer transition-all ${
                                isSelected
                                  ? 'border-primary bg-primary/5 shadow-sm'
                                  : 'border-surface-container-high bg-surface-container-low hover:border-surface-container-highest'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-semibold text-body-sm text-on-surface truncate">
                                  {candidate.name}
                                </span>
                                <span className="text-[11px] font-bold text-primary font-mono">
                                  {candidate.match_score}% Match
                                </span>
                              </div>

                              <div className="text-label-xs text-on-surface-variant mb-2 space-y-0.5">
                                <div className="truncate">🎯 {candidate.specialization}</div>
                                <div>⭐ {candidate.rating} rating • ⚡ {candidate.delivery_days}d SLA</div>
                                <div className="truncate text-[10px] text-on-surface-variant/70">
                                  🛠️ {candidate.ai_tools.slice(0, 2).join(', ')}
                                </div>
                              </div>

                              {candidate.match_reasons.length > 0 && (
                                <p className="text-[10px] text-emerald-400 line-clamp-2">
                                  ✓ {candidate.match_reasons[0]}
                                </p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {/* Recruiter confirmation notice */}
                  <div className="p-2.5 rounded bg-surface-container-low border border-surface-container-high/60 text-[11px] text-on-surface-variant/80">
                    <strong>Recruiter Decision Control:</strong> Selecting a replacement creator prepares the handoff agreement and invites the candidate. The system will never automatically remove or replace creators without your explicit action.
                  </div>

                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-4 py-2 text-label-sm rounded-lg border border-surface-container-highest hover:bg-surface-container text-on-surface-variant"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      disabled={isSubmitting || !selectedCandidate}
                      onClick={handleReplacementSubmit}
                      className="px-4 py-2 text-label-sm rounded-lg bg-primary hover:bg-primary/90 text-on-primary font-semibold shadow-sm transition-colors disabled:opacity-50"
                    >
                      {isSubmitting
                        ? 'Initiating Replacement...'
                        : `Propose Replacement (${selectedCandidate?.name || 'Select Creator'})`}
                    </button>
                  </div>
                </>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
