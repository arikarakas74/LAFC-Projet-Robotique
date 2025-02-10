import math
import threading
from model.map_model import MapModel

class Robot:
    WHEEL_BASE_WIDTH = 10.0  # cm (Distance between the wheels)
    WHEEL_DIAMETER = 5.0  # cm (Wheel diameter)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2  # cm (Wheel radius)
    
    MOTOR_LEFT = "left"
    MOTOR_RIGHT = "right"
    TICK_DURATION = 0.05  # 50 ms tick duration (matching simulation tick)
    
    def __init__(self, map_model):
        self.map_model = map_model
        self.motor_speeds = {self.MOTOR_LEFT: 0, self.MOTOR_RIGHT: 0}  # Motor speeds (dps)
        self.motor_positions = {self.MOTOR_LEFT: 0, self.MOTOR_RIGHT: 0}  # Motor angles (degrees)
        self.event_listeners = []  # List of event listeners
        self.stop_event = threading.Event()
        self.moving = False  # Movement status

    
    def add_event_listener(self, listener):
        """ Adds an event listener to the robot """
        self.event_listeners.append(listener)
    
    def trigger_event(self, event_type, **kwargs):
        """ Triggers an event and notifies all listeners with validation """
        valid_events = {"update_view", "update_speed_label"}
        if event_type not in valid_events:
            raise ValueError(f"Invalid event type: {event_type}")
        for listener in self.event_listeners:
            listener(event_type, **kwargs)
    
    def set_motor_dps(self, port, dps):
        """ Set the speed (degrees per second) for the specified motor(s) """
        if port in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            self.motor_speeds[port] = dps
        elif port == self.MOTOR_LEFT + self.MOTOR_RIGHT:
            self.motor_speeds[self.MOTOR_LEFT] = dps
            self.motor_speeds[self.MOTOR_RIGHT] = dps
        # Start movement if speed is set
        if dps != 0:
            self.start_movement()
        else:
            self.moving = False  # Stop movement if speed is zero

        self.trigger_event("update_speed_label", velocity=dps, direction_angle=self.map_model.robot_theta)

    def start_movement(self):
        """ Starts the simulation loop if not already running """
        if not self.moving:
            self.moving = True
            threading.Thread(target=self.update_simulation, daemon=True).start()

    
    def update_motors(self, tick):
        """ Updates the motor positions based on speed and tick duration with bounds checking """
        for motor in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            new_position = self.motor_positions[motor] + self.motor_speeds[motor] * tick
            self.motor_positions[motor] = max(-360, min(360, new_position))  # Clamping values within realistic bounds

    def normalize_angle(self, angle):
        """ Normalizes an angle to the range [-pi, pi] """
        return (angle + math.pi) % (2 * math.pi) - math.pi
    
    def update_simulation(self):
        """ Updates robot movement in the simulation loop """
        while self.moving and not self.stop_event.is_set():
            left_speed = self.motor_speeds[self.MOTOR_LEFT]  # Left motor speed (dps)
            right_speed = self.motor_speeds[self.MOTOR_RIGHT]  # Right motor speed (dps)
            
            # Compute wheel linear velocities (cm/s)
            left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
            right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
            
            # Compute linear and angular velocity
            linear_velocity = (left_velocity + right_velocity) / 2  # cm/s
            angular_velocity = (right_velocity - left_velocity) / self.WHEEL_BASE_WIDTH  # rad/s
            
            # Update position using kinematic model
            if angular_velocity == 0:
                # Moving straight
                self.map_model.robot_x += linear_velocity * math.cos(self.map_model.robot_theta)
                self.map_model.robot_y += linear_velocity * math.sin(self.map_model.robot_theta)
            else:
                # Moving in an arc
                radius = linear_velocity / angular_velocity
                delta_theta = angular_velocity * self.TICK_DURATION
                
                self.map_model.robot_x += radius * (math.sin(self.map_model.robot_theta + delta_theta) - math.sin(self.map_model.robot_theta))
                self.map_model.robot_y += radius * (-math.cos(self.map_model.robot_theta + delta_theta) + math.cos(self.map_model.robot_theta))
                self.map_model.robot_theta += delta_theta  # Update orientation
            
            # Normalize angle
            self.map_model.robot_theta = self.normalize_angle(self.map_model.robot_theta)
            
            # Update motor positions
            self.update_motors(self.TICK_DURATION)
            
            # Trigger view update event with validation
            self.trigger_event("update_view", x=self.map_model.robot_x, y=self.map_model.robot_y, direction_angle=self.map_model.robot_theta)
            
            # Use non-blocking event waiting instead of time.sleep
            self.stop_event.wait(self.TICK_DURATION)

    def stop_simulation(self):
        """ Stops the simulation loop """
        self.stop_event.set()
        self.moving = False
    
    def get_position(self):
        """ Returns the current position of the robot """
        return self.map_model.robot_x, self.map_model.robot_y, self.map_model.robot_theta
    
    def get_motor_position(self):
        """ Returns the current motor positions (degrees) """
        return self.motor_positions[self.MOTOR_LEFT], self.motor_positions[self.MOTOR_RIGHT]
    
    def offset_motor_encoder(self, port, offset):
        """ Resets the motor encoder by subtracting the given offset """
        if port in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            self.motor_positions[port] -= offset
