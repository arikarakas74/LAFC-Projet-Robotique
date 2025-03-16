import math
import numpy as np
from model.map_model import MapModel
from utils.geometry3d import normalize_angle_3d, rotation_matrix_from_angles

class RobotModel:
    """3D robot model with physics properties."""
    
    # Physical constants
    WHEEL_BASE_WIDTH = 20.0  # Distance between wheels (cm)
    WHEEL_DIAMETER = 5.0     # Wheel diameter (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    HEIGHT = 15.0            # Height of the robot (cm)

    def __init__(self, map_model: MapModel):
        """Initialize the robot model with default values."""
        self.map_model = map_model
        
        # 3D position (x, y, z)
        self.x = 400  # Default position center of map
        self.y = 300
        self.z = 0.0  # Start at ground level
        
        # Use the start position from map model if available
        if map_model.start_position:
            self.x, self.y, self.z = map_model.start_position
        
        # 3D orientation (pitch, yaw, roll)
        self.pitch = 0.0  # X-axis rotation (up/down)
        self.yaw = 0.0    # Y-axis rotation (left/right) - primary direction
        self.roll = 0.0   # Z-axis rotation (tilt)
        
        # Motor speeds in degrees per second
        self.motor_speeds = {"left": 0, "right": 0}
        
        # Motor positions in degrees (for tracking rotation)
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

    def set_motor_speed(self, motor: str, dps: float):
        """Sets the speed of a motor in degrees per second with validation."""
        if motor in ["left", "right"]:
            self.motor_speeds[motor] = max(-1000, min(1000, dps))

    def update_motors(self, delta_time: float):
        """Updates the motor positions based on current speeds."""
        self.motor_positions["left"] += self.motor_speeds["left"] * delta_time
        self.motor_positions["right"] += self.motor_speeds["right"] * delta_time
        
        # Normalize motor positions to keep them in a reasonable range
        self.motor_positions["left"] %= 360.0
        self.motor_positions["right"] %= 360.0

    def get_state(self) -> dict:
        """Returns the current state of the robot."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pitch": self.pitch,
            "yaw": self.yaw,
            "roll": self.roll,
            "left_speed": self.motor_speeds["left"],
            "right_speed": self.motor_speeds["right"],
            "left_position": self.motor_positions["left"],
            "right_position": self.motor_positions["right"]
        }

    def get_position(self) -> tuple:
        """Returns the current 3D position as a tuple."""
        return (self.x, self.y, self.z)

    def get_orientation(self) -> tuple:
        """Returns the current 3D orientation as Euler angles."""
        return (self.pitch, self.yaw, self.roll)

    def get_forward_vector(self) -> np.ndarray:
        """Returns a unit vector pointing in the robot's forward direction."""
        # Create rotation matrix from current orientation
        rotation = rotation_matrix_from_angles(self.pitch, self.yaw, self.roll)
        
        # Forward vector is along the X-axis in the robot's local frame
        forward = np.array([1.0, 0.0, 0.0])
        
        # Transform to world coordinates
        world_forward = np.dot(rotation, forward)
        
        # Normalize to unit length
        return world_forward / np.linalg.norm(world_forward)