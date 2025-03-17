import math
from model.robot import RobotModel

class RobotReelAdapter:
    """
    """
    def __init__(self, robot: RobotModel, initial_position=(0, 0), initial_angle=0.0):
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

        delta_theta = (right_distance - left_distance) / self.track_width

        # En cas de rotation significatif
        if abs(delta_theta) > 1e-6:
            R = (left_distance + right_distance) / (2 * delta_theta)
            traveled_distance = abs(delta_theta * R)
        else:
            # S'il n'y a pas de rotation significatif, utiliser la distance moyenne
            traveled_distance = (left_distance + right_distance) / 2.0

        self.last_left_encoder = left_motor_pos
        self.last_right_encoder = right_motor_pos

        return traveled_distance

    def real_position_calc(self):
        """
        Updates and returns the current (x, y) position of the robot based on the
        differences in wheel encoder readings.
        """

    def calculate_angle_change(self):
        """
        Calcule le changement d'angle en fonction des rotations des moteurs.
        Retourne la variation d'angle en radians.
        """
        # Lire les positions actuelles des moteurs
        left_motor_pos = self.robot.motor_positions["left"]
        right_motor_pos = self.robot.motor_positions["right"]

        # Calcul des variations des encodeurs
        delta_left = left_motor_pos - self.last_motor_positions["left"]
        delta_right = right_motor_pos - self.last_motor_positions["right"]

        # Conversion des rotations en distance parcourue
        left_distance = (delta_left / 360.0) * (2 * math.pi * self.robot.WHEEL_RADIUS)
        right_distance = (delta_right / 360.0) * (2 * math.pi * self.robot.WHEEL_RADIUS)

        # Calcul du changement d'angle du robot
        angle_change = (right_distance - left_distance) / self.track_width

        return angle_change  # Retourne uniquement la variation d'angle en radians