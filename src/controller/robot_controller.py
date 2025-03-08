import math
import logging
import threading
from utils.geometry import normalize_angle

# Initialisation du logger pour le dessin de carré
square_logger = logging.getLogger('traceability.square')
square_logger.setLevel(logging.INFO)
square_handler = logging.FileHandler('traceability_square.log')
square_formatter = logging.Formatter('%(asctime)s - %(message)s')
square_handler.setFormatter(square_formatter)
square_logger.addHandler(square_handler)

SPEED_MULTIPLIER = 8.0

class RobotController:
    WHEEL_BASE_WIDTH = 20.0  # Correspond à RobotModel
    WHEEL_DIAMETER = 5.0
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    SPEED_STEP = 30.0

    def __init__(self, robot_model, map_model, cli_mode=True):
        self.robot_model = robot_model
        self.map_model = map_model
        self.drawing_square = False
        self.square_step = 0
        self.side_length = 0
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_angle = 0.0
        # Liste pour enregistrer les coins
        self.corners = []
        
        # Logger pour la traçabilité des positions
        self.position_logger = logging.getLogger('traceability.positions')
        self.position_logger.setLevel(logging.INFO)
        position_handler = logging.FileHandler('traceability_positions.log')
        position_formatter = logging.Formatter('%(asctime)s - Position: %(message)s')
        position_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(position_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(console_handler)
        
        # Démarrage du thread de saisie uniquement en mode CLI
        if cli_mode:
            self._start_input_thread()

    def _start_input_thread(self):
        threading.Thread(target=self._read_input, daemon=True).start()

    def _read_input(self):
        while True:
            key = input("Press a key (q/a/e/d/w/s): ").strip()
            if key == 'q':
                self.increase_left_speed()
            elif key == 'a':
                self.decrease_left_speed()
            elif key == 'e':
                self.increase_right_speed()
            elif key == 'd':
                self.decrease_right_speed()
            elif key == 'w':
                self.move_forward()
            elif key == 's':
                self.move_backward()

    def draw_square(self, side_length_cm):
        """Démarre le dessin d'un carré et enregistre les coins dans le fichier de log."""
        if not self.drawing_square:
            self.drawing_square = True
            self.square_step = 0
            self.side_length = side_length_cm
            square_logger.info(f"Début du dessin d'un carré de côté {side_length_cm} cm")
            # Initialisation de la liste des coins (premier coin = position de départ)
            self.corners = []
            self.corners.append((self.robot_model.x, self.robot_model.y))
            square_logger.info(f"Coin enregistré: ({self.robot_model.x}, {self.robot_model.y})")
            self._start_new_side()

    def _start_new_side(self):
        """Initialise un nouveau côté avec position et angle de départ."""
        self.start_x = self.robot_model.x
        self.start_y = self.robot_model.y
        self.start_angle = self.robot_model.direction_angle
        self.set_motor_speed("left", 250)
        self.set_motor_speed("right", 250)
        square_logger.info("Nouveau côté commencé")

    def _start_rotation(self):
        """Démarre la rotation pour passer à l'angle suivant."""
        self.start_angle = self.robot_model.direction_angle
        self.set_motor_speed("left", 160)
        self.set_motor_speed("right", -160)
        square_logger.info("Rotation démarrée")

    def update_physics(self, delta_time):
        if delta_time <= 0:
            return

        # Calculs pour la mise à jour physique du robot
        left_speed = self.robot_model.motor_speeds["left"]
        right_speed = self.robot_model.motor_speeds["right"]

        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (left_velocity - right_velocity) / self.WHEEL_BASE_WIDTH

        effective_delta_time = delta_time * SPEED_MULTIPLIER

        if left_velocity == right_velocity:
            new_x = self.robot_model.x + linear_velocity * math.cos(self.robot_model.direction_angle) * effective_delta_time
            new_y = self.robot_model.y + linear_velocity * math.sin(self.robot_model.direction_angle) * effective_delta_time
            new_angle = self.robot_model.direction_angle
        else:
            R = (self.WHEEL_BASE_WIDTH / 2) * (left_velocity + right_velocity) / (left_velocity - right_velocity)
            delta_theta = angular_velocity * effective_delta_time

            Cx = self.robot_model.x - R * math.sin(self.robot_model.direction_angle)
            Cy = self.robot_model.y + R * math.cos(self.robot_model.direction_angle)

            new_x = Cx + R * math.sin(self.robot_model.direction_angle + delta_theta)
            new_y = Cy - R * math.cos(self.robot_model.direction_angle + delta_theta)
            new_angle = self.robot_model.direction_angle + delta_theta

        self.robot_model.update_position(new_x, new_y, new_angle)
        self.robot_model.update_motors(delta_time)
        
        # Enregistrement de la nouvelle position pour la traçabilité
        self.position_logger.info(f"x={self.robot_model.x:.2f}, y={self.robot_model.y:.2f}, angle={math.degrees(self.robot_model.direction_angle):.2f}°")

        # Logique pour la séquence du carré
        if self.drawing_square:
            if self.square_step % 2 == 0:  # Phase linéaire
                distance = math.hypot(self.robot_model.x - self.start_x,
                                      self.robot_model.y - self.start_y)
                if distance >= max(self.side_length - 0.5, self.side_length * 0.98):
                    square_logger.info(f"Côté terminé, distance atteinte = {distance:.2f} cm, étape {self.square_step}")
                    self.stop()
                    self.square_step += 1

                    # Enregistrement du coin (fin du côté)
                    coin = (self.robot_model.x, self.robot_model.y)
                    self.corners.append(coin)
                    square_logger.info(f"Coin enregistré: {coin}")

                    if self.square_step < 8:
                        square_logger.info("Passage à la phase de rotation")
                        self._start_rotation()
            else:  # Phase angulaire
                current_angle = normalize_angle(self.robot_model.direction_angle)
                target_angle = normalize_angle(self.start_angle + math.pi / 2)
                angle_error = normalize_angle(target_angle - current_angle)

                if abs(angle_error) < math.radians(5):
                    self.set_motor_speed("left", 60 * (angle_error / math.radians(5)))
                    self.set_motor_speed("right", -60 * (angle_error / math.radians(5)))

                if abs(angle_error) <= math.radians(0.1):
                    square_logger.info(f"Rotation terminée, étape {self.square_step}")
                    self.stop()
                    self.robot_model.update_position(
                        self.robot_model.x,
                        self.robot_model.y,
                        target_angle  # Forçage de l'angle exact
                    )
                    self.square_step += 1

                    if self.square_step < 8:
                        square_logger.info("Démarrage d'un nouveau côté")
                        self._start_new_side()
                    else:
                        square_logger.info("Dessin du carré terminé")
                        self.drawing_square = False
                        # Vérification de la validité du carré
                        if self.check_square():
                            square_logger.info("Le carré a été correctement dessiné.")
                        else:
                            square_logger.info("Le carré n'est pas correctement dessiné.")

    def check_square(self, distance_tolerance=0.1, angle_tolerance=0.1745):
        """
        Vérifie que le carré est correctement tracé.
        - distance_tolerance : tolérance relative pour la longueur des côtés (10% par défaut)
        - angle_tolerance : tolérance en radians pour l'angle (environ 10°)
        """
        # Le carré doit avoir au moins 5 coins (le premier répété à la fin)
        if len(self.corners) < 5:
            return False

        # Vérifier que le premier et le dernier coin se rejoignent
        first = self.corners[0]
        last = self.corners[-1]
        if math.hypot(last[0] - first[0], last[1] - first[1]) > distance_tolerance * self.side_length:
            return False

        # Vérifier la longueur de chaque côté
        for i in range(1, len(self.corners)):
            d = math.hypot(self.corners[i][0] - self.corners[i-1][0],
                           self.corners[i][1] - self.corners[i-1][1])
            if abs(d - self.side_length) > distance_tolerance * self.side_length:
                return False

        # Vérifier que les angles entre les côtés sont proches de 90°
        def angle_between(v1, v2):
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            norm1 = math.hypot(v1[0], v1[1])
            norm2 = math.hypot(v2[0], v2[1])
            if norm1 == 0 or norm2 == 0:
                return 0
            cos_angle = dot / (norm1 * norm2)
            cos_angle = max(-1, min(1, cos_angle))
            return math.acos(cos_angle)

        for i in range(1, len(self.corners) - 1):
            v1 = (self.corners[i][0] - self.corners[i-1][0],
                  self.corners[i][1] - self.corners[i-1][1])
            v2 = (self.corners[i+1][0] - self.corners[i][0],
                  self.corners[i+1][1] - self.corners[i][1])
            angle = angle_between(v1, v2)
            if abs(angle - math.pi/2) > angle_tolerance:
                return False

        return True

    def set_motor_speed(self, motor, speed):
        self.robot_model.set_motor_speed(motor, speed)

    def stop(self):
        self.set_motor_speed("left", 0)
        self.set_motor_speed("right", 0)

    def increase_left_speed(self):
        new_speed = self.robot_model.motor_speeds["left"] + self.SPEED_STEP
        self.set_motor_speed("left", new_speed)

    def decrease_left_speed(self):
        new_speed = self.robot_model.motor_speeds["left"] - self.SPEED_STEP
        self.set_motor_speed("left", new_speed)

    def increase_right_speed(self):
        new_speed = self.robot_model.motor_speeds["right"] + self.SPEED_STEP
        self.set_motor_speed("right", new_speed)

    def decrease_right_speed(self):
        new_speed = self.robot_model.motor_speeds["right"] - self.SPEED_STEP
        self.set_motor_speed("right", new_speed)

    def move_forward(self):
        self.set_motor_speed("left", self.robot_model.motor_speeds["left"] + self.SPEED_STEP)
        self.set_motor_speed("right", self.robot_model.motor_speeds["right"] + self.SPEED_STEP)

    def move_backward(self):
        self.set_motor_speed("left", self.robot_model.motor_speeds["left"] - self.SPEED_STEP)
        self.set_motor_speed("right", self.robot_model.motor_speeds["right"] - self.SPEED_STEP)
