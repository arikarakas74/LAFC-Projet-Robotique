import tkinter as tk
import math
import threading

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
            ("Draw Square", self.draw_square),
            ("set balise", self.map_controller.set_end_mode),
            ("suivre balise", self.suivre),
            ("Reset", self.reset_all)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)


    def draw_square(self):
        from controller.StrategyAsync import PolygonStrategy
        import threading
        import time

        square_strategy = PolygonStrategy(n=4, side_length_cm=100, vitesse_avance=2000, vitesse_rotation=500)
        
        def run_strategy():
            delta_time = 0.02  # intervalle de mise à jour (20ms)
            square_strategy.start(self.simulation_controller.robot_model)
            while not square_strategy.is_finished():
                square_strategy.step(self.simulation_controller.robot_model, delta_time)
                time.sleep(delta_time)
        
        threading.Thread(target=run_strategy, daemon=True).start()


    def suivre(self):
        from controller.StrategyAsync import FollowMovingBeaconStrategy
        import threading, time

        # Créer la stratégie avec les paramètres souhaités
        strategy = FollowMovingBeaconStrategy(vitesse_rotation=90, vitesse_avance=250)

        def run_strategy():
            delta_time = 0.02  # Intervalle d'update (20 ms)
            # Initialiser la stratégie avec le modèle du robot
            strategy.start(self.simulation_controller.robot_model)
            # Boucle d'update : on appelle step() jusqu'à ce que la stratégie s'arrête
            while not strategy.is_finished():
                strategy.step(self.simulation_controller.robot_model, delta_time)
                time.sleep(delta_time)

        # Lancer la boucle d'update dans un thread séparé pour ne pas bloquer l'interface
        threading.Thread(target=run_strategy, daemon=True).start()



    def reset_all(self):
        """Réinitialise l'application."""
        self.simulation_controller.reset_simulation()
        self.map_controller.reset()
