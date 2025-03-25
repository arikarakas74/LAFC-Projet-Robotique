import math
from model.map_model import MapModel
from utils.geometry import normalize_angle
from controller.adapter import RobotAdapter

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

    def decide_turn_direction(self,angle_rad,base_speed):

        speed_ratio = 0.5
        positions = self.get_motor_positions()
        self.left_initial = positions["left"]
        self.right_initial = positions["right"]

        if angle_rad > 0:  # Virage à droite
            self.fast_wheel = "left"
            self.slow_wheel = "right"
        else:  # Virage à gauche
            self.fast_wheel = "right"
            self.slow_wheel = "left"
        self.set_motor_speed(self.fast_wheel,base_speed)
        self.set_motor_speed(self.slow_wheel, base_speed * speed_ratio)

    def calcule_angle(self):
        positions = self.get_motor_positions()
        delta_left = positions["left"] - self.left_initial
        delta_right = positions["right"] - self.right_initial

        # On suppose que l'adaptateur fournit WHEEL_DIAMETER et WHEEL_BASE_WIDTH
        wheel_circumference = 2 * math.pi * self.WHEEL_DIAMETER / 2
        angle = (delta_left - delta_right) * wheel_circumference / (360 * self.WHEEL_BASE_WIDTH)
        return angle
    
    def slow_speed(self,new_slow_speed):
        self.set_motor_speed(self.slow_wheel, new_slow_speed)

