import math
import numpy as np
from model.map_model import MapModel
from utils.geometry import normalize_angle
from utils.geometry3d import normalize_angle_3d, rotation_matrix_from_angles

class RobotModel:
    WHEEL_BASE_WIDTH = 20.0  # cm
    WHEEL_DIAMETER = 5.0     # cm
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    HEIGHT = 15.0            # cm - height of the robot

    def __init__(self, map_model: MapModel):
        print("init robot")
        self.map_model = map_model
        # 3D position (x, y, z)
        self.x, self.y = map_model.start_position
        self.z = 0.0  # Start at ground level
        
        # 3D orientation (pitch, yaw, roll)
        self.pitch = 0.0  # X-axis rotation (up/down)
        self.yaw = 0.0    # Y-axis rotation (left/right) - equivalent to the 2D direction_angle
        self.roll = 0.0   # Z-axis rotation (tilt)
        
        self.motor_speeds = {"left": 0, "right": 0}
        self.motor_positions = {"left": 0, "right": 0}

    def update_position(self, new_x: float, new_y: float, new_z: float, 
                         new_pitch: float, new_yaw: float, new_roll: float):
        """Updates the robot's 3D position and orientation after checking for collisions."""
        if not (self.map_model.is_collision_3d(new_x, new_y, new_z) or 
                self.map_model.is_out_of_bounds_3d(new_x, new_y, new_z)):
            self.x = new_x
            self.y = new_y
            self.z = new_z
            self.pitch, self.yaw, self.roll = normalize_angle_3d(new_pitch, new_yaw, new_roll)

    def set_motor_speed(self, motor: str, dps: int):
        """Sets the speed of a motor with validation."""
        if motor in ["left", "right"]:
            self.motor_speeds[motor] = max(-1000, min(1000, dps))

    def get_state(self) -> dict:
        """Returns a snapshot of the current state in 3D."""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'pitch': self.pitch,
            'yaw': self.yaw,  # equivalent to the old 'angle'
            'roll': self.roll,
            'left_speed': self.motor_speeds["left"],
            'right_speed': self.motor_speeds["right"]
        }
        
    def update_motors(self, delta_time):
        """Updates the motor positions with the elapsed time."""
        for motor in ["left", "right"]:
            self.motor_positions[motor] += self.motor_speeds[motor] * delta_time
            
    def get_transformation_matrix(self) -> np.ndarray:
        """Returns the 4x4 transformation matrix for the robot's current position and orientation."""
        # Create the rotation matrix from Euler angles
        rotation = rotation_matrix_from_angles(self.pitch, self.yaw, self.roll)
        
        # Add translation component
        rotation[0, 3] = self.x
        rotation[1, 3] = self.y
        rotation[2, 3] = self.z
        
        return rotation