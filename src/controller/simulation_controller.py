import threading
import time
from typing import Callable, List
from model.robot import RobotModel
from controller.robot_controller import RobotController

class SimulationController:
    def __init__(self, map_model, robot_model):
        self.robot_model = robot_model
        self.map_model = map_model
        self.robot_controller = RobotController(self.robot_model, self.map_model)
        self.simulation_running = False
        self.listeners: List[Callable[[dict], None]] = []
        self.update_interval = 0.02  # 50 Hz

    def add_state_listener(self, callback: Callable[[dict], None]):
        self.listeners.append(callback)

    def _notify_listeners(self):
        state = self.robot_model.get_state()
        for callback in self.listeners:
            callback(state)

    def run_simulation(self):
        if self.simulation_running:
            return

        if self.robot_model.x != self.map_model.start_position[0] or self.robot_model.y != self.map_model.start_position[1]:
            self.robot_model.x, self.robot_model.y = self.map_model.start_position

        self.simulation_running = True
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.daemon = True
        self.thread.start()

    def run_loop(self):
        last_time = time.time()
        while self.simulation_running:
            current_time = time.time()
            delta = current_time - last_time
            last_time = current_time

            self.robot_controller.update_physics(delta)
            self._notify_listeners()
            time.sleep(self.update_interval)

    def stop_simulation(self):
        self.simulation_running = False
        self.robot_controller.stop()
        if self.thread:
            self.thread.join()

    def reset_simulation(self):
        self.stop_simulation()
        self.robot_model.x, self.robot_model.y = self.map_model.start_position
        self.robot_model.direction_angle = 0.0