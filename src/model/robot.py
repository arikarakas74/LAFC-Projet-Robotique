import math
from model.map_model import MapModel

class Robot:
    WHEEL_BASE_WIDTH = 10.0  # Distance entre les roues (cm)
    WHEEL_DIAMETER = 5.0     # Diamètre des roues (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    
    MOTOR_LEFT = "left"
    MOTOR_RIGHT = "right"
    
    def __init__(self, map_model: MapModel):
        self.map_model = map_model
        self.motor_speeds = {self.MOTOR_LEFT: 0, self.MOTOR_RIGHT: 0}
        self.motor_positions = {self.MOTOR_LEFT: 0, self.MOTOR_RIGHT: 0}
        self.event_listeners = []
        self.moving = False

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
            self.motor_positions[motor] %= 360  # Normalisation à 360°

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
    
    @staticmethod
    def normalize_angle(angle):
        """Normalise l'angle entre -π et π"""
        return angle % (2 * math.pi)