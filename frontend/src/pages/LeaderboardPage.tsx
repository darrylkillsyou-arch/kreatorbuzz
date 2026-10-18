import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import type {
  MonthlyLeaderboardData,
} from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { getCreatorAvatar } from '../lib/creatorImages';

export const LeaderboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedMonth, setSelectedMonth] = useState<string>('2026-10');
  const [data, setData] = useState<MonthlyLeaderboardData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadMonthlyLeaderboard(selectedMonth);
  }, [selectedMonth]);

  const loadMonthlyLeaderboard = async (month: string) => {
    setIsLoading(true);
    try {
      const res = await api.leaderboard.get({ month });
      setData(res);
    } catch (err) {
      console.error('Failed to load monthly leaderboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrevMonth = () => {
    if (selectedMonth === '2026-10') setSelectedMonth('2026-09');
    else if (selectedMonth === '2026-09') setSelectedMonth('2026-08');
  };

  const handleNextMonth = () => {
    if (selectedMonth === '2026-08') setSelectedMonth('2026-09');
    else if (selectedMonth === '2026-09') setSelectedMonth('2026-10');
  };

  const getMovementBadge = (mov: string) => {
    if (mov.startsWith('+')) {
      return (
        <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          <span className="material-symbols-outlined text-[13px]">arrow_upward</span>
          {mov.slice(1)}
        </span>
      );
    }
    if (mov.startsWith('-')) {
      return (
        <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
          <span className="material-symbols-outlined text-[13px]">arrow_downward</span>
          {mov.slice(1)}
        </span>
      );
    }
    if (mov === '=') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-surface-container text-on-surface-variant">
          =
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-secondary/15 text-secondary border border-secondary/30">
        NEW
      </span>
    );
  };

  const getAwardIcon = (title: string) => {
    switch (title) {
      case 'Creator of the Month':
        return 'workspace_premium';
      case 'Top Rated':
        return 'star';
      case 'Most Productive':
        return 'bolt';
      case 'Delivery Leader':
        return 'task_alt';
      case 'Rising Creator':
        return 'trending_up';
      default:
        return 'military_tech';
    }
  };

  const stats = data?.summary;
  const top10 = data?.top_10 || [];
  const awards = data?.awards || [];
  const categoryChampions = data?.category_champions || [];

  return (
    <div className="relative w-full overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute -top-32 left-1/4 w-[600px] h-[360px] bg-secondary-container/20 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-96 right-10 w-[420px] h-[420px] bg-secondary-fixed/30 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-gutter py-space-lg lg:py-space-xl">
        {/* Section Header with Navigation */}
        <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-space-lg pb-space-lg border-b border-surface-container-high mb-space-md">
          <div className="max-w-2xl space-y-space-xs">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-2 h-2 rounded-full bg-secondary"></span>
              <span className="font-label-sm text-label-sm uppercase tracking-widest text-secondary font-semibold">
                Monthly Performance Arena
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
              Creator Leaderboard
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">
              Who performed best on CODE XERO this month? Dynamic rankings calculated exclusively from real client projects, milestone approvals, and verified reviews.
            </p>
          </div>

          {/* Month Selector Controls */}
          <div className="flex items-center gap-2 bg-surface-container p-1.5 rounded-xl border border-outline-variant/40 shadow-sm flex-shrink-0">
            <button
              type="button"
              onClick={handlePrevMonth}
              disabled={selectedMonth === '2026-08'}
              className="p-2 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Previous Month"
            >
              <span className="material-symbols-outlined text-[18px]">chevron_left</span>
            </button>

            <span className="px-3 py-1 font-headline-sm text-headline-sm text-on-surface font-semibold min-w-[150px] text-center">
              {data?.month_name || selectedMonth}
            </span>

            <button
              type="button"
              onClick={handleNextMonth}
              disabled={selectedMonth === '2026-10'}
              className="p-2 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Next Month"
            >
              <span className="material-symbols-outlined text-[18px]">chevron_right</span>
            </button>
          </div>
        </header>

        {/* Real Monthly Platform Summary Metrics */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-space-md mb-space-xl">
            <div className="p-space-md bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
              <span className="text-xs uppercase tracking-wider text-on-surface-variant font-medium">Completed Projects</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="font-headline-md text-headline-md text-on-surface font-bold">{stats.completed_projects}</span>
                <span className="text-xs text-on-surface-variant">in {data?.month_name.split(' ')[0]}</span>
              </div>
            </div>

            <div className="p-space-md bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
              <span className="text-xs uppercase tracking-wider text-on-surface-variant font-medium">Verified Reviews</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="font-headline-md text-headline-md text-secondary font-bold">{stats.verified_reviews}</span>
                <span className="text-xs text-on-surface-variant">({stats.average_verified_rating.toFixed(1)}★ avg)</span>
              </div>
            </div>

            <div className="p-space-md bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
              <span className="text-xs uppercase tracking-wider text-on-surface-variant font-medium">Active Creators</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="font-headline-md text-headline-md text-on-surface font-bold">{stats.active_creators}</span>
                <span className="text-xs text-on-surface-variant">qualifying</span>
              </div>
            </div>

            <div className="p-space-md bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
              <span className="text-xs uppercase tracking-wider text-on-surface-variant font-medium">Deliverables Completed</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="font-headline-md text-headline-md text-emerald-400 font-bold">{stats.deliverables_completed}</span>
                <span className="text-xs text-on-surface-variant">approved assets</span>
              </div>
            </div>
          </div>
        )}

        {isLoading ? (
          <LoadingSpinner message={`Calculating live rankings for ${data?.month_name || selectedMonth}...`} />
        ) : (
          <>
            {/* ============================================================== */}
            {/* 1. TOP 10 CREATORS — MONTHLY RANKING                          */}
            {/* ============================================================== */}
            <section className="mb-space-xl">
              <div className="flex items-center justify-between pb-space-xs mb-space-md border-b border-surface-container-high">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[22px] text-amber-400">emoji_events</span>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                    Top 10 Creators — {data?.month_name}
                  </h2>
                </div>
                <span className="text-xs text-on-surface-variant">
                  Ranked by 100-point Monthly Performance Score
                </span>
              </div>

              {top10.length === 0 ? (
                <div className="p-space-lg bg-surface-container-low rounded-xl border border-outline-variant/30 text-center">
                  <p className="text-on-surface-variant">No qualifying completed projects recorded for this month.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3">
                  {top10.map((c) => (
                    <article
                      key={c.creator_id}
                      className="p-space-md sm:p-space-lg bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm hover:shadow-md transition-all flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4"
                    >
                      {/* Left Side: Rank, Movement, Identity */}
                      <div className="flex items-start gap-4">
                        <div className="flex flex-col items-center justify-center w-12 h-12 rounded-xl bg-surface-container border border-outline-variant/40 flex-shrink-0">
                          <span className="font-headline-sm text-headline-sm font-bold text-on-surface leading-none">
                            #{String(c.rank).padStart(2, '0')}
                          </span>
                          <div className="mt-1">{getMovementBadge(c.rank_movement)}</div>
                        </div>

                        <img
                          src={c.avatar || getCreatorAvatar(c.name)}
                          alt={c.name}
                          className="w-14 h-14 rounded-full object-cover border border-outline-variant flex-shrink-0"
                        />

                        <div className="space-y-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                              {c.name}
                            </h3>
                            {c.badge && (
                              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-secondary/15 text-secondary border border-secondary/30">
                                {c.badge}
                              </span>
                            )}
                            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-surface-container text-on-surface-variant">
                              {c.primary_category}
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-surface-container-high text-on-surface-variant" title="Independent Profile Completeness Metric">
                              Profile Strength: {c.profile_strength}%
                            </span>
                          </div>

                          <p className="text-xs text-on-surface-variant">
                            {c.specialization}
                          </p>

                          <div className="text-xs text-on-surface-variant pt-0.5">
                            <span className="font-semibold text-secondary">Performance: </span>
                            <span>{c.explanation}</span>
                          </div>
                        </div>
                      </div>

                      {/* Right Side: Score & Operational Breakdown */}
                      <div className="flex flex-wrap items-center gap-4 w-full lg:w-auto justify-between lg:justify-end border-t lg:border-t-0 pt-3 lg:pt-0 border-surface-container">
                        <div className="grid grid-cols-4 gap-2 text-center min-w-[280px]">
                          <div className="p-2 bg-surface-container rounded-lg">
                            <span className="text-[10px] text-on-surface-variant uppercase block">Projects</span>
                            <span className="font-semibold text-on-surface text-sm">{c.metrics.completed_projects}</span>
                          </div>
                          <div className="p-2 bg-surface-container rounded-lg">
                            <span className="text-[10px] text-on-surface-variant uppercase block">Reviews</span>
                            <span className="font-semibold text-secondary text-sm">
                              {c.metrics.verified_rating ? `${c.metrics.verified_rating}★` : 'N/A'}
                            </span>
                          </div>
                          <div className="p-2 bg-surface-container rounded-lg">
                            <span className="text-[10px] text-on-surface-variant uppercase block">Milestones</span>
                            <span className="font-semibold text-on-surface text-sm">{c.metrics.released_milestones}</span>
                          </div>
                          <div className="p-2 bg-surface-container rounded-lg border border-primary/20 bg-primary/5">
                            <span className="text-[10px] text-primary uppercase block font-semibold">Score</span>
                            <span className="font-bold text-primary text-sm">{c.monthly_performance_score}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Link
                            to={`/creators/${c.creator_id}`}
                            className="px-3.5 py-2 rounded-lg bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md text-label-md transition-colors"
                          >
                            View Profile
                          </Link>
                          <button
                            type="button"
                            onClick={() => navigate(`/briefs?creator=${c.creator_id}`)}
                            className="px-3.5 py-2 rounded-lg bg-primary text-on-primary hover:bg-primary-container hover:text-on-surface font-label-md text-label-md transition-colors cursor-pointer shadow-sm"
                          >
                            Hire
                          </button>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            {/* ============================================================== */}
            {/* 2. MONTHLY AWARDS                                             */}
            {/* ============================================================== */}
            {awards.length > 0 && (
              <section className="mb-space-xl">
                <div className="flex items-center gap-2 pb-space-xs mb-space-md border-b border-surface-container-high">
                  <span className="material-symbols-outlined text-[22px] text-secondary">military_tech</span>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                    Monthly Awards — {data?.month_name}
                  </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-md">
                  {awards.map((award, i) => (
                    <div
                      key={i}
                      className="p-space-md bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-secondary/15 text-secondary border border-secondary/30">
                            <span className="material-symbols-outlined text-[15px]">{getAwardIcon(award.award_title)}</span>
                            {award.award_title}
                          </span>
                          <span className="text-xs font-semibold text-emerald-400">{award.score} pts</span>
                        </div>

                        <div className="flex items-center gap-3 my-2">
                          <img
                            src={award.avatar || getCreatorAvatar(award.creator_name)}
                            alt={award.creator_name}
                            className="w-10 h-10 rounded-full object-cover border border-outline-variant"
                          />
                          <div>
                            <Link to={`/creators/${award.creator_id}`} className="font-headline-sm text-base font-semibold text-on-surface hover:text-secondary block">
                              {award.creator_name}
                            </Link>
                            <span className="text-xs text-on-surface-variant">{award.category}</span>
                          </div>
                        </div>

                        <p className="text-xs text-on-surface-variant mt-2 leading-relaxed">
                          {award.reason}
                        </p>
                      </div>

                      <div className="pt-3 mt-3 border-t border-surface-container flex justify-end">
                        <Link
                          to={`/creators/${award.creator_id}`}
                          className="text-xs font-semibold text-secondary hover:underline inline-flex items-center gap-1"
                        >
                          View Creator Portfolio →
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* ============================================================== */}
            {/* 3. CATEGORY CHAMPIONS — TOP 3 ACROSS ALL 9 CATEGORIES          */}
            {/* ============================================================== */}
            <section className="mb-space-xl">
              <div className="flex items-center justify-between pb-space-xs mb-space-md border-b border-surface-container-high">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[22px] text-secondary">category</span>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                    Category Champions — {data?.month_name}
                  </h2>
                </div>
                <span className="text-xs text-on-surface-variant">Top 3 performers in each discipline</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-md">
                {categoryChampions.map((catGroup) => (
                  <div
                    key={catGroup.category}
                    className="p-space-md bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between pb-2 mb-3 border-b border-surface-container">
                        <h3 className="font-headline-sm text-base font-semibold text-on-surface">
                          {catGroup.category}
                        </h3>
                        <span className="text-xs text-on-surface-variant font-medium">
                          {catGroup.creators.length} {catGroup.creators.length === 1 ? 'Leader' : 'Leaders'}
                        </span>
                      </div>

                      {catGroup.creators.length === 0 ? (
                        <p className="text-xs text-on-surface-variant py-4 text-center">No projects in this discipline this month.</p>
                      ) : (
                        <div className="space-y-2.5">
                          {catGroup.creators.map((c, idx) => (
                            <div key={c.creator_id} className="flex items-center justify-between p-2 rounded-lg bg-surface-container hover:bg-surface-container-high transition-colors">
                              <div className="flex items-center gap-2.5 min-w-0">
                                <span className="font-bold text-xs text-secondary w-5 flex-shrink-0">
                                  #{idx + 1}
                                </span>
                                <img
                                  src={c.avatar || getCreatorAvatar(c.name)}
                                  alt={c.name}
                                  className="w-7 h-7 rounded-full object-cover flex-shrink-0 border border-outline-variant"
                                />
                                <div className="truncate">
                                  <Link to={`/creators/${c.creator_id}`} className="text-xs font-semibold text-on-surface hover:text-secondary block truncate">
                                    {c.name}
                                  </Link>
                                  <span className="text-[10px] text-on-surface-variant block">
                                    {c.metrics.completed_projects} projects • {c.metrics.verified_rating}★
                                  </span>
                                </div>
                              </div>

                              <div className="text-right flex-shrink-0 pl-2">
                                <span className="font-bold text-xs text-on-surface block">{c.monthly_performance_score}</span>
                                <span className="text-[10px] text-on-surface-variant">score</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
};
