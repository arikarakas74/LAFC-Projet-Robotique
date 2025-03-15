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
    Simulation controller for 3D robot movement and square drawing.
    
    Manages both real-time updates of the robot's 3D position and the sequence
    of commands to trace a square (alternating linear phases and rotations).
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
        self.is_3d_mode = True       # Whether to use 3D physics

        # Variables for square drawing control
        self.drawing_square = False
        self.square_step = 0
        self.side_length = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_z = 0.0
        self.start_angle = 0.0
        self.corners = []  # List of recorded corners

        # Logger for robot position traceability
        self.position_logger = logging.getLogger('traceability.positions')
        self.position_logger.setLevel(logging.INFO)
        position_handler = logging.FileHandler('traceability_positions.log')
        position_formatter = logging.Formatter('%(asctime)s - Position: %(message)s')
        position_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(position_handler)

        # Console logger
        if not cli_mode:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(position_formatter)
            self.position_logger.addHandler(console_handler)

        self.simulation_thread = None

    def add_state_listener(self, callback: Callable[[dict], None]):
        """Adds a callback that will be notified on each robot state update."""
        self.listeners.append(callback)

    def _notify_listeners(self):
        """Notifies all listeners with the current robot state."""
        state = self.robot_model.get_state()
        for callback in self.listeners:
            callback(state)

    def run_simulation(self):
        """Starts the simulation in a separate thread."""
        if self.simulation_running:
            return

        # Position the robot at the starting point if necessary
        start_pos = self.map_model.start_position
        if (self.robot_model.x, self.robot_model.y) != start_pos:
            self.robot_model.x, self.robot_model.y = start_pos
            self.robot_model.z = 0.0  # Start at ground level

        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.simulation_thread.start()

    def run_loop(self):
        """Main simulation loop, running in a separate thread."""
        last_time = time.time()
        
        while self.simulation_running:
            current_time = time.time()
            delta_time = (current_time - last_time) * SPEED_MULTIPLIER
            last_time = current_time
            
            # Update physics for the robot
            if self.is_3d_mode:
                self.update_physics_3d(delta_time)
            else:
                self.update_physics_2d(delta_time)  # For backward compatibility
                
            # Update motor positions
            self.robot_model.update_motors(delta_time)
            
            # Notify listeners of the new state
            self._notify_listeners()
            
            # Check if drawing a square and update if necessary
            if self.drawing_square:
                self.update_square_drawing()
                
            # Sleep to maintain the desired update rate
            time.sleep(self.update_interval)
            
    def update_physics_2d(self, delta_time):
        """Updates the 2D physics for backward compatibility."""
        # Get the current position and orientation
        x, y = self.robot_model.x, self.robot_model.y
        yaw = self.robot_model.yaw  # Using yaw as the 2D angle
        
        # Get motor speeds
        left_speed = self.robot_model.motor_speeds["left"]  # degrees per second
        right_speed = self.robot_model.motor_speeds["right"]  # degrees per second
        
        # Convert degrees per second to radians per second
        left_angular_velocity = math.radians(left_speed)
        right_angular_velocity = math.radians(right_speed)
        
        # Calculate wheel velocities
        left_wheel_velocity = left_angular_velocity * self.WHEEL_RADIUS
        right_wheel_velocity = right_angular_velocity * self.WHEEL_RADIUS
        
        # Calculate linear and angular velocities
        linear_velocity = (left_wheel_velocity + right_wheel_velocity) / 2
        angular_velocity = (right_wheel_velocity - left_wheel_velocity) / self.WHEEL_BASE_WIDTH
        
        # Calculate new position and orientation
        new_yaw = yaw + angular_velocity * delta_time
        
        # Use yaw for movement direction
        new_x = x + linear_velocity * math.cos(new_yaw) * delta_time
        new_y = y + linear_velocity * math.sin(new_yaw) * delta_time
        
        # Update the robot model (using 3D update with z=0 and other angles=0)
        self.robot_model.update_position(new_x, new_y, 0.0, 0.0, new_yaw, 0.0)
        
        # Log the new position
        self.position_logger.info(f"X: {new_x:.2f}, Y: {new_y:.2f}, Angle: {math.degrees(new_yaw):.2f}°")
        
    def update_physics_3d(self, delta_time):
        """Updates the 3D physics based on robot motor speeds and orientation."""
        # Get the current position and orientation
        x, y, z = self.robot_model.x, self.robot_model.y, self.robot_model.z
        pitch, yaw, roll = self.robot_model.pitch, self.robot_model.yaw, self.robot_model.roll
        
        # Get motor speeds
        left_speed = self.robot_model.motor_speeds["left"]  # degrees per second
        right_speed = self.robot_model.motor_speeds["right"]  # degrees per second
        
        # Convert degrees per second to radians per second
        left_angular_velocity = math.radians(left_speed)
        right_angular_velocity = math.radians(right_speed)
        
        # Calculate wheel velocities
        left_wheel_velocity = left_angular_velocity * self.WHEEL_RADIUS
        right_wheel_velocity = right_angular_velocity * self.WHEEL_RADIUS
        
        # Calculate linear and angular velocities in the robot's local frame
        linear_velocity = (left_wheel_velocity + right_wheel_velocity) / 2
        angular_velocity_yaw = (right_wheel_velocity - left_wheel_velocity) / self.WHEEL_BASE_WIDTH
        
        # Calculate new orientation (pitch changes based on terrain, yaw from steering, roll can be affected by forces)
        # For simplicity, we'll just update yaw directly and use small pitch/roll variations for demonstration
        new_yaw = yaw + angular_velocity_yaw * delta_time
        
        # Simulate small pitch and roll changes based on speed (for demonstration)
        # In a real physics simulation, these would be calculated from forces and torques
        speed_factor = abs(linear_velocity) / 10.0  # Normalize for effect
        terrain_pitch = 0.0  # This would normally be calculated from the terrain
        new_pitch = pitch * 0.95 + terrain_pitch * 0.05  # Slowly return to terrain orientation
        new_roll = roll * 0.95  # Slowly return to level
        
        # Apply small random variations for realism (optional)
        if linear_velocity > 0.1:
            new_pitch += (math.sin(time.time() * 5) * 0.01 * speed_factor)
            new_roll += (math.sin(time.time() * 3) * 0.01 * speed_factor)
        
        # Calculate movement in 3D space
        # The primary movement is still on the x-y plane based on yaw
        movement_vector = np.array([
            linear_velocity * math.cos(new_yaw),
            linear_velocity * math.sin(new_yaw),
            0.0  # Normally this would include vertical movement from terrain
        ])
        
        # Apply pitch and roll effects on movement (for a more realistic simulation)
        # This is a simplified version; a full physics engine would use proper transformations
        if abs(new_pitch) > 0.01:
            # Pitch affects forward/up motion
            movement_vector[0] *= math.cos(new_pitch)
            movement_vector[2] += linear_velocity * math.sin(new_pitch)
        
        # Calculate new position
        new_x = x + movement_vector[0] * delta_time
        new_y = y + movement_vector[1] * delta_time
        new_z = z + movement_vector[2] * delta_time
        
        # Apply gravity (simplified, no collision response yet)
        if new_z > 0:
            new_z -= 0.5 * self.GRAVITY * delta_time * delta_time  # Simple gravity formula
        else:
            new_z = 0  # Ground level
        
        # Normalize angles and update the robot model
        new_pitch, new_yaw, new_roll = normalize_angle_3d(new_pitch, new_yaw, new_roll)
        self.robot_model.update_position(new_x, new_y, new_z, new_pitch, new_yaw, new_roll)
        
        # Log the new position
        self.position_logger.info(
            f"X: {new_x:.2f}, Y: {new_y:.2f}, Z: {new_z:.2f}, "
            f"Pitch: {math.degrees(new_pitch):.2f}°, Yaw: {math.degrees(new_yaw):.2f}°, Roll: {math.degrees(new_roll):.2f}°"
        )

    def stop_simulation(self):
        """Stops the simulation."""
        self.simulation_running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)

    def toggle_3d_mode(self, enabled=True):
        """Toggles between 2D and 3D physics modes."""
        self.is_3d_mode = enabled
        message = "3D" if enabled else "2D"
        self.position_logger.info(f"Switched to {message} physics mode")
        
    def update_square_drawing(self):
        """Updates the square drawing process."""
        # Get the current state
        state = self.robot_model.get_state()
        x, y = state['x'], state['y']
        
        # Use yaw as the primary orientation angle
        current_angle = state['yaw']
        
        # The rest of the square drawing logic remains mostly unchanged
        # but would need updates for 3D visualization and logging
        # ...
        
    def draw_square(self, side_length):
        """Starts the process of drawing a square with the specified side length."""
        if self.drawing_square:
            return
            
        self.drawing_square = True
        self.square_step = 0
        self.side_length = side_length
        
        # Record the starting position (now in 3D)
        state = self.robot_model.get_state()
        self.start_x = state['x']
        self.start_y = state['y']
        self.start_z = state['z']
        self.start_angle = state['yaw']  # Using yaw as primary direction
        
        self.corners = [(self.start_x, self.start_y, self.start_z)]
        
        # Log the start of square drawing
        square_logger.info(f"Starting square drawing with side length: {side_length}")
        square_logger.info(f"Starting position: ({self.start_x:.2f}, {self.start_y:.2f}, {self.start_z:.2f})")
        
        # Initial movement to draw the first side
        self.robot_model.set_motor_speed("left", 100)
        self.robot_model.set_motor_speed("right", 100)
        
    # Other methods would be updated similarly to support 3D
