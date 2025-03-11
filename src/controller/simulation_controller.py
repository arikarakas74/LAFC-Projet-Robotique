import threading
import time
import math
import logging
from typing import Callable, List
from model.robot import RobotModel
from controller.robot_controller import RobotController
from utils.geometry import normalize_angle

# --- Configuration des loggers ---

# Logger pour la traçabilité du dessin du carré
square_logger = logging.getLogger('traceability.square')
square_logger.setLevel(logging.INFO)
square_handler = logging.FileHandler('traceability_square.log')
square_formatter = logging.Formatter('%(asctime)s - %(message)s')
square_handler.setFormatter(square_formatter)
square_logger.addHandler(square_handler)

# Multiplicateur pour accélérer la simulation
SPEED_MULTIPLIER = 8.0

class SimulationController:
    """
    Contrôleur de simulation pour le déplacement du robot et le dessin d'un carré.
    
    Gère à la fois la mise à jour en temps réel de la position du robot et la séquence
    de commandes pour tracer un carré (alternance de phases linéaires et de rotations).
    """
    WHEEL_BASE_WIDTH = 20.0  # Distance entre les roues (cm)
    WHEEL_DIAMETER = 5.0     # Diamètre des roues (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2

    def __init__(self, map_model, robot_model):
        """
        Initialise le contrôleur de simulation.
        
        :param map_model: Modèle de la carte (contenant par exemple la position de départ)
        :param robot_model: Modèle du robot (position, moteurs, etc.)
        """
        self.robot_model = robot_model
        self.map_model = map_model
        self.robot_controller = RobotController(self.robot_model, self.map_model)
        self.simulation_running = False
        self.listeners: List[Callable[[dict], None]] = []
        self.update_interval = 0.02  # Intervalle de mise à jour : 50 Hz

        # Variables de contrôle pour le dessin du carré
        self.drawing_square = False
        self.square_step = 0
        self.side_length = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_angle = 0.0
        self.corners = []  # Liste des coins enregistrés

        # Logger pour la traçabilité des positions du robot
        self.position_logger = logging.getLogger('traceability.positions')
        self.position_logger.setLevel(logging.INFO)
        position_handler = logging.FileHandler('traceability_positions.log')
        position_formatter = logging.Formatter('%(asctime)s - Position: %(message)s')
        position_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(position_handler)

        # Logger pour afficher en console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(console_handler)

        self.simulation_thread = None

    def add_state_listener(self, callback: Callable[[dict], None]):
        """Ajoute un callback qui sera notifié à chaque mise à jour de l'état du robot."""
        self.listeners.append(callback)

    def _notify_listeners(self):
        """Notifie tous les listeners avec l'état actuel du robot."""
        state = self.robot_model.get_state()
        for callback in self.listeners:
            callback(state)

    def run_simulation(self):
        """Démarre la simulation dans un thread séparé."""
        if self.simulation_running:
            return

        # Positionner le robot au point de départ si nécessaire
        start_pos = self.map_model.start_position
        if (self.robot_model.x, self.robot_model.y) != start_pos:
            self.robot_model.x, self.robot_model.y = start_pos

        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.simulation_thread.start()

    def run_loop(self):
        """Boucle principale de la simulation, s'exécutant dans un thread séparé."""
        last_time = time.time()
        while self.simulation_running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            self.update_physics(delta_time)
            self._notify_listeners()
            time.sleep(self.update_interval)

    def update_physics(self, delta_time: float):
        """
        Met à jour la position et l'orientation du robot en fonction du temps écoulé.
        
        :param delta_time: Temps écoulé depuis la dernière mise à jour
        """
        if delta_time <= 0:
            return

        # --- Calcul des vitesses à partir des moteurs ---
        left_speed = self.robot_model.motor_speeds["left"]
        right_speed = self.robot_model.motor_speeds["right"]

        # Conversion des vitesses (degrés/s) en vitesse linéaire (cm/s)
        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

        # Calcul de la vitesse linéaire et angulaire
        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (left_velocity - right_velocity) / self.WHEEL_BASE_WIDTH

        # Application du multiplicateur de vitesse pour la simulation
        effective_delta = delta_time * SPEED_MULTIPLIER

        # --- Mise à jour de la position en fonction du type de mouvement ---
        if left_velocity == right_velocity:
            # Mouvement en ligne droite
            new_x = self.robot_model.x + linear_velocity * math.cos(self.robot_model.direction_angle) * effective_delta
            new_y = self.robot_model.y + linear_velocity * math.sin(self.robot_model.direction_angle) * effective_delta
            new_angle = self.robot_model.direction_angle
        else:
            # Mouvement circulaire (arc de cercle)
            delta_theta = angular_velocity * effective_delta
            R = (self.WHEEL_BASE_WIDTH / 2) * (left_velocity + right_velocity) / (left_velocity - right_velocity)
            # Centre de rotation
            center_x = self.robot_model.x - R * math.sin(self.robot_model.direction_angle)
            center_y = self.robot_model.y + R * math.cos(self.robot_model.direction_angle)
            # Nouvelle position calculée sur l'arc
            new_x = center_x + R * math.sin(self.robot_model.direction_angle + delta_theta)
            new_y = center_y - R * math.cos(self.robot_model.direction_angle + delta_theta)
            new_angle = self.robot_model.direction_angle + delta_theta

        # Mise à jour du modèle du robot
        self.robot_model.update_position(new_x, new_y, new_angle)
        self.robot_model.update_motors(delta_time)

        # Enregistrement de la position actuelle pour la traçabilité
        self.position_logger.info(
            f"x={self.robot_model.x:.2f}, y={self.robot_model.y:.2f}, angle={math.degrees(self.robot_model.direction_angle):.2f}°"
        )

        # --- Gestion du dessin du carré ---
        if self.drawing_square:
            if self.square_step % 2 == 0:
                self._handle_square_linear_phase()
            else:
                self._handle_square_rotation_phase()

    def _handle_square_linear_phase(self):
        """Gère la phase de déplacement linéaire (dessin d'un côté du carré)."""
        distance_travelled = math.hypot(self.robot_model.x - self.start_x,
                                        self.robot_model.y - self.start_y)
        if distance_travelled >= max(self.side_length - 0.5, self.side_length * 0.98):
            square_logger.info(
                f"Côté terminé, distance atteinte = {distance_travelled:.2f} cm, étape {self.square_step}"
            )
            self.robot_model.set_motor_speed("left", 0)
            self.robot_model.set_motor_speed("right", 0)
            self.square_step += 1

            # Enregistrement du coin
            corner = (self.robot_model.x, self.robot_model.y)
            self.corners.append(corner)
            square_logger.info(f"Coin enregistré: {corner}")

            if self.square_step < 8:
                square_logger.info("Passage à la phase de rotation")
                self._start_rotation()

    def _handle_square_rotation_phase(self):
        """Gère la phase de rotation (pour aligner le robot sur le prochain côté)."""
        current_angle = normalize_angle(self.robot_model.direction_angle)
        target_angle = normalize_angle(self.start_angle + math.pi / 2)
        angle_error = normalize_angle(target_angle - current_angle)

        # Ajustement fin de la rotation selon l'erreur angulaire
        if abs(angle_error) < math.radians(5):
            correction_speed = 60 * (angle_error / math.radians(5))
            self.robot_model.set_motor_speed("left", correction_speed)
            self.robot_model.set_motor_speed("right", -correction_speed)

        # Vérification si la rotation est terminée
        if abs(angle_error) <= math.radians(0.1):
            square_logger.info(f"Rotation terminée, étape {self.square_step}")
            self.robot_model.set_motor_speed("left", 0)
            self.robot_model.set_motor_speed("right", 0)
            # Forçage de l'angle exact
            self.robot_model.update_position(
                self.robot_model.x,
                self.robot_model.y,
                target_angle
            )
            self.square_step += 1

            if self.square_step < 8:
                square_logger.info("Démarrage d'un nouveau côté")
                self._start_new_side()
            else:
                square_logger.info("Dessin du carré terminé")
                self.drawing_square = False
                if self.check_square():
                    square_logger.info("Le carré a été correctement dessiné.")
                else:
                    square_logger.info("Le carré n'est pas correctement dessiné.")

    def draw_square(self, side_length_cm: float):
        """
        Démarre le processus de dessin d'un carré.
        
        :param side_length_cm: Longueur d'un côté du carré en centimètres.
        """
        if not self.drawing_square:
            self.drawing_square = True
            self.square_step = 0
            self.side_length = side_length_cm
            square_logger.info(f"Début du dessin d'un carré de côté {side_length_cm} cm")
            # Enregistrement du premier coin (position de départ)
            self.corners = [(self.robot_model.x, self.robot_model.y)]
            square_logger.info(f"Coin enregistré: ({self.robot_model.x}, {self.robot_model.y})")
            self._start_new_side()

    def _start_rotation(self):
        """Initialise la phase de rotation pour passer au côté suivant."""
        self.start_angle = self.robot_model.direction_angle
        # Paramétrage des moteurs pour la rotation (moteur gauche avance, droit recule)
        self.robot_model.set_motor_speed("left", 160)
        self.robot_model.set_motor_speed("right", -160)
        square_logger.info("Rotation démarrée")

    def _start_new_side(self):
        """Prépare le démarrage d'un nouveau côté du carré."""
        self.start_x = self.robot_model.x
        self.start_y = self.robot_model.y
        self.start_angle = self.robot_model.direction_angle
        self.robot_model.set_motor_speed("left", 250)
        self.robot_model.set_motor_speed("right", 250)
        square_logger.info("Nouveau côté commencé")

    def check_square(self, distance_tolerance=0.1, angle_tolerance=0.1745) -> bool:
        """
        Vérifie que le carré a été correctement tracé.
        
        :param distance_tolerance: Tolérance relative sur la longueur des côtés (10% par défaut)
        :param angle_tolerance: Tolérance en radians pour l'angle (environ 10°)
        :return: True si le carré est correct, False sinon.
        """
        # Le carré doit contenir au moins 5 coins (le premier répété à la fin)
        if len(self.corners) < 5:
            return False

        # Vérifier que le premier et le dernier coin se rejoignent
        first_corner = self.corners[0]
        last_corner = self.corners[-1]
        if math.hypot(last_corner[0] - first_corner[0], last_corner[1] - first_corner[1]) > distance_tolerance * self.side_length:
            return False

        # Vérifier la longueur de chaque côté
        for i in range(1, len(self.corners)):
            side_distance = math.hypot(
                self.corners[i][0] - self.corners[i-1][0],
                self.corners[i][1] - self.corners[i-1][1]
            )
            if abs(side_distance - self.side_length) > distance_tolerance * self.side_length:
                return False

        # Vérifier que les angles entre côtés sont proches de 90°
        def angle_between(v1, v2):
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            norm1 = math.hypot(v1[0], v1[1])
            norm2 = math.hypot(v2[0], v2[1])
            if norm1 == 0 or norm2 == 0:
                return 0
            cos_angle = max(-1, min(1, dot / (norm1 * norm2)))
            return math.acos(cos_angle)

        for i in range(1, len(self.corners) - 1):
            vector1 = (
                self.corners[i][0] - self.corners[i-1][0],
                self.corners[i][1] - self.corners[i-1][1]
            )
            vector2 = (
                self.corners[i+1][0] - self.corners[i][0],
                self.corners[i+1][1] - self.corners[i][1]
            )
            angle = angle_between(vector1, vector2)
            if abs(angle - math.pi / 2) > angle_tolerance:
                return False

        return True

    def stop_simulation(self):
        """Arrête la simulation et le contrôleur du robot."""
        self.simulation_running = False
        self.robot_controller.stop()
        if self.simulation_thread:
            self.simulation_thread.join()

    def reset_simulation(self):
        """
        Réinitialise la simulation en arrêtant le contrôleur et en repositionnant le robot
        à la position de départ.
        """
        self.stop_simulation()
        self.robot_model.x, self.robot_model.y = self.map_model.start_position
        self.robot_model.direction_angle = 0.0

    def square(self):
        """Méthode raccourcie pour démarrer le dessin d'un carré de 200 cm de côté."""
        self.draw_square(200)
