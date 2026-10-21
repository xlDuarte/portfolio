"""OpenCV optical-flow benchmark for motorsport onboard motion.

No actual F1 footage is bundled: frames are reproducibly SYNTHETIC and generated
with a known translational transform. Validation is against that transform.
"""
from __future__ import annotations
import argparse
import json
from typing import Any

import cv2
import numpy as np


def synthetic_pair(seed: int = 103, shift_x: float = 6.0, shift_y: float = -3.0,
                   width: int = 640, height: int = 360) -> tuple[np.ndarray, np.ndarray]:
    """Render track-side markers and apply subpixel affine translation."""
    if width < 100 or height < 100:
        raise ValueError("frames must be at least 100 by 100")
    if not np.isfinite([shift_x, shift_y]).all():
        raise ValueError("pixel shifts must be finite")
    rng = np.random.default_rng(seed)
    frame = np.zeros((height, width), dtype=np.uint8)
    for _ in range(220):
        x = int(rng.integers(20, width - 20))
        y = int(rng.integers(20, height - 20))
        cv2.rectangle(frame, (x-3, y-3), (x+3, y+3), 230, -1)
        cv2.circle(frame, (x, y), 6, 100, 1)
    matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    shifted = cv2.warpAffine(frame, matrix, (width, height), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return frame, shifted


def track_features(frame0: np.ndarray, frame1: np.ndarray, *, focal_px: float = 850.0,
                   expected_shift: tuple[float, float] | None = None) -> dict[str, Any]:
    """Track features with Lucas-Kanade optical flow and robust median displacement."""
    if focal_px <= 0 or not np.isfinite(focal_px):
        raise ValueError("focal_px must be finite and positive")
    if frame0.ndim != 2 or frame1.shape != frame0.shape or frame0.dtype != np.uint8 or frame1.dtype != np.uint8:
        raise ValueError("equal-shape uint8 grayscale frames required")
    points = cv2.goodFeaturesToTrack(frame0, maxCorners=500, qualityLevel=0.02,
                                      minDistance=8, blockSize=5)
    if points is None or len(points) < 10:
        raise ValueError("insufficient image features")
    moved, status, error = cv2.calcOpticalFlowPyrLK(frame0, frame1, points, None,
                            winSize=(21, 21), maxLevel=3,
                            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))
    if moved is None or status is None:
        raise ValueError("optical flow tracking failed")
    good = status.reshape(-1) == 1
    delta = (moved - points).reshape(-1, 2)[good]
    if len(delta) < 10:
        raise ValueError("too few successfully tracked features")
    center = np.median(delta, axis=0)
    dist = np.linalg.norm(delta - center, axis=1)
    mad = np.median(dist)
    inliers = dist <= max(1.5, 3 * 1.4826 * mad)
    if inliers.sum() < 10:
        raise ValueError("too few coherent motion vectors")
    dx, dy = np.median(delta[inliers], axis=0)
    output: dict[str, Any] = {
        "algorithm": "OpenCV goodFeaturesToTrack + calcOpticalFlowPyrLK",
        "dataset": "synthetic translated image pair (not race footage)",
        "tracked_features": int(inliers.sum()),
        "total_detected_features": int(len(points)),
        "median_dx_px": round(float(dx), 4),
        "median_dy_px": round(float(dy), 4),
        "apparent_yaw_deg": round(float(np.degrees(np.arctan(dx / focal_px))), 5),
        "apparent_pitch_deg": round(float(np.degrees(np.arctan(dy / focal_px))), 5),
        "limitations": "camera motion estimate only; cannot separate translational parallax or road banking without depth/calibration",
    }
    if expected_shift is not None:
        truth = np.asarray(expected_shift, dtype=float)
        if truth.shape != (2,) or not np.isfinite(truth).all():
            raise ValueError("expected shift must be two finite values")
        output["endpoint_error_px"] = round(float(np.linalg.norm(np.array([dx, dy]) - truth)), 4)
    return output


def run() -> dict[str, Any]:
    a, b = synthetic_pair()
    return track_features(a, b, expected_shift=(6, -3))

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
