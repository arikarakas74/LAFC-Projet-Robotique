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
        tolerance_rad = math.radians(5.0) # Increased Tolerance to 5 degrees
        if abs(angle_error) < tolerance_rad:
            self.adapter.set_motor_speed('left', 0)
            self.adapter.set_motor_speed('right', 0)
            self.finished = True
            self.logger.info(f"Virage terminé. Angle final: {math.degrees(current_turned_angle):.1f}° (Error: {angle_error:.2f} rad)")
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

# --- Restore and Simplify Horizontal U-Turn Strategy for Q1.2 ---

class HorizontalUTurnStrategy(AsyncCommande):
    """ 
    Strategy for Q1.2: Moves horizontally, stops, makes U-turns at obstacles/walls, loops.
    Uses only MOVING, TURNING, FINISHED states.
    """

    def __init__(self, adapter, map_model, vitesse_avance=150, vitesse_rotation=100, proximity_threshold=30, max_turns=4):
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
        # States: MOVING, TURNING, FINISHED
        self.state = 'MOVING' 
        self.current_sub_command = None
        self.angle_before_turn = 0.0 # Add attribute to store angle
        
        self.started = False
        self.finished = False
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.state == 'FINISHED': return
        self.started = True
        self.logger.info(f"Starting HorizontalUTurnStrategy Q1.2: Target {self.max_turns} turns.")
        self._start_moving()
        
    def _start_moving(self):
        self.logger.debug(f"State: {self.state} -> Starting Avancer")
        self.current_sub_command = Avancer(float('inf'), self.vitesse_avance, self.adapter)
        self.state = 'MOVING' # Ensure state is MOVING
        self.current_sub_command.start()
        
    def _start_turning(self):
        # Store the angle *before* starting the turn command
        self.angle_before_turn = self.adapter.direction_angle 
        self.logger.debug(f"State: {self.state} -> Starting Tourner from angle {math.degrees(self.angle_before_turn):.1f}")
        self.current_sub_command = Tourner(math.pi, self.vitesse_rotation, self.adapter)
        self.state = 'TURNING' # Ensure state is TURNING
        self.current_sub_command.start()

    def is_finished(self):
        return self.finished

    def step(self, delta_time):
        if not self.started or self.finished:
            return True # Indicate finished

        if self.state == 'MOVING':
            # --- Collision Check --- 
            current_x = self.adapter.x
            current_y = self.adapter.y
            current_angle = self.adapter.direction_angle
            # Use robot width for probes (safer than just center)
            half_width = self.adapter.WHEEL_BASE_WIDTH / 2.0 
            probe_dist = self.proximity_threshold
            
            # Calculate points slightly ahead and to the sides of the robot
            front_x = current_x + probe_dist * math.cos(current_angle)
            front_y = current_y + probe_dist * math.sin(current_angle)
            left_angle = current_angle + math.pi / 2
            right_angle = current_angle - math.pi / 2
            probe_lx = front_x + half_width * math.cos(left_angle)
            probe_ly = front_y + half_width * math.sin(left_angle)
            probe_rx = front_x + half_width * math.cos(right_angle)
            probe_ry = front_y + half_width * math.sin(right_angle)

            # Check collision at left, right, and center points ahead
            collision_l = self.map_model.is_collision(probe_lx, probe_ly) or \
                          self.map_model.is_out_of_bounds(probe_lx, probe_ly)
            collision_r = self.map_model.is_collision(probe_rx, probe_ry) or \
                          self.map_model.is_out_of_bounds(probe_rx, probe_ry)
            collision_c = self.map_model.is_collision(front_x, front_y) or \
                          self.map_model.is_out_of_bounds(front_x, front_y)
            
            collision = collision_l or collision_r or collision_c
            
            if collision:
                 self.logger.info(f"Obstacle/boundary detected ({self.state}). Stopping. Turn count: {self.turn_count + 1}")
                 # Stop immediately
                 stop_command = Arreter(self.adapter)
                 stop_command.start() # Instantaneous
                 self.current_sub_command = None # Discard Avancer
                 
                 self.turn_count += 1
                 if self.turn_count >= self.max_turns:
                     self.logger.info(f"Max turns ({self.max_turns}) reached. Finishing.")
                     self.state = 'FINISHED'
                     self.finished = True
                 else:
                     # Start turning (angle_before_turn is set inside this method)
                     self._start_turning()
                 return self.finished # Return finished status
            else:
                # No collision: Continue moving if command exists
                if self.current_sub_command:
                    self.current_sub_command.step(delta_time)
                else:
                     self.logger.warning("No Avancer command in MOVING state, restarting.")
                     self._start_moving()

        elif self.state == 'TURNING':
            if self.current_sub_command:
                sub_finished = self.current_sub_command.step(delta_time)
                if sub_finished:
                    self.logger.debug("Tourner finished.")
                    self.current_sub_command = None # Clear finished command
                    
                    # --- Explicitly set angle after turn --- 
                    target_angle = normalize_angle(self.angle_before_turn + math.pi)
                    self.adapter.direction_angle = target_angle 
                    self.logger.debug(f"Angle explicitly set to {math.degrees(target_angle):.1f} after turn.")
                    # -----------------------------------------

                    # Transition back to moving
                    self._start_moving() 
            else:
                # Safety: If no turn command, attempt to start one
                self.logger.error("In TURNING state but no turning command found!")
                self._start_turning() 
        
        elif self.state == 'FINISHED':
            self.finished = True
            
        return self.finished
