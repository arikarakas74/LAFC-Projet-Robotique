from vpython import *
import threading
import time
import math
import base64  # Vous n'aurez plus besoin de base64 ici, mais on peut le laisser
import os
# Imports nécessaires pour la capture en mémoire
from PIL import Image
import numpy as np 
import cv2 # Make sure cv2 is imported at the top

class VpythonView:
    def __init__(self, simulation_controller, key_handler):
        """ Initialisation de la vue 3D """
        self.simulation_controller = simulation_controller
        # self.images stockera maintenant des tableaux NumPy (images OpenCV)
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
        self.scene.caption = "Left: 0.0°/s, Right: 0.0°/s, Angle: 0.0°"

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

        #Mise à jour de label de la vitesse et l'angle
        speed_text = (
            f"Left: {state['left_speed']:.1f}°/s, "
            f"Right: {state['right_speed']:.1f}°/s, "
            f"Angle: {math.degrees(state['angle']):.1f}°"
        )
        self.scene.caption = speed_text


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
            # Capturer une image environ toutes les secondes
            sleep_time = 1.0 
            time_elapsed = time.time() - start_time
            actual_sleep = max(0, sleep_time - time_elapsed)
            if actual_sleep > 0:
                time.sleep(actual_sleep)



    def get_latest_image(self):
        """Récupère la dernière image avec métadonnées"""
        with self._lock:
            if self.images:
                return self.images[-1]
        return None

    def capture_embedded_image(self):
        """ Capture l'image, la sauvegarde, la relit et stocke le tableau NumPy si valide. """
        image_path = None
        try:
            # Définir le chemin de sauvegarde dans un sous-dossier du projet
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            captures_dir = os.path.join(src_dir, "captures")

            if not os.path.exists(captures_dir):
                os.makedirs(captures_dir)

            # Utiliser un timestamp avec microsecondes pour garantir l'unicité
            timestamp = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000000) % 1000000:06d}"
            # Générer le nom de base SANS .png
            base_filename = f"embedded_view_{timestamp}"
            # Construire le chemin complet SANS .png pour VPython capture
            vpython_capture_path = os.path.join(captures_dir, base_filename)

            # 1. Sauvegarder l'image sur le disque (VPython ajoutera .png)
            self.embedded_view.capture(vpython_capture_path)
            # print(f"Attempted to save image via VPython capture with base: {vpython_capture_path}") # Debug

            # 2. Attendre un court instant après la sauvegarde
            print(f"{time.strftime('%H:%M:%S')} - Saved (presumably with mangled name), waiting 0.1s...")
            time.sleep(3) 

            # 3. Prédire le nom de fichier "bizarre" que VPython semble créer
            # Prendre le chemin absolu de ce que nous avons passé à capture()
            absolute_vpython_capture_path = os.path.abspath(vpython_capture_path)
            # Remplacer les séparateurs de chemin par des underscores
            mangled_base_name = absolute_vpython_capture_path.replace(os.path.sep, '_')
            # Ajouter .png
            predicted_actual_filename = mangled_base_name + ".png"
            # Construire le chemin complet vers ce fichier dans le dossier de captures
            absolute_mangled_path = os.path.join(captures_dir, predicted_actual_filename)

            
            # --- Debugging File System Visibility ---
            print(f"{time.strftime('%H:%M:%S')} - Checking existence of predicted mangled path: {absolute_mangled_path}")
            file_exists = os.path.exists(absolute_mangled_path)
            print(f"{time.strftime('%H:%M:%S')} - Predicted mangled file exists? {file_exists}")
            if not file_exists:
                try:
                    print(f"{time.strftime('%H:%M:%S')} - Listing directory contents of: {captures_dir}")
                    dir_contents = os.listdir(captures_dir)
                    print(f"{time.strftime('%H:%M:%S')} - Directory contents: {dir_contents}")
                except Exception as list_err:
                    print(f"{time.strftime('%H:%M:%S')} - Error listing directory: {list_err}")
            # --- End Debugging ---

            print(f"{time.strftime('%H:%M:%S')} - Attempting to read with Pillow: {os.path.basename(absolute_mangled_path)}")
            
            opencv_image = None # Initialiser à None
            try:
                # Utiliser Pillow pour ouvrir le fichier avec le nom "bizarre"
                pil_image = Image.open(absolute_mangled_path)
                pil_image.load() # Forcer le chargement des données
                # Convertir l'image Pillow (RGB) en tableau NumPy OpenCV (BGR)
                opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                pil_image.close() # Fermer le handle du fichier
                print(f"{time.strftime('%H:%M:%S')} - Pillow read successful for {os.path.basename(absolute_mangled_path)}")
            except FileNotFoundError:
                 print(f"[WARN] Pillow Error: File not found at {absolute_mangled_path}. Skipping frame.")
            except Exception as pil_err:
                 print(f"[WARN] Pillow Error reading {os.path.basename(absolute_mangled_path)}: {pil_err}. Skipping frame.")
            

            # 4. Valider et stocker si la lecture et conversion ont réussi
            if opencv_image is not None and opencv_image.size > 0:
                # Ajouter l'image (tableau NumPy) à la liste de manière thread-safe
                with self._lock:
                    self.images.append(opencv_image)
                    # Limiter la taille si nécessaire
                    if len(self.images) > 10: # Garder seulement les 10 dernières images
                        self.images.pop(0)
                # print(f"Successfully read back and stored image: {os.path.basename(absolute_mangled_path)}") # Debug
            else:
                print(f"[WARN] Failed to read back image {os.path.basename(absolute_mangled_path)}. Skipping frame.")
                # Optionnel: Supprimer le fichier potentiellement corrompu/vide
                # if absolute_mangled_path and os.path.exists(absolute_mangled_path):
                #     try:
                #         os.remove(absolute_mangled_path)
                #     except Exception as remove_err:
                #         print(f"Error removing problematic file: {remove_err}")


        except Exception as e:
            print(f"Error during capture/read-back process for {predicted_actual_filename}: {e}")


    def analyze_image(self, image_data):
        """
        Analyse une image (fournie comme tableau NumPy) pour détecter une balise bleue.
        Retourne une liste des informations sur les balises détectées (centre et rayon).
        """
        detections = []
        # Pas besoin d'importer cv2/numpy ici si déjà fait globalement ou dans __init__
        # Assurez-vous que les imports sont présents au niveau du module.
        # try:
        #     import cv2
        #     import numpy as np
        # except ImportError:
        #     print("OpenCV et numpy sont nécessaires pour l'analyse d'image.")
        #     return detections

        # L'image est déjà un tableau NumPy, pas besoin de cv2.imread
        if image_data is None or image_data.size == 0:
            print("Erreur: Données d'image invalides fournies à analyze_image.")
            return detections
        
        # Utiliser directement image_data
        image_for_display = image_data.copy() # Copier si on veut dessiner dessus sans affecter l'original

        # Convertir en espace HSV pour une meilleure détection de couleur
        hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)

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
                cv2.circle(image_for_display, center, radius, (0, 255, 0), 2)
                detections.append({"center": center, "radius": radius})
                print(f"Balise bleue détectée au centre {center} avec un rayon de {radius}")

       
        # Optionnel: Afficher l'image avec les détections pour le débogage
        # cv2.imshow("Detection", image_for_display)
        # cv2.waitKey(1) 

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
        self.scene.caption = "Left: 0.0°/s, Right: 0.0°/s, Angle: 0.0°"
