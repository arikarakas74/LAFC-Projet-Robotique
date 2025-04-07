#!/usr/bin/env python3
import threading
import time
import math
import logging
from typing import Callable, List
from model.robot import RobotModel
from controller.robot_controller import RobotController

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

    def __init__(self, map_model, robot_models: List[RobotModel], cli_mode=False):
        """
        Initialise le contrôleur de simulation avec une liste de robots.
        """
        self.map_model = map_model
        self.robot_models = robot_models # Store list of models
        # Create a controller for each model
        self.robot_controllers = [RobotController(model, self.map_model, cli_mode and i == 0) 
                                  for i, model in enumerate(self.robot_models)]
        self.simulation_running = False
        self.listeners: List[Callable[[List[dict]], None]] = [] # Listener gets a list of states
        self.update_interval = 0.02

        # Logger pour la traçabilité des positions du robot
        self.position_logger = logging.getLogger('traceability.positions')
        self.position_logger.setLevel(logging.INFO)
        position_handler = logging.FileHandler('traceability_positions.log')
        position_formatter = logging.Formatter('%(asctime)s - Robot %(robot_name)s - Position: %(message)s')
        position_handler.setFormatter(position_formatter)
        self.position_logger.addHandler(position_handler)

        self.simulation_thread = None
        self.control_panel = None

    def set_control_panel(self, control_panel):
        """Stores a reference to the control panel for strategy updates."""
        self.control_panel = control_panel

    def add_state_listener(self, callback: Callable[[List[dict]], None]): # Expects list of states
        self.listeners.append(callback)

    def _notify_listeners(self):
        """Notifie tous les listeners avec la liste des états actuels des robots."""
        states = [model.get_state() for model in self.robot_models]
        for callback in self.listeners:
            callback(states)

    def run_simulation(self):
        if self.simulation_running:
            return
        print("Starting simulation...")
        # No need to set start pos here, assume it's done at RobotModel creation
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.simulation_thread.start()

    def run_loop(self):
        last_time = time.time()
        while self.simulation_running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            # Update physics for all robots
            for robot_model in self.robot_models:
                self.update_physics(robot_model, delta_time)
                
            self._notify_listeners()
            
            if self.control_panel:
                # Pass delta_time to control panel strategy step
                self.control_panel.step_strategy(delta_time)
                
            time.sleep(self.update_interval)

    def update_physics(self, robot_model: RobotModel, delta_time: float):
        """
        Met à jour la position et l'orientation d'un robot spécifique.
        """
        if delta_time <= 0:
            return

        left_speed = robot_model.motor_speeds["left"]
        right_speed = robot_model.motor_speeds["right"]

        left_velocity = (left_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)
        right_velocity = (right_speed / 360.0) * (2 * math.pi * self.WHEEL_RADIUS)

        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (right_velocity - left_velocity) / self.WHEEL_BASE_WIDTH # Corrected order

        effective_delta = delta_time * SPEED_MULTIPLIER

        # Initial position and angle
        current_x = robot_model.x
        current_y = robot_model.y
        current_angle_rad = math.radians(robot_model.direction_angle) # Convert degrees to radians

        if left_velocity == right_velocity:
            # Mouvement en ligne droite
            new_x = current_x + linear_velocity * math.cos(current_angle_rad) * effective_delta
            new_y = current_y + linear_velocity * math.sin(current_angle_rad) * effective_delta
            new_angle_rad = current_angle_rad
        else:
            # Mouvement circulaire (arc de cercle)
            if angular_velocity == 0: # Avoid division by zero if velocities are equal but non-zero
                 new_x = current_x + linear_velocity * math.cos(current_angle_rad) * effective_delta
                 new_y = current_y + linear_velocity * math.sin(current_angle_rad) * effective_delta
                 new_angle_rad = current_angle_rad
            else:
                delta_theta_rad = angular_velocity * effective_delta
                # Radius of curvature calculation needs careful check if angular_velocity is near zero
                # R = linear_velocity / angular_velocity # Simpler formula for radius
                # Let's use the ICC (Instantaneous Center of Curvature) approach for robustness
                R = (self.WHEEL_BASE_WIDTH / 2) * (right_velocity + left_velocity) / (right_velocity - left_velocity)

                # Center of rotation (ICC)
                icc_x = current_x - R * math.sin(current_angle_rad)
                icc_y = current_y + R * math.cos(current_angle_rad)

                # New position calculated by rotating around ICC
                new_x = icc_x + math.cos(delta_theta_rad) * (current_x - icc_x) - math.sin(delta_theta_rad) * (current_y - icc_y)
                new_y = icc_y + math.sin(delta_theta_rad) * (current_x - icc_x) + math.cos(delta_theta_rad) * (current_y - icc_y)
                new_angle_rad = current_angle_rad + delta_theta_rad

        # Convert angle back to degrees for the model
        new_angle_deg = math.degrees(new_angle_rad)
        
        # Mise à jour du modèle du robot
        robot_model.update_position(new_x, new_y, new_angle_deg)
        robot_model.update_motors(delta_time)
        
        # Log position with robot name
        self.position_logger.info(
            f"x={robot_model.x:.2f}, y={robot_model.y:.2f}, angle={robot_model.direction_angle:.2f}°",
            extra={'robot_name': robot_model.name}
        )

    def stop_simulation(self):
        self.simulation_running = False
        # Stop all robot controllers
        for controller in self.robot_controllers:
            controller.stop()
        if self.simulation_thread:
            print("Waiting for simulation thread to finish...")
            self.simulation_thread.join()
            self.simulation_thread = None
        print("Simulation stopped.")

    def reset_simulation(self):
        print("Resetting simulation...")
        was_running = self.simulation_running
        if was_running:
            self.stop_simulation()
        # Reset each robot model to its initial state (requires map_model to store initial positions or pass them)
        # For now, just reset angle and motors, position reset handled by MainApplication/MapController potentially
        # This might need adjustment based on how initial positions are managed.
        for robot_model in self.robot_models:
            # Find original start position (assuming map_model stores it or we pass it)
            # Simplified: Resetting angle and motors only here.
            robot_model.direction_angle = 0.0
            robot_model.motor_speeds = {"left": 0, "right": 0}
            robot_model.motor_positions = {"left": 0, "right": 0}
            robot_model.last_motor_positions = robot_model.motor_positions.copy()
            robot_model.drawing_active = False # Turn off drawing on reset
        # Restart simulation if it was running before reset
        # if was_running:
        #     self.run_simulation()
        self._notify_listeners() # Notify view about reset state

    # Helper to get a specific robot model (e.g., for strategies)
    def get_robot_model(self, index=0):
        if 0 <= index < len(self.robot_models):
            return self.robot_models[index]
        return None

    # Helper to get a specific robot controller (e.g., for keyboard bindings)
    def get_robot_controller(self, index=0):
        if 0 <= index < len(self.robot_controllers):
            return self.robot_controllers[index]
        return None
