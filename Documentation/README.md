# LAFC-Projet-Robotique Technical Documentation

## Architecture Overview

The project follows the Model-View-Controller (MVC) architecture pattern, with clear separation of concerns between data models, visualization components, and control logic.

### Component Relationships

```
[Model Layer] <-> [Controller Layer] <-> [View Layer]
     ^                    ^                    ^
     |                    |                    |
RobotModel    SimulationController    VpythonView/GUI/CLI
MapModel      RobotController         ControlPanel
Clock         MapController          RobotView/MapView
```

## Detailed Component Documentation

### Model Layer

#### RobotModel (`src/model/robot.py`)
- **Purpose**: Manages robot state and behavior
- **Key Properties**:
  - `x`, `y`: Current position coordinates
  - `direction_angle`: Current orientation in radians
  - `motor_speeds`: Dictionary of left/right motor speeds
- **Key Methods**:
  - `update_position(delta_time)`: Updates robot position based on motor speeds
  - `set_motor_speed(motor, speed)`: Sets individual motor speeds
  - `get_position()`: Returns current position and orientation

#### MapModel (`src/model/map_model.py`)
- **Purpose**: Manages environment and obstacles
- **Key Properties**:
  - `obstacles`: List of obstacle positions
  - `end_position`: Target/beacon position
  - `dimensions`: Environment size
- **Key Methods**:
  - `add_obstacle(x, y)`: Adds obstacle to environment
  - `is_valid_position(x, y)`: Checks if position is valid
  - `get_nearest_obstacle(x, y)`: Finds closest obstacle

#### Clock (`src/model/clock.py`)
- **Purpose**: Manages simulation timing
- **Key Methods**:
  - `get_time()`: Returns current simulation time
  - `get_delta_time()`: Returns time since last update
  - `update()`: Updates simulation time

### Controller Layer

#### SimulationController (`src/controller/simulation_controller.py`)
- **Purpose**: Main simulation orchestrator
- **Key Properties**:
  - `map_model`: Reference to environment model
  - `robot_model`: Reference to robot model
  - `robot_controller`: Robot movement controller
- **Key Methods**:
  - `update(delta_time)`: Updates simulation state
  - `start_simulation()`: Initializes simulation
  - `stop_simulation()`: Stops simulation

#### RobotController (`src/controller/robot_controller.py`)
- **Purpose**: Manages robot movement
- **Key Methods**:
  - `move_forward()`: Sets forward movement
  - `move_backward()`: Sets backward movement
  - `turn_left()`, `turn_right()`: Rotation control
  - `stop()`: Stops robot movement

#### StrategyAsync (`src/controller/StrategyAsync.py`)
- **Purpose**: Implements movement patterns
- **Key Classes**:
  - `AsyncCommande`: Base class for all strategies
  - `Accelerer`: Gradual speed increase
  - `Freiner`: Gradual speed decrease
  - `Avancer`: Forward movement
  - `Tourner`: Rotation movement
  - `PolygonStrategy`: Draws regular polygons
  - `FollowMovingBeaconStrategy`: Follows moving target
  - `CommandeComposite`: Combines multiple commands

### View Layer

#### VpythonView (`src/view/vpython_view.py`)
- **Purpose**: 3D visualization using VPython
- **Key Methods**:
  - `update_display()`: Updates 3D visualization
  - `handle_keydown(event)`: Processes keyboard input
  - `draw_robot()`: Renders robot in 3D
  - `draw_environment()`: Renders environment

#### ControlPanel (`src/view/control_panel.py`)
- **Purpose**: GUI control interface
- **Key Features**:
  - Speed control sliders
  - Movement buttons
  - Status display
  - Strategy selection

#### RobotView/MapView (`src/view/robot_view.py`, `src/view/map_view.py`)
- **Purpose**: 2D visualization components
- **Key Methods**:
  - `draw_robot()`: Renders robot in 2D
  - `draw_map()`: Renders environment
  - `update_display()`: Updates visualization

## Movement Strategies

### Basic Movements
1. **Acceleration/Deceleration**
   ```python
   Accelerer(target_speed, duration)
   Freiner(current_speed, duration)
   ```

2. **Linear Movement**
   ```python
   Avancer(distance_cm, vitesse)
   ```

3. **Rotation**
   ```python
   Tourner(angle_rad, vitesse_deg_s)
   ```

### Complex Strategies
1. **Polygon Drawing**
   ```python
   PolygonStrategy(n, side_length_cm, vitesse_avance, vitesse_rotation)
   ```
   - `n`: Number of sides
   - `side_length_cm`: Length of each side
   - `vitesse_avance`: Forward speed
   - `vitesse_rotation`: Rotation speed

2. **Beacon Following**
   ```python
   FollowMovingBeaconStrategy(vitesse_rotation, vitesse_avance, tolerance_distance=5, step_distance=5)
   ```
   - `vitesse_rotation`: Rotation speed
   - `vitesse_avance`: Forward speed
   - `tolerance_distance`: Distance threshold for target reached
   - `step_distance`: Movement step size

## Event Flow

1. **User Input**
   - Keyboard events → View Layer
   - GUI controls → View Layer

2. **Control Processing**
   - View → Controller
   - Controller processes input
   - Controller updates Model

3. **State Update**
   - Model updates robot state
   - Model updates environment state

4. **Visualization**
   - Model → View
   - View updates display

## Error Handling

1. **Collision Detection**
   - MapModel validates positions
   - RobotModel checks for collisions
   - Controller handles collision responses

2. **Boundary Checking**
   - MapModel validates coordinates
   - Prevents out-of-bounds movement

3. **Strategy Validation**
   - Strategy classes validate parameters
   - Error handling for invalid configurations

## Performance Considerations

1. **Update Frequency**
   - Clock controls simulation timing
   - Configurable update rates
   - Smooth animation handling

2. **Resource Management**
   - Efficient 3D rendering
   - Memory management for large environments
   - Cleanup of unused resources

## Future Improvements

1. **Potential Enhancements**
   - Additional movement strategies
   - Enhanced collision detection
   - More visualization options
   - Network multiplayer support

2. **Optimization Opportunities**
   - Improved rendering performance
   - Better memory management
   - Enhanced strategy execution 