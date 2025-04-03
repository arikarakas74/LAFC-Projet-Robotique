import time
import math
import threading
from collections import deque
import numpy as np

class MockRobot2IN013:
    """
    Mock-up du robot réel Robot2IN013.
    Toutes les actions sont simulées par des affichages (print).
    """
    
    WHEEL_BASE_WIDTH         = 117   # en mm
    WHEEL_DIAMETER           = 66.5  # en mm
    WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * math.pi  # en mm
    WHEEL_CIRCUMFERENCE      = WHEEL_DIAMETER * math.pi      # en mm
   
    def __init__(self, nb_img=10, fps=25, resolution=(640,480), servoPort="SERVO1", motionPort="AD1"):
        print("MockRobot2IN013: Initialisation du robot simulé.")
        self.nb_img = nb_img
        self.fps = fps
        self.resolution = resolution
        self._img_queue = deque(maxlen=nb_img)
        # Simulation des positions et vitesses des moteurs
        self.motor_positions = {"MOTOR_LEFT": 0.0, "MOTOR_RIGHT": 0.0}
        self.motor_speeds = {"MOTOR_LEFT": 0.0, "MOTOR_RIGHT": 0.0}
        self._recording = False
        self._thread = None
        self.fps_camera = fps
        # Démarrage de l'enregistrement simulé des images
        self.start_recording()

    def stop(self):
        """Arrête le robot (simulation)."""
        print("MockRobot2IN013: Arrêt du robot.")
        self.set_motor_dps("left", 0)
        self.set_motor_dps("right", 0)
        print("MockRobot2IN013: LED éteintes (simulé).")

    def get_image(self):
        """Retourne la dernière image simulée."""
        if self._img_queue:
            print("MockRobot2IN013: Retour de la dernière image simulée.")
            return self._img_queue[-1][0]
        else:
            print("MockRobot2IN013: Aucune image disponible.")
            return None

    def get_images(self):
        """Retourne la liste des images simulées."""
        print("MockRobot2IN013: Retour de toutes les images simulées.")
        return list(self._img_queue)

    def set_motor_dps(self, port, dps):
        """
        Définit la vitesse d'un moteur en degrés par seconde.
        :param port: 'left' ou 'right'
        :param dps: vitesse en dps
        """
       
        self.motor_speeds[port] = dps
        print(f"[Mock] Vitesse du moteur '{port}' réglée à {dps} dps")
 


    def update_encoders(self, delta_time):
        """
        Met à jour les positions des moteurs en fonction du temps écoulé.
        :param delta_time: Temps écoulé (en secondes)
        """
       
        for motor in ["MOTOR_LEFT", "MOTOR_RIGHT"]:
            # La position augmente de (vitesse en dps * delta_time)
           
            self.motor_positions[motor] += self.motor_speeds[motor] * delta_time
        print(f"[Mock] Nouvelles positions des moteurs : {self.motor_positions}")

    def get_motor_position(self):
        """
        Retourne la position actuelle des moteurs sous forme de tuple (left, right).
        """
        print(f"[Mock] Lecture des positions : {self.motor_positions}")
        return (self.motor_positions["MOTOR_LEFT"], self.motor_positions["MOTOR_RIGHT"])
    def offset_motor_encoder(self, port, offset):
        """Simule le décalage de l'encodeur pour un moteur."""
        print(f"MockRobot2IN013: Décalage de l'encodeur du moteur '{port}' de {offset} degrés.")
        self.motor_positions[port] += offset

    def get_distance(self):
        """Simule la lecture du capteur de distance (en mm)."""
        simulated_distance = 100  # valeur fixe simulée
        print(f"MockRobot2IN013: Capteur de distance simulé retourne {simulated_distance} mm.")
        return simulated_distance

    def servo_rotate(self, position):
        """Simule la rotation du servo."""
        print(f"MockRobot2IN013: Rotation du servo à {position} degrés.")

    def start_recording(self):
        """Démarre l'enregistrement simulé des images."""
        print("MockRobot2IN013: Démarrage de l'enregistrement des images simulé.")


    def _stop_recording(self):
        """Arrête l'enregistrement simulé."""
        print("MockRobot2IN013: Arrêt de l'enregistrement des images simulé.")


    def _start_recording(self):
        """Fonction interne pour simuler l'enregistrement d'images."""
        print("MockRobot2IN013: Enregistrement des images simulé en cours.")


    def __getattr__(self, attr):
        """
        Simule l'accès aux attributs ou méthodes non définis explicitement.
        Par exemple, pour simuler set_led ou d'autres fonctions de EasyGoPiGo3.
        """
        def method(*args, **kwargs):
            print(f"MockRobot2IN013: Méthode '{attr}' appelée avec args {args} et kwargs {kwargs} (simulé).")
        return method
    
if __name__ == "__main__":
    robot = MockRobot2IN013()
    
    # Régler la vitesse des moteurs
    robot.set_motor_dps("left", 60)    # 60 dps pour le moteur gauche
    robot.set_motor_dps("right", 60)   # 60 dps pour le moteur droit
    
    # Obtenir et afficher les positions finales après les mises à jour
    positions = robot.get_motor_position()
    print("Positions finales :", positions)


