# LAFC-Projet-Robotique - LU2IN013

A robot simulation program that allows users to control and simulate a robot using different interfaces. The project provides a Tkinter-based GUI, a VPython 3D simulation environment, and a command-line (CLI) mode. The robot can navigate through an environment while providing real-time position and angle information.

## Project Structure

The project follows an MVC (Model-View-Controller) architecture:

```
src/
├── controller/     # Contains simulation control logic and strategies
├── model/          # Contains robot and map models
├── robot/          # Robot implementations
├── utils/          # Utility functions
├── view/           # GUI and visualization components
├── cli_main.py     # CLI entry point
├── gui_main.py     # Tkinter GUI entry point
├── vpython_main.py # VPython 3D interface entry point
└── main.py         # Main entry point
```

## Requirements

- Python 3.x
- Tkinter (for GUI mode)
- VPython (for 3D simulation mode)
- Other dependencies will be installed automatically

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/LAFC-Projet-Robotique.git
    ```

2. Navigate to the project directory:
    ```bash
    cd LAFC-Projet-Robotique
    ```

3. (Optional) Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. Install dependencies:
    ```bash
    pip install vpython  # Required for 3D simulation
    ```

## Running the Program

The program can be run in three different modes:

### 1. Tkinter GUI Mode

To run the simulation with the Tkinter graphical interface:

```bash
python3 src/gui_main.py
```

This will open a window with:
- A canvas displaying the robot
- Control buttons for moving the robot and setting waypoints
- Real-time information about the robot's position and orientation

### 2. VPython 3D Simulation Mode

To run the simulation with the VPython 3D interface:

```bash
python3 src/vpython_main.py
```

This will open a web browser with:
- A 3D visualization of the robot and environment
- Control buttons in the interface
- The ability to set start and end positions by clicking in the 3D environment

### 3. CLI Mode (Command Line Interface)

For command-line operation without graphical interface:

```bash
python3 src/cli_main.py
```

In CLI mode:
1. You'll be prompted to enter commands
2. The simulation will run and display robot position updates in the terminal

### Main Entry Point

You can also use the main entry point which supports selecting the interface:

```bash
python3 src/main.py          # Defaults to GUI mode
python3 src/main.py --gui    # Explicit GUI mode
python3 src/main.py --cli    # CLI mode
python3 src/main.py --vpython # VPython 3D mode
```

## Features

- Multiple interface options (Tkinter GUI, VPython 3D, CLI)
- Real-time position and angle tracking
- Interactive robot control
- Coordinate-based positioning system
- Path planning and obstacle detection
- Movement strategies (polygon drawing, beacon following)
- Image capture and analysis (in VPython mode)

## Interacting with the Simulation

### Tkinter Interface
- Use the control panel buttons to:
  - Set start and end positions
  - Draw a square path
  - Reset the simulation
  - Follow a path to the goal

### VPython 3D Interface
- Use the control panel buttons to:
  - Set start and beacon positions (click in the 3D view after selecting)
  - Run the simulation
  - Draw a square path
  - Follow the beacon
  - Reset the simulation
  - Capture and analyze images

## Troubleshooting

If you encounter any of these issues:

1. "python: command not found" - Try using `python3` instead of `python` in all commands.
2. If VPython doesn't open properly, make sure you have a modern web browser installed.
3. On macOS, if Tkinter is not available, you may need to install Python with Tkinter support:
   ```bash
   brew install python-tk
   ```

## Documentation

For more detailed documentation, see the `documentation/` directory, especially:
- `project_documentation.md`: Comprehensive documentation of all components

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

