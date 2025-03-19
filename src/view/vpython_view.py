from vpython import *
import threading
import time
import math

class VpythonView:
    def __init__(self, simulation_controller, key_handler):
        """ Initialisation de la vue 3D """
        self.simulation_controller = simulation_controller

        # Création de la scène 3D
        self.scene = canvas(title="3D Robot Simulation", width=800, height=600)
        self.scene.center = vector(400, 0, 300)
        self.scene.background = color.white
        self.scene.forward = vector(0, -1, -1)  # Ajustement de l'angle de la caméra

        # Liaison des événements du clavier
        self.scene.bind("keydown", key_handler)

        # Création du sol
        self.floor = box(pos=vector(400, -1, 300), size=vector(800, 1, 600), color=color.green)

         # Création du corps du robot
        self.robot_body = cylinder(pos=vector(400, 5, 300), axis=vector(0, 10, 0), radius=10, color=color.blue)

        # Roues du robot
        self.wheel_left = cylinder(pos=vector(390, 3, 300), axis=vector(0, 6, 0), radius=3, color=color.black)
        self.wheel_right = cylinder(pos=vector(410, 3, 300), axis=vector(0, 6, 0), radius=3, color=color.black)

        # Surveillance de l'état du robot
        self.simulation_controller.add_state_listener(self.update_robot)

        # Trajectoire du robot
        self.path = curve(color=color.red, radius=1)

        # Lancement du thread de rendu
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def update_robot(self, state):
        """Mise à jour de la position du robot dans la scène 3D"""
        x, y = state['x'], state['y']
        angle = state['angle']  

        # Mise à jour de la position du robot
        self.robot_body.pos = vector(x, 5, y)
        
        # Rotation du robot
        self.robot_body.axis = vector(10 * math.cos(angle), 0, 10 * math.sin(angle))

        # Les roues suivent la rotation
        self.wheel_left.pos = vector(x - 10 * math.sin(angle), 3, y + 10 * math.cos(angle))
        self.wheel_right.pos = vector(x + 10 * math.sin(angle), 3, y - 10 * math.cos(angle))

        self.path.append(vector(x, 0, y))

    def run(self):
        """ Rafraîchissement continu de l'affichage 3D """
        while self.running:
            rate(50)  # 50 FPS

    def stop(self):
        import os
        """ Arrêt de la mise à jour de la vue 3D et sortie complète du processus """
        self.running = False

        # Forcer la sortie du processus Python
        os._exit(0)


    def reset_vpython_view(self):
        self.robot_body.pos = vector(400, 5, 300)
        self.robot_body.axis=vector(0, 10, 0)
        self.wheel_left.pos = vector(390, 3, 300)
        self.wheel_left.axis=vector(0, 6, 0)
        self.wheel_right.pos = vector(410, 3, 300)
        self.wheel_right.axis=vector(0, 6, 0)
        self.path.clear()
