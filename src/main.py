import argparse
import time
import math
from controller.simulation_controller import SimulationController
from model.map_model import MapModel
from model.robot import RobotModel

class HeadlessSimulation:
    """Classe pour l'exécution en mode console sans interface graphique"""
    def __init__(self):
        self.map_model = MapModel(20, 20)
        self.robot_model = RobotModel(self.map_model)
        self.sim_controller = SimulationController(self.map_model, self.robot_model)
        self.sim_controller.add_state_listener(self.print_state)
    
    def print_state(self, state):
        """Affiche l'état du robot dans la console"""
        print(f"Position: ({state['x']:.1f}, {state['y']:.1f}) | "
              f"Angle: {math.degrees(state['angle']):.1f}° | "
              f"Speeds: L={state['left_speed']}°/s R={state['right_speed']}°/s")
    
    def run(self):
        """Exécute la simulation en mode console"""
        print("Démarrage de la simulation (Ctrl+C pour arrêter)")
        self.sim_controller.run_simulation()
        
        # Exemple de commande automatique
        self.sim_controller.robot_controller.set_motor_speed("left", 2)
        self.sim_controller.robot_controller.set_motor_speed("right", 2)
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.sim_controller.stop_simulation()
            print("\nSimulation arrêtée")

def main():
    # Configuration des arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Simulation de robot MVC")
    parser.add_argument('mode', 
                      choices=['gui', 'cli'], 
                      nargs='?',
                      default='gui',
                      help="Mode d'exécution: gui (par défaut) ou cli")
    args = parser.parse_args()

    if args.mode == 'gui':
        # Import des composants GUI uniquement si nécessaire
        import tkinter as tk
        from controller.map_controller import MapController
        from view.robot_view import RobotView
        from view.map_view import MapView
        from view.control_panel import ControlPanel

        class RobotApp:
            """Classe principale pour l'interface graphique"""
            def __init__(self, root):
                self.root = root
                self.root.title("Robot Simulation MVC")
            
                # Configuration des modèles
                self.map_model = MapModel(20, 20)
                self.robot_model = RobotModel(self.map_model)
                self.sim_controller = SimulationController(self.map_model, self.robot_model)
                
                # Création des vues et contrôleurs
                main_frame = tk.Frame(self.root)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                self.robot_view = RobotView(main_frame, self.sim_controller)
                self.map_view = MapView(
                    parent=main_frame,
                    rows=20,
                    cols=20,
                    grid_size=30,
                    robot_view=self.robot_view
                )
                
                self.map_controller = MapController(
                    map_model=self.map_model,
                    map_view=self.map_view,
                    window=self.root
                )
                
                # Panneau de contrôle
                self.control_panel = ControlPanel(
                    parent=self.root,
                    map_controller=self.map_controller,
                    simulation_controller=self.sim_controller
                )
                
                # Configuration du layout
                self.control_panel.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
                main_frame.pack(fill=tk.BOTH, expand=True)
                self.map_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.robot_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Lancement de l'application GUI
        root = tk.Tk()
        app = RobotApp(root)
        root.mainloop()
    else:
        # Lancement de la version console
        simulation = HeadlessSimulation()
        simulation.run()

if __name__ == "__main__":
    main()