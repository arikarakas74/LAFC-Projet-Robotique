import tkinter as tk  # Import tkinter module
from model.robot import Robot  # Adjusted the import path

class SimulationController:
    """Handles the simulation flow and interactions between model and view."""

    def __init__(self, map_instance):
        self.map = map_instance
        self.simulation_running = False
        self.simulator = None  # Corrected placement

    def run_simulation(self):
        """Starts the robot simulation."""
        if self.simulation_running:
            self.map.map_view.update_message_label(text="Simulation already running.") # Access map_view
            return

        if not self.map.map_model.start_position: # Access map_model
            self.map.map_view.update_message_label(text="Please set the start position.") # Access map_view
            return

        self.map.robot = Robot(self.map.map_model.start_position, self.map)  # Create robot instance, access map_model
        self.map.map_view.create_speed_label()  # Create speed label in the view
        self.map.robot.set_speed_label(self.map.map_view.speed_label)  # Set the speed label to robot
        self.map.map_view.update_message_label(text="Use W/S to move forward/backward and A/D to turn left/right.") # Access map_view
        self.map.robot.draw()
        self.map.robot.update_motion() # Start motion update
        self.simulation_running = True

    def reset_map(self):
        """Resets the map and simulation."""
        if self.simulator:
            self.simulator.stop()
            self.simulator = None

        if self.map.robot:
            if self.map.robot.current_after:
                self.map.window.after_cancel(self.map.robot.current_after)
            if self.simulation_running:
                if self.map.map_view.speed_label:
                    self.map.map_view.speed_label.destroy()
                    self.map.map_view.speed_label = None
            self.map.robot.acceleration = 0
            self.map.robot.velocity = 0
            self.map.map_view.delete_item("robot") # Access map_view
            self.map.robot = None

        self.simulation_running = False
        self.map.map_view.delete_all() # Access map_view
        self.map.map_model.reset() # Access map_model
        self.map.map_view.update_message_label(text="Map reset.") # Access map_view
        self.map.window.update()

    def draw_square(self):
        """Starts the robot drawing a square."""
        if not self.map.robot:
            self.map.map_view.update_message_label(text="Start the simulation first.") # Access map_view
            return
        self.map.robot.draw_square()