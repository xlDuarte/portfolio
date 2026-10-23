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

No false claims of actual race wins, F1 affiliation, verified professional employment, or validated enterprise/business outcomes have been introduced. The entry portal and industrial application remain static. The Motorsport route now has a full animation runtime (Three.js/WebGL, Lenis, shared ticker, shaders, 3D/procedural helmet, scrolling map, seven plates, reticle, checkered dissolves and sign-off). Its circuit outline is an original illustration, not a representation of a licensed circuit layout. Photorealistic parity is contingent on authorized external GLB/HDR/portrait texture assets, explicitly documented in `site/motorsport/assets/README.md`; these are not shipped as Gabriel's identity.

## Validation

- Run `python -m unittest discover -s tests -p test_portal_split.py -v` after syncing the full repository.
- Parse `site/motorsport/effects.js` and `asset-scene.js` as ECMAScript modules and compile shaders in Chromium/Firefox/WebKit with hardware acceleration as available.
- Test WebGL blocked mode, missing CDN, missing asset, and a locally licensed asset pack explicitly via `?assetScene=1`.
- Check link navigation, browser console, 320px / 390px / 768px / 1440px layout, reduced-motion accessibility and keyboard navigation.
- Verify that GitHub Pages `scripts/prepare_pages.py` maps `../` paths appropriately under `/portfolio/` and that Vercel serves the same pages at domain root.
- Validate the full suite and GitHub Actions before production merge.
