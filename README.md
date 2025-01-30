# LAFC-Projet-Robotique - LU2IN013

A simple robot simulation program that allows users to set start and end positions, place obstacles, and run a robot to navigate through a grid-based environment. The robot will move towards its goal while avoiding obstacles.

## Trello
[Project Trello Board](https://trello.com/invite/b/6790cac1e266a0256f541dae/ATTIf9a8031f4e259cceb72fa6d61ba8627b61608668/robot-project)

## Features
- Set a **start position** for the robot.
- Set an **end position** for the robot's goal.
- Add and remove **obstacles** in the grid.
- The robot will move toward the goal, avoiding obstacles, and will stop when it reaches the destination.

## Files Overview
The code is divided into four main files:

- **`map.py`**: Contains the `Map` class that handles the graphical user interface (GUI) and user interactions (setting start, end, obstacles).
- **`robot.py`**: Contains the `Robot` class, which defines the robot's movement logic.
- **`simulator.py`**: Contains the `RobotSimulator` class, which controls the simulation and updates the UI as the robot moves.
- **`main.py`**: The entry point of the program, which initializes the map and runs the simulation.

## Requirements
- Python 3.x
- Tkinter (comes pre-installed with Python)

## Installation

1. Clone or download the repository to your local machine.

    ```bash
    git clone https://github.com/arikarakas74/LAFC-Projet-Robotique.git
    ```

2. Navigate to the project directory:

    ```bash
    cd LAFC-Projet-Robotique
    ```

3. Make sure you have Python 3 installed. You can check this by running:

    ```bash
    python --version
    ```

    If Python 3.x is not installed, download and install it from [python.org](https://www.python.org/).

## Running the Program

1. Open a terminal or command prompt in the project directory where the Python files are located.

2. Run the program by executing:

    ```bash
    python3 main.py
    ```

3. A graphical interface will open. You can now:
   - Set the **start position** by clicking on the grid.
   - Set the **end position** by clicking on the grid.
   - Set **obstacles** by clicking on the grid.
   - Click the **Run Simulation** button to start the robot's movement.
   - Click **Reset** to reset the map.

## How It Works
- The **map** is represented as a grid with rows and columns. You can customize the size of the grid (default: 15x15).
- The **robot** starts at the designated start position and moves toward the goal (end position) in small increments.
- The robot avoids obstacles while moving. If the robot reaches the goal, the simulation will stop and display a success message.

## Example Usage

1. Open the graphical interface.
2. Click "Set Start" and click on a grid cell to place the start position (yellow square).
3. Click "Set End" and click on a grid cell to place the end position (green square).
4. Click "Set Obstacles" and click on grid cells to place obstacles (red squares).
5. Click "Run Simulation" to see the robot move towards the goal while avoiding obstacles.
6. Click "Reset" to clear the grid and start a new simulation.


