import threading
import time
import math
import logging
import numpy as np
from typing import Callable, List
from model.robot import RobotModel
from controller.robot_controller import RobotController
from utils.geometry import normalize_angle
from utils.geometry3d import normalize_angle_3d
from controller.strategy import StrategyManager
from utils.data_exporter import DataExporter

# --- Configuration des loggers ---

# Logger pour la traçabilité du dessin du carré
square_logger = logging.getLogger('traceability.square')
square_logger.setLevel(logging.INFO)
square_handler = logging.FileHandler('traceability_square.log')
square_formatter = logging.Formatter('%(asctime)s - %(message)s')
square_handler.setFormatter(square_formatter)
square_logger.addHandler(square_handler)

# Multiplicateur pour accélérer la simulation
SPEED_MULTIPLIER = 8.0

class SimulationController:
    """
    Simulation controller for 3D robot movement and pattern following.
    
    Manages real-time updates of the robot's 3D position and handles the physics
    simulation for robot movement. Core responsibility is managing the simulation
    loop and physics calculations.
    """
    WHEEL_BASE_WIDTH = 20.0  # Distance between wheels (cm)
    WHEEL_DIAMETER = 5.0     # Wheel diameter (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    GRAVITY = 9.81           # Gravity acceleration (m/s²)

    def __init__(self, map_model, robot_model, cli_mode=False):
        """
        Initializes the simulation controller.
        
        Args:
            map_model: Map model (containing the start position, etc.)
            robot_model: Robot model (position, motors, etc.)
            cli_mode: Whether the simulation is running in CLI mode
        """
        self.robot_model = robot_model
        self.map_model = map_model
        self.robot_controller = RobotController(self.robot_model, self.map_model, cli_mode)
        self.simulation_running = False
        self.listeners: List[Callable[[dict], None]] = []
        self.update_interval = 0.02  # Update interval: 50 Hz
        self.simulation_time = 0.0
        self.simulation_thread = None
        self.simulation_lock = threading.Lock()
        self.target_fps = 60
        self.physics_substeps = 10
        self.log_data = []
        self.MAX_LOG_ENTRIES = 1000  # Maximum number of log entries to keep

        # Logger for robot position traceability
        self.position_logger = logging.getLogger('traceability.position')
        self.position_logger.setLevel(logging.INFO)
        position_handler = logging.FileHandler('traceability_positions.log')
        position_formatter = logging.Formatter('%(asctime)s - %(message)s')
        position_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(position_handler)

        # Console logger
        if not cli_mode:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(position_formatter)
            self.position_logger.addHandler(console_handler)

        # Create the strategy manager and data exporter
        # These are accessible by other components directly
        self.strategy_manager = StrategyManager(self.robot_model)
        self.data_exporter = DataExporter()
        
        # Set up logging
        self.logger = logging.getLogger("SimulationController")
        self.logger.info("Simulation controller initialized")

    def add_state_listener(self, callback: Callable[[dict], None]):
        """Adds a callback that will be notified on each robot state update."""
        self.listeners.append(callback)

    def _notify_listeners(self):
        """Notifies all listeners with the current robot state."""
        state = self.robot_model.get_state()
        for callback in self.listeners:
            callback(state)

    def run_simulation(self):
        """
        Start the simulation if it's not already running.
        """
        if self.simulation_running:
            self.logger.warning("Simulation is already running")
            return

        # Check if we have a starting position
        start_pos = self.map_model.start_position
        if start_pos:
            # Handle 3D vs 2D start position
            if len(start_pos) == 3:
                # We have a 3D position with z-coordinate
                self.robot_model.set_position(start_pos[0], start_pos[1], start_pos[2])
                self.logger.info(f"Positioned robot at 3D start: ({start_pos[0]}, {start_pos[1]}, {start_pos[2]})")
            else:
                # We have a 2D position, set z to 0
                self.robot_model.set_position(start_pos[0], start_pos[1], 0.0)
                self.logger.info(f"Positioned robot at 2D start: ({start_pos[0]}, {start_pos[1]}, 0.0)")
        
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        self.logger.info("Simulation started")

        # If we have a beacon position, set a timer to follow it automatically
        if self.map_model.beacon_position:
            beacon_pos = self.map_model.beacon_position
            timer = threading.Timer(1.0, self.strategy_manager.follow_beacon, args=[beacon_pos])
            timer.daemon = True
            timer.start()
            
            # Log beacon position (2D or 3D)
            if len(beacon_pos) == 3:
                self.logger.info(f"Set to follow 3D beacon at ({beacon_pos[0]}, {beacon_pos[1]}, {beacon_pos[2]})")
            else:
                self.logger.info(f"Set to follow 2D beacon at ({beacon_pos[0]}, {beacon_pos[1]})")

    def stop_simulation(self):
        """
        Stop the simulation if it's running.
        """
        if not self.simulation_running:
            self.logger.warning("Simulation is not running")
            return

        self.simulation_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
        
        # Stop any running strategy
        self.strategy_manager.stop_strategy()
        self.logger.info("Simulation stopped")

    def _simulation_loop(self):
        """
        Main simulation loop.
        """
        self.logger.debug("Simulation loop started")
        last_time = time.time()
        
        while self.simulation_running:
            # Calculate frame time
            current_time = time.time()
            frame_time = current_time - last_time
            last_time = current_time
            
            # Cap frame time to avoid large jumps
            frame_time = min(frame_time, 0.1)
            
            # Update simulation
            self._update_simulation(frame_time)
            
            # Sleep to maintain target FPS
            target_frame_time = 1.0 / self.target_fps
            sleep_time = max(0, target_frame_time - (time.time() - current_time))
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        self.logger.debug("Simulation loop ended")

    def _update_simulation(self, frame_time):
        """
        Update the simulation state.
        
        Args:
            frame_time: The time elapsed since the last frame
        """
        # Perform physics updates in substeps for stability
        substep_time = frame_time / self.physics_substeps
        
        with self.simulation_lock:
            for _ in range(self.physics_substeps):
                self._update_physics(substep_time)
                
            # Update total simulation time
            self.simulation_time += frame_time
            
            # Notify listeners about the updated state
            self._notify_listeners()
            
            # Log the robot state periodically (every 0.1 seconds of simulation time)
            if int(self.simulation_time * 10) > int((self.simulation_time - frame_time) * 10):
                self._log_robot_state()

    def _update_physics(self, delta_time):
        """
        Update the physics state.
        
        Args:
            delta_time: The time elapsed since the last physics update
        """
        # Update robot physics
        self.robot_model.update(delta_time)
        
        # Check for collisions with map boundaries
        self._check_map_boundaries()
        
        # Check for collisions with obstacles
        self._check_obstacle_collisions()

    def _check_map_boundaries(self):
        """Check and handle collisions with map boundaries."""
        map_width = self.map_model.width
        map_height = self.map_model.height
        
        state = self.robot_model.get_state()
        x, y = state['x'], state['y']
        
        # Simple boundary checking - clamp position and stop movement in that direction
        if x < 0:
            self.robot_model.set_position(0, y, state['z'])
            self.robot_model.stop_movement_x()
        elif x > map_width:
            self.robot_model.set_position(map_width, y, state['z'])
            self.robot_model.stop_movement_x()
            
        if y < 0:
            self.robot_model.set_position(x, 0, state['z'])
            self.robot_model.stop_movement_y()
        elif y > map_height:
            self.robot_model.set_position(x, map_height, state['z'])
            self.robot_model.stop_movement_y()

    def _check_obstacle_collisions(self):
        """Check and handle collisions with obstacles."""
        # Get robot state
        state = self.robot_model.get_state()
        robot_x, robot_y, robot_z = state['x'], state['y'], state['z']
        robot_radius = self.robot_model.radius
        
        # Check for collisions with 3D obstacles
        for obstacle_id, (min_point, max_point, _) in self.map_model.obstacles_3d.items():
            # Simple collision detection with bounding box
            # Check if robot sphere intersects with obstacle box
            
            # Calculate closest point on box to robot center
            closest_x = max(min_point[0], min(robot_x, max_point[0]))
            closest_y = max(min_point[1], min(robot_y, max_point[1]))
            closest_z = max(min_point[2], min(robot_z, max_point[2]))
            
            # Calculate distance from closest point to robot center
            dx = robot_x - closest_x
            dy = robot_y - closest_y
            dz = robot_z - closest_z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # If distance is less than robot radius, we have a collision
            if distance < robot_radius:
                # Simple collision response - push robot away
                if distance > 0:  # Avoid division by zero
                    push_factor = (robot_radius - distance) / distance
                    push_x = dx * push_factor
                    push_y = dy * push_factor
                    push_z = dz * push_factor
                    
                    # Update robot position
                    self.robot_model.update_position(
                        robot_x + push_x,
                        robot_y + push_y,
                        robot_z + push_z,
                        state['pitch'],
                        state['yaw'],
                        state['roll']
                    )
                    
                    # Log collision
                    self.logger.info(f"Collision with obstacle {obstacle_id}")

    def _log_robot_state(self):
        """Log the current robot state for analysis."""
        state = self.robot_model.get_state().copy()
        state['time'] = self.simulation_time
        
        # Add to log data, maintaining maximum size
        self.log_data.append(state)
        if len(self.log_data) > self.MAX_LOG_ENTRIES:
            self.log_data.pop(0)

    def get_log_data(self):
        """
        Get the logged robot state data.
        
        Returns:
            list: List of logged robot states
        """
        with self.simulation_lock:
            return self.log_data.copy()
            
    def export_log_data(self, file_path):
        """
        Export the logged data to a CSV file.
        
        Args:
            file_path: Path to save the CSV file
        """
        return self.data_exporter.export_to_csv(self.get_log_data(), file_path)

    def is_simulation_running(self):
        """
        Check if the simulation is running.
        
        Returns:
            bool: True if the simulation is running, False otherwise
        """
        return self.simulation_running
