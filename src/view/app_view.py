import tkinter as tk
from model.map_model import MapModel
from view.map_view import MapView
from view.control_panel import ControlPanel
from controller.map_controller import MapController
from controller.simulation_controller import SimulationController
from view.robot_view import RobotView

class AppView:
    """Main application class to orchestrate MVC components."""

    def __init__(self, rows, cols, grid_size=30):
        self.window = tk.Tk()
        self.window.title("Robot Simulator")

        self.map_model = MapModel(rows, cols)
        self.map_view = MapView(self, rows, cols, grid_size)
        self.robot_view = RobotView(self.map_view)
        self.map_controller = MapController(self.map_model, self.map_view, self.window)  # Pass map_model, map_view, and window to MapController
        self.simulation_controller = SimulationController(self, self.map_model, self.robot_view, None)  # Initialize SimulationController without control_panel
        self.control_panel = ControlPanel(self.window, self.map_controller, self.simulation_controller)  # Create ControlPanel with simulation_controller
        self.simulation_controller.control_panel = self.control_panel  # Set control_panel in SimulationController

        # Bind events - these should mostly call controller methods
        self.map_view.canvas.bind("<Button-1>", self.map_controller.handle_click)
        self.map_view.canvas.bind("<B1-Motion>", self.map_controller.handle_drag)
        self.map_view.canvas.bind("<Double-Button-1>", self.map_controller.finalize_shape)
        self.map_view.canvas.bind("<Button-3>", self.map_controller.delete_obstacle)
        self.map_view.canvas.bind("<ButtonRelease-1>", self.map_controller.stop_drag)

        self.window.bind("<w>", lambda event: self.simulation_controller.robot_controller.increase_speed())
        self.window.bind("<s>", lambda event: self.simulation_controller.robot_controller.decrease_speed())
        self.window.bind("<q>", lambda event: self.simulation_controller.robot_controller.increase_left_speed())
        self.window.bind("<a>", lambda event: self.simulation_controller.robot_controller.decrease_left_speed())
        self.window.bind("<e>", lambda event: self.simulation_controller.robot_controller.increase_right_speed())
        self.window.bind("<d>", lambda event: self.simulation_controller.robot_controller.decrease_right_speed())

    def run(self):
        """Runs the main application loop."""
        self.window.mainloop()
