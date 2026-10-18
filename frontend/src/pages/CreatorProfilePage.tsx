import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import type { Creator } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { CreatorAvatar } from '../components/CreatorAvatar';
import { ProposalModal } from '../components/ProposalModal';
import { getCreatorHeroImage } from '../lib/creatorImages';
import { useAuth } from '../contexts/AuthContext';

export const CreatorProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [creator, setCreator] = useState<Creator | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isShortlisted, setIsShortlisted] = useState(false);
  const [isProposalOpen, setIsProposalOpen] = useState(false);
  const [verifiedReviews, setVerifiedReviews] = useState<any[]>([]);

  // Match scores are only valid when derived server-side from a brief recommendation.
  // We do NOT read ?match= from the URL — that param is unauthenticated and spoofable.
  // Match badges are shown on Discover cards only (where the score was computed server-side).

  useEffect(() => {
    if (id) {
      setIsLoading(true);
      api.creators
        .getById(id)
        .then((c) => {
          setCreator(c);
          if (user) {
            api.shortlist.list().then((list) => {
              setIsShortlisted(list.some((item) => String(item.id) === String(c.id)));
            }).catch(() => {});
          }
        })
        .finally(() => setIsLoading(false));

      // Fetch verified creator reviews
      api.workspaces.getCreatorReviews(id).then((revs) => {
        setVerifiedReviews(revs || []);
      }).catch(() => {});
    }
  }, [id, user]);

  const handleHire = () => {
    if (!creator) return;
    setIsProposalOpen(true);
  };

  const handleToggleShortlist = async () => {
    if (!creator) return;
    if (!user) {
      navigate('/login');
      return;
    }
    const cId = String(creator.id);
    if (isShortlisted) {
      setIsShortlisted(false);
      try {
        await api.shortlist.remove(cId);
      } catch {
        setIsShortlisted(true);
      }
    } else {
      setIsShortlisted(true);
      try {
        await api.shortlist.add(cId, creator.user_id ? String(creator.user_id) : undefined);
      } catch {
        setIsShortlisted(false);
      }
    }
  };

  if (isLoading || !creator) {
    return <LoadingSpinner message="Loading creator portfolio..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-gutter py-space-xl w-full">
      {/* Profile Header Card */}
      <div className="bg-surface-container-low rounded-2xl p-space-lg md:p-space-xl border border-outline-variant/30 shadow-sm mb-space-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-space-lg">
          {/* Avatar & Title */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-space-md">
            <CreatorAvatar
              src={creator.avatar}
              name={creator.name}
              size="xl"
              shape="rounded"
              className="w-24 h-24 sm:w-28 sm:h-28 shadow-md"
            />
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-label-sm text-label-sm uppercase tracking-widest text-secondary font-semibold">
                  {creator.tier}
                </span>
                {creator.core_category && (
                  <span className="inline-flex items-center gap-1 text-[11px] text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded-full font-semibold">
                    <span className="material-symbols-outlined text-[14px]">category</span>
                    {creator.core_category}
                  </span>
                )}
                {creator.is_verified && (
                  <span className="inline-flex items-center gap-1 text-[11px] text-secondary bg-secondary-fixed/30 px-2 py-0.5 rounded-full font-semibold">
                    <span className="material-symbols-outlined text-[14px]">verified</span>
                    Verified Creator
                  </span>
                )}
              </div>
              <h1 className="font-display text-[32px] md:text-display text-on-surface tracking-tight leading-tight">
                {creator.name}
              </h1>
              <p className="font-body-md text-body-md text-on-surface-variant">
                {creator.specialization} • {creator.location}
              </p>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-space-sm w-full md:w-auto">
            <button
              onClick={handleToggleShortlist}
              className="flex-1 md:flex-initial px-space-md py-3 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-lg transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <span
                className="material-symbols-outlined text-[18px]"
                style={isShortlisted ? { fontVariationSettings: "'FILL' 1" } : {}}
              >
                bookmark
              </span>
              <span>{isShortlisted ? 'Shortlisted' : 'Shortlist'}</span>
            </button>
            <button
              onClick={handleHire}
              className="flex-1 md:flex-initial px-space-lg py-3 rounded-full bg-primary text-on-primary font-label-lg hover:bg-primary-container hover:text-on-surface transition-all flex items-center justify-center gap-2 shadow-sm cursor-pointer"
            >
              <span>Hire Creator</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </div>

        {/* Telemetry Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-md mt-space-lg pt-space-lg border-t border-surface-container-high">
          <div className="bg-surface-container rounded-xl p-space-md">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase block">
              SLA Delivery Index
            </span>
            <span className="font-headline-sm text-headline-sm text-on-surface font-semibold mt-1 block">
              {creator.sla_index}%
            </span>
          </div>
          <div className="bg-surface-container rounded-xl p-space-md">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase block">
              Completed Projects
            </span>
            <span className="font-headline-sm text-headline-sm text-on-surface font-semibold mt-1 block">
              {creator.commissions_count} Projects
            </span>
          </div>
          <div className="bg-surface-container rounded-xl p-space-md">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase block">
              Velocity
            </span>
            <span className="font-headline-sm text-headline-sm text-on-surface font-semibold mt-1 block">
              {creator.velocity_days || '4–6 Days'}
            </span>
          </div>
          <div className="bg-surface-container rounded-xl p-space-md">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase block">
              Commercial Day Rate
            </span>
            <span className="font-headline-sm text-headline-sm text-secondary font-semibold mt-1 block">
              ₹{Number(creator.rate_per_day).toLocaleString('en-IN')} / day
            </span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Biography & Pipeline + Portfolio */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
        {/* Left Column: Bio & Technical Architecture (4 Cols) */}
        <div className="lg:col-span-4 space-y-space-md">
          {/* Biography */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl border border-outline-variant/30 space-y-space-xs shadow-sm">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">About</h3>
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
              {creator.bio}
            </p>
          </div>

          {/* Specializations & Capabilities */}
          {creator.sub_specializations && creator.sub_specializations.length > 0 && (
            <div className="bg-surface-container-lowest p-space-lg rounded-xl border border-outline-variant/30 space-y-space-sm shadow-sm">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Specializations</h3>
              <div className="flex flex-wrap gap-2">
                {creator.sub_specializations.map((sub, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-secondary-fixed/40 text-on-secondary-fixed rounded-full font-label-sm text-xs font-medium"
                  >
                    {sub}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Pipeline & Weights */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl border border-outline-variant/30 space-y-space-sm shadow-sm">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">AI Tools Used</h3>
            <div className="flex flex-wrap gap-2">
              {creator.tools_and_pipeline.map((tool, i) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-surface-container-high rounded-full font-label-sm text-label-sm text-on-surface uppercase tracking-wider"
                >
                  {tool}
                </span>
              ))}
            </div>
          </div>

          {/* Style Aesthetics */}
          {creator.style_tags && creator.style_tags.length > 0 && (
            <div className="bg-surface-container-lowest p-space-lg rounded-xl border border-outline-variant/30 space-y-space-sm shadow-sm">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Aesthetic Styles</h3>
              <div className="flex flex-wrap gap-2">
                {creator.style_tags.map((style, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-surface-container-highest text-on-surface rounded-full font-label-sm text-xs"
                  >
                    {style}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Prompt Architecture Note */}
          {creator.prompt_architecture && (
            <div className="bg-surface-container p-space-lg rounded-xl border border-secondary/20 space-y-space-xs">
              <span className="font-label-sm text-label-sm text-secondary uppercase tracking-wider font-semibold block">
                How they work
              </span>
              <p className="font-body-sm text-body-sm text-on-surface leading-relaxed">
                {creator.prompt_architecture}
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Featured Works & Portfolio (8 Cols) */}
        <div className="lg:col-span-8 space-y-space-lg">
          <div className="flex items-center justify-between">
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Selected Portfolio Work</h2>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase">
              Archival TIF & 4K ProRes
            </span>
          </div>

          {/* Hero Work Plate */}
          <div className="bg-surface-container-low rounded-2xl overflow-hidden border border-outline-variant/30 shadow-md group">
            <div className="relative aspect-video w-full overflow-hidden bg-surface-container">
              <img
                src={creator.hero_image}
                alt={creator.hero_title || creator.name}
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = getCreatorHeroImage(creator.id, creator.specialization, creator.hero_category);
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-primary/80 via-transparent to-transparent"></div>
              <div className="absolute bottom-6 left-6 right-6 text-on-primary">
                <span className="font-label-sm text-secondary-fixed uppercase tracking-wider block mb-1">
                  Featured Work
                </span>
                <h3 className="font-headline-md text-headline-md text-on-primary">
                  {creator.hero_title || 'Autonomous Cinematic Synthesis'}
                </h3>
              </div>
            </div>
          </div>

          {/* Additional Portfolio Pieces */}
          {creator.featured_works && creator.featured_works.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-md">
              {creator.featured_works.map((work, idx) => (
                <div
                  key={idx}
                  className="bg-surface-container-low rounded-xl overflow-hidden border border-outline-variant/30 shadow-sm group"
                >
                  <div className="relative aspect-[4/3] w-full overflow-hidden bg-surface-container">
                    <img
                      src={work.image}
                      alt={work.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = getCreatorHeroImage(`${creator.id}_${idx}`, creator.specialization, work.tag);
                      }}
                    />
                  </div>
                  <div className="p-space-md">
                    <span className="font-label-sm text-[10px] text-secondary uppercase tracking-wider block">
                      {work.tag || 'Portfolio piece'}
                    </span>
                    <h4 className="font-headline-sm text-[18px] text-on-surface mt-0.5">
                      {work.title}
                    </h4>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Verified Project Reviews Section */}
          <div className="bg-surface-container-low p-space-lg rounded-2xl border border-outline-variant/30 shadow-sm space-y-space-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[24px] text-secondary">verified</span>
                <h3 className="font-headline-md text-headline-md text-on-surface">Verified Project Reviews</h3>
              </div>
              <span className="font-label-sm text-label-sm text-secondary uppercase font-semibold">
                {verifiedReviews.length} {verifiedReviews.length === 1 ? 'Review' : 'Reviews'}
              </span>
            </div>

            {verifiedReviews.length === 0 ? (
              <p className="font-body-md text-body-md text-on-surface-variant py-4 text-center">
                No verified project reviews yet. Completed projects with escrow release unlock verified client reviews.
              </p>
            ) : (
              <div className="space-y-3">
                {verifiedReviews.map((rev) => (
                  <div
                    key={rev.id}
                    className="p-space-md rounded-xl bg-surface-container-lowest border border-outline-variant/20 space-y-2 shadow-sm"
                  >
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="font-label-md text-on-surface font-semibold">
                          {rev.recruiter?.full_name || rev.recruiter?.email || 'Verified Recruiter'}
                        </span>
                        <span className="px-2 py-0.5 rounded-full bg-secondary-fixed/50 text-on-secondary-fixed text-[11px] font-semibold flex items-center gap-1">
                          <span className="material-symbols-outlined text-[12px]">verified</span>
                          <span>Verified Project</span>
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-secondary font-label-md font-bold">
                          {'★'.repeat(rev.rating)}{'☆'.repeat(5 - rev.rating)}
                        </span>
                        <span className="font-body-sm text-[11px] text-on-surface-variant">
                          {new Date(rev.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
                        </span>
                      </div>
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface leading-relaxed">
                      "{rev.comment}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Hire Creator Proposal Modal */}
      {isProposalOpen && creator && (
        <ProposalModal creator={creator} onClose={() => setIsProposalOpen(false)} />
      )}
    </div>
  );
};
