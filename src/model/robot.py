import math
from src.model.map_model import MapModel
from src.utils.geometry import normalize_angle
from src.controller.adapter import RobotAdapter

class RobotModel(RobotAdapter):
    WHEEL_BASE_WIDTH = 20.0  # cm
    WHEEL_DIAMETER = 5.0     # cm
    WHEEL_RADIUS = WHEEL_DIAMETER / 2

    def __init__(self, map_model: MapModel):
        print("init robot")
        self.map_model = map_model
        self.x, self.y = map_model.start_position 
        self.direction_angle = 0.0
        self.motor_speeds = {"left": 0, "right": 0}
        self.motor_positions = {"left": 0, "right": 0}
        self.last_motor_positions = self.motor_positions.copy()
        self.distance=0
        self.fast_wheel = None
        self.slow_wheel=None

    def update_position(self, new_x: float, new_y: float, new_angle: float):
        """Met à jour la position après vérification des collisions"""
        if not ( self.map_model.is_collision(new_x, new_y) or self.map_model.is_out_of_bounds(new_x, new_y)):
            self.x = new_x
            self.y = new_y
            self.direction_angle =normalize_angle(new_angle)

    def set_motor_speed(self, motor: str, dps: int):
        """Définit la vitesse d'un moteur avec validation"""
        if motor in ["left", "right"]:
            self.motor_speeds[motor] = dps

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


    
    def get_motor_positions(self) -> dict:
        return self.motor_positions
    

    
    def get_distance(self) -> float:
        return 0.0  # À implémenter selon le modèle
    


    def calculer_distance_parcourue(self) -> float:

        old_positions = self.last_motor_positions
        new_positions = self.motor_positions
        delta_left = new_positions["left"] - old_positions["left"]
        delta_right = new_positions["right"] - old_positions["right"]

        left_distance = math.radians(delta_left) * self.WHEEL_RADIUS
        right_distance = math.radians(delta_right) * self.WHEEL_RADIUS

        # Mettre à jour les anciennes positions avec les nouvelles
        self.last_motor_positions = new_positions.copy()
        self.distance+=(left_distance + right_distance) / 2 
        # Retourne la distance moyenne parcourue
        return self.distance
    
    def resetDistance(self):
        self.distance=0
    def decide_turn_direction(self, angle_rad: float, base_speed: float):
        """Sets motor speeds for an in-place rotation."""
        self.last_motor_positions = self.get_motor_positions() # Store initial pos for angle calc
        
        # For in-place turn, speeds are equal and opposite
        turn_speed = base_speed # Use base_speed as the magnitude

        if angle_rad < 0: # Turn Left (CCW)
             # Left wheel backward, Right wheel forward
             self.set_motor_speed('left', -turn_speed)
             self.set_motor_speed('right', turn_speed)
             # Keep track for slow_speed (though it might become redundant)
             self.fast_wheel = 'right' 
             self.slow_wheel = 'left'
        elif angle_rad > 0: # Turn Right (CW)
             # Left wheel forward, Right wheel backward
             self.set_motor_speed('left', turn_speed)
             self.set_motor_speed('right', -turn_speed)
             # Keep track for slow_speed
             self.fast_wheel = 'left'
             self.slow_wheel = 'right'
        else: # angle_rad is 0
             # Don't turn, set speeds to 0? Or handle in Tourner strategy?
             # Let's set to 0 for safety, Tourner should handle 0 angle better now.
             self.set_motor_speed('left', 0)
             self.set_motor_speed('right', 0)
             self.fast_wheel = None
             self.slow_wheel = None
        
        # print(f"Set turn speeds: L={self.motor_speeds['left']}, R={self.motor_speeds['right']}")

    def calcule_angle(self) -> float:
        """Calculates the angle turned (in radians) based on wheel encoder differences."""
        positions = self.get_motor_positions()
        # Calculate change since the turn started (using last_motor_positions set by decide_turn_direction)
        delta_left_deg = positions["left"] - self.last_motor_positions["left"]
        delta_right_deg = positions["right"] - self.last_motor_positions["right"]

        # Convert degrees of wheel rotation to radians
        delta_left_rad = math.radians(delta_left_deg)
        delta_right_rad = math.radians(delta_right_deg)

        # Calculate arc length traveled by each wheel
        arc_left = delta_left_rad * self.WHEEL_RADIUS
        arc_right = delta_right_rad * self.WHEEL_RADIUS

        # Calculate the change in robot orientation angle (radians)
        # Positive angle corresponds to clockwise rotation (right wheel forward, left backward)
        angle_rad = (arc_right - arc_left) / self.WHEEL_BASE_WIDTH
        
        return angle_rad
    
    def slow_speed(self,new_slow_speed):
        self.set_motor_speed(self.slow_wheel, new_slow_speed)

    
