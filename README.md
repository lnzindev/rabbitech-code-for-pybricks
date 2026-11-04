<div align="center">

# RABBITECH · PYBRICKS AUTOPILOT

**Robotics · LEGO SPIKE Prime · Pybricks · Embedded Systems**

A modular control system for the Rabbitech robotics project, built to run eight sequential routines on a LEGO SPIKE Prime hub.

[Source code](https://github.com/lnzindev/rabbitech-code-for-pybricks) · [Developer profile](https://github.com/lnzindev) · [Rabbitech projects](https://github.com/lnzindev?tab=repositories)

![Python](https://img.shields.io/badge/Python-Pybricks%20MicroPython-171522?style=flat-square&logo=python&logoColor=3776ab)
![Platform](https://img.shields.io/badge/Platform-LEGO%20SPIKE%20Prime-171522?style=flat-square)
![Control](https://img.shields.io/badge/Control-Adaptive%20PID-171522?style=flat-square)
![Status](https://img.shields.io/badge/Project-Experimental-171522?style=flat-square)

</div>

---

## About the project

**Rabbitech Pybricks Autopilot** is an experimental robotics control system developed for LEGO SPIKE Prime using Pybricks MicroPython.

The project separates reusable movement and motor-control functions from the routines that execute each mission. A central controller waits for the left hub button before starting each routine, allowing the robot to run up to eight programmed sequences in order.

The code is part of the hands-on robotics work developed around the **Rabbitech** team.

## Main features

- **Sequential controller:** manages eight routines through a single entry point.
- **Adaptive movement:** uses heading feedback and a PID-style correction loop to keep the robot on course.
- **Motion profiles:** supports acceleration and deceleration ramps.
- **Turning control:** includes two-wheel and one-wheel turning routines.
- **Motor monitoring:** detects motors that stop responding during movement.
- **Persistent learning data:** stores movement statistics and adaptive correction values in hub storage.
- **Gripper control:** provides independent commands for the left and right grippers.

## Repository structure

| File | Responsibility |
|---|---|
| `main.py` | Main program. Runs the eight routines in sequence. |
| `base.py` | Shared hardware setup, movement functions, turning, grippers and adaptive memory. |
| `memoria.py` | Basic test script for saving and restoring learning data. |
| `saida_1.py` – `saida_8.py` | Individual routines executed by the main controller. |

## Hardware configuration

The current configuration in `base.py` uses the following ports:

| Port | Component |
|---|---|
| C | Left gripper motor |
| D | Right gripper motor |
| E | Left drive motor |
| F | Right drive motor |

**Wheel diameter:** 56 mm  
**Hub:** LEGO SPIKE Prime  
**Runtime:** Pybricks MicroPython 3.6.1 (as specified in the source code)

Check the physical motor connections and wheel orientation before running the robot. If your build uses different ports or directions, update the hardware configuration in `base.py`.

## How the controller works

1. The hub initializes the shared hardware configuration and loads saved adaptive data.
2. The controller waits for the IMU to become ready and stops the drive motors.
3. The hub displays the number of the next routine.
4. Press and release the **left button** to start that routine.
5. After execution, the controller stops the motors and checks the routine's return value.
6. If a routine returns `False`, the sequence is interrupted and the hub displays an error. Otherwise, the next routine is prepared.
7. When all routines finish, the hub displays `FIM`.

## Running the program

1. Install a Pybricks-compatible firmware on the LEGO SPIKE Prime hub.
2. Open the project files in the Pybricks code editor.
3. Transfer the required Python files to the hub.
4. Run **`main.py`**. It is the entry point and imports the other modules.
5. Place the robot in a safe test area and trigger each routine using the left hub button.

> **Important:** Test each routine individually with the robot lifted or in a clear, controlled area before running the complete sequence. Motor direction, attachment position, wheel grip and mission layout can change the robot's behavior.

## Configuration

Movement settings and hardware parameters are centralized in `base.py`, including:

- Drive and turning speeds.
- Gripper speed and target angles.
- Wheel diameter.
- Heading correction constants.
- Turning tolerance and timeout.
- Adaptive memory limits.

Change these values carefully and validate them on the physical robot.

## Current limitations

- The eight routine files currently contain the same example movement sequence. Replace each example with its intended mission routine before competition use.
- The project has not been documented here as competition-validated hardware.
- Adaptive memory stores correction values and movement counters; it does not automatically guarantee better results on every surface or robot configuration.
- Always verify the behavior of the robot after changing code or hardware.

## Project philosophy

This repository follows the same approach used across my projects: build, test, understand what fails, and improve through iteration.

Robotics connects software to the physical world. Every movement is a real test of the code.

---

## Sobre o projeto

O **Rabbitech Pybricks Autopilot** é um sistema experimental de controle para LEGO SPIKE Prime, desenvolvido com Pybricks MicroPython.

O projeto separa as funções reutilizáveis de movimento e controle dos motores das rotinas individuais. Um controlador central organiza até oito saídas em sequência, aguardando o botão esquerdo do hub para iniciar cada uma.

### Objetivos

- Centralizar o controle dos motores e das garras.
- Melhorar a precisão dos deslocamentos usando a IMU.
- Aplicar rampas de aceleração e desaceleração.
- Registrar dados de movimentos concluídos e falhas.
- Manter o código modular e fácil de evoluir.

**Desenvolvido como parte dos experimentos de robótica da Rabbitech.**

<div align="center">

**RABBITECH · BUILD · TEST · IMPROVE**

[GitHub](https://github.com/lnzindev) · [Repositório](https://github.com/lnzindev/rabbitech-code-for-pybricks)

</div>
