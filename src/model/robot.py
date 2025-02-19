import math
from model.map_model import MapModel
import time

class Robot:
    WHEEL_BASE_WIDTH = 10.0  # Distance entre les roues (cm)
    WHEEL_DIAMETER = 5.0     # Diamètre des roues (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    
    MOTOR_LEFT = "left"
    MOTOR_RIGHT = "right"
    
    def __init__(self, map_model: MapModel):
        self.map_model = map_model
        self.x, self.y = map_model.start_position  # Position stockée dans le modèle
        self.direction_angle = 0.0
        self.motor_speeds = {self.MOTOR_LEFT: 0, self.MOTOR_RIGHT: 0}
        self.motor_positions = {self.MOTOR_LEFT: 0, self.MOTOR_RIGHT: 0}
        self.event_listeners = []
        self.moving = False
    
    def update_position(self, new_x, new_y, new_angle):
        """Met à jour la position du robot"""
        print(f"Before update: x={self.x}, y={self.y}, angle={self.direction_angle}")

        self.x = new_x
        self.y = new_y
        self.direction_angle = new_angle

        print(f"After update: x={self.x}, y={self.y}, angle={self.direction_angle}")

    def add_event_listener(self, listener):
        """Ajoute un écouteur d'événements"""
        self.event_listeners.append(listener)
    
    def trigger_event(self, event_type, **kwargs):
        """Déclenche un événement"""
        valid_events = {"update_view", "update_speed_label"}
        if event_type not in valid_events:
            raise ValueError(f"Événement invalide: {event_type}")
        for listener in self.event_listeners:
            listener(event_type, **kwargs)

    def set_motor_dps(self, port, dps):
        """Définit la vitesse des moteurs"""
        if port in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            self.motor_speeds[port] = dps

        # Gestion de l'état de mouvement
        if self.motor_speeds[self.MOTOR_LEFT] == 0 and self.motor_speeds[self.MOTOR_RIGHT] == 0:
            self.moving = False
        else:
            self.moving = True
            
        self.trigger_event("update_speed_label", 
        left_speed=self.motor_speeds[self.MOTOR_LEFT],
        right_speed=self.motor_speeds[self.MOTOR_RIGHT],
        direction_angle=0)

    def update_motors(self, delta_time):
        """Met à jour les positions des moteurs avec le temps écoulé"""
        for motor in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            self.motor_positions[motor] += self.motor_speeds[motor] * delta_time
            self.motor_positions[motor] %= 360  # Normalisation à 
    
    def move_motors(self, delta_time):
        left_speed = self.motor_speeds[self.MOTOR_LEFT]
        right_speed = self.motor_speeds[self.MOTOR_RIGHT]

        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

        v = (left_velocity + right_velocity) / 2
        omega = (right_velocity - left_velocity) / self.WHEEL_BASE_WIDTH

        new_x = self.x + v * math.cos(self.direction_angle) * delta_time
        new_y = self.y + v * math.sin(self.direction_angle) * delta_time
        new_angle = self.direction_angle + omega * delta_time

        self.update_position(new_x, new_y, new_angle)


    def stop_simulation(self):
        """Arrête la simulation"""
        self.moving = False


    def start_movement(self):
        """Démarre le mouvement du robot"""
        if not self.moving:
            self.moving = True

    # Méthodes utilitaires
    def get_motor_speed(self):
        return (self.motor_speeds[self.MOTOR_LEFT], 
                self.motor_speeds[self.MOTOR_RIGHT])
    
    def offset_motor_encoder(self, port, offset):
        """Réinitialise l'encodeur du moteur"""
        if port in [self.MOTOR_LEFT, self.MOTOR_RIGHT]:
            self.motor_positions[port] -= offset
    
    def get_position(self):
        return self.x, self.y ,self.direction_angle
    
    def draw_square(self):
        """Fait avancer le robot en dessinant un carré"""
        print("Démarrage du dessin du carré...")  

        for x in range(4):
            start_left_pos = self.motor_positions[self.MOTOR_LEFT]
            start_right_pos = self.motor_positions[self.MOTOR_RIGHT]

            self.set_motor_dps(self.MOTOR_LEFT, 60)
            self.set_motor_dps(self.MOTOR_RIGHT, 60)  

            while abs(self.motor_positions[self.MOTOR_LEFT] - start_left_pos) < 300:
                time.sleep(0.05)

            self.offset_motor_encoder(self.MOTOR_LEFT, self.motor_positions[self.MOTOR_LEFT])
            self.offset_motor_encoder(self.MOTOR_RIGHT, self.motor_positions[self.MOTOR_RIGHT])

            self.set_motor_dps(self.MOTOR_LEFT, 0)
            self.set_motor_dps(self.MOTOR_RIGHT, 0)

            time.sleep(0.2)

            start_left_pos = self.motor_positions[self.MOTOR_LEFT]
            start_right_pos = self.motor_positions[self.MOTOR_RIGHT]

            self.set_motor_dps(self.MOTOR_LEFT, 30)
            self.set_motor_dps(self.MOTOR_RIGHT, -30)
            

            while abs(self.motor_positions[self.MOTOR_LEFT] - start_left_pos) <= 90:
                time.sleep(0.05)

            self.offset_motor_encoder(self.MOTOR_LEFT, self.motor_positions[self.MOTOR_LEFT])
            self.offset_motor_encoder(self.MOTOR_RIGHT, self.motor_positions[self.MOTOR_RIGHT])

            self.set_motor_dps(self.MOTOR_LEFT, 0)
            self.set_motor_dps(self.MOTOR_RIGHT, 0)

            time.sleep(0.2)
            
        print("Carré complété !")

    @staticmethod
    def normalize_angle(angle):
        """Normalise l'angle entre -π et π"""
        return angle % (2 * math.pi)
