# LAFC-Projet-Robotique - LU2IN013

A robot simulation program that allows users to control and simulate a robot in both graphical (GUI) and command-line (CLI) modes. The robot can navigate through an environment while providing real-time position and angle information.

## Project Structure

The project follows an MVC (Model-View-Controller) architecture:

```
src/
├── controller/     # Contains simulation control logic
├── model/         # Contains robot and map models
├── utils/         # Utility functions
├── view/          # GUI and visualization components
└── main.py        # Main entry point
```

## Requirements
- Python 3.x
- Required Python packages (will be added automatically)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/arikarakas74/LAFC-Projet-Robotique.git
    ```

2. Navigate to the project directory:
    ```bash
    cd LAFC-Projet-Robotique
    ```

## Running the Program

The program can be run in two modes:

### 1. GUI Mode (Graphical Interface)
This is the default mode that provides a visual interface for robot simulation:

```bash
python3 src/main.py
```
or explicitly:
```bash
python3 src/main.py --gui
```

In GUI mode, you can control the robot using:
- W key: Move forward
- S key: Move backward
- (Additional controls may be available)

The simulation will display real-time updates of the robot's position and angle.

### 2. CLI Mode (Command Line Interface)
For command-line operation without graphical interface:

```bash
python3 src/main.py --cli
```

In CLI mode:
1. You'll be prompted to enter start position coordinates (X: 0-800, Y: 0-600)
2. The simulation will run and display robot position updates in the terminal

## Features
- Real-time position and angle tracking
- Multiple operation modes (GUI/CLI)
- Interactive robot control in GUI mode
- Coordinate-based positioning system
- Robot movement simulation with precise angle calculations

## Development

The project uses Git for version control. Main branches:
- `main`: Primary development branch
- `src2`: Alternative development branch

To switch between branches:
```bash
git checkout main  # or src2
```

## Troubleshooting

If you encounter the "python: command not found" error, try using `python3` instead of `python` in all commands.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

## Trello
[Project Trello Board](https://trello.com/invite/b/6790cac1e266a0256f541dae/ATTIf9a8031f4e259cceb72fa6d61ba8627b61608668/robot-project)

## Files Overview
The code is divided into several components following the MVC pattern:

- **`model/map_model.py`**: Contains the `MapModel` class that handles the environment representation
- **`model/robot.py`**: Contains the `Robot` class, which defines the robot's movement logic
- **`controller/simulation_controller.py`**: Contains the simulation control logic
- **`view/app_view.py`**: Handles the graphical user interface (GUI)
- **`main.py`**: The entry point of the program

## How It Works
- The program provides a simulation environment for a robot
- In GUI mode, the robot can be controlled using keyboard inputs (W for forward, S for backward)
- The simulation provides real-time feedback of the robot's position (X, Y) and angle
- The robot's movement is simulated with precise calculations for position and orientation

## Example Usage

1. Start the program in GUI mode:
   ```bash
   python3 src/main.py
   ```
2. The simulation window will open
3. Use the following controls:
   - Press W to move the robot forward
   - Press S to move the robot backward
4. Watch the real-time updates of the robot's position and angle in the terminal

