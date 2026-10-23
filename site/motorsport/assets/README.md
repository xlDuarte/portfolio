# Motorsport 3D asset pack — optional licensed mode

The published Motorsport page uses procedural illustrations and a functional Three.js fallback. It deliberately **does not present a third-party racing driver as Gabriel Reis Duarte**.

## How to enable the photorealistic pipeline

Supply an asset pack you are authorized to use, under `site/motorsport/assets/hero/scene/`:

| Filename | Required role |
| --- | --- |
| `helmet3.glb` | Draco-compressed helmet with PBR materials / normal / metallic-roughness |
| `studio-light.hdr` | HDR environment filtered by `PMREMGenerator` |
| `noise.webp` | Dynamic burn/reveal edge noise |
| `person-diffuse.webp` | Licensed subject photograph |
| `person-depth.webp` | Depth map for parallax |
| `person-alpha.webp` | Portrait silhouette cut-out |
| `person-normal.webp` | Normal map for cursor relighting |

Then visit `/motorsport/?assetScene=1`. The adapter initializes `GLTFLoader`, `DRACOLoader`, `RGBELoader`, uploads maps, compiles the shader/material variants and switches to the asset-driven scene. Errors are visible in a UI banner identifying the failed resource; the procedural scene remains available.

The owner-provided source reference additionally identifies a third-party demonstration asset host. `?referenceScene=1` is an **explicit opt-in inspection mode** and displays a notice that the photograph and helmet are a third-party visual reference, not Gabriel. Do not use those assets as a published personal portrait or redistribute them without authorization.

## Included runtime features

- Single rAF ticker, Lenis smooth scrolling, 1ms substep damped springs, word/letter stagger;
- Hero WebGL shader with crown-to-chin noise burn, cyan front and cursor-trail capsules, dynamic outline, angle/subject parallax and portrait normal relighting;
- Original analytic contour field, 0.9-scale/55%-shade sticky stack, light/dark disintegrating flags;
- Halftone track/map canvas with **8004 lattice positions**, dashed moving axes, ping and pointer reticle;
- 6-second lap tracer, 4 turn markers, corner-dependent traversal and cooling trail;
- 7 research-project timeline plates with 3-layer procedural parallax, year reveals, rail marker and hover dimming;
- Animated paddock contour field, five-stage method strip, moving dashed links and sign-off figure;
- Responsive tiers, keyboard focus, reduced-motion support, visible failure handling and fallbacks.

## Limitations

The procedural artwork is **not a pixel-perfect replacement for the original third-party photograph or proprietary helmet geometry**. The optional asset-driven adapter reproduces that rendering pipeline when assets are provided; visual equivalence requires the actual authorized files and browser-based reference comparisons.

The projects linked by this portfolio are research and software demonstrations; data provenance is documented in the individual case studies.
