import time
from src.controller.simulation_controller import SimulationController
from src.model.map_model import MapModel
from src.controller.map_controller import MapController
from src.model.robot import RobotModel
from src.view.vpython_view import VpythonView
from src.view.vpython_control_panel import VPythonControlPanel
import vpython

class MainApplication:
    def __init__(self):
        """ 3D Robot Simulation with VPython and Control Panel """
        
        # Initialisation de la carte et du modèle de robot
        self.map_model = MapModel()
        self.robot_model = RobotModel(self.map_model)
        self.sim_controller = SimulationController(self.map_model, self.robot_model, False)
        
        # Initialisation de la vue 3D VPython
        self.vpython_view = VpythonView(self.sim_controller, self.handle_keydown)

        self.map_controller = MapController(self.map_model, None, None)
        
        # Création du panneau de contrôle VPython
        self.control_panel = VPythonControlPanel(self.map_controller, self.sim_controller,self.vpython_view,self.map_model)
        
        # Liaison des événements du clavier
        scene.bind("keydown", self.handle_keydown)
    
    def handle_keydown(self, evt):
        """ Traitement des événements de pression de touches du clavier """
        print(f"Key pressed event detected!")  # S'assurer que la fonction est appelée

        key = evt.key
        print(f"Key pressed: {key}")
        if key == 'q':
            self.sim_controller.robot_controller.increase_left_speed()
        elif key == 'a':
            self.sim_controller.robot_controller.decrease_left_speed()
        elif key == 'e':
            self.sim_controller.robot_controller.increase_right_speed()
        elif key == 'd':
            self.sim_controller.robot_controller.decrease_right_speed()
        elif key == 'w':
            self.sim_controller.robot_controller.move_forward()
        elif key == 's':
            self.sim_controller.robot_controller.move_backward()


def run_vpython():
    app = MainApplication()
    while True:
        time.sleep(0.1)  # Maintenir le processus VPython en cours d'exécution

if __name__ == "__main__":
    run_vpython()
