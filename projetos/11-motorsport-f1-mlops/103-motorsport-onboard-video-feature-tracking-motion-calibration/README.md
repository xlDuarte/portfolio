# 103 — Motorsport Onboard Video: OpenCV Feature Tracking

**Status:** validated synthetic optical-flow benchmark; not validation against real F1 footage.

## Problem and real implementation

Measure apparent onboard-camera motion in grayscale frame pairs rather than
inventing motion vectors. `motorsport/optical_flow.py` builds 220 reproducible
trackside landmarks, generates frames with a known translation, detects corners
with `cv2.goodFeaturesToTrack` and tracks them with
`cv2.calcOpticalFlowPyrLK` (Lucas–Kanade). It applies median/MAD filtering,
converts displacement to small-angle estimates using focal length, and
reports endpoint error against the known simulation transform.

## Run

Install `opencv-python-headless>=4.8,<5`, `numpy>=1.24,<3` with
`requirements-case-studies.txt`, then run
`python projetos/11-motorsport-f1-mlops/103-motorsport-onboard-video-feature-tracking-motion-calibration/main.py`

Run regression tests: `python -m unittest discover -s tests -v`.

## Limitations

Apparent optical-flow pitch/yaw is not actual vehicle IMU yaw or calibrated
camera rotational movement. Motion parallax, depth variations, dynamic
objects, lens distortion, vibration, rolling shutter, and track geometry
are not addressed. No external footage or inference over real race video is
present. A real footage pipeline needs appropriate recording permissions,
calibration, frame timestamps, stabilization, and independently reviewed
reference labels.
