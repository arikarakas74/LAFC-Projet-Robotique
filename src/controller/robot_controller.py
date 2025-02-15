from model.robot import Robot
from view.robot_view import RobotView
from view.control_panel import ControlPanel
from model.map_model import MapModel
SPEED_STEP = 30  # How much speed to add/remove per key press
import math
import threading

class RobotController:
    WHEEL_BASE_WIDTH = 10.0  # cm (Distance between the wheels)
    WHEEL_DIAMETER = 5.0  # cm (Wheel diameter)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2  # cm (Wheel radius)
    
    MOTOR_LEFT = "left"
    MOTOR_RIGHT = "right"
    TICK_DURATION = 0.05  # 50 ms tick duration (matching simulation tick)
    def __init__(self, robot: Robot, robot_view: RobotView, control_panel: ControlPanel, window,map_model: MapModel):
        """Initializes the RobotController with references to the robot, its view, the control panel, and the window."""
        self.robot = robot
        self.robot_view = robot_view
        self.control_panel = control_panel
        self.window = window  # Store the window object
        self.running = True
        self.robot.add_event_listener(self.handle_robot_event)
        self.map_model=map_model
        self._start_observer_thread()
        

    def handle_robot_event(self, event_type, **kwargs):
        """Handles events from the robot."""
        if event_type == "update_view":
            self.robot_view.draw(kwargs["x"], kwargs["y"], kwargs["direction_angle"])
        elif event_type == "update_speed_label":
            left_speed = kwargs.get("left_speed", 0)
            right_speed = kwargs.get("right_speed", 0)
            direction_angle = kwargs.get("direction_angle", 0)
            self.control_panel.update_speed_label(left_speed, right_speed, direction_angle)
        elif event_type == "after":
            callback = kwargs.get("callback")
            if callable(callback):
                return self.window.after(kwargs["delay"], callback, kwargs.get("obstacles", []), kwargs.get("goal_position", None))


    def _start_observer_thread(self):
        def observer_loop():
            while self.running:
                self.update_simulation()
                threading.Event().wait(self.TICK_DURATION)
        threading.Thread(target=observer_loop, daemon=True).start()
    def update_simulation(self):
        """ Updates robot movement in the simulation loop """
        while True:
            left_speed = self.robot.motor_speeds.get(self.MOTOR_LEFT, 0) 
            right_speed = self.robot.motor_speeds.get(self.MOTOR_RIGHT, 0)

            if left_speed == 0 and right_speed == 0:
                self.robot.stop_event.wait(self.TICK_DURATION)
                continue 

            left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
            right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

            linear_velocity = (left_velocity + right_velocity) / 2
            angular_velocity = (right_velocity - left_velocity) / self.WHEEL_BASE_WIDTH
            
            if left_speed == -right_speed and left_speed != 0:
                self.map_model.robot_theta += angular_velocity * self.TICK_DURATION
                linear_velocity = 0  

            if (left_speed == 0 and right_speed != 0) or (left_speed != 0 and right_speed == 0):
                if left_speed == 0:
                    angular_velocity = right_velocity / (self.WHEEL_BASE_WIDTH / 2)
                else:
                    angular_velocity = -left_velocity / (self.WHEEL_BASE_WIDTH / 2)

                self.map_model.robot_theta += angular_velocity * self.TICK_DURATION
                linear_velocity = 0  # Pas de déplacement linéaire
   
            else:
                new_x = self.map_model.robot_x + linear_velocity * math.cos(self.map_model.robot_theta)
                new_y = self.map_model.robot_y + linear_velocity * math.sin(self.map_model.robot_theta)

                if self.map_model.is_collision(new_x, new_y) or self.map_model.is_out_of_bounds(new_x, new_y):
                    self.robot.motor_speeds[self.MOTOR_LEFT] = 0
                    self.robot.motor_speeds[self.MOTOR_RIGHT] = 0
                else:
                    self.map_model.robot_x = new_x
                    self.map_model.robot_y = new_y

                self.map_model.robot_theta += angular_velocity * self.TICK_DURATION
                    
            self.map_model.robot_theta = self.robot.normalize_angle(self.map_model.robot_theta)

            self.robot.trigger_event("update_view", x=self.map_model.robot_x, y=self.map_model.robot_y, direction_angle=self.map_model.robot_theta)

            self.robot.stop_event.wait(self.TICK_DURATION)


    def increase_left_speed(self):
        """Reduce the left wheel speed (turn right)"""
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] + SPEED_STEP)  

    def decrease_left_speed(self):
        """Increase the left wheel speed (turn left)"""

        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] - SPEED_STEP) 

    def increase_right_speed(self):
        """Reduce the right wheel speed (turn left)"""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] + SPEED_STEP)  
    def decrease_right_speed(self):
        """Increase the right wheel speed (turn right)"""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] - SPEED_STEP)  
    
    def stop_rotation(self):
        """Release the rotation key to immediately stop rotating, but the simulation continues running."""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 0)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 0)

