# Project Documentation

## Project Structure

This project implements a robot simulation environment with different graphical interfaces (Tkinter and VPython). It follows the Model-View-Controller (MVC) architecture pattern.

### Directory Structure

```
LAFC-Projet-Robotique/
├── documentation/              # Project documentation
│   ├── project_documentation.md  # This file
│   └── ...                     # Other documentation files
│
├── src/                        # Source code
│   ├── controller/             # Controller components
│   │   ├── StrategyAsync.py    # Robot control strategies
│   │   ├── adapter.py          # Adapter interfaces
│   │   ├── map_controller.py   # Map controller
│   │   ├── robot_controller.py # Robot controller
│   │   └── simulation_controller.py # Overall simulation controller
│   │
│   ├── model/                  # Model components
│   │   ├── clock.py           # Clock for time management
│   │   ├── map_model.py       # Map data model
│   │   └── robot.py           # Robot model
│   │
│   ├── robot/                  # Robot-specific code
│   │   └── robot.py           # Concrete robot implementation
│   │
│   ├── utils/                  # Utility functions
│   │   └── geometry.py        # Geometric calculations
│   │
│   ├── view/                   # View components
│   │   ├── control_panel.py   # Control panel (Tkinter)
│   │   ├── map_view.py        # Map visualization (Tkinter)
│   │   ├── robot_view.py      # Robot visualization (Tkinter)
│   │   ├── vpython_control_panel.py # Control panel (VPython)
│   │   └── vpython_view.py    # 3D visualization (VPython)
│   │
│   ├── cli_main.py            # Command-line interface entry point
│   ├── gui_main.py            # Tkinter GUI entry point
│   ├── main.py                # Main entry point
│   └── vpython_main.py        # VPython GUI entry point
└── ...
```

### Application Architecture

The project follows the MVC (Model-View-Controller) architecture:

1. **Model**: Contains the core data structures and logic for the robot and map.
   - `model/robot.py`: Represents the robot's state and physics.
   - `model/map_model.py`: Handles the map state, start/end positions, and obstacles.
   - `model/clock.py`: Manages time for the simulation.

2. **View**: Responsible for displaying the robot, map, and controls.
   - Tkinter interface: `robot_view.py`, `map_view.py`, `control_panel.py`
   - VPython 3D interface: `vpython_view.py`, `vpython_control_panel.py`

3. **Controller**: Connects the models and views, manages user input.
   - `simulation_controller.py`: Orchestrates the entire simulation.
   - `robot_controller.py`: Controls the robot's movements.
   - `map_controller.py`: Manages interactions with the map.
   - `StrategyAsync.py`: Implements robot movement strategies.

### Entry Points

The application provides multiple entry points:
- `main.py`: Main application entry point.
- `gui_main.py`: Launches the Tkinter GUI.
- `vpython_main.py`: Launches the VPython 3D interface.
- `cli_main.py`: Command-line interface.

---

## `src/main.py`

**Purpose:** This script serves as the main entry point for the Robot Simulation application. It determines the execution mode (GUI, CLI, or VPython) based on command-line arguments and launches the corresponding interface.

**Functions:**

### `main()`

-   **Signature:** `main()`
-   **Parameters:** None
-   **Returns:** `None`
-   **Description:**
    -   Initializes an `ArgumentParser` to handle command-line arguments.
    -   Defines an optional positional argument `mode` with choices:
        -   `'gui'`: Runs the graphical user interface (default).
        -   `'cli'`: Runs the command-line interface.
        -   `'vpython'`: Runs the VPython 3D simulation.
    -   Parses the provided arguments.
    -   Based on the selected `mode`:
        -   Imports `gui_main` and calls `gui_main.run_gui()` if `mode` is `'gui'`.
        -   Imports `cli_main` and calls `cli_main.run_cli()` if `mode` is `'cli'`.
        -   Imports `vpython_main` and calls `vpython_main.run_vpython()` if `mode` is `'vpython'`.
-   **Relationship:** Acts as the central dispatcher for the application, selecting the appropriate user interface or simulation environment based on user command-line input.
-   **Callers:** This function is executed when `src/main.py` is run as the main script (`if __name__ == "__main__":`).
-   **Calls:**
    -   `argparse.ArgumentParser`
    -   `ArgumentParser.add_argument`
    -   `ArgumentParser.parse_args`
    -   `gui_main.run_gui` (conditionally)
    -   `cli_main.run_cli` (conditionally)
    -   `vpython_main.run_vpython` (conditionally)

## `src/gui_main.py`

**Purpose:** This script sets up and runs the main graphical user interface (GUI) for the robot simulation using the `tkinter` library. It integrates the Model-View-Controller (MVC) components for the simulation.

**Classes:**

### `MainApplication(tk.Tk)`

-   **Inherits from:** `tkinter.Tk` (the main window class)
-   **Description:** Represents the main application window and orchestrates the creation and layout of various GUI components, models, and controllers.
-   **Methods:**
    -   **`__init__(self)`**
        -   **Signature:** `__init__(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:**
            -   Initializes the `tk.Tk` superclass.
            -   Sets the window title to "Robot Simulation MVC".
            -   Calls `_create_menu()` to set up the file menu.
            -   Creates main frames (`main_frame`, `canvas_frame`, `controls_frame`) using `ttk.Frame` for layout.
            -   Initializes the data models: `MapModel` and `RobotModel`.
            -   Initializes the `SimulationController`, passing `cli_mode=False`.
            -   Creates the views: `RobotView` and `MapView`, associating them with their respective controllers and parent frames.
            -   Creates the `MapController`, linking the map model and view.
            -   Creates the `ControlPanel` for user interaction (start, reset buttons), linking it to the controllers.
            -   Registers `on_state_update` as a listener to the simulation controller.
            -   Binds keyboard keys (`q`, `a`, `e`, `d`, `w`, `s`) to robot control methods in the `SimulationController`.
        -   **Relationship:** Acts as the constructor and setup method for the entire GUI application, initializing all necessary components and linking them together.
        -   **Calls:**
            -   `super().__init__()`
            -   `self.title()`
            -   `self._create_menu()`
            -   `ttk.Frame()`
            -   `MapModel()`
            -   `RobotModel()`
            -   `SimulationController()`
            -   `RobotView()`
            -   `MapView()`
            -   `MapController()`
            -   `ControlPanel()`
            -   `self.sim_controller.add_state_listener()`
            -   `self.bind()` (multiple times)
    -   **`_create_menu(self)`**
        -   **Signature:** `_create_menu(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Creates the main menu bar with a "File" menu containing a "Quit" option that calls the `self.quit` method.
        -   **Relationship:** Responsible for setting up the application's menu.
        -   **Calls:**
            -   `tk.Menu()`
            -   `self.config()`
            -   `menubar.add_cascade()`
            -   `file_menu.add_command()`
    -   **`on_state_update(self, state)`**
        -   **Signature:** `on_state_update(self, state)`
        -   **Parameters:**
            -   `self`
            -   `state`: The current state information from the simulation.
        -   **Returns:** `None`
        -   **Description:** Placeholder method intended to be called by the `SimulationController` when the simulation state changes. Currently, it does nothing (`pass`), but could be implemented to update GUI elements based on the `state`.
        -   **Relationship:** Callback function for simulation state updates.
        -   **Called By:** `SimulationController` (via listener mechanism).

**Functions:**

### `run_gui()`

-   **Signature:** `run_gui()`
-   **Parameters:** None
-   **Returns:** `None`
-   **Description:** Creates an instance of the `MainApplication` class and starts the `tkinter` main event loop (`app.mainloop()`), which makes the GUI window appear and become interactive.
-   **Relationship:** The primary function to launch the GUI version of the application.
-   **Callers:** `src/main.py` (when `mode` is `'gui'`).
-   **Calls:**
    -   `MainApplication()`
    -   `MainApplication.mainloop()`

**Dependencies:**

-   `tkinter` (standard library)
-   `controller.map_controller.MapController`
-   `view.robot_view.RobotView`
-   `view.map_view.MapView`
-   `view.control_panel.ControlPanel`
-   `model.map_model.MapModel`
-   `model.robot.RobotModel`
-   `controller.simulation_controller.SimulationController`

## `src/cli_main.py`

**Purpose:** Provides a command-line interface (CLI) for running the robot simulation without a graphical interface. It allows viewing the robot's state in the console and potentially interacting with it via keyboard commands (though direct interaction setup is primarily in `RobotController`).

**Classes:**

### `HeadlessSimulation`

-   **Description:** Encapsulates the setup and execution logic for running the simulation in a non-GUI (headless) mode.
-   **Methods:**
    -   **`__init__(self)`**
        -   **Signature:** `__init__(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:**
            -   Initializes the `MapModel` and `RobotModel`.
            -   Initializes the `SimulationController`, crucially passing `cli_mode=True`. This enables the `RobotController` within it to start a separate thread for handling CLI keyboard input.
            -   Registers the `print_state` method as a listener to the simulation controller to receive state updates.
        -   **Relationship:** Constructor for the CLI simulation environment.
        -   **Calls:**
            -   `MapModel()`
            -   `RobotModel()`
            -   `SimulationController(..., cli_mode=True)`
            -   `self.sim_controller.add_state_listener()`
    -   **`print_state(self, state)`**
        -   **Signature:** `print_state(self, state)`
        -   **Parameters:**
            -   `self`
            -   `state` (dict): A dictionary containing the robot's current state (`x`, `y`, `angle`, `left_speed`, `right_speed`).
        -   **Returns:** `None`
        -   **Description:** Formats and prints the robot's current position, angle (in degrees), and motor speeds to the standard output.
        -   **Relationship:** Callback function used by the `SimulationController` to display state updates in the CLI.
        -   **Called By:** `SimulationController` (via listener mechanism).
        -   **Calls:**
            -   `print()`
            -   `math.degrees()`
    -   **`run(self)`**
        -   **Signature:** `run(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:**
            -   Prints a startup message.
            -   Starts the simulation loop by calling `self.sim_controller.run_simulation()`. This likely starts a background thread for the simulation logic.
            -   **(Note: The code immediately sets motor speeds to 0 after starting the simulation. This might be intended as an initial state or could potentially stop the robot instantly if `run_simulation` doesn't block.)**
            -   Enters an infinite loop (`while True: time.sleep(0.1)`), keeping the main thread alive.
            -   Includes a `try...except KeyboardInterrupt` block to catch Ctrl+C, which then calls `self.sim_controller.stop_simulation()` and prints a shutdown message.
        -   **Relationship:** The main execution method for the CLI simulation. Starts the simulation and keeps the application running until interrupted.
        -   **Calls:**
            -   `print()`
            -   `self.sim_controller.run_simulation()`
            -   `self.sim_controller.robot_model.set_motor_speed()` (potentially overriding initial simulation behavior)
            -   `time.sleep()`
            -   `self.sim_controller.stop_simulation()` (on KeyboardInterrupt)

**Functions:**

### `run_cli()`

-   **Signature:** `run_cli()`
-   **Parameters:** None
-   **Returns:** `None`
-   **Description:** Creates an instance of the `HeadlessSimulation` class and calls its `run()` method to start the CLI simulation.
-   **Relationship:** The primary function to launch the CLI version of the application.
-   **Callers:** `src/main.py` (when `mode` is `'cli'`).
-   **Calls:**
    -   `HeadlessSimulation()`
    -   `HeadlessSimulation.run()`

**Dependencies:**

-   `time` (standard library)
-   `math` (standard library)
-   `controller.simulation_controller.SimulationController`
-   `model.map_model.MapModel`
-   `model.robot.RobotModel`

## `src/vpython_main.py`

**Purpose:** This script initializes and runs the 3D simulation visualization using the VPython library. It sets up the necessary models, controllers, and VPython-specific views and control panels.

**Classes:**

### `MainApplication`

-   **Description:** Manages the setup and event handling for the VPython simulation environment.
-   **Methods:**
    -   **`__init__(self)`**
        -   **Signature:** `__init__(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:**
            -   Initializes the `MapModel` and `RobotModel`.
            -   Initializes the `SimulationController` with `cli_mode=False`.
            -   Initializes the `VpythonView`, providing it with the simulation controller and a reference to the `handle_keydown` method for keyboard event handling.
            -   Initializes the `MapController`. Note: It passes `None` for the `view` and `parent` arguments, suggesting the map might not be directly visualized or controlled via this controller in the VPython context, or its interaction is handled differently.
            -   Initializes the `VPythonControlPanel`, linking it to the controllers, the VPython view, and the map model.
            -   Binds the VPython scene's `keydown` event to the `self.handle_keydown` method.
        -   **Relationship:** Constructor for the VPython simulation application, setting up the core components and linking them.
        -   **Calls:**
            -   `MapModel()`
            -   `RobotModel()`
            -   `SimulationController()`
            -   `VpythonView()`
            -   `MapController()`
            -   `VPythonControlPanel()`
            -   `vpython.scene.bind()`
    -   **`handle_keydown(self, evt)`**
        -   **Signature:** `handle_keydown(self, evt)`
        -   **Parameters:**
            -   `self`
            -   `evt`: The VPython event object containing details about the key press.
        -   **Returns:** `None`
        -   **Description:**
            -   Callback function triggered by key presses in the VPython window.
            -   Retrieves the pressed key from `evt.key`.
            -   Based on the key (`q`, `a`, `e`, `d`, `w`, `s`), calls the corresponding speed or movement control methods on the `robot_controller` accessed via `self.sim_controller`.
            -   Includes `print` statements for debugging key presses.
        -   **Relationship:** Handles user keyboard input for controlling the robot within the VPython simulation.
        -   **Called By:** VPython event loop (when a `keydown` event occurs in the bound `scene`).
        -   **Calls:**
            -   `print()`
            -   `self.sim_controller.robot_controller.increase_left_speed()` (conditionally)
            -   `self.sim_controller.robot_controller.decrease_left_speed()` (conditionally)
            -   `self.sim_controller.robot_controller.increase_right_speed()` (conditionally)
            -   `self.sim_controller.robot_controller.decrease_right_speed()` (conditionally)
            -   `self.sim_controller.robot_controller.move_forward()` (conditionally)
            -   `self.sim_controller.robot_controller.move_backward()` (conditionally)

**Functions:**

### `run_vpython()`

-   **Signature:** `run_vpython()`
-   **Parameters:** None
-   **Returns:** `None`
-   **Description:**
    -   Creates an instance of the `MainApplication` class.
    -   Enters an infinite loop (`while True: time.sleep(0.1)`). This loop keeps the main thread alive, allowing the VPython window and its internal event loop to continue running and remain responsive.
-   **Relationship:** The primary function to launch the VPython simulation version of the application.
-   **Callers:** `src/main.py` (when `mode` is `'vpython'`).
-   **Calls:**
    -   `MainApplication()`
    -   `time.sleep()`

**Dependencies:**

-   `time` (standard library)
-   `controller.simulation_controller.SimulationController`
-   `model.map_model.MapModel`
-   `controller.map_controller.MapController`
-   `model.robot.RobotModel`
-   `view.vpython_view.VpythonView`
-   `view.vpython_control_panel.VPythonControlPanel`
-   `vpython` (external library)

## `src/controller/simulation_controller.py`

**Purpose:** This module defines the `SimulationController` class, which is responsible for managing the core simulation loop. It updates the robot's state based on physics calculations at regular intervals, runs the simulation in a separate thread, handles starting, stopping, and resetting the simulation, and notifies listeners (like views) about state changes.

**Constants:**

-   `SPEED_MULTIPLIER` (float): Intended multiplier to speed up or slow down the simulation time. (Note: Currently defined but not used in the `update_physics` calculation as of the analyzed code version).
-   `WHEEL_BASE_WIDTH` (float): The distance between the centers of the two wheels of the robot (in cm). Used in kinematic calculations.
-   `WHEEL_DIAMETER` (float): The diameter of the robot's wheels (in cm).
-   `WHEEL_RADIUS` (float): The radius of the robot's wheels (in cm), calculated from `WHEEL_DIAMETER`.

**Classes:**

### `SimulationController`

-   **Description:** Orchestrates the robot simulation, handling the time loop, physics updates, state management, and communication with other components.
-   **Attributes:**
    -   `robot_model` (`RobotModel`): The model representing the robot's state (position, orientation, motor speeds).
    -   `map_model` (`MapModel`): The model representing the simulation map (e.g., start position, obstacles).
    -   `robot_controller` (`RobotController`): The controller responsible for handling robot-specific actions and user input (like keyboard controls).
    -   `simulation_running` (bool): Flag indicating if the simulation loop is active.
    -   `listeners` (List[Callable[[dict], None]]): A list of callback functions to be notified of robot state updates.
    -   `update_interval` (float): The target time interval (in seconds) between simulation updates (e.g., 0.02 corresponds to 50 Hz).
    -   `position_logger` (`logging.Logger`): Logger instance configured to write robot position data to `traceability_positions.log`.
    -   `simulation_thread` (`threading.Thread` or `None`): The thread object running the `run_loop` method.
-   **Methods:**
    -   **`__init__(self, map_model, robot_model, cli_mode=False)`**
        -   **Signature:** `__init__(self, map_model: MapModel, robot_model: RobotModel, cli_mode: bool = False)`
        -   **Parameters:**
            -   `map_model`: The map model instance.
            -   `robot_model`: The robot model instance.
            -   `cli_mode`: Boolean flag indicating if the simulation is running in CLI mode (passed to `RobotController`).
        -   **Returns:** `None`
        -   **Description:** Initializes the controller, storing references to the models, creating a `RobotController` instance, setting up the listener list, defining the update interval, and configuring the position logger.
        -   **Relationship:** Constructor, sets up the simulation environment.
        -   **Calls:**
            -   `RobotController()`
            -   `logging.getLogger()`
            -   `logging.FileHandler()`
            -   `logging.Formatter()`
            -   `logger.setLevel()`
            -   `handler.setFormatter()`
            -   `logger.addHandler()`
    -   **`add_state_listener(self, callback)`**
        -   **Signature:** `add_state_listener(self, callback: Callable[[dict], None])`
        -   **Parameters:**
            -   `callback`: A function that accepts a dictionary representing the robot state.
        -   **Returns:** `None`
        -   **Description:** Adds the provided `callback` function to the `listeners` list.
        -   **Relationship:** Allows other components (e.g., views) to subscribe to state updates.
        -   **Called By:** `gui_main.MainApplication`, `cli_main.HeadlessSimulation`.
    -   **`_notify_listeners(self)`**
        -   **Signature:** `_notify_listeners(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Retrieves the current robot state using `self.robot_model.get_state()` and calls each registered listener function with this state.
        -   **Relationship:** Internal method for broadcasting state updates.
        -   **Called By:** `run_loop()`.
        -   **Calls:**
            -   `self.robot_model.get_state()`
            -   Listener callbacks (e.g., `gui_main.MainApplication.on_state_update`, `cli_main.HeadlessSimulation.print_state`).
    -   **`run_simulation(self)`**
        -   **Signature:** `run_simulation(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Starts the simulation if it's not already running. It ensures the robot is at the `map_model.start_position`, sets `simulation_running` to `True`, creates a new daemon thread targeting the `run_loop` method, and starts the thread.
        -   **Relationship:** Public method to initiate the simulation process.
        -   **Called By:** `cli_main.HeadlessSimulation.run()`, `view.control_panel.ControlPanel.start_simulation()`, `view.vpython_control_panel.VPythonControlPanel.start_simulation()`.
        -   **Calls:**
            -   `threading.Thread()`
            -   `thread.start()`
    -   **`run_loop(self)`**
        -   **Signature:** `run_loop(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** The core simulation loop executed by the background thread. It continuously calculates the time elapsed (`delta_time`) since the last iteration, calls `update_physics` to update the robot's state, calls `_notify_listeners` to inform subscribers, and then pauses for `self.update_interval` seconds. The loop continues as long as `self.simulation_running` is `True`.
        -   **Relationship:** The heart of the simulation, running asynchronously.
        -   **Called By:** `threading.Thread` (internally when `start()` is called).
        -   **Calls:**
            -   `time.time()`
            -   `self.update_physics()`
            -   `self._notify_listeners()`
            -   `time.sleep()`
    -   **`update_physics(self, delta_time)`**
        -   **Signature:** `update_physics(self, delta_time: float)`
        -   **Parameters:**
            -   `delta_time`: The time elapsed (in seconds) since the last physics update.
        -   **Returns:** `None`
        -   **Description:** Performs the kinematic calculations to update the robot's position (`x`, `y`) and orientation (`direction_angle`). It retrieves motor speeds from `robot_model`, converts them to linear velocities, calculates the overall linear and angular velocity of the robot based on the differential drive model. It handles both straight-line motion (when wheel velocities are equal) and curved motion (using calculations involving the radius of curvature). Finally, it updates the robot's state in the `robot_model` using `update_position` and calls `update_motors`. It also logs the new position.
        -   **Relationship:** Calculates the robot's movement based on motor speeds and time.
        -   **Called By:** `run_loop()`.
        -   **Calls:**
            -   `math.pi`, `math.cos`, `math.sin`, `math.degrees`
            -   `self.robot_model.update_position()`
            -   `self.robot_model.update_motors()`
            -   `self.position_logger.info()`
    -   **`stop_simulation(self)`**
        -   **Signature:** `stop_simulation(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Stops the simulation by setting `simulation_running` to `False`, which terminates the `run_loop`. It also calls the `stop()` method of the associated `robot_controller` (likely to stop any input handling threads) and waits for the `simulation_thread` to finish using `join()`.
        -   **Relationship:** Public method to gracefully halt the simulation.
        -   **Called By:** `cli_main.HeadlessSimulation.run` (on KeyboardInterrupt), `self.reset_simulation()`, `view.control_panel.ControlPanel.stop_simulation()`, `view.vpython_control_panel.VPythonControlPanel.stop_simulation()`.
        -   **Calls:**
            -   `self.robot_controller.stop()`
            -   `self.simulation_thread.join()` (if thread exists)
    -   **`reset_simulation(self)`**
        -   **Signature:** `reset_simulation(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Resets the simulation state. It first calls `stop_simulation()` to halt any ongoing simulation, then resets the robot's position (`x`, `y`) and angle (`direction_angle`) in the `robot_model` back to the initial state defined by `self.map_model.start_position` and 0.0 angle.
        -   **Relationship:** Public method to return the simulation to its starting configuration.
        -   **Called By:** `view.control_panel.ControlPanel.reset_simulation()`, `view.vpython_control_panel.VPythonControlPanel.reset_simulation()`.
        -   **Calls:**
            -   `self.stop_simulation()`

**Dependencies:**

-   `threading` (standard library)
-   `time` (standard library)
-   `math` (standard library)
-   `logging` (standard library)
-   `typing` (standard library)
-   `model.robot.RobotModel`
-   `controller.robot_controller.RobotController`
-   `model.map_model.MapModel` (implied via constructor)

## `src/controller/robot_controller.py`

**Purpose:** This module defines the `RobotController` class, which is responsible for handling direct control actions for the robot, primarily related to its movement (adjusting motor speeds). It can optionally run a separate thread to read keyboard input in CLI mode.

**Classes:**

### `RobotController`

-   **Description:** Provides methods to control the robot's motors and handles keyboard input when running in CLI mode.
-   **Attributes:**
    -   `robot_model` (`RobotModel`): Reference to the robot model to modify its state (motor speeds).
    -   `map_model` (`MapModel`): Reference to the map model (currently unused within this class's methods, but stored).
    -   `SPEED_STEP` (float, class attribute): The amount by which motor speeds are increased or decreased with each command (degrees/second).
-   **Methods:**
    -   **`__init__(self, robot_model, map_model, cli_mode=False)`**
        -   **Signature:** `__init__(self, robot_model: RobotModel, map_model: MapModel, cli_mode: bool = False)`
        -   **Parameters:**
            -   `robot_model`: The robot model instance.
            -   `map_model`: The map model instance.
            -   `cli_mode`: If `True`, starts a background thread to listen for keyboard input via `_start_input_thread`.
        -   **Returns:** `None`
        -   **Description:** Initializes the controller, storing references to the models. Conditionally starts the CLI input thread.
        -   **Relationship:** Constructor, sets up references and potentially the CLI input handler.
        -   **Called By:** `controller.simulation_controller.SimulationController.__init__()`.
        -   **Calls:** `self._start_input_thread()` (conditionally).
    -   **`_start_input_thread(self)`**
        -   **Signature:** `_start_input_thread(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Creates and starts a new daemon thread that executes the `_read_input` method.
        -   **Relationship:** Internal helper to launch the CLI input listener.
        -   **Called By:** `__init__()`.
        -   **Calls:** `threading.Thread()`, `thread.start()`.
    -   **`_read_input(self)`**
        -   **Signature:** `_read_input(self)`
        -   **Parameters:** `self`
        -   **Returns:** Never returns (infinite loop).
        -   **Description:** Runs in a separate thread (if `cli_mode` was True). Enters an infinite loop that prompts the user for input (`input(...)`), reads a key press, and calls the corresponding robot control method (`increase_left_speed`, `decrease_left_speed`, etc.) based on the key entered (`q`, `a`, `e`, `d`, `w`, `s`).
        -   **Relationship:** Handles keyboard input specifically for the CLI mode.
        -   **Called By:** `threading.Thread` (internally when `start()` is called).
        -   **Calls:**
            -   `input()`
            -   `str.strip()`
            -   `self.increase_left_speed()` (conditionally)
            -   `self.decrease_left_speed()` (conditionally)
            -   `self.increase_right_speed()` (conditionally)
            -   `self.decrease_right_speed()` (conditionally)
            -   `self.move_forward()` (conditionally)
            -   `self.move_backward()` (conditionally)
    -   **`stop(self)`**
        -   **Signature:** `stop(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Stops the robot by setting both left and right motor speeds to 0 in the `robot_model`.
        -   **Relationship:** Halts the robot's movement.
        -   **Called By:** `controller.simulation_controller.SimulationController.stop_simulation()`.
        -   **Calls:** `self.robot_model.set_motor_speed()` (twice).
    -   **`increase_left_speed(self)`**
        -   **Signature:** `increase_left_speed(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Increases the left motor speed by `SPEED_STEP`.
        -   **Relationship:** Control command.
        -   **Called By:** `_read_input()`, `gui_main.MainApplication` (via lambda binding), `vpython_main.MainApplication.handle_keydown()`.
        -   **Calls:** `self.robot_model.set_motor_speed()`.
    -   **`decrease_left_speed(self)`**
        -   **Signature:** `decrease_left_speed(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Decreases the left motor speed by `SPEED_STEP`.
        -   **Relationship:** Control command.
        -   **Called By:** `_read_input()`, `gui_main.MainApplication` (via lambda binding), `vpython_main.MainApplication.handle_keydown()`.
        -   **Calls:** `self.robot_model.set_motor_speed()`.
    -   **`increase_right_speed(self)`**
        -   **Signature:** `increase_right_speed(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Increases the right motor speed by `SPEED_STEP`.
        -   **Relationship:** Control command.
        -   **Called By:** `_read_input()`, `gui_main.MainApplication` (via lambda binding), `vpython_main.MainApplication.handle_keydown()`.
        -   **Calls:** `self.robot_model.set_motor_speed()`.
    -   **`decrease_right_speed(self)`**
        -   **Signature:** `decrease_right_speed(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Decreases the right motor speed by `SPEED_STEP`.
        -   **Relationship:** Control command.
        -   **Called By:** `_read_input()`, `gui_main.MainApplication` (via lambda binding), `vpython_main.MainApplication.handle_keydown()`.
        -   **Calls:** `self.robot_model.set_motor_speed()`.
    -   **`move_forward(self)`**
        -   **Signature:** `move_forward(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Increases the speed of both motors by `SPEED_STEP` to move the robot forward (or increase forward speed).
        -   **Relationship:** Control command.
        -   **Called By:** `_read_input()`, `gui_main.MainApplication` (via lambda binding), `vpython_main.MainApplication.handle_keydown()`.
        -   **Calls:** `self.robot_model.set_motor_speed()` (twice).
    -   **`move_backward(self)`**
        -   **Signature:** `move_backward(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Decreases the speed of both motors by `SPEED_STEP` to move the robot backward (or decrease forward speed/increase backward speed).
        -   **Relationship:** Control command.
        -   **Called By:** `_read_input()`, `gui_main.MainApplication` (via lambda binding), `vpython_main.MainApplication.handle_keydown()`.
        -   **Calls:** `self.robot_model.set_motor_speed()` (twice).

**Dependencies:**

-   `math` (standard library, though seemingly unused in this specific file)
-   `threading` (standard library)
-   `model.robot.RobotModel` (implied via constructor)
-   `model.map_model.MapModel` (implied via constructor)

## `src/controller/StrategyAsync.py`

**Purpose:** This module defines a framework for creating and executing asynchronous robot commands and strategies. It provides a base class `AsyncCommande` and several concrete command implementations (`Avancer`, `Tourner`, `Arreter`) as well as composite strategies (`PolygonStrategy`, `FollowBeaconByImageStrategy`, `CommandeComposite`). These commands are designed to be executed incrementally via a `step` method, allowing for non-blocking control flows.

**Classes:**

### `AsyncCommande` (Interface)

-   **Description:** Base class defining the interface for all asynchronous commands. It requires subclasses to implement `start`, `step`, and `is_finished` methods.
-   **Methods:**
    -   **`__init__(self, adapter=None)`**
        -   **Signature:** `__init__(self, adapter=None)`
        -   **Parameters:**
            -   `adapter`: An optional adapter object providing the interface to control the robot (e.g., set motor speeds, get sensor data).
        -   **Returns:** `None`
        -   **Description:** Stores the adapter reference.
    -   **`start(self)`** (Abstract)
        -   **Signature:** `start(self)`
        -   **Description:** Intended to initialize the command execution (e.g., set initial motor speeds). Must be implemented by subclasses.
    -   **`step(self, delta_time)`** (Abstract)
        -   **Signature:** `step(self, delta_time: float)`
        -   **Parameters:** `delta_time`: Time elapsed since the last step.
        -   **Description:** Executes one step of the command's logic. Should return `True` if the command finished during this step, `False` otherwise. Must be implemented by subclasses.
    -   **`is_finished(self)`** (Abstract)
        -   **Signature:** `is_finished(self)`
        -   **Description:** Returns `True` if the command has completed its execution, `False` otherwise. Must be implemented by subclasses.

---

### `Avancer(AsyncCommande)`

-   **Description:** Command to move the robot forward a specific distance based on encoder readings (or simulated distance).
-   **Attributes (in addition to base):**
    -   `distance_cm` (float): Target distance to travel in centimeters.
    -   `vitesse` (float): Target speed for both motors (degrees per second).
    -   `wheel_radius` (float): Radius of the wheels (cm), fixed at 2.5 cm.
    -   `started` (bool): Flag indicating if `start()` has been called.
    -   `finished` (bool): Flag indicating if the target distance has been reached.
    -   `logger` (`logging.Logger`): Logger instance for this command.
-   **Methods:**
    -   **`__init__(self, distance_cm, vitesse, adapter)`**
        -   **Signature:** `__init__(self, distance_cm: float, vitesse: float, adapter)`
        -   **Parameters:** `distance_cm`, `vitesse`, `adapter`.
        -   **Description:** Initializes the command with target distance, speed, and the adapter.
    -   **`start(self)`**
        -   **Description:** Sets both left and right motor speeds to `self.vitesse` using the adapter. Sets `self.started` to `True`. Prints debug messages.
        -   **Calls:** `self.adapter.set_motor_speed()` (twice), `print()`.
    -   **`step(self, delta_time)`**
        -   **Description:** If not started, calls `start()`. Gets the distance traveled from the adapter (`calculer_distance_parcourue`). If the distance meets or exceeds `distance_cm`, stops the motors (sets speeds to 0), sets `self.finished` to `True`, logs completion, resets the distance counter on the adapter (`resetDistance`), and returns `True`. Otherwise, returns `False`.
        -   **Calls:** `self.start()`, `self.adapter.calculer_distance_parcourue()`, `self.adapter.set_motor_speed()` (twice, on finish), `self.logger.info()`, `self.adapter.resetDistance()`.
    -   **`is_finished(self)`**
        -   **Description:** Returns the value of `self.finished`.

---

### `Tourner(AsyncCommande)`

-   **Description:** Command to turn the robot by a specific angle (in radians) using differential wheel speeds.
-   **Attributes (in addition to base):**
    -   `angle_rad` (float): Target angle to turn (radians).
    -   `base_speed` (float): Base speed for the faster wheel during the turn (degrees per second).
    -   `started` (bool): Flag indicating if `start()` has been called.
    -   `finished` (bool): Flag indicating if the target angle has been reached.
    -   `logger` (`logging.Logger`): Logger instance.
    -   `speed_ratio` (float): Ratio applied to `base_speed` to determine the slower wheel's speed (fixed at 0.5).
-   **Methods:**
    -   **`__init__(self, angle_rad, vitesse_deg_s, adapter)`**
        -   **Signature:** `__init__(self, angle_rad: float, vitesse_deg_s: float, adapter)`
        -   **Parameters:** `angle_rad`, `vitesse_deg_s` (base speed), `adapter`.
        -   **Description:** Initializes the command with target angle, base speed, and the adapter.
    -   **`start(self)`**
        -   **Description:** Calls the adapter's `decide_turn_direction` method to set initial motor speeds based on the angle and base speed. Sets `self.started` to `True`. Logs the start of the turn. Prints a debug message.
        -   **Calls:** `self.adapter.decide_turn_direction()`, `self.logger.info()`, `print()`.
    -   **`step(self, delta_time)`**
        -   **Description:** Gets the current angle turned from the adapter (`calcule_angle`). Calculates the error relative to `angle_rad`. If the absolute error is within tolerance (`0.5` degrees), stops the motors, sets `self.finished` to `True`, logs completion, and returns `True`. Otherwise, applies a proportional correction (`Kp = 0.8`) to the slower wheel's speed based on the error, updates the slow wheel speed via `adapter.slow_speed()`, and returns `False`.
        -   **Calls:** `self.adapter.calcule_angle()`, `math.radians()`, `math.degrees()`, `abs()`, `self.adapter.set_motor_speed()` (twice, on finish), `self.logger.info()`, `max()`, `min()`, `self.adapter.slow_speed()`.
    -   **`is_finished(self)`**
        -   **Description:** Returns the value of `self.finished`.
    -   **`calculer_angle_par_encodages(...)`**
        -   **Signature:** `calculer_angle_par_encodages(self, pos_init_l, pos_init_r, pos_l, pos_r, rayon, entraxe)`
        -   **Description:** A static-like method (though defined as an instance method) providing a simplified formula to calculate the turned angle based on initial and current encoder positions, wheel radius (`rayon`), and wheelbase (`entraxe`). **Note: This method does not seem to be used by the `Tourner` command itself in the provided code.**
        -   **Calls:** `math.pi`.

---

### `Arreter(AsyncCommande)`

-   **Description:** Command to immediately stop the robot's motors.
-   **Attributes (in addition to base):**
    -   `finished` (bool): Set to `True` immediately upon starting.
    -   `started` (bool): Flag indicating if `start()` has been called.
    -   `logger` (`logging.Logger`): Logger instance.
-   **Methods:**
    -   **`__init__(self, adapter)`**
        -   **Signature:** `__init__(self, adapter)`
        -   **Parameters:** `adapter`.
        -   **Description:** Initializes the command with the adapter.
    -   **`start(self)`**
        -   **Description:** Sets both motor speeds to 0 using the adapter. Sets `self.started` and `self.finished` to `True`. Logs execution.
        -   **Calls:** `self.adapter.set_motor_speed()` (twice), `self.logger.info()`.
    -   **`step(self, delta_time)`**
        -   **Description:** If not started, calls `start()`. Returns `self.finished` (which is always `True` after `start`).
        -   **Calls:** `self.start()`.
    -   **`is_finished(self)`**
        -   **Description:** Returns `self.finished` (always `True` after the first step).

---

### `PolygonStrategy(AsyncCommande)`

-   **Description:** A composite strategy that makes the robot trace a regular polygon (specifically, a square in the current implementation, as `turning_angle` is fixed at 90 degrees).
-   **Attributes (in addition to base):**
    -   `logger` (`logging.Logger`): Logger instance.
    -   `commands` (List[AsyncCommande]): A list containing a sequence of `Avancer` and `Tourner` commands to trace the polygon sides and turns, followed by an `Arreter` command.
    -   `current_index` (int): Index of the command currently being executed in the `commands` list.
    -   `finished` (bool): Flag indicating if all commands in the sequence have finished.
-   **Methods:**
    -   **`__init__(self, n, adapter, side_length_cm, vitesse_avance, vitesse_rotation)`**
        -   **Signature:** `__init__(self, n: int, adapter, side_length_cm: float, vitesse_avance: float, vitesse_rotation: float)`
        -   **Parameters:**
            -   `n`: Number of sides for the polygon (must be >= 3).
            -   `adapter`: The robot control adapter.
            -   `side_length_cm`: Length of each side.
            -   `vitesse_avance`: Speed for the `Avancer` commands.
            -   `vitesse_rotation`: Base speed for the `Tourner` commands.
        -   **Description:** Validates `n`. Creates a list (`self.commands`) containing `n` pairs of `Avancer` and `Tourner` commands. **Note: The `turning_angle` is hardcoded to `math.radians(90)`, meaning it always creates a square path regardless of `n` > 4.** Appends a final `Arreter` command. Initializes `current_index` to 0 and `finished` to `False`.
        -   **Calls:** `ValueError` (if n < 3), `logging.getLogger()`, `math.radians()`, `Avancer()`, `Tourner()`, `Arreter()`, `list.append()`, `self.logger.info()`.
    -   **`start(self)`**
        -   **Description:** If the `commands` list is not empty, calls the `start()` method of the first command in the list.
        -   **Calls:** `self.commands[0].start()` (conditionally).
    -   **`step(self, delta_time)`**
        -   **Description:** Checks if the current command (`self.commands[self.current_index]`) has finished using `is_finished()`. If not, calls its `step()` method. If the current command has finished, increments `current_index`. If there are more commands, calls `start()` on the new current command. If all commands are finished (`current_index` reaches the end), sets `self.finished` to `True`. Returns `self.finished`.
        -   **Calls:** `len()`, `cmd.is_finished()`, `cmd.step()`, `self.commands[...].start()` (conditionally).
    -   **`is_finished(self)`**
        -   **Description:** Returns `self.finished`.

---

### `FollowBeaconByImageStrategy(AsyncCommande)`

-   **Description:** A strategy to make the robot navigate towards a beacon (presumably blue) detected in images captured by a camera (simulated via `vpython_view`). It tries to center the beacon in the image and move towards it until it's within a certain radius.
-   **Attributes (in addition to base):**
    -   `vitesse_rotation` (float): Speed for corrective turns.
    -   `vitesse_avance` (float): Speed for moving forward when aligned.
    -   `tolerance_angle` (float): Angular tolerance (degrees) for considering the beacon centered.
    -   `tolerance_radius` (float): Radius threshold (pixels?) indicating the robot is close enough to the beacon.
    -   `step_distance` (float): Distance (cm) to move forward in each `Avancer` step when aligned.
    -   `vpython_view` (`VpythonView`): Reference to the VPython view object, used to get the latest image path and analyze the image.
    -   `logger` (`logging.Logger`): Logger instance.
    -   `started` (bool): Flag indicating if `start()` has been called.
    -   `finished` (bool): Flag indicating if the beacon has been reached.
-   **Methods:**
    -   **`__init__(self, vitesse_rotation, vitesse_avance, tolerance_angle=2, tolerance_radius=20, step_distance=5, adapter=None, vpython_view=None)`**
        -   **Signature:** `__init__(self, vitesse_rotation: float, vitesse_avance: float, tolerance_angle: float = 2, tolerance_radius: float = 20, step_distance: float = 5, adapter=None, vpython_view=None)`
        -   **Parameters:** Speeds, tolerances, step distance, adapter, and the `vpython_view` instance.
        -   **Description:** Initializes the strategy with the provided parameters.
    -   **`start(self)`**
        -   **Description:** Sets `self.started` to `True` and logs the strategy start.
        -   **Calls:** `self.logger.info()`.
    -   **`step(self, delta_time)`**
        -   **Description:** Complex step logic:
            1.  If not started, calls `start()`.
            2.  Gets the latest image path from `vpython_view.get_latest_image()`.
            3.  If no image, logs an error and returns `False`.
            4.  Calls `vpython_view.analyze_image()` with the image path.
            5.  If no detections (beacon not found):
                -   Logs message.
                -   Creates and executes one step of a small `Tourner` command (10 degrees) to search.
                -   Returns `False`.
            6.  If detections found:
                -   Takes the first detection (`detections[0]`).
                -   Checks if `detection["radius"]` is >= `tolerance_radius`.
                    -   If yes (close enough): Stops motors, sets `finished` to `True`, logs message, returns `True`.
                -   If no (not close enough):
                    -   Calculates horizontal error (`error_x`) of the beacon center relative to the image center (assumes image width 400px).
                    -   Calculates angular error (`angle_error`) based on `error_x` and a fixed field of view (60 degrees).
                    -   Applies a dead zone: if `abs(angle_error_deg)` < `tolerance_angle`, set `angle_error` to 0.
                    -   If `angle_error` is non-zero: Creates and executes one step of a `Tourner` command with `angle_error`.
                    -   If `angle_error` is zero (aligned): Creates and executes one step of an `Avancer` command with `step_distance`.
                    -   Returns `self.finished`.
        -   **Calls:** `self.start()`, `self.vpython_view.get_latest_image()`, `self.logger.error()`, `self.vpython_view.analyze_image()`, `self.logger.info()`, `math.radians()`, `Tourner()`, `cmd.start()`, `cmd.step()`, `self.adapter.set_motor_speed()`, `math.degrees()`, `abs()`, `Avancer()`.
    -   **`is_finished(self)`**
        -   **Description:** Returns `self.finished`.

---

### `CommandeComposite(AsyncCommande)`

-   **Description:** A strategy that executes a sequence of other `AsyncCommande` instances one after another.
-   **Attributes (in addition to base):**
    -   `commands` (List[AsyncCommande]): The list of commands to execute sequentially.
    -   `current_index` (int): Index of the command currently being executed.
    -   `finished` (bool): Flag indicating if all commands in the sequence are finished.
-   **Methods:**
    -   **`__init__(self, adapter)`**
        -   **Signature:** `__init__(self, adapter)`
        -   **Parameters:** `adapter`.
        -   **Description:** Initializes the composite command with an empty list of commands and the adapter.
    -   **`ajouter_commande(self, commande)`**
        -   **Signature:** `ajouter_commande(self, commande: AsyncCommande)`
        -   **Parameters:** `commande`: An instance of `AsyncCommande` (or subclass) to add to the sequence.
        -   **Returns:** `None`
        -   **Description:** Appends the given command to the `self.commands` list.
    -   **`start(self)`**
        -   **Description:** If the `commands` list is not empty, calls the `start()` method of the first command.
        -   **Calls:** `self.commands[0].start()` (conditionally).
    -   **`step(self, delta_time)`**
        -   **Description:** Similar logic to `PolygonStrategy.step`. Executes the `step()` method of the current command. If it finishes, increments `current_index` and starts the next command if one exists. Sets `self.finished` to `True` when all commands are done. Returns `self.finished`.
        -   **Calls:** `len()`, `cmd.is_finished()`, `cmd.step()`, `self.commands[...].start()` (conditionally).
    -   **`is_finished(self)`**
        -   **Description:** Returns `self.finished`.

**Dependencies:**

-   `time` (standard library, but seemingly unused directly in this file)
-   `math` (standard library)
-   `logging` (standard library)
-   `utils.geometry.normalize_angle` (potentially used implicitly by adapter or other parts, not directly here)
-   Requires an `adapter` object conforming to the expected interface (e.g., `set_motor_speed`, `calculer_distance_parcourue`, `resetDistance`, `calcule_angle`, `decide_turn_direction`, `slow_speed`). This is likely provided by `controller.adapter.RobotAdapter`.
-   `FollowBeaconByImageStrategy` depends on a `vpython_view` object with specific methods (`get_latest_image`, `analyze_image`).

---

## `src/controller/map_controller.py`

**Purpose:** This module defines the `MapController` class, which acts as the intermediary between the `MapModel` (data) and the `MapView` (presentation) for the map-related functionalities in the GUI. It handles user interactions on the map canvas (clicks, drags) based on the current mode (setting start/end points, drawing obstacles) and updates the model and view accordingly.

**Classes:**

### `MapController`

-   **Description:** Manages user interactions with the map view (Tkinter canvas) and updates the map model. It listens to events from the model to keep the view synchronized.
-   **Attributes:**
    -   `map_model` (`MapModel`): Reference to the map data model.
    -   `map_view` (`MapView`): Reference to the map view (Tkinter canvas wrapper). Can be `None` (e.g., in VPython mode).
    -   `window`: Reference to the main application window (likely `gui_main.MainApplication`).
    -   `mode` (str): Current interaction mode (`'set_start'`, `'set_end'`, `'set_obstacles'`, potentially others or `None`). Determines how clicks/drags are interpreted.
-   **Methods:**
    -   **`__init__(self, map_model: MapModel, map_view: MapView, window)`**
        -   **Signature:** `__init__(self, map_model: MapModel, map_view: MapView, window)`
        -   **Parameters:** `map_model`, `map_view`, `window`.
        -   **Returns:** `None`
        -   **Description:** Initializes the controller, storing references to the model, view, and window. If `map_view` is provided, it registers itself as an event listener to the `map_model` and binds various mouse events (`<Button-1>`, `<B1-Motion>`, `<Double-Button-1>`, `<Button-3>`, `<ButtonRelease-1>`) on the `map_view.canvas` to its handler methods (`handle_click`, `handle_drag`, etc.).
        -   **Relationship:** Constructor, sets up connections between model, view, and controller.
        -   **Called By:** `gui_main.MainApplication.__init__()`, `vpython_main.MainApplication.__init__()`.
        -   **Calls:** `self.map_model.add_event_listener()`, `self.map_view.canvas.bind()` (multiple times).
    -   **`handle_map_event(self, event_type, **kwargs)`**
        -   **Signature:** `handle_map_event(self, event_type: str, **kwargs)`
        -   **Parameters:**
            -   `event_type`: The type of event from the model (e.g., `"start_position_changed"`).
            -   `**kwargs`: Additional data associated with the event (e.g., `position`, `points`, `obstacle_id`).
        -   **Returns:** `None`
        -   **Description:** Callback method triggered by the `MapModel` when its state changes. Based on the `event_type`, it calls the appropriate drawing or deletion methods on the `map_view` to keep the visual representation synchronized with the model. For "start_position_changed", it also updates the robot's position in the `robot_view`.
        -   **Relationship:** Model-to-View synchronization logic.
        -   **Called By:** `MapModel` (via event listener mechanism).
        -   **Calls:** `self.map_view.robot_view.x`, `self.map_view.robot_view.y` (assignment), `self.map_view.draw_start()`, `self.map_view.draw_end()`, `self.map_view.draw_obstacle()`, `self.map_view.delete_item()`, `self.map_view.clear_all()`.
    -   **`set_start_mode(self)`**
        -   **Signature:** `set_start_mode(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Sets the controller's `mode` to `'set_start'`. If `map_view` exists, updates its message label to guide the user.
        -   **Relationship:** Mode setting triggered by UI elements (e.g., buttons in `ControlPanel`).
        -   **Called By:** `view.control_panel.ControlPanel.__init__()` (via lambda).
        -   **Calls:** `self.map_view.update_message_label()`.
    -   **`set_end_mode(self)`**
        -   **Signature:** `set_end_mode(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Sets the controller's `mode` to `'set_end'`. If `map_view` exists, updates its message label.
        -   **Relationship:** Mode setting triggered by UI elements.
        -   **Called By:** `view.control_panel.ControlPanel.__init__()` (via lambda).
        -   **Calls:** `self.map_view.update_message_label()`.
    -   **`set_obstacles_mode(self)`**
        -   **Signature:** `set_obstacles_mode(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Sets the controller's `mode` to `'set_obstacles'`. Clears any temporary points (`current_points`) and lines (`current_lines`) in the `map_model`. If `map_view` exists, updates its message label.
        -   **Relationship:** Mode setting triggered by UI elements.
        -   **Called By:** `view.control_panel.ControlPanel.__init__()` (via lambda).
        -   **Calls:** `self.map_model.current_points` (assignment), `self.map_model.current_lines` (assignment), `self.map_view.update_message_label()`.
    -   **`handle_click(self, event)`**
        -   **Signature:** `handle_click(self, event)`
        -   **Parameters:** `event`: The Tkinter mouse event object.
        -   **Returns:** `None`
        -   **Description:** Handles left mouse button clicks (`<Button-1>`). The action depends on the current `mode`:
            -   `'set_start'`: Calls `map_model.set_start_position()` with click coordinates.
            -   `'set_end'`: Calls `map_model.set_end_position()` with click coordinates.
            -   `'set_obstacles'`: 
                -   If not currently drawing (`current_shape` is None): Checks if the click is inside an existing obstacle (`point_in_polygon`). If yes, initiates dragging (`dragging_obstacle`, `drag_start`). If no, starts drawing a new obstacle line (`current_points`, `current_shape`).
                -   If already drawing: Appends the point to `current_points` and draws a connecting line segment, storing its ID in `current_lines`.
        -   **Relationship:** Core user interaction handler for placing points and starting obstacle drawing/dragging.
        -   **Called By:** Tkinter event loop (bound to `<Button-1>`).
        -   **Calls:** `self.map_model.set_start_position()`, `self.map_model.set_end_position()`, `utils.geometry.point_in_polygon()`, `self.map_view.create_line()`, `list.append()`.
    -   **`add_obstacle(self)`**
        -   **Signature:** `add_obstacle(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Intended to be called when a shape is finalized. If `current_points` exist, it creates a permanent polygon visualization (`map_view.create_polygon`), generates a unique `obstacle_id`, adds the obstacle data to the `map_model`, clears the temporary drawing state (`current_points`, `current_shape`), and updates the message label.
        -   **Relationship:** Finalizes an obstacle addition after drawing.
        -   **Called By:** `finalize_shape()`.
        -   **Calls:** `self.map_view.create_polygon()`, `len()`, `self.map_model.add_obstacle()`, `self.map_model.current_points` (assignment), `self.map_model.current_shape` (assignment), `self.map_view.update_message_label()`.
    -   **`handle_drag(self, event)`**
        -   **Signature:** `handle_drag(self, event)`
        -   **Parameters:** `event`: The Tkinter mouse event object.
        -   **Returns:** `None`
        -   **Description:** Handles mouse movement while the left button is pressed (`<B1-Motion>`). If in `'set_obstacles'` mode and currently drawing (`current_shape` exists), it appends the current point to `current_points` and draws a new line segment from the previous point to the current one, adding the line ID to `current_lines`. **Note: The logic for dragging existing obstacles seems incomplete or missing here; it only handles drawing new shapes.**
        -   **Relationship:** User interaction handler for continuous drawing.
        -   **Called By:** Tkinter event loop (bound to `<B1-Motion>`).
        -   **Calls:** `self.map_model.current_points.append()`, `self.map_view.create_line()`, `self.map_model.current_lines.append()`.
    -   **`is_shape_closed(self)`**
        -   **Signature:** `is_shape_closed(self)`
        -   **Parameters:** `self`
        -   **Returns:** `bool`: `True` if the currently drawn shape's start and end points are close enough, `False` otherwise.
        -   **Description:** Checks if the list of `current_points` has at least 3 points and if the distance between the first and last point is within a tolerance (15 pixels).
        -   **Relationship:** Helper function for `finalize_shape`.
        -   **Called By:** `finalize_shape()`.
        -   **Calls:** `len()`, `abs()`.
    -   **`finalize_shape(self, event=None)`**
        -   **Signature:** `finalize_shape(self, event=None)`
        -   **Parameters:** `event`: The Tkinter mouse event object (optional, from `<Double-Button-1>`).
        -   **Returns:** `None`
        -   **Description:** Handles double left-clicks (`<Double-Button-1>`) in `'set_obstacles'` mode when a shape is being drawn (`current_shape` exists). It checks if the shape is closed using `is_shape_closed()`. If closed, it deletes the temporary drawing lines (`current_lines`) from the view, clears `current_lines` in the model, and calls `add_obstacle()` to make the shape permanent. If not closed, it updates the message label instructing the user.
        -   **Relationship:** Completes the obstacle drawing process.
        -   **Called By:** Tkinter event loop (bound to `<Double-Button-1>`).
        -   **Calls:** `self.is_shape_closed()`, `self.map_view.delete_item()` (in loop), `self.map_model.current_lines` (assignment), `self.add_obstacle()`, `self.map_view.update_message_label()`.
    -   **`delete_obstacle(self, event)`**
        -   **Signature:** `delete_obstacle(self, event)`
        -   **Parameters:** `event`: The Tkinter mouse event object.
        -   **Returns:** `None`
        -   **Description:** Handles right mouse button clicks (`<Button-3>`). It iterates through the obstacles in `map_model.obstacles`. If the click location (`x`, `y`) is inside an obstacle's polygon (`point_in_polygon`), it calls `map_view.delete_obstacle_visual` to remove the drawing, `map_model.remove_obstacle` to remove the data, updates the message label, and breaks the loop.
        -   **Relationship:** User interaction handler for removing obstacles.
        -   **Called By:** Tkinter event loop (bound to `<Button-3>`).
        -   **Calls:** `utils.geometry.point_in_polygon()`, `self.map_view.delete_obstacle_visual()`, `self.map_model.remove_obstacle()`, `self.map_view.update_message_label()`.
    -   **`stop_drag(self, event)`**
        -   **Signature:** `stop_drag(self, event)`
        -   **Parameters:** `event`: The Tkinter mouse event object.
        -   **Returns:** `None`
        -   **Description:** Handles the release of the left mouse button (`<ButtonRelease-1>`). It resets the dragging state in the `map_model` (`dragging_obstacle`, `drag_start`) to `None`.
        -   **Relationship:** Completes a drag operation (intended for moving obstacles, though the move logic isn't fully implemented in `handle_drag`).
        -   **Called By:** Tkinter event loop (bound to `<ButtonRelease-1>`).
        -   **Calls:** None directly, modifies `map_model` attributes.
    -   **`reset(self)`**
        -   **Signature:** `reset(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Calls the `delete_all()` method on the `map_view` to clear the canvas visually. **Note: This seems incomplete as it doesn't reset the `map_model` data.** A more complete reset would likely involve calling a reset method on the `map_model` as well, which would then trigger `handle_map_event` to clear the view properly via the event system.
        -   **Relationship:** Intended to reset the map.
        -   **Called By:** `view.control_panel.ControlPanel.reset_map()`.
        -   **Calls:** `self.map_view.delete_all()`.

**Dependencies:**

-   `model.map_model.MapModel`
-   `view.map_view.MapView` (optional)
-   `utils.geometry.point_in_polygon`
-   `model.robot.RobotModel` (imported but seemingly unused directly)
-   Tkinter event object structure (implicitly)

---

## `src/controller/adapter.py`

**Purpose:** This module defines an adapter pattern to abstract the way the robot's hardware (or simulation) is controlled. It provides an abstract base class `RobotAdapter` and a concrete implementation `RealRobotAdapter` (presumably intended for a physical robot, although it might interact with a simulated robot model that mimics a real one, like the `RobotModel` class). This allows strategies (`StrategyAsync`) and controllers to interact with the robot through a consistent interface, regardless of whether it's real or simulated.

**Classes:**

### `RobotAdapter(ABC)`

-   **Inherits from:** `abc.ABC` (Abstract Base Class)
-   **Description:** Defines the abstract interface that all robot adapters must implement. This ensures that any component using an adapter can rely on a specific set of methods being available.
-   **Methods (Abstract):**
    -   **`set_motor_speed(self, motor: str, speed: float)`**
        -   Abstract method. Implementations should set the speed of the specified motor (`'left'` or `'right'`).
    -   **`get_motor_positions(self) -> dict`**
        -   Abstract method. Implementations should return the current angular position (e.g., in degrees) of the motors as a dictionary `{'left': pos_l, 'right': pos_r}`.
    -   **`calculer_distance_parcourue(self)`**
        -   Abstract method. Implementations should calculate and return the distance traveled since the last reset, likely based on encoder readings.
    -   **`resetDistance(self)`**
        -   Abstract method. Implementations should reset the internal distance counter used by `calculer_distance_parcourue`.
    -   **`decide_turn_direction(self, adapter)`**
        -   Abstract method. **Note:** The parameter name `adapter` seems incorrect for this context; it likely should be related to the target angle and speed. Implementations should initiate a turn based on the desired angle and speed, setting appropriate differential speeds.
    -   **`calcule_angle(self)`**
        -   Abstract method. Implementations should calculate and return the total angle turned since the start of the last turn command, likely based on encoder readings.

---

### `RealRobotAdapter(RobotAdapter)`

-   **Inherits from:** `RobotAdapter`
-   **Description:** A concrete implementation of the `RobotAdapter` interface, designed to interact with a `real_robot` object (which could be an instance of `model.robot.RobotModel` or a driver for actual hardware).
-   **Attributes:**
    -   `robot`: The underlying robot object being controlled.
    -   `motor_positions` (dict): Seems intended to store motor positions, but isn't actively used in the provided methods (superseded by `last_motor_positions`).
    -   `last_motor_positions` (tuple/list): Stores the motor encoder readings from the previous call to `calculer_distance_parcourue` or `__init__`.
    -   `fast_wheel` (str or None): Stores the identifier (`'MOTOR_LEFT'` or `'MOTOR_RIGHT'`) of the faster wheel during a turn.
    -   `slow_wheel` (str or None): Stores the identifier of the slower wheel during a turn.
    -   `distance` (float): Accumulates the distance calculated by `calculer_distance_parcourue`.
-   **Methods:**
    -   **`__init__(self, real_robot)`**
        -   **Signature:** `__init__(self, real_robot)`
        -   **Parameters:** `real_robot`: The robot object to control.
        -   **Returns:** `None`
        -   **Description:** Stores the `real_robot` reference. Initializes `motor_positions` (unused?), `fast_wheel`, `slow_wheel`, and `distance`. Gets initial motor positions using `robot.get_motor_position()` and stores them in `last_motor_positions`.
        -   **Calls:** `self.robot.get_motor_position()`.
    -   **`set_motor_speed(self, motor: str, speed: float)`**
        -   **Signature:** `set_motor_speed(self, motor: str, speed: float)`
        -   **Description:** Implements the abstract method. Maps the logical motor name (`'left'`, `'right'`) to the `real_robot`'s port names (`'MOTOR_LEFT'`, `'MOTOR_RIGHT'`) and calls `self.robot.set_motor_dps()` to set the speed.
        -   **Calls:** `self.robot.set_motor_dps()`.
    -   **`get_motor_positions(self) -> dict`**
        -   **Signature:** `get_motor_positions(self) -> dict`
        -   **Description:** Implements the abstract method. Calls `self.robot.get_motor_position()` to get the raw encoder values (tuple) and returns them formatted as a dictionary `{'left': left_pos, 'right': right_pos}`.
        -   **Calls:** `self.robot.get_motor_position()`.
    -   **`calculer_distance_parcourue(self) -> float`**
        -   **Signature:** `calculer_distance_parcourue(self) -> float`
        -   **Description:** Implements the abstract method. Gets current motor positions. Calculates the change in angle (`delta_left`, `delta_right`) since the `last_motor_positions`. Converts these angular changes (degrees) to linear distances using the wheel diameter (`self.robot.WHEEL_DIAMETER`). Averages the left and right distances and adds this average to the accumulated `self.distance`. Updates `last_motor_positions`. Prints debug messages. Returns the total accumulated `self.distance`. **Note:** Assumes `self.robot` has a `WHEEL_DIAMETER` attribute.
        -   **Calls:** `self.robot.get_motor_position()`, `math.radians()`, `print()`.
    -   **`resetDistance(self)`**
        -   **Signature:** `resetDistance(self)`
        -   **Description:** Implements the abstract method. Prints the final distance before reset. Resets the accumulated `self.distance` to 0.
        -   **Calls:** `print()`.
    -   **`decide_turn_direction(self, angle_rad, base_speed)`**
        -   **Signature:** `decide_turn_direction(self, angle_rad: float, base_speed: float)`
        -   **Description:** Implements the abstract method (correcting the signature based on usage in `StrategyAsync`). Gets initial motor positions for angle calculation later. Determines which wheel should be faster/slower based on the sign of `angle_rad` (positive for right turn, negative for left). Stores the corresponding motor ports (`'MOTOR_LEFT'`, `'MOTOR_RIGHT'`) in `self.fast_wheel` and `self.slow_wheel`. Sets the fast wheel to `base_speed` and the slow wheel to `base_speed * speed_ratio` (where `speed_ratio` is hardcoded to 0.5).
        -   **Calls:** `self.get_motor_positions()`, `self.robot.set_motor_dps()` (twice).
    -   **`calcule_angle(self) -> float`**
        -   **Signature:** `calcule_angle(self) -> float`
        -   **Description:** Implements the abstract method. Gets current motor positions. Calculates the change in encoder readings (`delta_left`, `delta_right`) relative to the initial positions stored during `decide_turn_direction`. Calculates the angle turned using the formula: `angle = (delta_left - delta_right) * wheel_circumference / (360 * self.robot.WHEEL_BASE_WIDTH)`. **Note:** Assumes `self.robot` has `WHEEL_DIAMETER` and `WHEEL_BASE_WIDTH` attributes.
        -   **Calls:** `self.get_motor_positions()`, `math.pi`.
    -   **`slow_speed(self, new_slow_speed: float)`**
        -   **Signature:** `slow_speed(self, new_slow_speed: float)`
        -   **Description:** Helper method (not part of the abstract interface but used by `Tourner` strategy). Sets the speed of the wheel designated as `self.slow_wheel` during the last call to `decide_turn_direction`.
        -   **Calls:** `self.set_motor_speed()`.

**Dependencies:**

-   `abc` (standard library)
-   `math` (standard library)
-   Requires a `real_robot` object with methods like `get_motor_position()`, `set_motor_dps()` and attributes like `WHEEL_DIAMETER`, `WHEEL_BASE_WIDTH`.

--- 

## `src/model/map_model.py`

**Purpose:** This module defines the `MapModel` class which serves as the model component in the MVC architecture for the map/environment in which the robot operates. It stores and manages data about obstacles, start/end positions, and provides functionality for event handling, collision detection, and boundary checking.

**Classes:**

### `MapModel`

-   **Description:** Represents the map/environment data, including obstacles, start/end positions, and the current drawing state.
-   **Attributes:**
    -   `obstacles` (dict): Dictionary of obstacles with format `{obstacle_id: (points, polygon_id, line_ids)}` where:
        -   `obstacle_id` (str): Unique identifier for the obstacle.
        -   `points` (list): List of (x, y) tuples representing the vertices of the obstacle polygon.
        -   `polygon_id`: Tkinter canvas ID for the polygon shape (view reference).
        -   `line_ids`: Tkinter canvas IDs for any lines associated with the obstacle (view reference).
    -   `start_position` (tuple): (x, y) coordinates of the robot's starting position. Initialized to (0, 0).
    -   `end_position` (tuple or None): (x, y) coordinates of the end/goal position if set, otherwise `None`.
    -   `current_shape` (ID or None): Reference to the temporary shape currently being drawn (used during obstacle creation).
    -   `current_points` (list): List of (x, y) points collected during the current drawing operation.
    -   `current_lines` (list): List of line IDs created during the current drawing operation (view references).
    -   `dragging_obstacle` (str or None): ID of the obstacle currently being dragged, or `None` if not dragging.
    -   `drag_start` (tuple or None): (x, y) coordinates where a drag operation started, or `None` if not dragging.
    -   `event_listeners` (list): List of callback functions that will be notified when the model changes.
-   **Methods:**
    -   **`__init__(self)`**
        -   **Signature:** `__init__(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Initializes the map model with default values. Sets `start_position` to (0, 0), `end_position` to `None`, and initializes empty collections for obstacles, drawing state, and event listeners.
    -   **`add_event_listener(self, listener)`**
        -   **Signature:** `add_event_listener(self, listener)`
        -   **Parameters:** `listener`: A callback function that accepts `event_type` and `**kwargs` parameters.
        -   **Returns:** `None`
        -   **Description:** Adds the provided `listener` function to the list of event listeners. These listeners will be notified when the map state changes.
        -   **Called By:** `controller.map_controller.MapController.__init__()`
    -   **`notify_event_listeners(self, event_type, **kwargs)`**
        -   **Signature:** `notify_event_listeners(self, event_type: str, **kwargs)`
        -   **Parameters:**
            -   `event_type`: String identifying the type of event that occurred.
            -   `**kwargs`: Additional data relevant to the event.
        -   **Returns:** `None`
        -   **Description:** Calls each registered listener function, passing `event_type` and `kwargs` to it.
        -   **Called By:** `self.reset()`, `self.set_start_position()`, `self.set_end_position()`, `self.add_obstacle()`, `self.remove_obstacle()`, `self.move_obstacle()`
    -   **`reset(self)`**
        -   **Signature:** `reset(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Clears all obstacles and resets start/end positions to `None`. Notifies listeners of the reset via the "map_reset" event.
        -   **Called By:** This method is not directly called by any other part of the provided code. It could be triggered by a reset button in the UI or other control flow not shown.
        -   **Calls:** `dict.clear()`, `self.notify_event_listeners()`
    -   **`set_start_position(self, position)`**
        -   **Signature:** `set_start_position(self, position: tuple)`
        -   **Parameters:** `position`: A tuple (x, y) representing the new start position.
        -   **Returns:** `None`
        -   **Description:** Updates the start position and notifies listeners of the change via the "start_position_changed" event.
        -   **Called By:** `controller.map_controller.MapController.handle_click()`
        -   **Calls:** `self.notify_event_listeners()`
    -   **`set_end_position(self, position)`**
        -   **Signature:** `set_end_position(self, position: tuple)`
        -   **Parameters:** `position`: A tuple (x, y) representing the new end position.
        -   **Returns:** `None`
        -   **Description:** Updates the end position and notifies listeners of the change via the "end_position_changed" event.
        -   **Called By:** `controller.map_controller.MapController.handle_click()`
        -   **Calls:** `self.notify_event_listeners()`
    -   **`add_obstacle(self, obstacle_id, points, polygon_id, line_ids)`**
        -   **Signature:** `add_obstacle(self, obstacle_id: str, points: list, polygon_id, line_ids: list)`
        -   **Parameters:**
            -   `obstacle_id`: Unique identifier for the obstacle.
            -   `points`: List of (x, y) tuples representing the obstacle's vertices.
            -   `polygon_id`: Tkinter canvas ID for the obstacle's polygon shape (view reference).
            -   `line_ids`: List of Tkinter canvas IDs for any lines associated with the obstacle (view reference).
        -   **Returns:** `None`
        -   **Description:** Adds a new obstacle to the `obstacles` dictionary and notifies listeners via the "obstacle_added" event.
        -   **Called By:** `controller.map_controller.MapController.add_obstacle()`
        -   **Calls:** `self.notify_event_listeners()`
    -   **`remove_obstacle(self, obstacle_id)`**
        -   **Signature:** `remove_obstacle(self, obstacle_id: str)`
        -   **Parameters:** `obstacle_id`: The ID of the obstacle to remove.
        -   **Returns:** `None`
        -   **Description:** Removes the specified obstacle from the `obstacles` dictionary and notifies listeners via the "obstacle_removed" event.
        -   **Called By:** `controller.map_controller.MapController.delete_obstacle()`
        -   **Calls:** `dict.__contains__()`, `dict.__delitem__()`, `self.notify_event_listeners()`
    -   **`move_obstacle(self, obstacle_id, new_points)`**
        -   **Signature:** `move_obstacle(self, obstacle_id: str, new_points: list)`
        -   **Parameters:**
            -   `obstacle_id`: The ID of the obstacle to move.
            -   `new_points`: Updated list of (x, y) tuples representing the obstacle's new vertices.
        -   **Returns:** `None`
        -   **Description:** Updates the points of the specified obstacle and notifies listeners via the "obstacle_moved" event. **Note: This method appears to be incomplete, as it replaces the entire obstacle tuple with just `new_points`, losing the `polygon_id` and `line_ids` information. This could cause issues if called directly.**
        -   **Called By:** This method is not directly called by any other part of the provided code, which suggests it might be unused or that the dragging implementation is incomplete.
        -   **Calls:** `dict.__contains__()`, `self.notify_event_listeners()`
    -   **`is_collision(self, x, y)`**
        -   **Signature:** `is_collision(self, x: float, y: float) -> bool`
        -   **Parameters:** `x`, `y`: Coordinates to check for collision.
        -   **Returns:** `bool`: `True` if the point collides with any obstacle, `False` otherwise.
        -   **Description:** Checks if the given point (x, y) is inside any obstacle polygon. **Note: The method's docstring mentions a "corrected version" but it's unclear what was corrected from an earlier version.**
        -   **Called By:** This method is not directly called by any other part of the provided code, but would likely be used by the `SimulationController` or `RobotModel` to check if the robot has collided with an obstacle.
        -   **Calls:** `utils.geometry.point_in_polygon()`
    -   **`is_out_of_bounds(self, x, y)`**
        -   **Signature:** `is_out_of_bounds(self, x: float, y: float) -> bool`
        -   **Parameters:** `x`, `y`: Coordinates to check for boundary violations.
        -   **Returns:** `bool`: `True` if the point is outside the map boundaries, `False` otherwise.
        -   **Description:** Checks if the given point (x, y) is outside the predefined map boundaries. Uses hardcoded values `MAP_WIDTH = 800` and `MAP_HEIGHT = 600` to define the map dimensions.
        -   **Called By:** This method is not directly called by any other part of the provided code, but would likely be used by the `SimulationController` or `RobotModel` to check if the robot has moved out of bounds.

**Dependencies:**

-   `utils.geometry.point_in_polygon`

--- 

## `src/model/robot.py`

**Purpose:** This module defines the `RobotModel` class which represents the robot's physical properties and state within the simulation. It implements the `RobotAdapter` interface, allowing it to be used with the strategy pattern for robot movement, and includes methods for updating position, controlling motors, calculating distances and angles.

**Classes:**

### `RobotModel(RobotAdapter)`

-   **Inherits from:** `controller.adapter.RobotAdapter`
-   **Description:** Represents the robot's physical state and provides methods for controlling it within the simulation. By implementing the `RobotAdapter` interface, it can be used with the strategy classes from `StrategyAsync.py`.
-   **Class Attributes (Constants):**
    -   `WHEEL_BASE_WIDTH` (float): The distance between the centers of the two wheels (20.0 cm).
    -   `WHEEL_DIAMETER` (float): The diameter of the wheels (5.0 cm).
    -   `WHEEL_RADIUS` (float): The radius of the wheels (WHEEL_DIAMETER / 2, or 2.5 cm).
-   **Instance Attributes:**
    -   `map_model` (`MapModel`): Reference to the map model for collision detection.
    -   `x`, `y` (float): The robot's current position coordinates.
    -   `direction_angle` (float): The robot's current orientation angle in radians.
    -   `motor_speeds` (dict): Dictionary containing the current speed of each motor in degrees per second (`{'left': speed_l, 'right': speed_r}`).
    -   `motor_positions` (dict): Dictionary containing the cumulative angular positions of each motor (`{'left': pos_l, 'right': pos_r}`).
    -   `last_motor_positions` (dict): Copy of `motor_positions` used for calculating distance traveled.
    -   `distance` (float): Accumulated distance traveled since the last reset.
    -   `fast_wheel` (str or None): The identifier of the faster wheel during a turn (`'left'` or `'right'`).
    -   `slow_wheel` (str or None): The identifier of the slower wheel during a turn (`'left'` or `'right'`).
-   **Methods:**
    -   **`__init__(self, map_model: MapModel)`**
        -   **Signature:** `__init__(self, map_model: MapModel)`
        -   **Parameters:** `map_model`: The map model for collision detection.
        -   **Returns:** `None`
        -   **Description:** Initializes the robot with the provided `map_model`. Sets the initial position to `map_model.start_position`, orientation to 0, motor speeds to 0, and initializes other attributes.
        -   **Calls:** `print()`, `map_model.start_position`, `dict.copy()`.
    -   **`update_position(self, new_x: float, new_y: float, new_angle: float)`**
        -   **Signature:** `update_position(self, new_x: float, new_y: float, new_angle: float)`
        -   **Parameters:**
            -   `new_x`: Proposed new x-coordinate.
            -   `new_y`: Proposed new y-coordinate.
            -   `new_angle`: Proposed new orientation angle (radians).
        -   **Returns:** `None`
        -   **Description:** Updates the robot's position and orientation if the new position doesn't collide with obstacles or boundaries. Uses `map_model.is_collision()` and `map_model.is_out_of_bounds()` for validation. Normalizes the angle using `normalize_angle()`.
        -   **Called By:** `controller.simulation_controller.SimulationController.update_physics()`.
        -   **Calls:** `self.map_model.is_collision()`, `self.map_model.is_out_of_bounds()`, `utils.geometry.normalize_angle()`.
    -   **`set_motor_speed(self, motor: str, dps: int)`**
        -   **Signature:** `set_motor_speed(self, motor: str, dps: int)`
        -   **Parameters:**
            -   `motor`: The motor to set (`'left'` or `'right'`).
            -   `dps`: The desired speed in degrees per second.
        -   **Returns:** `None`
        -   **Description:** Sets the speed of the specified motor if `motor` is a valid identifier (`'left'` or `'right'`).
        -   **Called By:** Various methods including `controller.robot_controller.RobotController` methods, `cli_main.HeadlessSimulation.run()`, `controller.adapter.RealRobotAdapter.slow_speed()`, etc.
        -   **Calls:** None directly, modifies `self.motor_speeds`.
    -   **`get_state(self) -> dict`**
        -   **Signature:** `get_state(self) -> dict`
        -   **Returns:** `dict`: Current state of the robot as a dictionary.
        -   **Description:** Returns a snapshot of the robot's current state as a dictionary with keys: `'x'`, `'y'`, `'angle'`, `'left_speed'`, `'right_speed'`.
        -   **Called By:** `controller.simulation_controller.SimulationController._notify_listeners()`.
        -   **Calls:** None, just creates and returns a dictionary.
    -   **`update_motors(self, delta_time)`**
        -   **Signature:** `update_motors(self, delta_time: float)`
        -   **Parameters:** `delta_time`: Time elapsed (in seconds) since the last update.
        -   **Returns:** `None`
        -   **Description:** Updates the angular positions (`motor_positions`) of both motors based on their speeds and `delta_time`.
        -   **Called By:** `controller.simulation_controller.SimulationController.update_physics()`.
        -   **Calls:** None directly, modifies `self.motor_positions`.
    -   **`get_motor_positions(self) -> dict`**
        -   **Signature:** `get_motor_positions(self) -> dict`
        -   **Returns:** `dict`: Current motor positions as a dictionary.
        -   **Description:** Implements the abstract method from `RobotAdapter`. Returns the current `motor_positions` dictionary. Unlike `RealRobotAdapter`, which queries the physical robot, this simply returns the internal state.
        -   **Called By:** `self.calculer_distance_parcourue()`, `self.decide_turn_direction()`, `self.calcule_angle()`.
        -   **Calls:** None, just returns `self.motor_positions`.
    -   **`get_distance(self) -> float`**
        -   **Signature:** `get_distance(self) -> float`
        -   **Returns:** `float`: Always returns 0.0.
        -   **Description:** A stub method that always returns 0.0. The docstring indicates it should be implemented "selon le modèle", suggesting this might be a placeholder for future functionality or compatibility.
        -   **Called By:** This method is not directly called by any other part of the provided code.
        -   **Calls:** None.
    -   **`calculer_distance_parcourue(self) -> float`**
        -   **Signature:** `calculer_distance_parcourue(self) -> float`
        -   **Returns:** `float`: The cumulative distance traveled.
        -   **Description:** Implements the abstract method from `RobotAdapter`. Calculates the distance traveled since the last call based on the change in wheel positions (`delta_left`, `delta_right`). Converts angular changes to linear distances using `WHEEL_RADIUS`. Updates `last_motor_positions` and accumulates distance in `self.distance`. Returns the total accumulated distance.
        -   **Called By:** `controller.StrategyAsync.Avancer.step()`.
        -   **Calls:** `self.get_motor_positions()`, `math.radians()`, `dict.copy()`.
    -   **`resetDistance(self)`**
        -   **Signature:** `resetDistance(self)`
        -   **Returns:** `None`
        -   **Description:** Implements the abstract method from `RobotAdapter`. Resets the accumulated distance counter (`self.distance`) to 0.
        -   **Called By:** `controller.StrategyAsync.Avancer.step()`.
        -   **Calls:** None directly, modifies `self.distance`.
    -   **`decide_turn_direction(self, angle_rad, base_speed)`**
        -   **Signature:** `decide_turn_direction(self, angle_rad: float, base_speed: float)`
        -   **Parameters:**
            -   `angle_rad`: The target turning angle in radians.
            -   `base_speed`: The base speed (for the faster wheel) in degrees per second.
        -   **Returns:** `None`
        -   **Description:** Implements the abstract method from `RobotAdapter`. Records initial motor positions for later angle calculation. Determines which wheel should turn faster based on the sign of `angle_rad` (positive for right turn, negative for left) and sets `self.fast_wheel` and `self.slow_wheel` accordingly. Sets the motors to appropriate speeds, with the slow wheel at `base_speed * speed_ratio` (where `speed_ratio` is hardcoded to 0.5).
        -   **Called By:** `controller.StrategyAsync.Tourner.start()`.
        -   **Calls:** `self.get_motor_positions()`, `self.set_motor_speed()` (twice).
    -   **`calcule_angle(self) -> float`**
        -   **Signature:** `calcule_angle(self) -> float`
        -   **Returns:** `float`: The angle turned since `decide_turn_direction` was called.
        -   **Description:** Implements the abstract method from `RobotAdapter`. Calculates the angle turned based on the change in encoder positions (`delta_left`, `delta_right`) relative to the initial positions stored during `decide_turn_direction`. Uses the formula: `angle = (delta_left - delta_right) * wheel_circumference / (360 * self.WHEEL_BASE_WIDTH)`.
        -   **Called By:** `controller.StrategyAsync.Tourner.step()`.
        -   **Calls:** `self.get_motor_positions()`, `math.pi`.
    -   **`slow_speed(self, new_slow_speed)`**
        -   **Signature:** `slow_speed(self, new_slow_speed: float)`
        -   **Parameters:** `new_slow_speed`: The new speed to set for the slower wheel.
        -   **Returns:** `None`
        -   **Description:** Implements the method required by strategies like `Tourner`. Sets the speed of the wheel currently designated as the "slow wheel" during a turn.
        -   **Called By:** `controller.StrategyAsync.Tourner.step()`.
        -   **Calls:** `self.set_motor_speed()`.

**Dependencies:**

-   `math` (standard library)
-   `model.map_model.MapModel`
-   `utils.geometry.normalize_angle`
-   `controller.adapter.RobotAdapter`

--- 

## `src/model/clock.py`

**Purpose:** This module defines the `Clock` class, which provides a simple time-keeping mechanism that can notify subscribers about time changes. This is potentially useful for simulation timing, animation, or any component that needs regular updates based on elapsed time.

**Classes:**

### `Clock`

-   **Description:** A timer that runs in its own loop (when `start()` is called) and notifies registered callbacks about elapsed time. The notifications occur as frequently as possible, with a small sleep to prevent excessive CPU usage.
-   **Attributes:**
    -   `subscribers` (list): List of callback functions to notify about time changes.
    -   `last_time` (float): Timestamp of the last update, used to calculate elapsed time (`delta_time`).
    -   `running` (bool): Flag indicating if the clock is running. Controls the main loop in `start()`.
-   **Methods:**
    -   **`__init__(self)`**
        -   **Signature:** `__init__(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Initializes the clock with an empty list of subscribers. Sets `last_time` to the current time using `time.time()` and sets `running` to `True`.
        -   **Calls:** `time.time()`, initializes empty `subscribers` list.
    -   **`add_subscriber(self, callback)`**
        -   **Signature:** `add_subscriber(self, callback)`
        -   **Parameters:** `callback`: A function that accepts a `delta_time` parameter.
        -   **Returns:** `None`
        -   **Description:** Adds the provided `callback` function to the list of subscribers that will be notified of time changes.
        -   **Called By:** This method is not directly called by any other part of the provided code, suggesting the `Clock` class might be unused or used optionally.
        -   **Calls:** `list.append()`.
    -   **`start(self)`**
        -   **Signature:** `start(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None` (though it contains an infinite loop until `stop()` is called)
        -   **Description:** Starts the main timing loop. While `running` is `True`, it continuously:
            1. Gets the current time.
            2. Calculates `delta_time` (time elapsed since `last_time`).
            3. Updates `last_time` to the current time.
            4. Calls each subscriber function with `delta_time`.
            5. Sleeps for a small interval (0.001 seconds) to reduce CPU usage.
        -   **Called By:** This method is not directly called by any other part of the provided code.
        -   **Calls:** `time.time()`, `time.sleep()`, and invokes each callback function in `subscribers` with `delta_time`.
    -   **`stop(self)`**
        -   **Signature:** `stop(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Sets `running` to `False`, which will cause the main loop in `start()` to terminate (if it's running).
        -   **Called By:** This method is not directly called by any other part of the provided code.
        -   **Calls:** None directly, just modifies `self.running`.

**Dependencies:**
-   `time` (standard library)

**Note:** This class doesn't appear to be directly used in the simulation logic seen in other files. It may be an alternative timing mechanism that was implemented but not integrated, or it could be used in parts of the code not yet analyzed. The main simulation in `SimulationController` uses its own timing mechanism with `threading` and operates at a fixed update rate.

---

## `src/view/robot_view.py`

**Purpose:** This module defines the `RobotView` class which handles the visual representation of the robot in the Tkinter GUI. It renders the robot as a triangle on a canvas, displays speed and angle information, and can optionally show the robot's path.

**Classes:**

### `RobotView`

-   **Description:** Manages the visualization of the robot on a Tkinter canvas. It creates a triangular representation of the robot that points in the direction of movement, and includes a label displaying speed and angle information.
-   **Attributes:**
    -   `parent`: The parent widget (typically a frame) that contains the canvas.
    -   `canvas` (`tk.Canvas`): The Tkinter canvas where the robot is drawn.
    -   `speed_label` (`tk.Label`): A label widget displaying speed and angle information.
    -   `WHEEL_BASE_WIDTH` (float): The width between the robot's wheels, used for drawing proportions.
    -   `last_x`, `last_y` (float or None): The previous position of the robot, used for drawing the path trace.
-   **Methods:**
    -   **`__init__(self, parent, sim_controller)`**
        -   **Signature:** `__init__(self, parent, sim_controller)`
        -   **Parameters:**
            -   `parent`: The parent widget to contain the canvas.
            -   `sim_controller`: The `SimulationController` instance that manages the robot's state.
        -   **Returns:** `None`
        -   **Description:** Initializes the view by creating a canvas and label. Gets the `WHEEL_BASE_WIDTH` from the robot model for proper proportional rendering. Registers as a listener to the `sim_controller` to receive state updates.
        -   **Called By:** `gui_main.MainApplication.__init__()`.
        -   **Calls:** `tk.Canvas()`, `tk.Label()`, `canvas.pack()`, `label.pack()`, `sim_controller.add_state_listener()`.
    -   **`update_display(self, state)`**
        -   **Signature:** `update_display(self, state)`
        -   **Parameters:**
            -   `state`: A dictionary containing the robot's current state (`x`, `y`, `angle`, `left_speed`, `right_speed`).
        -   **Returns:** `None`
        -   **Description:** Callback method called by the `sim_controller` when the robot state changes. It schedules a safe update in the Tkinter event loop using `parent.after()`.
        -   **Called By:** `SimulationController` (via listener mechanism).
        -   **Calls:** `self.parent.after()`.
    -   **`_safe_update(self, state)`**
        -   **Signature:** `_safe_update(self, state)`
        -   **Parameters:**
            -   `state`: A dictionary containing the robot's current state.
        -   **Returns:** `None`
        -   **Description:** Internal method that is executed in the Tkinter event loop (scheduled by `update_display`). It calls both `_draw_robot` and `_update_labels` to update the visual representation.
        -   **Called By:** Tkinter event loop (scheduled by `update_display`).
        -   **Calls:** `self._draw_robot()`, `self._update_labels()`.
    -   **`_draw_robot(self, state)`**
        -   **Signature:** `_draw_robot(self, state)`
        -   **Parameters:**
            -   `state`: A dictionary containing the robot's current state.
        -   **Returns:** `None`
        -   **Description:** Internal method that draws the robot as a triangle on the canvas. First, it deletes any existing robot representations (with tag "robot"). If `last_x` and `last_y` are not `None`, it draws a line from the previous position to the current one (creating a trace of the robot's path). It updates `last_x` and `last_y` to the current position. Then it calculates the three points of the triangle (front, left, right) using trigonometry based on the robot's position, orientation, and `WHEEL_BASE_WIDTH`. Finally, it creates a blue triangle on the canvas with these points.
        -   **Called By:** `self._safe_update()`.
        -   **Calls:** `self.canvas.delete()`, `self.canvas.create_line()`, `math.cos()`, `math.sin()`, `self.canvas.create_polygon()`.
    -   **`_update_labels(self, state)`**
        -   **Signature:** `_update_labels(self, state)`
        -   **Parameters:**
            -   `state`: A dictionary containing the robot's current state.
        -   **Returns:** `None`
        -   **Description:** Internal method that updates the speed and angle information displayed in the `speed_label`. It converts the angle from radians to degrees for display purposes.
        -   **Called By:** `self._safe_update()`.
        -   **Calls:** `math.degrees()`, `self.speed_label.config()`.
    -   **`clear_robot(self)`**
        -   **Signature:** `clear_robot(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Clears the robot and any trace lines from the canvas. Resets `last_x` and `last_y` to `None` and clears the text in the speed label.
        -   **Called By:** This method is not directly called by any other part of the provided code, but could be used during simulation reset or when changing views.
        -   **Calls:** `self.canvas.delete()`, `self.speed_label.config()`.

**Dependencies:**
-   `math` (standard library)
-   `tkinter` (standard library)
-   Requires a `sim_controller` object with `add_state_listener()` method and `robot_model` attribute with `WHEEL_BASE_WIDTH` property

---

## `src/view/map_view.py`

**Purpose:** This module defines the `MapView` class which is responsible for rendering the map elements (start/end positions, obstacles) on the Tkinter canvas. It provides methods to draw, update, and delete map elements, interacting with the same canvas used by `RobotView`.

**Classes:**

### `MapView`

-   **Description:** Manages the visualization of map elements (start/end positions, obstacles) on a Tkinter canvas, which is shared with the `RobotView` to provide a unified display for the simulation.
-   **Attributes:**
    -   `parent`: The parent widget that contains the canvas.
    -   `robot_view` (`RobotView`): Reference to the robot view instance, primarily to access its canvas.
    -   `canvas` (`tk.Canvas`): Reference to the canvas from `robot_view` where map elements are drawn.
    -   `speed_label`: Seems to be referenced in `clear_all` but is not defined in the constructor. This appears to be a design issue.
-   **Methods:**
    -   **`__init__(self, parent, robot_view)`**
        -   **Signature:** `__init__(self, parent, robot_view)`
        -   **Parameters:**
            -   `parent`: The parent widget for the view.
            -   `robot_view`: The `RobotView` instance from which to obtain the canvas.
        -   **Returns:** `None`
        -   **Description:** Initializes the view by storing references to the parent widget and robot view. Gets the canvas from the `robot_view` to use for drawing.
        -   **Called By:** `gui_main.MainApplication.__init__()`.
        -   **Calls:** None directly, just stores references.
    -   **`on_map_update(self, event_type, **kwargs)`**
        -   **Signature:** `on_map_update(self, event_type: str, **kwargs)`
        -   **Parameters:**
            -   `event_type`: The type of event from the model (e.g., "start_position_changed").
            -   `**kwargs`: Additional data related to the event (e.g., `position`, `points`, `obstacle_id`).
        -   **Returns:** `None`
        -   **Description:** Event handler method called in response to map model events. Delegates to appropriate drawing methods based on the `event_type`.
        -   **Called By:** This method doesn't appear to be directly called by any other code. It might be a legacy or unused method, or the connection to the model events might be elsewhere. The `MapController.handle_map_event` method seems to do similar work instead.
        -   **Calls:** `self.draw_start()`, `self.draw_end()`, `self.draw_obstacle()`, `self.delete_item()`, `self.clear_all()` (conditionally, based on `event_type`).
    -   **`draw_start(self, position)`**
        -   **Signature:** `draw_start(self, position: tuple)`
        -   **Parameters:** `position`: A tuple (x, y) representing the start position coordinates.
        -   **Returns:** `None`
        -   **Description:** Draws a yellow square at the specified position to represent the start point. First deletes any existing start marker.
        -   **Called By:** `MapController.handle_map_event()`.
        -   **Calls:** `print()`, `self.canvas.delete()`, `self.canvas.create_rectangle()`.
    -   **`draw_end(self, position)`**
        -   **Signature:** `draw_end(self, position: tuple)`
        -   **Parameters:** `position`: A tuple (x, y) representing the end position coordinates.
        -   **Returns:** `None`
        -   **Description:** Draws a green square at the specified position to represent the end point. First deletes any existing end marker.
        -   **Called By:** `MapController.handle_map_event()`.
        -   **Calls:** `self.canvas.delete()`, `self.canvas.create_rectangle()`.
    -   **`draw_obstacle(self, points)`**
        -   **Signature:** `draw_obstacle(self, points: list)`
        -   **Parameters:** `points`: A list of (x, y) tuples representing the vertices of the obstacle.
        -   **Returns:** The canvas ID of the created polygon.
        -   **Description:** Creates a red polygon with a black outline using the given points to represent an obstacle.
        -   **Called By:** `MapController.handle_map_event()`.
        -   **Calls:** `self.canvas.create_polygon()`.
    -   **`delete_item(self, tag_or_id)`**
        -   **Signature:** `delete_item(self, tag_or_id)`
        -   **Parameters:** `tag_or_id`: A tag string or canvas item ID to delete.
        -   **Returns:** `None`
        -   **Description:** Deletes the specified item from the canvas, given either its ID or tag.
        -   **Called By:** `MapController.handle_map_event()`, `MapController.finalize_shape()`.
        -   **Calls:** `self.canvas.delete()`.
    -   **`move_item(self, item_id, dx, dy)`**
        -   **Signature:** `move_item(self, item_id, dx: float, dy: float)`
        -   **Parameters:**
            -   `item_id`: The canvas ID of the item to move.
            -   `dx`: The change in x-coordinate.
            -   `dy`: The change in y-coordinate.
        -   **Returns:** `None`
        -   **Description:** Moves the specified canvas item by the given delta (dx, dy). **Note: This method doesn't appear to be called in the provided code, potentially part of an incomplete dragging implementation.**
        -   **Called By:** This method is not directly called by any other part of the provided code.
        -   **Calls:** `self.canvas.move()`.
    -   **`create_line(self, p1, p2, fill="red", width=2)`**
        -   **Signature:** `create_line(self, p1: tuple, p2: tuple, fill: str = "red", width: int = 2)`
        -   **Parameters:**
            -   `p1`: The starting point (x, y) tuple.
            -   `p2`: The ending point (x, y) tuple.
            -   `fill`: The color of the line (default: "red").
            -   `width`: The width of the line in pixels (default: 2).
        -   **Returns:** The canvas ID of the created line.
        -   **Description:** Creates a line on the canvas connecting points p1 and p2 with the specified fill color and width.
        -   **Called By:** `MapController.handle_click()`, `MapController.handle_drag()`.
        -   **Calls:** `self.canvas.create_line()`.
    -   **`create_polygon(self, points, fill="red", outline="black")`**
        -   **Signature:** `create_polygon(self, points: list, fill: str = "red", outline: str = "black")`
        -   **Parameters:**
            -   `points`: A list of (x, y) tuples representing the vertices of the polygon.
            -   `fill`: The fill color of the polygon (default: "red").
            -   `outline`: The outline color of the polygon (default: "black").
        -   **Returns:** The canvas ID of the created polygon.
        -   **Description:** Creates a polygon on the canvas with the specified points, fill color, and outline color.
        -   **Called By:** `MapController.add_obstacle()`.
        -   **Calls:** `self.canvas.create_polygon()`.
    -   **`delete_obstacle_visual(self, polygon_id, line_ids)`**
        -   **Signature:** `delete_obstacle_visual(self, polygon_id, line_ids: list)`
        -   **Parameters:**
            -   `polygon_id`: The canvas ID of the obstacle's polygon.
            -   `line_ids`: A list of canvas IDs for lines associated with the obstacle.
        -   **Returns:** `None`
        -   **Description:** Deletes the visual representation of an obstacle, including its polygon and associated lines.
        -   **Called By:** `MapController.delete_obstacle()`.
        -   **Calls:** `self.canvas.delete()` (multiple times).
    -   **`delete_all(self)`**
        -   **Signature:** `delete_all(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Deletes all items from the canvas, including the robot's visual representation.
        -   **Called By:** `self.clear_all()`, `MapController.reset()`.
        -   **Calls:** `self.canvas.delete("all")`, `self.robot_view.clear_robot()`.
    -   **`update_message_label(self, text)`**
        -   **Signature:** `update_message_label(self, text: str)`
        -   **Parameters:** `text`: The text to display in the message label.
        -   **Returns:** `None`
        -   **Description:** This is a stub method that does nothing (`pass`). It appears to be intended to update a UI element that isn't implemented in this class. **Note: The existence of this method may indicate that the interface was designed to be expanded with a message label, but it's not implemented in the current version.**
        -   **Called By:** Various methods in `MapController`: `set_start_mode()`, `set_end_mode()`, `set_obstacles_mode()`, `add_obstacle()`, `finalize_shape()`, `delete_obstacle()`.
        -   **Calls:** None, just `pass`.
    -   **`clear_all(self)`**
        -   **Signature:** `clear_all(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Clears all items on the canvas, resets the message label, and clears the speed label if it exists. **Note: This method references `self.speed_label` which is not defined in the constructor or elsewhere, suggesting a design oversight.**
        -   **Called By:** `MapController.handle_map_event()`.
        -   **Calls:** `self.delete_all()`, `self.update_message_label("")`, `self.speed_label.config()` (conditionally).

**Dependencies:**
-   `tkinter` (standard library)
-   The `robot_view` object is expected to provide:
    -   `canvas` attribute (`tk.Canvas` instance)
    -   `clear_robot()` method

---

## `src/view/control_panel.py`

**Purpose:** This module defines the `ControlPanel` class which creates and manages the UI controls for interacting with the simulation. It provides buttons for setting the start position, drawing obstacles, running the simulation, drawing a square path, following a beacon, and resetting the simulation.

**Classes:**

### `ControlPanel`

-   **Description:** Creates and manages the control panel UI components (buttons) that allow users to interact with the map and simulation.
-   **Attributes:**
    -   `parent`: The parent widget where the control panel will be placed.
    -   `map_controller` (`MapController`): Reference to the map controller for map-related actions.
    -   `simulation_controller` (`SimulationController`): Reference to the simulation controller for simulation-related actions.
    -   `control_frame` (`tk.Frame`): The frame widget containing the control buttons.
-   **Methods:**
    -   **`__init__(self, parent, map_controller, simulation_controller)`**
        -   **Signature:** `__init__(self, parent, map_controller, simulation_controller)`
        -   **Parameters:**
            -   `parent`: The parent widget where the control panel will be placed.
            -   `map_controller`: The map controller instance for map-related actions.
            -   `simulation_controller`: The simulation controller instance for simulation-related actions.
        -   **Returns:** `None`
        -   **Description:** Initializes the control panel by storing the references to the parent widget and controllers. Creates a frame for the buttons and calls `_create_buttons()` to populate it.
        -   **Called By:** `gui_main.MainApplication.__init__()`.
        -   **Calls:** `tk.Frame()`, `frame.pack()`, `self._create_buttons()`.
    -   **`_create_buttons(self)`**
        -   **Signature:** `_create_buttons(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Creates and arranges buttons in the control frame. Each button is associated with a specific action: setting the start position, drawing obstacles, running the simulation, drawing a square path, setting a beacon, following a beacon, and resetting the simulation.
        -   **Called By:** `self.__init__()`.
        -   **Calls:** `tk.Button()`, `btn.pack()`.
    -   **`draw_square(self)`**
        -   **Signature:** `draw_square(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Initiates the drawing of a square path by creating a `PolygonStrategy` with 4 sides and running it in a separate thread. The strategy uses the simulation controller's robot model as an adapter for the movements.
        -   **Called By:** Button click event (set up in `_create_buttons()`).
        -   **Calls:**
            -   `controller.StrategyAsync.PolygonStrategy()`
            -   `threading.Thread()`
            -   `thread.start()`
            -   Defines and uses a nested function `run_strategy()` which runs the strategy's `start()` and `step()` methods in a loop until finished.
    -   **`suivre(self)`**
        -   **Signature:** `suivre(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Initiates the beacon-following behavior by creating a `FollowMovingBeaconStrategy` and running it in a separate thread. **Note: There appears to be an inconsistency as the `FollowMovingBeaconStrategy` isn't directly visible in the provided code. The nested function initializes the strategy with the robot model, which suggests a slightly different API than what's seen with `PolygonStrategy`.**
        -   **Called By:** Button click event (set up in `_create_buttons()`).
        -   **Calls:**
            -   `controller.StrategyAsync.FollowMovingBeaconStrategy()`
            -   `threading.Thread()`
            -   `thread.start()`
            -   Defines and uses a nested function `run_strategy()` which starts the strategy with the robot model and then runs its `step()` method in a loop until finished.
    -   **`reset_all(self)`**
        -   **Signature:** `reset_all(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Resets both the simulation and the map by calling the respective reset methods on the controllers.
        -   **Called By:** Button click event (set up in `_create_buttons()`).
        -   **Calls:** `self.simulation_controller.reset_simulation()`, `self.map_controller.reset()`.

**Dependencies:**
-   `tkinter` (standard library)
-   `math` (standard library, though seemingly unused directly)
-   `threading` (standard library)
-   `controller.adapter.RealRobotAdapter`
-   `robot.robot.MockRobot2IN013` (imported but unused directly in the provided code)
-   `controller.StrategyAsync.PolygonStrategy` (imported in method)
-   `controller.StrategyAsync.FollowMovingBeaconStrategy` (imported in method)
-   Requires instances of `MapController` and `SimulationController`

**Note:** There are imports in the methods rather than at the module level, which is generally not recommended in Python. Additionally, some imported modules (like `math` and `MockRobot2IN013`) don't appear to be used directly in the provided code.

---

## `src/view/vpython_view.py`

**Purpose:** This module defines the `VpythonView` class which provides a 3D visualization of the robot and its environment using the VPython library. It includes a main view of the robot and its surroundings, as well as a secondary "embedded" view representing what the robot "sees" from its perspective. It also provides functionality for capturing and analyzing these views for image-based robot control.

**Classes:**

### `VpythonView`

-   **Description:** Creates and manages a 3D visualization of the robot simulation using VPython. It displays the robot, its path, and provides an "embedded" camera view from the robot's perspective. It also includes functionality for capturing images from the embedded view and performing image analysis to detect blue beacons.
-   **Attributes:**
    -   `simulation_controller` (`SimulationController`): Reference to the simulation controller for accessing robot state.
    -   `images` (list): List of captured image paths.
    -   `_running` (bool): Flag indicating if the image capture loop is running.
    -   `_lock` (`threading.Lock`): Lock for thread-safe access to the `images` list.
    -   `frame_rate` (int): Target frame rate for the visualization (30 FPS).
    -   `scene` (`vpython.canvas`): The main VPython canvas for 3D visualization.
    -   `floor` (`vpython.box`): The 3D representation of the floor/ground.
    -   `robot_body` (`vpython.cylinder`): The main body of the robot in 3D.
    -   `wheel_left`, `wheel_right` (`vpython.cylinder`): The wheels of the robot in 3D.
    -   `direction_marker` (`vpython.sphere`): A marker showing the robot's forward direction.
    -   `path` (`vpython.curve`): A curve showing the robot's path over time.
    -   `embedded_view` (`vpython.canvas`): A secondary canvas showing the view from the robot's perspective.
    -   `running` (bool): Flag indicating if the main rendering loop is running.
    -   `thread` (`threading.Thread`): Thread for the main rendering loop.
-   **Methods:**
    -   **`__init__(self, simulation_controller, key_handler)`**
        -   **Signature:** `__init__(self, simulation_controller, key_handler)`
        -   **Parameters:**
            -   `simulation_controller`: The simulation controller instance.
            -   `key_handler`: A function to handle keyboard events.
        -   **Returns:** `None`
        -   **Description:** Initializes the 3D visualization. Creates the main scene, floor, robot components, and embedded view. Sets up keyboard event handling and registers with the `simulation_controller` to receive state updates. Starts the rendering thread and image capture thread.
        -   **Called By:** `vpython_main.MainApplication.__init__()`.
        -   **Calls:** Various VPython creation methods (`canvas()`, `box()`, `cylinder()`, etc.), `simulation_controller.add_state_listener()`, `threading.Thread()`, `thread.start()`, `self.start_capture()`.
    -   **`update_robot(self, state)`**
        -   **Signature:** `update_robot(self, state)`
        -   **Parameters:**
            -   `state`: A dictionary containing the robot's current state (`x`, `y`, `angle`, `left_speed`, `right_speed`).
        -   **Returns:** `None`
        -   **Description:** Callback method called by the `simulation_controller` when the robot state changes. Updates the position and orientation of all robot components in the 3D view. Updates the embedded camera view to match the robot's perspective. Appends to the path curve. Updates the caption with speed and angle information.
        -   **Called By:** `SimulationController` (via listener mechanism).
        -   **Calls:** VPython vector operations, `math.sin()`, `math.cos()`, `math.degrees()`, `self.path.append()`.
    -   **`start_capture(self)`**
        -   **Signature:** `start_capture(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Starts the image capture thread that periodically captures images from the embedded view.
        -   **Called By:** `self.__init__()`.
        -   **Calls:** `threading.Thread()`, `thread.start()`.
    -   **`stop_capture(self)`**
        -   **Signature:** `stop_capture(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Stops the image capture thread.
        -   **Called By:** This method is not directly called by any other part of the provided code.
        -   **Calls:** `thread.join()`.
    -   **`_capture_loop(self)`**
        -   **Signature:** `_capture_loop(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** The main loop of the image capture thread. Calls `capture_embedded_image()` approximately every 0.02 seconds.
        -   **Called By:** The image capture thread.
        -   **Calls:** `time.time()`, `self.capture_embedded_image()`, `time.sleep()`.
    -   **`get_latest_image(self)`**
        -   **Signature:** `get_latest_image(self)`
        -   **Parameters:** `self`
        -   **Returns:** The path to the most recently captured image, or `None` if no images have been captured.
        -   **Description:** Retrieves the most recent image path from the `images` list in a thread-safe manner.
        -   **Called By:** `controller.StrategyAsync.FollowBeaconByImageStrategy.step()`.
        -   **Calls:** `self._lock.__enter__()`, `self._lock.__exit__()`.
    -   **`capture_embedded_image(self)`**
        -   **Signature:** `capture_embedded_image(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Captures an image from the embedded view canvas and saves it to the user's Downloads directory with a timestamp-based filename. Adds the image path to the `images` list. **Note: Uses `os.environ["USERPROFILE"]` which is specific to Windows. The code would need modification for other platforms.**
        -   **Called By:** `self._capture_loop()`.
        -   **Calls:** `os.path.join()`, `os.environ`, `os.path.exists()`, `os.makedirs()`, `time.strftime()`, `self.embedded_view.capture()`, `print()`, `time.sleep()`, `self.images.append()`.
    -   **`analyze_image(self, image)`**
        -   **Signature:** `analyze_image(self, image)`
        -   **Parameters:** `image`: The path to the image to analyze.
        -   **Returns:** A list of dictionaries, each containing `"center"` (tuple) and `"radius"` (float) for detected blue objects.
        -   **Description:** Analyzes the specified image to detect blue objects (beacons). Uses OpenCV for image processing and color detection. Returns information about detected blue regions including their center points and radii.
        -   **Called By:** `controller.StrategyAsync.FollowBeaconByImageStrategy.step()`.
        -   **Calls:** Various OpenCV methods (`cv2.imread()`, `cv2.cvtColor()`, `cv2.inRange()`, etc.), `print()`.
    -   **`run(self)`**
        -   **Signature:** `run(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** The main loop of the rendering thread. Ensures the VPython scene is updated at a rate of 50 frames per second.
        -   **Called By:** The rendering thread.
        -   **Calls:** `vpython.rate()`.
    -   **`stop(self)`**
        -   **Signature:** `stop(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Stops the rendering loop and forcibly exits the process. **Note: The use of `os._exit()` is generally not recommended as it skips cleanup handlers, flushing file buffers, etc.**
        -   **Called By:** This method is not directly called by any other part of the provided code.
        -   **Calls:** `os._exit()`.
    -   **`reset_vpython_view(self)`**
        -   **Signature:** `reset_vpython_view(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Resets the 3D visualization to its initial state, including resetting the robot's position, orientation, and clearing its path.
        -   **Called By:** This method is not directly called by any other part of the provided code, but presumably could be called when resetting the simulation.
        -   **Calls:** VPython object property assignments, `self.path.clear()`.

**Dependencies:**
-   `vpython` (external library) - For 3D visualization
-   `threading` (standard library)
-   `time` (standard library)
-   `math` (standard library)
-   `base64` (standard library, imported but unused)
-   `os` (standard library)
-   `cv2` (OpenCV, external library, imported dynamically in `analyze_image`)
-   `numpy` (external library, imported dynamically in `analyze_image`)

**Note:** The image capture functionality is designed for Windows systems (uses `os.environ["USERPROFILE"]` to find the Downloads directory). Modifications would be needed for cross-platform compatibility.

---

## `src/view/vpython_control_panel.py`

**Purpose:** This module defines the `VPythonControlPanel` class which provides a control interface for the VPython 3D simulation view. It enables user interaction with the simulation through buttons and mouse clicks on the 3D canvas.

**Classes:**

### `VPythonControlPanel`

-   **Description:** Creates and manages a control panel for the VPython-based robot simulation. It provides buttons for actions like setting start and end positions, running simulations, and executing different robot movement strategies. It also handles mouse interactions with the 3D scene.
-   **Attributes:**
    -   `map_model` (`MapModel`): Reference to the map model for setting positions.
    -   `map_controller` (`MapController`): Reference to the map controller.
    -   `simulation_controller` (`SimulationController`): Reference to the simulation controller.
    -   `vpython_view` (`VpythonView`): Reference to the VPython visualization.
    -   `start_box` (`vpython.box`): Visual marker for the start position in 3D.
    -   `end_box` (`vpython.box`): Visual marker for the end position (or beacon) in 3D.
    -   `mode` (str): Current interaction mode ('set_start', 'set_end', or None).
-   **Methods:**
    -   **`__init__(self, map_controller, simulation_controller, vpython_view, map_model)`**
        -   **Signature:** `__init__(self, map_controller, simulation_controller, vpython_view, map_model)`
        -   **Parameters:**
            -   `map_controller`: The map controller instance.
            -   `simulation_controller`: The simulation controller instance.
            -   `vpython_view`: The VPython visualization instance.
            -   `map_model`: The map model instance.
        -   **Returns:** `None`
        -   **Description:** Initializes the VPython control panel with references to the necessary controllers and models, creates the control buttons, and sets up event handling for mouse clicks.
        -   **Called By:** `vpython_main.MainApplication.__init__()` (presumably).
        -   **Calls:** `self._create_buttons()`, `self.vpython_view.scene.bind()`.
    -   **`_create_buttons(self)`**
        -   **Signature:** `_create_buttons(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Creates a set of buttons in the VPython interface for various simulation actions. Uses VPython's `wtext` and `button` functions to create the UI elements.
        -   **Called By:** `self.__init__()`.
        -   **Calls:** VPython's `wtext()` and `button()` functions.
    -   **`handle_click(self)`**
        -   **Signature:** `handle_click(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Event handler for mouse clicks on the VPython canvas. Calculates the 3D position where the user clicked and updates the appropriate marker (start or end position) based on the current mode. Also updates the corresponding position in the map model.
        -   **Called By:** VPython event system when the user clicks on the 3D canvas.
        -   **Calls:** VPython vector operations, `self.map_model.set_start_position()` or `self.map_model.set_end_position()`.
    -   **`create_start_box(self)`**
        -   **Signature:** `create_start_box(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Creates a red box to mark the start position in the 3D view if it doesn't exist already. Sets the interaction mode to 'set_start' to prepare for the next click event.
        -   **Called By:** Button event system when the "Set Start" button is clicked.
        -   **Calls:** VPython's `box()` function, `print()`.
    -   **`create_end_box(self)`**
        -   **Signature:** `create_end_box(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Creates a blue box to mark the end position (or beacon) in the 3D view if it doesn't exist already. Sets the interaction mode to 'set_end' to prepare for the next click event.
        -   **Called By:** Button event system when the "Set Balise" button is clicked.
        -   **Calls:** VPython's `box()` function, `print()`.
    -   **`draw_square(self)`**
        -   **Signature:** `draw_square(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Executes a strategy for the robot to draw a square. Creates and runs a `PolygonStrategy` with specific parameters for a square with 100cm sides.
        -   **Called By:** Button event system when the "Draw Square" button is clicked.
        -   **Calls:** `controller.StrategyAsync.PolygonStrategy` constructor and methods.
    -   **`suivre(self)`**
        -   **Signature:** `suivre(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Executes a strategy for the robot to follow a beacon using image analysis. Creates and runs a `FollowBeaconByImageStrategy` in a separate thread.
        -   **Called By:** Button event system when the "Follow Balise" button is clicked.
        -   **Calls:** `controller.StrategyAsync.FollowBeaconByImageStrategy` constructor and methods, `threading.Thread()`, `thread.start()`.
    -   **`reset_all(self)`**
        -   **Signature:** `reset_all(self)`
        -   **Parameters:** `self`
        -   **Returns:** `None`
        -   **Description:** Resets the simulation to its initial state. Hides and repositions the start and end markers, resets the simulation controller, and resets the VPython view.
        -   **Called By:** Button event system when the "Reset" button is clicked.
        -   **Calls:** `self.simulation_controller.reset_simulation()`, `self.vpython_view.reset_vpython_view()`, `print()`.

**Dependencies:**
-   `vpython` (external library) - For 3D visualization and UI elements
-   `model.map_model.MapModel` - For accessing map data
-   `view.vpython_view.VpythonView` - For accessing the 3D visualization
-   `threading` (standard library)
-   `time` (standard library)
-   `controller.StrategyAsync.PolygonStrategy` - For robot movement strategy
-   `controller.StrategyAsync.FollowBeaconByImageStrategy` - For robot image-based tracking strategy

**Note:** The class is designed as a companion to the VPython visualization, providing interactive controls for the 3D simulation. It integrates with other components of the system, such as the map model and the simulation controller, to provide a complete user interface for the robot simulation.

---