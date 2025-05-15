from ursina import Button, Text, color
from controller.StrategyAsync import FollowBeaconByCommandsStrategy
import threading
import time 

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
        self.square_thread  = None
        self.square_strategy = None
        self.wall_thread = None
        self.wall_strategy = None
        self.beacon_thread = None
        self.beacon_strategy = None

        self.create_buttons()

    def create_buttons(self):
        self.buttons = [
            Button(text='Set Start', color=color.azure, text_color=color.black, position=(-0.8, 0.45), scale=(0.2, 0.08),
                   on_click=self.create_start_box),
            Button(text='Set Balise', color=color.lime, text_color=color.black, position=(-0.8, 0.35), scale=(0.2, 0.08),
                   on_click=self.create_end_box),
            Button(text='Add Obstacle', color=color.red, text_color=color.black, position=(-0.8, 0.25), scale=(0.2, 0.08),
                   on_click=self.set_obstacle_mode),
            Button(text='Run Simulation', color=color.orange, text_color=color.black, position=(-0.8, 0.15), scale=(0.2, 0.08),
                   on_click=self.simulation_controller.run_simulation),
            Button(text='Follow Balise', color=color.yellow, text_color=color.black, position=(-0.8, 0.05), scale=(0.2, 0.08),
                   on_click=self.suivre),
            Button(text='Draw Square', color=color.cyan, text_color=color.black, position=(-0.8, -0.05), scale=(0.2, 0.08),
                   on_click=self.draw_square),
            Button(text='Reset', color=color.red, text_color=color.black, position=(-0.8, -0.15), scale=(0.2, 0.08),
                   on_click=self.reset_simulation),
            Button(text='Stop Wall', color=color.orange, text_color=color.black, position=(-0.8, -0.25), scale=(0.2, 0.08),
                   on_click=self.stop_before_wall)
        ]

        self.status_text = Text(text='Mode: None', position=(-0.85, 0.55), origin=(0, 0), scale=1.2)

    def create_start_box(self):
        self.mode = 'set_start'
        self.status_text.text = "Mode: Set Start"

    def create_end_box(self):
        self.mode = 'set_end'
        self.status_text.text = "Mode: Set End"

    def set_obstacle_mode(self):
        """Active le mode de placement d'obstacles."""
        self.mode = 'set_obstacle'
        self.status_text.text = "Mode: Add Obstacle"

    def stop_before_wall(self):
        """ exécution de la stratégie StopBeforeWall par le robot """
        if not self.simulation_controller.simulation_running:
            print("⚠️ Veuillez d'abord démarrer la simulation.")
            return

        from controller.StrategyAsync import StopBeforeWall

        # instancie la stratégie : arrêt à 100cm, vitesse 8000 dps
        self.wall_strategy = StopBeforeWall(
            target=100,
            vitesse_dps=8000,
            adapter=self.simulation_controller.robot_model
        )

        def run_strategy():
            delta_time = 0.02  # 20 ms entre chaque step (50 Hz)
            self.wall_strategy.start()
            while (self.simulation_controller.simulation_running and not self.wall_strategy.is_finished()):
                self.wall_strategy.step(delta_time)
                time.sleep(0.02)
            print("✅ StopBeforeWall terminée.")
            self.wall_strategy = None
            self.wall_thread = None

        self.wall_thread = threading.Thread(target=run_strategy, daemon=True)
        self.wall_thread.start()
    
    def suivre(self):

        """ exécution de la stratégie FollowBeaconByCommandsStrategy par le robot """
        if not self.simulation_controller.simulation_running:
            print("⚠️ Veuillez d'abord démarrer la simulation.")
            return

        from controller.StrategyAsync import FollowBeaconByCommandsStrategy

        ursina_view = self.ursina_view  # injecté dans __init__ d'UrsinaView

        # instancie la stratégie : avance 10 cm à 60°/s et tourne à 90°/s
        self.beacon_strategy = FollowBeaconByCommandsStrategy(
            adapter=self.simulation_controller.robot_model,
            ursina_view=ursina_view

        )

        def run_strategy():
            delta_time = 0.02  # 20 ms entre chaque step (50 Hz)
            self.beacon_strategy.start()
            while (self.simulation_controller.simulation_running and not self.beacon_strategy.is_finished()):
                self.beacon_strategy.step(delta_time)
                time.sleep(0.02)
            print("✅ FollowBeaconByCommandsStrategy terminée (ou interrompue).")
            self.beacon_thread = None
            self.beacon_strategy = None

        self.beacon_thread = threading.Thread(target=run_strategy, daemon=True)
        self.beacon_thread.start()

    def draw_square(self):
        """ exécution de la stratégie de dessin de carré par le robot """
        if not self.simulation_controller.simulation_running:
            print("⚠️ Veuillez d'abord démarrer la simulation.")
            return
        
        if self.square_thread and self.square_thread.is_alive():
            print("⚠️  Carré déjà en cours - ignorer.")
            return
        from controller.StrategyAsync import PolygonStrategy
        
        self.square_strategy = PolygonStrategy(4,self.simulation_controller.robot_model, side_length_cm=500, vitesse_avance=1050, vitesse_rotation=260)
        
        def run_strategy():
            delta_time = 0.02  # renouvelement 20 ms par fois
            
            self.square_strategy.start()
            while (self.simulation_controller.simulation_running and not self.square_strategy.is_finished()):
                self.square_strategy.step(delta_time)

            self.square_thread = None
            self.square_strategy = None

        self.square_thread = threading.Thread(target=run_strategy, daemon=True)
        self.square_thread.start()

    def reset_simulation(self):
        if self.square_strategy:
            self.square_strategy.finished = True
        if self.square_thread and self.square_thread.is_alive():
            self.square_thread.join(timeout=0.2)
        if self.beacon_strategy:
            self.beacon_strategy.finished = True
        if self.beacon_thread and self.beacon_thread.is_alive():
            self.beacon_thread.join(timeout=0.2)
        if self.wall_strategy:
            self.wall_strategy.finished = True
        if self.wall_thread and self.wall_thread.is_alive():
            self.wall_thread.join(timeout=0.2)
        self.simulation_controller.reset_simulation()
        self.ursina_view.reset_ursina_view()
        self.running = False
        self.status_text.text = "Mode: None"
        self.mode = None

    def step_strategy(self, delta_time):
        if self.current_strategy and not self.current_strategy.is_finished():
            self.current_strategy.step(self.simulation_controller.robot_model, delta_time)


