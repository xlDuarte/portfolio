# Porsche Cup — Acquisition workspace

Route: /cases/motorsport/110/. The page loads workspace.mjs and observed.mjs.

## Data and operation

Upload a locally acquired CSV with time_s followed by measured channels. Supported delimiters are comma with decimal point, and semicolon with decimal comma. Limits are 5 MB and 50,000 samples. Timestamps must strictly increase. Duplicate headers, missing cells, unknown channels, non-finite values and negative wheel loads or speeds are rejected. Each accepted channel must be populated for every sample.

Supported channels are load_FL_N, load_FR_N, load_RL_N, load_RR_N, temp_FL_C, temp_FR_C, temp_RL_C, temp_RR_C, ax_ms2, ay_ms2, damper_velocity_mms and speed_kmh. A missing channel displays an unavailable state.

Controls cover file import, time range, playback rate, selected instant, tire selection, signal selection and export. CSV export preserves every sample in the selected interval. JSON exports sample means and extrema with the original filename and unverified-user-source label. The downloadable template contains only headers.

## Interpretation

Total load is the sum of four measured wheel loads. Front share is (FL+FR)/total and cross load is (FL+RR)/total. Both require all four channels and a positive total. Tire colors scale within the selected interval and do not identify an optimal operating temperature. One temperature channel is supported per wheel. Sensor type and placement are supplied by the acquisition owner.

The G-G panel uses measured lateral and longitudinal acceleration. Sign conventions and gravity correction must be checked at source. Cursor values use the last sample at or before the selected time. Charts subsample while preserving interval endpoints; statistical summaries use every sample. Means are arithmetic sample means, not time-weighted integrals.

No acquisition is bundled for Porsche. OpenF1 data is not used to fill Porsche channels. The previous illustrative physics model remains available as a legacy module tested independently and is not imported by this workspace.

## Verification

Run node tests/porsche_observed_checks.mjs and python -m unittest discover -s tests -p test_porsche.py -v.

## Seminar engineering workspace

The second workspace is implemented in seminar.mjs and engineering.mjs. It maps the supplied Motorsports Performance Engineering Seminar 2026 syllabus (pages 6–10) to 13 computational analyses and a structured event report. The Coverage tab lists each topic, its implementation and external dependencies.

- Acquisition quality checks sampling intervals and gaps. Physical sensor accuracy still requires calibration.
- Lap comparison aligns by distance, uses the shared distance interval and linear interpolation, and calculates B-minus-A deltas with equal-distance sectors.
- Driver analysis integrates threshold durations using sample intervals. Reported lateral acceleration is observed demand; it does not establish maximum tire grip. Steering residual requires road-wheel angle and curvature.
- Tire analysis fits lateral stiffness in a user-selected low-angle range and reports measured force normalized by load. Load associations are not controlled identification of load sensitivity.
- Longitudinal slip uses (omega * effective_radius - speed) / speed, excluding speed below 1 m/s.
- Tire measurements calculate inner/outer and crown gradients, wear per distance, ideal-gas pressure evolution and cold pressure for a user-specified hot target. Gas temperature, constant volume and constant gas quantity are assumptions.
- Thermal analysis consumes calibrated numeric x/y/temperature exports, not false-color JPEG values or proprietary radiometric files. Calibration and emissivity remain in the source software.
- Race timing consumes normalized per-car lap records. It excludes pit laps from clean-pace summaries and reports observed totals, not official classification.
- Strategy uses dynamic programming under user-entered tank, consumption and tire-life limits. No traffic or safety-car model. Stops and refuel time are additive; refuelling zero prohibits refuelling.
- Wet/dry crossover calculates the number of remaining laps needed to recover the pit loss at the entered pace difference.
- Setup A/B reports sample distributions and standard error under an independence assumption. Conditions, driver and fuel must be controlled.
- The independent lap simulator is periodic, point-mass, constant-grip, with wheel power and drag. Lateral and longitudinal limits are independent. It does not implement suspension, downforce or ChassisSim.
- Simulator comparison accepts measured and simulated profiles normalized to the same time/distance/speed schema.
- Event preparation records responsibilities, paperwork, regulations, track walk, briefing, tire/setup plan, radio, debrief, technical review and actions. Local save and Markdown export are available.

Templates contain headers only. Source files are processed locally. Numerical test fixtures are confined to tests. Exported analysis JSON records filenames, parameters, source status and methodology.

The PDF is a syllabus, not the full teaching material. FLIR, HH Timing and ChassisSim exercises require their external software, licensed materials and relevant data. No equivalence to their algorithms or completion of an in-person track day is claimed.

Run node tests/porsche_engineering_checks.mjs for analytical checks, invalid-input checks and comparison of the stint optimizer against exhaustive partitions.
