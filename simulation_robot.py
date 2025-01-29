from Map import Map
from Robot import Robot

class RobotSimulator:
    def __init__(self, rows, cols, map_instance):
        self.rows = rows
        self.cols = cols
        self.map = map_instance

    def simulate(self, robot, start_position, end_position):
        path = robot.find_path(start_position, end_position, self.rows, self.cols, self.map.obstacles)

        if not path:
            print("No path found!")
            self.map.message_label.config(text="No path found!")
            self.map.draw_x()
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

if __name__ == "__main__":
    rows, cols = 15, 15
    map_instance = Map(rows, cols)
    map_instance.draw_grid()

    robot = Robot((0, 0))
    simulator = RobotSimulator(rows, cols, map_instance)

    map_instance.keep_open()
