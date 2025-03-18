import math
import logging

class RobotReelAdapter:
    """
    Adaptateur permettant de suivre la position et l'orientation du robot
    en utilisant uniquement les encodeurs moteurs.
    """

    def __init__(self, robot, initial_position=None, initial_angle=0.0):
        """
        Initialise l'adaptateur avec les informations initiales du robot.
        :param robot: Instance du modèle de robot
        :param initial_position: Position initiale supposée du robot (x, y)
        :param initial_angle: Angle initial supposé du robot (radians)
        """
        self.robot = robot
        self.last_left_encoder = robot.motor_positions["left"]
        self.last_right_encoder = robot.motor_positions["right"]
        self.current_angle = initial_angle  # L'angle du robot en radians
        self.current_position = list(initial_position) if initial_position else [0.0, 0.0]
        self.wheel_radius = robot.WHEEL_RADIUS
        self.track_width = robot.WHEEL_BASE_WIDTH

    def calculate_distance_traveled(self):
        """
        Calcule la distance parcourue par le robot en fonction des rotations des roues.
        Retourne la distance parcourue en cm.
        """
        # Lire les positions actuelles des moteurs
        left_motor_pos = self.robot.motor_positions["left"]
        right_motor_pos = self.robot.motor_positions["right"]

        # Calculer les différences entre les positions du moteur
        delta_left = left_motor_pos - self.last_left_encoder
        delta_right = right_motor_pos - self.last_right_encoder

        # Calculer la distance parcourue par chaque roue
        left_distance = math.radians(delta_left) * self.wheel_radius
        right_distance = math.radians(delta_right) * self.wheel_radius

        # Distance moyenne parcourue
        traveled_distance = (left_distance + right_distance) / 2.0

        # Mise à jour des positions des encodeurs
        self.last_left_encoder = left_motor_pos
        self.last_right_encoder = right_motor_pos

        return traveled_distance

    def real_position_calc(self):
        """
        Met à jour et renvoie la position actuelle (x, y) du robot en fonction des encodeurs moteurs.
        """
        distance_moved = self.calculate_distance_traveled()
        angle_change = self.calculate_angle()  

        self.current_angle += angle_change 

        # Yeni (x, y) konumunu hesapla
        delta_x = distance_moved * math.cos(self.current_angle)
        delta_y = distance_moved * math.sin(self.current_angle)

        self.current_position[0] += delta_x
        self.current_position[1] += delta_y

        return tuple(self.current_position)  

    def calculate_angle(self):
        """
        Calcule le changement d'angle en fonction des rotations des moteurs.
        Retourne la variation d'angle en **radians** (PAS EN DEGRÉS!).
        """
        delta_left = self.robot.motor_positions["left"] - self.last_left_encoder
        delta_right = self.robot.motor_positions["right"] - self.last_right_encoder

        # Conversion des rotations en distance parcourue
        left_distance = math.radians(delta_left) * self.wheel_radius
        right_distance = math.radians(delta_right) * self.wheel_radius

        # Calcul du changement d'angle du robot
        angle_change = (right_distance - left_distance) / self.track_width

        self.current_angle += angle_change  # Garde l'angle retournée

        return angle_change  

class Avancer:
    """
    Commande pour faire avancer le robot d'une certaine distance
    en utilisant uniquement les encodeurs moteurs.
    """

    def __init__(self, distance_cm, vitesse):
        """
        Initialise la commande d'avancement.
        :param distance_cm: Distance cible à parcourir (en cm)
        :param vitesse: Vitesse de déplacement
        """
        self.distance_cm = distance_cm  # Distance cible à parcourir
        self.vitesse = vitesse  # Vitesse du robot
        self.started = False
        self.finished = False
        self.initial_distance = None  # Distance initiale enregistrée
        self.logger = logging.getLogger("strategy.Avancer")

    def start(self, robot, adapter):
        """
        Démarre la commande d'avancement.
        :param robot: Instance du modèle de robot
        :param adapter: Instance de RobotReelAdapter pour calculer la distance
        """
        self.initial_distance = adapter.calculate_distance_traveled()  # Enregistre la distance initiale
        robot.set_motor_speed("left", self.vitesse)
        robot.set_motor_speed("right", self.vitesse)
        self.started = True
        self.logger.info("Avancer started.")

    def step(self, robot, adapter, delta_time):
        """
        Met à jour l'état du déplacement et vérifie si la distance cible est atteinte.
        :param robot: Instance du modèle de robot
        :param adapter: Instance de RobotReelAdapter
        :param delta_time: Temps écoulé depuis la dernière mise à jour (c'est ajouté si nous voulons faire des test sur temps et vitesse après)
        """
        if not self.started:
            self.start(robot, adapter)

        # Calcule la distance parcourue depuis le début
        current_distance = adapter.calculate_distance_traveled() - self.initial_distance

        if current_distance >= self.distance_cm:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Avancer finished.")

        return self.finished

    def is_finished(self):
        """
        Vérifie si la commande est terminée.
        """
        return self.finished