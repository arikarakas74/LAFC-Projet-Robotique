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
        self.simulation_controller.reset_simulation()
        if self.map_controller is not None:
            self.map_controller.reset()