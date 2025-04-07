import sys
import os
import argparse # Import argparse
import logging # Import logging

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
from src.controller.StrategyAsync import HorizontalUTurnStrategy, Avancer, Tourner, Arreter, CommandeComposite, AsyncCommande # Import the new strategy and commands

# --- Helper Command for Pen --- 
class SetPen(AsyncCommande):
    """Simple command to set the robot's pen state."""
    def __init__(self, adapter, state: bool):
        super().__init__(adapter)
        self.target_state = state
        self.finished = False
    def start(self):
        if hasattr(self.adapter, 'draw'): # Check if adapter has draw method
            self.adapter.draw(self.target_state)
        else:
            print(f"Warning: Adapter {type(self.adapter).__name__} has no draw() method.")
        self.finished = True
    def step(self, delta_time):
        if not self.finished: self.start()
        return self.finished
    def is_finished(self):
        return self.finished

# --- Helper Commands for Pen Color --- 
class SetPenColor(AsyncCommande):
    """Simple command to set the robot's pen color."""
    def __init__(self, adapter, color: str):
        super().__init__(adapter)
        self.target_color = color
        self.finished = False
    def start(self):
        if self.target_color == "red" and hasattr(self.adapter, 'red'):
            self.adapter.red()
        elif self.target_color == "blue" and hasattr(self.adapter, 'blue'):
            self.adapter.blue()
        else:
            print(f"Warning: Adapter {type(self.adapter).__name__} cannot set color {self.target_color}.")
        self.finished = True
    def step(self, delta_time):
        if not self.finished: self.start()
        return self.finished
    def is_finished(self):
        return self.finished

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
    
    # Manually draw the initial robot state since sim loop isn't running
    initial_robot_state = robot_model.get_state()
    robot_view._safe_update(initial_robot_state) # Call the internal update method directly
    
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

# --- Question Q1.2 --- 

def q1_2():
    """Run the Horizontal U-Turn strategy."""

    # --- Basic Logging Setup --- 
    logging.basicConfig(
        level=logging.DEBUG, # Show DEBUG, INFO, WARNING, ERROR, CRITICAL
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Optional: Set higher level for noisy libraries if needed
    # logging.getLogger("SomeLibrary").setLevel(logging.WARNING)
    
    # --- GUI and Model Setup (Similar to q1_1) --- 
    root = tk.Tk()
    root.title("SOLO TME - Q1.2 U-Turn Strategy")

    map_model = MapModel()
    robot_model = RobotModel(map_model=map_model)

    start_pos = (50, 550) # Bottom-left corner
    map_model.set_start_position(start_pos)
    robot_model.x, robot_model.y = start_pos
    robot_model.direction_angle = 0 # Start facing right for HorizontalUTurnStrategy

    center_x, center_y = 400, 300
    obstacle_size = 50
    obstacle_half = obstacle_size / 2
    spacing = 150

    center_obstacle_points = [
        (center_x - obstacle_half, center_y - obstacle_half),
        (center_x + obstacle_half, center_y - obstacle_half),
        (center_x + obstacle_half, center_y + obstacle_half),
        (center_x - obstacle_half, center_y + obstacle_half)
    ]
    map_model.add_obstacle("obs_center", center_obstacle_points, None, [])
    upper_obstacle_points = [
        (center_x - obstacle_half, center_y - spacing - obstacle_half),
        (center_x + obstacle_half, center_y - spacing - obstacle_half),
        (center_x + obstacle_half, center_y - spacing + obstacle_half),
        (center_x - obstacle_half, center_y - spacing + obstacle_half)
    ]
    map_model.add_obstacle("obs_upper", upper_obstacle_points, None, [])
    lower_obstacle_points = [
        (center_x - obstacle_half, center_y + spacing - obstacle_half),
        (center_x + obstacle_half, center_y + spacing - obstacle_half),
        (center_x + obstacle_half, center_y + spacing + obstacle_half),
        (center_x - obstacle_half, center_y + spacing + obstacle_half)
    ]
    map_model.add_obstacle("obs_lower", lower_obstacle_points, None, [])

    sim_controller = SimulationController(map_model=map_model, robot_model=robot_model, cli_mode=False)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    robot_view = RobotView(canvas_frame, sim_controller)
    map_view = MapView(canvas_frame, robot_view)
    map_controller = MapController(map_model, map_view, root)

    map_controller.handle_map_event("start_position_changed", position=map_model.start_position)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_center", points=center_obstacle_points)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_upper", points=upper_obstacle_points)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_lower", points=lower_obstacle_points)

    # --- Strategy Execution --- 
    # Instantiate the strategy
    # Note: RobotModel implements the adapter interface needed by the strategy.
    strategy = HorizontalUTurnStrategy(
        adapter=robot_model, 
        map_model=map_model,
        vitesse_avance=1500,      # Adjust speed as needed
        vitesse_rotation=90,       # Adjust speed as needed
        proximity_threshold=200,    # How close to get before turning
        max_turns=10
    )

    # Function to run the strategy loop in a thread
    def run_strategy_loop():
        print("Starting HorizontalUTurnStrategy loop...")
        delta_time = sim_controller.update_interval # Use simulation's update interval
        strategy.start() 
        while not strategy.is_finished():
            strategy.step(delta_time) 
            time.sleep(delta_time) # Important to avoid busy-waiting
        print("HorizontalUTurnStrategy finished.")
        # Optionally stop simulation after strategy finishes
        # sim_controller.stop_simulation()

    # Start the simulation loop (updates physics and notifies views)
    sim_controller.run_simulation() 
    
    # Start the strategy execution in a separate thread
    strategy_thread = threading.Thread(target=run_strategy_loop, daemon=True)
    strategy_thread.start()

    print("Q1.2: Running Horizontal U-Turn Strategy...")

    # Start the Tkinter main loop
    root.mainloop()

# --- Question Q1.3 --- 

def q1_3():
    """Demonstrate robot pen drawing functionality."""
    # --- Basic Logging Setup --- 
    logging.basicConfig(level=logging.INFO) # INFO level is sufficient here

    # --- GUI and Model Setup --- 
    root = tk.Tk()
    root.title("SOLO TME - Q1.3 Pen Drawing")
    map_model = MapModel()
    robot_model = RobotModel(map_model=map_model)
    start_pos = (100, 100)
    map_model.set_start_position(start_pos)
    robot_model.x, robot_model.y = start_pos
    robot_model.direction_angle = 0 # Start facing right
    sim_controller = SimulationController(map_model=map_model, robot_model=robot_model)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    robot_view = RobotView(canvas_frame, sim_controller)
    map_view = MapView(canvas_frame, robot_view)
    map_controller = MapController(map_model, map_view, root)

    map_controller.handle_map_event("start_position_changed", position=map_model.start_position)
    
    # Manually draw initial robot state
    initial_robot_state = robot_model.get_state()
    robot_view._safe_update(initial_robot_state)

    # --- Define Pen Up/Down Commands --- 
    # SetPen class is now defined at the top level

    # --- Create Sequence of Commands --- 
    sequence = CommandeComposite(robot_model) # Robot model acts as adapter
    v_avance = 1500

    # 1. Move forward a bit with pen UP (default)
    sequence.ajouter_commande(SetPen(robot_model, True))
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    sequence.ajouter_commande(SetPen(robot_model, False))
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    sequence.ajouter_commande(SetPen(robot_model, True))
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    sequence.ajouter_commande(SetPen(robot_model, False))
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    
    

    # 4. Stop
    sequence.ajouter_commande(Arreter(robot_model))
    
    # --- Run the Sequence --- 
    def run_sequence_loop():
        logging.info("Starting Q1.3 sequence loop...")
        delta_time = sim_controller.update_interval 
        sequence.start() 
        while not sequence.is_finished():
            sequence.step(delta_time) 
            time.sleep(delta_time) 
        logging.info("Q1.3 sequence finished.")

    sim_controller.run_simulation() 
    sequence_thread = threading.Thread(target=run_sequence_loop, daemon=True)
    sequence_thread.start()

    logging.info("Q1.3: Running pen drawing sequence...")
    root.mainloop()

# --- Question Q1.4 --- 
def q1_4():
    """Demonstrate robot pen color change functionality."""
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("SOLO TME - Q1.4 Pen Color")
    map_model = MapModel()
    robot_model = RobotModel(map_model=map_model)
    start_pos = (100, 100)
    map_model.set_start_position(start_pos)
    robot_model.x, robot_model.y = start_pos
    robot_model.direction_angle = 0 # Start facing right
    sim_controller = SimulationController(map_model=map_model, robot_model=robot_model)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    robot_view = RobotView(canvas_frame, sim_controller)
    map_view = MapView(canvas_frame, robot_view)
    map_controller = MapController(map_model, map_view, root)
    map_controller.handle_map_event("start_position_changed", position=map_model.start_position)
    initial_robot_state = robot_model.get_state()
    robot_view._safe_update(initial_robot_state)

    # --- Create Sequence of Commands --- 
    sequence = CommandeComposite(robot_model)
    v_avance = 1500 # Speed for moving forward
    # v_rot is not needed for this sequence

    # 1. Move forward with pen UP (default color blue)
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    
    # 2. Set color RED (pen still up)
    sequence.ajouter_commande(SetPenColor(robot_model, "red"))
    
    # 3. Move forward (pen still up, color now red)
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    
    # 4. Put pen DOWN (will draw RED)
    sequence.ajouter_commande(SetPen(robot_model, True))
    
    # 5. Move forward (draws RED line)
    sequence.ajouter_commande(Avancer(100, v_avance, robot_model))
    
    # 6. Set color BLUE (pen still down)
    sequence.ajouter_commande(SetPenColor(robot_model, "blue"))
    
    # 7. Move forward (draws BLUE line)
    sequence.ajouter_commande(Avancer(100, v_avance, robot_model))
    
    # 8. Put pen UP
    sequence.ajouter_commande(SetPen(robot_model, False))

    # 9. Move forward (no trace)
    sequence.ajouter_commande(Avancer(50, v_avance, robot_model))
    
    # 10. Stop
    sequence.ajouter_commande(Arreter(robot_model))
    
    # --- Run the Sequence --- 
    def run_sequence_loop():
        logging.info("Starting Q1.4 sequence loop...")
        delta_time = sim_controller.update_interval 
        sequence.start() 
        while not sequence.is_finished():
            sequence.step(delta_time) 
            time.sleep(delta_time) 
        logging.info("Q1.4 sequence finished.")

    sim_controller.run_simulation() 
    sequence_thread = threading.Thread(target=run_sequence_loop, daemon=True)
    sequence_thread.start()

    logging.info("Q1.4: Running pen color sequence...")
    root.mainloop()

# --- Question Q1.5 --- 

def q1_5():
    """Run the Horizontal U-Turn strategy with color changes."""
    
    logging.basicConfig(level=logging.DEBUG) # Use DEBUG to see strategy states
    
    # --- GUI and Model Setup (Similar to q1_2) --- 
    root = tk.Tk()
    root.title("SOLO TME - Q1.5 U-Turn Strategy with Color")

    map_model = MapModel()
    robot_model = RobotModel(map_model=map_model)

    start_pos = (50, 550) # Bottom-left corner
    map_model.set_start_position(start_pos)
    robot_model.x, robot_model.y = start_pos
    robot_model.direction_angle = 0 # Start facing right for strategy

    # Add obstacles (same as q1_2)
    center_x, center_y = 400, 300
    obstacle_size = 50; obstacle_half = obstacle_size / 2; spacing = 150
    center_obstacle_points = [(center_x - obstacle_half, center_y - obstacle_half),(center_x + obstacle_half, center_y - obstacle_half),(center_x + obstacle_half, center_y + obstacle_half),(center_x - obstacle_half, center_y + obstacle_half)]
    map_model.add_obstacle("obs_center", center_obstacle_points, None, [])
    upper_obstacle_points = [(center_x - obstacle_half, center_y - spacing - obstacle_half),(center_x + obstacle_half, center_y - spacing - obstacle_half),(center_x + obstacle_half, center_y - spacing + obstacle_half),(center_x - obstacle_half, center_y - spacing + obstacle_half)]
    map_model.add_obstacle("obs_upper", upper_obstacle_points, None, [])
    lower_obstacle_points = [(center_x - obstacle_half, center_y + spacing - obstacle_half),(center_x + obstacle_half, center_y + spacing - obstacle_half),(center_x + obstacle_half, center_y + spacing + obstacle_half),(center_x - obstacle_half, center_y + spacing + obstacle_half)]
    map_model.add_obstacle("obs_lower", lower_obstacle_points, None, [])

    sim_controller = SimulationController(map_model=map_model, robot_model=robot_model, cli_mode=False)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    robot_view = RobotView(canvas_frame, sim_controller)
    map_view = MapView(canvas_frame, robot_view)
    map_controller = MapController(map_model, map_view, root)

    map_controller.handle_map_event("start_position_changed", position=map_model.start_position)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_center", points=center_obstacle_points)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_upper", points=upper_obstacle_points)
    map_controller.handle_map_event("obstacle_added", obstacle_id="obs_lower", points=lower_obstacle_points)
    
    # Manually draw initial robot state
    initial_robot_state = robot_model.get_state()
    robot_view._safe_update(initial_robot_state)

    # --- Strategy Execution --- 
    # Use the modified HorizontalUTurnStrategy (ensure it's the latest version)
    strategy = HorizontalUTurnStrategy(
        adapter=robot_model, 
        map_model=map_model,
        vitesse_avance=1500,     # Moderate speed
        vitesse_rotation=1000,   # Moderate turn speed
        proximity_threshold=40, # Adjusted threshold from Q1.2 debugging
        max_turns=6             # Reduced turns for quicker demo
    )

    def run_strategy_loop():
        print("Starting HorizontalUTurnStrategy Q1.5 loop...")
        delta_time = sim_controller.update_interval
        strategy.start()
        while not strategy.is_finished():
            strategy.step(delta_time) 
            time.sleep(delta_time) 
        print("HorizontalUTurnStrategy Q1.5 finished.")

    sim_controller.run_simulation()
    strategy_thread = threading.Thread(target=run_strategy_loop, daemon=True)
    strategy_thread.start()

    print("Q1.5: Running Horizontal U-Turn Strategy with Color...")
    root.mainloop()

# --- Question Q2.1 ---

def q2_1():
    """Set up simulation with two robots (mouse and cat)."""
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("SOLO TME - Q2.1 Two Robots")

    # --- Model Setup ---
    map_model = MapModel()
    # Create two robot models
    mouse_model = RobotModel(map_model=map_model)
    cat_model = RobotModel(map_model=map_model)

    # Define start positions
    mouse_start_pos = (50, 550)  # Bottom-left
    cat_start_pos = (750, 50)    # Top-right
    
    # Set initial state for mouse
    map_model.set_start_position(mouse_start_pos) # Set map's primary start if needed
    mouse_model.x, mouse_model.y = mouse_start_pos
    mouse_model.direction_angle = 0 # Facing right
    mouse_model.blue() # Mouse is blue (redundant with view logic but good practice)
    mouse_model.draw(True) # Mouse leaves a trace

    # Set initial state for cat
    cat_model.x, cat_model.y = cat_start_pos
    cat_model.direction_angle = math.pi # Facing left
    cat_model.red() # Cat is red
    cat_model.draw(True) # Cat leaves a trace

    # --- Controller Setup ---
    # Pass both models to the SimulationController
    sim_controller = SimulationController(
        map_model=map_model, 
        mouse_model=mouse_model, 
        cat_model=cat_model,
        cli_mode=False 
    )

    # --- GUI Setup ---
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # RobotView now handles drawing multiple robots based on state updates
    robot_view = RobotView(canvas_frame, sim_controller) 
    # MapView setup remains the same
    map_view = MapView(canvas_frame, robot_view)
    map_controller = MapController(map_model, map_view, root)

    # Draw map elements if any (e.g., obstacles from q1 could be added here)
    map_controller.handle_map_event("start_position_changed", position=map_model.start_position) # Draws primary start

    # Manually trigger initial draw for both robots
    initial_state = {
        'mouse': mouse_model.get_state(),
        'cat': cat_model.get_state()
    }
    robot_view._safe_update(initial_state) 

    # --- Run Simulation ---
    # Give cat some initial speed (mouse is controlled by keyboard via RobotController)
    cat_model.set_motor_speed('left', 100)
    cat_model.set_motor_speed('right', 100)

    sim_controller.run_simulation() 

    print("Q2.1: Running simulation with Mouse (blue) and Cat (red/orange).")
    root.mainloop()

# --- Entry Point --- 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run specific questions for the SOLO TME.")
    parser.add_argument(
        'question', 
        choices=['q1.1', 'q1.2', 'q1.3', 'q1.4', 'q1.5', 'q2.1'], # Corrected choices list
        help='Specify which question to run'
    )
    args = parser.parse_args()

    if args.question == 'q1.1':
        print("Running Question 1.1...")
        q1_1()
    elif args.question == 'q1.2':
        print("Running Question 1.2...")
        q1_2()
    elif args.question == 'q1.3':
        print("Running Question 1.3...")
        q1_3()
    elif args.question == 'q1.4':
        print("Running Question 1.4...")
        q1_4()
    elif args.question == 'q1.5': 
        print("Running Question 1.5...")
        q1_5()
    elif args.question == 'q2.1': # Add q2.1 execution
        print("Running Question 2.1...")
        q2_1()
    else:
        print(f"Unknown question: {args.question}. Please choose from available options.") 