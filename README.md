# LAFC-Projet-Robotique

A 3D robot simulation project with multiple visualization options (VPython 3D, GUI, and CLI interfaces).

## Project Overview

This project implements a robot simulation environment with the following key features:
- 3D visualization using VPython
- Multiple control interfaces (3D, GUI, CLI)
- Advanced movement strategies (polygon drawing, beacon following)
- Real-time robot control and monitoring
- Configurable simulation environment

## Project Structure

```
LAFC-Projet-Robotique/
├── src/
│   ├── model/                 # Core data models
│   │   ├── robot.py          # Robot state and behavior
│   │   ├── map_model.py      # Environment and obstacles
│   │   └── clock.py          # Simulation timing
│   ├── controller/           # Control logic
│   │   ├── simulation_controller.py  # Main simulation control
│   │   ├── robot_controller.py      # Robot movement control
│   │   ├── map_controller.py        # Environment control
│   │   └── StrategyAsync.py         # Movement strategies
│   ├── view/                 # Visualization components
│   │   ├── vpython_view.py          # 3D visualization
│   │   ├── vpython_control_panel.py # 3D control interface
│   │   ├── control_panel.py         # GUI control interface
│   │   ├── robot_view.py            # Robot visualization
│   │   └── map_view.py              # Environment visualization
│   ├── utils/                # Utility functions
│   │   └── geometry.py      # Geometric calculations
│   ├── vpython_main.py      # 3D visualization entry point
│   ├── gui_main.py          # GUI interface entry point
│   ├── cli_main.py          # CLI interface entry point
│   └── main.py              # Main program entry point
├── Documentation/           # Project documentation
└── requirements.txt        # Project dependencies
```

## Core Components

### Model Layer (`src/model/`)
- `RobotModel`: Manages robot state, position, and movement
- `MapModel`: Handles environment, obstacles, and positions
- `Clock`: Controls simulation timing and updates

### Controller Layer (`src/controller/`)
- `SimulationController`: Orchestrates the simulation
- `RobotController`: Manages robot movement and control
- `MapController`: Handles environment interactions
- `StrategyAsync`: Implements movement patterns (polygon drawing, beacon following)

### View Layer (`src/view/`)
- `VpythonView`: 3D visualization using VPython
- `VPythonControlPanel`: 3D interface controls
- `ControlPanel`: GUI interface controls
- `RobotView`: Robot visualization components
- `MapView`: Environment visualization components

## Requirements

- Python 3.x
- VPython for 3D visualization
- PyQt5 for GUI interface
- Additional dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/arikarakas74/LAFC-Projet-Robotique.git
cd LAFC-Projet-Robotique
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Program

### 3D Visualization (VPython)
```bash
python3 src/vpython_main.py
```

### GUI Interface
```bash
python3 src/gui_main.py
```

### CLI Interface
```bash
python3 src/cli_main.py
```

## Key Features

### Movement Strategies
- Polygon Drawing: Draw regular polygons with configurable sides and size
- Beacon Following: Follow a moving beacon with adjustable parameters
- Basic Movements: Forward, backward, rotation, acceleration, deceleration

### Control Interfaces
- 3D Visualization: Interactive 3D view with real-time control
- GUI Interface: Traditional window-based control panel
- CLI Interface: Command-line control and monitoring

### Environment Features
- Configurable obstacles
- Position tracking
- Collision detection
- Real-time updates

## Development Guidelines

1. Follow the MVC architecture pattern
2. Implement new features as separate strategies
3. Maintain compatibility across all interfaces
4. Document new functions and classes
5. Test changes across all visualization modes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

