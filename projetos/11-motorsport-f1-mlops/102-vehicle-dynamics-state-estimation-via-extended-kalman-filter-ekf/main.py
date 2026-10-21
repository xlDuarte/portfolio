#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project #102: Vehicle Dynamics State Estimation via Extended Kalman Filter (EKF)
Benchmark: F1 Skill 02 — State Estimation (Steering Angle, Yaw Rate, Lateral Accel -> Sideslip Angle)
Author: Gabriel Reis Duarte (@gabrielrduarte)
Stack: Python, Extended Kalman Filter (EKF), Sensor Fusion, Vehicle Dynamics
"""

import math
import random


def run_ekf_sideslip_estimation(n_steps=100, dt=0.02):
    """
    Estimates vehicle sideslip angle beta (rad) using a kinematic/dynamic bicycle model EKF.
    Inputs: steering_angle delta, measured yaw_rate r_meas, lateral_accel ay_meas.
    """
    random.seed(102)
    vx = 62.0  # m/s (~223 km/h cornering entry)
    x_est = 0.0  # estimated sideslip angle beta (rad)
    p_cov = 0.05  # estimation error covariance
    q_proc = 1e-4  # process noise variance
    r_meas_var = 2.5e-3  # measurement noise variance

    sq_errors = []
    for k in range(n_steps):
        t = k * dt
        steering_delta = 0.045 * math.sin(2.0 * math.pi * 0.5 * t)
        yaw_rate = 0.32 * math.sin(2.0 * math.pi * 0.5 * t - 0.1)
        true_beta = 0.028 * math.sin(2.0 * math.pi * 0.5 * t - 0.18)

        # Simulated lateral acceleration sensor with Gaussian noise
        ay_measured = vx * yaw_rate + (-95.0 * true_beta) + random.gauss(0.0, 0.25)

        # 1. EKF Predict Step: beta_dot ~ (ay / vx) - yaw_rate
        beta_pred = x_est + dt * ((ay_measured / vx) - yaw_rate)
        p_pred = p_cov + q_proc

        # 2. EKF Update Step using linearized lateral tire force observation H = -95.0
        h_jac = -95.0
        z_pred = vx * yaw_rate + h_jac * beta_pred
        innovation = ay_measured - z_pred
        s_cov = (h_jac * p_pred * h_jac) + r_meas_var
        k_gain = (p_pred * h_jac) / s_cov

        x_est = beta_pred + k_gain * innovation
        p_cov = (1.0 - k_gain * h_jac) * p_pred

        sq_errors.append((x_est - true_beta) ** 2)

    rmse_rad = math.sqrt(sum(sq_errors) / len(sq_errors))
    return {"rmse_deg": round(math.degrees(rmse_rad), 4), "final_beta_deg": round(math.degrees(x_est), 3)}


if __name__ == "__main__":
    metrics = run_ekf_sideslip_estimation()
    print("[F1 VEHICLE DYNAMICS EKF] Sideslip Angle Validation:", metrics)
