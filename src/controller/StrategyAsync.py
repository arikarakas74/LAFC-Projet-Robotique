import time
import math
import logging
from src.utils.geometry import normalize_angle

# Interface de commande asynchrone
class AsyncCommande:
    def __init__(self, adapter=None):
        self.adapter = adapter

    def start(self):
        raise NotImplementedError

    def step(self, delta_time):
        raise NotImplementedError

    def is_finished(self):
        raise NotImplementedError

# Commande pour avancer d'une distance donnée (en cm) en se basant sur les encodeurs
class Avancer(AsyncCommande):
    def __init__(self, distance_cm, vitesse, adapter):
        super().__init__(adapter)
        self.distance_cm = distance_cm      # Distance à parcourir en cm
        self.vitesse = vitesse              # Vitesse en dps (degrés par seconde)
        self.wheel_radius = 2.5             # Rayon de la roue en cm
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("AvancerAdapter")

    def start(self):
        self.adapter.set_motor_speed("left", self.vitesse)
        print("lina")
        self.adapter.set_motor_speed("right", self.vitesse)
        
        self.started = True
        print("Commande Avancer démarrée.")

    def step(self, delta_time):
        if not self.started:
            self.start()
        traveled_distance = self.adapter.calculer_distance_parcourue()
        if traveled_distance >= self.distance_cm:
            self.adapter.set_motor_speed("left", 0)
            self.adapter.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Commande terminée, distance parcourue: {traveled_distance:.2f} cm")
            self.adapter.resetDistance()
        return self.finished

    def is_finished(self):
        return self.finished

# Commande pour tourner d'un angle donné (en radians) avec une vitesse de référence (en degrés/s)
class Tourner(AsyncCommande):
    def __init__(self, angle_rad, vitesse_deg_s, adapter):
        super().__init__(adapter)
        self.angle_rad = angle_rad
        self.base_speed = vitesse_deg_s
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Tourner")
        self.speed_ratio = 0.5  # Pour créer une différence de vitesse entre les roues

    def start(self):
        # Reset angle calculation before starting
        self.adapter.last_motor_positions = self.adapter.get_motor_positions()
        
        # Directly use the modified decide_turn_direction for in-place rotation
        self.adapter.decide_turn_direction(self.angle_rad, self.base_speed)

        self.started = True
        self.logger.info(f"Début virage: {math.degrees(self.angle_rad):.1f}°")
        #print("Commande tourner démarrée.") # Optional debug print

    def step(self, delta_time):
        if not self.started:
            self.start()
        
        current_turned_angle = self.adapter.calcule_angle()
        angle_error = normalize_angle(self.angle_rad - current_turned_angle)
        # angle_error_deg = math.degrees(angle_error)

        # --- Add Debug Logging --- 
        target_deg = math.degrees(self.angle_rad)
        current_turned_deg = math.degrees(current_turned_angle)
        error_deg = math.degrees(angle_error)
        self.logger.debug(f"Tourner Step: Target={target_deg:.1f}, Turned={current_turned_deg:.1f}, Error={error_deg:.1f}")
        # ------------------------- 

        #print(f"Angle actuel: {math.degrees(current_turned_angle):.1f}°, Erreur: {angle_error_deg:.1f}°") # Optional debug

        # Check if turn is complete within tolerance
        tolerance_rad = math.radians(1.0) # Tolerance of 1 degree
        if abs(angle_error) < tolerance_rad:
            self.adapter.set_motor_speed('left', 0)
            self.adapter.set_motor_speed('right', 0)
            self.finished = True
            self.logger.info(f"Virage terminé. Angle final: {math.degrees(current_turned_angle):.1f}°")
            return True
        else:
            # Since decide_turn_direction now sets opposing speeds,
            # we just let it run until the angle is met. No speed adjustment needed here.
            pass
            
        return False

    def is_finished(self):
        return self.finished

    def calculer_angle_par_encodages(self, pos_init_l, pos_init_r, pos_l, pos_r, rayon, entraxe):
        """Version simplifiée du calcul d'angle à partir des encodeurs."""
        return ((pos_l - pos_init_l) - (pos_r - pos_init_r)) * (math.pi * rayon) / (180 * entraxe)

# Commande pour arrêter immédiatement le robot
class Arreter(AsyncCommande):
    def __init__(self, adapter):
        super().__init__(adapter)
        self.finished = False
        self.started = False
        self.logger = logging.getLogger("strategy.Arreter")

    def start(self):
        self.adapter.set_motor_speed("left", 0)
        self.adapter.set_motor_speed("right", 0)
        self.started = True
        self.finished = True
        self.logger.info("Arreter executed.")

    def step(self, delta_time):
        if not self.started:
            self.start()
        return self.finished

    def is_finished(self):
        return self.finished

# Stratégie composite pour faire suivre au robot un chemin polygonal
class PolygonStrategy(AsyncCommande):
    def __init__(self, n, adapter, side_length_cm, vitesse_avance, vitesse_rotation):
        super().__init__(adapter)
        if n < 3:
            raise ValueError("Au moins 3 côtés sont requis.")
        self.logger = logging.getLogger("strategy.PolygonStrategy")
        self.commands = []
        turning_angle = math.radians(90)
        for i in range(n):
            self.commands.append(Avancer(side_length_cm, vitesse_avance, adapter))
            self.commands.append(Tourner(turning_angle, vitesse_rotation, adapter))
            self.logger.info(f"Côté {i+1} ajouté.")
        self.commands.append(Arreter(adapter))
        self.current_index = 0
        self.finished = False

    def start(self):
        if self.commands:
            self.commands[0].start()

    def step(self, delta_time):
        if self.current_index < len(self.commands):
            cmd = self.commands[self.current_index]
            if not cmd.is_finished():
                cmd.step(delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commands):
                    self.commands[self.current_index].start()
        else:
            self.finished = True
        return self.finished

    def is_finished(self):
        return self.finished

# Stratégie pour suivre une balise mobile
class FollowBeaconByImageStrategy(AsyncCommande):
    def __init__(self, vitesse_rotation, vitesse_avance, tolerance_angle=2, tolerance_radius=20, step_distance=5, adapter=None, vpython_view=None):
        """
        vitesse_rotation : vitesse de rotation du robot (en degrés ou rad/s, à calibrer)
        vitesse_avance : vitesse d'avancement du robot
        tolerance_angle : seuil en degrés pour considérer que la balise est centrée
        tolerance_radius : seuil sur le rayon détecté indiquant que le robot est proche de la balise
        step_distance : distance d'avancée par commande
        adapter : interface de commande (doit disposer de set_motor_speed, etc.)
        vpython_view : instance de VpythonView qui contient la fonction analyze_image modifiée
        """
        super().__init__(adapter)
        self.vitesse_rotation = vitesse_rotation
        self.vitesse_avance = vitesse_avance
        self.tolerance_angle = tolerance_angle  # en degrés
        self.tolerance_radius = tolerance_radius  # seuil sur le rayon détecté
        self.step_distance = step_distance
        self.vpython_view = vpython_view
        self.logger = logging.getLogger("strategy.FollowBeaconByImageStrategy")
        self.started = False
        self.finished = False

    def start(self):
        self.started = True
        self.logger.info("FollowBeaconByImageStrategy started.")

    def step(self, delta_time):
        if not self.started:
            self.start()

        # Récupérer le chemin de la dernière image capturée
        latest_image = self.vpython_view.get_latest_image()
        if latest_image is None:
            self.logger.error("Aucune image capturée.")
            return False

        # Analyse de l'image pour détecter la balise bleue
        detections = self.vpython_view.analyze_image(latest_image)
        if not detections:
            self.logger.info("Aucune balise détectée, rotation pour recherche...")
            # Si aucune balise n'est détectée, tourner d'une petite rotation (ici 10°)
            turn_angle = math.radians(10)
            turn_cmd = Tourner(turn_angle, self.vitesse_rotation, self.adapter)
            turn_cmd.start()
            turn_cmd.step(delta_time)
            return False

        # Considérer la première détection comme la balise ciblée
        detection = detections[0]
        center_x, _ = detection["center"]

        # Vérifier si le rayon détecté indique que le robot est déjà proche
        if detection["radius"] >= self.tolerance_radius:
            self.logger.info("Balise atteinte, arrêt des moteurs.")
            # Arrêter les moteurs (méthode à implémenter selon votre adapter)
            self.adapter.set_motor_speed("left", 0)
            self.adapter.set_motor_speed("right", 0)
            self.finished = True
            return True

        # Supposons une largeur d'image de 400 pixels (adapter selon votre configuration)
        image_width = 400  
        image_center_x = image_width / 2
        error_x = center_x - image_center_x

        # Calcul de l'angle d'erreur en radians à partir du décalage horizontal et du champ de vision
        field_of_view = math.radians(60)  # champ de vision de 60°
        angle_error = (error_x / image_width) * field_of_view
        angle_error_deg = math.degrees(angle_error)
        self.logger.info(f"Erreur angulaire calculée : {angle_error_deg:.2f}°")

        # Zone morte : si l'erreur angulaire est inférieure à la tolérance, on considère l'angle comme nul
        if abs(angle_error_deg) < self.tolerance_angle:
            angle_error = 0

        # Appliquer une commande corrective en fonction de l'erreur d'orientation
        if angle_error != 0:
            turn_cmd = Tourner(angle_error, self.vitesse_rotation, self.adapter)
            turn_cmd.start()
            turn_cmd.step(delta_time)
        else:
            advance_cmd = Avancer(self.step_distance, self.vitesse_avance, self.adapter)
            advance_cmd.start()
            advance_cmd.step(delta_time)

        return self.finished

    def is_finished(self):
        return self.finished

# Commande composite pour regrouper plusieurs commandes asynchrones
class CommandeComposite(AsyncCommande):
    def __init__(self, adapter):
        super().__init__(adapter)
        self.commandes = []
        self.current_index = 0

    def ajouter_commande(self, commande):
        self.commandes.append(commande)

    def start(self):
        if self.commandes:
            self.commandes[0].start()

    def step(self, delta_time):
        if self.current_index < len(self.commandes):
            cmd = self.commandes[self.current_index]
            if not cmd.is_finished():
                cmd.step(delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commandes):
                    self.commandes[self.current_index].start()
        return self.current_index >= len(self.commandes)

    def is_finished(self):
        return self.current_index >= len(self.commandes)

# --- Strategies for Pen Color and State ---

class StrategySetPenState(AsyncCommande):
    """Base helper to set pen state (up/down)."""
    def __init__(self, adapter, state: bool):
        super().__init__(adapter)
        if not hasattr(self.adapter, 'draw'):
             print(f"ERROR: Adapter {type(self.adapter).__name__} has no draw() method.")
             self.finished = True # Prevent running
             return
        self.target_state = state
        self.finished = False
    def start(self):
        self.adapter.draw(self.target_state)
        self.finished = True
    def step(self, delta_time):
        if not self.finished: self.start()
        return self.finished
    def is_finished(self):
        return self.finished

class StrategySetPenColor(AsyncCommande):
    """Base helper to set pen color."""
    def __init__(self, adapter, color: str):
        super().__init__(adapter)
        self.target_color = color
        self.finished = False
    def start(self):
        color_set = False
        if self.target_color == "red" and hasattr(self.adapter, 'red'):
            self.adapter.red()
            color_set = True
        elif self.target_color == "blue" and hasattr(self.adapter, 'blue'):
            self.adapter.blue()
            color_set = True
            
        if not color_set:
            print(f"Warning: Adapter {type(self.adapter).__name__} cannot set color {self.target_color}.")
        self.finished = True
    def step(self, delta_time):
        if not self.finished: self.start()
        return self.finished
    def is_finished(self):
        return self.finished

class StrategyRed(CommandeComposite):
    """Sets pen color to red and puts pen down."""
    def __init__(self, adapter):
        super().__init__(adapter)
        self.ajouter_commande(StrategySetPenColor(adapter, "red"))
        self.ajouter_commande(StrategySetPenState(adapter, True)) # Pen down

class StrategyBlue(CommandeComposite):
    """Sets pen color to blue and puts pen down."""
    def __init__(self, adapter):
        super().__init__(adapter)
        self.ajouter_commande(StrategySetPenColor(adapter, "blue"))
        self.ajouter_commande(StrategySetPenState(adapter, True)) # Pen down

class StrategyInvisible(StrategySetPenState):
    """Puts pen up."""
    def __init__(self, adapter):
        super().__init__(adapter, False) # Pen up

# --- Modified Horizontal U-Turn Strategy for Q1.5 ---

class HorizontalUTurnStrategy(AsyncCommande):
    """ 
    Simplified strategy using Avancer, Tourner, Arreter, and Color strategies.
    Moves horizontally, stops, makes U-turns at obstacles/walls, loops.
    Draws RED when moving right, BLUE when moving left.
    """

    def __init__(self, adapter, map_model, vitesse_avance=150, vitesse_rotation=100, proximity_threshold=30, max_turns=10):
        super().__init__(adapter)
        if not adapter or not map_model:
             print("ERROR: Adapter or MapModel not provided to HorizontalUTurnStrategy")
             self.state = 'FINISHED'
             self.finished = True
             return
             
        self.map_model = map_model
        self.vitesse_avance = vitesse_avance
        self.vitesse_rotation = vitesse_rotation
        self.proximity_threshold = proximity_threshold
        self.max_turns = max_turns

        self.turn_count = 0
        # States: SETTING_RED, MOVING_RIGHT, STOPPING_R, TURNING_L, 
        #         SETTING_BLUE, MOVING_LEFT, STOPPING_L, TURNING_R, FINISHED
        self.state = 'SETTING_RED' 
        self.current_sub_command = None
        
        self.started = False
        self.finished = False
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.state == 'FINISHED': return
        self.started = True
        self.logger.info(f"Starting HorizontalUTurnStrategy Q1.5: Target {self.max_turns} turns.")
        # Initial state: Set pen to Red and Down
        self._start_set_color_and_pen("red")

    def _start_set_color_and_pen(self, color):
        self.logger.debug(f"State: {self.state} -> Starting Strategy{color.capitalize()}")
        if color == "red":
            self.current_sub_command = StrategyRed(self.adapter)
            self.state = 'SETTING_RED'
        else: # blue
            self.current_sub_command = StrategyBlue(self.adapter)
            self.state = 'SETTING_BLUE'
        self.current_sub_command.start()
        
    def _start_moving(self):
        self.logger.debug(f"State: {self.state} -> Starting Avancer")
        self.current_sub_command = Avancer(float('inf'), self.vitesse_avance, self.adapter)
        # State changes after moving starts
        if self.state == 'SETTING_RED': self.state = 'MOVING_RIGHT'
        elif self.state == 'SETTING_BLUE': self.state = 'MOVING_LEFT'
        self.current_sub_command.start()
        
    def _start_turning(self, direction):
        self.logger.debug(f"State: {self.state} -> Starting Tourner ({direction})")
        # For U-turn, always turn pi radians
        self.current_sub_command = Tourner(math.pi, self.vitesse_rotation, self.adapter)
        # State changes after turning starts
        if direction == 'left': self.state = 'TURNING_L'
        else: self.state = 'TURNING_R' # Assumes turning right after moving left
        self.current_sub_command.start()
        
    def _start_stopping(self, previous_state):
        self.logger.debug(f"State: {self.state} -> Starting Arreter")
        # Stop movement and lift pen
        self.current_sub_command = CommandeComposite(self.adapter)
        self.current_sub_command.ajouter_commande(Arreter(self.adapter))
        self.current_sub_command.ajouter_commande(StrategyInvisible(self.adapter))
        # Set state based on where we were moving
        if previous_state == 'MOVING_RIGHT': self.state = 'STOPPING_R'
        else: self.state = 'STOPPING_L'
        self.current_sub_command.start()

    def is_finished(self):
        return self.finished

    def step(self, delta_time):
        if not self.started or self.finished:
            return True # Indicate finished

        # --- Collision Check (only during movement) ---
        if self.state in ['MOVING_RIGHT', 'MOVING_LEFT']:
            # ... (Collision detection logic remains the same as before) ...
            current_x = self.adapter.x
            current_y = self.adapter.y
            current_angle = self.adapter.direction_angle
            half_width = self.adapter.WHEEL_BASE_WIDTH / 2.0
            probe_dist = self.proximity_threshold
            perp_angle = current_angle + math.pi / 2 
            front_center_x = current_x + probe_dist * math.cos(current_angle)
            front_center_y = current_y + probe_dist * math.sin(current_angle)
            offset_lx = half_width * math.cos(perp_angle)
            offset_ly = half_width * math.sin(perp_angle)
            probe_lx = front_center_x + offset_lx
            probe_ly = front_center_y + offset_ly
            offset_rx = -offset_lx 
            offset_ry = -offset_ly
            probe_rx = front_center_x + offset_rx
            probe_ry = front_center_y + offset_ry
            collision_l = self.map_model.is_collision(probe_lx, probe_ly) or \
                          self.map_model.is_out_of_bounds(probe_lx, probe_ly)
            collision_r = self.map_model.is_collision(probe_rx, probe_ry) or \
                          self.map_model.is_out_of_bounds(probe_rx, probe_ry)
            collision = collision_l or collision_r
            
            if collision:
                 self.logger.info(f"Obstacle/boundary detected ({self.state}). Stopping. Turn count: {self.turn_count + 1}")
                 self._start_stopping(self.state) # Stop and lift pen
                 return self.finished # Let the stopping command run in the next step

        # --- Execute Current Sub-command and State Transitions ---
        if self.current_sub_command:
            sub_finished = self.current_sub_command.step(delta_time)
            if sub_finished:
                self.logger.debug(f"Sub-command {type(self.current_sub_command).__name__} finished in state {self.state}")
                # State transitions based on which command finished
                if self.state == 'SETTING_RED':
                     self._start_moving()
                elif self.state == 'SETTING_BLUE':
                     self._start_moving()
                elif self.state == 'STOPPING_R': # Finished stopping after moving right
                    self.turn_count += 1
                    if self.turn_count >= self.max_turns:
                        self.logger.info(f"Max turns ({self.max_turns}) reached. Finishing.")
                        self.state = 'FINISHED'
                        self.finished = True
                    else:
                        self._start_turning('left') # Turn left after moving right
                elif self.state == 'STOPPING_L': # Finished stopping after moving left
                     self.turn_count += 1 # Count this turn too
                     if self.turn_count >= self.max_turns:
                        self.logger.info(f"Max turns ({self.max_turns}) reached. Finishing.")
                        self.state = 'FINISHED'
                        self.finished = True
                     else:
                        self._start_turning('right') # Turn right after moving left
                elif self.state == 'TURNING_L': # Finished turning left
                    self._start_set_color_and_pen("blue") # Set up for moving left
                elif self.state == 'TURNING_R': # Finished turning right
                    self._start_set_color_and_pen("red") # Set up for moving right
                elif self.state in ['MOVING_RIGHT', 'MOVING_LEFT']:
                     # Avancer(inf) should not finish, only be interrupted by collision
                     self.logger.warning(f"Avancer command finished unexpectedly in state {self.state}")
                     self._start_stopping(self.state) # Stop if Avancer somehow finishes
                else:
                    self.logger.error(f"Unhandled finished sub-command in state {self.state}")
                    self.state = 'FINISHED'
                    self.finished = True
                    
                # Clear the finished command
                self.current_sub_command = None 
                    
        elif self.state != 'FINISHED':
            # Safety check: If no command is running but not finished, log error
            self.logger.error(f"No sub-command running in state {self.state}")
            # Attempt recovery based on state? Or just finish?
            self.state = 'FINISHED' # Safer to just finish
            self.finished = True

        return self.finished
