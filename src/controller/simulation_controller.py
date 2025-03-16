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
from controller.Strategy import StrategyExecutor, PolygonStrategy, FollowBeaconStrategy

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
    
    Manages real-time updates of the robot's 3D position and executes 
    movement strategies for various patterns and behaviors.
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

        self.simulation_thread = None

        # Create the strategy executor
        self.strategy_executor = StrategyExecutor(self)

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
        if start_pos:
            # Handle 3D start position
            if len(start_pos) == 3:
                self.robot_model.x, self.robot_model.y, self.robot_model.z = start_pos
            else:
                self.robot_model.x, self.robot_model.y = start_pos
                self.robot_model.z = 0.0  # Start at ground level

        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.simulation_thread.start()
        
        # If a beacon is set, automatically follow it
        if self.map_model.end_position is not None:
            # Use a small delay to ensure the simulation has fully started
            # before following the beacon
            threading.Timer(0.5, self.follow_beacon).start()
            
            # Log that we're automatically following the beacon
            beacon_pos = self.map_model.end_position
            if len(beacon_pos) == 3:
                beacon_x, beacon_y, beacon_z = beacon_pos
                self.position_logger.info(f"Auto-following beacon at ({beacon_x:.1f}, {beacon_y:.1f}, {beacon_z:.1f})")
            else:
                beacon_x, beacon_y = beacon_pos
                self.position_logger.info(f"Auto-following beacon at ({beacon_x:.1f}, {beacon_y:.1f})")

    def run_loop(self):
        """Main simulation loop, running in a separate thread."""
        last_time = time.time()
        
        while self.simulation_running:
            current_time = time.time()
            delta_time = (current_time - last_time) * SPEED_MULTIPLIER
            last_time = current_time

            # Update 3D physics for the robot
            self.update_physics_3d(delta_time)
                
            # Update motor positions
            self.robot_model.update_motors(delta_time)
            
            # Notify listeners of the new state
            self._notify_listeners()
            
            # Check if drawing a square and update if necessary
            if self.drawing_square:
                self.update_square_drawing()
                
            # Sleep to maintain the desired update rate
            time.sleep(self.update_interval)

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

    def update_square_drawing(self):
        """Updates the square drawing process."""
        # Get the current state
        state = self.robot_model.get_state()
        x, y = state['x'], state['y']
        
        # Use yaw as the primary orientation angle
        current_angle = state['yaw']
        
        # The square drawing logic for 3D visualization and logging
        # ...

    def draw_polygon(self, sides, side_length):
        """
        Draws a regular polygon with the specified number of sides and side length.
        
        Args:
            sides: The number of sides of the polygon
            side_length: The length of each side in centimeters
        """
        if sides < 3:
            self.position_logger.error("A polygon must have at least 3 sides")
            return
            
        # Create a polygon strategy
        polygon_strategy = PolygonStrategy(
            sides=sides,
            side_length_cm=side_length,
            movement_speed=100,  # Use a moderate speed
            turning_speed=45     # 45 degrees per second
        )
        
        # Execute the strategy
        self.strategy_executor.execute_strategy(polygon_strategy)
        self.position_logger.info(f"Started drawing a {sides}-sided polygon with side length {side_length}cm")
    
    def draw_square(self, side_length):
        """Draws a square with the specified side length using the strategy pattern."""
        self.draw_polygon(4, side_length)
        
    def draw_triangle(self, side_length):
        """Draws a triangle with the specified side length using the strategy pattern."""
        self.draw_polygon(3, side_length)
    
    def draw_pentagon(self, side_length):
        """Draws a pentagon with the specified side length using the strategy pattern."""
        self.draw_polygon(5, side_length)
        
    def follow_beacon(self):
        """
        Makes the robot follow the beacon (end position) using the FollowBeaconStrategy.
        
        The robot will orient itself towards the beacon and move towards it.
        If no beacon is set, a warning will be logged.
        """
        # Check if a strategy is already running
        if self.strategy_executor.is_running():
            current_strategy = self.strategy_executor.current_strategy
            # If it's already a FollowBeaconStrategy, just ensure it's aware of any changes
            if isinstance(current_strategy, FollowBeaconStrategy):
                self.position_logger.info("Already following beacon - continuing with current strategy")
                # Reset the state to ensure it picks up the latest beacon position
                current_strategy.reset_state()
                return
            else:
                # If a different strategy is running, stop it
                self.strategy_executor.stop()
                self.position_logger.info("Stopped previous strategy to follow beacon")
            
        # Check if the beacon is set
        if self.map_model.end_position is None:
            self.position_logger.warning("Cannot follow beacon: No beacon position set")
            return
            
        # Create a beacon following strategy with default parameters
        beacon_strategy = FollowBeaconStrategy(
            distance_tolerance=10,  # Stop within 10cm of the beacon
            angle_tolerance=0.2,    # Allow 0.2 radians (~11 degrees) of orientation error
            movement_speed=100,     # Move at 100% speed
            turning_speed=45        # Turn at 45 degrees per second
        )
        
        # Execute the strategy
        self.strategy_executor.execute_strategy(beacon_strategy)
        
        # Log that we've started following the beacon
        beacon_pos = self.map_model.end_position
        if len(beacon_pos) == 3:
            beacon_x, beacon_y, beacon_z = beacon_pos
            self.position_logger.info(f"Started following beacon at ({beacon_x:.1f}, {beacon_y:.1f}, {beacon_z:.1f})")
        else:
            beacon_x, beacon_y = beacon_pos
            self.position_logger.info(f"Started following beacon at ({beacon_x:.1f}, {beacon_y:.1f})")
        
    def stop_strategy(self):
        """Stops any running strategy."""
        self.strategy_executor.stop()
        self.position_logger.info("Stopped strategy execution")
    
    def is_strategy_running(self):
        """
        Checks if a strategy is currently running.
        
        Returns:
            bool: True if a strategy is running, False otherwise
        """
        return self.strategy_executor.is_running()

    def export_movements_to_file(self, output_file="robot_movements.csv"):
        """Exports recorded robot movements to a CSV file.
        
        Args:
            output_file: Name of the CSV file to export to. Default is "robot_movements.csv".
            
        Returns:
            bool: True if export was successful, False otherwise.
        """
        try:
            # Read the traceability log file
            with open("traceability_positions.log", "r") as log_file:
                lines = log_file.readlines()
            
            # Open output CSV file
            with open(output_file, "w") as csv_file:
                # Write header
                csv_file.write("Timestamp,X,Y,Z,Pitch,Yaw,Roll\n")
                
                # Process each line from the log
                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    # Extract timestamp and position data
                    parts = line.split(" - Position: ")
                    if len(parts) != 2:
                        continue
                    
                    timestamp = parts[0].strip()
                    position_data = parts[1].strip()
                    
                    # Extract X, Y, Z values and angles
                    x, y, z = 0.0, 0.0, 0.0
                    pitch, yaw, roll = 0.0, 0.0, 0.0
                    
                    # Parse X, Y
                    if "X:" in position_data and "Y:" in position_data:
                        try:
                            x_part = position_data.split("X:")[1].split(",")[0].strip()
                            x = float(x_part)
                            
                            y_part = position_data.split("Y:")[1].split(",")[0].strip()
                            y = float(y_part)
                        except:
                            pass
                    
                    # Parse Z if present
                    if "Z:" in position_data:
                        try:
                            z_part = position_data.split("Z:")[1].split(",")[0].strip()
                            z = float(z_part)
                        except:
                            pass
                    
                    # Parse angles
                    if "Pitch:" in position_data:
                        try:
                            pitch_part = position_data.split("Pitch:")[1].split("°")[0].strip()
                            pitch = float(pitch_part)
                        except:
                            pass
                            
                    if "Yaw:" in position_data:
                        try:
                            yaw_part = position_data.split("Yaw:")[1].split("°")[0].strip()
                            yaw = float(yaw_part)
                        except:
                            pass
                    elif "Angle:" in position_data:  # Backward compatibility for 2D logs
                        try:
                            yaw_part = position_data.split("Angle:")[1].split("°")[0].strip()
                            yaw = float(yaw_part)
                        except:
                            pass
                            
                    if "Roll:" in position_data:
                        try:
                            roll_part = position_data.split("Roll:")[1].split("°")[0].strip()
                            roll = float(roll_part)
                        except:
                            pass
                    
                    # Write to CSV
                    csv_file.write(f"{timestamp},{x},{y},{z},{pitch},{yaw},{roll}\n")
            
            self.position_logger.info(f"Movements exported to {output_file}")
            return True
        except Exception as e:
            self.position_logger.error(f"Error exporting movements: {str(e)}")
            return False

    # Other methods would be updated similarly to support 3D
