from model.robot import Robot
from view.robot_view import RobotView
from view.control_panel import ControlPanel
from model.map_model import MapModel
SPEED_STEP = 30  # How much speed to add/remove per key press
import math
import threading
from utils.geometry import normalize_angle
# En haut du fichier
from model.clock import Clock  # Nouvelle classe d'horloge

class RobotController:
    WHEEL_BASE_WIDTH = 10.0  # cm (Distance between the wheels)
    WHEEL_DIAMETER = 5.0  # cm (Wheel diameter)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2  # cm (Wheel radius)
    
    MOTOR_LEFT = "left"
    MOTOR_RIGHT = "right"
    TICK_DURATION = 0.05  # 50 ms tick duration (matching simulation tick)
    def __init__(self, robot: Robot, robot_view: RobotView, control_panel: ControlPanel, window,map_model: MapModel):
        """Initializes the RobotController with references to the robot, its view, the control panel, and the window."""
        self.robot = robot
        self.robot_view = robot_view
        self.control_panel = control_panel
        self.window = window  # Store the window object
        self.running = True
        self.robot.add_event_listener(self.handle_robot_event)
        self.map_model=map_model
        self.clock = Clock(self.TICK_DURATION)  # Initialiser l'horloge
        self.clock.add_subscriber(self.update_simulation)  # Abonner la méthode
        self.clock.start()
    def schedule_update(self):
        """Planifie les mises à jour via l'horloge de Tkinter"""
        self.update_simulation()
        self.window.after(int(self.TICK_DURATION * 1000), self.schedule_update)       

    def handle_robot_event(self, event_type, **kwargs):
        """Handles events from the robot."""
        if event_type == "update_view":
            # Utiliser les valeurs de RobotView
            self.robot_view.draw(kwargs["x"], kwargs["y"], kwargs["direction_angle"])
            # Utiliser les valeurs de RobotView
            self.robot_view.draw(kwargs["x"], kwargs["y"], kwargs["direction_angle"])
        if event_type == "update_view":
            self.robot_view.draw(kwargs["x"], kwargs["y"], kwargs["direction_angle"])
        elif event_type == "update_speed_label":
            left_speed = kwargs.get("left_speed", 0)
            right_speed = kwargs.get("right_speed", 0)
            direction_angle = kwargs.get("direction_angle", 0)
            self.control_panel.update_speed_label(left_speed, right_speed, direction_angle)
        elif event_type == "after":
            callback = kwargs.get("callback")
            if callable(callback):
                return self.window.after(kwargs["delay"], callback, kwargs.get("obstacles", []), kwargs.get("goal_position", None))



    def update_simulation(self):
        """Appelée automatiquement à chaque tick d'horloge"""
        # Récupérer les vitesses actuelles
        left_speed = self.robot.motor_speeds.get(self.MOTOR_LEFT, 0)
        right_speed = self.robot.motor_speeds.get(self.MOTOR_RIGHT, 0)

        if left_speed == 0 and right_speed == 0:
            return

        # 1. Mettre à jour les encodeurs
        self.robot.update_motors(self.TICK_DURATION)

        # 2. Calculer la cinématique
        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (right_velocity - left_velocity) / self.WHEEL_BASE_WIDTH

        # 3. Calculer la nouvelle position
        new_x = self.robot_view.x
        new_y = self.robot_view.y
        
        # Cas spécial : rotation sur place
        if left_speed == -right_speed and left_speed != 0:
            self.robot_view.direction_angle += angular_velocity * self.TICK_DURATION
            linear_velocity = 0

        # Cas spécial : pivotement sur une roue
        elif left_speed == 0 or right_speed == 0:
            pivot_radius = self.WHEEL_BASE_WIDTH / 2
            angular_velocity = (right_velocity if left_speed == 0 else -left_velocity) / pivot_radius
            self.robot_view.direction_angle += angular_velocity * self.TICK_DURATION
            linear_velocity = 0

        # Mouvement linéaire normal
        else:
            new_x = self.robot_view.x + linear_velocity * math.cos(self.robot_view.direction_angle) * self.TICK_DURATION
            new_y = self.robot_view.y + linear_velocity * math.sin(self.robot_view.direction_angle) * self.TICK_DURATION

        # 4. Vérifier les collisions et les limites
        if not (self.map_model.is_collision(new_x, new_y) or self.map_model.is_out_of_bounds(new_x, new_y)):
            self.robot_view.x = new_x
            self.robot_view.y = new_y
            self.robot_view.direction_angle += angular_velocity * self.TICK_DURATION

        # 5. Normaliser l'angle
        self.robot_view.direction_angle = normalize_angle(self.robot_view.direction_angle)

        # 6. Synchroniser la vue
        self.window.after(0, self._sync_view)

    def _sync_view(self):
        """Met à jour l'interface depuis le thread principal"""
        # Mettre à jour la position du robot
        self.robot.trigger_event("update_view", 
                                x=self.robot_view.x,
                                y=self.robot_view.y,
                                direction_angle=self.robot_view.direction_angle)
        
        # Mettre à jour les labels de vitesse
        left_speed = self.robot.motor_speeds.get(self.MOTOR_LEFT, 0)
        right_speed = self.robot.motor_speeds.get(self.MOTOR_RIGHT, 0)
        self.control_panel.update_speed_label(left_speed, right_speed, math.degrees(self.robot_view.direction_angle))


    def increase_left_speed(self):
        """Reduce the left wheel speed (turn right)"""
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] + SPEED_STEP)  

    def decrease_left_speed(self):
        """Increase the left wheel speed (turn left)"""

        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, self.robot.motor_speeds[self.robot.MOTOR_RIGHT] - SPEED_STEP) 

    def increase_right_speed(self):
        """Reduce the right wheel speed (turn left)"""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] + SPEED_STEP)  
    def decrease_right_speed(self):
        """Increase the right wheel speed (turn right)"""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, self.robot.motor_speeds[self.robot.MOTOR_LEFT] - SPEED_STEP)  
    
    def stop_rotation(self):
        """Release the rotation key to immediately stop rotating, but the simulation continues running."""
        self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 0)
        self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 0)

