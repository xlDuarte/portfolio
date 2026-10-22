# Portfolio information architecture — personal entry + two laboratories

This is a **visual and navigation redesign**, not a claim that 111 projects are validated in production.

## Entry points

| Path | Purpose | Design |
|---|---|---|
| `/` | About Gabriel Reis Duarte + two major choices | Minimal white editorial layout, concise biography, direct GitHub/LinkedIn |
| `/industry/` | Retained original industrial/data analytics portfolio | Existing original full site preserved, with one small back-home link |
| `/motorsport/` | Separate automotive/F1 research editorial site | Ice-white + black + cyan, race-track line animation, selected cases and research links |

The F1 trained-research page remains at `/f1-models/`, and all prior `site/cases/`, docs and other paths remain untouched. Existing industry SPA hash routes remain supported under `/industry/#/...`.

## Decision record

The uploaded reference describes an art-directed microsite for a specific F1 driver with unprovided licensed photographs, a proprietary Draco helmet model, HDR, image textures, and a custom Three.js scene. This implementation adapts the **visual direction** (Oswald, Space Grotesk, cyan, dark panels, circuit outlines, restrained motion) to **Gabriel's research portfolio** rather than copying Kimi Antonelli's identity, season statistics or unavailable 3D assets.

No false claims of actual race wins, F1 affiliation, verified professional employment, or validated enterprise/business outcomes have been introduced. Pages are static and lightweight. The track outline is an original graphic illustration, not a representation of an actual licensed circuit layout.

## Validation

- Run `python -m unittest discover -s tests -p test_portal_split.py -v` after syncing the full repository.
- Check link navigation, browser console, 320px / 390px / 768px / 1440px layout, reduced-motion accessibility and keyboard navigation.
- Verify that GitHub Pages `scripts/prepare_pages.py` maps `../` paths appropriately under `/portfolio/` and that Vercel serves the same pages at domain root.
- Validate the full suite and GitHub Actions before production merge.
