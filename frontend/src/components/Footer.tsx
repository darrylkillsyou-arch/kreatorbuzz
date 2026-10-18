import React from 'react';
import { Link } from 'react-router-dom';
import { BrandMark } from './BrandMark';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-surface-container-low shadow-[0_-1px_6px_rgba(0,0,0,0.02)]">
      <div className="max-w-7xl mx-auto px-gutter py-space-xl">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-space-lg mb-space-xl">
          <div className="md:col-span-5 flex flex-col justify-between pr-0 md:pr-space-lg">
            <div className="space-y-space-md">
              <BrandMark size="sm" />
              <p className="font-body-md text-body-md text-on-surface-variant max-w-sm">
                Creator marketplace for AI images, videos, design, and digital content. Find creators or get hired for your next project.
              </p>
            </div>
            <div className="mt-space-lg">
              <span className="font-label-sm text-label-sm text-secondary uppercase tracking-wider">
                Creator Marketplace • Est. 2024
              </span>
            </div>
          </div>

          <div className="md:col-span-7 grid grid-cols-3 gap-space-md">
            <div className="flex flex-col space-y-space-sm">
              <h3 className="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-space-xs">
                Marketplace
              </h3>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/discover">
                Featured Creators
              </Link>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/briefs">
                AI Project Assistant
              </Link>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/leaderboard">
                Top Creators
              </Link>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/briefs">
                Start a Project
              </Link>
            </div>

            <div className="flex flex-col space-y-space-sm">
              <h3 className="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-space-xs">
                Platform
              </h3>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/workspaces">
                Creator Studio
              </Link>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/community">
                Community
              </Link>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/leaderboard">
                Leaderboard
              </Link>
              <Link className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" to="/register">
                Create Account
              </Link>
            </div>

            <div className="flex flex-col space-y-space-sm">
              <h3 className="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-space-xs">
                Trust & Safety
              </h3>
              <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#provenance">
                Content Provenance
              </a>
              <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#treaties">
                Project Contracts
              </a>
              <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#integrity">
                IP Protection
              </a>
              <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#vault">
                Payment Security
              </a>
            </div>
          </div>
        </div>

        <div className="pt-space-lg flex flex-col sm:flex-row items-center justify-between gap-space-sm border-t border-surface-container-highest/60">
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            © 2025 CODE XERO. Built for AI creators and clients.
          </p>
          <div className="flex items-center gap-space-md">
            <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#terms">
              Terms
            </a>
            <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#privacy">
              Privacy
            </a>
            <a className="font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="#provenance">
              Content Provenance
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
