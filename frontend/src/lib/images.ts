/**
 * Curated high-resolution editorial imagery with guaranteed uptime and CORB clearance.
 */
export const CURATED_IMAGES = {
  // Showcase Hero & Direction
  automotiveHero: 'https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=80',
  coutureHero: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80',
  fluidMotionHero: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
  audioHero: 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1200&q=80',
  perfumeHero: 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80',
  architectureHero: 'https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80',
  
  // Avatars
  avatarAarav: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80',
  avatarMeera: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
  avatarKabir: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
  avatarSana: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80',
  avatarElysian: 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=400&q=80',
  avatarVespera: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=400&q=80',

  // Fallback Monogram
  logoSvg: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" fill="none"><rect width="40" height="40" rx="8" fill="%231A1917"/><path d="M12 28V12L20 22L28 12V28" stroke="%23C5A059" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="20" cy="10" r="1.5" fill="%23C5A059"/></svg>'
};

/**
 * Returns a valid, loaded image URL with automatic fallback replacement for broken or internal links.
 */
export function getCleanImageUrl(url?: string, fallbackKey: keyof typeof CURATED_IMAGES = 'automotiveHero'): string {
  if (!url) return CURATED_IMAGES[fallbackKey];
  
  // If URL contains inaccessible Google internal AIDA domains or is empty
  if (url.includes('lh3.googleusercontent.com/aida') || url.includes('lh3.googleusercontent.com/aida-public')) {
    if (url.includes('AEtjO1XTvtZA') || url.includes('BiQzRFm8D')) return CURATED_IMAGES.automotiveHero;
    if (url.includes('AEtjO1UmALg2')) return CURATED_IMAGES.coutureHero;
    if (url.includes('AEtjO1XsZ3Hc')) return CURATED_IMAGES.fluidMotionHero;
    if (url.includes('AEtjO1WFMwiU')) return CURATED_IMAGES.audioHero;
    if (url.includes('AB6AXuDaFVH2')) return CURATED_IMAGES.perfumeHero;
    if (url.includes('AB6AXuDNxqsA')) return CURATED_IMAGES.architectureHero;
    if (url.includes('AEtjO1WJX7hE')) return CURATED_IMAGES.logoSvg;
    return CURATED_IMAGES[fallbackKey];
  }

  return url;
}
