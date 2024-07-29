> [!NOTE]
> This repository is part of the final exam for the *Reinforcement Learning* course held by professor Antonio Celani at [University of Trieste](https://www.units.it/en) in the 2023-2024 academic year.


# Traffic Lights Optimization with Reinforcement Learning techniques

## Overview
This project simulates an intersection with traffic lights and cars using Pygame. The goal of the simulation is to maximize the throughput and minimize waiting times and queue lengths of cars at the intersection by optimizing the **traffic light policies** using Reinforcement Learning techniques. 

A fixed time policy is considered as the baseline model for the stoplight. Then, an MDP model is implemented along with 2 Reinforcement Learning algorithms: **Policy Iteration** and **Value Iteration**, and the three solutions are compared.

Cars are spawned according to a customizable rule, and various statistics are tracked during the simulation.

## Features
- Simulates traffic lights at an intersection.
- Supports different traffic light policies: MDP (with PI or VI) and Fixed Time for baseline comparison.
- Uses Reinforcement Learning techniques to maximize the throughput, minimize waiting times and queue lengths of cars.
- Customizable car spawn rule.
- Displays real-time statistics and information about the simulation.
- Visual representation of cars and traffic lights.

## Requirements

- Python 3.x
- Pygame
- Other dependencies listed in `requirements.txt`


