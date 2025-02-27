# robot_controller.py
import math
from utils.geometry import normalize_angle
from model.robot import RobotModel
from model.map_model import MapModel
import keyboard

SPEED_MULTIPLIER = 8.0

class RobotController:
    WHEEL_BASE_WIDTH = 20.0  # Doit correspondre à RobotModel
    WHEEL_DIAMETER = 5.0
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    SPEED_STEP = 30.0

    def __init__(self, robot_model, map_model):
        self.robot_model = robot_model
        self.map_model = map_model
        self.drawing_square = False
        self.square_step = 0
        self.side_length = 0
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_angle = 0.0
        self._setup_key_bindings()

    def _setup_key_bindings(self):
        keyboard.add_hotkey('q', self.increase_left_speed)
        keyboard.add_hotkey('a', self.decrease_left_speed)
        keyboard.add_hotkey('e', self.increase_right_speed)
        keyboard.add_hotkey('d', self.decrease_right_speed)
        keyboard.add_hotkey('w', self.move_forward)
        keyboard.add_hotkey('s', self.move_backward)

    def draw_square(self, side_length_cm):
        """Démarre un carré avec une précision de 0.1°"""
        if not self.drawing_square:
            self.drawing_square = True
            self.square_step = 0
            self.side_length = side_length_cm
            self._start_new_side()

    def _start_new_side(self):
        """Initialise un côté avec référence de position"""
        self.start_x = self.robot_model.x
        self.start_y = self.robot_model.y
        self.start_angle = self.robot_model.direction_angle
        self.set_motor_speed("left", 250)  # Vitesse réduite pour stabilité
        self.set_motor_speed("right", 250)

    def _start_rotation(self):
        """Rotation contrôlée avec compensation inertielle"""
        self.start_angle = self.robot_model.direction_angle
        self.set_motor_speed("left", 160)   # Vitesse optimisée
        self.set_motor_speed("right", -160)

    def update_physics(self, delta_time):
        if delta_time <= 0:
            return

        # Application du multiplicateur de vitesse de façon uniforme
        effective_delta_time = delta_time * SPEED_MULTIPLIER

        # Calculs cinématiques précis
        left_speed = self.robot_model.motor_speeds["left"]
        right_speed = self.robot_model.motor_speeds["right"]

        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (left_velocity - right_velocity) / self.WHEEL_BASE_WIDTH

        # Mise à jour de la position
        if left_velocity == right_velocity:
            # Déplacement en ligne droite
            new_x = self.robot_model.x + linear_velocity * math.cos(self.robot_model.direction_angle) * effective_delta_time
            new_y = self.robot_model.y + linear_velocity * math.sin(self.robot_model.direction_angle) * effective_delta_time
            new_angle = self.robot_model.direction_angle
        else:
            # Déplacement suivant un arc de cercle (rotation)
            R = (self.WHEEL_BASE_WIDTH / 2) * (left_velocity + right_velocity) / (left_velocity - right_velocity)
            delta_theta = angular_velocity * effective_delta_time

            Cx = self.robot_model.x - R * math.sin(self.robot_model.direction_angle)
            Cy = self.robot_model.y + R * math.cos(self.robot_model.direction_angle)

            new_x = Cx + R * math.sin(self.robot_model.direction_angle + delta_theta)
            new_y = Cy - R * math.cos(self.robot_model.direction_angle + delta_theta)
            new_angle = self.robot_model.direction_angle + delta_theta

        self.robot_model.update_position(new_x, new_y, new_angle)
        self.robot_model.update_motors(delta_time)

        # Logique de contrôle du carré améliorée
        if self.drawing_square:
            if self.square_step % 2 == 0:  # Phase linéaire
                distance = math.hypot(
                    self.robot_model.x - self.start_x,
                    self.robot_model.y - self.start_y
                )
                
                # Marge de 0.5 cm + compensation dynamique
                if distance >= max(self.side_length - 0.5, self.side_length * 0.98):
                    self.stop()
                    self.square_step += 1
                    if self.square_step < 8:
                        self._start_rotation()
            else:  # Phase angulaire
                current_angle = normalize_angle(self.robot_model.direction_angle)
                target_angle = normalize_angle(self.start_angle + math.pi / 2)
                angle_error = normalize_angle(target_angle - current_angle)
                
                # Contrôle proportionnel pour précision
                if abs(angle_error) < math.radians(5):
                    self.set_motor_speed("left", 60 * (angle_error / math.radians(5)))
                    self.set_motor_speed("right", -60 * (angle_error / math.radians(5)))
                
                # Validation finale avec compensation
                if abs(angle_error) <= math.radians(0.1):
                    self.stop()
                    self.robot_model.update_position(
                        self.robot_model.x,
                        self.robot_model.y,
                        target_angle  # Forçage de l'angle exact
                    )
                    self.square_step += 1
                    if self.square_step < 8:
                        self._start_new_side()
                    else:
                        self.drawing_square = False


    # Méthodes existantes
    def set_motor_speed(self, motor, speed):
        self.robot_model.set_motor_speed(motor, speed)

    def stop(self):
        self.set_motor_speed("left", 0)
        self.set_motor_speed("right", 0)

    def increase_left_speed(self):
        new_speed = self.robot_model.motor_speeds["left"] + self.SPEED_STEP
        self.set_motor_speed("left", new_speed)

    def decrease_left_speed(self):
        new_speed = self.robot_model.motor_speeds["left"] - self.SPEED_STEP
        self.set_motor_speed("left", new_speed)

    def increase_right_speed(self):
        new_speed = self.robot_model.motor_speeds["right"] + self.SPEED_STEP
        self.set_motor_speed("right", new_speed)

    def decrease_right_speed(self):
        new_speed = self.robot_model.motor_speeds["right"] - self.SPEED_STEP
        self.set_motor_speed("right", new_speed)

    def move_forward(self):
        self.set_motor_speed("left", self.robot_model.motor_speeds["left"] + self.SPEED_STEP)
        self.set_motor_speed("right", self.robot_model.motor_speeds["right"] + self.SPEED_STEP)

    def move_backward(self):
        self.set_motor_speed("left", self.robot_model.motor_speeds["left"] - self.SPEED_STEP)
        self.set_motor_speed("right", self.robot_model.motor_speeds["right"] - self.SPEED_STEP)