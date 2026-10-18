import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import type { Creator } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { CreatorAvatar } from '../components/CreatorAvatar';
import { ProposalModal } from '../components/ProposalModal';

export const SavedCreatorsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [savedCreators, setSavedCreators] = useState<Creator[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [proposalTarget, setProposalTarget] = useState<Creator | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadSavedCreators();
  }, [user]);

  const loadSavedCreators = async () => {
    if (!user) {
      setSavedCreators([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const list = await api.shortlist.list();
      setSavedCreators(list);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load saved creators.');
    } finally {
      setIsLoading(false);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleRemove = async (creator: Creator) => {
    const prev = [...savedCreators];
    setSavedCreators((curr) => curr.filter((c) => c.id !== creator.id));
    showToast(`Removed ${creator.name} from Saved Creators.`);

    try {
      await api.shortlist.remove(creator.id);
    } catch (err: any) {
      setSavedCreators(prev);
      setErrorMessage(err.message || 'Failed to remove creator from shortlist.');
    }
  };

  return (
    <div className="flex flex-col w-full min-h-screen">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-secondary text-on-secondary px-5 py-3 rounded-full shadow-2xl font-label-md flex items-center gap-2 border border-secondary-container animate-fade-in">
          <span className="material-symbols-outlined text-[18px]">bookmark_remove</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-gutter w-full pt-space-lg pb-space-2xl">
        {/* Header Section */}
        <section className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pb-space-lg border-b border-outline-variant/20">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2 h-2 rounded-full bg-secondary"></span>
              <span className="font-label-sm text-label-sm uppercase tracking-widest text-secondary font-semibold">
                Saved Creators
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
              Saved Creators & Shortlist
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-2 max-w-2xl">
              Curated shortlist of AI directors, artists, and generative creators for upcoming brand briefs.
            </p>
          </div>

          <div className="flex items-center gap-space-sm shrink-0">
            <Link
              to="/discover"
              className="inline-flex items-center gap-2 px-space-md py-2.5 bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md rounded-full transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">explore</span>
              <span>Discover Creators</span>
            </Link>
          </div>
        </section>

        {/* Error Banner */}
        {errorMessage && (
          <div className="mt-space-md p-space-md bg-error-container/20 border border-error/30 text-on-surface rounded-xl flex items-center justify-between">
            <span className="text-body-sm">{errorMessage}</span>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-on-surface-variant hover:text-on-surface text-xs underline ml-4 cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Body Content */}
        <div className="mt-space-lg">
          {isLoading ? (
            <LoadingSpinner message="Loading your saved creators..." />
          ) : !user ? (
            <div className="bg-surface-container-low rounded-2xl p-space-2xl text-center border border-outline-variant/30 space-y-4 my-8">
              <div className="w-14 h-14 rounded-full bg-surface-container-high text-on-surface-variant mx-auto flex items-center justify-center">
                <span className="material-symbols-outlined text-[28px]">lock</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">Sign in to view Saved Creators</h3>
              <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto">
                Log in as a Recruiter to save, shortlist, and manage creator selections across your sessions.
              </p>
              <button
                onClick={() => navigate('/login')}
                className="inline-flex items-center gap-2 px-space-lg py-2.5 bg-primary text-on-primary font-label-lg rounded-full hover:bg-primary-container hover:text-on-surface transition-all shadow-sm cursor-pointer"
              >
                Sign in to CODE XERO
              </button>
            </div>
          ) : savedCreators.length === 0 ? (
            <div className="bg-surface-container-low rounded-2xl p-space-2xl text-center border border-outline-variant/30 space-y-4 my-8">
              <div className="w-14 h-14 rounded-full bg-surface-container-high text-on-surface-variant mx-auto flex items-center justify-center">
                <span className="material-symbols-outlined text-[28px]">bookmark_border</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">No saved creators yet.</h3>
              <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto">
                Explore the marketplace and click the bookmark icon on any creator card to add them to your shortlist.
              </p>
              <div>
                <Link
                  to="/discover"
                  className="inline-flex items-center gap-2 px-space-lg py-2.5 bg-primary text-on-primary font-label-lg rounded-full hover:bg-primary-container hover:text-on-surface transition-all shadow-sm cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">search</span>
                  <span>Discover Creators</span>
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-lg">
              {savedCreators.map((creator) => {
                const category = creator.hero_category || creator.specialization.split('•')[0].trim();
                const rateFormatted = `₹${(creator.rate_per_day || 1500).toLocaleString('en-IN')}`;

                return (
                  <article
                    key={creator.id}
                    className="bg-surface-container-low rounded-2xl overflow-hidden border border-outline-variant/30 hover:border-outline-variant shadow-sm transition-all flex flex-col justify-between group"
                  >
                    <div>
                      {/* Hero Image Container */}
                      <div className="relative aspect-[16/10] overflow-hidden bg-surface-container">
                        <img
                          src={creator.hero_image || creator.avatar}
                          alt={creator.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                        {/* Top Badges */}
                        <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
                          <span className="px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md text-[11px] font-label-sm uppercase tracking-wider text-white font-semibold">
                            {category}
                          </span>
                          <button
                            onClick={() => handleRemove(creator)}
                            title="Remove from Saved"
                            className="w-8 h-8 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center text-secondary hover:text-error transition-colors cursor-pointer"
                            type="button"
                          >
                            <span
                              className="material-symbols-outlined text-[18px]"
                              style={{ fontVariationSettings: "'FILL' 1" }}
                            >
                              bookmark
                            </span>
                          </button>
                        </div>

                        {/* Rating Overlay */}
                        <div className="absolute bottom-3 right-3 flex items-center gap-1 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-full text-white text-xs font-semibold">
                          <span className="material-symbols-outlined text-amber-400 text-[14px]">star</span>
                          <span>{(creator.rating ?? 5.0).toFixed(1)}</span>
                        </div>
                      </div>

                      {/* Card Body */}
                      <div className="p-space-md">
                        <div className="flex items-center gap-3 mb-2">
                          <CreatorAvatar src={creator.avatar} name={creator.name} size="md" />
                          <div className="min-w-0 flex-1">
                            <h3 className="font-headline-sm text-[18px] text-on-surface font-semibold truncate">
                              {creator.name}
                            </h3>
                            <p className="font-body-sm text-xs text-on-surface-variant truncate">
                              {creator.specialization}
                            </p>
                          </div>
                        </div>

                        {/* Metrics Bar */}
                        <div className="flex items-center justify-between pt-2 border-t border-outline-variant/20 mt-3 text-xs">
                          <span className="text-on-surface-variant">Starting Rate:</span>
                          <span className="font-label-md font-semibold text-on-surface">{rateFormatted}/day</span>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="p-space-md pt-0 flex items-center gap-2">
                      <Link
                        to={`/creators/${creator.id}`}
                        className="flex-1 text-center py-2 px-3 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-xs font-semibold transition-colors"
                      >
                        View Profile
                      </Link>
                      <button
                        onClick={() => setProposalTarget(creator)}
                        className="flex-1 py-2 px-3 rounded-full bg-primary text-on-primary hover:bg-primary-container hover:text-on-surface font-label-md text-xs font-semibold transition-all shadow-sm cursor-pointer"
                        type="button"
                      >
                        Hire Creator
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* Proposal Modal */}
      {proposalTarget && (
        <ProposalModal creator={proposalTarget} onClose={() => setProposalTarget(null)} />
      )}
    </div>
  );
};
