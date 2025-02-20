import math
from utils.geometry import normalize_angle
from model.robot import RobotModel  # Modèle robot
from model.map_model import MapModel      # Modèle carte
import keyboard


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
        if delta_time <= 0:
            return

        l_speed = self.robot_model.motor_speeds["left"]
        r_speed = self.robot_model.motor_speeds["right"]
        
        # Calcul des vitesses linéaires (cm/s)
        l_velocity = (l_speed / 360) * (2 * math.pi * self.robot_model.WHEEL_RADIUS)
        r_velocity = (r_speed / 360) * (2 * math.pi * self.robot_model.WHEEL_RADIUS)
        
        linear = (l_velocity + r_velocity) / 2
        angular = (r_velocity - l_velocity) / self.robot_model.WHEEL_BASE_WIDTH

        new_x = self.robot_model.x + linear * math.cos(self.robot_model.direction_angle) * delta_time
        new_y = self.robot_model.y + linear * math.sin(self.robot_model.direction_angle) * delta_time
        new_angle = normalize_angle(self.robot_model.direction_angle + angular * delta_time)

        self.robot_model.update_position(new_x, new_y, new_angle)

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