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

import math
import logging
from controller.StrategyAsync import AsyncCommande

class Tourner(AsyncCommande):
    def __init__(self, angle_rad, vitesse_deg_s):
        """
        :param angle_rad: Angle de rotation cible en radians 
                         (positif = droite, négatif = gauche)
        :param vitesse_deg_s: Vitesse de référence en degrés/s
        """
        self.angle_rad = angle_rad
        self.base_speed = vitesse_deg_s
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Tourner")
        
        # Configuration du rapport de vitesse entre roues
        self.speed_ratio = 0.5  # 50% de différence de vitesse entre roues

    def start(self, robot):
        """Initialisation des moteurs pour un virage en arc"""
        self.robot = robot
        self.left_initial = robot.motor_positions["left"]
        self.right_initial = robot.motor_positions["right"]

        # Détermination de la roue rapide/lente selon le sens
        if self.angle_rad > 0:  # Droite
            self.fast_wheel = "left"
            self.slow_wheel = "right"
        else:  # Gauche
            self.fast_wheel = "right"
            self.slow_wheel = "left"

        # Application des vitesses initiales
        robot.set_motor_speed(self.fast_wheel, self.base_speed)
        robot.set_motor_speed(self.slow_wheel, self.base_speed * self.speed_ratio)

        self.started = True
        self.logger.info(f"Début virage en arc: {math.degrees(self.angle_rad):.1f}°")

    def step(self, robot, delta_time):
        """Contrôle proportionnel de la rotation"""
        # Calcul angle actuel
        delta_left = robot.motor_positions["left"] - self.left_initial
        delta_right = robot.motor_positions["right"] - self.right_initial
        
        wheel_circumference = 2 * math.pi * robot.WHEEL_DIAMETER/2
        angle = (delta_left - delta_right) * wheel_circumference / (360 * robot.WHEEL_BASE_WIDTH)
        
        # Calcul erreur et correction
        error = self.angle_rad - angle
        tol = math.radians(0.5)  # Tolérance de 0.5°
        
        if abs(error) <= tol:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)

            self.finished = True
            self.logger.info(f"Virage terminé | Erreur: {math.degrees(error):.2f}°")
            return True

        # Correction proportionnelle (seulement sur la roue lente)
        Kp = 0.8  # Gain plus doux
        correction = Kp * math.degrees(error)
        
        # Application de la correction
        new_slow_speed = self.base_speed * self.speed_ratio + correction
        new_slow_speed = max(min(new_slow_speed, self.base_speed), 0)  # Bornage
        
        robot.set_motor_speed(self.slow_wheel, new_slow_speed)
        
        return False

    def is_finished(self):
        return self.finished

    def calculer_angle_par_encodages(self, pos_init_l, pos_init_r, pos_l, pos_r, rayon, entraxe):
        """Version simplifiée du calcul d'angle"""
        return ((pos_l - pos_init_l) - (pos_r - pos_init_r)) * (math.pi * rayon) / (180 * entraxe)


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
            self.commands.append(Tourner(turning_angle, vitesse_rotation))
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
