from ursina import Button, Text, color
from controller.StrategyAsync import FollowBeaconByImageStrategy
import threading


class UrsinaControlPanel:
    def __init__(self, simulation_controller, map_model):
        self.simulation_controller = simulation_controller
        self.map_model = map_model
        self.running = False
        self.current_strategy = None
        self.mode = None
        self.start_box = None
        self.end_box = None
        self.ursina_view = None  

        self.create_buttons()

    def create_buttons(self):
        self.buttons = [
            Button(text='Set Start', color=color.azure, position=(-0.8, 0.45), scale=(0.2, 0.08),
                   on_click=self.create_start_box),
            Button(text='Set Balise', color=color.lime, position=(-0.8, 0.35), scale=(0.2, 0.08),
                   on_click=self.create_end_box),
            Button(text='Run Simulation', color=color.orange, position=(-0.8, 0.25), scale=(0.2, 0.08),
                   on_click=self.simulation_controller.run_simulation),
            Button(text='Follow Balise', color=color.yellow, position=(-0.8, 0.15), scale=(0.2, 0.08),
                   on_click=self.suivre),
            Button(text='Draw Square', color=color.cyan, position=(-0.8, 0.05), scale=(0.2, 0.08),
                   on_click=self.draw_square),
            Button(text='Reset', color=color.red, position=(-0.8, -0.05), scale=(0.2, 0.08),
                   on_click=self.reset_simulation)
        ]

        self.status_text = Text(text='Mode: None', position=(-0.85, 0.55), origin=(0, 0), scale=1.2)

    def create_start_box(self):
        self.mode = 'set_start'
        self.status_text.text = "Mode: Set Start"

    def create_end_box(self):
        self.mode = 'set_end'
        self.status_text.text = "Mode: Set End"

    def suivre(self):
        if not self.simulation_controller.simulation_running:
            print("⚠️ Veuillez d'abord démarrer la simulation.")
            return
        self.current_strategy = FollowBeaconByImageStrategy(vitesse_rotation=90, vitesse_avance=250)
        self.current_strategy.start(self.simulation_controller.robot_model)

    def draw_square(self):
        """ exécution de la stratégie de dessin de carré par le robot """
        if not self.simulation_controller.simulation_running:
            print("⚠️ Veuillez d'abord démarrer la simulation.")
            return
        from controller.StrategyAsync import PolygonStrategy
        
        square_strategy = PolygonStrategy(4,self.simulation_controller.robot_model, side_length_cm=500, vitesse_avance=1050, vitesse_rotation=260)
        
        def run_strategy():
            delta_time = 0.02  # renouvelement 20 ms par fois
            
            while not square_strategy.is_finished():
                square_strategy.step(delta_time)

        threading.Thread(target=run_strategy, daemon=True).start()

    def reset_simulation(self):
        self.simulation_controller.reset_simulation()
        self.ursina_view.reset_ursina_view()
        self.running = False
        self.status_text.text = "Mode: None"
        self.mode = None

    def step_strategy(self, delta_time):
        if self.current_strategy and not self.current_strategy.is_finished():
            self.current_strategy.step(self.simulation_controller.robot_model, delta_time)


