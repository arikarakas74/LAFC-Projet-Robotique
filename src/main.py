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
        from tkinter import ttk
        from controller.map_controller import MapController
        from view.robot_view import RobotView
        from view.map_view import MapView
        from view.control_panel import ControlPanel

        class MainApplication(tk.Tk):
            def __init__(self):
                super().__init__()
                self.title("Robot Simulation MVC")
                self._create_menu()

                # Création de la zone principale
                main_frame = ttk.Frame(self)
                main_frame.pack(fill="both", expand=True)

                # Zone de dessin (Canvas) en haut
                canvas_frame = ttk.Frame(main_frame)
                canvas_frame.pack(side="top", fill="both", expand=True)

                # Zone de contrôle en bas
                controls_frame = ttk.Frame(main_frame, padding=10)
                controls_frame.pack(side="bottom", fill="x")

                # Initialisation des modèles et du contrôleur de simulation
                self.map_model = MapModel(20, 20)
                self.robot_model = RobotModel(self.map_model)
                self.sim_controller = SimulationController(self.map_model, self.robot_model)

                # Création des vues
                self.robot_view = RobotView(canvas_frame, self.sim_controller)
                self.map_view = MapView(
                    parent=canvas_frame,
                    rows=20,
                    cols=20,
                    grid_size=30,
                    robot_view=self.robot_view
                )
                # Le canvas occupe tout l'espace disponible
                self.robot_view.canvas.pack(fill="both", expand=True)

                # Création du contrôleur de la carte
                self.map_controller = MapController(self.map_model, self.map_view, self)

                # Pour centrer réellement les boutons, on crée un sous-frame
                inner_frame = ttk.Frame(controls_frame)
                inner_frame.pack(anchor='center')

                # Panneau de contrôle pour lancer la simulation, réinitialiser, etc.
                self.control_panel = ControlPanel(inner_frame, self.map_controller, self.sim_controller)
                self.control_panel.control_frame.pack(pady=5)

                # Ajout d'un listener pour mettre à jour certains éléments de l'interface si nécessaire
                self.sim_controller.add_state_listener(self.on_state_update)



                # Ajout des bindings pour les commandes clavier via la fenêtre principale
                self.bind("<q>", lambda event: self.sim_controller.robot_controller.increase_left_speed())
                self.bind("<a>", lambda event: self.sim_controller.robot_controller.decrease_left_speed())
                self.bind("<e>", lambda event: self.sim_controller.robot_controller.increase_right_speed())
                self.bind("<d>", lambda event: self.sim_controller.robot_controller.decrease_right_speed())

            def _create_menu(self):
                menubar = tk.Menu(self)
                self.config(menu=menubar)
                file_menu = tk.Menu(menubar, tearoff=False)
                menubar.add_cascade(label="File", menu=file_menu)
                file_menu.add_command(label="Quit", command=self.quit)

            def on_state_update(self, state):
                # Mise à jour de l'interface en temps réel si besoin
                pass

        # Lancement de l'application GUI
        app = MainApplication()
        app.mainloop()
    else:
        # Lancement de la version console (CLI)
        simulation = HeadlessSimulation()
        simulation.run()

if __name__ == "__main__":
    main()
