import tkinter as tk
import math

class ControlPanel:
    """Handles the control buttons for user interaction."""

    def __init__(self, parent, map_controller, simulation_controller):
        self.parent = parent  # 'parent' is now the correct parent object
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        self.control_frame = tk.Frame(parent)  # Use parent directly
        self.control_frame.pack()
        self.speed_label = None

        # Buttons for user interaction
        self.set_start_button = tk.Button(self.control_frame, text="Set Start", command=self.map_controller.set_start_mode)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_obstacles_button = tk.Button(self.control_frame, text="Set Obstacles", command=self.map_controller.set_obstacles_mode)
        self.set_obstacles_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = tk.Button(self.control_frame, text="Run Simulation", command=self.simulation_controller.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_all)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.draw_square_button = tk.Button(self.control_frame, text="Draw Square", command=self.simulation_controller.draw_square)
        self.draw_square_button.pack(side=tk.LEFT, padx=5, pady=5)

    def set_speed_label(self, label):
        """Sets the speed label created in view."""
        self.speed_label = label

    def update_speed_label(self, left_speed, right_speed, direction_angle):
        """Updates the speed label text."""
        if self.speed_label and self.speed_label.winfo_exists():
            self.speed_label.config(text=f"left wheel speed: {left_speed:.2f} - right wheel speed: {right_speed:.2f} | direction_angle: {math.degrees(direction_angle):.2f}°")

    def reset_all(self):
        """Resets the entire map including the robot."""
        self.simulation_controller.reset_map(include_robot=True)
