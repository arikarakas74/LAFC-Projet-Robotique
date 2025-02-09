from model.robot import Robot
from view.robot_view import RobotView
from view.control_panel import ControlPanel

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
            velocity = kwargs.get("velocity", 0)
            direction_angle = kwargs.get("direction_angle", 0)
            self.control_panel.update_speed_label(velocity, direction_angle)
        elif event_type == "robot_stopped":
            self.robot.stop_simulation()
            self.robot_view.clear_robot()
            self.control_panel.update_message_label("Robot stopped")
        elif event_type == "goal_reached":
            self.robot.stop_simulation()
            self.control_panel.destroy_speed_label()
            self.robot_view.update_message_label(text="Goal reached!")
        elif event_type == "after":
            callback = kwargs.get("callback")
            if callable(callback):
                return self.window.after(kwargs["delay"], callback, kwargs.get("obstacles", []), kwargs.get("goal_position", None))


    def start_robot_movement(self, speed_left, speed_right):
        """Starts the robot's movement with given motor speeds."""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, speed_left)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, speed_right)
    
    def stop_robot(self):
        """Stops the robot and updates the UI."""
        self.robot.stop_simulation()
        self.robot_view.clear_robot()
        self.control_panel.update_message_label("Robot stopped")
