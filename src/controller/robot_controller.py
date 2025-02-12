from model.robot import Robot
from view.robot_view import RobotView
from view.control_panel import ControlPanel
SPEED_STEP = 30  # How much speed to add/remove per key press

class RobotController:
    def __init__(self, robot: Robot, robot_view: RobotView, control_panel: ControlPanel, window):
        """Initializes the RobotController with references to the robot, its view, the control panel, and the window."""
        self.robot = robot
        self.robot_view = robot_view
        self.control_panel = control_panel
        self.window = window  # Store the window object
        self.robot.add_event_listener(self.handle_robot_event)

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


    def increase_speed(self):
        """ Increases speed for both wheels """
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] + SPEED_STEP)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] + SPEED_STEP)

    def decrease_speed(self):
        """ Decreases speed for both wheels """
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] - SPEED_STEP)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] - SPEED_STEP)

    def increase_left_speed(self):
        """ 增加左轮速度 """
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] + SPEED_STEP)

    def decrease_left_speed(self):
        """ 减少左轮速度 """
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] - SPEED_STEP)

    def increase_right_speed(self):
        """ 增加右轮速度 """
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] + SPEED_STEP)

    def decrease_right_speed(self):
        """ 减少右轮速度 """
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] - SPEED_STEP)
    
    def stop_rotation(self):
        """ 松开旋转按键后，立即停止旋转，但仿真继续运行 """
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 0)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 0)

