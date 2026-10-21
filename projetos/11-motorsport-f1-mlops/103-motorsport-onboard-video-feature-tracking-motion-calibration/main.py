#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project #103: Motorsport Onboard Video Feature Tracking & Motion Calibration
Benchmark: F1 Skill 03 — Computer Vision (Onboard Braking & Cornering Motion Analysis)
Author: Gabriel Reis Duarte (@gabrielrduarte)
Stack: Python, OpenCV, Optical Flow Feature Tracking, Camera Calibration
"""

import math


def analyze_onboard_optical_flow():
    """
    Simulates feature displacement vectors (u, v) from onboard camera frames during
    heavy braking (pitch dive) and apex cornering (yaw + roll), converting pixel shifts
    into calibrated angular velocity estimates and documenting physical limitations.
    """
    focal_px = 1280.0
    frames = []
    for frame_idx in range(1, 61):
        # Braking phase (frames 1-25), Cornering apex (frames 26-60)
        pitch_shift_px = 14.5 if frame_idx <= 25 else -3.2
        yaw_shift_px = 4.0 if frame_idx <= 25 else 38.0 * math.sin((frame_idx - 25) * 0.08)
        apparent_yaw_deg = math.degrees(math.atan2(yaw_shift_px, focal_px))
        apparent_pitch_deg = math.degrees(math.atan2(pitch_shift_px, focal_px))
        frames.append((frame_idx, round(apparent_pitch_deg, 3), round(apparent_yaw_deg, 3)))

    return {
        "tracked_frames": len(frames),
        "peak_braking_pitch_deg": max(f[1] for f in frames),
        "peak_cornering_yaw_deg": max(f[2] for f in frames),
        "documented_limitations": [
            "Scale ambiguity without known 3D track reference landmarks or stereo depth",
            "Rolling-shutter distortion under high-frequency kerb/engine vibration",
            "Suspension pitch/roll couples with road banking in single-camera homography"
        ]
    }


if __name__ == "__main__":
    print("[F1 ONBOARD COMPUTER VISION]", analyze_onboard_optical_flow())
