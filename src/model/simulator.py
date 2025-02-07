import time

class RobotSimulator:
    """Gère la simulation du déplacement du robot."""

    def __init__(self, map_model, robot):
        self.map_model = map_model
        self.robot = robot
        self.running = False

    def start_simulation(self, end_position):
        """Démarre la simulation."""
        self.running = True
        while self.running:
            if self.robot.move_towards(end_position):
                print("🚀 Le robot a atteint sa destination !")
                self.running = False
            time.sleep(0.05)

    def stop_simulation(self):
        """Arrête la simulation."""
        self.running = False
