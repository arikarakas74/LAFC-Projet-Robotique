import math
from model.map_model import MapModel
from utils.geometry import normalize_angle

class RobotModel:
    WHEEL_BASE_WIDTH = 20.0  # cm
    WHEEL_DIAMETER = 5.0     # cm
    WHEEL_RADIUS = WHEEL_DIAMETER / 2

    def __init__(self, map_model: MapModel):
        self.map_model = map_model
        self.x, self.y = map_model.start_position 
        self.direction_angle = 0.0
        self.motor_speeds = {"left": 0, "right": 0}
        self.motor_positions = {"left": 0, "right": 0}
        
        # Camera properties
        self.camera_fov = math.radians(60)  # 60-degree field of view
        self.camera_resolution = (640, 480)  # Camera resolution in pixels
        self.camera_height = 10.0  # Camera height from ground in cm
        self.camera_angle = 0.0  # Camera tilt angle in radians

    def update_position(self, new_x: float, new_y: float, new_angle: float):
        """Met à jour la position après vérification des collisions"""
        if not ( self.map_model.is_collision(new_x, new_y) or self.map_model.is_out_of_bounds(new_x, new_y)):
            self.x = new_x
            self.y = new_y
            self.direction_angle =normalize_angle(new_angle)

    def set_motor_speed(self, motor: str, dps: int):
        """Définit la vitesse d'un moteur avec validation"""
        if motor in ["left", "right"]:
            self.motor_speeds[motor] = max(-1000, min(1000, dps))

    def get_state(self) -> dict:
        """Retourne un snapshot de l'état courant"""
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.direction_angle,
            'left_speed': self.motor_speeds["left"],
            'right_speed': self.motor_speeds["right"]
        }
    def update_motors(self, delta_time):
        """Met à jour les positions des moteurs avec le temps écoulé"""
        for motor in ["left", "right"]:
            self.motor_positions[motor] += self.motor_speeds[motor] * delta_time

    def get_camera_view(self):
        """Simulates what the camera sees and returns beacon detection information"""
        end_pos = self.map_model.end_position
        if end_pos is None:
            return None
            
        target_x, target_y = end_pos
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Calculate angle to beacon relative to robot's direction
        angle_to_beacon = math.atan2(dy, dx)
        relative_angle = normalize_angle(angle_to_beacon - self.direction_angle)
        
        # Check if beacon is within camera's field of view
        if abs(relative_angle) > self.camera_fov / 2:
            return None
            
        # Calculate distance to beacon
        distance = math.hypot(dx, dy)
        
        # Calculate beacon's position in camera frame (simplified)
        # This is a basic approximation - in reality, this would involve more complex camera geometry
        camera_x = (relative_angle + self.camera_fov/2) / self.camera_fov * self.camera_resolution[0]
        camera_y = self.camera_resolution[1] / 2  # Assuming beacon is at horizon level
        
        return {
            'detected': True,
            'distance': distance,
            'angle': relative_angle,
            'camera_x': camera_x,
            'camera_y': camera_y
        }