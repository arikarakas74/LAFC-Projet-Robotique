class RobotSimulator:
    def __init__(self, map_instance):
        self.map = map_instance
        self.running = False  
        self.robot = None
        self.current_after = None

    def simulate(self, robot):
        self.running = True
        self.map.robot = robot
        self.move_step(robot)

    def move_step(self, robot):
        if not self.running or robot is None:
            return
            
        
        if self.running:
            if self.current_after:
                self.map.window.after_cancel(self.current_after)
            self.current_after = self.map.window.after(50, 
                lambda: self.move_step(robot, end_position))

    def stop(self):
        self.running = False
        if self.current_after:
            self.map.window.after_cancel(self.current_after)
        if self.map.robot:
            self.map.canvas.delete("robot")
            self.map.robot = None

    def reset(self):
        self.stop()
        self.map.canvas.delete("all")
        self.map.obstacles.clear()
        self.map.start_position = None
        self.map.robot = None
        self.map.message_label.config(text="")
        self.map.window.update()