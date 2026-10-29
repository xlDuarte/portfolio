# Race Replay / project 109

Canonical entrypoint: `site/cases/motorsport/109/index.html`.
The Motorsport hub forwards its project-109 route to this entrypoint.

The independent white/cyan dashboard uses deck.gl 9.1.14 for the local-coordinate circuit and Apache ECharts 6.0.0 for linked telemetry. Dependencies are version-pinned, served locally from `vendor/` and loaded independently. Files are the unmodified npm package distributions, with their licenses alongside. A native SVG view and charts preserve replay, selection, controls and export if loading or GPU initialization fails.

`session.mjs` is a data adapter over the unchanged `../lab/engine.mjs`. The shared clock is clamped to 0–900 seconds. Playback uses elapsed animation-frame time and pauses when the tab is hidden. Drivers, current indicators and telemetry exports derive from the same engine and parameters. Acceleration is a central finite difference of the synthetic speed signal; the position-advance model is independent of that signal. No real track, GPS, sensor data or physical validity is implied.

Run data regression checks: `node tests/replay_session_checks.mjs`.
Run route and entrypoint checks: `python -m unittest discover -s tests -p test_replay_session.py`.

Browser verification performed at desktop 1440px, tablet 768px and mobile 390px: actual pinned deck.gl/ECharts builds, 2D/3D switching, unique selected driver and ranks, play/pause/end/reset, scrub, chart-click seek, grip/compare/window settings, JSON export, hub routing and network-failure fallback. The checked-in screenshot is captured from the running interface.
