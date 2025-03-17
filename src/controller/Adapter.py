import math
from model.robot import RobotModel

class RobotReelAdapter:
    """
    """
    def __init__(self, robot: RobotModel):
        self.robot = robot
        self.wheel_radius = robot.WHEEL_RADIUS
        self.track_width = robot.WHEEL_BASE_WIDTH

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