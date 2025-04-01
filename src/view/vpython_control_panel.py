from vpython import *
from model.map_model import MapModel
from view.vpython_view import VpythonView
import threading
import time

class VPythonControlPanel:
    """Panneau de contrôle VPython, adapté à la version GUI de ControlPanel"""

    def __init__(self, map_controller, simulation_controller,vpython_view,map_model):
        self.map_model = map_model
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        self.vpython_view = vpython_view
        self.start_box = None  # VPython point start
        self.end_box = None  # VPython point end
        self.mode = None

        # Création des boutons du panneau de contrôle VPython
        self._create_buttons()

        # Écoute des événements de clic sur le canevas VPython
        self.vpython_view.scene.bind("click", self.handle_click)

    def _create_buttons(self):
        """ Ajout de boutons dans l'interface VPython  """
        wtext(text="  Control Panel  ")
        
        buttons = [
            ("Set Start", self.create_start_box),  
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Draw Square", self.draw_square), 
            ("Set Balise", self.create_end_box),
            ("Follow Balise", self.suivre), 
            ("Reset", self.reset_all),
            ("stop", self.vpython_view.stop) ,
            ("prendre photo", self.vpython_view.capture_embedded_image) ,
            ("analyze", self.vpython_view.analyze_image) 

        ]

        for text, cmd in buttons:
            button(text=text, bind=cmd)

    def handle_click(self):
        """ Traitement des événements de clic sur le canevas VPython, calcul de l'intersection du rayon avec le plan de fond """
        print("🔹 Click event detected in VpythonView!")

        ray_origin = self.vpython_view.scene.camera.pos  # Position de la caméra
        ray_direction = norm(self.vpython_view.scene.mouse.pos - ray_origin)  # Calcul de la direction du rayon

        ground_y = -1
        t = (ground_y - ray_origin.y) / ray_direction.y  # Calcul du paramètre d'intersection du rayon avec le plan 
        click_pos = ray_origin + t * ray_direction  # Calcul du point d'intersection

        if 0 <= click_pos.x <= 800 and 0 <= click_pos.z <= 600:
            if self.mode == 'set_start':
                self.start_box.pos = vector(click_pos.x, ground_y + 1 , click_pos.z)
                self.start_box.visible = True
                self.map_model.set_start_position((click_pos.x, click_pos.z))  # Call set_start_position on the map model
            elif self.mode == 'set_end' :
                self.end_box.pos = vector(click_pos.x, ground_y + 1 , click_pos.z)
                self.end_box.visible = True
                self.map_model.set_end_position((click_pos.x, click_pos.z))  # Call set_start_position on the map model

    def create_start_box(self):
        """ Création du point de départ dans l'affichage VPython """
        if self.start_box is None:  
            self.start_box = box(pos=vector(400, 0, 300.5), size=vector(10, 10, 10), color=vector(1, 0, 0))
        self.mode = 'set_start'
        print("Start box created. Click anywhere to set the start position.")

    def create_end_box(self):
        """ Création des points de départ et d'arrivée dans l'affichage VPython  """
        if self.end_box is None: 
            self.end_box = box(pos=vector(400, 0, 300.5), size=vector(10, 10, 10), color=vector(0, 0, 1))
        self.mode = 'set_end'
        print("Start box created. Click anywhere to set the start position.")
    
    def draw_square(self):
        """ exécution de la stratégie de dessin de carré par le robot """
        from controller.StrategyAsync import PolygonStrategy
        
        square_strategy = PolygonStrategy(4,self.simulation_controller.robot_model, side_length_cm=100, vitesse_avance=350, vitesse_rotation=260)
        
        def run_strategy():
            delta_time = 0.02  # renouvelement 20 ms par fois
            square_strategy.start()
            while not square_strategy.is_finished():
                square_strategy.step(delta_time)
        
        run_strategy()

    def suivre(self):
        """Permet au robot de suivre la balise en utilisant l'analyse d'image."""
        from controller.StrategyAsync import FollowBeaconByImageStrategy
        import time, threading

        # Récupérer le modèle de robot et la vue depuis le contrôleur de simulation.
        # Ici, 'simulation_controller.robot_model' est l'adaptateur
        # et 'simulation_controller.vpython_view' est l'instance de VpythonView.

        # Instanciation de la stratégie avec les paramètres souhaités.
        strategy = FollowBeaconByImageStrategy(
            vitesse_rotation=500,
            vitesse_avance=1500,
            tolerance_angle=1,
            tolerance_radius=20,
            step_distance=10,
            adapter=self.simulation_controller.robot_model,
            vpython_view=self.vpython_view
        )

        def run_strategy():
            delta_time = 0.02  # Intervalle de temps en secondes
            strategy.start()   # Démarrage de la stratégie
            while not strategy.is_finished():
                strategy.step(delta_time)
                time.sleep(delta_time)

        # Lancer la stratégie dans un thread en arrière-plan.
        threading.Thread(target=run_strategy, daemon=True).start()



    def reset_all(self):
        """ Adaptation de la version GUI de Reset, réinitialisation de l'affichage VPython """
        if self.start_box:
            self.start_box.visible = False
            self.start_box.pos=vector(400, 0, 300.5)
        if self.end_box: 
            self.end_box.visible = False
            self.end_box.pos=vector(400, 0, 300.5)

        self.simulation_controller.reset_simulation()
        self.vpython_view.reset_vpython_view()

        print("Simulation reset.")
