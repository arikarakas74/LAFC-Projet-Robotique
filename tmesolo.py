import sys
import os

# Add project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import tkinter as tk
import math
import time
import threading

# Import necessary components from your project
from src.model.map_model import MapModel
from src.model.robot import RobotModel
from src.controller.simulation_controller import SimulationController
from src.controller.map_controller import MapController
from src.view.robot_view import RobotView
from src.view.map_view import MapView
from src.view.control_panel import ControlPanel
from src.gui_main import MainApplication # Assuming gui_main contains the main Tkinter setup

# --- Question Q1.1 --- 

def q1_1():
    """Create a simulation with 3 aligned obstacles and robot in bottom-left."""
    
    # Create a Tkinter root window (it might be hidden later)
    root = tk.Tk()
    root.title("SOLO TME - Q1.1 Simulation")

    # --- Reusing setup from gui_main.py or similar --- 
    # Initialize models
    map_model = MapModel()
    robot_model = RobotModel(map_model=map_model)

    # Define start position and obstacles
    start_pos = (50, 550)  # Bottom-left corner
    map_model.set_start_position(start_pos)
    robot_model.x, robot_model.y = start_pos
    robot_model.direction_angle = -math.pi / 2 # Pointing upwards

    # Center coordinates (assuming 800x600 canvas)
    center_x, center_y = 400, 300
    obstacle_size = 50
    obstacle_half = obstacle_size / 2
    spacing = 150 # Spacing between obstacles

    # Define obstacle shapes (simple squares for now)
    # Center obstacle
    center_obstacle_points = [
        (center_x - obstacle_half, center_y - obstacle_half),
        (center_x + obstacle_half, center_y - obstacle_half),
        (center_x + obstacle_half, center_y + obstacle_half),
        (center_x - obstacle_half, center_y + obstacle_half)
    ]
    map_model.add_obstacle("obs_center", center_obstacle_points, None, [])

    # Upper middle obstacle
    upper_obstacle_points = [
        (center_x - obstacle_half, center_y - spacing - obstacle_half),
        (center_x + obstacle_half, center_y - spacing - obstacle_half),
        (center_x + obstacle_half, center_y - spacing + obstacle_half),
        (center_x - obstacle_half, center_y - spacing + obstacle_half)
    ]
    map_model.add_obstacle("obs_upper", upper_obstacle_points, None, [])

    # Lower middle obstacle
    lower_obstacle_points = [
        (center_x - obstacle_half, center_y + spacing - obstacle_half),
        (center_x + obstacle_half, center_y + spacing - obstacle_half),
        (center_x + obstacle_half, center_y + spacing + obstacle_half),
        (center_x - obstacle_half, center_y + spacing + obstacle_half)
    ]
    map_model.add_obstacle("obs_lower", lower_obstacle_points, None, [])

    # Initialize Simulation Controller (ensure cli_mode=False if using GUI parts)
    sim_controller = SimulationController(map_model=map_model, robot_model=robot_model, cli_mode=False)

    # --- Setting up the GUI --- 
    # Create main frames for layout (similar to gui_main)
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    controls_frame = tk.Frame(main_frame)
    controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

    # Create views
    robot_view = RobotView(canvas_frame, sim_controller)
    map_view = MapView(canvas_frame, robot_view)

    # Create Map Controller - Link model and view
    map_controller = MapController(map_model, map_view, root)

    # Create Control Panel - Optional for this question, but good for consistency
    # control_panel = ControlPanel(controls_frame, map_controller, sim_controller)

    # Manually draw initial state from map_model as MapController might miss initial setup
    map_controller.handle_map_event("start_position_changed", position=map_model.start_position)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_center", points=center_obstacle_points)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_upper", points=upper_obstacle_points)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_lower", points=lower_obstacle_points)

    # Register state listener for robot view updates
    sim_controller.add_state_listener(robot_view.update_display)
    
    # Optionally start the simulation loop if needed for visualization
    # sim_controller.run_simulation()

    print("Q1.1: Simulation window created with 3 obstacles and robot at bottom-left.")
    print("Robot Start Position:", start_pos)
    print("Obstacles:")
    print("- Center:", center_obstacle_points)
    print("- Upper Middle:", upper_obstacle_points)
    print("- Lower Middle:", lower_obstacle_points)

    # Start the Tkinter main loop
    root.mainloop()

# --- Entry Point --- 

if __name__ == '__main__':
    # Example: Run question 1.1
    q1_1() 