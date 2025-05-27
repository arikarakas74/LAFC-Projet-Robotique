from abc import ABC, abstractmethod
import math
import cv2
import numpy as np
from PIL import Image
import cv2
# Interface d'adaptateur abstraite
class RobotAdapter(ABC):
    @abstractmethod
    def set_motor_speed(self, motor: str, speed: float):
        pass
    
    @abstractmethod
    def get_motor_positions(self) -> dict:
        pass
    def get_robot_camera_image(self):
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
    @abstractmethod
    def get_distance(self):
        """Retourne la lecture du capteur de distance (en mm)."""
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
        port = 1 if motor == "left" else 2
        self.robot.set_motor_dps(port, speed)
    
    def get_motor_positions(self) -> dict:
        left, right = self.robot.get_motor_position()
        return {"left": left, "right": right}
    
 
    def calculer_distance_parcourue(self) -> float:
        # Récupère les positions actuelles des encodeurs (en degrés)
        new_positions = self.robot.get_motor_position()
        # Calcul des variations d'angle pour chaque roue 
        delta_left = new_positions[0] - self.last_motor_positions[0]
        delta_right = new_positions[1] - self.last_motor_positions[1]
        # Conversion des variations d'angle en distance parcourue (en mètres)
        # math.radians() convertit les degrés en radians
        left_distance = math.radians(delta_left) * self.robot.WHEEL_DIAMETER / 2.0
        right_distance = math.radians(delta_right) * self.robot.WHEEL_DIAMETER / 2.0

        # Mise à jour de la distance totale parcourue : moyenne des distances des deux roues
        print(f" Avant Distance parcourue (m) : {self.distance:.2f}")
        self.distance += (left_distance + right_distance) / 2

        # Mise à jour des positions précédentes pour la prochaine lecture
        self.last_motor_positions = new_positions

        # Affiche la distance cumulée parcourue par le robot
        print(f"Distance parcourue (m) : {self.distance:.2f}")

        # Retourne la distance cumulée parcourue par le robot
        return self.distance


    def resetDistance(self):
       print(f"Distance parcourue (m) a la fin de la phase avancer : {self.distance:.2f}")
       self.distance=0

    def decide_turn_direction(self,angle_rad,base_speed):

        speed_ratio = 0.5
        positions = self.get_motor_positions()
        self.left_initial = positions["left"]
        self.right_initial = positions["right"]

        if angle_rad > 0:  # Virage à droite
            self.fast_wheel = "MOTOR_LEFT"
            self.slow_wheel = "MOTOR_RIGHT"
        else:  # Virage à gauche
            self.fast_wheel = "MOTOR_RIGHT"
            self.slow_wheel = "MOTOR_LEFT"
        self.set_motor_speed(self.fast_wheel,base_speed)
        self.set_motor_speed(self.slow_wheel, base_speed * speed_ratio)

    def calcule_angle(self):
        positions = self.get_motor_positions()
        print("positions :" + str(positions["left"]) + str(positions["right"]))
        delta_left = positions["left"] - self.left_initial
        delta_right = positions["right"] - self.right_initial

        # On suppose que l'adaptateur fournit WHEEL_DIAMETER et WHEEL_BASE_WIDTH
        wheel_circumference = 2 * math.pi * self.robot.WHEEL_DIAMETER / 2
        angle = (delta_left - delta_right) * wheel_circumference / (360 * self.robot.WHEEL_BASE_WIDTH)

        return angle
    
    def slow_speed(self,new_slow_speed):
        self.set_motor_speed(self.slow_wheel, new_slow_speed)
    def detect_multicolor_beacon(self, img_array=None):
        """
        Détecte les balises rouge, vert, bleu, jaune dans l'image.
        Retourne un dictionnaire : {couleur: (radius, cx, cy)}
        """
        if img_array is None:
            img_array = self.img_array
        if img_array is None:
            return {}

        # Flip vertical si nécessaire
        frame = np.flipud(img_array)

        # Conversion RGB → BGR → HSV
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        # Définir les plages HSV pour chaque couleur
        color_ranges = {
            "blue":   ((100, 150, 50), (140, 255, 255)),
            "red1":   ((0, 150, 50),   (10, 255, 255)),    # bas du rouge
            "red2":   ((170, 150, 50), (180, 255, 255)),   # haut du rouge
            "green":  ((40, 100, 50),  (80, 255, 255)),
            "yellow": ((20, 100, 100), (35, 255, 255))
        }

        detected = {}

        for color in ["blue", "green", "yellow"]:
            lower, upper = color_ranges[color]
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # Nettoyage
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                (cx, cy), radius = cv2.minEnclosingCircle(c)
                if radius > 5:
                    detected[color] = (radius, int(cx), int(cy))

        # Gestion spéciale du rouge (deux plages HSV à fusionner)
        mask_red1 = cv2.inRange(hsv, np.array(color_ranges["red1"][0]), np.array(color_ranges["red1"][1]))
        mask_red2 = cv2.inRange(hsv, np.array(color_ranges["red2"][0]), np.array(color_ranges["red2"][1]))
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN,  kernel)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            (cx, cy), radius = cv2.minEnclosingCircle(c)
            if radius > 5:
                detected["red"] = (radius, int(cx), int(cy))

        return detected
    
    def get_robot_camera_image(self):
        return self.get_image()
