# Marathon Character Select

A fun interactive web app for 4 friends running the Hamburg Marathon 2026. Styled as a video game character selection screen with 3D animations, particle effects, MP3 sound effects, and a tilted map background.

## Tech Stack

- **Frontend**: SvelteKit 5 (Svelte 5 runes: `$props()`, `$state()`, `$derived()`, `$effect()`)
- **Static Adapter**: `@sveltejs/adapter-static` for GitHub Pages deployment
- **Hosting**: GitHub Pages at `pietz.ai/marathon/` (custom domain planned)
- **Future Backend**: FastAPI (Python via `uv`)
- **No Go** — Python only for backend

## Commands

- `npm run dev` — Start dev server (default: http://localhost:5173)
- `npm run build` — Build static site to `build/`
- `npm run preview` — Preview built site

## Deployment

- GitHub Actions workflow at `.github/workflows/deploy.yml`
- Auto-deploys on push to `main`
- Base path `/marathon` set in `svelte.config.js` for GitHub Pages subdirectory
- All static asset references use `$app/paths` `base` prefix
- When switching to a custom domain, change `paths.base` back to `''`

## Characters

Order in the `characters` array matters — it maps 1:1 to `scenePositions` in CharacterSelect. All content is in German.

| Index | Name  | Color (hex) | Subtitle          | Age |
|-------|-------|-------------|-------------------|-----|
| 0     | Tobi  | `#f1c40f` (yellow) | Das Kampfschwein | 33 |
| 1     | Kevin | `#3498db` (blue)   | Das Einzelkind   | 34 |
| 2     | Jonas | `#e74c3c` (red)    | Der Nette Doktor | 34 |
| 3     | Alex  | `#2ecc71` (green)  | Der Ü40-Veteran  | 45 |

### Stats (unified across all characters)
Tempo, Ausdauer, Kampfgeist, Erfahrung, Hilfeleistung

## Scene Layout

Characters are arranged in a **parallelogram** on the tilted map:

```
        Tobi (40%, 33%)           Alex (73%, 33%)
              ↑                        ↑
          +13, +30                 +13, +30
              |                        |
    Kevin (27%, 3%)            Jonas (60%, 3%)
```

Lower row: Kevin, Jonas. Upper row: Tobi, Alex. Characters closer to the bottom have higher z-index so they overlap correctly.

## Map Background

- **Image**: `static/images/hamburg-map.png` — dark-themed map screenshot centered on the Alster
- **CSS Transform**: `perspective(1200px) rotateX(35deg) scale(1.3)` with `transform-origin: center bottom`
- **Anchored to bottom**: `position: absolute; bottom: 0; left: 0;`
- **Sizing**: `width: 100%; height: 160%`
- **Image positioning**: `object-fit: cover; object-position: center 70%`
- **Opacity**: `0.55`
- **Vignette**: radial-gradient overlay fading edges into the `#0a0a1a` background

If the map needs repositioning, adjust `object-position` first, then tilt angle and scale.

## Key Design Decisions

- **Retro gaming aesthetic**: "Press Start 2P" font from Google Fonts, dark theme (`#0a0a1a`), colored glows
- **3D spin on hover**: `requestAnimationFrame` loop with custom easing (NOT CSS animation). Single-face (no back image). Lands at exactly 360° then resets to 0° on next frame to avoid end-jiggle.
- **Particle effects on hover**: Glowing dots in character color, spread across full body height. 8 particles behind, 6 in front. CSS `@keyframes particle-rise` with staggered delays.
- **Rise-up hover effect**: Character + stone platform translate up with `cubic-bezier(0.34, 1.56, 0.64, 1)` overshoot
- **Spotlight glow**: Two radial gradients (top + bottom) appear on hover
- **Title effects**: "Runner" text has a shimmer gradient animation + speed line streaks flying across
- **Sound effects**: MP3 files via Web Audio API. Preloaded as ArrayBuffers on page mount, decoded on first user gesture. Coin sound on hover, character-specific sounds on click.
- **Character cards**: Modal overlay on click with animated stat bars, quote, fun facts ("INTEL"). 0.6s fade-in with delay. Closes on backdrop click or Escape.
- **Responsive**: All character sizes use `clamp()`. Touch detection via `@media (hover: none) and (pointer: coarse)`.

## File Structure

```
src/
├── routes/
│   ├── +page.svelte              # Main page — renders CharacterSelect, preloads audio
│   ├── +layout.svelte            # Global styles, font loading, CSS reset
│   └── +layout.ts                # prerender = true (for static adapter)
├── lib/
│   ├── data/
│   │   └── characters.ts         # Character/CharacterStat interfaces + data array (German)
│   ├── components/
│   │   ├── CharacterSelect.svelte # Stage: title with shimmer+streaks, map scene, character positions, bottom bar
│   │   ├── Character.svelte       # Individual character: 3D spin, hover particles, stone platform, spotlights
│   │   ├── CharacterCard.svelte   # Click-to-open info card modal (stats, quote, intel)
│   │   ├── PlaceholderAvatar.svelte # SVG silhouette placeholder (fallback)
│   │   └── HamburgMap.svelte      # UNUSED — SVG map attempt
│   ├── audio.ts                   # AudioManager: MP3 preload + Web Audio API playback
│   └── assets/
│       └── favicon.svg
static/
├── images/
│   ├── hamburg-map.png            # Dark map screenshot of Hamburg/Alster
│   ├── tobi.png                   # Character photos (transparent background)
│   ├── kevin.png
│   ├── jonas.png
│   └── alex.png
└── sounds/
    ├── coin.mp3                   # Hover sound (all characters)
    ├── whoa.mp3                   # Tobi click sound
    ├── mamma-mia.mp3              # Kevin click sound
    ├── yipee.mp3                  # Jonas click sound
    └── yeahoo.mp3                 # Alex click sound
.github/
└── workflows/
    └── deploy.yml                 # GitHub Actions: build + deploy to GitHub Pages
```

## Pending / Future Work

### Future Features
- Custom domain setup (change `paths.base` to `''`)
- Voting/betting on who finishes first
- FastAPI backend (Python/`uv`)
- Railway deployment

### Cleanup Candidates
- `src/lib/components/HamburgMap.svelte` — replaced by PNG image approach
- `alster_map_data.json` — coordinate data for the SVG map
- `alster_map_research.md` — research notes
