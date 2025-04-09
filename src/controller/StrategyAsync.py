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
        self.current_sub_command = None # Garder une référence à la sous-commande en cours

    def start(self):
        self.started = True
        self.logger.info("FollowBeaconByImageStrategy started.")

    def step(self, delta_time):
        if not self.started:
            self.start()

        # Si une sous-commande est en cours, on la continue
        if self.current_sub_command:
            self.current_sub_command.step(delta_time)
            if self.current_sub_command.is_finished():
                self.logger.info("Sous-commande terminée.")
                self.current_sub_command = None # Prêt pour la prochaine décision
            # Tant qu'une sous-commande tourne, la stratégie principale n'est pas finie et attend
            return False 
        
        # Si aucune sous-commande n'est en cours, analyser l'image et décider
        # (Ce bloc ne sera atteint que lorsque la commande précédente sera terminée)
        if self.finished:
            return True

        # 1. Obtenir la dernière image
        latest_image_data = self.vpython_view.get_latest_image()
        if latest_image_data is None:
            self.logger.warn("No image data available this cycle.")
            return False # Attendre qu'une image soit disponible
        else:
            self.logger.debug("Received new image data for analysis.")

        # 2. Analyser l'image
        detections = self.vpython_view.analyze_image(latest_image_data)
        self.logger.debug(f"Image analysis found {len(detections)} detections.")

        # 3. Logique de décision pour choisir la PROCHAINE sous-commande
        if not detections:
            # Balise non trouvée: Lancer une recherche
            self.logger.info("Beacon NOT detected. Initiating SEARCH turn.")
            search_angle = math.radians(15) # Tourner de 15 degrés pour chercher
            self.current_sub_command = Tourner(search_angle, self.vitesse_rotation * 0.5, self.adapter)
            self.current_sub_command.start()
        else:
            # Balise trouvée
            detection = detections[0]
            center_x, _ = detection["center"]
            radius = detection["radius"]
            self.logger.debug(f"Beacon detected at center=({center_x},{_}), radius={radius:.1f}")

            # 4. Vérifier si assez proche
            if radius >= self.tolerance_radius:
                self.logger.info(f"Beacon REACHED (radius {radius:.1f} >= {self.tolerance_radius}). Initiating STOP.")
                self.current_sub_command = Arreter(self.adapter)
                self.current_sub_command.start()
                self.finished = True # La stratégie est terminée
            else:
                # 5. Calculer l'erreur angulaire
                image_width = 400 # A AJUSTER SI NÉCESSAIRE
                center_image_x = image_width / 2
                error_x = center_x - center_image_x
                fov_horizontal = 60 # degrés, A AJUSTER SI NÉCESSAIRE
                angle_error = math.degrees(math.atan((error_x / center_image_x) * math.tan(math.radians(fov_horizontal / 2))))
                self.logger.debug(f"Calculated angular error: {angle_error:.2f} degrees.")

                # 6. Décider entre Tourner et Avancer
                if abs(angle_error) >= self.tolerance_angle:
                    # Non aligné: Lancer commande Tourner
                    self.logger.info(f"MISALIGNED (error {angle_error:.2f} >= {self.tolerance_angle}). Initiating TURN by {angle_error:.1f} deg.")
                    # Tourner de l'angle d'erreur calculé
                    self.current_sub_command = Tourner(math.radians(angle_error), self.vitesse_rotation, self.adapter)
                    self.current_sub_command.start()
                else:
                    # Aligné: Lancer commande Avancer
                    self.logger.info(f"ALIGNED (error {angle_error:.2f} < {self.tolerance_angle}). Initiating ADVANCE by {self.step_distance}cm.")
                    # Avancer d'une petite distance fixe
                    self.current_sub_command = Avancer(self.step_distance, self.vitesse_avance, self.adapter)
                    self.current_sub_command.start()
        
        # La stratégie elle-même n'est pas terminée (sauf si Arreter a été appelée)
        # Elle retournera False car une sous-commande vient d'être lancée (ou on attend une image)
        return False 

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
