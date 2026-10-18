import type { Creator, CommunityPost, Workspace, LeaderboardStats } from '../types';

export const INITIAL_CREATORS: Creator[] = [
  {
    id: 'aarav-studio',
    name: 'Aarav Studio',
    avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80',
    specialization: 'AI Videos • Product Ads • Social Media • Milan',
    location: 'Milan, Italy',
    tier: 'Tier-1 Master',
    is_verified: true,
    rate_per_day: 75000,
    sla_index: 99.4,
    commissions_count: 48,
    on_time_rate: 100,
    compatibility_score: 98,
    velocity_days: '4–6 Days Turnaround',
    licensing: 'Full Commercial & Raw Seeds',
    tools_and_pipeline: ['Runway Gen-3', 'Sora Enterprise', 'Custom Latent LoRA', 'ComfyUI'],
    hero_image: 'https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=80',
    hero_title: 'Aethelgard 2026: Hyper-Luxury Kinetic Runway',
    hero_category: 'AI Videos / Product Ads',
    bio: 'Experienced creator of cinematic product videos, runway campaigns, and high-end automotive ads for global brands.',
    prompt_architecture: 'Multi-pass latent upscaling with negative weighting against runway gloss to preserve tactile vellum skin tones and photorealistic vehicular reflection highlights.',
    featured_works: [
      {
        title: 'Aethelgard 2026: Kinetic Runway',
        image: 'https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=80',
        aspect: '16:9',
        tag: 'Automotive'
      },
      {
        title: 'Bespoke Electrified Monolith',
        image: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80',
        aspect: '16:9',
        tag: 'Commercial Film'
      }
    ]
  },
  {
    id: 'meera-visuals',
    name: 'Meera Visuals',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
    specialization: 'Fashion • AI Images • Paris',
    location: 'Paris, France',
    tier: 'Experienced Creator',
    is_verified: true,
    rate_per_day: 50000,
    sla_index: 98.9,
    commissions_count: 36,
    on_time_rate: 99.2,
    compatibility_score: 95,
    velocity_days: '3–5 Days Turnaround',
    licensing: 'Editorial & Worldwide Digital',
    tools_and_pipeline: ['Midjourney v6', 'SDXL Custom Lora', 'Magnific Relit', 'Upscale Pro'],
    hero_image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80',
    hero_title: 'Vespera Nocturne: Volumetric Organza & Bioluminescent Weave',
    hero_category: 'Fashion / AI Images',
    bio: 'Creates photorealistic fashion images, digital fabrics, and garment visuals for European fashion brands and campaigns.',
    prompt_architecture: 'Volumetric ruff collar geometry strictly congruent across 9 render variants with custom drapery tension latents.',
    featured_works: [
      {
        title: 'Vespera Nocturne',
        image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80',
        aspect: '4:5',
        tag: 'Couture'
      }
    ]
  },
  {
    id: 'kabir-motion',
    name: 'Kabir Motion',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
    specialization: '3D & CGI • Animation • London',
    location: 'London, UK',
    tier: 'Verified Master',
    is_verified: true,
    rate_per_day: 45000,
    sla_index: 97.8,
    commissions_count: 29,
    on_time_rate: 98.5,
    compatibility_score: 92,
    velocity_days: '5–7 Days Turnaround',
    licensing: 'Full Commercial Rights',
    tools_and_pipeline: ['Unreal Engine 5.4', 'Gaussian Splatting', 'ControlNet v2', 'NeRF'],
    hero_image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
    hero_title: 'Quantum Fluid Mechanics in Spatial Cinema',
    hero_category: '3D & CGI / Animation',
    bio: 'Creates 3D, CGI, and animation for brand installations, holograms, and cinematic campaigns.',
    prompt_architecture: 'Point-cloud guided flow simulation combined with deep spatial coherence vectors.',
    featured_works: [
      {
        title: 'Liquid Titanium Chronograph',
        image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80',
        aspect: '16:9',
        tag: '3D Motion'
      }
    ]
  },
  {
    id: 'sana-ai-lab',
    name: 'Sana AI Lab',
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80',
    specialization: 'Audio & Voice • Tokyo',
    location: 'Tokyo, Japan',
    tier: 'Acoustic Fellow',
    is_verified: true,
    rate_per_day: 35000,
    sla_index: 99.5,
    commissions_count: 42,
    on_time_rate: 100,
    compatibility_score: 96,
    velocity_days: '2–4 Days Turnaround',
    licensing: 'Synchronized & Master Rights',
    tools_and_pipeline: ['Suno v3.5 Custom Weights', 'Udio Acoustic Stems', 'SpectraSyn', 'Pro Tools'],
    hero_image: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80',
    hero_title: 'Symphonic Synesthesia for Digital Spaces',
    hero_category: 'Audio & Voice',
    bio: 'Creates brand audio, voice, and original soundtracks with spatial mixing for digital spaces.',
    prompt_architecture: 'Multi-layer stem separation with custom harmonic temperament scaling.',
    featured_works: [
      {
        title: 'Holographic Audio Suite',
        image: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80',
        aspect: '16:9',
        tag: 'Audio & Voice'
      }
    ]
  },
  {
    id: 'julian-thorne',
    name: 'Julian Thorne',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80',
    specialization: 'Graphic Design • Product Ads • Berlin',
    location: 'Berlin, Germany',
    tier: 'Verified Master',
    is_verified: true,
    rate_per_day: 55000,
    sla_index: 98.1,
    commissions_count: 24,
    on_time_rate: 97.5,
    compatibility_score: 91,
    velocity_days: '4–5 Days Turnaround',
    licensing: 'Global Commercial',
    tools_and_pipeline: ['Midjourney v6', 'Stable Cascade', 'Lightroom Latent Engine'],
    hero_image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
    hero_title: 'Monumental Monograph Architecture',
    hero_category: 'Graphic Design / Product Ads',
    bio: 'Creates architecture visuals, print campaigns, and monochrome product ads with a strong graphic design style.',
    prompt_architecture: 'Archival monochrome film emulation with organic grain microstructure preservation.',
    featured_works: []
  },
  {
    id: 'maya-lin',
    name: 'Maya Lin',
    avatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=400&q=80',
    specialization: '3D & CGI • Fashion • Stockholm',
    location: 'Stockholm, Sweden',
    tier: 'Emerging Master',
    is_verified: true,
    rate_per_day: 40000,
    sla_index: 96.5,
    commissions_count: 18,
    on_time_rate: 96.0,
    compatibility_score: 89,
    velocity_days: '3–6 Days Turnaround',
    licensing: 'Perpetual Commercial',
    tools_and_pipeline: ['Cinema 4D', 'Flux 1.1 Pro', 'Octane Render', 'SDXL'],
    hero_image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
    hero_title: 'Bio-Organic Jewelry & Fluid Metal',
    hero_category: '3D & CGI / Fashion',
    bio: 'Creates 3D jewelry, fluid metal forms, and fashion accessory visuals for cosmetics and accessory brands.',
    prompt_architecture: 'Zero-gravity fluid viscosity conditioning with anisotropic brushed metal shaders.',
    featured_works: []
  }
];

export const INITIAL_POSTS: CommunityPost[] = [
  {
    id: 'post-1',
    author_id: 'meera-visuals',
    author_name: 'Meera Visuals',
    author_initial: 'M',
    author_title: 'Fashion Content Creator',
    author_location: 'Paris',
    author_badge: 'Experienced Creator',
    badge_class: 'bg-secondary-fixed text-on-secondary-fixed',
    time_ago: '2h ago',
    title: 'Vespera Nocturne: Volumetric Organza & Bioluminescent Weave',
    body: 'Exploration in translating structural digital couture into high-drape translucent fabrics under dramatic chiaroscuro illumination. Layered multi-pass latent upscaling to retain hand-embroidered silver bullion threads while preventing silk compression artifacts.',
    post_type: 'Showcase',
    pipeline_badges: ['Midjourney v6', 'SDXL Custom Lora', 'Magnific Relit', 'Prompt Iterations ×42'],
    media_url: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80',
    media_caption: 'High-fashion model in sculptural ethereal violet and champagne organza gown with botanical embroidery under cinematic chiaroscuro studio lighting',
    prompt_notes: 'Employed negative weighting against standard runway gloss to preserve matte tactile vellum skin tones. Multi-angle seed pinning kept volumetric ruff collar geometry strictly congruent across 9 render variants.',
    likes_count: 1420,
    comments_count: 82,
    is_liked: false,
    is_hireable: true,
    creator_id: 'meera-visuals'
  },
  {
    id: 'post-2',
    author_id: 'kabir-motion',
    author_name: 'Kabir Motion',
    author_initial: 'K',
    author_title: 'Neural Physics & 3D Volumetrics',
    author_location: 'London',
    author_badge: 'Verified Master',
    badge_class: 'bg-surface-container-high text-on-surface',
    time_ago: '5h ago',
    title: 'Temporal Stability in 60fps Anisotropic Fluid Simulations',
    body: 'Breakthrough in cross-frame latent coherence for liquid metal simulations. By locking depth-maps to custom NeRF geometry prior to Kling v2 injection, we achieved zero ghosting across extreme 360 camera spirals.',
    post_type: 'Showcase',
    pipeline_badges: ['Runway Gen-3', 'Unreal Engine 5.4', 'Gaussian Splatting', 'ControlNet Depth'],
    media_url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
    media_caption: 'Fluid metallic dynamics simulation with zero temporal artifacting',
    prompt_notes: 'Keyframe anchor tokens injected every 12 frames to restrict fluid dispersion within bounding volume.',
    likes_count: 890,
    comments_count: 45,
    is_liked: false,
    is_hireable: true,
    creator_id: 'kabir-motion'
  },
  {
    id: 'post-3',
    author_id: 'monolith-brand',
    author_name: 'Monolith Heritage Studio',
    author_initial: 'M',
    author_title: 'Creative Direction Team',
    author_location: 'Geneva',
    author_badge: 'Recruiter / Client',
    badge_class: 'bg-primary text-on-primary',
    time_ago: '1d ago',
    title: 'OPEN BRIEF: 4K Cinematic Horological Film (Escrow: ₹7,00,000)',
    body: 'Looking for an experienced content creator skilled in product close-ups, watch movement physics, and crystal lighting for our upcoming timepiece launch.',
    post_type: 'Open brief',
    pipeline_badges: ['Escrow Secured', 'SLA: 10 Days', '4K Deliverables', 'Macro Lighting'],
    likes_count: 312,
    comments_count: 28,
    is_liked: false,
    is_hireable: false
  }
];

export const INITIAL_WORKSPACES: Workspace[] = [
  {
    id: 'ws-aethelgard',
    brief_id: 'brief-aethelgard',
    brief_ref: 'MC-2026-AET',
    title: 'Aethelgard 2026 Commercial',
    description: 'Haute-couture speculative hypercar launch film marrying organic brutalist architecture, liquid metallic textiles, and neural photorealistic kinetic rendering.',
    brand_id: 'brand-1',
    brand_name: 'Aethelgard Motors',
    creator: INITIAL_CREATORS[0],
    total_budget: 4400,
    stage_tag: 'Production (Milestone 2)',
    category_tag: 'Haute Generative Cine',
    unread_count: 2,
    created_at: 'Oct 14, 2025',
    milestones: [
      {
        id: 'm-1',
        step_number: 1,
        title: 'Moodboard & Visual Paradigm Anchors',
        description: 'Style frames, aesthetic tokens, lighting palette, and character seed locks.',
        status: 'completed',
        amount: 880,
        payout_percentage: 20,
        completion_date: 'Oct 18, 2025'
      },
      {
        id: 'm-2',
        step_number: 2,
        title: 'Animatic & Key Motion Trajectories',
        description: '30-second camera animatic, camera velocity curves, rhythm sync with scratch track.',
        status: 'in_progress',
        amount: 1320,
        payout_percentage: 30
      },
      {
        id: 'm-3',
        step_number: 3,
        title: 'High-Res Multi-Pass Render Sequences',
        description: '4K raw Sora + Kling latent synthesis passes, volumetric relighting, fiber embroidery textures.',
        status: 'pending',
        amount: 1320,
        payout_percentage: 30
      },
      {
        id: 'm-4',
        step_number: 4,
        title: 'Final Color Grade, Audio Master & Rights Escrow Release',
        description: 'Master ProRes 4444 delivery, spatial stems, metadata provenance certificate hash.',
        status: 'pending',
        amount: 880,
        payout_percentage: 20
      }
    ],
    deliverables: [
      {
        id: 'del-1',
        title: 'Aethelgard_RoughCut_v04.mp4',
        type: 'Video / In Progress',
        resolution: '4K ProRes Proxy',
        file_size: '420 MB',
        url: '#',
        status: 'Awaiting Client Review'
      },
      {
        id: 'del-2',
        title: 'Keyframe_Styleframes_Archive.zip',
        type: 'Approved Assets',
        resolution: '3840x2160 PNG',
        file_size: '1.2 GB',
        url: '#',
        status: 'Approved'
      }
    ],
    messages: [
      {
        id: 'msg-1',
        sender_id: 'creator-aarav',
        sender_name: 'Aarav Studio',
        sender_role: 'creator',
        sender_avatar: INITIAL_CREATORS[0].avatar,
        content: 'I have uploaded the Milestone 2 camera trajectory animatic with the new dusk lighting grade. The wet asphalt specular highlights now match the moodboard exactly.',
        created_at: '10:24 AM'
      },
      {
        id: 'msg-2',
        sender_id: 'brand-1',
        sender_name: 'Aethelgard Recruiter',
        sender_role: 'brand',
        content: 'Reviewing the motion now. The vehicle silhouette reveal at 0:14 is breathtaking. Checking audio sync with our team.',
        created_at: '10:48 AM'
      }
    ]
  },
  {
    id: 'ws-sana-spatial',
    brief_id: 'brief-sana',
    brief_ref: 'MC-2026-SAN',
    title: 'Spatial Holographic Audio Suite',
    description: 'Bespoke spatial sound architecture and neural ambient stems for flagship boutique spatial experience in Tokyo.',
    brand_id: 'brand-2',
    brand_name: 'Lumina Tokyo',
    creator: INITIAL_CREATORS[3],
    total_budget: 2850,
    stage_tag: 'Review & Approvals',
    category_tag: 'Neural Audio & Synthetics',
    unread_count: 0,
    created_at: 'Oct 19, 2025',
    milestones: [
      {
        id: 'm-s1',
        step_number: 1,
        title: 'Acoustic Tone Sketches',
        description: 'Generative ambient textures and binaural frequency mapping.',
        status: 'completed',
        amount: 855,
        payout_percentage: 30,
        completion_date: 'Oct 22, 2025'
      },
      {
        id: 'm-s2',
        step_number: 2,
        title: 'Full Spatial Stems Master',
        description: 'Multi-channel 7.1.4 mix and dynamic responsive generative seeds.',
        status: 'completed',
        amount: 1995,
        payout_percentage: 70
      }
    ],
    deliverables: [
      {
        id: 'del-s1',
        title: 'Lumina_SpatialAudio_Stems_Master.zip',
        type: 'Audio 24-bit 96kHz',
        resolution: '7.1.4 Dolby Atmos',
        file_size: '2.4 GB',
        url: '#',
        status: 'Ready for Escrow Release'
      }
    ],
    messages: [
      {
        id: 'msg-s1',
        sender_id: 'creator-sana',
        sender_name: 'Sana AI Lab',
        sender_role: 'creator',
        content: 'All 8 channel stems delivered with lossless FLAC rendering.',
        created_at: 'Yesterday'
      }
    ]
  },
  {
    id: 'ws-meera-lookbook',
    brief_id: 'brief-meera',
    brief_ref: 'MC-2025-MEE',
    title: "Autumn Editorial Lookbook '25",
    description: 'Generative high-fashion campaign with 16 hero images and short motion video clips.',
    brand_id: 'brand-3',
    brand_name: 'Vespera Studio',
    creator: INITIAL_CREATORS[1],
    total_budget: 6200,
    stage_tag: 'Delivered & Escrow Released',
    category_tag: 'Fashion Campaign',
    unread_count: 0,
    created_at: 'Sep 28, 2025',
    milestones: [
      {
        id: 'm-m1',
        step_number: 1,
        title: 'Styleframe Conception',
        description: 'Textile prompts, lighting studies, model face consistency.',
        status: 'completed',
        amount: 1860,
        payout_percentage: 30,
        completion_date: 'Oct 02, 2025'
      },
      {
        id: 'm-m2',
        step_number: 2,
        title: 'Final 16 Look Master Plates & Video Vignettes',
        description: 'High-res archival TIF + 4K MP4 deliverables.',
        status: 'completed',
        amount: 4340,
        payout_percentage: 70,
        completion_date: 'Oct 12, 2025'
      }
    ],
    deliverables: [
      {
        id: 'del-m1',
        title: 'VesperaStudio_Autumn25_CompleteArchive.zip',
        type: 'TIF / 4K Video',
        resolution: 'Ultra-Res Master',
        file_size: '5.8 GB',
        url: '#',
        status: 'Archived & Verified'
      }
    ],
    messages: []
  }
];

export const LEADERBOARD_STATS: LeaderboardStats = {
  median_sla: '99.1%',
  total_briefs: 1482,
  escrow_integrity: '100%'
};
