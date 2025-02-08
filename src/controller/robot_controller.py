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
            self.control_panel.update_speed_label(kwargs["velocity"], kwargs["direction_angle"])
        elif event_type == "robot_stopped":
            self.robot_view.clear_robot()
        elif event_type == "goal_reached":
            self.control_panel.destroy_speed_label()
            self.robot_view.update_message_label(text="Goal reached!")
        elif event_type == "cancel_after":
            self.window.after_cancel(kwargs["after_id"])
        elif event_type == "after":
            return self.window.after(kwargs["delay"], kwargs["callback"], kwargs["obstacles"], kwargs["goal_position"])
