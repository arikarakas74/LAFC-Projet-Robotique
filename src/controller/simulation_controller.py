from model.robot import Robot  # Adjusted the import path
from view.control_panel import ControlPanel
from controller.map_controller import MapController  # Import MapController
from controller.robot_controller import RobotController  # Import RobotController
from model.map_model import MapModel
from view.robot_view import RobotView

class SimulationController:
    """Handles the simulation flow and interactions between model and view."""

    def __init__(self, map_instance, map_model, robot_view, control_panel=None):
        self.map_model = map_model
        self.robot_view = robot_view
        self.map = map_instance
        self.simulation_running = False
        self.robot = None
        self.robot_controller = None
        self.map_controller = MapController(self.map.map_model, self.map.map_view, self.map.window)  # Initialize map_controller with required arguments
        self.control_panel = control_panel  # Use the provided control_panel
    
    def update_view(self):
        x, y, theta = self.robot_view.get_position()
        self.robot_view.draw(x, y, theta)  

    def run_simulation(self):
        """Starts the robot simulation."""
        if self.map_model.start_position:
            start_x, start_y = self.map_model.start_position
            self.robot_view.x = start_x
            self.robot_view.y = start_y
        if self.simulation_running:
            self.map.map_view.update_message_label(text="Simulation already running.") # Access map_view
            return

        if not self.map.map_model.start_position: # Access map_model
            self.map.map_view.update_message_label(text="Please set the start position.") # Access map_view
            return

        self.map.robot = Robot(self.map.map_model)  # Create robot instance with map dimensions
        self.update_view()
        self.map.robot.add_event_listener(lambda event, **kwargs: self.update_view())
        self.map.robot.start_movement()
        self.map.map_view.create_speed_label()  # Create speed label in the view
        self.control_panel.set_speed_label(self.map.map_view.speed_label)  # Set the speed label to control panel
        self.robot_controller = RobotController(self.map.robot, self.map.map_view.robot_view, self.control_panel, self.map.window,self.map_model)  # Pass window to RobotController
        self.map.map_view.update_message_label(text="Use W/S to move forward/backward and A/D to turn left/right.") # Access map_view
        self.simulation_running = True

    def reset_map(self, include_robot=False):

        self.simulation_running = False
        self.map.map_view.delete_all()  # Access map_view
        self.map.map_model.reset()  # Access map_model
        self.map.map_view.update_message_label(text="Map reset.")  # Access map_view
        if self.map.map_view.speed_label:
            self.map.map_view.speed_label.destroy()
            self.map.map_view.speed_label = None
        self.map.window.update()

        self.map.map_view.robot_view.clear_robot()  # Clear the robot from the canvas

        if include_robot:
            self.reset_robot()

    def reset_robot(self):
        """Resets the robot to its initial state."""
        if self.map.robot:
            self.map.robot.stop_simulation()
            self.map.robot = None
        self.map.map_view.robot_view.clear_robot()  # Clear the robot from the canvas

    def draw_square(self):
        """Starts the robot drawing a square."""
        if not self.map.robot:
            self.map.map_view.update_message_label(text="Start the simulation first.") # Access map_view
            return
        self.map.robot.draw_square(obstacles=self.map.map_model.obstacles)  # Pass obstacles to draw_square
