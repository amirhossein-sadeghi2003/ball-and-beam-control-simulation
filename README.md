# Ball and Beam Control Simulation

Control-oriented simulation project for a ball-and-beam system.

This project models a classical ball-and-beam control problem as preparation for a future hardware implementation. In the future hardware version, a servo motor will change the beam angle and a distance sensor will measure the ball position.

## Motivation

The goal of this project is to connect dynamics, feedback control, simulation, and future embedded implementation. It fits into a broader intelligent physical systems portfolio focused on modeling, sensing, estimation, and control of real-world dynamic systems.

## Planned Features

- Ball-and-beam dynamics simulation
- PID controller for position control
- Setpoint tracking
- Step response plots
- Position error plots
- Control signal plots
- Disturbance and noise experiments
- Documentation for future hardware implementation

## Future Hardware Direction

A future extension of this project may use:

- ESP32 microcontroller
- Servo motor for beam actuation
- Distance sensor for ball position measurement
- PID control running on embedded hardware
- Serial logging and Python-based analysis

## Project Structure

ball-and-beam-control-simulation/
- src/
- results/
- docs/
- README.md
- requirements.txt
- .gitignore

## Status

Initial project structure created. Dynamics and controller implementation will be added next.
