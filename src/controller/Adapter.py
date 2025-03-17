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