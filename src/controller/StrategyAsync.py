import time
import math
import logging
from utils.geometry import normalize_angle

# Interface de commande asynchrone
class AsyncCommande:
    def start(self, robot):
        raise NotImplementedError
    def step(self, robot, delta_time):
        raise NotImplementedError
    def is_finished(self):
        raise NotImplementedError

class Accelerer(AsyncCommande):
    def __init__(self, target_speed, duration):
        self.target_speed = target_speed
        self.duration = duration
        self.elapsed = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Accelerer")
    def start(self, robot):
        self.interval = self.duration / 10.0
        self.started = True
        self.logger.info("Acceleration started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        self.elapsed += delta_time
        fraction = min(self.elapsed / self.duration, 1.0)
        speed = self.target_speed * fraction
        robot.set_motor_speed("left", speed)
        robot.set_motor_speed("right", speed)
        if self.elapsed >= self.duration:
            self.finished = True
            self.logger.info("Acceleration finished.")
        return self.finished
    def is_finished(self):
        return self.finished

class Freiner(AsyncCommande):
    def __init__(self, current_speed, duration):
        self.current_speed = current_speed
        self.duration = duration
        self.elapsed = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Freiner")
    def start(self, robot):
        self.started = True
        self.logger.info("Deceleration started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        self.elapsed += delta_time
        fraction = max(1 - self.elapsed / self.duration, 0)
        speed = self.current_speed * fraction
        robot.set_motor_speed("left", speed)
        robot.set_motor_speed("right", speed)
        if self.elapsed >= self.duration:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Deceleration finished.")
        return self.finished
    def is_finished(self):
        return self.finished


class Avancer:
    """
    Adaptateur pour la commande "Avancer" pour un robot réel sans positions (x, y).
    La distance parcourue est calculée à partir des encodeurs des moteurs.
    """
    def __init__(self, distance_cm, vitesse):
        self.distance_cm = distance_cm      # Distance à parcourir en cm
        self.vitesse = vitesse              # Vitesse en dps (degrés par seconde)
        self.wheel_radius = 2.5    # Rayon de la roue en cm
        self.started = False
        self.finished = False
        self.initial_left = None            # Position initiale de l'encodeur gauche
        self.initial_right = None           # Position initiale de l'encodeur droit
        self.logger = logging.getLogger("AvancerRealAdapter")

    def start(self, robot):
        """
        Enregistre les positions initiales des encodeurs et démarre les moteurs.
        """
        self.initial_left = robot.motor_positions["left"]
        self.initial_right = robot.motor_positions["right"]

        # Utilisation de set_motor_dps si disponible, sinon set_motor_speed
        if hasattr(robot, "set_motor_dps"):
            robot.set_motor_dps(robot.MOTOR_LEFT, self.vitesse)
            robot.set_motor_dps(robot.MOTOR_RIGHT, self.vitesse)
        else:
            robot.set_motor_speed("left", self.vitesse)
            robot.set_motor_speed("right", self.vitesse)

        self.started = True
        self.logger.info("Commande AvancerRealAdapter démarrée.")

    def step(self, robot, delta_time):
        """
        Appelée périodiquement pour mettre à jour la commande.
        La distance parcourue est calculée à partir des différences d'encodeur.
        """
        if not self.started:
            self.start(robot)

        # Récupérer les valeurs actuelles des encodeurs
        current_left = robot.motor_positions["left"]
        current_right = robot.motor_positions["right"]

        # Calculer la variation par rapport aux valeurs initiales
        delta_left = current_left - self.initial_left
        delta_right = current_right - self.initial_right

        # Conversion des rotations (en degrés) en distance (cm)
        left_distance = math.radians(delta_left) * self.wheel_radius
        right_distance = math.radians(delta_right) * self.wheel_radius

        # On fait la moyenne des deux distances pour estimer la distance parcourue
        traveled_distance = (left_distance + right_distance) / 2.0

        if traveled_distance >= self.distance_cm:
            # Arrêter les moteurs une fois la distance désirée atteinte
            if hasattr(robot, "set_motor_dps"):
                robot.set_motor_dps(robot.MOTOR_LEFT, 0)
                robot.set_motor_dps(robot.MOTOR_RIGHT, 0)
            else:
                robot.set_motor_speed("left", 0)
                robot.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Commande terminée, distance parcourue: {traveled_distance:.2f} cm")

        return self.finished

    def is_finished(self):
        """Retourne True si la commande est terminée."""
        return self.finished


class Tourner(AsyncCommande):
    
    def __init__(self, angle_rad, vitesse_deg_s, forward_speed):
        """
        :param angle_rad: Angle à tourner (en radians)
        :param vitesse_deg_s: Vitesse maximale de correction de la rotation (en degrés/s)
        :param forward_speed: Vitesse de déplacement en avant (en unités compatibles avec set_motor_speed)
        """
        self.angle_rad = angle_rad
        self.vitesse_deg_s = vitesse_deg_s
        self.forward_speed = forward_speed
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Tourner")
        
    def start(self, robot):
        # Calcul de l'angle cible en fonction de l'angle courant du robot
        self.target_angle = normalize_angle(robot.direction_angle + self.angle_rad)
        self.started = True
        self.logger.info("Tourner started.")
        
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
            
        tol = math.radians(0.001)  # Tolérance (ici environ 0.1° en radians)
        current_angle = normalize_angle(robot.direction_angle)
        error = normalize_angle(self.target_angle - current_angle)
        
        if abs(error) < tol:
            # Une fois le virage réalisé, on supprime la correction pour continuer tout droit
            robot.set_motor_speed("left", self.forward_speed)
            robot.set_motor_speed("right", self.forward_speed)
            self.finished = True
            self.logger.info("Tourner finished.")
        else:
            # Correction proportionnelle : on calcule une vitesse de correction en fonction de l'erreur
            Kp = 8.0
            correction_speed = Kp * math.degrees(error)
            # Limitation de la correction à la vitesse maximale définie
            correction_speed = max(-self.vitesse_deg_s, min(self.vitesse_deg_s, correction_speed))
            # Application d'une vitesse de base forward_speed à chaque moteur
            # avec un ajustement différentiel pour effectuer le virage
            robot.set_motor_speed("left", self.forward_speed + correction_speed)
            robot.set_motor_speed("right", self.forward_speed - correction_speed)
            
        return self.finished
        
    def is_finished(self):
        return self.finished


class Arreter(AsyncCommande):
    def __init__(self):
        self.finished = False
        self.started = False
        self.logger = logging.getLogger("strategy.Arreter")
    def start(self, robot):
        robot.set_motor_speed("left", 0)
        robot.set_motor_speed("right", 0)
        self.started = True
        self.finished = True
        self.logger.info("Arreter executed.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        return self.finished
    def is_finished(self):
        return self.finished

class PolygonStrategy(AsyncCommande):
    def __init__(self, n, side_length_cm, vitesse_avance, vitesse_rotation):
        if n < 3:
            raise ValueError("At least 3 sides required.")
        self.logger = logging.getLogger("strategy.PolygonStrategy")
        self.commands = []
        turning_angle = math.radians(90)
        for i in range(n):
            self.commands.append(Avancer(side_length_cm, vitesse_avance))
            self.commands.append(Tourner(turning_angle, vitesse_rotation,100))
            self.logger.info(f"Side {i+1} added.")
        self.commands.append(Arreter())
        self.current_index = 0
        self.finished = False
    def start(self, robot):
        if self.commands:
            self.commands[0].start(robot)
    def step(self, robot, delta_time):
        if self.current_index < len(self.commands):
            cmd = self.commands[self.current_index]
            if not cmd.is_finished():
                cmd.step(robot, delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commands):
                    self.commands[self.current_index].start(robot)
        else:
            self.finished = True
        return self.finished
    def is_finished(self):
        return self.finished

class FollowMovingBeaconStrategy(AsyncCommande):
    def __init__(self, vitesse_rotation, vitesse_avance, tolerance_distance=5, step_distance=5):
        self.vitesse_rotation = vitesse_rotation  
        self.vitesse_avance = vitesse_avance          
        self.tolerance_distance = tolerance_distance  
        self.step_distance = step_distance            
        self.logger = logging.getLogger("strategy.FollowMovingBeaconStrategy")
        self.started = False
        self.finished = False
    def start(self, robot):
        self.started = True
        self.logger.info("FollowMovingBeacon started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        end_pos = robot.map_model.end_position  # Beacon position
        if end_pos is None:
            self.logger.error("Beacon position not defined.")
            self.finished = True
            return self.finished
        target_x, target_y = end_pos
        current_x, current_y = robot.x, robot.y
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)
        if distance <= self.tolerance_distance:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.logger.info("Beacon reached.")
            self.finished = True
        else:
            target_angle = math.atan2(dy, dx)
            angle_to_turn = normalize_angle(target_angle - robot.direction_angle)
            if abs(math.degrees(angle_to_turn)) > 2:
                turn_cmd = Tourner(angle_to_turn, self.vitesse_rotation,100)
                turn_cmd.start(robot)
                turn_cmd.step(robot, delta_time)
            else:
                advance_cmd = Avancer(min(self.step_distance, distance), self.vitesse_avance)
                advance_cmd.start(robot)
                advance_cmd.step(robot, delta_time)
        return self.finished
    def is_finished(self):
        return self.finished

class CommandeComposite(AsyncCommande):
    def __init__(self):
        self.commandes = []
        self.current_index = 0
    def ajouter_commande(self, commande):
        self.commandes.append(commande)
    def start(self, robot):
        if self.commandes:
            self.commandes[0].start(robot)
    def step(self, robot, delta_time):
        if self.current_index < len(self.commandes):
            cmd = self.commandes[self.current_index]
            if not cmd.is_finished():
                cmd.step(robot, delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commandes):
                    self.commandes[self.current_index].start(robot)
        return self.current_index >= len(self.commandes)
    def is_finished(self):
        return self.current_index >= len(self.commandes)
