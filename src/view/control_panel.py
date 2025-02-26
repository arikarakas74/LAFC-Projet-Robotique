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
        buttons = [
            ("Set Start", self.map_controller.set_start_mode),
            ("Set Obstacles", self.map_controller.set_obstacles_mode),
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Reset", self.reset_all),
            ("draw", self.simulation_controller.square)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)

    def reset_all(self):
        """Réinitialise l'application."""
        self.simulation_controller.reset_simulation()
        self.map_controller.reset()