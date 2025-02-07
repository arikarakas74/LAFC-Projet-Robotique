import math
import tkinter as tk

class Robot:
    """Gère les mouvements du robot avec une détection avancée des collisions et des capteurs."""

    def __init__(self, start_position, map_model, radius=10):
        self.x, self.y = start_position
        self.map_model = map_model
        self.direction_angle = 0  # Orientation du robot
        self.velocity = 0
        self.acceleration = 0
        self.max_speed = 8
        self.acceleration_rate = 0.2
        self.radius = radius  # Rayon du robot pour la détection des collisions
        
        # Capteurs
        self.distance_sensor = 100  # Distance max de détection d'obstacles
        self.accelerometer = (0, 0)  # Valeur simulée (accélération en x, y)
        self.camera_view = []  # Simuler une vision par caméra

    def move_towards(self, target_position):
        """Déplace le robot vers une position cible avec vérification avancée des collisions."""
        new_x, new_y = self.calculate_new_position()
        
        if not self.is_collision(new_x, new_y):
            self.x, self.y = new_x, new_y
        
        return (self.x, self.y) == target_position

    def calculate_new_position(self):
        """Calcule la nouvelle position en fonction de la direction et de la vitesse."""
        angle_rad = math.radians(self.direction_angle)
        new_x = self.x + self.velocity * math.cos(angle_rad)
        new_y = self.y + self.velocity * math.sin(angle_rad)
        return new_x, new_y

    def is_collision(self, new_x, new_y):
        """Vérifie si le robot entre en collision avec un obstacle en considérant sa taille."""
        for obs_x, obs_y in self.map_model.obstacles:
            distance = math.sqrt((new_x - obs_x) ** 2 + (new_y - obs_y) ** 2)
            if distance < self.radius + 10:  # 10 = marge de sécurité
                return True  # Collision détectée
        return False
    
    def get_distance_to_obstacle(self):
        """Simule un capteur de distance en retournant la distance au prochain obstacle."""
        min_distance = self.distance_sensor
        for obs_x, obs_y in self.map_model.obstacles:
            distance = math.sqrt((self.x - obs_x) ** 2 + (self.y - obs_y) ** 2)
            min_distance = min(min_distance, distance)
        return min_distance

    def read_accelerometer(self):
        """Simule un accéléromètre pour suivre l'accélération du robot."""
        self.accelerometer = (self.velocity * math.cos(math.radians(self.direction_angle)), 
                              self.velocity * math.sin(math.radians(self.direction_angle)))
        return self.accelerometer
    
    def turn_left(self):
        self.direction_angle = (self.direction_angle - 10) % 360

    def turn_right(self):
        self.direction_angle = (self.direction_angle + 10) % 360

    def update_sensor_display(self, label):
        """Met à jour l'affichage des capteurs en temps réel."""
        distance = self.get_distance_to_obstacle()
        acceleration = self.read_accelerometer()
        label.config(text=f"Distance: {distance:.2f} cm | Accel: {acceleration}")
