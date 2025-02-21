import math
from utils.geometry import normalize_angle
from model.robot import RobotModel  # Modèle robot
from model.map_model import MapModel      # Modèle carte
import keyboard

SPEED_MULTIPLIER = 8.0
class RobotController:
    WHEEL_BASE_WIDTH = 10.0  # cm
    WHEEL_DIAMETER = 5.0     # cm
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    SPEED_STEP = 30.0

    def __init__(self, robot_model, map_model):
        self.robot_model = robot_model
        self.map_model = map_model
        self._setup_key_bindings()

    def _setup_key_bindings(self):
        """Lie les touches aux actions."""
        keyboard.add_hotkey('q', self.increase_left_speed)
        keyboard.add_hotkey('a', self.increase_left_speed)
        keyboard.add_hotkey('e', self.increase_right_speed)
        keyboard.add_hotkey('d', self.decrease_right_speed)
        keyboard.add_hotkey('w', self.move_forward)
        keyboard.add_hotkey('s', self.move_backward)

    def update_physics(self, delta_time):

        """Met à jour la simulation avec le temps écoulé"""
        if delta_time <= 0:
            return

        # Récupération des vitesses
        left_speed = self.robot_model.motor_speeds["left"]
        right_speed = self.robot_model.motor_speeds["right"]
        
        # Calcul des vitesses linéaire/angulaire
        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        
        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (left_velocity - right_velocity) / self.WHEEL_BASE_WIDTH

        if left_velocity == right_velocity:
            new_x = self.robot_model.x + SPEED_MULTIPLIER * linear_velocity * math.cos(self.robot_model.direction_angle) * delta_time
            new_y = self.robot_model.y + SPEED_MULTIPLIER * linear_velocity * math.sin(self.robot_model.direction_angle) * delta_time
            new_angle = self.robot_model.direction_angle
        else:
            R = (self.WHEEL_BASE_WIDTH / 2) * (left_velocity + right_velocity) / (left_velocity - right_velocity)
            delta_theta = angular_velocity * delta_time * SPEED_MULTIPLIER/2
            
            Cx = self.robot_model.x - R * math.sin(self.robot_model.direction_angle)
            Cy = self.robot_model.y + R * math.cos(self.robot_model.direction_angle)

            new_x = Cx + R * math.sin(self.robot_model.direction_angle + delta_theta)
            new_y = Cy - R * math.cos(self.robot_model.direction_angle + delta_theta)
            new_angle = self.robot_model.direction_angle + delta_theta

            # contrôle à distance basé sur le nouvel emplacement

        self.robot_model.update_position(new_x, new_y, new_angle)
        # Mise à jour des encodeurs
        self.robot_model.update_motors(delta_time)

        # Synchronisation avec l'interfac


        

    

    def set_motor_speed(self, motor, speed):
        self.robot_model.set_motor_speed(motor, speed)

    def stop(self):
        self.set_motor_speed("left", 0)
        self.set_motor_speed("right", 0)

    # Commandes de contrôle
    def increase_left_speed(self):
        self.robot_model.set_motor_speed("left", self.robot_model.motor_speeds["left"] + self.SPEED_STEP)

    def decrease_left_speed(self):
        self.robot_model.set_motor_speed("left", self.robot_model.motor_speeds["left"] - self.SPEED_STEP)

    def increase_right_speed(self):
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] + self.SPEED_STEP)

    def decrease_right_speed(self):
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] - self.SPEED_STEP)

    def move_forward(self):
        """Increase both motor speeds to move forward."""
        print("Moving forward") 
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] + self.SPEED_STEP)
        self.robot_model.set_motor_speed("left",self.robot_model.motor_speeds["left"] + self.SPEED_STEP)

    def move_backward(self):
        """Decrease both motor speeds to move backward."""
        print("Moving backward")
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] - self.SPEED_STEP)
        self.robot_model.set_motor_speed("left",self.robot_model.motor_speeds["left"] - self.SPEED_STEP)

    def stop_rotation(self):
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 0)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 0)

    def cleanup(self):
        """Nettoyage des ressources"""
        self.clock.stop()
        self.clock_thread.join()