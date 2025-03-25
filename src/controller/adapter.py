from abc import ABC, abstractmethod
import math
# Interface d'adaptateur abstraite
class RobotAdapter(ABC):
    @abstractmethod
    def set_motor_speed(self, motor: str, speed: float):
        pass
    
    @abstractmethod
    def get_motor_positions(self) -> dict:
        pass
    
    @abstractmethod
    def update_motors(self, delta_time: float):
        pass
    
    @abstractmethod
    def calculer_distance_parcourue(self):
        pass
    @abstractmethod
    def resetDistance(self):
        pass
    @abstractmethod
    def decide_turn_direction(self, adapter):
        pass
    @abstractmethod
    def calcule_angle(self):
        pass

# Adaptateur pour le robot réel
class RealRobotAdapter(RobotAdapter):
    def __init__(self, real_robot):
        self.robot = real_robot
        self.motor_positions = {"left": 0, "right": 0}
        self.last_motor_positions = self.robot.get_motor_position()
        self.fast_wheel=None
        self.slow_wheel=None
        self.distance=0
    
    def set_motor_speed(self, motor: str, speed: float):
        port = self.robot.MOTOR_LEFT if motor == "left" else self.robot.MOTOR_RIGHT
        self.robot.set_motor_dps(port, int(speed))
    
    def get_motor_positions(self) -> dict:
        left, right = self.robot.get_motor_position()
        return {"left": left, "right": right}
    
    def update_motors(self, delta_time: float):
        pass  # Le robot réel gère cela automatiquement
    

    def calculer_distance_parcourue(self) -> float:
        # Récupère les positions actuelles des encodeurs (en degrés)
        # Ici, on suppose que get_motor_position() renvoie un tuple (position_gauche, position_droite)
        new_positions = self.robot.get_motor_position()  

        # Calcul des variations d'angle pour chaque roue
        delta_left = new_positions[0] - self.last_motor_positions[0]
        delta_right = new_positions[1] - self.last_motor_positions[1]

        # Conversion des variations d'angle en distance parcourue (en mètres)
        # math.radians() convertit les degrés en radians
        left_distance = math.radians(delta_left) * self.robot.WHEEL_RADIUS
        right_distance = math.radians(delta_right) * self.robot.WHEEL_RADIUS

        # Mise à jour de la distance totale parcourue : moyenne des distances des deux roues
        self.distance += (left_distance + right_distance) / 2

        # Mise à jour des positions précédentes pour la prochaine lecture
        self.last_motor_positions = new_positions

        # Retourne la distance cumulée parcourue par le robot
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
        self.robot.set_motor_dps(self.fast_wheel,base_speed)
        self.robot.set_motor_dps(self.slow_wheel, base_speed * speed_ratio)

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
    
