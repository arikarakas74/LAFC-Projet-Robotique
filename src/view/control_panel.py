import tkinter as tk
import math
import threading
from controller.adapter import RealRobotAdapter
from robot.robot import MockRobot2IN013

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
            ("Avance", self.suivre),
            ("dessine", self.trace),
            ("Reset", self.reset_all)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)

    def trace(self) :
        self.simulation_controller.robot_model.dessine(not self.simulation_controller.robot_model.crayon)
    def draw_square(self):
        from controller.StrategyAsync import PolygonStrategy
        import threading
        import time
        #adapteRobot=RealRobotAdapter(MockRobot2IN013())
        square_strategy = PolygonStrategy(4,self.simulation_controller.robot_model, side_length_cm=100, vitesse_avance=2000, vitesse_rotation=500)
        
        def run_strategy():
            delta_time = 0.02  # intervalle de mise à jour (20ms)
            square_strategy.start()
            while not square_strategy.is_finished():
                square_strategy.step( delta_time)
                time.sleep(delta_time)
        
        threading.Thread(target=run_strategy, daemon=True).start()


    def suivre(self):
        from controller.StrategyAsync import AvnacePuisRecul
        import threading, time

        # Créer la stratégie avec les paramètres souhaités
        AvnacePuisReculStrategie = AvnacePuisRecul(self.simulation_controller.robot_model, 1000, 350, 
                 safe_distance=30, sensor_max_distance=100, sensor_step=5)
        
        def run_strategy():
            delta_time = 0.02  # intervalle de mise à jour (20ms)
            AvnacePuisReculStrategie.start()
            while not AvnacePuisReculStrategie.is_finished():
                AvnacePuisReculStrategie.step( delta_time)
                time.sleep(delta_time)
        
        threading.Thread(target=run_strategy, daemon=True).start() 

        



    def reset_all(self):
        """Réinitialise l'application."""
        self.simulation_controller.reset_simulation()
        self.map_controller.reset()