import React from 'react';
import { Link } from 'react-router-dom';

interface ConfirmedBriefCardProps {
  brief?: any;
  fallbackTitle: string;
  fallbackBudget: number;
}

export const ConfirmedBriefCard: React.FC<ConfirmedBriefCardProps> = ({
  brief,
  fallbackTitle,
  fallbackBudget,
}) => {
  const title = brief?.title || fallbackTitle;
  const description = brief?.description || 'No extended brief description provided.';
  const category = brief?.category || brief?.content_type || 'AI Generation';
  const style = brief?.style || 'Cinematic Photorealistic';
  const tools = brief?.required_skills || ['Midjourney v6', 'Runway Gen-3', 'ComfyUI'];
  const deliverables = brief?.deliverables_expected || brief?.deliverable_formats || ['1x 4K Master Video', '2x 9:16 Social Cutdowns'];
  const aspectRatio = brief?.aspect_ratio || '16:9 & 9:16';
  const duration = brief?.duration || '15-30s';
  const budget = brief?.budget || fallbackBudget;
  const deadline = brief?.deadline || 'As agreed in milestone schedule';

  return (
    <div className="bg-surface-container-low rounded-2xl p-6 border border-surface-container-high/60">
      <div className="flex items-start justify-between gap-4 mb-4 pb-3 border-b border-surface-container-high flex-wrap">
        <div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">assignment_turned_in</span>
            <h3 className="font-title-md text-title-md text-on-surface">Confirmed Project Brief</h3>
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
            Single source of truth for scope, technical constraints, and deliverables
          </p>
        </div>
        {brief?.id && (
          <Link
            to={`/briefs?id=${brief.id}`}
            className="inline-flex items-center gap-1 text-primary hover:underline font-label-sm"
          >
            <span>View Original Brief</span>
            <span className="material-symbols-outlined text-[16px]">open_in_new</span>
          </Link>
        )}
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="font-title-sm text-title-sm text-on-surface">{title}</h4>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1 leading-relaxed">
            {description}
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 pt-2">
          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high">
            <span className="font-label-xs text-on-surface-variant block">Category / Type</span>
            <span className="font-title-xs text-title-xs text-on-surface capitalize font-medium">{category}</span>
          </div>

          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high">
            <span className="font-label-xs text-on-surface-variant block">Creative Style</span>
            <span className="font-title-xs text-title-xs text-on-surface font-medium">{style}</span>
          </div>

          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high">
            <span className="font-label-xs text-on-surface-variant block">Total Budget</span>
            <span className="font-title-xs text-title-xs text-primary font-bold">
              ₹{Number(budget).toLocaleString('en-IN')}
            </span>
          </div>

          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high">
            <span className="font-label-xs text-on-surface-variant block">Aspect Ratio</span>
            <span className="font-title-xs text-title-xs text-on-surface font-medium">{aspectRatio}</span>
          </div>

          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high">
            <span className="font-label-xs text-on-surface-variant block">Duration</span>
            <span className="font-title-xs text-title-xs text-on-surface font-medium">{duration}</span>
          </div>

          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high col-span-2 sm:col-span-1 md:col-span-3">
            <span className="font-label-xs text-on-surface-variant block">Target Deadline</span>
            <span className="font-title-xs text-title-xs text-on-surface font-medium">
              {typeof deadline === 'string' && deadline.includes('T')
                ? new Date(deadline).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })
                : deadline}
            </span>
          </div>
        </div>

        {/* AI Tools & Workflows */}
        <div className="pt-2">
          <span className="font-label-xs text-on-surface-variant block mb-1.5 font-medium">Approved AI Tools & Pipeline:</span>
          <div className="flex flex-wrap gap-1.5">
            {tools.map((tool: string, idx: number) => (
              <span
                key={idx}
                className="px-2.5 py-0.5 bg-surface-container-high text-on-surface font-label-xs rounded-md border border-surface-container-highest"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>

        {/* Deliverables Expected */}
        <div className="pt-2">
          <span className="font-label-xs text-on-surface-variant block mb-1.5 font-medium">Deliverables Expected:</span>
          <div className="flex flex-wrap gap-2">
            {(Array.isArray(deliverables) ? deliverables : [deliverables]).map((del: string, idx: number) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-surface-container text-on-surface font-label-xs rounded-md border border-surface-container-high flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[14px] text-primary">check_box</span>
                {del}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
