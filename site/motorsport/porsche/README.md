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
