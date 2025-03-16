"""
Robot movement strategies.

This module provides classes and utilities for controlling robot movement
through various strategies, from basic movements to complex patterns.
"""

import threading
import time
import math
import logging
import numpy as np
from utils.geometry import normalize_angle

# --- Base Strategy Classes ---

class AsyncCommand:
    """Base class for asynchronous robot commands."""
    
    def start(self, robot_model):
        """
        Start command execution.
        
        Args:
            robot_model: The robot model to control
        """
        raise NotImplementedError("Subclasses must implement start()")
        
    def step(self, robot_model, delta_time):
        """
        Execute one step of the command.
        
        Args:
            robot_model: The robot model to control
            delta_time: Time elapsed since the last step
            
        Returns:
            bool: True if the command has finished, False otherwise
        """
        raise NotImplementedError("Subclasses must implement step()")
        
    def is_finished(self):
        """
        Check if the command has finished executing.
        
        Returns:
            bool: True if the command has finished, False otherwise
        """
        raise NotImplementedError("Subclasses must implement is_finished()")

# --- Basic Movement Commands ---
        
class MoveForward(AsyncCommand):
    """Command to move the robot forward by a specified distance."""
    
    def __init__(self, distance_cm, speed=20.0):
        """
        Initialize the command.
        
        Args:
            distance_cm: The distance to move in centimeters
            speed: The speed to move at in cm/s
        """
        self.distance_cm = distance_cm
        self.speed = speed
        self.started = False
        self.finished = False
        self.distance_moved = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.logger = logging.getLogger("strategy.MoveForward")
        
    def start(self, robot_model):
        """Start moving forward."""
        self.started = True
        self.finished = False
        self.distance_moved = 0.0
        
        # Record starting position
        state = robot_model.get_state()
        self.start_x = state['x']
        self.start_y = state['y']
        
        # Calculate motor speeds needed to achieve desired linear speed
        # Convert from cm/s to degrees/s for the motors
        wheel_radius = robot_model.WHEEL_RADIUS
        wheel_circumference = 2 * math.pi * wheel_radius
        
        # Calculate degrees per cm
        degrees_per_cm = 360 / wheel_circumference
        
        # Calculate degrees per second for the desired speed
        dps = self.speed * degrees_per_cm
        
        # Set motor speeds
        robot_model.set_motor_speed("left", dps)
        robot_model.set_motor_speed("right", dps)
        
        self.logger.debug(f"Started moving forward at {self.speed}cm/s ({dps}°/s)")
        
    def step(self, robot_model, delta_time):
        """Update the command state."""
        if not self.started:
            self.start(robot_model)
            
        if self.finished:
            return True
            
        # Check how far we've moved
        state = robot_model.get_state()
        current_x = state['x']
        current_y = state['y']
        
        # Calculate distance moved
        dx = current_x - self.start_x
        dy = current_y - self.start_y
        self.distance_moved = math.sqrt(dx * dx + dy * dy)
        
        # Check if we've reached the target distance
        if self.distance_moved >= self.distance_cm:
            # Stop the robot
            robot_model.set_motor_speed("left", 0)
            robot_model.set_motor_speed("right", 0)
            self.finished = True
            self.logger.debug(f"Finished moving forward, moved {self.distance_moved:.2f}cm")
            return True
            
        return False
        
    def is_finished(self):
        """Check if the command has finished."""
        return self.finished

class Turn(AsyncCommand):
    """Command to turn the robot by a specified angle."""
    
    def __init__(self, angle_rad, speed=45.0):
        """
        Initialize the command.
        
        Args:
            angle_rad: The angle to turn in radians (positive for left, negative for right)
            speed: The angular speed in degrees per second
        """
        self.angle_rad = angle_rad
        self.speed_deg_per_sec = speed
        self.started = False
        self.finished = False
        self.start_angle = 0.0
        self.current_angle = 0.0
        self.angle_turned = 0.0
        self.logger = logging.getLogger("strategy.Turn")
        
    def start(self, robot_model):
        """Start turning."""
        self.started = True
        self.finished = False
        
        # Record starting angle
        state = robot_model.get_state()
        self.start_angle = state['yaw']
        self.current_angle = self.start_angle
        self.angle_turned = 0.0
        
        # Calculate motor speeds for turning
        # For turning, we need opposite motor directions
        wheel_base = robot_model.WHEEL_BASE_WIDTH
        wheel_radius = robot_model.WHEEL_RADIUS
        
        # Convert angular speed from deg/s to rad/s
        speed_rad_per_sec = math.radians(self.speed_deg_per_sec)
        
        # Calculate linear speed at each wheel needed for the desired angular speed
        # v = ω * r, where r is the distance from the center of rotation to the wheel
        linear_speed = speed_rad_per_sec * (wheel_base / 2)
        
        # Convert linear speed to degrees per second for the motors
        wheel_circumference = 2 * math.pi * wheel_radius
        degrees_per_cm = 360 / wheel_circumference
        motor_speed = linear_speed * degrees_per_cm
        
        # Set motor speeds with opposite signs for turning
        # Positive angle_rad means turn left (CCW), so left motor backward, right motor forward
        if self.angle_rad > 0:
            robot_model.set_motor_speed("left", -motor_speed)
            robot_model.set_motor_speed("right", motor_speed)
        else:
            robot_model.set_motor_speed("left", motor_speed)
            robot_model.set_motor_speed("right", -motor_speed)
            
        self.logger.debug(f"Started turning at {self.speed_deg_per_sec}°/s, target angle: {math.degrees(self.angle_rad):.2f}°")
        
    def step(self, robot_model, delta_time):
        """Update the command state."""
        if not self.started:
            self.start(robot_model)
            
        if self.finished:
            return True
            
        # Check how far we've turned
        state = robot_model.get_state()
        self.current_angle = state['yaw']
        
        # Calculate angle turned (accounting for wraparound)
        self.angle_turned = normalize_angle(self.current_angle - self.start_angle)
        
        # Check if we've reached the target angle
        # For positive angle_rad, we want angle_turned >= angle_rad
        # For negative angle_rad, we want angle_turned <= angle_rad
        target_reached = False
        if self.angle_rad > 0:
            target_reached = self.angle_turned >= self.angle_rad
        else:
            target_reached = self.angle_turned <= self.angle_rad
            
        if target_reached:
            # Stop the robot
            robot_model.set_motor_speed("left", 0)
            robot_model.set_motor_speed("right", 0)
            self.finished = True
            self.logger.debug(f"Finished turning, turned {math.degrees(self.angle_turned):.2f}°")
            return True
        
        return False
        
    def is_finished(self):
        """Check if the command has finished."""
        return self.finished

class Stop(AsyncCommand):
    """Command to immediately stop the robot."""
    
    def __init__(self):
        """Initialize the command."""
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Stop")
        
    def start(self, robot_model):
        """Stop the robot."""
        self.started = True
        
        # Set motor speeds to zero
        robot_model.set_motor_speed("left", 0)
        robot_model.set_motor_speed("right", 0)
        
        self.finished = True
        self.logger.debug("Robot stopped")
        
    def step(self, robot_model, delta_time):
        """Update the command state."""
        if not self.started:
            self.start(robot_model)
        return True
        
    def is_finished(self):
        """Check if the command has finished."""
        return self.finished

# --- Complex Movement Strategies ---

class PolygonStrategy(AsyncCommand):
    """
    Strategy to make the robot draw a polygon with a specified number of sides.
    """
    def __init__(self, sides, side_length, move_speed, turn_speed):
        """
        Initialize the strategy.
        
        Args:
            sides: Number of sides in the polygon
            side_length: Length of each side in cm
            move_speed: Speed to move at in cm/s
            turn_speed: Speed to turn at in degrees/s
        """
        self.sides = sides
        self.side_length = side_length
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.current_step = 0
        self.total_steps = sides * 2  # Each side requires a move and a turn
        self.current_command = None
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.PolygonStrategy")
        
    def start(self, robot_model):
        """Start the polygon drawing strategy."""
        self.started = True
        self.logger.info(f"Starting to draw a {self.sides}-sided polygon with sides of {self.side_length}cm")
        # Start with moving forward
        self._start_next_command(robot_model)
        
    def step(self, robot_model, delta_time):
        """Execute one step of the polygon drawing strategy."""
        if not self.started:
            self.start(robot_model)
            
        if self.finished:
            return True
            
        # Execute the current command
        if self.current_command and self.current_command.step(robot_model, delta_time):
            # Current command is finished, move to the next step
            self.current_step += 1
            
            if self.current_step >= self.total_steps:
                # We've completed the polygon
                self.finished = True
                self.logger.info("Completed drawing polygon")
                return True
                
            # Start the next command
            self._start_next_command(robot_model)
            
        return False
        
    def _start_next_command(self, robot_model):
        """
        Start the next command in the sequence.
        
        The sequence alternates between moving forward and turning.
        """
        if self.current_step % 2 == 0:
            # Even steps are moves
            self.current_command = MoveForward(self.side_length, self.move_speed)
            self.logger.debug(f"Starting side {(self.current_step // 2) + 1} of {self.sides}")
        else:
            # Odd steps are turns
            turn_angle = 2 * math.pi / self.sides
            self.current_command = Turn(turn_angle, self.turn_speed)
            self.logger.debug(f"Turning {math.degrees(turn_angle):.2f}° for corner {(self.current_step // 2) + 1}")
            
        self.current_command.start(robot_model)
            
    def is_finished(self):
        """Check if the polygon is complete."""
        return self.finished

class FollowBeaconStrategy(AsyncCommand):
    """
    Strategy to make the robot follow a beacon at specified coordinates.
    """
    def __init__(self, beacon_pos, distance_tolerance=5.0, angle_tolerance=0.1, 
                 move_speed=20.0, turn_speed=45.0):
        """
        Initialize the strategy.
        
        Args:
            beacon_pos: Tuple of (x, y) or (x, y, z) coordinates of the beacon
            distance_tolerance: How close to get to the beacon in cm
            angle_tolerance: How close to align with the beacon in radians
            move_speed: Speed to move at in cm/s
            turn_speed: Speed to turn at in degrees/s
        """
        self.beacon_pos = beacon_pos
        self.distance_tolerance = distance_tolerance
        self.angle_tolerance = angle_tolerance
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.current_command = None
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.FollowBeaconStrategy")
        
    def start(self, robot_model):
        """Start the beacon following strategy."""
        self.started = True
        
        # Log the beacon position (either 2D or 3D)
        if len(self.beacon_pos) == 3:
            self.logger.info(f"Starting to follow beacon at ({self.beacon_pos[0]:.2f}, {self.beacon_pos[1]:.2f}, {self.beacon_pos[2]:.2f})")
        else:
            self.logger.info(f"Starting to follow beacon at ({self.beacon_pos[0]:.2f}, {self.beacon_pos[1]:.2f})")
            
        # First, we need to turn toward the beacon
        self._update_navigation(robot_model)
        
    def step(self, robot_model, delta_time):
        """Execute one step of the beacon following strategy."""
        if not self.started:
            self.start(robot_model)
            
        if self.finished:
            return True
            
        # Execute the current command if we have one
        if self.current_command:
            if self.current_command.step(robot_model, delta_time):
                # Current command is finished, update navigation
                self.current_command = None
        
        # If we don't have a current command, update navigation
        if not self.current_command:
            self._update_navigation(robot_model)
            
        return self.finished
        
    def _update_navigation(self, robot_model):
        """
        Update the navigation based on the current position and the beacon position.
        
        This method calculates the distance and angle to the beacon and decides
        whether to turn or move forward.
        """
        state = robot_model.get_state()
        current_x = state['x']
        current_y = state['y']
        current_z = state.get('z', 0)  # Default to 0 if z not in state
        current_yaw = state['yaw']
        
        # Extract beacon coordinates
        beacon_x, beacon_y = self.beacon_pos[0], self.beacon_pos[1]
        beacon_z = self.beacon_pos[2] if len(self.beacon_pos) > 2 else 0
        
        # Calculate distance to beacon in 3D
        distance = math.sqrt(
            (beacon_x - current_x) ** 2 + 
            (beacon_y - current_y) ** 2 + 
            (beacon_z - current_z) ** 2
        )
        
        # Check if we've reached the beacon
        if distance <= self.distance_tolerance:
            self.logger.info(f"Reached beacon within tolerance ({distance:.2f}cm)")
            self.current_command = Stop()
            self.current_command.start(robot_model)
            self.finished = True
            return
            
        # Calculate angle to beacon in the XY plane
        angle_to_beacon = math.atan2(beacon_y - current_y, beacon_x - current_x)
        
        # Calculate the error in angle
        angle_error = normalize_angle(angle_to_beacon - current_yaw)
        
        # Check if we need to turn
        if abs(angle_error) > self.angle_tolerance:
            self.logger.debug(f"Turning to align with beacon, error: {math.degrees(angle_error):.2f}°")
            self.current_command = Turn(angle_error, self.turn_speed)
            self.current_command.start(robot_model)
        else:
            # We're aligned, move forward
            forward_distance = min(distance, 100)  # Limit maximum forward movement
            self.logger.debug(f"Moving forward {forward_distance:.2f}cm toward beacon")
            self.current_command = MoveForward(forward_distance, self.move_speed)
            self.current_command.start(robot_model)
            
    def is_finished(self):
        """Check if the beacon has been reached."""
        return self.finished

# --- Strategy Execution ---

class StrategyExecutor:
    """
    Executor for robot movement strategies.
    
    The executor runs robot movement strategies in a separate thread,
    allowing strategies to be executed asynchronously.
    """
    def __init__(self, robot_model):
        """
        Initialize the strategy executor.
        
        Args:
            robot_model: The robot model to control
        """
        self.robot_model = robot_model
        self.command = None
        self.command_thread = None
        self.stop_requested = False
        self.is_running_flag = False
        self.logger = logging.getLogger("StrategyExecutor")
        
    def execute(self, command):
        """
        Execute a strategy command.
        
        Args:
            command: The AsyncCommand to execute
        """
        # Stop any currently running command
        self.stop()
        
        # Set the new command
        self.command = command
        self.stop_requested = False
        
        # Start execution in a new thread
        self.command_thread = threading.Thread(target=self._execute_thread, daemon=True)
        self.command_thread.start()
        
    def stop(self):
        """Stop the currently executing command."""
        if self.is_running():
            self.logger.info("Stopping strategy execution")
            self.stop_requested = True
            
            # Wait for the thread to complete with a timeout
            if self.command_thread:
                self.command_thread.join(timeout=1.0)
                
            # Reset state
            self.command = None
            self.command_thread = None
            self.is_running_flag = False
        
    def is_running(self):
        """
        Check if a command is currently running.
        
        Returns:
            bool: True if a command is running, False otherwise
        """
        return self.is_running_flag
        
    def _execute_thread(self):
        """Thread function for executing a command."""
        if not self.command:
            return
            
        try:
            self.is_running_flag = True
            self.logger.info(f"Starting execution of {self.command.__class__.__name__}")
            
            # Start the command
            self.command.start(self.robot_model)
            
            # Main execution loop
            last_time = time.time()
            while not self.stop_requested and not self.command.is_finished():
                # Calculate delta time
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time
                
                # Execute a step of the command
                self.command.step(self.robot_model, delta_time)
        
                # Small sleep to avoid using too much CPU
                time.sleep(0.01)
                
            # Complete execution
            if self.stop_requested:
                self.logger.info("Strategy execution stopped by request")
            else:
                self.logger.info(f"Strategy {self.command.__class__.__name__} completed successfully")
                
        except Exception as e:
            self.logger.error(f"Error during strategy execution: {str(e)}", exc_info=True)
            
        finally:
            # Ensure we reset the running flag even if an exception occurs
            self.is_running_flag = False

# --- Strategy Management ---

class StrategyManager:
    """
    Manager for robot movement strategies.
    
    This class provides a high-level interface for creating and
    executing robot movement strategies, simplifying access to
    strategy functionality for other components.
    """
    def __init__(self, robot_model):
        """
        Initialize the strategy manager.
        
        Args:
            robot_model: The robot model to control
        """
        self.robot_model = robot_model
        self.strategy_executor = StrategyExecutor(robot_model)
        self.logger = logging.getLogger("StrategyManager")
        
    # Basic movement commands
    
    def move_forward(self, distance_cm, speed=20.0):
        """
        Move the robot forward by a specific distance.
        
        Args:
            distance_cm: The distance to move in centimeters
            speed: The speed to move at in cm/s
        """
        self.logger.info(f"Starting move forward: {distance_cm}cm at {speed}cm/s")
        command = MoveForward(distance_cm, speed)
        self.strategy_executor.execute(command)
        
    def turn(self, angle_degrees, speed=45.0):
        """
        Turn the robot by a specific angle.
        
        Args:
            angle_degrees: The angle to turn in degrees (positive for left, negative for right)
            speed: The angular speed in degrees per second
        """
        angle_rad = math.radians(angle_degrees)
        self.logger.info(f"Starting turn: {angle_degrees}° at {speed}°/s")
        command = Turn(angle_rad, speed)
        self.strategy_executor.execute(command)
        
    def stop(self):
        """Immediately stop the robot."""
        self.logger.info("Stopping robot")
        command = Stop()
        self.strategy_executor.execute(command)
        
    # Shape drawing commands
    
    def draw_polygon(self, sides, side_length=30.0, move_speed=20.0, turn_speed=45.0):
        """
        Make the robot draw a polygon with a specified number of sides.
        
        Args:
            sides: Number of sides in the polygon
            side_length: Length of each side in cm
            move_speed: Speed to move at in cm/s
            turn_speed: Speed to turn at in degrees/s
        """
        if sides < 3:
            self.logger.warning(f"Cannot draw polygon with {sides} sides. Minimum is 3.")
            return
            
        self.logger.info(f"Starting to draw {sides}-sided polygon with sides of {side_length}cm")
        command = PolygonStrategy(sides, side_length, move_speed, turn_speed)
        self.strategy_executor.execute(command)
        
    # Beacon following
    
    def follow_beacon(self, beacon_pos, distance_tolerance=5.0, angle_tolerance=0.1,
                      move_speed=20.0, turn_speed=45.0):
        """
        Make the robot follow a beacon at specified coordinates.
        
        Args:
            beacon_pos: Tuple of (x, y) or (x, y, z) coordinates of the beacon
            distance_tolerance: How close to get to the beacon in cm
            angle_tolerance: How close to align with the beacon in radians
            move_speed: Speed to move at in cm/s
            turn_speed: Speed to turn at in degrees/s
        """
        self.logger.info(f"Starting to follow beacon at coordinates: {beacon_pos}")
        command = FollowBeaconStrategy(
            beacon_pos, 
            distance_tolerance, 
            angle_tolerance,
            move_speed, 
            turn_speed
        )
        self.strategy_executor.execute(command)
        
    # Strategy control
    
    def stop_strategy(self):
        """Stop the currently executing strategy."""
        self.logger.info("Stopping current strategy")
        self.strategy_executor.stop()
        
    def is_strategy_running(self):
        """
        Check if a strategy is currently running.
        
        Returns:
            bool: True if a strategy is running, False otherwise
        """
        return self.strategy_executor.is_running() 