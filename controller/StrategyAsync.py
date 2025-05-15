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

# Commande pour tourner d'un angle donné avec une vitesse de référence
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
        self.fast_wheel = self.adapter.fast_wheel
        self.slow_wheel = self.adapter.slow_wheel
        self.started = True
        self.logger.info(f"Début virage: {math.degrees(self.angle_rad):.1f}°")
        print("Commande tourner démarrée.")

    def step(self, delta_time):
        angle = self.adapter.calcule_angle()
        error = self.angle_rad - angle
        tol = math.radians(0.3)  # Tolérance de 0.3°

        close  = abs(error) < math.radians(8)
        coeff  = 0.3 if close else 1.0
        self.adapter.set_motor_speed(self.fast_wheel, self.base_speed * coeff)
        
        # Correction proportionnelle sur la roue lente
        Kp = 0.6
        correction = Kp * math.degrees(error)
        new_slow_speed = self.base_speed * self.speed_ratio * coeff + correction
        new_slow_speed = max(min(new_slow_speed, self.base_speed * coeff), 0)
        self.adapter.slow_speed(new_slow_speed)

        if abs(error) <= tol:
            self.adapter.set_motor_speed("left", 0)
            self.adapter.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info(f"Virage terminé | Erreur: {math.degrees(error):.2f}°")
            return True
        
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



class StopBeforeWall(AsyncCommande):
    """
    Avance à vitesse constante jusqu’à ce que la distance mesurée
    devienne < target. Puis stop et termine.
    """
    def __init__(self, target: float, vitesse_dps: float, adapter):
        super().__init__(adapter)
        self.target = target
        self.vitesse = vitesse_dps
        self.started = False
        self.finished = False

    def start(self):
        self.adapter.set_motor_speed("left",  self.vitesse)
        self.adapter.set_motor_speed("right", self.vitesse)
        self.started = True
        print("[StopBeforeWall] GO !")

    def step(self, dt):
        if not self.started:
            self.start()
        dist = self.adapter.get_distance()
        print(f"[StopBeforeWall] distance={dist:.0f}")
        if dist <= self.target:
            self.adapter.set_motor_speed("left",  0)
            self.adapter.set_motor_speed("right", 0)
            self.finished = True
            print("[StopBeforeWall] Arrêt")
        return self.finished

    def is_finished(self):
        return self.finished



class FollowBeaconByCommandsStrategy(AsyncCommande):
    """
    Stratégie qui suit une balise BLEUE :
      1) Recherche (pivot) si perdue.
      2) Avance droit tant qu’elle est loin (< skip_centering_radius).
      3) Si dans le cône avant, calcule DISTANCE unique pour Avancer.
      4) Lance un seul Avancer(dist_cm) et attend sa fin.
    """
    def __init__(self, adapter, ursina_view,
                 target_radius_px: float      = 160.0,
                 cm_per_px: float             = 0.9,
                 forward_speed: float         = 2000.0,
                 turn_speed_deg: float        = 90.0,
                 skip_centering_radius: float = 4.0,
                 forward_cone_frac: float     = 0.4):
        super().__init__(adapter)
        self.view                   = ursina_view
        self.target_radius_px       = target_radius_px
        self.cm_per_px              = cm_per_px
        self.forward_speed          = forward_speed
        self.turn_speed_deg         = turn_speed_deg
        self.skip_centering_radius  = skip_centering_radius
        self.forward_cone_frac      = forward_cone_frac
        self.composite              = None
        self.finished               = False
        self.logger                 = logging.getLogger("strategy.FollowBeacon")

    def start(self):
        print("[FollowBeacon] start() → moteurs à 0")
        self.adapter.set_motor_speed("left",  0)
        self.adapter.set_motor_speed("right", 0)

    def step(self, delta_time):
        print("[FollowBeacon] step()")
        if self.finished:
            print("  → terminé")
            return True

        # 1) Si un Avancer est en cours, on le poursuit jusqu'à la fin
        if self.composite and not self.composite.is_finished():
            print("  → continuation de l’Avancer en cours")
            running = not self.composite.step(delta_time)
            print(f"    → still running: {running}")
            return not running

        # 2) Récupérer l'image et détecter le beacon
        img = self.view.get_robot_camera_image()
        if img is None:
            print("  → pas d'image, arrêt")
            self.adapter.set_motor_speed("left",  0)
            self.adapter.set_motor_speed("right", 0)
            return False

        beacon = self.view.detect_blue_beacon(img)
        if beacon is None:
            print("  → beacon perdu, pivot recherche")
            self.adapter.set_motor_speed("left",  self.turn_speed_deg)
            self.adapter.set_motor_speed("right", -self.turn_speed_deg)
            return False

        radius_px, cx, _ = beacon
        w = img.shape[1]
        center_px = w // 2
        print(f"  → beacon vu: radius={radius_px:.1f}px, cx={cx}")

        # Si près au beacon, arrete
        if radius_px >= self.target_radius_px * 0.97:   # %3 tolerance
            print("    → Seuil de rayon atteint, ARRET.")
            self.composite = CommandeComposite(self.adapter)
            self.composite.ajouter_commande(Arreter(self.adapter))
            self.composite.start()
            self.composite.step(delta_time)
            self.finished = True
            return True

        # 3) Si très loin, avance droit par un seul Avancer
        if radius_px < self.skip_centering_radius:
            dist_cm = (self.target_radius_px - radius_px) * self.cm_per_px
            print(f"    → loin (radius<{self.skip_centering_radius}), Avancer unique {dist_cm:.1f} cm")
            self._launch_forward(dist_cm, delta_time)
            return False

        # 4) Si dans le cône avant, calcule distance unique
        left_lim  = center_px * (1 - self.forward_cone_frac)
        right_lim = center_px * (1 + self.forward_cone_frac)
        if left_lim <= cx <= right_lim:
            # distance jusqu’à radius cible
            dist_cm = max(0.0, (self.target_radius_px - radius_px) * self.cm_per_px)
            print(f"    → dans cône avant, Avancer unique {dist_cm:.1f} cm")
            # si déjà proche, on termine
            if dist_cm <= 0:
                print("    → déjà dans radius cible, fin")
                self.finished = True
                return True
            self._launch_forward(dist_cm, delta_time)
            return False

        # 5) Sinon, on recentre par pivot avant d’avancer
        if cx > center_px:
            print("    → beacon à droite, pivot à DROITE")
            self.adapter.set_motor_speed("left",  -self.turn_speed_deg)
            self.adapter.set_motor_speed("right",  self.turn_speed_deg)
        else:
            print("    → beacon à gauche, pivot à GAUCHE")
            self.adapter.set_motor_speed("left",   self.turn_speed_deg)
            self.adapter.set_motor_speed("right",  -self.turn_speed_deg)
        return False

    def _launch_forward(self, dist_cm, delta_time):
        """Crée un composite Avancer(dist_cm) et le démarre une fois pour toutes."""
        print(f"      → création de Avancer({dist_cm:.1f} cm)")
        self.composite = CommandeComposite(self.adapter)
        self.composite.ajouter_commande(
            Avancer(dist_cm, self.forward_speed, self.adapter)
        )
        self.composite.start()
        self.composite.step(delta_time)

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
