import React from 'react';
import type { AgreedLicensing } from '../../types';

interface AgreedUsageRightsProps {
  licensing?: AgreedLicensing;
}

export const AgreedUsageRights: React.FC<AgreedUsageRightsProps> = ({ licensing }) => {
  const lic = licensing || {
    commercial_use: true,
    usage_types: ['Paid Ads', 'Organic Social', 'Website'],
    territory: 'Worldwide',
    duration_months: 12,
    duration_label: '12 Months',
    platforms: ['Instagram', 'YouTube', 'Website'],
    notes: 'Standard commercial production grant applicable upon final deliverable approval.',
  };

  return (
    <div className="bg-surface-container-low rounded-2xl p-6 border border-surface-container-high/60">
      <div className="flex items-start justify-between gap-4 mb-6 pb-4 border-b border-surface-container-high flex-wrap">
        <div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-2xl">verified_user</span>
            <h3 className="font-title-md text-title-md text-on-surface">Agreed Commercial Usage Rights</h3>
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Confirmed contractual licensing scope established between recruiter and creator for this engagement
          </p>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-full font-label-sm text-label-sm">
          <span className="material-symbols-outlined text-[16px]">check_circle</span>
          <span>Contractually Agreed</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Commercial Use Permission */}
        <div className="bg-surface-container p-4 rounded-xl border border-surface-container-high">
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm mb-1.5">
            <span className="material-symbols-outlined text-[18px] text-primary">storefront</span>
            <span>Commercial Rights</span>
          </div>
          <p className="font-title-sm text-title-sm text-on-surface flex items-center gap-1.5">
            {lic.commercial_use ? (
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                <span className="material-symbols-outlined text-[18px]">verified</span>
                Commercial Use Granted
              </span>
            ) : (
              <span className="text-amber-400 font-semibold">Non-Commercial / Portfolio Only</span>
            )}
          </p>
          <span className="font-label-xs text-on-surface-variant block mt-1">
            Permitted for direct brand advertising & promotion
          </span>
        </div>

        {/* Territory */}
        <div className="bg-surface-container p-4 rounded-xl border border-surface-container-high">
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm mb-1.5">
            <span className="material-symbols-outlined text-[18px] text-primary">public</span>
            <span>Territory</span>
          </div>
          <p className="font-title-sm text-title-sm text-on-surface font-semibold">
            {lic.territory || 'Worldwide'}
          </p>
          <span className="font-label-xs text-on-surface-variant block mt-1">
            Geographic jurisdiction where deliverables may be distributed
          </span>
        </div>

        {/* Duration */}
        <div className="bg-surface-container p-4 rounded-xl border border-surface-container-high">
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm mb-1.5">
            <span className="material-symbols-outlined text-[18px] text-primary">schedule</span>
            <span>Usage Duration</span>
          </div>
          <p className="font-title-sm text-title-sm text-on-surface font-semibold">
            {lic.duration_label || `${lic.duration_months} Months`}
          </p>
          <span className="font-label-xs text-on-surface-variant block mt-1">
            Valid from project completion date
          </span>
        </div>

        {/* Usage Types */}
        <div className="bg-surface-container p-4 rounded-xl border border-surface-container-high md:col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm mb-1.5">
            <span className="material-symbols-outlined text-[18px] text-primary">campaign</span>
            <span>Permitted Usage Types</span>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {(lic.usage_types || ['Paid Ads', 'Organic Social']).map((type, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-surface-container-high text-on-surface font-label-xs rounded-md border border-surface-container-highest"
              >
                {type}
              </span>
            ))}
          </div>
        </div>

        {/* Channels & Platforms */}
        <div className="bg-surface-container p-4 rounded-xl border border-surface-container-high md:col-span-2">
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm mb-1.5">
            <span className="material-symbols-outlined text-[18px] text-primary">devices</span>
            <span>Authorized Channels & Platforms</span>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {(lic.platforms || ['Instagram', 'YouTube', 'Website']).map((plat, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-primary/10 text-primary font-label-xs rounded-md border border-primary/20 flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-[14px]">check</span>
                {plat}
              </span>
            ))}
          </div>
        </div>
      </div>

      {lic.notes && (
        <div className="mt-5 p-3.5 bg-surface-container rounded-xl border border-surface-container-high text-body-sm text-on-surface-variant flex items-start gap-2.5">
          <span className="material-symbols-outlined text-primary text-[20px] shrink-0 mt-0.5">info</span>
          <div>
            <span className="font-semibold text-on-surface">Licensing Scope Provision:</span>
            <p className="mt-0.5">{lic.notes}</p>
          </div>
        </div>
      )}
    </div>
  );
};
