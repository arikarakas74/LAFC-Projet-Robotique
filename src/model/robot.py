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

        left_speed = self.motor_speeds[self.MOTOR_LEFT]
        right_speed = self.motor_speeds[self.MOTOR_RIGHT]


        if left_speed == 0 and right_speed == 0:
            self.moving = False  
        else:
            self.moving = True
            self.start_movement() 

        self.trigger_event("update_speed_label", left_speed=left_speed, right_speed=right_speed, direction_angle=0)

    def update_motors(self, tick):
        """ Updates the motor positions based on speed and tick duration with bounds checking """
        for motor in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            new_position = self.motor_positions[motor] + self.motor_speeds[motor] * tick
            self.motor_positions[motor] = max(-360, min(360, new_position))  # Clamping values within realistic bounds

    def normalize_angle(self, angle):
        """ Normalizes an angle to the range [-pi, pi] """
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle




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

    def get_motor_speed(self):
        """Returns the current motor speeds (degrees per second)"""
        return self.motor_speeds[self.MOTOR_LEFT], self.motor_speeds[self.MOTOR_RIGHT]
    def start_movement(self):
        """Start the robot simulation and let it begin moving."""
        if not self.moving:
            self.moving = True
            self.stop_event.clear()
            threading.Thread(target=self.update_simulation, daemon=True).start()

    def update_simulation(self):
        """Simulation loop to update the robot's state."""
        while not self.stop_event.is_set():
            self.update_motors(self.TICK_DURATION)
            # Simulate other behaviors (e.g., collision detection, position tracking)
            threading.Event().wait(self.TICK_DURATION)  # Wait for the next tick
    


