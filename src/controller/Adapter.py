import math
import time

class RobotReelAdapter:
    """
    """
    def __init__(self, robot, initial_position=[0, 0], initial_angle=0.0):
        self.robot = robot
        self.last_left_encoder = robot.motor_positions["left"]
        self.last_right_encoder = robot.motor_positions["right"]
        self.current_angle = initial_angle  # L'angle du robot en radians
        self.current_position = initial_position
        self.wheel_radius = robot.WHEEL_RADIUS
        self.track_width = robot.WHEEL_BASE_WIDTH

    def calculate_distance_traveled(self):
        """
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

        traveled_distance = (left_distance + right_distance) / 2.0

        self.last_left_encoder = left_motor_pos
        self.last_right_encoder = right_motor_pos

        return traveled_distance

    def real_position_calc(self):
        """
        Met à jour et renvoie la position actuelle (x, y) du robot en fonction des différences entre les lectures des roues.
        """
        distance_moved = self.calculate_distance_traveled()

        current_angle_deg = self.calculate_angle()
        current_angle_rad = math.radians(current_angle_deg)

        delta_x = distance_moved * math.cos(current_angle_rad)
        delta_y = distance_moved * math.sin(current_angle_rad)

        self.current_position[0] += delta_x
        self.current_position[1] += delta_y

        return self.current_position

    def calculate_angle(self):
        """
        Calcule le changement d'angle en fonction des rotations des moteurs.
        Retourne la variation d'angle en radians.
        """
        delta_left = self.robot.motor_positions["left"] - self.last_left_encoder
        delta_right = self.robot.motor_positions["right"] - self.last_right_encoder

        # Conversion des rotations en distance parcourue
        left_distance = math.radians(delta_left) * self.wheel_radius
        right_distance = math.radians(delta_right) * self.wheel_radius

        # Calcul du changement d'angle du robot
        angle_change = (right_distance - left_distance) / self.track_width

        self.current_angle += angle_change

        return math.degrees(self.current_angle)