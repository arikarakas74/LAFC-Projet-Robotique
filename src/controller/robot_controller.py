import math
import threading
import numpy as np


class RobotController:
    """Controller for robot movement in 3D space."""
    
    SPEED_STEP = 30.0
    
    def __init__(self, robot_model, map_model, cli_mode=False):
        """
        Initializes the robot controller.
        
        Args:
            robot_model: The robot model to control
            map_model: The map model for environment data
            cli_mode: Whether the controller is running in CLI mode
        """
        self.robot_model = robot_model
        self.map_model = map_model

        # Start the input thread only in CLI mode
        if cli_mode:
            self._start_input_thread()

    def _start_input_thread(self):
        """Starts a separate thread for keyboard input in CLI mode."""
        threading.Thread(target=self._read_input, daemon=True).start()

    def _read_input(self):
        """Continuously reads and processes keyboard input in CLI mode."""
        while True:
            key = input("Press a key (q/a/e/d/w/s/r/f/arrows): ").strip().lower()
            if key == 'q':
                self.increase_left_speed()
            elif key == 'a':
                self.decrease_left_speed()
            elif key == 'e':
                self.increase_right_speed()
            elif key == 'd':
                self.decrease_right_speed()
            elif key == 'w':
                self.move_forward()
            elif key == 's':
                self.move_backward()
            elif key == 'r':  # Raise (increase Z)
                self.move_up()
            elif key == 'f':  # Fall (decrease Z)
                self.move_down()
            elif key == 'up':
                self.pitch_up()
            elif key == 'down':
                self.pitch_down()
            elif key == 'left':
                self.roll_left()
            elif key == 'right':
                self.roll_right()

    def stop(self):
        """Stops all motor movement."""
        self.robot_model.set_motor_speed("left", 0)
        self.robot_model.set_motor_speed("right", 0)

    def increase_left_speed(self):
        """Increases the speed of the left motor."""
        new_speed = self.robot_model.motor_speeds["left"] + self.SPEED_STEP
        self.robot_model.set_motor_speed("left", new_speed)

    def decrease_left_speed(self):
        """Decreases the speed of the left motor."""
        new_speed = self.robot_model.motor_speeds["left"] - self.SPEED_STEP
        self.robot_model.set_motor_speed("left", new_speed)

    def increase_right_speed(self):
        """Increases the speed of the right motor."""
        new_speed = self.robot_model.motor_speeds["right"] + self.SPEED_STEP
        self.robot_model.set_motor_speed("right", new_speed)

    def decrease_right_speed(self):
        """Decreases the speed of the right motor."""
        new_speed = self.robot_model.motor_speeds["right"] - self.SPEED_STEP
        self.robot_model.set_motor_speed("right", new_speed)

    def move_forward(self):
        """Moves the robot forward by increasing both motor speeds."""
        self.robot_model.set_motor_speed("left", self.robot_model.motor_speeds["left"] + self.SPEED_STEP)
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] + self.SPEED_STEP)

    def move_backward(self):
        """Moves the robot backward by decreasing both motor speeds."""
        self.robot_model.set_motor_speed("left", self.robot_model.motor_speeds["left"] - self.SPEED_STEP)
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] - self.SPEED_STEP)
        
    # 3D-specific movement methods
        
    def move_up(self):
        """Moves the robot upward in 3D space."""
        # In a real robot, this might control propellers, jump mechanism, etc.
        # Here we directly modify the z-coordinate for demonstration
        new_z = self.robot_model.z + 5.0
        self.robot_model.update_position(
            self.robot_model.x, 
            self.robot_model.y, 
            new_z,
            self.robot_model.pitch,
            self.robot_model.yaw,
            self.robot_model.roll
        )
        
    def move_down(self):
        """Moves the robot downward in 3D space."""
        new_z = max(0, self.robot_model.z - 5.0)  # Don't go below ground
        self.robot_model.update_position(
            self.robot_model.x, 
            self.robot_model.y, 
            new_z,
            self.robot_model.pitch,
            self.robot_model.yaw,
            self.robot_model.roll
        )
        
    def pitch_up(self):
        """Rotates the robot up around the X-axis."""
        new_pitch = self.robot_model.pitch + math.radians(5.0)
        self.robot_model.update_position(
            self.robot_model.x, 
            self.robot_model.y, 
            self.robot_model.z,
            new_pitch,
            self.robot_model.yaw,
            self.robot_model.roll
        )
        
    def pitch_down(self):
        """Rotates the robot down around the X-axis."""
        new_pitch = self.robot_model.pitch - math.radians(5.0)
        self.robot_model.update_position(
            self.robot_model.x, 
            self.robot_model.y, 
            self.robot_model.z,
            new_pitch,
            self.robot_model.yaw,
            self.robot_model.roll
        )
        
    def roll_left(self):
        """Rotates the robot left around the Z-axis."""
        new_roll = self.robot_model.roll + math.radians(5.0)
        self.robot_model.update_position(
            self.robot_model.x, 
            self.robot_model.y, 
            self.robot_model.z,
            self.robot_model.pitch,
            self.robot_model.yaw,
            new_roll
        )
        
    def roll_right(self):
        """Rotates the robot right around the Z-axis."""
        new_roll = self.robot_model.roll - math.radians(5.0)
        self.robot_model.update_position(
            self.robot_model.x, 
            self.robot_model.y, 
            self.robot_model.z,
            self.robot_model.pitch,
            self.robot_model.yaw,
            new_roll
        )
