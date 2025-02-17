from model.robot import Robot
from view.robot_view import RobotView
from view.control_panel import ControlPanel
from model.map_model import MapModel
from model.clock import Clock
import math
import threading
from utils.geometry import normalize_angle

SPEED_STEP = 30  # Incrément/décrément de vitesse

class RobotController:
    WHEEL_BASE_WIDTH = 20.0  # Distance entre les roues (cm)
    WHEEL_DIAMETER = 5.0     # Diamètre des roues (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    
    MOTOR_LEFT = "left"
    MOTOR_RIGHT = "right"

    def __init__(self, robot: Robot, robot_view: RobotView, control_panel: ControlPanel, window, map_model: MapModel):
        self.robot = robot
        self.robot_view = robot_view
        self.control_panel = control_panel
        self.window = window
        self.map_model = map_model
        self.running = True
        
        # Configuration de l'horloge temps-réel
        self.clock = Clock()
        self.clock.add_subscriber(self.update_simulation)
        self.clock_thread = threading.Thread(target=self.clock.start)
        self.clock_thread.daemon = True
        self.last_printed_position = (self.robot.x, self.robot.y)
        self.clock_thread.start()
        
        # Événements robot
        self.robot.add_event_listener(self.handle_robot_event)

    def handle_robot_event(self, event_type, **kwargs):
        """Gère les événements du robot"""
        if event_type == "update_view":
            self.robot_view.draw(
                kwargs["x"], 
                kwargs["y"], 
                kwargs["direction_angle"]
            )
        elif event_type == "update_speed_label":
            self.control_panel.update_speed_label(
                kwargs.get("left_speed", 0),
                kwargs.get("right_speed", 0),
                kwargs.get("direction_angle", 0)
            )

    def update_simulation(self, delta_time):
        """Met à jour la simulation avec le temps écoulé"""
        if delta_time <= 0:
            return

        # Récupération des vitesses
        left_speed = self.robot.motor_speeds.get(self.MOTOR_LEFT, 0)
        right_speed = self.robot.motor_speeds.get(self.MOTOR_RIGHT, 0)
        
        # Calcul des vitesses linéaire/angulaire
        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        
        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (right_velocity - left_velocity) / self.WHEEL_BASE_WIDTH

        if left_velocity == right_velocity:
            linear_velocity = (left_velocity + right_velocity) / 2
            new_x = self.robot.x + linear_velocity * math.cos(self.robot.direction_angle) * delta_time
            new_y = self.robot.y + linear_velocity * math.sin(self.robot.direction_angle) * delta_time
            new_angle = self.robot.direction_angle
        else:
            R = (self.WHEEL_BASE_WIDTH / 2) * (left_velocity + right_velocity) / (right_velocity - left_velocity)
            angular_velocity = (left_velocity - right_velocity) / self.WHEEL_BASE_WIDTH
            delta_theta = angular_velocity * delta_time
            
            Cx = self.robot.x - R * math.sin(self.robot.direction_angle)
            Cy = self.robot.y + R * math.cos(self.robot.direction_angle)

            new_x = Cx + R * math.sin(self.robot.direction_angle + delta_theta)
            new_y = Cy - R * math.cos(self.robot.direction_angle + delta_theta)
            new_angle = self.robot.direction_angle + delta_theta

        # Vérification des collisions
        if not (self.map_model.is_collision(new_x, new_y) or self.map_model.is_out_of_bounds(new_x, new_y)):
            self.robot.x = new_x
            self.robot.y = new_y
            self.robot.direction_angle = normalize_angle(new_angle)

            # contrôle à distance basé sur le nouvel emplacement
            last_x, last_y = self.last_printed_position
            distance_moved = math.sqrt((self.robot.x - last_x)**2 + (self.robot.y - last_y)**2)

            if distance_moved >= 0.1:
                print(f"Robot Position: x={self.robot.x:.2f}, y={self.robot.y:.2f}, angle={math.degrees(self.robot.direction_angle):.2f}°")
                self.last_printed_position = (self.robot.x, self.robot.y)
        
        # Mise à jour des encodeurs
        self.robot.update_motors(delta_time)

        # Synchronisation avec l'interface
        self.window.after(0, self._sync_view)

    def _sync_view(self):
        """Synchronise la vue avec le thread principal"""
        self.robot.trigger_event("update_view", 
                               x=self.robot.x,
                               y=self.robot.y,
                               direction_angle=self.robot.direction_angle)
        
        self.control_panel.update_speed_label(
            self.robot.motor_speeds.get(self.MOTOR_LEFT, 0),
            self.robot.motor_speeds.get(self.MOTOR_RIGHT, 0),
            math.degrees(self.robot.direction_angle)
        )

    # Commandes de contrôle
    def increase_left_speed(self):
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 
                               self.robot.motor_speeds[self.robot.MOTOR_LEFT] + SPEED_STEP)

    def decrease_left_speed(self):
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 
                               self.robot.motor_speeds[self.robot.MOTOR_LEFT] - SPEED_STEP)

    def increase_right_speed(self):
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 
                               self.robot.motor_speeds[self.robot.MOTOR_RIGHT] + SPEED_STEP)

    def decrease_right_speed(self):
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 
                               self.robot.motor_speeds[self.robot.MOTOR_RIGHT] - SPEED_STEP)

    def stop_rotation(self):
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 0)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 0)

    def cleanup(self):
        """Nettoyage des ressources"""
        self.clock.stop()
        self.clock_thread.join()
