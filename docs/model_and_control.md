# Ball-and-Beam Model and Control Notes

This document explains the simplified dynamic model, PID controller, simulation assumptions, and engineering interpretation used in this project.

## 1. System Description

The ball-and-beam system is a classical feedback control problem. A ball moves along a beam, and the controller changes the beam angle to regulate the ball position.

In a future hardware implementation:

- A servo motor changes the beam angle.
- A distance sensor measures the ball position.
- A microcontroller runs a feedback controller.
- The controller tries to keep the ball near a desired setpoint.

This simulation is a first step toward that hardware system.

## 2. Simplified Dynamic Model

The simulation uses a simplified control-oriented model:

x_ddot = K * sin(theta)

where:

- x is the ball position along the beam
- x_dot is the ball velocity
- x_ddot is the ball acceleration
- theta is the beam angle
- K is a simplified dynamics gain

This model captures the main qualitative behavior:

- Positive beam angle accelerates the ball in one direction.
- Negative beam angle accelerates the ball in the opposite direction.
- Larger beam angles produce stronger acceleration.
- The controller must regulate a dynamic system with position and velocity.

The model is not intended to be a full mechanical derivation. Instead, it is used to study control behavior and prepare for future embedded implementation.

## 3. Numerical Integration

The simulation uses a fixed time step:

dt = 0.01 s

At each simulation step:

1. The setpoint is selected.
2. The noisy measured position is generated.
3. The position error is computed.
4. The PID controller computes a beam angle command.
5. The beam angle is limited by actuator saturation.
6. The ball acceleration is computed.
7. Velocity and position are updated using numerical integration.
8. The ball position is constrained to remain within the beam length.

## 4. PID Controller

The controller uses the standard PID form:

u = Kp * e + Ki * integral(e) + Kd * derivative(e)

where:

- u is the beam angle command
- e is the position error
- Kp is the proportional gain
- Ki is the integral gain
- Kd is the derivative gain

The current controller gains are:

- Kp = 2.8
- Ki = 0.15
- Kd = 1.25

The controller output is limited to represent a realistic maximum beam angle:

- Maximum beam angle = ±12 degrees

## 5. Sensor Noise

The simulation includes measurement noise:

measurement_noise_std = 0.002 m

This represents uncertainty from a future real distance sensor. The controller does not receive the true position directly. Instead, it receives a noisy position measurement.

This makes the simulation more realistic than a perfect-state-feedback example.

## 6. Disturbance Injection

A temporary disturbance is applied between:

7.0 s <= t <= 7.5 s

This disturbance represents an external physical effect, such as:

- a small push on the ball
- vibration
- imperfect beam motion
- unmodeled dynamics

The disturbance response is useful for evaluating whether the controller can recover after an unexpected event.

## 7. Actuator Saturation

The beam angle is limited to ±12 degrees.

This is important because real actuators cannot produce unlimited control effort. Saturation makes the simulation more realistic and prevents the PID controller from commanding physically impossible beam angles.

## 8. Beam Boundary Constraint

The simulated beam half-length is:

0.30 m

The ball position is constrained between:

-0.30 m <= x <= 0.30 m

If the ball reaches the beam boundary, its velocity is reset to zero. This approximates the physical limit of the ball remaining on the beam.

## 9. Engineering Interpretation

This project is intentionally designed as a bridge between simulation and hardware.

Important engineering aspects included in the simulation:

- dynamic response rather than static prediction
- feedback control loop behavior
- noisy sensor measurement
- actuator limits
- disturbance response
- setpoint changes
- logged data for analysis
- plots for interpreting controller behavior

These aspects make the project closer to a real cyber-physical system than a purely mathematical or coding exercise.

## 10. Future Improvements

Possible future improvements include:

- deriving a more detailed nonlinear mechanical model
- adding a servo motor dynamics model
- adding sensor sampling-rate limitations
- adding measurement filtering
- comparing P, PI, PD, and PID controllers
- adding automatic PID tuning experiments
- implementing the controller on ESP32
- validating the simulation against real hardware data

## 11. Connection to Future Hardware

The future hardware version may include:

- ESP32 microcontroller
- servo motor for beam angle control
- distance sensor for ball position measurement
- external power supply for servo stability
- serial logging for real-time data collection
- Python plotting scripts for analyzing real response

This simulation provides the control logic and analysis foundation for that future implementation.
