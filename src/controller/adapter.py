from abc import ABC, abstractmethod

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


# Adaptateur pour le robot simulé
"""class SimulatedRobotAdapter(RobotAdapter):
    def __init__(self, robot_model):
        self.robot = robot_model
    
    def set_motor_speed(self, motor: str, speed: float):
        self.robot.set_motor_speed(motor, speed)
    
    def get_motor_positions(self) -> dict:
        return self.robot.motor_positions
    
    def update_motors(self, delta_time: float):
        self.robot.update_motors(delta_time)
    
    def get_distance(self) -> float:
        return 0.0  # À implémenter selon le modèle
    
    @property
    def x(self) -> float:
        return self.robot.x
    
    @property
    def y(self) -> float:
        return self.robot.y
    
    @property
    def direction_angle(self) -> float:
        return self.robot.direction_angle
"""
# Adaptateur pour le robot réel
class RealRobotAdapter(RobotAdapter):
    def __init__(self, real_robot):
        self.robot = real_robot
        self._motor_positions = {"left": 0, "right": 0}
    
    def set_motor_speed(self, motor: str, speed: float):
        port = self.robot.MOTOR_LEFT if motor == "left" else self.robot.MOTOR_RIGHT
        self.robot.set_motor_dps(port, int(speed))
    
    def get_motor_positions(self) -> dict:
        left, right = self.robot.get_motor_position()
        return {"left": left, "right": right}
    
    def update_motors(self, delta_time: float):
        pass  # Le robot réel gère cela automatiquement
    
    def get_distance(self) -> float:
        return self.robot.get_distance() / 10.0  # Conversion mm -> cm
    
