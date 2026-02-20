# Marathon Character Select

A fun interactive web app for 4 friends running the Hamburg Marathon 2026. Styled as a video game character selection screen with 3D animations, synthesized sound effects, and a tilted map background.

## Tech Stack

- **Frontend**: SvelteKit 5 (Svelte 5 runes: `$props()`, `$state()`, `$derived()`, `$effect()`)
- **Static Adapter**: `@sveltejs/adapter-static` for GitHub Pages deployment
- **Hosting**: GitHub Pages (static), Railway later (when backend is added)
- **Future Backend**: FastAPI (Python via `uv`)
- **No Go** — Python only for backend

## Commands

- `npm run dev` — Start dev server (default: http://localhost:5173)
- `npm run build` — Build static site to `build/`
- `npm run preview` — Preview built site

## Characters

Order in the `characters` array matters — it maps 1:1 to `scenePositions` in CharacterSelect.

| Index | Name  | Color (hex) | Subtitle          | Key Trait                                |
|-------|-------|-------------|--------------------|------------------------------------------|
| 0     | Tobi  | `#f1c40f` (yellow) | The Silent Grinder | Doesn't look sporty, insane mental grit  |
| 1     | Kevin | `#3498db` (blue)   | The Late Arrival   | Always last to show up for everything    |
| 2     | Jonas | `#e74c3c` (red)    | The Nice Doctor    | Actual doctor, medical humor             |
| 3     | Alex  | `#2ecc71` (green)  | The Veteran        | Only one with marathon experience; is 38 but group says 45 |

## Scene Layout

Characters are arranged in a **parallelogram** on the tilted map:

```
        Tobi (44%, 27%)           Alex (68%, 27%)
              ↑                        ↑
          +11, +24                 +11, +24
              |                        |
    Kevin (33%, 3%)            Jonas (57%, 3%)
```

Lower row: Kevin, Jonas. Upper row: Tobi, Alex. The vector from lower→upper is identical (+11% x, +24% bottom) for both pairs, keeping the parallelogram symmetric.

## Map Background

- **Image**: `static/images/hamburg-map.png` — dark-themed map screenshot centered on the Alster, with the Alster positioned in the lower portion of the image so it appears closer with perspective tilt.
- **CSS Transform**: `perspective(1200px) rotateX(35deg) scale(1.3)` with `transform-origin: center bottom`
- **Sizing**: `width: 100%; height: 160%; margin-top: -30%` to extend above viewport
- **Image positioning**: `object-fit: cover; object-position: center 70%`
- **Opacity**: `0.55`
- **Vignette**: radial-gradient overlay fading edges into the `#0a0a1a` background

If the map needs repositioning, adjust `object-position` and `margin-top` first, then tilt angle and scale.

## Key Design Decisions

- **Retro gaming aesthetic**: "Press Start 2P" font from Google Fonts, dark theme (`#0a0a1a`), colored glows
- **3D spin on hover**: `requestAnimationFrame` loop with custom easing (NOT CSS animation). Front = photo, back = AI-generated rear view (both placeholder SVGs for now). Lands at exactly 360° then resets to 0° on next frame to avoid end-jiggle.
- **Rise-up hover effect**: Character + stone platform translate up 30px with `cubic-bezier(0.34, 1.56, 0.64, 1)` overshoot
- **Sound effects**: FM-synthesized "Yahoo!" sounds via Web Audio API (no audio files). Different pitch per character. Initialized on first interaction to respect autoplay policy.
- **Character cards**: Modal overlay on click with animated stat bars, quote, fun facts ("INTEL"). Closes on backdrop click or Escape.

## File Structure

```
src/
├── routes/
│   ├── +page.svelte              # Main page — renders CharacterSelect
│   ├── +layout.svelte            # Global styles, font loading, CSS reset
│   └── +layout.ts                # prerender = true (for static adapter)
├── lib/
│   ├── data/
│   │   └── characters.ts         # Character/CharacterStat interfaces + data array
│   ├── components/
│   │   ├── CharacterSelect.svelte # Stage: title, map scene, character positions, bottom bar
│   │   ├── Character.svelte       # Individual character: 3D spin, hover, stone platform
│   │   ├── CharacterCard.svelte   # Click-to-open info card modal
│   │   ├── PlaceholderAvatar.svelte # SVG silhouette placeholder (used until real photos)
│   │   └── HamburgMap.svelte      # UNUSED — SVG map attempt, kept for reference
│   ├── audio.ts                   # AudioManager: FM synthesis sounds (Yahoo!, click)
│   └── assets/
│       └── favicon.svg
static/
└── images/
    └── hamburg-map.png            # Dark map screenshot of Hamburg/Alster
trivia.md                          # Character trivia for generating card content
alster_map_data.json               # UNUSED — geographic coordinate data from research
alster_map_research.md             # UNUSED — research document
```

## Pending / Future Work

### Next Steps
- **Real photos**: Replace placeholder SVGs with transparent-background photos of each person. Set `imageFront` in `characters.ts` and place images in `static/images/`.
- **AI back views**: Generate rear-view images for 3D spin effect. Set `imageBack` in `characters.ts`.
- **More trivia**: `trivia.md` has TODOs per character — collect more jokes/facts, update `characters.ts`.

### Future Features
- Voting/betting on who finishes first
- FastAPI backend (Python/`uv`)
- Railway deployment
- GitHub Pages deployment via CI

### Cleanup Candidates
These files are unused and can be deleted if no longer needed:
- `src/lib/components/HamburgMap.svelte` — replaced by PNG image approach
- `alster_map_data.json` — coordinate data for the SVG map
- `alster_map_research.md` — research notes
