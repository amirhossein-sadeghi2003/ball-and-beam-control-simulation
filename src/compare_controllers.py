import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


class PIDController:
    def __init__(self, kp, ki, kd, output_limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limit = output_limit

        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt

        output = (
            self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )

        output = np.clip(output, -self.output_limit, self.output_limit)

        self.previous_error = error
        return output


def setpoint_profile(t):
    if t < 2.0:
        return 0.00
    if t < 6.0:
        return 0.12
    if t < 9.0:
        return -0.08
    return 0.05


def simulate_controller(controller_name, gains, seed=42):
    dt = 0.01
    total_time = 12.0
    time = np.arange(0.0, total_time, dt)

    dynamics_gain = 5.0
    max_beam_angle_deg = 12.0
    max_beam_angle_rad = np.deg2rad(max_beam_angle_deg)
    beam_half_length = 0.30
    measurement_noise_std = 0.002

    pid = PIDController(
        kp=gains["kp"],
        ki=gains["ki"],
        kd=gains["kd"],
        output_limit=max_beam_angle_rad,
    )

    position = 0.0
    velocity = 0.0

    rng = np.random.default_rng(seed=seed)

    rows = []

    for t in time:
        setpoint = setpoint_profile(t)

        measured_position = position + rng.normal(0.0, measurement_noise_std)
        error = setpoint - measured_position

        beam_angle = pid.update(error, dt)

        disturbance = 0.0
        if 7.0 <= t <= 7.5:
            disturbance = 0.6

        acceleration = dynamics_gain * np.sin(beam_angle) + disturbance

        velocity += acceleration * dt
        position += velocity * dt

        if position > beam_half_length:
            position = beam_half_length
            velocity = 0.0
        elif position < -beam_half_length:
            position = -beam_half_length
            velocity = 0.0

        rows.append(
            {
                "controller": controller_name,
                "time_s": t,
                "setpoint_m": setpoint,
                "position_m": position,
                "measured_position_m": measured_position,
                "velocity_m_s": velocity,
                "error_m": setpoint - position,
                "beam_angle_deg": np.rad2deg(beam_angle),
                "disturbance_m_s2": disturbance,
            }
        )

    return pd.DataFrame(rows)


def compute_metrics(df):
    rows = []

    for controller_name, group in df.groupby("controller"):
        rmse = np.sqrt(np.mean((group["setpoint_m"] - group["position_m"]) ** 2))
        mean_abs_error = np.mean(np.abs(group["setpoint_m"] - group["position_m"]))
        max_abs_error = np.max(np.abs(group["setpoint_m"] - group["position_m"]))
        mean_abs_control = np.mean(np.abs(group["beam_angle_deg"]))
        max_abs_control = np.max(np.abs(group["beam_angle_deg"]))

        rows.append(
            {
                "controller": controller_name,
                "rmse_m": rmse,
                "mean_abs_error_m": mean_abs_error,
                "max_abs_error_m": max_abs_error,
                "mean_abs_control_deg": mean_abs_control,
                "max_abs_control_deg": max_abs_control,
            }
        )

    return pd.DataFrame(rows).sort_values("rmse_m")


def main():
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    controllers = {
        "P": {"kp": 2.8, "ki": 0.0, "kd": 0.0},
        "PD": {"kp": 2.8, "ki": 0.0, "kd": 1.25},
        "PID": {"kp": 2.8, "ki": 0.15, "kd": 1.25},
    }

    all_runs = []

    for controller_name, gains in controllers.items():
        run_df = simulate_controller(controller_name, gains)
        all_runs.append(run_df)

    comparison_df = pd.concat(all_runs, ignore_index=True)
    metrics_df = compute_metrics(comparison_df)

    comparison_df.to_csv(results_dir / "controller_comparison_timeseries.csv", index=False)
    metrics_df.to_csv(results_dir / "controller_comparison.csv", index=False)

    plt.figure(figsize=(10, 5))

    first_group = True
    for controller_name, group in comparison_df.groupby("controller"):
        if first_group:
            plt.plot(
                group["time_s"],
                group["setpoint_m"],
                linestyle="--",
                label="Setpoint",
            )
            first_group = False

        plt.plot(
            group["time_s"],
            group["position_m"],
            label=f"{controller_name} position",
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.title("Controller Comparison: Position Tracking")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / "controller_comparison_tracking.png", dpi=200)
    plt.close()

    plt.figure(figsize=(10, 5))

    for controller_name, group in comparison_df.groupby("controller"):
        plt.plot(
            group["time_s"],
            group["error_m"],
            label=f"{controller_name} error",
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Tracking error (m)")
    plt.title("Controller Comparison: Tracking Error")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / "controller_comparison_error.png", dpi=200)
    plt.close()

    print("Controller comparison completed.")
    print(metrics_df.to_string(index=False))
    print("Saved outputs to results/")


if __name__ == "__main__":
    main()
