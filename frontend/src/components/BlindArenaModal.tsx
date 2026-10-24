import React, { useState } from 'react';
import type { BlindCreatorCardItem, BlindRevealData } from '../types';
import { api } from '../lib/api';
import { CreatorAvatar } from './CreatorAvatar';
import { TrustBadges } from './TrustBadges';

interface BlindArenaModalProps {
  candidates: BlindCreatorCardItem[];
  tagline?: string;
  briefId?: number | null;
  onClose: () => void;
  onHire: (creatorData: any) => void;
}

export const BlindArenaModal: React.FC<BlindArenaModalProps> = ({
  candidates,
  tagline = 'Choose the work. Then meet the creator.',
  briefId,
  onClose,
  onHire,
}) => {
  const [selectedToken, setSelectedToken] = useState<string>(candidates[0]?.blind_token || '');
  const [isRevealing, setIsRevealing] = useState(false);
  const [revealData, setRevealData] = useState<BlindRevealData | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [shortlisted, setShortlisted] = useState(false);
  const [isShortlisting, setIsShortlisting] = useState(false);

  const selectedCandidate = candidates.find((c) => c.blind_token === selectedToken);

  const handleReveal = async () => {
    if (!selectedToken || isRevealing) return;
    setIsRevealing(true);
    setErrorMsg('');

    try {
      const allTokens = candidates.map((c) => c.blind_token);
      const res = await api.comparison.revealBlind({
        blind_token: selectedToken,
        all_tokens: allTokens,
      });
      setRevealData(res);
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to reveal creator.');
    } finally {
      setIsRevealing(false);
    }
  };

  const handleShortlistRevealed = async () => {
    if (!revealData || shortlisted || isShortlisting) return;
    setIsShortlisting(true);
    try {
      await api.shortlist.add({
        creator_profile_id: revealData.revealed_creator.creator_id,
        creator_user_id: revealData.revealed_creator.user_id,
        brief_id: briefId || undefined,
      });
      setShortlisted(true);
    } catch (err) {
      console.error('Failed to shortlist revealed creator', err);
    } finally {
      setIsShortlisting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
      <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-2xl w-full max-w-5xl shadow-2xl overflow-hidden flex flex-col max-h-[94vh]">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-surface-container flex items-center justify-between bg-surface-container-low/60">
          <div className="flex items-center gap-2.5">
            <span className="w-8 h-8 rounded-lg bg-secondary-container/30 text-secondary flex items-center justify-center">
              <span className="material-symbols-outlined text-[20px]">visibility_off</span>
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-headline-sm font-bold text-on-surface text-base sm:text-lg">
                  Blind Arena
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-secondary-container/40 text-secondary uppercase tracking-wider">
                  Fair Hiring Mode
                </span>
              </div>
              <p className="text-xs text-on-surface-variant italic">{tagline}</p>
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

        {/* Content Body: Pre-Reveal vs Post-Reveal */}
        <div className="p-4 sm:p-5 overflow-y-auto flex-1">
          {errorMsg && (
            <div className="p-3 mb-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {errorMsg}
            </div>
          )}

          {!revealData ? (
            /* WHILE BLIND: Hide Name/Photo/Rank; Show Work Quality & Portfolio */
            <div className="space-y-5">
              <div className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/20 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2 text-on-surface-variant">
                  <span className="material-symbols-outlined text-secondary text-[18px]">lock</span>
                  <span>
                    Identities, ratings, and follower counts are masked to eliminate prestige bias. Choose based purely on craft.
                  </span>
                </div>
                <button
                  type="button"
                  disabled={!selectedToken || isRevealing}
                  onClick={handleReveal}
                  className="px-5 py-2 rounded-full font-bold bg-secondary hover:bg-secondary/90 text-on-secondary shadow-md flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px]">visibility</span>
                  <span>{isRevealing ? 'Revealing...' : `Reveal ${selectedCandidate?.anonymous_id || 'Selection'}`}</span>
                </button>
              </div>

              {/* Candidate Cards Grid */}
              <div className={`grid grid-cols-1 md:grid-cols-${candidates.length} gap-4`}>
                {candidates.map((card) => {
                  const isSelected = selectedToken === card.blind_token;

                  return (
                    <div
                      key={card.blind_token}
                      onClick={() => setSelectedToken(card.blind_token)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between gap-3 relative ${
                        isSelected
                          ? 'bg-surface-container-low border-secondary shadow-lg ring-1 ring-secondary/50'
                          : 'bg-surface-container-low/40 border-outline-variant/30 hover:border-outline-variant/60'
                      }`}
                    >
                      <div className="space-y-3">
                        {/* Blind Header */}
                        <div className="flex items-start justify-between gap-2 pb-2.5 border-b border-surface-container">
                          <div className="flex items-center gap-2.5">
                            <div className="w-10 h-10 rounded-full bg-surface-container-high border border-outline-variant/40 flex items-center justify-center font-bold text-secondary text-sm">
                              {card.anonymous_id.replace('Creator ', '')}
                            </div>
                            <div>
                              <h3 className="font-bold text-on-surface text-sm">{card.anonymous_id}</h3>
                              <p className="text-[11px] text-on-surface-variant">{card.specialization}</p>
                            </div>
                          </div>
                          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-secondary-container/40 text-secondary">
                            {card.match_score}% Fit
                          </span>
                        </div>

                        {/* Portfolio Works Gallery Preview */}
                        <div className="space-y-1.5">
                          <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-semibold block">
                            Portfolio Samples ({card.portfolio_samples.length})
                          </span>
                          <div className="grid grid-cols-2 gap-1.5">
                            {card.portfolio_samples.slice(0, 2).map((item, idx) => (
                              <div
                                key={idx}
                                className="h-24 rounded-lg overflow-hidden bg-surface-container relative group border border-outline-variant/20"
                              >
                                <img
                                  src={item.image_url}
                                  alt={item.title}
                                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-1.5">
                                  <span className="text-[10px] font-medium text-white truncate w-full">
                                    {item.title}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Operational Metrics */}
                        <div className="grid grid-cols-2 gap-1.5 text-xs">
                          <div className="p-2 rounded bg-surface-container text-center">
                            <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Turnaround</span>
                            <span className="font-bold text-on-surface text-xs">{card.delivery_days} Days</span>
                          </div>
                          <div className="p-2 rounded bg-surface-container text-center">
                            <span className="text-[10px] text-on-surface-variant block uppercase font-medium">Starting Rate</span>
                            <span className="font-bold text-secondary text-xs">₹{card.starting_rate.toLocaleString('en-IN')}</span>
                          </div>
                        </div>

                        {/* Strengths */}
                        <div className="space-y-1 text-[11px]">
                          <span className="font-semibold text-emerald-400 block uppercase tracking-wider text-[10px]">
                            Strengths for Brief
                          </span>
                          {card.strengths.slice(0, 2).map((s, idx) => (
                            <p key={idx} className="text-on-surface text-[11px] leading-tight flex items-start gap-1">
                              <span className="text-emerald-400">•</span>
                              <span>{s}</span>
                            </p>
                          ))}
                        </div>
                      </div>

                      {/* Select Pill */}
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedToken(card.blind_token);
                        }}
                        className={`w-full py-1.5 rounded-full text-xs font-semibold transition-colors flex items-center justify-center gap-1 ${
                          isSelected
                            ? 'bg-secondary text-on-secondary shadow-sm'
                            : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[14px]">
                          {isSelected ? 'check_circle' : 'radio_button_unchecked'}
                        </span>
                        <span>{isSelected ? 'Selected Candidate' : 'Choose Candidate'}</span>
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* POST-REVEAL VIEW: Revealed Identity & Decision Transparency */
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-300 text-xs font-medium">
                  <span className="material-symbols-outlined text-[20px]">check_circle</span>
                  <span>Identity revealed! You chose based on work quality and style alignment.</span>
                </div>
                <button
                  type="button"
                  onClick={() => setRevealData(null)}
                  className="text-xs text-on-surface-variant hover:text-on-surface underline cursor-pointer"
                >
                  Back to Blind Arena
                </button>
              </div>

              {/* Winner Profile Card */}
              <div className="bg-surface-container-low rounded-xl border border-secondary/30 p-5 space-y-4 shadow-lg">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-surface-container">
                  <div className="flex items-center gap-3">
                    <CreatorAvatar
                      src={revealData.revealed_creator.avatar_url || ''}
                      name={revealData.revealed_creator.display_name}
                      size="lg"
                    />
                    <div>
                      <h3 className="font-bold text-on-surface text-lg">
                        {revealData.revealed_creator.display_name}
                      </h3>
                      <p className="text-xs text-on-surface-variant">
                        {revealData.revealed_creator.specialization} • {revealData.revealed_creator.core_category}
                      </p>
                      <div className="flex items-center gap-2 mt-1 text-xs">
                        <span className="font-bold text-secondary">{revealData.revealed_creator.rating}★ rating</span>
                        <span className="text-on-surface-variant">• {revealData.revealed_creator.delivery_days} days delivery</span>
                        <span className="text-on-surface-variant">• ₹{revealData.revealed_creator.starting_rate.toLocaleString('en-IN')}/day</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      disabled={shortlisted || isShortlisting}
                      onClick={handleShortlistRevealed}
                      className={`px-4 py-2 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer ${
                        shortlisted
                          ? 'bg-secondary-container/20 text-secondary border border-secondary/30'
                          : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[16px]">
                        {shortlisted ? 'bookmark_added' : 'bookmark_add'}
                      </span>
                      <span>{shortlisted ? 'Shortlisted' : 'Shortlist Creator'}</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => onHire(revealData.revealed_creator)}
                      className="px-5 py-2 rounded-full text-xs font-bold bg-primary hover:bg-primary-container text-on-primary shadow-sm flex items-center gap-1 cursor-pointer transition-all"
                    >
                      <span>Proceed to Hire</span>
                      <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </button>
                  </div>
                </div>

                {/* Why This Creator Won */}
                <div className="p-3.5 rounded-xl bg-surface-container text-xs space-y-1">
                  <span className="font-bold text-secondary uppercase tracking-wider text-[11px] flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">trophy</span>
                    Why This Creator Won
                  </span>
                  <p className="text-on-surface leading-relaxed">{revealData.why_this_creator_won}</p>
                </div>

                {/* What the other candidates did better */}
                {revealData.what_others_did_better.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-surface-container/60 border border-outline-variant/20 text-xs space-y-2">
                    <span className="font-bold text-on-surface-variant uppercase tracking-wider text-[11px] flex items-center gap-1">
                      <span className="material-symbols-outlined text-[16px]">balance</span>
                      What Other Candidates Did Better (Fairness Transparency)
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {revealData.what_others_did_better.map((other, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-surface-container-low text-[11px] space-y-1">
                          <span className="font-semibold text-on-surface block">{other.anonymous_id}</span>
                          <ul className="space-y-0.5 text-on-surface-variant">
                            {other.strengths.map((str, sIdx) => (
                              <li key={sIdx} className="flex items-start gap-1">
                                <span className="text-secondary">•</span>
                                <span>{str}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trust Record */}
                <TrustBadges
                  badges={revealData.revealed_creator.badges}
                  reliability={revealData.revealed_creator.reliability}
                  isRisingCreator={revealData.revealed_creator.is_rising_creator}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
