import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


class PDController:
    def __init__(self, kp, kd, output_limit):
        self.kp = kp
        self.kd = kd
        self.output_limit = output_limit
        self.previous_error = 0.0

    def update(self, error, dt):
        derivative = (error - self.previous_error) / dt
        output = self.kp * error + self.kd * derivative
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


def simulate_pd(kp, kd, seed=42, save_timeseries=False):
    dt = 0.01
    total_time = 12.0
    time = np.arange(0.0, total_time, dt)

    dynamics_gain = 5.0
    max_beam_angle_deg = 12.0
    max_beam_angle_rad = np.deg2rad(max_beam_angle_deg)
    beam_half_length = 0.30
    measurement_noise_std = 0.002

    controller = PDController(
        kp=kp,
        kd=kd,
        output_limit=max_beam_angle_rad,
    )

    position = 0.0
    velocity = 0.0

    rng = np.random.default_rng(seed=seed)
    rows = []

    for t in time:
        setpoint = setpoint_profile(t)

        measured_position = position + rng.normal(0.0, measurement_noise_std)
        error_for_controller = setpoint - measured_position

        beam_angle = controller.update(error_for_controller, dt)

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

        true_error = setpoint - position

        if save_timeseries:
            rows.append(
                {
                    "time_s": t,
                    "setpoint_m": setpoint,
                    "position_m": position,
                    "measured_position_m": measured_position,
                    "velocity_m_s": velocity,
                    "error_m": true_error,
                    "beam_angle_deg": np.rad2deg(beam_angle),
                    "disturbance_m_s2": disturbance,
                }
            )
        else:
            rows.append(
                {
                    "error_m": true_error,
                    "beam_angle_deg": np.rad2deg(beam_angle),
                }
            )

    df = pd.DataFrame(rows)

    rmse = np.sqrt(np.mean(df["error_m"] ** 2))
    mean_abs_error = np.mean(np.abs(df["error_m"]))
    max_abs_error = np.max(np.abs(df["error_m"]))
    mean_abs_control = np.mean(np.abs(df["beam_angle_deg"]))
    max_abs_control = np.max(np.abs(df["beam_angle_deg"]))

    metrics = {
        "kp": kp,
        "kd": kd,
        "rmse_m": rmse,
        "mean_abs_error_m": mean_abs_error,
        "max_abs_error_m": max_abs_error,
        "mean_abs_control_deg": mean_abs_control,
        "max_abs_control_deg": max_abs_control,
    }

    return metrics, df


def main():
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    kp_values = np.round(np.arange(1.5, 4.6, 0.5), 2)
    kd_values = np.round(np.arange(0.3, 2.1, 0.3), 2)

    tuning_rows = []

    for kp in kp_values:
        for kd in kd_values:
            metrics, _ = simulate_pd(kp=kp, kd=kd, save_timeseries=False)
            tuning_rows.append(metrics)

    tuning_df = pd.DataFrame(tuning_rows).sort_values("rmse_m")
    tuning_df.to_csv(results_dir / "pd_tuning_results.csv", index=False)

    best = tuning_df.iloc[0]
    best_metrics, best_df = simulate_pd(
        kp=float(best["kp"]),
        kd=float(best["kd"]),
        save_timeseries=True,
    )

    best_df.to_csv(results_dir / "pd_tuning_best_response.csv", index=False)

    pivot = tuning_df.pivot(index="kp", columns="kd", values="rmse_m")

    plt.figure(figsize=(9, 6))
    plt.imshow(
        pivot.values,
        aspect="auto",
        origin="lower",
        extent=[
            kd_values.min(),
            kd_values.max(),
            kp_values.min(),
            kp_values.max(),
        ],
    )
    plt.colorbar(label="RMSE (m)")
    plt.xlabel("Kd")
    plt.ylabel("Kp")
    plt.title("PD Tuning: RMSE Across Gain Grid")
    plt.tight_layout()
    plt.savefig(results_dir / "pd_tuning_rmse_heatmap.png", dpi=200)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(best_df["time_s"], best_df["setpoint_m"], linestyle="--", label="Setpoint")
    plt.plot(best_df["time_s"], best_df["position_m"], label="Best PD response")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.title(
        f"Best PD Response: Kp={best_metrics['kp']:.2f}, Kd={best_metrics['kd']:.2f}"
    )
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / "pd_tuning_best_response.png", dpi=200)
    plt.close()

    print("PD tuning experiment completed.")
    print("Best gain combination:")
    print(
        f"Kp={best_metrics['kp']:.2f}, "
        f"Kd={best_metrics['kd']:.2f}, "
        f"RMSE={best_metrics['rmse_m']:.4f} m, "
        f"MAE={best_metrics['mean_abs_error_m']:.4f} m"
    )
    print("Top 10 tuning results:")
    print(tuning_df.head(10).to_string(index=False))
    print("Saved outputs to results/")


if __name__ == "__main__":
    main()
