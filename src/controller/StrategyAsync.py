import time
import math
import logging
from utils.geometry import normalize_angle

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
        self.adapter.decide_turn_direction(self.angle_rad, self.base_speed)
        self.started = True
        self.logger.info(f"Début virage: {math.degrees(self.angle_rad):.1f}°")
        print("Commande tourner démarrée.")

    def step(self, delta_time):
        angle = self.adapter.calcule_angle()
        error = self.angle_rad - angle
        tol = math.radians(0.5)  # Tolérance de 0.5°
        if abs(error) <= tol:
            self.adapter.set_motor_speed("left", 0)
            self.adapter.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Virage terminé | Erreur: {math.degrees(error):.2f}°")
            return True
        # Correction proportionnelle sur la roue lente
        Kp = 0.8
        correction = Kp * math.degrees(error)
        new_slow_speed = self.base_speed * self.speed_ratio + correction
        new_slow_speed = max(min(new_slow_speed, self.base_speed), 0)
        self.adapter.slow_speed(new_slow_speed)
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

# Stratégie pour suivre une balise par analyse d'image
class FollowBeaconByImageStrategy(AsyncCommande):
    def __init__(self, vitesse_rotation, vitesse_avance, tolerance_angle=5, tolerance_radius=30, search_turn_angle=15, step_distance=3, adapter=None, vpython_view=None):
        """
        vitesse_rotation : Vitesse pour les commandes Tourner (en degrés/s).
        vitesse_avance : Vitesse pour les commandes Avancer.
        tolerance_angle : Seuil en degrés pour considérer la balise centrée.
        tolerance_radius : Seuil sur le rayon détecté indiquant que le robot est proche.
        search_turn_angle: Angle de rotation (en degrés) pour la recherche.
        step_distance : Distance d'avancée par commande Avancer.
        adapter : Interface de commande (RobotModel).
        vpython_view : Instance de VpythonView pour obtenir l'image.
        """
        super().__init__(adapter)
        self.vitesse_rotation = vitesse_rotation
        self.vitesse_avance = vitesse_avance
        self.tolerance_angle = tolerance_angle  # en degrés
        self.tolerance_radius = tolerance_radius
        self.search_turn_angle_rad = math.radians(search_turn_angle)
        self.step_distance = step_distance
        self.vpython_view = vpython_view
        self.logger = logging.getLogger("strategy.FollowBeacon")

        self.STATE_SEARCHING = "SEARCHING"
        self.STATE_ALIGNING = "ALIGNING"
        self.STATE_ADVANCING = "ADVANCING"
        self.STATE_FINISHED = "FINISHED"

        self.current_state = self.STATE_SEARCHING
        self.current_sub_command = None
        self.finished = False
        self.image_analysis_requested = True # Demander une analyse au premier pas

        self.image_width = 400 # Largeur d'image supposée (à vérifier/configurer)
        self.fov_horizontal = math.radians(60) # Champ de vision horizontal supposé

    def start(self):
        self.current_state = self.STATE_SEARCHING
        self.current_sub_command = None
        self.finished = False
        self.image_analysis_requested = True
        self.logger.info("FollowBeaconByImageStrategy démarrée. État initial: SEARCHING")
        # On ne lance pas de sous-commande immédiatement, on attend le premier step pour analyser

    def step(self, delta_time):
        if self.finished:
            return True

        # 1. Exécuter la sous-commande en cours si elle existe
        if self.current_sub_command:
            if not self.current_sub_command.is_finished():
                self.current_sub_command.step(delta_time)
                # Pendant qu'une sous-commande s'exécute, on n'analyse pas l'image
                return False 
            else:
                # La sous-commande est terminée, on peut analyser l'image et décider de la suite
                self.logger.info(f"Sous-commande {type(self.current_sub_command).__name__} terminée.")
                self.current_sub_command = None
                self.image_analysis_requested = True

        # 2. Si une analyse d'image est demandée (après fin de sous-commande ou au début)
        if self.image_analysis_requested:
            latest_image_data = self.vpython_view.get_latest_image()
            self.image_analysis_requested = False # Reset la demande

            if latest_image_data is None:
                self.logger.warning("Aucune donnée d'image disponible, reste en état actuel.")
                # Si on était en recherche, on pourrait relancer une recherche, sinon on attend
                if self.current_state == self.STATE_SEARCHING and self.current_sub_command is None:
                     self._initiate_search()
                return False # Attendre la prochaine image

            # Analyse de l'image
            detections = self.vpython_view.analyze_image(latest_image_data)

            # 3. Décider de l'état suivant et de la prochaine sous-commande
            if not detections:
                 # Pas de balise détectée
                if self.current_state != self.STATE_SEARCHING:
                    self.logger.info("Balise perdue. Passage à l'état SEARCHING.")
                    self.current_state = self.STATE_SEARCHING
                self._initiate_search()

            else:
                # Balise détectée
                detection = detections[0] # Prendre la première
                center_x, _ = detection["center"]
                radius = detection["radius"]
                self.logger.info(f"Balise détectée. Centre X: {center_x}, Rayon: {radius:.1f}")

                # Proche de la balise?
                if radius >= self.tolerance_radius:
                    self.logger.info("Balise atteinte (rayon suffisant). Passage à l'état FINISHED.")
                    self.current_state = self.STATE_FINISHED
                    self._initiate_stop()
                    self.finished = True
                    return True

                # Calcul de l'erreur angulaire
                error_x = center_x - (self.image_width / 2)
                angle_error = (error_x / self.image_width) * self.fov_horizontal # en radians
                angle_error_deg = math.degrees(angle_error)
                self.logger.info(f"Erreur angulaire calculée: {angle_error_deg:.2f}°")

                # Aligné?
                if abs(angle_error_deg) > self.tolerance_angle:
                    # Pas aligné -> ALIGNING
                    if self.current_state != self.STATE_ALIGNING:
                         self.logger.info(f"Non aligné (erreur > {self.tolerance_angle}°). Passage à l'état ALIGNING.")
                         self.current_state = self.STATE_ALIGNING
                    self._initiate_alignment(angle_error)
                else:
                    # Aligné -> ADVANCING
                    if self.current_state != self.STATE_ADVANCING:
                        self.logger.info(f"Aligné (erreur <= {self.tolerance_angle}°). Passage à l'état ADVANCING.")
                        self.current_state = self.STATE_ADVANCING
                    self._initiate_advance()
            
        # Si on arrive ici, c'est qu'une nouvelle sous-commande a été lancée (ou on attend)
        return self.finished

    def _initiate_search(self):
        self.logger.info(f"Lancement sous-commande: Tourner (recherche {math.degrees(self.search_turn_angle_rad):.1f}°)")
        self.current_sub_command = Tourner(self.search_turn_angle_rad, self.vitesse_rotation, self.adapter)
        self.current_sub_command.start()

    def _initiate_alignment(self, angle_error_rad):
        self.logger.info(f"Lancement sous-commande: Tourner (alignement {math.degrees(angle_error_rad):.1f}°)")
        self.current_sub_command = Tourner(angle_error_rad, self.vitesse_rotation, self.adapter)
        self.current_sub_command.start()

    def _initiate_advance(self):
        self.logger.info(f"Lancement sous-commande: Avancer ({self.step_distance} cm)")
        self.current_sub_command = Avancer(self.step_distance, self.vitesse_avance, self.adapter)
        self.current_sub_command.start()

    def _initiate_stop(self):
        self.logger.info("Lancement sous-commande: Arreter")
        self.current_sub_command = Arreter(self.adapter)
        self.current_sub_command.start()
        # L'arrêt est immédiat, on peut le considérer fini tout de suite pour la logique
        self.current_sub_command.step(0) 

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
