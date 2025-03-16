import time
import math
import logging
import threading
from utils.geometry import normalize_angle
from utils.geometry3d import normalize_angle_3d

class AsyncCommand:
    """
    Base interface for asynchronous robot commands.
    Each command is executed step by step in a non-blocking way.
    """
    def start(self, robot_model):
        """
        Initialize the command execution.
        
        Args:
            robot_model: The robot model to control
        """
        raise NotImplementedError
        
    def step(self, robot_model, delta_time):
        """
        Execute one step of the command.
        
        Args:
            robot_model: The robot model to control
            delta_time: The time elapsed since the last step
            
        Returns:
            bool: True if the command has finished executing, False otherwise
        """
        raise NotImplementedError
        
    def is_finished(self):
        """
        Check if the command has finished executing.
        
        Returns:
            bool: True if the command has finished, False otherwise
        """
        raise NotImplementedError
        
class Accelerate(AsyncCommand):
    """
    Command to gradually accelerate the robot to a target speed.
    """
    def __init__(self, target_speed, duration):
        """
        Initialize the command.
        
        Args:
            target_speed: The target speed to reach
            duration: The duration of the acceleration in seconds
        """
        self.target_speed = target_speed
        self.duration = duration
        self.elapsed = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Accelerate")
        
    def start(self, robot_model):
        """Start acceleration."""
        self.started = True
        self.logger.info(f"Starting acceleration to {self.target_speed} over {self.duration}s")
        
    def step(self, robot_model, delta_time):
        """Execute one step of acceleration."""
        if not self.started:
            self.start(robot_model)
            
        self.elapsed += delta_time
        fraction = min(self.elapsed / self.duration, 1.0)
        speed = self.target_speed * fraction
        
        robot_model.set_motor_speed("left", speed)
        robot_model.set_motor_speed("right", speed)
        
        if self.elapsed >= self.duration:
            self.finished = True
            self.logger.info("Acceleration completed")
            
        return self.finished
        
    def is_finished(self):
        """Check if acceleration is complete."""
        return self.finished
        
class Decelerate(AsyncCommand):
    """
    Command to gradually decelerate the robot to a stop.
    """
    def __init__(self, current_speed, duration):
        """
        Initialize the command.
        
        Args:
            current_speed: The current speed of the robot
            duration: The duration of the deceleration in seconds
        """
        self.current_speed = current_speed
        self.duration = duration
        self.elapsed = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Decelerate")
        
    def start(self, robot_model):
        """Start deceleration."""
        self.started = True
        self.logger.info(f"Starting deceleration from {self.current_speed} over {self.duration}s")
        
    def step(self, robot_model, delta_time):
        """Execute one step of deceleration."""
        if not self.started:
            self.start(robot_model)
            
        self.elapsed += delta_time
        fraction = max(1.0 - self.elapsed / self.duration, 0.0)
        speed = self.current_speed * fraction
        
        robot_model.set_motor_speed("left", speed)
        robot_model.set_motor_speed("right", speed)
        
        if self.elapsed >= self.duration:
            robot_model.set_motor_speed("left", 0)
            robot_model.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Deceleration completed")
            
        return self.finished
        
    def is_finished(self):
        """Check if deceleration is complete."""
        return self.finished
        
class MoveForward(AsyncCommand):
    """
    Command to move the robot forward by a specific distance.
    """
    def __init__(self, distance_cm, speed):
        """
        Initialize the command.
        
        Args:
            distance_cm: The distance to move in centimeters
            speed: The speed to move at
        """
        self.distance_cm = distance_cm
        self.speed = speed
        self.started = False
        self.finished = False
        self.start_x = None
        self.start_y = None
        self.start_z = None
        self.logger = logging.getLogger("strategy.MoveForward")
        
    def start(self, robot_model):
        """Start moving forward."""
        state = robot_model.get_state()
        self.start_x = state['x']
        self.start_y = state['y']
        self.start_z = state['z']
        
        robot_model.set_motor_speed("left", self.speed)
        robot_model.set_motor_speed("right", self.speed)
        
        self.started = True
        self.logger.info(f"Starting to move forward {self.distance_cm}cm at speed {self.speed}")
        
    def step(self, robot_model, delta_time):
        """Execute one step of moving forward."""
        if not self.started:
            self.start(robot_model)
            
        state = robot_model.get_state()
        current_x = state['x']
        current_y = state['y']
        current_z = state['z']
        
        # Calculate the 3D distance traveled
        distance_traveled = math.sqrt(
            (current_x - self.start_x) ** 2 + 
            (current_y - self.start_y) ** 2 + 
            (current_z - self.start_z) ** 2
        )
        
        if distance_traveled >= self.distance_cm:
            robot_model.set_motor_speed("left", 0)
            robot_model.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Completed moving forward {distance_traveled:.2f}cm")
            
        return self.finished
        
    def is_finished(self):
        """Check if movement is complete."""
        return self.finished

class Turn(AsyncCommand):
    """
    Command to turn the robot by a specific angle.
    """
    def __init__(self, angle_rad, angular_speed_deg_s):
        """
        Initialize the command.
        
        Args:
            angle_rad: The angle to turn in radians
            angular_speed_deg_s: The angular speed in degrees per second
        """
        self.angle_rad = angle_rad
        self.angular_speed_deg_s = angular_speed_deg_s
        self.started = False
        self.finished = False
        self.target_angle = None
        self.logger = logging.getLogger("strategy.Turn")
        
    def start(self, robot_model):
        """Start turning."""
        state = robot_model.get_state()
        current_yaw = state['yaw']
        self.target_angle = normalize_angle(current_yaw + self.angle_rad)
        
        self.started = True
        self.logger.info(f"Starting to turn {math.degrees(self.angle_rad):.2f}° at {self.angular_speed_deg_s}°/s")
        
    def step(self, robot_model, delta_time):
        """Execute one step of turning."""
        if not self.started:
            self.start(robot_model)
            
        state = robot_model.get_state()
        current_yaw = state['yaw']
        
        # Calculate the error (difference between target and current angle)
        error = normalize_angle(self.target_angle - current_yaw)
        
        # Check if we're close enough to the target angle
        if abs(error) < math.radians(0.5):  # 0.5 degree tolerance
            robot_model.set_motor_speed("left", 0)
            robot_model.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Completed turning")
            return True
        
        # Calculate proportional control
        Kp = 5.0  # Proportional gain
        turn_speed = Kp * math.degrees(error)
        
        # Limit the turning speed
        turn_speed = max(-self.angular_speed_deg_s, min(self.angular_speed_deg_s, turn_speed))
        
        # Set motor speeds for turning
        robot_model.set_motor_speed("left", -turn_speed)
        robot_model.set_motor_speed("right", turn_speed)
        
        return False
        
    def is_finished(self):
        """Check if turning is complete."""
        return self.finished

class Stop(AsyncCommand):
    """
    Command to immediately stop the robot.
    """
    def __init__(self):
        """Initialize the command."""
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Stop")
        
    def start(self, robot_model):
        """Start stopping."""
        robot_model.set_motor_speed("left", 0)
        robot_model.set_motor_speed("right", 0)
        
        self.started = True
        self.finished = True
        self.logger.info("Robot stopped")
        
    def step(self, robot_model, delta_time):
        """Execute one step of stopping."""
        if not self.started:
            self.start(robot_model)
            
        return True
        
    def is_finished(self):
        """Check if stopping is complete."""
        return self.finished

class PolygonStrategy(AsyncCommand):
    """
    Strategy to draw a regular polygon.
    """
    def __init__(self, sides, side_length_cm, movement_speed, turning_speed):
        """
        Initialize the strategy.
        
        Args:
            sides: The number of sides of the polygon
            side_length_cm: The length of each side in centimeters
            movement_speed: The speed to move at
            turning_speed: The speed to turn at in degrees per second
        """
        if sides < 3:
            raise ValueError("A polygon must have at least 3 sides")
            
        self.sides = sides
        self.side_length = side_length_cm
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed
        
        # Calculate the turning angle for a regular polygon
        self.turning_angle = 2 * math.pi / sides
        
        # Create the sequence of commands
        self.commands = []
        for i in range(sides):
            self.commands.append(MoveForward(side_length_cm, movement_speed))
            self.commands.append(Turn(self.turning_angle, turning_speed))
            
        # Add a final stop command
        self.commands.append(Stop())
        
        self.current_command_index = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.PolygonStrategy")
        
    def start(self, robot_model):
        """Start executing the polygon strategy."""
        if len(self.commands) > 0:
            self.commands[0].start(robot_model)
            
        self.started = True
        self.logger.info(f"Starting to draw a {self.sides}-sided polygon with side length {self.side_length}cm")
        
    def step(self, robot_model, delta_time):
        """Execute one step of the polygon strategy."""
        if not self.started:
            self.start(robot_model)
            
        # If all commands have been executed, we're done
        if self.current_command_index >= len(self.commands):
            self.finished = True
            return True
            
        # Get the current command
        current_command = self.commands[self.current_command_index]
        
        # Execute one step of the current command
        command_finished = current_command.step(robot_model, delta_time)
        
        # If the current command is finished, move to the next one
        if command_finished:
            self.current_command_index += 1
            self.logger.info(f"Completed command {self.current_command_index}/{len(self.commands)}")
            
            # If there are more commands, start the next one
            if self.current_command_index < len(self.commands):
                next_command = self.commands[self.current_command_index]
                next_command.start(robot_model)
            else:
                self.finished = True
                self.logger.info("Polygon drawing completed")
                
        return self.finished
        
    def is_finished(self):
        """Check if the polygon strategy is complete."""
        return self.finished

class StrategyExecutor:
    """
    Class to execute a strategy in a separate thread.
    """
    def __init__(self, simulation_controller):
        """
        Initialize the executor.
        
        Args:
            simulation_controller: The simulation controller to use
        """
        self.simulation_controller = simulation_controller
        self.robot_model = simulation_controller.robot_model
        self.current_strategy = None
        self.strategy_thread = None
        self.running = False
        self.delta_time = 0.02  # 50Hz update rate
        self.logger = logging.getLogger("strategy.Executor")
        
    def execute_strategy(self, strategy):
        """
        Execute a strategy.
        
        Args:
            strategy: The strategy to execute
        """
        # Stop any running strategy
        self.stop()
        
        # Set the new strategy
        self.current_strategy = strategy
        
        # Start the strategy thread
        self.running = True
        self.strategy_thread = threading.Thread(target=self._strategy_loop, daemon=True)
        self.strategy_thread.start()
        
        self.logger.info(f"Started executing strategy: {strategy.__class__.__name__}")
        
    def _strategy_loop(self):
        """Main loop for executing the strategy."""
        if self.current_strategy is None:
            self.logger.error("No strategy to execute")
            return
            
        # Start the strategy
        self.current_strategy.start(self.robot_model)
        
        # Execute the strategy step by step until it's finished or stopped
        while self.running:
            if self.current_strategy.is_finished():
                break
                
            self.current_strategy.step(self.robot_model, self.delta_time)
            time.sleep(self.delta_time)
            
        self.logger.info("Strategy execution completed")
        
    def stop(self):
        """Stop the current strategy."""
        if self.running:
            self.running = False
            
            if self.strategy_thread and self.strategy_thread.is_alive():
                self.strategy_thread.join(timeout=1.0)
                
            # Stop the robot
            self.robot_model.set_motor_speed("left", 0)
            self.robot_model.set_motor_speed("right", 0)
            
            self.logger.info("Strategy execution stopped")
            
    def is_running(self):
        """Check if a strategy is running."""
        return self.running and self.strategy_thread and self.strategy_thread.is_alive()

class FollowBeaconStrategy(AsyncCommand):
    """
    Strategy to make the robot follow a beacon (end position).
    The robot will orient itself towards the beacon and move towards it.
    """
    def __init__(self, distance_tolerance=10, angle_tolerance=0.2, movement_speed=100, turning_speed=45):
        """
        Initialize the strategy.
        
        Args:
            distance_tolerance: The distance (in cm) at which the robot is considered to have reached the beacon
            angle_tolerance: The angle (in radians) at which the robot is considered to be facing the beacon
            movement_speed: The speed at which the robot moves towards the beacon
            turning_speed: The speed at which the robot turns towards the beacon (degrees per second)
        """
        self.distance_tolerance = distance_tolerance
        self.angle_tolerance = angle_tolerance  # Increased from 0.1 to 0.2 radians (about 11 degrees)
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed
        self.started = False
        self.finished = False
        self.current_command = None
        self.logger = logging.getLogger("strategy.FollowBeaconStrategy")
        self.last_beacon_pos = None  # Track the last beacon position to detect changes
        self.waiting_for_beacon_change = False  # Flag to indicate waiting for a new beacon position
        self.last_position = None  # Track last position to detect collisions
        self.collision_count = 0  # Counter for potential collisions
        
    def start(self, robot_model):
        """Start following the beacon."""
        self.started = True
        # Initialize the last beacon position
        self.last_beacon_pos = robot_model.map_model.end_position
        self.last_position = (robot_model.x, robot_model.y)
        self.waiting_for_beacon_change = False
        self.collision_count = 0
        self.logger.info("Started following beacon")
        
    def reset_state(self):
        """Reset the waiting state to follow a new beacon."""
        self.waiting_for_beacon_change = False
        self.collision_count = 0
        self.logger.info("Reset state to follow new beacon")
        
    def step(self, robot_model, delta_time):
        """Execute one step of following the beacon."""
        if not self.started:
            self.start(robot_model)
            
        # Get the current state
        state = robot_model.get_state()
        x, y, z = state['x'], state['y'], state['z']
        yaw = state['yaw']
        
        # Detect collision (robot not moving despite motors running)
        current_position = (x, y)
        if self.last_position:
            position_diff = math.sqrt((current_position[0] - self.last_position[0])**2 + 
                                     (current_position[1] - self.last_position[1])**2)
            if position_diff < 0.1 and not self.waiting_for_beacon_change:
                self.collision_count += 1
                if self.collision_count > 20:  # If stuck for several frames
                    self.logger.warning("Potential collision detected, resetting direction")
                    # Try to move away from obstacle
                    robot_model.set_motor_speed("left", -30)  # Reverse slightly
                    robot_model.set_motor_speed("right", -30)
                    self.collision_count = 0  # Reset counter
                    return False
            else:
                self.collision_count = 0  # Reset if moving
        
        # Update last position
        self.last_position = current_position
        
        # Get the beacon position - check on every step for immediate changes
        beacon_pos = robot_model.map_model.end_position
        
        # If no beacon is set, wait in position 
        if beacon_pos is None:
            if not self.waiting_for_beacon_change:
                self.logger.info("No beacon position set, waiting for beacon")
                robot_model.set_motor_speed("left", 0)
                robot_model.set_motor_speed("right", 0)
                self.waiting_for_beacon_change = True
            return False  # Stay in the strategy but do nothing
            
        # Check if the beacon position has changed or we were waiting
        if self.last_beacon_pos != beacon_pos or self.waiting_for_beacon_change:
            self.logger.info(f"Beacon position changed to {beacon_pos}, resuming movement")
            self.last_beacon_pos = beacon_pos
            self.waiting_for_beacon_change = False
            self.collision_count = 0
        
        # Handle 3D or 2D beacon position
        if len(beacon_pos) == 3:
            beacon_x, beacon_y, beacon_z = beacon_pos
        else:
            beacon_x, beacon_y = beacon_pos
            beacon_z = 0  # Assume beacon is at ground level
        
        # Calculate distance to beacon
        dx = beacon_x - x
        dy = beacon_y - y
        dz = beacon_z - z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # If we've reached the beacon, wait for a new beacon
        if distance <= self.distance_tolerance:
            robot_model.set_motor_speed("left", 0)
            robot_model.set_motor_speed("right", 0)
            
            if not self.waiting_for_beacon_change:
                self.logger.info(f"Reached beacon at ({beacon_x:.2f}, {beacon_y:.2f}, {beacon_z:.2f}), waiting for new position")
                self.waiting_for_beacon_change = True
                
            return False  # Don't finish the strategy, keep waiting for a new beacon
            
        # If we're waiting for a beacon change but haven't reached it yet 
        # (this handles the case where a new beacon was set while waiting)
        if self.waiting_for_beacon_change:
            self.waiting_for_beacon_change = False
            self.logger.info(f"Resuming movement to beacon at ({beacon_x:.2f}, {beacon_y:.2f})")
            
        # Calculate target angle to beacon (in 2D for simplicity)
        target_angle = math.atan2(dy, dx)
        
        # Calculate the difference between the current angle and the target angle
        angle_diff = normalize_angle(target_angle - yaw)
        
        # Use a combined approach: turn and move at the same time with different speeds
        # This prevents the robot from getting stuck in a perpetual turning loop
        
        # Calculate turn component based on angle difference
        # Use a proportional control with gain of 0.8 (this is a tuning parameter)
        turn_factor = min(1.0, abs(angle_diff) / math.pi)  # Normalized from 0 to 1
        turn_speed = self.turning_speed * turn_factor * 0.8
        
        # Calculate forward movement component
        # Move faster when facing the target, slower when turning sharply
        forward_factor = 1.0 - min(0.8, turn_factor)  # Higher when more aligned
        forward_speed = self.movement_speed * forward_factor
        
        # Apply motor speeds with differential steering
        if angle_diff > 0:  # Need to turn left
            robot_model.set_motor_speed("left", forward_speed - turn_speed)
            robot_model.set_motor_speed("right", forward_speed + turn_speed)
        else:  # Need to turn right
            robot_model.set_motor_speed("left", forward_speed + turn_speed)
            robot_model.set_motor_speed("right", forward_speed - turn_speed)
        
        # Log movement data
        self.logger.info(
            f"Moving toward beacon at ({beacon_x:.2f}, {beacon_y:.2f}), " +
            f"distance: {distance:.2f}cm, " +
            f"angle diff: {math.degrees(angle_diff):.2f}°, " +
            f"forward: {forward_speed:.2f}, turn: {turn_speed:.2f}"
        )
            
        return False  # Never finish the strategy, always keep waiting for beacon changes
        
    def is_finished(self):
        """Check if we've reached the beacon."""
        return False  # Never finish - the strategy stays active to react to new beacon positions 