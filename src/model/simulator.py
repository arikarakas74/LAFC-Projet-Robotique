class RobotSimulator:
    def __init__(self, map_instance):
        self.map = map_instance
        self.running = False
        self.robot = None
        self.current_after = None

    def simulate(self, robot, end_position):
        self.running = True
        self.map.robot = robot
        self.move_step(robot, end_position) # Example - adapt if needed

    def move_step(self, robot, end_position): # Example - adapt or remove if needed
        if not self.running or robot is None:
            return

        # ... (Logic for one simulation step, if needed, otherwise logic can be in robot.py)
        # This is a placeholder, original code might not require a simulator class for movement.
        # Adapt or remove this method based on your actual simulation needs.

        if self.running:
            if self.current_after:
                self.map.window.after_cancel(self.current_after)
            self.current_after = self.map.window.after(50,
                lambda: self.move_step(robot, end_position)) # Example delay

    def stop(self):
        self.running = False
        if self.current_after:
            self.map.window.after_cancel(self.current_after)
        if self.map.robot:
            self.map.map_view.canvas.delete("robot") # Access map_view
            self.map.robot = None

    def reset(self):
        self.stop()
        self.map.map_view.canvas.delete("all") # Access map_view
        self.map.map_model.reset() # Access map_model to reset data
        self.map.robot = None
        self.map.map_view.message_label.config(text="") # Access map_view
        self.map.window.update()