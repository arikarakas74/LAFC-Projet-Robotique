import time
import math
import logging
from utils.geometry import normalize_angle

# Interface de commande asynchrone
class AsyncCommande:
    def start(self, adapter):
        raise NotImplementedError

    def step(self, adapter, delta_time):
        raise NotImplementedError

    def is_finished(self):
        raise NotImplementedError


# Commande pour avancer d'une distance donnée (en cm) en se basant sur les encodeurs
class Avancer(AsyncCommande):
    def __init__(self, distance_cm, vitesse):
        self.distance_cm = distance_cm      # Distance à parcourir en cm
        self.vitesse = vitesse              # Vitesse en dps (degrés par seconde)
        self.wheel_radius = 2.5             # Rayon de la roue en cm
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("AvancerAdapter")

    def start(self, adapter):
        adapter.set_motor_speed("left", self.vitesse)
        adapter.set_motor_speed("right", self.vitesse)
        self.started = True
        self.logger.info("Commande Avancer démarrée.")

    def step(self, adapter, delta_time):
        if not self.started:
            self.start(adapter)
        traveled_distance = adapter.calculer_distance_parcourue()

        if traveled_distance >= self.distance_cm:
            adapter.set_motor_speed("left", 0)
            adapter.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Commande terminée, distance parcourue: {traveled_distance:.2f} cm")
            adapter.resetDistance()

        return self.finished

    def is_finished(self):
        return self.finished

# Commande pour tourner d'un angle donné (en radians) avec une vitesse de référence (en degrés/s)
class Tourner(AsyncCommande):
    def __init__(self, angle_rad, vitesse_deg_s):
        """
        :param angle_rad: Angle de rotation cible en radians (positif = droite, négatif = gauche)
        :param vitesse_deg_s: Vitesse de référence en degrés/s
        """
        self.angle_rad = angle_rad
        self.base_speed = vitesse_deg_s
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Tourner")
        self.speed_ratio = 0.5  # Pour créer une différence de vitesse entre les roues

    def start(self, adapter):
        self.adapter = adapter
        self.adapter.decide_turn_direction(self.angle_rad,self.base_speed)
        self.started = True
        self.logger.info(f"Début virage: {math.degrees(self.angle_rad):.1f}°")

    def step(self, adapter, delta_time):
        angle=adapter.calcule_angle()

        error = self.angle_rad - angle
        tol = math.radians(0.5)  # Tolérance de 0.5°
        if abs(error) <= tol:
            adapter.set_motor_speed("left", 0)
            adapter.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Virage terminé | Erreur: {math.degrees(error):.2f}°")
            return True

        # Correction proportionnelle sur la roue lente
        Kp = 0.8
        correction = Kp * math.degrees(error)
        new_slow_speed = self.base_speed * self.speed_ratio + correction
        new_slow_speed = max(min(new_slow_speed, self.base_speed), 0)
        adapter.slow_speed(new_slow_speed)
        
        return False

    def is_finished(self):
        return self.finished

    def calculer_angle_par_encodages(self, pos_init_l, pos_init_r, pos_l, pos_r, rayon, entraxe):
        """Version simplifiée du calcul d'angle à partir des encodeurs."""
        return ((pos_l - pos_init_l) - (pos_r - pos_init_r)) * (math.pi * rayon) / (180 * entraxe)

# Commande pour arrêter immédiatement le robot
class Arreter(AsyncCommande):
    def __init__(self):
        self.finished = False
        self.started = False
        self.logger = logging.getLogger("strategy.Arreter")

    def start(self, adapter):
        adapter.set_motor_speed("left", 0)
        adapter.set_motor_speed("right", 0)
        self.started = True
        self.finished = True
        self.logger.info("Arreter executed.")

    def step(self, adapter, delta_time):
        if not self.started:
            self.start(adapter)
        return self.finished

    def is_finished(self):
        return self.finished

# Stratégie composite pour faire suivre au robot un chemin polygonal
class PolygonStrategy(AsyncCommande):
    def __init__(self, n, side_length_cm, vitesse_avance, vitesse_rotation):
        if n < 3:
            raise ValueError("Au moins 3 côtés sont requis.")
        self.logger = logging.getLogger("strategy.PolygonStrategy")
        self.commands = []
        turning_angle = math.radians(90)
        for i in range(n):
            self.commands.append(Avancer(side_length_cm, vitesse_avance))
            self.commands.append(Tourner(turning_angle, vitesse_rotation))
            self.logger.info(f"Côté {i+1} ajouté.")
        self.commands.append(Arreter())
        self.current_index = 0
        self.finished = False

    def start(self, adapter):
        if self.commands:
            self.commands[0].start(adapter)

    def step(self, adapter, delta_time):
        if self.current_index < len(self.commands):
            cmd = self.commands[self.current_index]
            if not cmd.is_finished():
                cmd.step(adapter, delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commands):
                    self.commands[self.current_index].start(adapter)
        else:
            self.finished = True
        return self.finished

    def is_finished(self):
        return self.finished

# Stratégie pour suivre une balise mobile
"""class FollowMovingBeaconStrategy(AsyncCommande):
    def __init__(self, vitesse_rotation, vitesse_avance, tolerance_distance=5, step_distance=5):
        self.vitesse_rotation = vitesse_rotation
        self.vitesse_avance = vitesse_avance
        self.tolerance_distance = tolerance_distance
        self.step_distance = step_distance
        self.logger = logging.getLogger("strategy.FollowMovingBeaconStrategy")
        self.started = False
        self.finished = False

    def start(self, adapter):
        self.started = True//
        self.logger.info("FollowMovingBeacon started.")

    def step(self, adapter, delta_time):
        if not self.started:
            self.start(adapter)
        # Supposons que l'adaptateur fournit un accès au modèle de carte via adapter.map_model
        end_pos = adapter.map_model.end_position  # Position de la balise
        if end_pos is None:
            self.logger.error("Beacon position not defined.")
            self.finished = True
            return self.finished

        target_x, target_y = end_pos
        current_x, current_y = adapter.x, adapter.y
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)

        if distance <= self.tolerance_distance:
            adapter.set_motor_speed("left", 0)
            adapter.set_motor_speed("right", 0)
            self.logger.info("Beacon reached.")
            self.finished = True
        else:
            target_angle = math.atan2(dy, dx)
            angle_to_turn = normalize_angle(target_angle - adapter.direction_angle)
            if abs(math.degrees(angle_to_turn)) > 2:
                # Exécuter une commande de virage pour corriger l'orientation
                turn_cmd = Tourner(angle_to_turn, self.vitesse_rotation)
                turn_cmd.start(adapter)
                turn_cmd.step(adapter, delta_time)
            else:
                # Exécuter une commande d'avancée pour réduire la distance
                advance_cmd = Avancer(min(self.step_distance, distance), self.vitesse_avance)
                advance_cmd.start(adapter)
                advance_cmd.step(adapter, delta_time)
        return self.finished

    def is_finished(self):
        return self.finished"
        """

# Commande composite pour regrouper plusieurs commandes asynchrones
class CommandeComposite(AsyncCommande):
    def __init__(self):
        self.commandes = []
        self.current_index = 0

    def ajouter_commande(self, commande):
        self.commandes.append(commande)

    def start(self, adapter):
        if self.commandes:
            self.commandes[0].start(adapter)

    def step(self, adapter, delta_time):
        if self.current_index < len(self.commandes):
            cmd = self.commandes[self.current_index]
            if not cmd.is_finished():
                cmd.step(adapter, delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commandes):
                    self.commandes[self.current_index].start(adapter)
        return self.current_index >= len(self.commandes)

    def is_finished(self):
        return self.current_index >= len(self.commandes)
