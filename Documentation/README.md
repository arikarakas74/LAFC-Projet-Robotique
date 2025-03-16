# LAFC-Projet-Robotique - Comprehensive Documentation

## Project Overview

The LAFC-Projet-Robotique is a robot simulation program that allows users to control and simulate a robot's movement in a 3D environment. The application follows the Model-View-Controller (MVC) architecture pattern and can run in both GUI (graphical user interface) and CLI (command-line interface) modes.

## Code Structure

The project is organized following the MVC pattern, with clear separation of concerns:

```
src/
├── controller/     # Contains simulation control logic
│   ├── map_controller.py
│   ├── robot_controller.py
│   ├── simulation_controller.py
│   └── strategy.py           # Movement strategies implementation
├── model/          # Contains data models
│   ├── clock.py
│   ├── map_model.py
│   └── robot.py
├── utils/          # Utility functions
│   ├── geometry.py
│   └── geometry3d.py
├── view/           # UI components
│   ├── control_panel.py
│   ├── map_view.py
│   ├── robot_view.py
│   └── robot_view_3d.py
├── cli_main.py     # CLI mode entry point
├── gui_main.py     # GUI mode entry point
└── main.py         # Application entry point
```

## Core Components

### 1. Entry Points

#### `main.py`
The main entry point for the application that:
- Parses command-line arguments to determine the execution mode (GUI or CLI)
- Imports and calls the appropriate mode-specific entry point

#### `gui_main.py`
Entry point for the GUI mode that:
- Creates the main application window using Tkinter
- Initializes all necessary models, views, and controllers
- Sets up the user interface with robot visualization and control panels
- Handles keyboard input for robot control

#### `cli_main.py`
Entry point for the CLI mode that:
- Initializes a headless simulation without a graphical interface
- Sets up the models and controllers
- Prints robot state updates to the console
- Provides a thread for processing user input from the command line

### 2. Models

#### `model/robot.py` - `RobotModel`
Represents the robot in the simulation with:
- Physical attributes (wheel base width, wheel diameter)
- Position coordinates (x, y) and direction angle
- Motor speeds and positions for both left and right wheels
- Methods for updating position and setting motor speeds
- Collision detection using the map model

#### `model/map_model.py` - `MapModel`
Represents the environment in which the robot operates:
- Manages obstacles, start position, and end position
- Provides methods for adding, removing, and moving obstacles
- Implements collision detection logic
- Uses an observer pattern to notify listeners of changes

#### `model/clock.py` - `Clock`
Manages time in the simulation:
- Runs a continuous timer loop
- Notifies subscribers about time updates
- Used to maintain consistent simulation speed

### 3. Controllers

#### `controller/robot_controller.py` - `RobotController`
Controls the robot's movement:
- Provides methods for adjusting motor speeds
- Handles keyboard input in CLI mode
- Implements movement commands (forward, backward, turning)

#### `controller/simulation_controller.py` - `SimulationController`
Core logic for the simulation:
- Updates robot physics based on motor speeds
- Manages the simulation loop
- Implements special features like square drawing
- Logs robot positions for traceability
- Notifies listeners of state changes

#### `controller/map_controller.py` - `MapController`
Manages interactions with the map:
- Handles user input for map manipulation
- Processes drawing of obstacles
- Controls placement of start and end positions

### 4. Views

#### `view/robot_view.py` - `RobotView`
Visualization of the robot:
- Renders the robot on a canvas
- Draws the robot's trajectory
- Updates position and angle labels
- Receives state updates from the simulation controller

#### `view/robot_view_3d.py` - `RobotView3D`
Visualization of the robot in 3D:
- Renders the robot in a 3D environment
- Handles 3D transformations and rendering

#### `view/map_view.py` - `MapView`
Visualization of the environment:
- Renders obstacles, start position, and end position
- Updates the display based on map model changes
- Manages the canvas for drawing

#### `view/control_panel.py` - `ControlPanel`
User interface for controlling the simulation:
- Provides buttons for starting/stopping the simulation
- Includes controls for drawing a square
- Displays control instructions

### 5. Utilities

#### `utils/geometry.py`
Contains mathematical utility functions:
- `point_in_polygon`: Determines if a point is inside a polygon (for collision detection)
- `normalize_angle`: Keeps angles within the range of [-π, π]

#### `utils/geometry3d.py`
Contains 3D geometry utility functions:
- `rotate_point`: Rotates a point around a given axis
- `translate_point`: Translates a point in 3D space

## Functionality Flow

### Initialization Process

1. The application starts from `main.py` which determines the mode (GUI or CLI)
2. In GUI mode:
   - `gui_main.py` creates a Tkinter application
   - Models are initialized (MapModel, RobotModel)
   - Views are created and attached to the models
   - Controllers are set up to connect models and views
   - Event bindings are established for keyboard control

3. In CLI mode:
   - `cli_main.py` creates a HeadlessSimulation
   - Models and controllers are initialized
   - A thread is started to accept keyboard input
   - State changes are printed to the console

### Simulation Loop

1. The `SimulationController` runs a continuous loop in a separate thread
2. In each iteration:
   - Time delta is calculated
   - Robot physics are updated based on motor speeds
   - New position and orientation are calculated
   - Collision detection is performed
   - State listeners are notified of changes
   - Positions are logged for traceability

### Robot Movement Physics

The robot's movement follows a differential drive model:
1. Left and right wheel speeds determine:
   - Linear velocity (average of both wheels)
   - Angular velocity (difference between wheels divided by wheel base width)
2. New position is calculated using:
   - Current position
   - Direction angle
   - Linear velocity
   - Time delta
3. New angle is calculated using angular velocity and time delta

### Robot Control

Robot control is implemented through:
1. Direct motor speed commands:
   - `increase_left_speed()`
   - `decrease_left_speed()`
   - `increase_right_speed()`
   - `decrease_right_speed()`
2. High-level movement commands:
   - `move_forward()`
   - `move_backward()`
3. In GUI mode, these commands are bound to keyboard keys:
   - W: Move forward
   - S: Move backward
   - Q: Increase left wheel speed
   - A: Decrease left wheel speed
   - E: Increase right wheel speed
   - D: Decrease right wheel speed

### Special Features

#### Square Drawing
The application includes a flexible polygon drawing feature:
1. `draw_polygon(sides, side_length)` method enables drawing any regular polygon
2. The robot follows a sequence of moves:
   - Move forward to draw a side
   - Rotate by the appropriate angle (360°/sides)
   - Repeat for all sides
3. The polygon drawing process is tracked in real-time
4. The user interface provides a dialog to specify the number of sides

## Key Design Patterns

### MVC Architecture
- **Models**: Represent data structures and business logic (RobotModel, MapModel)
- **Views**: Handle the visual representation (RobotView, RobotView3D, MapView)
- **Controllers**: Coordinate between models and views (SimulationController, RobotController)

### Observer Pattern
- Used for notifying components of state changes
- Implemented through callbacks and event listeners

### State Pattern
- The robot and simulation have well-defined states
- State transitions are managed by controllers

## Logging and Traceability

The application includes console logging for key operations:
- Robot movements and position tracking
- Polygon drawing progress
- Beacon following status
- Collision detection

## User Interaction

### GUI Mode
- Interactive control through keyboard inputs
- Visual feedback of robot movement
- Real-time position and angle display
- Canvas for visualizing the robot and its environment

### CLI Mode
- Command-line control through keyboard inputs
- Text-based feedback of robot position and angle
- Suitable for headless environments or testing

## Performance Considerations

- Simulation runs in a separate thread to avoid UI blocking
- Time delta is used to ensure consistent movement regardless of processing speed
- Simulation speed can be adjusted with the `SPEED_MULTIPLIER` constant

## Conclusion

The LAFC-Projet-Robotique is a well-structured simulation application that demonstrates good software design principles. It effectively separates concerns using the MVC pattern, provides multiple interfaces for different use cases, and implements realistic physics for robot movement simulation. The codebase is organized in a modular, extensible way that would allow for future enhancements such as more complex environments, additional robot types, or advanced movement algorithms. 