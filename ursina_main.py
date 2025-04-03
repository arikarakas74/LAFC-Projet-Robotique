from ursina import Ursina
from model.map_model import MapModel
from model.robot import RobotModel
from controller.simulation_controller import SimulationController
from view.ursina_control_panel import UrsinaControlPanel
from view.ursina_view import UrsinaView
import time


class MainApplication:
    def __init__(self):
        self.app = Ursina()

        # initialiser le modèle
        self.map_model = MapModel()
        self.robot_model = RobotModel(self.map_model)

        #  initialiser le contrôleur
        self.sim_controller = SimulationController(self.map_model, self.robot_model)

        # Initialiser la vue et le panneau de contrôle
        self.control_panel = UrsinaControlPanel(self.sim_controller, self.map_model)
        self.ursina_view = UrsinaView(self.sim_controller, self.control_panel)

        # Liaison de la boucle principale
        self.last_time = time.time()
        self.app.update = self.update
        self.app.run()

    def update(self):
        delta_time = time.time() - self.last_time
        self.last_time = time.time()

        if self.control_panel.running:
            self.sim_controller.step_simulation(delta_time)
            self.control_panel.step_strategy(delta_time)


if __name__ == "__main__":
    MainApplication()
