import tkinter as tk

class ControlPanel:
    """Handles the control buttons for user interaction."""

    def __init__(self, parent, map_controller, simulation_controller):
        self.parent = parent # 'parent' is now the Map class instance
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        self.control_frame = tk.Frame(parent.window)
        self.control_frame.pack()

        # Buttons for user interaction
        self.set_start_button = tk.Button(self.control_frame, text="Set Start", command=self.map_controller.set_start_mode)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_obstacles_button = tk.Button(self.control_frame, text="Set Obstacles", command=self.map_controller.set_obstacles_mode)
        self.set_obstacles_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = tk.Button(self.control_frame, text="Run Simulation", command=self.simulation_controller.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.simulation_controller.reset_map)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.draw_square_button = tk.Button(self.control_frame, text="Draw Square", command=self.simulation_controller.draw_square)
        self.draw_square_button.pack(side=tk.LEFT, padx=5, pady=5)