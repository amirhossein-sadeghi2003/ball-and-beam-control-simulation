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


def simulate_ball_and_beam():
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # Simulation settings
    dt = 0.01
    total_time = 12.0
    time = np.arange(0.0, total_time, dt)

    # Simplified ball-and-beam dynamics
    # x_ddot = K * sin(theta)
    # This is a control-oriented model, not a full mechanical derivation.
    dynamics_gain = 5.0

    # Beam and actuator constraints
    max_beam_angle_deg = 12.0
    max_beam_angle_rad = np.deg2rad(max_beam_angle_deg)

    # Beam physical limits
    beam_half_length = 0.30  # meters

    # PID gains
    pid = PIDController(
        kp=2.8,
        ki=0.15,
        kd=1.25,
        output_limit=max_beam_angle_rad,
    )

    # State variables
    position = 0.0
    velocity = 0.0

    # Sensor noise setting
    measurement_noise_std = 0.002  # meters

    # Data storage
    positions = []
    measured_positions = []
    velocities = []
    setpoints = []
    errors = []
    beam_angles = []
    disturbances = []

    rng = np.random.default_rng(seed=42)

    for t in time:
        # Setpoint profile
        if t < 2.0:
            setpoint = 0.00
        elif t < 6.0:
            setpoint = 0.12
        elif t < 9.0:
            setpoint = -0.08
        else:
            setpoint = 0.05

        measured_position = position + rng.normal(0.0, measurement_noise_std)
        error = setpoint - measured_position

        beam_angle = pid.update(error, dt)

        # Add a temporary disturbance between 7 and 7.5 seconds
        disturbance = 0.0
        if 7.0 <= t <= 7.5:
            disturbance = 0.6

        acceleration = dynamics_gain * np.sin(beam_angle) + disturbance

        velocity += acceleration * dt
        position += velocity * dt

        # Keep ball within beam limits
        if position > beam_half_length:
            position = beam_half_length
            velocity = 0.0
        elif position < -beam_half_length:
            position = -beam_half_length
            velocity = 0.0

        positions.append(position)
        measured_positions.append(measured_position)
        velocities.append(velocity)
        setpoints.append(setpoint)
        errors.append(error)
        beam_angles.append(np.rad2deg(beam_angle))
        disturbances.append(disturbance)

    df = pd.DataFrame(
        {
            "time_s": time,
            "setpoint_m": setpoints,
            "position_m": positions,
            "measured_position_m": measured_positions,
            "velocity_m_s": velocities,
            "error_m": errors,
            "beam_angle_deg": beam_angles,
            "disturbance_m_s2": disturbances,
        }
    )

    df.to_csv(results_dir / "ball_beam_simulation_data.csv", index=False)

    rmse = np.sqrt(np.mean((df["setpoint_m"] - df["position_m"]) ** 2))
    mean_abs_error = np.mean(np.abs(df["setpoint_m"] - df["position_m"]))
    max_abs_error = np.max(np.abs(df["setpoint_m"] - df["position_m"]))

    metrics = pd.DataFrame(
        {
            "metric": ["rmse_m", "mean_abs_error_m", "max_abs_error_m"],
            "value": [rmse, mean_abs_error, max_abs_error],
        }
    )
    metrics.to_csv(results_dir / "performance_metrics.csv", index=False)

    # Plot 1: position tracking
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"], df["setpoint_m"], linestyle="--", label="Setpoint")
    plt.plot(df["time_s"], df["position_m"], label="Ball position")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.title("Ball-and-Beam Position Tracking")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / "position_tracking.png", dpi=200)
    plt.close()

    # Plot 2: tracking error
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"], df["error_m"])
    plt.xlabel("Time (s)")
    plt.ylabel("Error (m)")
    plt.title("Position Tracking Error")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "tracking_error.png", dpi=200)
    plt.close()

    # Plot 3: control signal
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"], df["beam_angle_deg"])
    plt.xlabel("Time (s)")
    plt.ylabel("Beam angle (deg)")
    plt.title("PID Control Signal")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "control_signal.png", dpi=200)
    plt.close()

    # Plot 4: disturbance response
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"], df["position_m"], label="Ball position")
    plt.plot(df["time_s"], df["setpoint_m"], linestyle="--", label="Setpoint")
    plt.axvspan(7.0, 7.5, alpha=0.2, label="Disturbance interval")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.title("Response to Temporary Disturbance")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / "disturbance_response.png", dpi=200)
    plt.close()

    print("Ball-and-beam simulation completed.")
    print(f"RMSE: {rmse:.4f} m")
    print(f"Mean absolute error: {mean_abs_error:.4f} m")
    print(f"Max absolute error: {max_abs_error:.4f} m")
    print("Saved outputs to results/")


if __name__ == "__main__":
    simulate_ball_and_beam()
