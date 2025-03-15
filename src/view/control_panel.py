import tkinter as tk
import math

class ControlPanel:
    """Panneau de contrôle pour les interactions utilisateur."""
    
    def __init__(self, parent, map_controller, simulation_controller):
        self.parent = parent
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        
        # Frame pour les boutons
        self.control_frame = tk.Frame(parent)
        self.control_frame.pack()
        
        # Boutons
        self._create_buttons()

    def _create_buttons(self):
        # Common buttons for both 2D and 3D modes
        buttons = [
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Reset", self.reset_all),
        ]
        
        # Add map-specific buttons only if we have a map controller (2D mode)
        if self.map_controller is not None:
            map_buttons = [
                ("Set Start", self.map_controller.set_start_mode),
                ("Set Obstacles", self.map_controller.set_obstacles_mode),
                ("draw", self.simulation_controller.square)
            ]
            buttons = map_buttons + buttons
        
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)

    def reset_all(self):
        """Réinitialise l'application."""
        # Stop the simulation
        self.simulation_controller.stop_simulation()
        
        # Reset all wheel speeds to 0
        robot_controller = self.simulation_controller.robot_controller
        robot_controller.set_left_speed(0)
        robot_controller.set_right_speed(0)
        
        # Reset any other states if necessary (pitch, roll, etc. in 3D mode)
        robot_model = self.simulation_controller.robot_model
        if hasattr(robot_model, 'pitch'):
            robot_model.pitch = 0
        if hasattr(robot_model, 'roll'):
            robot_model.roll = 0
        
        # Restart the simulation
        self.simulation_controller.run_simulation()
        
        # Reset map if in 2D mode
        if self.map_controller is not None:
            self.map_controller.reset()