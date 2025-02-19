# main.py
import tkinter as tk
from controller.simulation_controller import SimulationController
from controller.map_controller import MapController
from model.map_model import MapModel
from model.robot import RobotModel
from view.robot_view import RobotView
from view.map_view import MapView
from view.control_panel import ControlPanel  # Ajout de l'import

class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Simulation MVC")
        
        # Configuration principale
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. Initialisation des modèles
        self.map_model = MapModel(20, 20)
        self.robot_model = RobotModel(self.map_model)
        self.sim_controller = SimulationController(self.map_model, self.robot_model)
        self.robot_view = RobotView(main_frame, self.sim_controller)       
        # 3. Création des vues
        self.map_view = MapView(
            parent=main_frame,
            rows=20,
            cols=20,
            grid_size=30,
            robot_view=self.robot_view
        )
        
        # 2. Création des contrôleurs

        self.map_controller = MapController(
            map_model=self.map_model,
            map_view=self.map_view,
            window=self.root
        )


        
        # Création du panneau de contrôle
        self.control_panel = ControlPanel(
            parent=self.root,
            map_controller=self.map_controller,
            simulation_controller=self.sim_controller
        )
        
        # 4. Configuration du layout
        self.control_panel.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.map_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.robot_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Injection des
        
        # 4. Configuration du layout
        self.map_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.robot_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 5. Création des contrôles
        

    def _create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        btn_start = tk.Button(control_frame, 
                            text="Start", 
                            command=self.sim_controller.run_simulation)
        btn_stop = tk.Button(control_frame, 
                           text="Stop", 
                           command=self.sim_controller.stop_simulation)
        btn_reset = tk.Button(control_frame, 
                            text="Reset", 
                            command=self.sim_controller.reset_simulation)

        btn_start.pack(side=tk.LEFT, padx=5)
        btn_stop.pack(side=tk.LEFT, padx=5)
        btn_reset.pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()

    ##########################################2###############################################
"""import time
from controller.simulation_controller import SimulationController
from model.map_model import MapModel
from model.robot import RobotModel

class HeadlessSimulation:
    def __init__(self):
        # Initialisation des composants de base
        self.map_model = MapModel(rows=20, cols=20)
        self.robot_model = RobotModel(self.map_model)
        self.sim_controller = SimulationController(self.map_model,self.robot_model)
        
        # Configuration du logging console
        self.sim_controller.add_state_listener(self.print_state)
        
    def print_state(self, state):
        #Affiche l'état du robot dans la console
        print(f"Position : ({state['x']:.1f}, {state['y']:.1f}) | "
              f"Angle : {math.degrees(state['angle']):.1f}° | "
              f"Vitesses : G={state['left_speed']}°/s D={state['right_speed']}°/s")

    def run(self):
        #Exécute la simulation en mode console
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

if __name__ == "__main__":
    import math
    simulation = HeadlessSimulation()
    simulation.run()
    
    
    
    
    
    
    
    
    
    #############################################################################################
    import tkinter as tk
from model.map_model import MapModel
from model.robot import RobotModel
from controller.map_controller import MapController
from controller.simulation_controller import SimulationController
from view.map_view import MapView
from view.robot_view import RobotView
from view.control_panel import ControlPanel

class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Simulation MVC")

        
        # 1. Modèles
        self.map_model = MapModel(rows=20, cols=20)
        self.robot_model = RobotModel(self.map_model)
        
        # 2. Contrôleurs
        self.simulation_controller = SimulationController(
            map_model=self.map_model,
            robot_model=self.robot_model
        )
        self.map_controller = MapController(
            map_model=self.map_model,
            map_view=None,
            window=self.root
        )
        
        # 3. Interface utilisateur
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panneau de contrôle
        self.control_panel = ControlPanel(
            parent=main_frame,
            map_controller=self.map_controller,
            simulation_controller=self.simulation_controller
        )
        
        # Vue carte
        self.map_view = MapView(
            parent=main_frame,
            rows=20,
            cols=20,
            grid_size=30,
            robot_view=None
        )
        self.map_controller.map_view = self.map_view  # Injection
        
        # Vue robot
        self.robot_view = RobotView(main_frame, self.simulation_controller)
        
        # Layout (tout en pack() pour éviter les conflits)
        self.control_panel.control_frame.pack(side=tk.TOP, fill=tk.X)
        self.map_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.robot_view.canvas.pack(side=tk.LEFT, fill=tk.BOTH)

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()
    
    
    
    
    """