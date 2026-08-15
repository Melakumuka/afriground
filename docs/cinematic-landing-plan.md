# Cinematic Landing Page — 3D Satellite & Ground Station

**Goal:** Replace the static hero background of the AfriGround landing page with a cinematic, real-time 3D scene: an Earth globe, a LEO satellite in orbit, a tracking ground station (dish) on the African continent, and a live animated data-link between them — all framed by a slow-moving camera, starfield, atmosphere glow, and bloom post-processing.

---

## 1. Tech Stack Decision

| Option | Verdict |
|---|---|
| **react-three-fiber + drei + postprocessing (Recommended)** | Declarative JSX scene graph, React 19 compatible (`@react-three/fiber@^9`), best DX for maintainability. |
| Vanilla `three` in one canvas component | Fewer deps, but manual lifecycle/scene code; harder to grow later (e.g., telemetry viz reuse). |
| CSS/canvas 2D trickery | Insufficient for a believable 3D satellite/globe. |

**Chosen stack:**

- `three` + `@types/three`
- `@react-three/fiber@^9` (React 19 support)
- `@react-three/drei` (helpers: `Stars`, `Float`, `Html`, `useProgress`)
- `@react-three/postprocessing` + `postprocessing` (Bloom)

> Note: `three` is heavy (~600 KB min+gzip). Keep it out of the main bundle for other pages — the scene must be **lazy-loaded** only on the landing page (see Phase 6).

**Constraints from codebase:**

- Next.js **16.3.0**, React **19.2.8**, Tailwind v4, next-intl. The landing page is an async Server Component — the 3D canvas must live in a `"use client"` component imported via `next/dynamic` with `ssr: false`.
- No 3D libs present yet — all three are new dev/prod deps, added to `apps/web/package.json` via `pnpm`.
- Style conventions: dark slate/cyan/indigo palette, glass panels, `font-mono` accents — the scene should emit cyan/indigo glow to match `globals.css` tokens.

---

## 2. Cinematic Vision & Scene Design

Camera starts low and slow, orbiting the globe **from Africa's perspective** (Africa centered), so the ground station and the satellite link are the visual anchors — matching the product story ("Africa's premier ground station network").

**Scene contents (left → right):**

1. **Starfield** — `drei <Stars>` (dense, faint, cyan-tinted).
2. **Earth globe** — right-of-center, stylized "tech" look: dark ocean, lit continent edges, subtle grid overlay, thin atmosphere halo.
3. **Atmosphere glow** — fresnel-style shader (or a slightly larger sphere with additive blending).
4. **Orbit ring + trail** — a faint LEO orbital ellipse around the globe with a glowing trailing line behind the satellite.
5. **Satellite** — low-poly procedural satellite (bus + 2 solar panels) with emissive cyan accents; orbits continuously (~90 s LEO-like loop).
6. **Ground station** — on Africa (Entoto ENT-1: lat 9.076, lng 38.740 → sphere surface position): parabolic dish built from primitives, on a small platform with a blinking status light.
7. **Link beam** — animated dashed/glowing line between dish and satellite, synced with the orbit so the beam sweeps and flickers as it tracks.
8. **Cinematic camera** — slow auto-drift (orbit + subtle dolly), mouse/touch parallax offset, clamped; `prefers-reduced-motion` disables drift.
9. **Bloom post-processing** — emissive materials and the beam bloom softly (cyan), core elements pop against the dark scene.

**Tone:** dark, high-contrast, emissive cyan/indigo — identical palette to the current hero overlay so the existing gradient overlays, badge, title, and CTAs blend seamlessly over the canvas.

---

## 3. File Structure

```
apps/web/src/
├─ components/
│  ├─ CinematicHero.tsx            # Client wrapper: canvas + overlays + dynamic import + fallback
│  ├─ three/
│  │  ├─ EarthScene.tsx            # <Canvas> root: camera, lights, effects, composition
│  │  ├─ Earth.tsx                 # Globe + rotation + optional texture/grid material
│  │  ├─ Atmosphere.tsx            # Fresnel glow shell
│  │  ├─ Starfield.tsx             # drei <Stars> wrapper
│  │  ├─ OrbitPath.tsx             # LEO ellipse line + animated trail
│  │  ├─ Satellite.tsx             # Procedural satellite mesh, useFrame orbit update
│  │  ├─ GroundStation.tsx         # Dish + platform + status light, tracks satellite
│  │  ├─ LinkBeam.tsx              # Dashed line dish → satellite (animated offset)
│  │  ├─ SceneCameraRig.tsx        # Auto-drift + mouse parallax + scroll fade
│  │  └─ useOrbitalMotion.ts       # ECI position math (true anomaly → position on ellipse)
│  └─ ...existing components unchanged
```

Data reuse: the 6 stations in `StationNetworkMap.tsx` include `lat/lng` — extract `STATIONS` into `src/data/stations.ts` (optional small refactor) so the 3D scene can place the dish at ENT-1's real coordinates. If the refactor is out of scope, hardcode ENT-1 coords in the scene.

---

## 4. Implementation Phases

### Phase 1 — Scaffold
1. Install deps in `apps/web`: `pnpm add three @react-three/fiber@^9 @react-three/drei @react-three/postprocessing postprocessing` and `pnpm add -D @types/three`.
2. Create `three/` folder + `CinematicHero.tsx` skeleton using `next/dynamic(() => import("@/components/three/EarthScene"), { ssr: false })`.
3. Suspense fallback: keep current static hero image as a shimmer/placeholder until the canvas reports ready (`drei useProgress` or `onCreated` → fade in canvas).
4. **Verification gate:** `pnpm --filter @afriground/web lint && build` pass; canvas mounts without WebGL console errors.

### Phase 2 — Static scene (Earth + stars + atmosphere)
1. `EarthScene.tsx`: `<Canvas camera={{ position, fov }}>` with ambient + directional cyan light.
2. `Earth.tsx`: sphere with a dark shader material (subtle grid / fresnel edge lighting). Optionally load an equirectangular earth texture from `/public` (use `useTexture`); if no license-safe texture, use procedural night-lights dots + grid.
3. `Atmosphere.tsx` + `Starfield.tsx`.
4. **Gate:** globe renders centered for Africa with correct orientation (rotate mesh so lat/lng mapping matches ENT-1 placement).

### Phase 3 — Satellite + orbit
1. `useOrbitalMotion.ts`: return position along a parameterized LEO ellipse (semi-major axis ≈ 1.25×globe radius, inclination ≈ 51.6°, period ≈ 90 s), rotating in world space so the orbit passes over East Africa.
2. `Satellite.tsx`: procedural mesh (bus, panels, antenna) with emissive accents; `useFrame` sets group position from the orbital math.
3. `OrbitPath.tsx`: `Line` (from drei) for the ellipse + a fading trail (points behind satellite).
4. **Gate:** satellite completes full orbit, trail follows, no jitter at frame rate.

### Phase 4 — Ground station + link
1. `GroundStation.tsx`: platform cylinder + dish (torus/parabola from `SphereGeometry` scaled) + mast; base at Earth surface at ENT-1 coords, oriented outward (normal of sphere). Add blinking LED (emissive, pulsing).
2. Dish tracking: each frame, `lookAt` the satellite position; the beam originates at dish and ends at satellite.
3. `LinkBeam.tsx`: dashed line (`LineDashedMaterial` with animated `dashOffset`) or thin tube with additive blending; intensity flickers with a noise function; color fades when satellite goes below the station's horizon (dot product of up-vector vs. sat direction).
4. **Gate:** beam visibly tracks satellite through the whole orbit, dips at horizon.

### Phase 5 — Cinematic polish
1. `SceneCameraRig.tsx`: slow auto-orbit + dolly (0.05 Hz), mouse parallax (lerp, clamped ±0.3 rad), touch parallax, and a scroll listener that pulls the camera back / fades opacity as the user scrolls past the hero.
2. `@react-three/postprocessing` **Bloom** (luminance threshold so only emissive/beam/bloom) + subtle Vignette.
3. HUD over canvas (existing badge/title/CTAs) gets entrance animation (staggered fade-up) synced to canvas ready, not on page load.
4. `prefers-reduced-motion`: static camera, slower/no bloom pulse; render one frame and pause the RAF loop.
5. **Gate:** hero looks "cinematic" — smooth 60 fps, graceful degradation on mobile.

### Phase 6 — Integration into landing page
1. In `apps/web/src/app/[locale]/page.tsx` hero section: replace the `<Image src="/hero_ground_station.jpg">` background with `<CinematicHero />` mounted `absolute inset-0 z-0`; keep gradient overlays and content on `z-10`. Remove the hero `<Image>` import.
2. Lazy-load: `CinematicHero` only mounts via `dynamic` + a load trigger; the other 5 sections keep static content, so `three` is **not** in their chunks.
3. Mobile perf: clamp `devicePixelRatio` to 1.5–2, reduce bloom resolution, optional `frameloop="demand"` when hero scrolled out of view (IntersectionObserver).
4. i18n: add any new copy (e.g., "Live simulation" caption, aria-labels) to `messages/en.json` + existing locales.
5. **Gate:** `pnpm --filter @afriground/web build` output shows `three`/`fiber` only in the landing chunk; other pages unaffected.

### Phase 7 — QA & verification
1. `pnpm --filter @afriground/web lint` — no new warnings.
2. `pnpm --filter @afriground/web build` — success; inspect chunk report.
3. Manual test matrix: Chrome/Firefox/Safari, desktop + mobile, touch parallax, reduced-motion emulation, WebGL-disabled fallback (static image stays as fallback via error boundary).
4. Performance: DevTools frame-rate check on mid-range device; bundle-size check vs. baseline.
5. Accessibility: canvas has `aria-hidden` (decorative) or a short role="img" label; all interactive info remains in DOM (existing cards/widgets below).

---

## 5. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Bundle bloat from `three` | Dynamic import + `ssr:false`; verify chunk split in build output |
| WebGL unavailable / GPU poor | Error boundary falls back to the current static hero image |
| React 19 + fiber version mismatch | Pin `@react-three/fiber@^9`; verify peer deps before installing |
| Motion sickness | `prefers-reduced-motion` + slow drift (≤5°/s) |
| Texture licensing (Earth imagery) | Use procedural shader material (grid + night lights) if no free texture |
| SSR hydration mismatch | Entire canvas under `dynamic(..., { ssr: false })` |
| Link/beam artifacts at low fps | Use additive blending + tolerant dash animation; no physics coupling |

---

## 6. Definition of Done

- Hero replaced by lazy-loaded cinematic 3D scene (satellite orbiting Earth, dish tracking, animated beam).
- Static image fallback preserved; reduced-motion and mobile supported.
- Lint + build green; `three` isolated to landing chunk.
- Existing copy/layout/i18n untouched except where needed.
