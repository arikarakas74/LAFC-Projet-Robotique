import math
import logging

class RobotReelAdapter:
    """
    Adaptateur permettant de suivre la position et l'orientation du robot
    en utilisant uniquement les encodeurs moteurs.
    """

    def __init__(self, robot, initial_position=[0, 0], initial_angle=0.0):
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
        self.current_position = initial_position
        self.wheel_radius = robot.WHEEL_RADIUS
        self.track_width = robot.WHEEL_BASE_WIDTH
        self.delta_left = None
        self.delta_right = None

    def calculate_distance_traveled(self):
        """
        Calcule la distance parcourue par le robot en fonction des rotations des roues.
        Retourne la distance parcourue en cm.
        """
        # Lire les positions actuelles des moteurs
        left_motor_pos = self.robot.motor_positions["left"]
        right_motor_pos = self.robot.motor_positions["right"]

        # Calculer les différences entre les positions du moteur
        if self.delta_left is None or self.delta_right is None:
            self.delta_left = left_motor_pos - self.last_left_encoder
            self.delta_right = right_motor_pos - self.last_right_encoder

        # Calculer la distance parcourue par chaque roue
        left_distance = math.radians(self.delta_left) * self.wheel_radius
        right_distance = math.radians(self.delta_right) * self.wheel_radius

        traveled_distance = (left_distance + right_distance) / 2.0

        self.last_left_encoder = left_motor_pos
        self.last_right_encoder = right_motor_pos

        return traveled_distance

    def real_position_calc(self):
        """
        Met à jour et renvoie la position actuelle (x, y) du robot en fonction des différences entre les lectures des roues.
        """
        self.delta_left = self.robot.motor_positions["left"] - self.last_left_encoder
        self.delta_right = self.robot.motor_positions["right"] - self.last_right_encoder

        distance_moved = self.calculate_distance_traveled()
        current_angle_rad = self.calculate_angle()

        delta_x = distance_moved * math.cos(current_angle_rad)
        delta_y = distance_moved * math.sin(current_angle_rad)

        self.current_position[0] += delta_x
        self.current_position[1] += delta_y

        self.delta_left = None
        self.delta_right = None

        return self.current_position

    def calculate_angle(self):
        """
        Calcule le changement d'angle en fonction des rotations des moteurs.
        Retourne l'angle en radian.
        """
        if self.delta_left is None or self.delta_right is None:
            self.delta_left = self.robot.motor_positions["left"] - self.last_left_encoder
            self.delta_right = self.robot.motor_positions["right"] - self.last_right_encoder

        if self.delta_left == 0 and self.delta_right == 0:
            return self.current_angle
        
        # Conversion des rotations en distance parcourue
        left_distance = math.radians(self.delta_left) * self.wheel_radius
        right_distance = math.radians(self.delta_right) * self.wheel_radius

        # Calcul du changement d'angle du robot
        angle_change = (left_distance - right_distance) / self.track_width

        self.current_angle += angle_change

        return self.current_angle  

class Accelerer:
    """
    Commande pour accélérer le robot progressivement jusqu'à une vitesse cible.
    """

    def __init__(self, target_speed, duration):
        """
        Initialise la commande d'accélération.
        :param target_speed: Vitesse cible à atteindre
        :param duration: Durée pour atteindre la vitesse cible (en secondes)
        """
        self.target_speed = target_speed  # Vitesse maximale à atteindre
        self.duration = duration  # Temps nécessaire pour atteindre la vitesse
        self.elapsed = 0  # Temps écoulé depuis le début de l'accélération
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Accelerer")

    def start(self, robot):
        """
        Démarre la commande d'accélération.
        :param robot: Instance du modèle de robot
        """
        self.elapsed = 0  # Réinitialise le temps écoulé
        self.started = True
        self.logger.info("Acceleration started.")

    def step(self, robot, delta_time):
        """
        Met à jour l'état de l'accélération en fonction du temps écoulé.
        :param robot: Instance du modèle de robot
        :param delta_time: Temps écoulé depuis la dernière mise à jour
        """
        if not self.started:
            self.start(robot)

        self.elapsed += delta_time
        fraction = min(self.elapsed / self.duration, 1.0)  # Calcul du pourcentage d'accélération
        speed = self.target_speed * fraction  # Augmente progressivement la vitesse

        robot.set_motor_speed("left", speed)
        robot.set_motor_speed("right", speed)

        if self.elapsed >= self.duration:
            self.finished = True
            self.logger.info("Acceleration finished.")

        return self.finished

    def is_finished(self):
        """
        Vérifie si la commande est terminée.
        """
        return self.finished

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