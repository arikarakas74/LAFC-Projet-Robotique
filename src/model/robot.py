import math
import cv2
import numpy as np
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
        self.camera_resolution = (640, 480)  # Camera resolution in pixels
        self.camera_height = 10.0  # Camera height from ground in cm
        self.camera_angle = 0.0  # Camera tilt angle in radians
        self.camera_focal_length = 500  # Focal length in pixels
        self.beacon_color = (0, 0, 255)  # Red color for beacon in BGR format
        self.beacon_size = 20  # Size of beacon in pixels

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
        """Simulates camera view and processes image to detect beacon"""
        # Create a blank image
        image = np.zeros((self.camera_resolution[1], self.camera_resolution[0], 3), dtype=np.uint8)
        
        # Get beacon position
        end_pos = self.map_model.end_position
        if end_pos is None:
            return None
            
        target_x, target_y = end_pos
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Calculate distance and angle to beacon
        distance = math.hypot(dx, dy)
        angle_to_beacon = math.atan2(dy, dx)
        relative_angle = normalize_angle(angle_to_beacon - self.direction_angle)
        
        # Simple projection to camera frame
        # Map the relative angle to camera coordinates
        # -π/2 to π/2 maps to 0 to camera width
        camera_x = int((relative_angle + math.pi/2) / math.pi * self.camera_resolution[0])
        camera_y = self.camera_resolution[1] // 2  # Place beacon at middle height
        
        # Check if beacon is within image bounds
        if (0 <= camera_x < self.camera_resolution[0] and 
            0 <= camera_y < self.camera_resolution[1]):
            # Draw beacon in image
            cv2.circle(image, (camera_x, camera_y), self.beacon_size, self.beacon_color, -1)
            
            # Process image to detect beacon
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color range for red beacon
            lower_red = np.array([0, 100, 100])
            upper_red = np.array([10, 255, 255])
            
            # Create mask for red color
            mask = cv2.inRange(hsv, lower_red, upper_red)
            
            # Find contours of red objects
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get the largest contour (should be our beacon)
                largest_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest_contour)
                
                if M["m00"] != 0:
                    # Calculate center of the beacon
                    cx = int(M["m10"] / M["m00"])
                    
                    # Calculate relative angle from center of image
                    # Map camera x coordinate back to angle
                    relative_angle = (cx / self.camera_resolution[0] * math.pi) - math.pi/2
                    
                    return {
                        'detected': True,
                        'distance': distance,
                        'angle': relative_angle,
                        'camera_x': cx,
                        'camera_y': camera_y
                    }
        
        return None