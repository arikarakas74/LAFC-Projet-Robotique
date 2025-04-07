#!/usr/bin/env python3
import threading
import time
import math
import logging
from typing import List, Callable, Dict

from src.model.robot import RobotModel
from src.controller.robot_controller import RobotController
from src.model.map_model import MapModel

# Multiplicateur pour accélérer la simulation
SPEED_MULTIPLIER = 8.0

class SimulationController:
    """
    Contrôleur de simulation pour le déplacement du robot.

    Gère la mise à jour en temps réel de la position du robot et la notification des
    listeners de l'état du robot.
    """
    WHEEL_BASE_WIDTH = 20.0  # Distance entre les roues (cm)
    WHEEL_DIAMETER = 5.0     # Diamètre des roues (cm)
    WHEEL_RADIUS = WHEEL_DIAMETER / 2

    def __init__(self, map_model: MapModel, mouse_model: RobotModel, cat_model: RobotModel, cli_mode=False):
        """
        Initialise le contrôleur de simulation.

        :param map_model: Modèle de la carte (contenant par exemple la position de départ)
        :param mouse_model: Modèle du robot (position, moteurs, etc.)
        :param cat_model: Modèle du robot (position, moteurs, etc.)
        """
        self.map_model = map_model
        # Store models in a dictionary
        self.robot_models = {'mouse': mouse_model, 'cat': cat_model}
        
        # Create controllers for each robot
        self.robot_controllers = {
            'mouse': RobotController(mouse_model, map_model, cli_mode=cli_mode),
            'cat': RobotController(cat_model, map_model, cli_mode=False) # Cat not controlled by CLI
        }
        
        self.simulation_running = False
        self.listeners = []
        self.update_interval = 0.02  # 50 Hz update rate

        # Logger setup (make sure it's initialized properly)
        self.position_logger = logging.getLogger("SimulationController")
        log_file = "traceability_positions.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        if not self.position_logger.hasHandlers(): # Avoid adding multiple handlers
             self.position_logger.addHandler(handler)
        self.position_logger.setLevel(logging.INFO)

        self.simulation_thread = None

    def add_state_listener(self, callback: Callable[[dict], None]):
        """Ajoute un listener pour les mises à jour de l'état."""
        self.listeners.append(callback)

    def _notify_listeners(self):
        """Notifie tous les listeners avec l'état combiné des robots."""
        # Create a combined state dictionary for all robots
        combined_state = {}
        for robot_id, model in self.robot_models.items():
            combined_state[robot_id] = model.get_state()
            
        for callback in self.listeners:
            # Pass the combined state dictionary
            callback(combined_state) 

    def run_simulation(self):
        """Démarre la simulation dans un thread séparé."""
        if self.simulation_running:
            return

        # Positionner le robot au point de départ si nécessaire
        start_pos = self.map_model.start_position
        if (self.robot_models['mouse'].x, self.robot_models['mouse'].y) != start_pos:
            self.robot_models['mouse'].x, self.robot_models['mouse'].y = start_pos

        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.simulation_thread.start()

    def run_loop(self):
        """Boucle principale de la simulation, s'exécutant dans un thread séparé."""
        last_time = time.time()
        while self.simulation_running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            self.update_physics(delta_time)
            self._notify_listeners()
            time.sleep(self.update_interval)

    def update_physics(self, delta_time: float):
        """
        Met à jour la position et l'orientation du robot en fonction du temps écoulé.

        :param delta_time: Temps écoulé depuis la dernière mise à jour
        """
        if delta_time <= 0:
            return

        # --- Calcul des vitesses à partir des moteurs ---
        left_speed = self.robot_models['mouse'].motor_speeds["left"]
        right_speed = self.robot_models['mouse'].motor_speeds["right"]

        # Conversion des vitesses (degrés/s) en vitesse linéaire (cm/s)
        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

        # Calcul de la vitesse linéaire et angulaire
        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (left_velocity - right_velocity) / self.WHEEL_BASE_WIDTH

        # Application du multiplicateur de vitesse pour la simulation
        effective_delta = delta_time 

        # --- Mise à jour de la position en fonction du type de mouvement ---
        if left_velocity == right_velocity:
            # Mouvement en ligne droite
            new_x = self.robot_models['mouse'].x + linear_velocity * math.cos(self.robot_models['mouse'].direction_angle) * effective_delta
            new_y = self.robot_models['mouse'].y + linear_velocity * math.sin(self.robot_models['mouse'].direction_angle) * effective_delta
            new_angle = self.robot_models['mouse'].direction_angle
        else:
            # Mouvement circulaire (arc de cercle)
            delta_theta = angular_velocity * effective_delta
            R = (self.WHEEL_BASE_WIDTH / 2) * (left_velocity + right_velocity) / (left_velocity - right_velocity)
            # Centre de rotation
            center_x = self.robot_models['mouse'].x - R * math.sin(self.robot_models['mouse'].direction_angle)
            center_y = self.robot_models['mouse'].y + R * math.cos(self.robot_models['mouse'].direction_angle)
            # Nouvelle position calculée sur l'arc
            new_x = center_x + R * math.sin(self.robot_models['mouse'].direction_angle + delta_theta)
            new_y = center_y - R * math.cos(self.robot_models['mouse'].direction_angle + delta_theta)
            new_angle = self.robot_models['mouse'].direction_angle + delta_theta

        # Mise à jour du modèle du robot
        self.robot_models['mouse'].update_position(new_x, new_y, new_angle)
        self.robot_models['mouse'].update_motors(delta_time)
        
        

        # Enregistrement de la position actuelle pour la traçabilité
        self.position_logger.info(
            f"x={self.robot_models['mouse'].x:.2f}, y={self.robot_models['mouse'].y:.2f}, angle={math.degrees(self.robot_models['mouse'].direction_angle):.2f}°"
        )

    def stop_simulation(self):
        """Arrête la simulation et le contrôleur du robot."""
        self.simulation_running = False
        for robot, controller in self.robot_controllers.items():
            controller.stop()
        if self.simulation_thread:
            self.simulation_thread.join()

    def reset_simulation(self):
        """
        Réinitialise la simulation en arrêtant le contrôleur et en repositionnant le robot
        à la position de départ.
        """
        self.stop_simulation()
        for robot, model in self.robot_models.items():
            model.x, model.y = self.map_model.start_position
            model.direction_angle = 0.0
