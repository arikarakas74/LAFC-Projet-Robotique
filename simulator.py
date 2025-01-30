class RobotSimulator:
    """Controls the execution of the robot's movement and updates the UI."""
    
    def __init__(self, map_instance):
        self.map = map_instance
    
    def simulate(self, robot, end_position):
        """Runs the movement simulation, updating the UI as the robot moves."""
        while not robot.move_towards(end_position):
            self.map.window.update()
            self.map.window.after(50)
        self.map.message_label.config(text="Robot reached goal!")
