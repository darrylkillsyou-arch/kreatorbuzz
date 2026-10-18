export const CORE_CATEGORIES = [
  'All',
  'AI Video',
  'AI Images',
  '3D & CGI',
  'Product Advertising',
  'Fashion',
  'Social Media',
  'Animation & Motion',
  'Branding & Design',
  'Audio & Voice',
] as const;

export type CoreCategory = (typeof CORE_CATEGORIES)[number];

// Backward-compatible alias for existing imports
export const MARKETPLACE_CATEGORIES = CORE_CATEGORIES;
export type MarketplaceCategory = CoreCategory;

export const CATEGORY_TAXONOMY: Record<
  string,
  {
    sub_specializations: string[];
    styles: string[];
    tools: string[];
  }
> = {
  'AI Video': {
    sub_specializations: [
      'Cinematic Video',
      'Commercial Ads',
      'Short-form & Reels',
      'VFX & Compositing',
      'Music Videos',
      'Documentary Style',
    ],
    styles: ['Cinematic', 'Photorealistic', 'Dramatic', 'Hyperreal', 'Luxury'],
    tools: ['Runway Gen-3', 'Sora', 'Kling AI', 'Luma Dream Machine', 'ComfyUI Flux', 'DaVinci Resolve', 'Premiere Pro'],
  },
  'AI Images': {
    sub_specializations: [
      'Portrait Photography',
      'Editorial Stills',
      'Product Imagery',
      'Concept Art',
      'Digital Art & Matte Painting',
      'Photo Retouching',
    ],
    styles: ['Editorial', 'Hyperreal', 'Photorealistic', 'Surreal', 'Minimal'],
    tools: ['Midjourney v6', 'Flux.1 Pro', 'Stable Diffusion XL', 'ComfyUI', 'Magnific AI', 'Topaz Gigapixel', 'Adobe Firefly'],
  },
  '3D & CGI': {
    sub_specializations: [
      'Product Rendering',
      'Architectural Visualization',
      'Character Modeling',
      'Spatial & Motion CGI',
      'Hard Surface & Industrial',
    ],
    styles: ['Hyperreal', 'Futuristic', 'Clean Commercial', 'Photorealistic', 'Surreal'],
    tools: ['Blender', 'Cinema 4D', 'Unreal Engine 5', 'Octane Render', 'Redshift', 'V-Ray', '3ds Max', 'Houdini AI'],
  },
  'Product Advertising': {
    sub_specializations: [
      'Commercial Campaigns',
      'E-commerce Creatives',
      'Luxury Product Ads',
      'Packaging & Brand Ads',
      'FMCG & Beauty Ads',
    ],
    styles: ['Clean Commercial', 'Luxury', 'Bold', 'Minimal', 'Photorealistic'],
    tools: ['Midjourney v6', 'Runway Gen-3', 'Photoshop AI', 'Adobe Firefly', 'Kling AI', 'Canva AI'],
  },
  'Fashion': {
    sub_specializations: [
      'Editorial Fashion',
      'Haute Couture & Runway',
      'Lookbook Campaigns',
      'Bridal & Indian Couture',
      'Virtual Models & Styling',
      'Textile & Pattern AI',
    ],
    styles: ['High Fashion', 'Luxury', 'Editorial', 'Warm', 'Surreal'],
    tools: ['Midjourney v6', 'Flux.1 Pro', 'Marvelous Designer', 'Photoshop Generative', 'Magnific AI'],
  },
  'Social Media': {
    sub_specializations: [
      'Instagram Creatives & Grids',
      'Reels & Short Video',
      'TikTok & Viral Clips',
      'Content Strategy & Posts',
      'Meme & Community Marketing',
    ],
    styles: ['Bold', 'Playful', 'Clean Commercial', 'Vibrant', 'Minimal'],
    tools: ['CapCut AI', 'Canva AI', 'Kling AI', 'Runway Gen-3', 'Adobe Express', 'Midjourney v6'],
  },
  'Animation & Motion': {
    sub_specializations: [
      'Motion Graphics',
      '2D Animation',
      '3D Animation',
      'Explainer Videos',
      'Anime & Illustration',
      'Logo Animation & Typography',
    ],
    styles: ['Kinetic', 'Playful', 'Bold', 'Futuristic', 'Minimal'],
    tools: ['After Effects', 'Cinema 4D', 'Blender', 'Rive', 'Toon Boom Harmony', 'Runway Gen-3'],
  },
  'Branding & Design': {
    sub_specializations: [
      'Brand Identity & Logos',
      'Packaging Design',
      'Custom Typography',
      'Print & Editorial Design',
      'UI/UX & App Graphics',
      'Infographics & Data Viz',
    ],
    styles: ['Minimal', 'Bold', 'Clean Commercial', 'Luxury', 'Futuristic'],
    tools: ['Adobe Illustrator', 'Figma AI', 'Photoshop AI', 'InDesign', 'Procreate AI', 'Canva AI'],
  },
  'Audio & Voice': {
    sub_specializations: [
      'AI Voice & Voice-over',
      'Sonic Branding & Jingles',
      'Film & Game Sound Design',
      'Podcast Production',
      'Soundtrack & Instrumental Music',
    ],
    styles: ['Cinematic', 'Minimal', 'Futuristic', 'Warm', 'Bold'],
    tools: ['ElevenLabs', 'Suno v3', 'Udio', 'Ableton Live', 'Logic Pro', 'Pro Tools', 'Murf AI', 'Adobe Podcast AI'],
  },
};

export const COMMON_STYLE_TAGS = [
  'All Styles',
  'Cinematic',
  'Luxury',
  'Editorial',
  'Photorealistic',
  'Hyperreal',
  'Futuristic',
  'Clean Commercial',
  'Minimal',
  'Bold',
  'High Fashion',
  'Playful',
  'Surreal',
];

export const COMMON_TOOLS = [
  'All Tools',
  'Midjourney',
  'Flux',
  'Runway',
  'ComfyUI',
  'Sora',
  'Kling',
  'Blender',
  'Cinema 4D',
  'Unreal Engine',
  'After Effects',
  'ElevenLabs',
  'Suno',
  'Photoshop',
  'Illustrator',
  'Figma',
];

export const CATEGORY_ALIASES: Record<string, string> = {
  'ai video': 'AI Video',
  'ai videos': 'AI Video',
  'video': 'AI Video',
  'videos': 'AI Video',
  'ai image': 'AI Images',
  'ai images': 'AI Images',
  'image': 'AI Images',
  'images': 'AI Images',
  '3d': '3D & CGI',
  'cgi': '3D & CGI',
  '3d & cgi': '3D & CGI',
  '3d/cgi': '3D & CGI',
  'product': 'Product Advertising',
  'product ads': 'Product Advertising',
  'product advertising': 'Product Advertising',
  'fashion': 'Fashion',
  'social': 'Social Media',
  'social media': 'Social Media',
  'animation': 'Animation & Motion',
  'animation & motion': 'Animation & Motion',
  'motion': 'Animation & Motion',
  'graphic design': 'Branding & Design',
  'branding': 'Branding & Design',
  'branding & design': 'Branding & Design',
  'branding & graphic design': 'Branding & Design',
  'design': 'Branding & Design',
  'audio': 'Audio & Voice',
  'voice': 'Audio & Voice',
  'audio & voice': 'Audio & Voice',
};
