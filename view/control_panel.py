import tkinter as tk
import math
import threading
from utils.geometry import normalize_angle # Needed for angle calculations

class ControlPanel:
    """Panneau de contrôle pour les interactions utilisateur."""
    
    def __init__(self, parent, map_controller, simulation_controller):
        self.parent = parent
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        
        # --- Q1.2 Strategy State ---
        self.q1_2_active = False
        self.q1_2_turn_count = 0
        self.q1_2_state = 'stopped' # 'stopped', 'moving_right', 'turning'
        self.q1_2_target_angle = 0
        self.q1_2_collision_distance = 30 # Distance threshold (pixels/units)
        self.q1_2_turn_speed = 180 # Degrees per second
        self.q1_2_move_speed = 50 # Pixels/units per second
        self.q1_2_max_turns = 10
        # --- End Q1.2 State ---
        
        # --- Q1.5 Strategy State ---
        self.q1_5_active = False
        self.q1_5_turn_count = 0
        self.q1_5_state = 'stopped' # 'stopped', 'moving_right', 'turning'
        self.q1_5_target_angle = 0
        self.q1_5_collision_distance = 30 # Use same distance as Q1.2
        self.q1_5_turn_speed = 180      # Use same speed as Q1.2
        self.q1_5_move_speed = 50       # Use same speed as Q1.2
        self.q1_5_max_turns = 10
        # --- End Q1.5 State ---
        
        # Frame pour les boutons
        self.control_frame = tk.Frame(parent)
        self.control_frame.pack()
        
        # Boutons
        self._create_buttons()
  


    def _create_buttons(self):
        buttons = [
            ("Set Start", self.map_controller.set_start_mode),
            ("Set Obstacles", self.map_controller.set_obstacles_mode),
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Reset", self.reset_all)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)


    def reset_all(self):
        """Réinitialise l'application."""
        self.simulation_controller.reset_simulation()
        self.map_controller.reset()
        # Reset q1.2 strategy state
        self.q1_2_active = False
        self.q1_2_turn_count = 0
        self.q1_2_state = 'stopped'
        # Reset q1.5 strategy state
        self.q1_5_active = False
        self.q1_5_turn_count = 0
        self.q1_5_state = 'stopped'
        # Optionally disable drawing on reset
        if hasattr(self.simulation_controller, 'robot_model'):
             self.StrategieInvisible()
        print("Application reset.")

    # --- Color Strategies (Q1.5) ---
    def StrategieBleu(self):
        """Sets drawing color to blue and enables drawing (for the first robot)."""
        print("Executing StrategieBleu (for mouse)")
        robot_model = self.simulation_controller.get_robot_model(0)
        if robot_model:
            robot_model.bleu()
            robot_model.dessine(True)
        else:
            print("Error: Mouse model (index 0) not found for StrategieBleu")

    def StrategieRouge(self):
        """Sets drawing color to red and enables drawing (for the first robot)."""
        print("Executing StrategieRouge (for mouse)")
        robot_model = self.simulation_controller.get_robot_model(0)
        if robot_model:
            robot_model.rouge()
            robot_model.dessine(True)
        else:
            print("Error: Mouse model (index 0) not found for StrategieRouge")

    def StrategieInvisible(self):
        """Disables drawing (for the first robot)."""
        print("Executing StrategieInvisible (for mouse)")
        robot_model = self.simulation_controller.get_robot_model(0)
        if robot_model:
            robot_model.dessine(False)
        else:
            print("Error: Mouse model (index 0) not found for StrategieInvisible")
    # --- End Color Strategies ---

    # --- Q1.2 Strategy Methods ---
    def start_q1_2_strategy(self):
        """Initializes and starts the Q1.2 strategy (for the first robot)."""
        print("Starting Q1.2 Strategy (for mouse)")
        self.reset_all() # Ensure clean state for all robots
        robot_model = self.simulation_controller.get_robot_model(0)
        if not robot_model:
            print("Error: Mouse model (index 0) not found for start_q1_2_strategy")
            return
        # Start Q1.2 for the mouse
        robot_model.direction_angle = 0 # Start facing right
        self.q1_2_active = True
        self.q1_2_turn_count = 0
        self.q1_2_state = 'moving_right'
        # Set motor speeds for moving right
        robot_model.set_motor_speed("left", self.q1_2_move_speed)
        robot_model.set_motor_speed("right", self.q1_2_move_speed)
        # Ensure simulation is running
        self.simulation_controller.run_simulation()

    def _check_collision_ahead(self):
        """Simplified collision check ahead of the *target* robot."""
        # Determine which robot to check based on active strategy
        robot_model = None
        check_dist = 0
        if self.q1_2_active:
            robot_model = self.simulation_controller.get_robot_model(0) # Q1.2 targets mouse
            check_dist = self.q1_2_collision_distance
        elif self.q1_5_active:
            robot_model = self.simulation_controller.get_robot_model(0) # Q1.5 targets mouse
            check_dist = self.q1_5_collision_distance
            
        if not robot_model:
            return False # No strategy active or robot not found

        angle_rad = math.radians(robot_model.direction_angle)
        check_x = robot_model.x + check_dist * math.cos(angle_rad)
        check_y = robot_model.y + check_dist * math.sin(angle_rad)

        # Check map boundaries (Adapt if map size is dynamic)
        map_width = self.map_controller.map_view.canvas_width if hasattr(self.map_controller.map_view, 'canvas_width') else 800
        map_height = self.map_controller.map_view.canvas_height if hasattr(self.map_controller.map_view, 'canvas_height') else 600
        if not (0 <= check_x <= map_width and 0 <= check_y <= map_height):
             print(f"Collision detected for {robot_model.name}: Wall")
             return True
        
        # Check obstacles
        if self.map_controller.map_model.is_collision(check_x, check_y):
            print(f"Collision detected for {robot_model.name}: Obstacle")
            return True
            
        return False

    def step_strategy(self, delta_time):
        """Update step for the active strategy (called by the main loop)."""
        # --- Q1.2 Logic (Targets robot 0 - mouse) ---
        if self.q1_2_active:
            robot = self.simulation_controller.get_robot_model(0)
            if not robot: return # Stop if mouse not found
            
            if self.q1_2_state == 'moving_right':
                # Physics handled by SimulationController, just check collision
                if self._check_collision_ahead(): # Checks collision for mouse
                    print(f"Q1.2 Turn {self.q1_2_turn_count + 1} initiated (mouse).")
                    self.q1_2_turn_count += 1
                    if self.q1_2_turn_count >= self.q1_2_max_turns:
                        print(f"Q1.2 Strategy finished after {self.q1_2_turn_count} turns (mouse).")
                        self.q1_2_active = False
                        self.q1_2_state = 'stopped'
                        robot.set_motor_speed("left", 0)
                        robot.set_motor_speed("right", 0)
                    else:
                        self.q1_2_state = 'turning'
                        self.q1_2_target_angle = normalize_angle(robot.direction_angle + 180)
                        print(f"Q1.2 Turning towards {self.q1_2_target_angle} degrees (mouse).")
                        turn_rate_sign = 1 # Assume counter-clockwise turn
                        robot.set_motor_speed("left", -self.q1_2_turn_speed / 2 * turn_rate_sign)
                        robot.set_motor_speed("right", self.q1_2_turn_speed / 2 * turn_rate_sign)
                # else: Motors already set to move right

            elif self.q1_2_state == 'turning':
                angle_diff = normalize_angle(self.q1_2_target_angle - robot.direction_angle)
                if abs(angle_diff) < 5: # Tolerance in degrees
                    print("Q1.2 Turn complete (mouse).")
                    robot.direction_angle = self.q1_2_target_angle # Snap to target
                    self.q1_2_state = 'moving_right'
                    robot.set_motor_speed("left", self.q1_2_move_speed)
                    robot.set_motor_speed("right", self.q1_2_move_speed)
                # else: Motors already set for turning

        # --- Q1.5 Logic (Targets robot 0 - mouse) ---
        elif self.q1_5_active: 
            robot = self.simulation_controller.get_robot_model(0)
            if not robot: return # Stop if mouse not found
            
            if self.q1_5_state == 'moving_right':
                # Moving right (Red trace for mouse). Check collision.
                if self._check_collision_ahead(): # Checks collision for mouse
                    print(f"Q1.5 Turn {self.q1_5_turn_count + 1} initiated (mouse).")
                    self.q1_5_turn_count += 1
                    if self.q1_5_turn_count >= self.q1_5_max_turns:
                        print(f"Q1.5 Strategy finished after {self.q1_5_turn_count} turns (mouse).")
                        self.q1_5_active = False
                        self.q1_5_state = 'stopped'
                        robot.set_motor_speed("left", 0)
                        robot.set_motor_speed("right", 0)
                        self.StrategieInvisible() # Turn off mouse drawing
                    else:
                        # Initiate 180-degree turn WITH BLUE color for mouse
                        self.StrategieBleu() # Set mouse color BEFORE starting turn
                        self.q1_5_state = 'turning'
                        self.q1_5_target_angle = normalize_angle(robot.direction_angle + 180)
                        print(f"Q1.5 Turning towards {self.q1_5_target_angle} degrees (mouse - Blue trace).")
                        turn_rate_sign = 1 # Assume counter-clockwise turn
                        robot.set_motor_speed("left", -self.q1_5_turn_speed / 2 * turn_rate_sign)
                        robot.set_motor_speed("right", self.q1_5_turn_speed / 2 * turn_rate_sign)
                # else: Continue moving right

            elif self.q1_5_state == 'turning':
                # Turning (Blue trace for mouse). Check if turn complete.
                angle_diff = normalize_angle(self.q1_5_target_angle - robot.direction_angle)
                if abs(angle_diff) < 5: # Tolerance in degrees
                    print("Q1.5 Turn complete (mouse).")
                    robot.direction_angle = self.q1_5_target_angle # Snap to target
                    # Start moving right WITH RED color for mouse
                    self.StrategieRouge() # Set mouse color BEFORE moving right
                    self.q1_5_state = 'moving_right'
                    robot.set_motor_speed("left", self.q1_5_move_speed)
                    robot.set_motor_speed("right", self.q1_5_move_speed)
                    print("Q1.5 Moving right (mouse - Red trace).")
                # else: Continue turning

    # --- Q1.5 Strategy Methods ---
    def start_q1_5_strategy(self):
        """Initializes and starts the Q1.5 strategy (for the first robot)."""
        print("Starting Q1.5 Strategy (for mouse)")
        self.reset_all() # Ensure clean state for all robots
        robot_model = self.simulation_controller.get_robot_model(0)
        if not robot_model:
            print("Error: Mouse model (index 0) not found for start_q1_5_strategy")
            return
        # Initialize Q1.5 state for the mouse
        robot_model.direction_angle = 0 # Start facing right
        self.q1_5_active = True
        self.q1_5_turn_count = 0
        self.q1_5_state = 'moving_right'
        # Apply initial color strategy for mouse
        self.StrategieRouge() # Start mouse with red trace
        # Set initial motor speeds for moving right (for mouse)
        robot_model.set_motor_speed("left", self.q1_5_move_speed)
        robot_model.set_motor_speed("right", self.q1_5_move_speed)
        print("Q1.5 Moving right (mouse - Red trace).")
        # Ensure simulation is running
        self.simulation_controller.run_simulation()

    # --- End Q1.5 Strategy Methods ---