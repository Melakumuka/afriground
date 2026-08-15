# AfriGround — Distinctive Cinematic Landing Page Implementation Plan

## Creative Direction

**Goal:** Replace the static hero of the AfriGround/AfriGround landing page with a cinematic, real-time 3D scene that communicates **orbital infrastructure**, not a generic "space startup" or AI SaaS aesthetic.

The scene should contain:

- Earth / Africa as the geographic anchor
- A LEO satellite
- A real ground-station dish positioned over East Africa
- A live satellite-to-ground communication link
- Subtle orbital motion
- Technical telemetry / mission-control information
- A restrained starfield
- Atmosphere and carefully controlled emissive effects

The visual concept is:

> **ORBITAL INFRASTRUCTURE — infrastructure connecting spacecraft to Earth.**

The website must feel like it was designed by a specialist aerospace/industrial design studio rather than generated from a generic AI landing-page template.

The 3D scene is therefore only one part of the design system. Typography, layout, data visualization, motion, color, spacing, and copy must all reinforce the same identity.

---

# 1. Design Principles

## 1.1 Primary Design Objective

The page should communicate, within a few seconds:

1. AfriGround operates real space infrastructure.
2. Satellites communicate through ground stations.
3. The network connects spacecraft, ground infrastructure and data.
4. The company is technically credible and operationally serious.
5. The visual identity is distinctive enough to be recognizable without the logo.

## 1.2 Design Personality

The design should feel:

- precise
- engineered
- calm
- technical
- confident
- infrastructural
- premium
- international
- aerospace-grade

It should NOT feel:

- playful SaaS
- generic AI startup
- gaming UI
- crypto/Web3
- sci-fi movie interface
- generic "future of space" marketing site

---

# 2. Anti-Generic AI Design Rules

These rules are mandatory.

## Do NOT use

- purple/blue AI gradients
- neon purple glow
- generic blue SaaS palette
- glassmorphism as the dominant visual language
- floating gradient blobs
- gradient text
- excessive rounded cards
- repeated three-card feature grids
- centered-everything hero
- generic laptop/dashboard mockups
- stock satellite photography
- decorative 3D planets
- excessive stars
- generic glowing world maps
- random floating particles
- generic AI illustrations
- excessive drop shadows
- excessive pill-shaped UI
- "Unlock the Future"
- "Powerful Solutions"
- "Seamless Experience"
- "Next Generation"
- "AI-powered" as empty marketing language

If any of these patterns appear during implementation, replace them with a more domain-specific visual treatment.

---

# 3. AfriGround Visual Identity — "Orbital Infrastructure"

## 3.1 Color Direction

Do NOT inherit the current dark slate/cyan/indigo palette simply because it is convenient.

The existing palette may be retained only where necessary for compatibility, but the new landing page should establish a more distinctive AfriGround identity.

Preferred direction:

| Role | Direction |
|---|---|
| Base | Warm technical off-white / very light mineral tone |
| Primary dark | Graphite / charcoal |
| Secondary | Muted industrial green |
| Signal accent | Controlled signal orange |
| Technical | Neutral grey |
| 3D emissive | Very restrained warm/cool signal glow |

The accent should be used like a real engineering signal indicator, not as a decorative neon effect.

The exact final hex values should be selected during the design phase and stored as design tokens.

## 3.2 Typography

Do not use Inter as the universal font.

Use:

- a distinctive modern grotesk/sans-serif for major headings
- a technical monospace for telemetry, coordinates and engineering metadata

Potential combinations may include:

- Space Grotesk + IBM Plex Mono
- Sora + IBM Plex Mono
- Manrope + JetBrains Mono

The final choice should be made after visual comparison, not arbitrarily.

Use monospace for meaningful data such as:

- UTC
- AOS
- LOS
- AZ
- EL
- SNR
- RF
- X-BAND
- S-BAND
- KA-BAND
- LAT
- LON
- satellite ID
- ground-station ID

---

# 4. Use a Design Skill Before Implementation

Create or use a dedicated frontend/design skill for the project.

Recommended project skill:

`AfriGround Frontend Design`

The skill should encode:

- AfriGround brand personality
- color tokens
- typography
- spacing
- layout principles
- anti-patterns
- motion principles
- technical visualization language
- responsive behavior
- accessibility rules
- browser visual QA process

The coding agent must read/apply this skill before implementing the landing page.

The skill should make the design rules persistent so that OpenCode/DeepSeek does not repeatedly fall back to generic AI landing-page patterns.

---

# 5. Creative Workflow

Do NOT use:

`prompt → generate website → done`

Use:

```text
Creative Direction
        ↓
Design Skill
        ↓
Design Brief
        ↓
Information Architecture
        ↓
Visual System
        ↓
Wireframe
        ↓
3D Scene Design
        ↓
Implementation
        ↓
Browser Rendering
        ↓
Screenshot / Visual QA
        ↓
Design Critique
        ↓
Targeted Refinement
```

Antigravity should be used for:

- browser rendering
- visual inspection
- responsive inspection
- screenshot comparison
- interaction testing
- visual QA

OpenCode + DeepSeek V4 Flash should be used for:

- implementation
- component development
- refactoring
- debugging
- CSS/layout changes
- integration
- targeted visual fixes

The coding agent should not redesign the entire page after every critique. Fix the highest-impact visual problems first.

---

# 6. Tech Stack Decision

| Option | Verdict |
|---|---|
| **react-three-fiber + drei + postprocessing (Recommended)** | Declarative JSX scene graph, React 19 compatible, maintainable and reusable for future telemetry/3D visualizations. |
| Vanilla `three` | Possible, but lifecycle and scene management become harder to maintain. |
| CSS/canvas 2D | Insufficient for the intended realistic orbital/ground-station relationship. |

**Chosen stack:**

- `three`
- `@types/three`
- `@react-three/fiber@^9`
- `@react-three/drei`
- `@react-three/postprocessing`
- `postprocessing`

Keep Three.js isolated to the landing page and lazy-load it.

---

# 7. Existing Codebase Constraints

Current codebase:

- Next.js 16.3.0
- React 19.2.8
- Tailwind v4
- next-intl
- landing page is an async Server Component
- 3D scene must live inside a `"use client"` component
- dynamic import must use `ssr: false`

The scene must be lazy-loaded.

Do not introduce global 3D dependencies into unrelated pages.

Existing functionality and internationalization must remain intact.

---

# 8. Cinematic Scene Concept

## 8.1 Core Composition

The composition should be asymmetrical.

Do not simply place:

`Earth center + satellite top + dish bottom + text centered`.

Instead create a cinematic composition where the 3D infrastructure visually interacts with the HTML content.

Suggested hierarchy:

```text
LEFT / UPPER LEFT
Brand + technical metadata

CENTER
Satellite / orbital path

RIGHT
Earth / Africa

LOWER / AFRICA
Ground station

BETWEEN SATELLITE + GROUND
Live communication link
```

The exact composition may change based on viewport.

---

# 9. Scene Contents

## 9.1 Starfield

Use `drei <Stars>` only as subtle depth.

The starfield must NOT become the dominant visual.

Avoid dense "space movie" stars.

---

## 9.2 Earth

Earth should have a restrained engineering visualization.

Preferred:

- dark/neutral ocean
- subtle geographic boundaries
- restrained continent lighting
- subtle grid
- minimal atmosphere
- no giant glowing Earth cliché

Africa must be clearly recognizable.

East Africa should be the visual anchor.

---

## 9.3 Atmosphere

Use a subtle fresnel-style atmosphere shell or larger sphere with additive blending.

The atmosphere should provide depth rather than a large cyan glow.

---

## 9.4 Ground Station

Use a procedural ground-station dish.

Location:

**Entoto ENT-1**

Approximate coordinates from the current plan:

- latitude: 9.076
- longitude: 38.740

The coordinates should be stored centrally and reused by both the 2D and 3D representations where possible.

The dish should:

- sit naturally on the Earth surface
- point toward the satellite
- track the satellite
- contain a small operational status indicator
- feel like infrastructure, not a toy model

---

## 9.5 Satellite

Use a procedural satellite model:

- spacecraft bus
- two solar panels
- antenna
- small emissive indicators

Avoid an over-detailed cinematic spacecraft model.

The satellite is a communication/infrastructure symbol, not the hero object itself.

---

# 10. Orbital Motion

`useOrbitalMotion.ts` should provide parameterized orbital motion.

Initial visualization:

- LEO-like orbit
- semi-major axis approximately 1.25× globe radius
- inclination approximately 51.6°
- approximately 90-second visual loop
- orbit oriented so the visualization passes over East Africa

This is a **visualization**, not a claim that a real spacecraft is in this exact orbit.

The UI should label simulated values appropriately where there is any possibility of confusion.

---

# 11. Ground-to-Satellite Link

The communication link is one of the most important visual elements.

It should communicate:

**Satellite → RF → Ground Station → AfriGround Network**

Use:

- a thin signal beam
- controlled emissive treatment
- animated packets/dashes
- subtle pulse
- directionality
- connection status

Avoid a giant glowing laser.

The link should look like a professional data visualization.

When the satellite moves below the ground station's horizon, reduce or disable the link.

---

# 12. Technical HUD

The hero should include small amounts of operational information.

Examples:

```text
AfriGround NETWORK

ENT-01
9.076° N
38.740° E

X-BAND
8.4 GHz

AOS
06:41:53 UTC

LOS
06:49:12 UTC

LINK
ACTIVE
```

Use data as visual language, not as fake decoration.

Where values are simulated, explicitly indicate:

`SIMULATION`

or

`LIVE VISUALIZATION`

Do not fabricate customer, satellite or network statistics.

---

# 13. Hero Copy

Avoid generic startup messaging.

The hero should communicate infrastructure.

Possible direction:

> **WE CONNECT SPACE TO EARTH.**

Supporting copy:

> Ground infrastructure, mission operations and satellite data — connected through one network.

The exact final copy should be selected based on the existing product positioning.

CTA direction:

- `Explore the Network`
- `Talk to AfriGround`
- `Mission Control`

Avoid generic:

- Get Started
- Learn More
- Discover the Future

---

# 14. Landing Page Narrative

The landing page should become a visual story rather than a collection of feature cards.

## Section 01 — HERO

**Satellite → Ground → Data**

Asymmetric cinematic 3D scene.

Primary headline.

Technical metadata.

Clear CTA.

---

## Section 02 — NETWORK

Show AfriGround's distributed ground infrastructure.

Instead of cards, use:

- geographic visualization
- station markers
- network lines
- large numerical statistics only where verified
- technical metadata

---

## Section 03 — GROUND INFRASTRUCTURE

Show:

```text
SATELLITE
    ↓
RF
    ↓
GROUND STATION
    ↓
AfriGround NETWORK
    ↓
CLOUD
```

This should be an elegant technical diagram rather than a generic illustration.

---

## Section 04 — MISSION CONTROL

Show an actual operational interface.

Include:

- spacecraft status
- telemetry
- pass schedule
- ground station
- contact state
- alerts
- command queue

Do NOT put the interface inside a laptop mockup.

Let the UI itself occupy the page.

---

## Section 05 — DATA

Narrative:

```text
SIGNAL
 ↓
RECEPTION
 ↓
PROCESSING
 ↓
DATA
 ↓
INTELLIGENCE
```

Use motion to show information flowing through the system.

---

## Section 06 — EARTH INTELLIGENCE

Show how satellite data becomes useful information:

- agriculture
- water
- infrastructure
- disaster response
- maritime
- environment

Use domain-specific visualizations.

Avoid generic AI imagery.

---

## Section 07 — ENGINEERING

Show:

- RF engineering
- ground-segment design
- mission control
- integration
- testing
- LEOP
- ground infrastructure

Use technical diagrams and specification-style layouts.

---

## Section 08 — GLOBAL NETWORK

Use a geographic infrastructure visualization.

Africa should remain a strategic visual anchor.

Do not use a generic glowing world map.

---

## Section 09 — PROOF

Use only verified data.

Possible metrics:

- ground stations
- countries
- satellites
- contacts
- data volume
- coverage
- uptime

If a value is not verified, use a clearly marked placeholder.

---

## Section 10 — CTA

End quietly and confidently.

Possible direction:

> **CONNECT YOUR SPACECRAFT.**

Buttons:

- Talk to AfriGround
- Explore the Platform

---

# 15. Layout System

Every major section should use a different composition.

Preferred:

- asymmetry
- editorial grids
- large typography
- technical diagrams
- full-width visual sections
- deliberate whitespace
- occasional dense information zones
- horizontal information systems
- vertical data streams

Avoid repetitive:

```text
ICON
HEADING
PARAGRAPH
BUTTON
```

and:

```text
CARD CARD CARD
```

---

# 16. Motion System

Motion should explain the system.

Use motion inspired by:

- orbital movement
- antenna tracking
- RF propagation
- network routing
- data transfer
- telemetry updates

Do NOT animate everything.

Do NOT use random floating particles.

Use easing and slow movement.

Support:

`prefers-reduced-motion`

Reduced-motion mode should:

- stop camera drift
- reduce or disable pulsing
- reduce bloom animation
- preserve the core information
- remain fully usable

---

# 17. File Structure

```text
apps/web/src/
├─ components/
│  ├─ CinematicHero.tsx
│  ├─ AfriGroundTechnicalHUD.tsx
│  ├─ NetworkVisualization.tsx
│  ├─ MissionControlPreview.tsx
│  ├─ DataFlowVisualization.tsx
│  ├─ three/
│  │  ├─ EarthScene.tsx
│  │  ├─ Earth.tsx
│  │  ├─ Atmosphere.tsx
│  │  ├─ Starfield.tsx
│  │  ├─ OrbitPath.tsx
│  │  ├─ Satellite.tsx
│  │  ├─ GroundStation.tsx
│  │  ├─ LinkBeam.tsx
│  │  ├─ SceneCameraRig.tsx
│  │  └─ useOrbitalMotion.ts
│  └─ ...existing components
│
├─ data/
│  └─ stations.ts
│
└─ styles/
   └─ ...existing styles
```

Reuse the existing station data.

The 6 stations currently used by `StationNetworkMap.tsx` should be extracted into `src/data/stations.ts` if practical.

Do not duplicate station coordinates.

---

# 18. Implementation Phases

## Phase 0 — Design System First

Before coding:

1. Inspect the existing landing page.
2. Inspect current brand assets.
3. Create the AfriGround visual direction.
4. Select typography.
5. Define color tokens.
6. Define spacing and grid.
7. Define motion rules.
8. Define anti-patterns.
9. Create a section-by-section composition plan.

**Gate:** do not begin 3D implementation until the visual system is documented.

---

## Phase 1 — Scaffold

1. Install:

```bash
pnpm add three @react-three/fiber@^9 @react-three/drei @react-three/postprocessing postprocessing
pnpm add -D @types/three
```

2. Create the `three/` folder.
3. Create `CinematicHero.tsx`.
4. Use dynamic import:

```tsx
dynamic(() => import("@/components/three/EarthScene"), {
  ssr: false,
})
```

5. Preserve the existing static hero image as the loading/failure fallback.

6. Gate:

```bash
pnpm --filter @afriground/web lint
pnpm --filter @afriground/web build
```

---

## Phase 2 — Static Scene

Build:

- Earth
- atmosphere
- subtle stars
- Africa orientation
- ground-station anchor

Gate:

- Africa orientation correct
- ENT-1 maps correctly
- no WebGL errors
- no visual over-glow

---

## Phase 3 — Satellite + Orbit

Implement:

- orbital math
- satellite
- orbit path
- restrained trail

Gate:

- smooth movement
- no jitter
- orbit remains visually coherent
- satellite never obscures important HTML copy

---

## Phase 4 — Ground Station + Link

Implement:

- dish
- tracking
- beam
- horizon visibility
- communication state

Gate:

- dish tracks satellite
- link follows satellite
- link disappears/reduces at horizon
- no giant laser effect

---

## Phase 5 — Technical HUD

Add:

- satellite ID
- ground station ID
- frequency
- AOS
- LOS
- UTC
- status

Mark simulated information appropriately.

Gate:

Technical information improves the composition instead of cluttering it.

---

## Phase 6 — Cinematic Polish

Implement:

- slow camera drift
- subtle parallax
- restrained bloom
- vignette only if necessary
- entrance animation
- scroll behavior
- reduced-motion behavior

The original plan proposed approximately 0.05 Hz camera motion and clamped mouse parallax. Keep movement subtle enough that the page feels like infrastructure rather than a game.

---

## Phase 7 — Landing Page Integration

Replace the existing static hero background with `<CinematicHero />`.

Keep:

- HTML content
- i18n
- accessibility
- CTA behavior
- gradient overlays only where they improve readability

Do not allow the 3D scene to overpower the content.

---

## Phase 8 — Visual QA

Antigravity must render and inspect:

- 1440px desktop
- 1280px desktop
- 1024px
- 768px
- 390px mobile

Check:

1. Does this look AI-generated?
2. Does it look like a generic SaaS website?
3. Is the AfriGround visual identity recognizable?
4. Is the hero too dark?
5. Is the 3D scene too dominant?
6. Are there too many cards?
7. Are gradients excessive?
8. Is typography distinctive?
9. Does the page communicate satellite infrastructure?
10. Do technical elements feel authentic?
11. Is mobile still visually strong?
12. Is motion useful rather than decorative?

If the answer to #1 or #2 is yes, identify the offending patterns and redesign them.

---

# 19. Visual QA Prompt for Antigravity / OpenCode

Use this after the first implementation:

```text
Do not modify the code yet.

Act as a hostile senior creative director reviewing the rendered AfriGround landing page.

The objective is to identify everything that makes the website look AI-generated, template-derived, generic SaaS, or visually predictable.

Inspect the rendered page in the browser.

Pay particular attention to:

- color palette
- typography
- hero composition
- section repetition
- card usage
- gradients
- border radius
- shadows
- spacing
- 3D scene
- technical visualizations
- copy
- motion
- responsive behavior

Compare the design against the project's "Orbital Infrastructure" design direction.

Return:

1. Top 10 problems
2. Severity for each problem
3. Why each problem makes the page feel generic
4. Specific replacement
5. Which changes have the highest visual impact

Do not make changes until the critique is complete.
```

Then run a second prompt:

```text
Implement only the highest-impact visual improvements from the critique.

Do not rewrite the entire page.

Preserve components and functionality that are already strong.

Prioritize:

1. distinctive visual identity
2. typography
3. composition
4. color
5. reduction of generic AI patterns
6. meaningful technical visualization

After implementation, render the page again and perform another visual QA pass.
```

---

# 20. Performance Requirements

## Desktop

Target:

- smooth 60 FPS on capable hardware
- minimal main-thread blocking
- lazy-loaded Three.js

## Mobile

- clamp devicePixelRatio to approximately 1.5–2
- reduce bloom resolution
- reduce particle count
- reduce geometry complexity
- reduce camera movement
- disable unnecessary post-processing
- pause animation when hero leaves viewport

Use IntersectionObserver where practical.

---

# 21. Fallback

The existing static hero image remains the fallback.

Fallback conditions:

- WebGL unavailable
- GPU failure
- Three.js loading failure
- low-performance mode
- user preference
- unexpected runtime error

The website must remain completely functional without WebGL.

---

# 22. Accessibility

The 3D scene is decorative unless specific information is intentionally exposed.

Use:

- `aria-hidden="true"` for purely decorative canvas
- accessible HTML equivalents for important information
- visible keyboard-accessible CTAs
- readable contrast
- reduced-motion support

Never make essential content available only inside WebGL.

---

# 23. Internationalization

Any new user-facing text must go through the existing `next-intl` message system.

Potential strings:

- Network status
- Live visualization
- Simulation
- Ground station
- Satellite
- AOS
- LOS
- Link active
- Explore network
- Talk to AfriGround

Do not hardcode customer-facing copy in components.

---

# 24. Definition of Done

The implementation is complete only when:

- [ ] Hero contains the cinematic 3D satellite/ground-station relationship.
- [ ] Africa is clearly the geographic anchor.
- [ ] ENT-1 coordinates are correctly represented.
- [ ] Satellite orbit is smooth.
- [ ] Ground station tracks the satellite.
- [ ] Link beam responds to the satellite's visibility.
- [ ] Technical HUD communicates real space-operation concepts.
- [ ] 3D scene feels engineered rather than decorative.
- [ ] Color palette is distinctive and not generic AI purple/blue.
- [ ] Typography is distinctive.
- [ ] Generic SaaS card repetition is avoided.
- [ ] No unnecessary glassmorphism or gradient blobs.
- [ ] Hero is asymmetric and visually memorable.
- [ ] Other sections have varied compositions.
- [ ] Mission Control is represented as an operational interface rather than a laptop mockup.
- [ ] Network visualization feels like infrastructure.
- [ ] Motion has a functional/semantic reason.
- [ ] Mobile layout is intentionally recomposed.
- [ ] `prefers-reduced-motion` works.
- [ ] WebGL fallback works.
- [ ] `pnpm --filter @afriground/web lint` passes.
- [ ] `pnpm --filter @afriground/web build` passes.
- [ ] Three.js remains isolated to the landing-page chunk.
- [ ] No fabricated business/customer/network statistics.
- [ ] Final browser screenshots have passed the visual QA process.
- [ ] The result does not resemble a generic AI-generated landing page.

---

# 25. Final Creative Standard

The final test is not:

> "Does this look beautiful?"

The final test is:

> **"Could somebody recognize AfriGround's website if the logo and company name were removed?"**

The intended answer should be **yes**.

The design should communicate:

**SPACECRAFT**

↓

**RF**

↓

**GROUND INFRASTRUCTURE**

↓

**NETWORK**

↓

**MISSION OPERATIONS**

↓

**DATA**

↓

**INTELLIGENCE**

That is the visual story of AfriGround.
