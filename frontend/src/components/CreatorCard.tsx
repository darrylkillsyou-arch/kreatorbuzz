import React from 'react';
import { Link } from 'react-router-dom';
import type { Creator } from '../types';
import { getCleanImageUrl } from '../lib/images';
import { CreatorAvatar } from './CreatorAvatar';
import { getCreatorHeroImage } from '../lib/creatorImages';

interface CreatorCardProps {
  creator: Creator;
  onHire?: (creator: Creator) => void;
  onShortlist?: (creator: Creator) => void;
  isShortlisted?: boolean;
}

export const CreatorCard: React.FC<CreatorCardProps> = ({
  creator,
  onHire,
  onShortlist,
  isShortlisted = false,
}) => {
  return (
    <div className="creator-card bg-surface-container-low rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col group border border-outline-variant/30">
      {/* Visual Header / Hero Thumbnail */}
      <div className="relative w-full aspect-[4/3] overflow-hidden bg-surface-container">
        <img
          alt={creator.hero_title || creator.name}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          src={creator.hero_image || getCleanImageUrl(creator.hero_image, 'automotiveHero')}
          onError={(e) => {
            (e.target as HTMLImageElement).src = getCreatorHeroImage(creator.id, creator.specialization, creator.hero_category);
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-primary/70 via-transparent to-transparent"></div>

        {/* Top Badges */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
          <span className="px-2.5 py-0.5 rounded-full bg-surface-container-lowest/90 backdrop-blur-md text-on-surface font-label-sm text-label-sm uppercase tracking-wider flex items-center gap-1 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
            {creator.compatibility_score ? `${creator.compatibility_score}% Match` : 'Verified Creator'}
          </span>
          {onShortlist && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                onShortlist(creator);
              }}
              className="w-8 h-8 rounded-full bg-surface-container-lowest/90 backdrop-blur-md flex items-center justify-center text-on-surface hover:text-secondary shadow-sm transition-colors cursor-pointer"
              title={isShortlisted ? 'Shortlisted' : 'Add to Shortlist'}
            >
              <span
                className="material-symbols-outlined text-[18px]"
                style={isShortlisted ? { fontVariationSettings: "'FILL' 1" } : {}}
              >
                bookmark
              </span>
            </button>
          )}
        </div>

        {/* Bottom Title on Image */}
        <div className="absolute bottom-3 left-3 right-3 text-on-primary">
          <span className="font-label-sm text-[10px] uppercase tracking-wider text-secondary-fixed block">
            {creator.hero_category || creator.specialization.split('•')[0]}
          </span>
          <h4 className="font-headline-sm text-[18px] text-on-primary leading-tight truncate">
            {creator.hero_title || creator.name}
          </h4>
        </div>
      </div>

      {/* Creator Details */}
      <div className="p-space-md flex flex-col justify-between flex-1 gap-space-sm">
        <div>
          <div className="flex items-center justify-between gap-2 mb-1">
            <div className="flex items-center gap-2 truncate">
              <CreatorAvatar src={creator.avatar} name={creator.name} size="sm" />
              <span className="font-headline-sm text-[17px] text-on-surface font-medium truncate">
                {creator.name}
              </span>
              {creator.is_verified && (
                <span className="material-symbols-outlined text-[15px] text-secondary flex-shrink-0" title="Verified Content Creator">
                  verified
                </span>
              )}
            </div>
            <span className="font-label-sm text-label-sm text-secondary font-semibold shrink-0">
              ₹{creator.rate_per_day.toLocaleString('en-IN')}/day
            </span>
          </div>

          <p className="font-body-sm text-body-sm text-on-surface-variant line-clamp-2">
            {creator.bio || creator.specialization}
          </p>
        </div>

        {/* Pipeline Tags */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {creator.tools_and_pipeline.slice(0, 3).map((tool, i) => (
            <span
              key={i}
              className="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-label-sm text-[10px] uppercase tracking-wider"
            >
              {tool}
            </span>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-space-xs pt-space-xs border-t border-surface-container-highest/60">
          <Link
            to={`/creators/${creator.id}`}
            className="flex-1 py-1.5 px-3 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md text-center transition-colors"
          >
            View profile
          </Link>
          {onHire ? (
            <button
              onClick={() => onHire(creator)}
              className="flex-1 py-1.5 px-3 rounded-full bg-primary text-on-primary font-label-md text-label-md text-center hover:bg-primary-container hover:text-on-surface transition-all cursor-pointer shadow-sm"
            >
              Hire creator
            </button>
          ) : (
            <Link
              to={`/creators/${creator.id}`}
              className="flex-1 py-1.5 px-3 rounded-full bg-primary text-on-primary font-label-md text-label-md text-center hover:bg-primary-container hover:text-on-surface transition-all shadow-sm"
            >
              Hire
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};
