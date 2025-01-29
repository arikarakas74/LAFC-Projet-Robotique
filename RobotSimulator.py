from Robot import Robot

class RobotSimulator:
    def __init__(self, rows, cols, map_instance):
        self.rows = rows
        self.cols = cols
        self.map = map_instance

    def simulate(self, robot, start_position, end_position):
        self.map.simulation_running = True
        path = robot.find_path(start_position, end_position, self.rows, self.cols, self.map.obstacles)

        if not path:
            print("No path found!")
            self.map.message_label.config(text="No path found!")
            self.map.simulation_running = False
            self.map.draw_x()
            self.map.keep_open()
            return

        for step in path:
            if step == end_position:
                self.map.update_tile(step, "blue")
                self.map.message_label.config(text="Robot reached goal!")
            else:
                self.map.update_tile(step, "blue")
                self.map.refresh()
                self.map.wait(500)
                self.map.update_tile(step, "lightblue")
                self.map.refresh()
                self.map.wait(500)

        print("Path Taken:", path)
        self.map.simulation_running = False
        self.map.keep_open()
