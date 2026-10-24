import React, { useState } from 'react';
import type { CreatorCompareCardData, DifferenceExplanationItem } from '../types';
import { CreatorAvatar } from './CreatorAvatar';
import { TrustBadges } from './TrustBadges';
import { api } from '../lib/api';

interface CreatorComparisonModalProps {
  candidates: CreatorCompareCardData[];
  differences: DifferenceExplanationItem[];
  summaryVerdict: string;
  briefId?: number | null;
  onClose: () => void;
  onHire: (creator: CreatorCompareCardData) => void;
}

export const CreatorComparisonModal: React.FC<CreatorComparisonModalProps> = ({
  candidates,
  differences,
  summaryVerdict,
  briefId,
  onClose,
  onHire,
}) => {
  const [shortlistedMap, setShortlistedMap] = useState<Record<number, boolean>>({});
  const [isSaving, setIsSaving] = useState<Record<number, boolean>>({});

  const handleShortlist = async (candidate: CreatorCompareCardData) => {
    setIsSaving((prev) => ({ ...prev, [candidate.creator_id]: true }));
    try {
      await api.shortlist.add({
        creator_profile_id: candidate.creator_id,
        creator_user_id: candidate.user_id,
        brief_id: briefId || undefined,
      });
      setShortlistedMap((prev) => ({ ...prev, [candidate.creator_id]: true }));
    } catch (err) {
      console.error('Failed to shortlist', err);
    } finally {
      setIsSaving((prev) => ({ ...prev, [candidate.creator_id]: false }));
    }
  };

  const getDiffForCreator = (creatorId: number) => {
    return differences.find((d) => d.creator_id === creatorId);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-2xl w-full max-w-5xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-surface-container flex items-center justify-between bg-surface-container-low/50">
          <div className="flex items-center gap-2.5">
            <span className="material-symbols-outlined text-secondary text-[24px]">compare_arrows</span>
            <div>
              <h2 className="font-headline-sm font-bold text-on-surface text-base sm:text-lg">
                Side-by-Side Creator Comparison
              </h2>
              <p className="text-xs text-on-surface-variant">
                Comparing {candidates.length} candidates with deterministic difference analysis
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-surface-container hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant cursor-pointer transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Verdict Banner */}
        <div className="px-5 py-2.5 bg-secondary-container/10 border-b border-secondary/20 flex items-center gap-2 text-xs text-secondary font-medium">
          <span className="material-symbols-outlined text-[18px]">insights</span>
          <span>{summaryVerdict}</span>
        </div>

        {/* Grid of Creators */}
        <div className="p-4 sm:p-5 overflow-y-auto flex-1">
          <div className={`grid grid-cols-1 md:grid-cols-${candidates.length} gap-4`}>
            {candidates.map((c) => {
              const diff = getDiffForCreator(c.creator_id);
              const isShortlisted = shortlistedMap[c.creator_id];

              return (
                <div
                  key={c.creator_id}
                  className="bg-surface-container-low rounded-xl border border-outline-variant/30 p-4 flex flex-col justify-between gap-4 hover:border-secondary/30 transition-all"
                >
                  <div className="space-y-3.5">
                    {/* Creator Identity & Match Score */}
                    <div className="flex items-start justify-between gap-2 pb-3 border-b border-surface-container">
                      <div className="flex items-center gap-2.5">
                        <CreatorAvatar src={c.avatar_url || ''} name={c.display_name} size="md" />
                        <div className="min-w-0">
                          <h3 className="font-bold text-on-surface text-sm truncate">{c.display_name}</h3>
                          <p className="text-[11px] text-on-surface-variant truncate">{c.specialization}</p>
                          <span className="text-[10px] text-secondary font-mono">
                            {c.core_category} • {c.rating}★
                          </span>
                        </div>
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-secondary-container/40 text-secondary shrink-0">
                        {c.match_score}% Fit
                      </span>
                    </div>

                    {/* Key Metrics */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2 rounded bg-surface-container text-center">
                        <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Day Rate</span>
                        <span className="font-bold text-secondary text-xs">₹{c.starting_rate.toLocaleString('en-IN')}</span>
                      </div>
                      <div className="p-2 rounded bg-surface-container text-center">
                        <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Turnaround</span>
                        <span className="font-bold text-on-surface text-xs">{c.delivery_days} Days</span>
                      </div>
                    </div>

                    {/* Licensing & Rights */}
                    <div className="p-2.5 rounded bg-surface-container/70 border border-outline-variant/20 text-[11px] space-y-1">
                      <div className="flex items-center justify-between font-semibold">
                        <span className="text-on-surface flex items-center gap-1">
                          <span className="material-symbols-outlined text-[14px] text-secondary">verified</span>
                          Licensing
                        </span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] uppercase font-bold ${
                          c.licensing_status === 'full_match' ? 'text-emerald-400' : 'text-amber-400'
                        }`}>
                          {c.licensing_status.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-on-surface-variant">
                        {c.licensing_summary} ({c.licensing_territory}, {c.licensing_duration})
                      </p>
                    </div>

                    {/* Unique Advantages (What this creator has that others do not) */}
                    {diff && diff.unique_advantages.length > 0 && (
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                          <span className="material-symbols-outlined text-[14px]">add_circle</span>
                          What {c.display_name.split(' ')[0]} Offers Uniquely
                        </span>
                        <ul className="space-y-1 text-xs">
                          {diff.unique_advantages.map((adv, idx) => (
                            <li key={idx} className="flex items-start gap-1.5 text-on-surface text-[11px] leading-tight">
                              <span className="text-emerald-400 font-bold shrink-0">•</span>
                              <span>{adv}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Tradeoffs vs peers */}
                    {diff && diff.tradeoffs_vs_others.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
                          <span className="material-symbols-outlined text-[14px]">tune</span>
                          Considerations vs Peers
                        </span>
                        <ul className="space-y-1 text-xs">
                          {diff.tradeoffs_vs_others.map((tr, idx) => (
                            <li key={idx} className="flex items-start gap-1.5 text-on-surface-variant text-[11px] leading-tight">
                              <span className="text-amber-400 font-bold shrink-0">•</span>
                              <span>{tr}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Tools */}
                    <div className="pt-1">
                      <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-semibold block mb-1">
                        Active Tools
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {c.ai_tools.map((t, idx) => (
                          <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-surface-container text-on-surface font-medium">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Trust Badges */}
                    <div className="pt-1">
                      <TrustBadges
                        badges={c.badges}
                        reliability={c.reliability}
                        isRisingCreator={c.is_rising_creator}
                        compact={true}
                      />
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="grid grid-cols-2 gap-2 pt-3 border-t border-surface-container text-xs">
                    <button
                      type="button"
                      disabled={isShortlisted || isSaving[c.creator_id]}
                      onClick={() => handleShortlist(c)}
                      className={`py-2 rounded-full font-medium transition-colors flex items-center justify-center gap-1 cursor-pointer ${
                        isShortlisted
                          ? 'bg-secondary-container/20 text-secondary border border-secondary/30'
                          : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[15px]">
                        {isShortlisted ? 'bookmark_added' : 'bookmark_add'}
                      </span>
                      <span>{isShortlisted ? 'Shortlisted' : 'Shortlist'}</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => onHire(c)}
                      className="py-2 rounded-full font-medium bg-primary hover:bg-primary-container text-on-primary transition-all flex items-center justify-center gap-1 cursor-pointer shadow-sm"
                    >
                      <span>Direct Hire</span>
                      <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
