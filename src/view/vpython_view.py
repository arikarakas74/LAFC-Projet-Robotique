
from vpython import *
import threading
import time
import math
import base64  # Vous n'aurez plus besoin de base64 ici, mais on peut le laisser
import os

class VpythonView:
    def __init__(self, simulation_controller, key_handler):
        """ Initialisation de la vue 3D """
        self.simulation_controller = simulation_controller
        self.images=[]
        self._running = False
        self._lock = threading.Lock()
        self.frame_rate = 30

        # Création de la scène principale
        self.scene = canvas(title="3D Robot Simulation", width=800, height=600)
        self.scene.center = vector(400, 0, 300)
        self.scene.background = color.white
        self.scene.forward = vector(0, -1, -1)  # Angle de la caméra globale
        self.scene.bind("keydown", key_handler)

        # Création du sol
        self.floor = box(pos=vector(400, -1, 300), size=vector(800, 1, 600), color=color.green)

        # Création du robot
        self.robot_body = cylinder(pos=vector(400, 5, 300), axis=vector(0, 10, 0), radius=10, color=color.blue)
        self.wheel_left = cylinder(pos=vector(390, 3, 300), axis=vector(0, 6, 0), radius=3, color=color.black)
        self.wheel_right = cylinder(pos=vector(410, 3, 300), axis=vector(0, 6, 0), radius=3, color=color.black)
        self.direction_marker = sphere(pos=vector(400, 10, 310), radius=3, color=color.red)

        # Lien avec le contrôleur de simulation
        self.simulation_controller.add_state_listener(self.update_robot)

        # Trajectoire du robot
        self.path = curve(color=color.red, radius=1)

        # Ajout de la vue de la caméra embarquée (fenêtre secondaire)
        self.embedded_view = canvas(title="Vue embarquée", width=400, height=300, x=810, y=0)
        self.embedded_view.background = color.gray(0.8)

        # Lancement du thread de rendu
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.start_capture()

    def update_robot(self, state):
        """ Mise à jour de la position du robot et de la vue embarquée """
        x, y = state['x'], state['y']
        angle = state['angle']

        # Mise à jour de la position et de l'orientation du robot
        self.robot_body.pos = vector(x, 5, y)
        self.wheel_left.pos = vector(x - 10 * math.sin(angle), 3, y + 10 * math.cos(angle))
        self.wheel_right.pos = vector(x + 10 * math.sin(angle), 3, y - 10 * math.cos(angle))
        self.direction_marker.pos = vector(x + 10 * math.cos(angle), 10, y + 10 * math.sin(angle))
        self.path.append(vector(x, 0, y))

        # Mise à jour de la vue embarquée (caméra sur le robot)
        cam_pos = vector(x, 5 + 8, y)
        cam_forward = vector(math.cos(angle), 0, math.sin(angle))
        self.embedded_view.camera.pos = cam_pos
        self.embedded_view.camera.axis = cam_forward * 20  # "20" définit la distance de vision
        self.embedded_view.camera.up = vector(0, 1, 0)


    def start_capture(self):
        """Démarre la simulation de capture continue"""
        self._running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.start()
        
    def stop_capture(self):
        """Arrête la simulation"""
        self._running = False
        self.thread.join()

    def _capture_loop(self):
        """Boucle de capture réaliste avec timing précis"""
        while self._running:
            start_time = time.time()
            self.capture_embedded_image()
            sleep_time = 0.02
            if sleep_time > 0:
                time.sleep(sleep_time)



    def get_latest_image(self):
        """Récupère la dernière image avec métadonnées"""
        with self._lock:
            if self.images:
                return self.images[-1]
        return None

    def capture_embedded_image(self):
            
            # Définir le dossier de destination et le créer s'il n'existe pas
            directory = r"C:\Users\PC01\Downloads"
            
     
            # Générer un nom de fichier unique (seulement le nom, sans chemin)
            filename = f"capture_{time.strftime('%Y%m%d-%H%M%S')}"
            
            # Capturer l'image en passant uniquement le nom du fichier
            self.embedded_view.capture(filename)
            print(directory+"\\"+filename)
            # Attendre un court instant pour s'assurer que le fichier a été créé
            time.sleep(0.5)
            self.images.append(directory+"\\"+filename+".png")
            


    def analyze_image(self,image):
        """
        Charge et analyse une image pour détecter une balise bleue.
        Retourne une liste des informations sur les balises détectées (centre et rayon).
        """
        detections = []
        try:
            import cv2
            import numpy as np
        except ImportError:
            print("OpenCV et numpy sont nécessaires pour l'analyse d'image.")
            return detections

        # Charger l'image
        image = cv2.imread(str(image ))
        if image is None:
            print("Erreur lors du chargement de l'image.")
            return detections

        # Convertir en espace HSV pour une meilleure détection de couleur
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Définir la plage de couleur pour le bleu
        lower_blue = np.array([100, 150, 0])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Réduire le bruit avec des opérations morphologiques
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        # Détecter les contours dans le masque
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Parcourir les contours détectés
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:  # Seuil pour ignorer les petits bruits
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(image, center, radius, (0, 255, 0), 2)
                detections.append({"center": center, "radius": radius})
                print(f"Balise bleue détectée au centre {center} avec un rayon de {radius}")

       

        return detections


    def run(self):
        """ Rafraîchissement continu de l'affichage 3D """
        while self.running:
            rate(50)  # 50 FPS

    def stop(self):
        import os
        """ Arrêt de la mise à jour de la vue 3D et sortie du processus """
        self.running = False
        os._exit(0)

    def reset_vpython_view(self):
        self.robot_body.pos = vector(400, 5, 300)
        self.robot_body.axis = vector(0, 10, 0)
        self.wheel_left.pos = vector(390, 3, 300)
        self.wheel_left.axis = vector(0, 6, 0)
        self.wheel_right.pos = vector(410, 3, 300)
        self.wheel_right.axis = vector(0, 6, 0)
        self.direction_marker.pos = vector(400, 10, 310)
        self.path.clear()
