import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../lib/api';
import type { Creator } from '../types';
import { CreatorCard } from '../components/CreatorCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ProposalModal } from '../components/ProposalModal';
import { CreatorAvatar } from '../components/CreatorAvatar';
import { getCleanImageUrl } from '../lib/images';
import { getCreatorHeroImage } from '../lib/creatorImages';
import {
  CORE_CATEGORIES,
  CATEGORY_TAXONOMY,
  COMMON_STYLE_TAGS,
  COMMON_TOOLS,
  CATEGORY_ALIASES,
} from '../lib/categories';
import { useAuth } from '../contexts/AuthContext';

export const DiscoverPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [creators, setCreators] = useState<Creator[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchPrompt, setSearchPrompt] = useState(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || 'All');
  const [selectedSpecialization, setSelectedSpecialization] = useState('All');
  const [selectedStyle, setSelectedStyle] = useState('All');
  const [selectedTool, setSelectedTool] = useState('All');
  const [shortlisted, setShortlisted] = useState<string[]>([]);
  const [proposalTarget, setProposalTarget] = useState<Creator | null>(null);
  const [visibleCount, setVisibleCount] = useState<number>(24);
  const [isAiWidgetOpen, setIsAiWidgetOpen] = useState(false);
  const creatorsSectionRef = useRef<HTMLElement>(null);

  const categories = [...CORE_CATEGORIES];

  const suggestionChips = [
    'AI Product Video',
    'Fashion',
    '3D & CGI',
    'Audio & Voice',
    'Social Media',
  ];

  // Sync state if URL query params change (category or search)
  useEffect(() => {
    const urlQuery = searchParams.get('search');
    const urlCategory = searchParams.get('category');
    if (urlQuery !== null && urlQuery !== searchPrompt) {
      setSearchPrompt(urlQuery);
    }
    if (urlCategory !== null) {
      const mapped = CATEGORY_ALIASES[urlCategory.toLowerCase().trim()] || urlCategory;
      if (mapped !== selectedCategory) {
        setSelectedCategory(mapped);
      }
    }
  }, [searchParams]);

  useEffect(() => {
    setVisibleCount(24);
    const timer = setTimeout(() => {
      loadCreators();
    }, 150);
    return () => clearTimeout(timer);
  }, [selectedCategory, searchPrompt, selectedSpecialization, selectedStyle, selectedTool]);

  useEffect(() => {
    // Reset secondary filters when core category changes
    setSelectedSpecialization('All');
  }, [selectedCategory]);

  useEffect(() => {
    loadShortlist();
  }, [user]);

  const loadShortlist = async () => {
    if (!user) {
      setShortlisted([]);
      return;
    }
    try {
      const list = await api.shortlist.list();
      setShortlisted(list.map((c) => String(c.id)));
    } catch {
      // ignore
    }
  };

  const loadCreators = async () => {
    setIsLoading(true);
    try {
      const data = await api.creators.list({
        category: selectedCategory === 'All' ? 'All' : selectedCategory,
        query: searchPrompt,
        specialization: selectedSpecialization === 'All' ? undefined : selectedSpecialization,
        style: selectedStyle === 'All' ? undefined : selectedStyle,
        tools: selectedTool === 'All' ? undefined : selectedTool,
      });
      setCreators(data);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (searchPrompt.trim()) {
      setSearchParams({ search: searchPrompt.trim() });
    } else {
      setSearchParams({});
    }
    loadCreators();
    setTimeout(() => {
      creatorsSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  const handleChipClick = (chip: string) => {
    setSearchPrompt(chip);
    setSearchParams({ search: chip });
    setTimeout(() => {
      creatorsSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  const handleClearSearch = () => {
    setSearchPrompt('');
    setSelectedCategory('All');
    setSearchParams({});
  };

  const handleHire = (creator: Creator) => {
    setProposalTarget(creator);
  };

  const handleToggleShortlist = async (creator: Creator) => {
    if (!user) {
      navigate('/login');
      return;
    }
    const cId = String(creator.id);
    if (shortlisted.includes(cId)) {
      setShortlisted((prev) => prev.filter((id) => id !== cId));
      try {
        await api.shortlist.remove(cId);
      } catch {
        setShortlisted((prev) => [...prev, cId]);
      }
    } else {
      setShortlisted((prev) => [...prev, cId]);
      try {
        await api.shortlist.add(cId, creator.user_id ? String(creator.user_id) : undefined);
      } catch {
        setShortlisted((prev) => prev.filter((id) => id !== cId));
      }
    }
  };

  const featured = creators[0] || null;
  const peers = creators.slice(1, 4);

  return (
    <div className="flex flex-col w-full">
      {/* Hero Section */}
      <section className="w-full max-w-7xl mx-auto px-gutter pt-space-xl pb-space-lg">
        <div className="max-w-3xl space-y-space-md">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded-full bg-surface-container-high text-secondary border border-secondary/20">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
            <span className="font-label-sm text-label-sm tracking-wider uppercase font-semibold">
              KreatorBuzz • Create Your Own Buzz
            </span>
          </div>
          <h1 className="font-display text-display text-on-surface tracking-tight leading-[1.08]">
            Discover the people shaping what’s next.
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
            Find elite AI content creators for generative video, hyperreal imagery, 3D CGI, and digital campaigns.
            Hire verified talent and create your own buzz.
          </p>
        </div>

        {/* Intelligent Prompt Discovery Bar */}
        <div className="mt-space-lg max-w-4xl">
          <form
            onSubmit={handleSearch}
            className="bg-surface-container-lowest rounded-full p-2 pl-space-md shadow-md flex items-center justify-between gap-space-sm border border-outline-variant/30"
          >
            <div className="flex items-center gap-space-sm flex-1 min-w-0">
              <span className="material-symbols-outlined text-secondary text-[22px] flex-shrink-0">
                auto_awesome
              </span>
              <input
                className="w-full bg-transparent border-0 outline-none font-body-md text-body-md text-on-surface placeholder:text-outline focus:ring-0 truncate"
                placeholder="Describe what you want to create (e.g., product video, fashion images, 3D ad)..."
                type="text"
                value={searchPrompt}
                onChange={(e) => setSearchPrompt(e.target.value)}
              />
              {searchPrompt && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  aria-label="Clear search prompt"
                  className="p-1 rounded-full text-on-surface-variant hover:text-on-surface hover:bg-surface-container flex-shrink-0 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">close</span>
                </button>
              )}
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-shrink-0 px-space-lg py-3 rounded-full bg-primary text-on-primary font-label-lg text-label-lg hover:bg-surface-container-highest hover:text-on-surface transition-all flex items-center gap-space-xs cursor-pointer disabled:opacity-75"
            >
              <span>{isLoading ? 'Searching...' : 'Find creators'}</span>
              <span className="material-symbols-outlined text-[18px]">
                {isLoading ? 'hourglass_empty' : 'arrow_forward'}
              </span>
            </button>
          </form>

          {/* Suggestion Pill Chips */}
          <div className="flex flex-wrap items-center gap-2 mt-space-sm pt-1">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mr-1">
              Popular searches:
            </span>
            {suggestionChips.map((chip, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleChipClick(chip)}
                className="prompt-chip px-space-sm py-1 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-all cursor-pointer"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Creator Showcase (Asymmetric 12-Column Split) */}
      {featured && (
        <section className="w-full max-w-7xl mx-auto px-gutter py-space-lg">
          <div className="flex items-baseline justify-between mb-space-md">
            <div>
              <span className="font-label-sm text-label-sm text-secondary uppercase tracking-widest block mb-1">
                Featured Creator
              </span>
              <h2 className="font-headline-lg text-headline-lg text-on-surface">
                Project Spotlight
              </h2>
            </div>
            <div className="hidden sm:flex items-center gap-space-xs text-on-surface-variant font-label-md text-label-md">
              <span className="material-symbols-outlined text-[16px] text-secondary">verified_user</span>
              <span>Verified commercial rights</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
            {/* Main Featured Cinematic Showcase Card (Desktop 8-col) */}
            <div className="lg:col-span-8 bg-surface-container-low rounded-xl overflow-hidden shadow-sm flex flex-col group border border-outline-variant/30">
              <div className="relative w-full aspect-[16/9] overflow-hidden bg-surface-container">
                <img
                  alt={featured.hero_title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.02]"
                  src={featured.hero_image || getCleanImageUrl(featured.hero_image)}
                  onError={(e) => { (e.target as HTMLImageElement).src = getCreatorHeroImage(featured.id, featured.specialization, featured.hero_category); }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-primary/80 via-transparent to-transparent"></div>
                <div className="absolute top-4 left-4 flex gap-2">
                  <span className="px-space-sm py-1 rounded-full bg-surface-container-lowest/90 backdrop-blur-md text-on-surface font-label-sm text-label-sm uppercase tracking-wider flex items-center gap-1 shadow-sm">
                    <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span> Open for Projects
                  </span>
                  <span className="px-space-sm py-1 rounded-full bg-surface-container-lowest/90 backdrop-blur-md text-on-surface font-label-sm text-label-sm">
                    {featured.location}
                  </span>
                </div>
                <div className="absolute bottom-4 left-4 right-4 text-on-primary">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-label-md text-label-md uppercase tracking-wider text-secondary-fixed">
                      Master Edition #084
                    </span>
                    <span className="text-xs opacity-60">•</span>
                    <span className="font-label-md text-label-md opacity-90">
                      {featured.hero_category}
                    </span>
                  </div>
                  <h3 className="font-headline-md text-headline-md text-on-primary drop-shadow-sm">
                    {featured.hero_title}
                  </h3>
                </div>
              </div>

              {/* Telemetry & Action Bar */}
              <div className="p-space-lg space-y-space-md">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm">
                  <div className="flex items-center gap-space-sm">
                    <CreatorAvatar src={featured.avatar} name={featured.name} size="lg" />
                    <div>
                      <div className="flex items-center gap-1">
                        <span className="font-label-lg text-label-lg text-on-surface">{featured.name || 'Aarav Studio'}</span>
                        <span className="material-symbols-outlined text-[16px] text-secondary" title="Verified Content Creator">
                          verified
                        </span>
                      </div>
                      <span className="font-body-sm text-body-sm text-on-surface-variant">
                        {featured.specialization}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-space-sm">
                    <Link
                      to={`/creators/${featured.id}`}
                      className="px-space-md py-2 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-lg text-label-lg transition-colors"
                    >
                      View portfolio
                    </Link>
                    <button
                      onClick={() => handleHire(featured)}
                      className="px-space-md py-2 rounded-full bg-primary text-on-primary font-label-lg text-label-lg hover:bg-surface-container-highest hover:text-on-surface transition-colors shadow-sm cursor-pointer"
                    >
                      Hire creator
                    </button>
                  </div>
                </div>

                {/* Telemetry Badges */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm pt-space-xs">
                  <div className="bg-surface-container rounded-lg p-space-sm">
                    <span className="font-label-sm text-label-sm text-on-surface-variant block uppercase">
                      {featured.compatibility_score ? 'Compatibility' : 'Verification'}
                    </span>
                    <span className="font-label-lg text-label-lg text-on-surface flex items-center gap-1 mt-0.5">
                      <span className="material-symbols-outlined text-secondary text-[16px]">
                        {featured.compatibility_score ? 'tune' : 'verified'}
                      </span>
                      {featured.compatibility_score ? `${featured.compatibility_score}% Match` : 'Tier-1 Verified'}
                    </span>
                  </div>
                  <div className="bg-surface-container rounded-lg p-space-sm">
                    <span className="font-label-sm text-label-sm text-on-surface-variant block uppercase">Velocity</span>
                    <span className="font-label-lg text-label-lg text-on-surface flex items-center gap-1 mt-0.5">
                      <span className="material-symbols-outlined text-secondary text-[16px]">bolt</span>
                      {featured.velocity_days}
                    </span>
                  </div>
                  <div className="bg-surface-container rounded-lg p-space-sm">
                    <span className="font-label-sm text-label-sm text-on-surface-variant block uppercase">Licensing</span>
                    <span className="font-label-lg text-label-lg text-on-surface flex items-center gap-1 mt-0.5">
                      <span className="material-symbols-outlined text-secondary text-[16px]">verified</span>
                      Full Commercial
                    </span>
                  </div>
                  <div className="bg-surface-container rounded-lg p-space-sm">
                    <span className="font-label-sm text-label-sm text-on-surface-variant block uppercase">AI Tools Used</span>
                    <span className="font-label-lg text-label-lg text-on-surface flex items-center gap-1 mt-0.5">
                      <span className="material-symbols-outlined text-secondary text-[16px]">neurology</span>
                      {featured.tools_and_pipeline.slice(0, 2).join(' + ')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Curated Peers Column (Desktop 4-col) */}
            <div className="lg:col-span-4 space-y-space-md">
              <div className="flex items-center justify-between">
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Top Creators</h3>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Top Tier</span>
              </div>
              {peers.map((peer) => (
                <div
                  key={peer.id}
                  onClick={() => navigate(`/creators/${peer.id}`)}
                  className="bg-surface-container-low rounded-xl p-space-md shadow-sm hover:shadow-md transition-all group cursor-pointer flex gap-space-md items-center border border-outline-variant/30"
                >
                  <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-surface-container">
                    <img
                      alt={peer.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      src={peer.hero_image || getCleanImageUrl(peer.hero_image)}
                      onError={(e) => { (e.target as HTMLImageElement).src = getCreatorHeroImage(peer.id, peer.specialization); }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <CreatorAvatar src={peer.avatar} name={peer.name} size="xs" />
                      <h4 className="font-label-lg text-label-lg text-on-surface truncate group-hover:text-secondary transition-colors">
                        {peer.name}
                      </h4>
                      <span className="material-symbols-outlined text-[14px] text-secondary">verified</span>
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface-variant truncate">
                      {peer.specialization.split('•')[0]}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-0.5 rounded bg-surface-container font-label-sm text-[10px] text-on-surface uppercase">
                        {peer.sla_index}% SLA
                      </span>
                      <span className="font-label-sm text-secondary font-semibold">
                        ₹{peer.rate_per_day.toLocaleString('en-IN')}/d
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Explore Content Creators Grid */}
      <section ref={creatorsSectionRef} id="explore-creators" className="w-full max-w-7xl mx-auto px-gutter py-space-xl scroll-mt-24">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md mb-space-lg">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-headline-lg text-headline-lg text-on-surface">
                Explore Content Creators
              </h2>
              <span className="px-2.5 py-0.5 rounded-full bg-surface-container font-label-md text-label-md text-secondary font-semibold">
                {creators.length} available
              </span>
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Browse by category, tools, and delivery speed.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-space-md py-1.5 rounded-full font-label-md text-label-md transition-colors cursor-pointer ${
                  selectedCategory === cat
                    ? 'bg-primary text-on-primary font-semibold shadow-sm'
                    : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Secondary Taxonomy Bar: Sub-Specializations (when category is selected) + Style & Tool Selectors */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-space-lg p-3 bg-surface-container-lowest rounded-xl border border-outline-variant/30">
          {/* Sub-specializations (Contextual to Category) */}
          <div className="flex flex-wrap items-center gap-1.5 flex-1 min-w-[280px]">
            <span className="font-label-sm text-xs text-on-surface-variant uppercase tracking-wider font-semibold mr-1">
              {selectedCategory !== 'All' ? `${selectedCategory}:` : 'Specialty:'}
            </span>
            <button
              type="button"
              onClick={() => setSelectedSpecialization('All')}
              className={`px-3 py-1 rounded-full text-xs font-label-sm transition-colors cursor-pointer ${
                selectedSpecialization === 'All'
                  ? 'bg-secondary text-on-secondary font-medium'
                  : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
              }`}
            >
              All
            </button>
            {(selectedCategory !== 'All' && CATEGORY_TAXONOMY[selectedCategory]?.sub_specializations || [
              'Cinematic Video',
              'Portrait Photography',
              'Product Rendering',
              'Editorial Fashion',
              'Motion Graphics',
              'AI Voice',
              'Brand Identity',
            ]).map((sub) => (
              <button
                key={sub}
                type="button"
                onClick={() => setSelectedSpecialization(sub)}
                className={`px-3 py-1 rounded-full text-xs font-label-sm transition-colors cursor-pointer ${
                  selectedSpecialization === sub
                    ? 'bg-secondary text-on-secondary font-medium shadow-sm'
                    : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                }`}
              >
                {sub}
              </button>
            ))}
          </div>

          {/* Secondary Dropdown Selectors: Style & Tools */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Style Filter */}
            <div className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px] text-on-surface-variant">palette</span>
              <select
                value={selectedStyle}
                onChange={(e) => setSelectedStyle(e.target.value)}
                className="bg-surface-container text-xs text-on-surface px-2.5 py-1.5 rounded-lg border border-outline-variant/30 focus:outline-none focus:border-primary cursor-pointer"
                aria-label="Filter by style"
              >
                {COMMON_STYLE_TAGS.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            {/* Tool Filter */}
            <div className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px] text-on-surface-variant">build</span>
              <select
                value={selectedTool}
                onChange={(e) => setSelectedTool(e.target.value)}
                className="bg-surface-container text-xs text-on-surface px-2.5 py-1.5 rounded-lg border border-outline-variant/30 focus:outline-none focus:border-primary cursor-pointer"
                aria-label="Filter by AI tool"
              >
                {COMMON_TOOLS.map((tl) => (
                  <option key={tl} value={tl}>
                    {tl}
                  </option>
                ))}
              </select>
            </div>

            {/* Clear All Filters Button */}
            {(selectedSpecialization !== 'All' || selectedStyle !== 'All' || selectedTool !== 'All') && (
              <button
                type="button"
                onClick={() => {
                  setSelectedSpecialization('All');
                  setSelectedStyle('All');
                  setSelectedTool('All');
                }}
                className="text-xs text-secondary hover:underline cursor-pointer ml-1"
              >
                Reset filters
              </button>
            )}
          </div>
        </div>

        {/* Active Query Pill */}
        {searchPrompt.trim() && (
          <div className="flex items-center gap-2 mb-space-md">
            <span className="font-label-sm text-label-sm text-on-surface-variant">
              Filtered by prompt:
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed font-label-md text-label-md shadow-sm">
              <span className="material-symbols-outlined text-[16px]">search</span>
              <span className="max-w-xs truncate font-medium">"{searchPrompt}"</span>
              <button
                type="button"
                onClick={handleClearSearch}
                aria-label="Remove search filter"
                className="hover:opacity-75 cursor-pointer ml-0.5"
              >
                <span className="material-symbols-outlined text-[14px]">close</span>
              </button>
            </span>
            <button
              type="button"
              onClick={handleClearSearch}
              className="text-xs text-on-surface-variant hover:text-on-surface underline ml-1 cursor-pointer"
            >
              Reset to all
            </button>
          </div>
        )}

        {isLoading ? (
          <LoadingSpinner message="Loading creators..." />
        ) : creators.length === 0 ? (
          <div className="bg-surface-container-low rounded-2xl p-12 text-center border border-outline-variant/30 max-w-xl mx-auto my-8 space-y-4">
            <span className="material-symbols-outlined text-secondary text-[48px]">search_off</span>
            <h3 className="font-headline-md text-headline-md text-on-surface">No creators found</h3>
            <p className="font-body-md text-body-md text-on-surface-variant">
              No verified creators matched "{searchPrompt}". Try searching for broader terms like "video", "fashion", or "3D", or reset your search to view all creators.
            </p>
            <button
              type="button"
              onClick={handleClearSearch}
              className="px-space-lg py-2.5 rounded-full bg-primary text-on-primary font-label-md text-label-md hover:bg-surface-container-highest hover:text-on-surface transition-all cursor-pointer shadow-sm"
            >
              Reset Search & Show All Creators
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-lg">
              {creators.slice(0, visibleCount).map((creator) => (
                <CreatorCard
                  key={creator.id}
                  creator={creator}
                  onHire={handleHire}
                  onShortlist={handleToggleShortlist}
                  isShortlisted={shortlisted.includes(creator.id)}
                />
              ))}
            </div>

            {visibleCount < creators.length && (
              <div className="flex flex-col items-center justify-center pt-space-md gap-2">
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Showing {Math.min(visibleCount, creators.length)} of {creators.length} creators
                </p>
                <button
                  type="button"
                  onClick={() => setVisibleCount((prev) => prev + 24)}
                  className="px-8 py-3 rounded-full bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md text-label-md transition-all border border-outline-variant/40 shadow-sm flex items-center gap-2 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">expand_more</span>
                  Load More Creators ({creators.length - visibleCount} remaining)
                </button>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Private Concierge Desk Banner */}
      <section className="w-full max-w-7xl mx-auto px-gutter pb-space-xl">
        <div className="bg-surface-container-lowest rounded-2xl p-space-lg md:p-space-xl border border-secondary/20 shadow-sm flex flex-col md:flex-row items-center justify-between gap-space-lg">
          <div className="space-y-space-xs max-w-xl">
            <span className="font-label-sm text-label-sm text-secondary uppercase tracking-widest font-semibold">
              Need help planning a project?
            </span>
            <h3 className="font-headline-lg text-headline-lg text-on-surface">
              Need a production team or custom AI model?
            </h3>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Describe your project and we will help match you with creators, estimate a budget, and protect payment in escrow.
            </p>
          </div>
          <Link
            to="/briefs"
            className="px-space-lg py-3 rounded-full bg-primary text-on-primary font-label-lg text-label-lg hover:bg-primary-container hover:text-on-surface transition-all flex items-center gap-space-xs shrink-0 shadow-sm"
          >
            <span>Start a Project</span>
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </Link>
        </div>
      </section>

      {/* Proposal Modal */}
      {proposalTarget && (
        <ProposalModal
          creator={proposalTarget}
          onClose={() => setProposalTarget(null)}
        />
      )}

      {/* KreatorBuzz AI Copilot Floating Entry Point */}
      <div className="fixed bottom-6 right-6 z-40 max-w-sm">
        {isAiWidgetOpen ? (
          <div className="bg-surface-container-lowest text-on-surface rounded-2xl p-space-md border border-secondary/40 shadow-2xl space-y-space-sm animate-fade-in backdrop-blur-md">
            <div className="flex items-center justify-between pb-1 border-b border-surface-container">
              <div className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[18px] text-secondary">auto_awesome</span>
                <span className="font-label-md font-bold text-on-surface">Buzz Copilot</span>
              </div>
              <button
                type="button"
                onClick={() => setIsAiWidgetOpen(false)}
                className="p-1 rounded-full text-on-surface-variant hover:bg-surface-container cursor-pointer"
                title="Minimize"
              >
                <span className="material-symbols-outlined text-[16px]">close</span>
              </button>
            </div>
            <div>
              <h4 className="font-headline-sm text-sm text-on-surface font-semibold">
                Need help finding the right creator?
              </h4>
              <p className="font-body-sm text-[13px] text-on-surface-variant leading-relaxed mt-1">
                Tell Buzz Copilot what you want to create and we’ll structure your brief, milestones, and match top creators.
              </p>
              <span className="text-[11px] text-secondary font-medium block mt-1">
                Create Your Own Buzz.
              </span>
            </div>
            <button
              type="button"
              onClick={() => navigate('/briefs')}
              className="w-full py-2.5 bg-primary text-on-primary font-label-md rounded-full hover:bg-primary-container hover:text-on-surface transition-all flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
              <span>Ask Buzz Copilot</span>
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setIsAiWidgetOpen(true)}
            className="bg-primary hover:bg-primary-container text-on-primary px-4 py-2.5 rounded-full shadow-xl flex items-center gap-2 font-label-md transition-all border border-secondary/30 hover:scale-105 cursor-pointer group"
          >
            <span className="material-symbols-outlined text-[20px] text-secondary group-hover:rotate-12 transition-transform">
              auto_awesome
            </span>
            <span className="font-semibold">Ask Buzz Copilot</span>
          </button>
        )}
      </div>
    </div>
  );
};

