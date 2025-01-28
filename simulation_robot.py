import tkinter as tk
from queue import PriorityQueue

class Map:
    def __init__(self, rows, cols, grid_size=50):
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.window = tk.Tk()
        self.window.title("Robot Simulator")

        self.canvas = tk.Canvas(self.window, width=cols * grid_size, height=rows * grid_size)
        self.canvas.pack()

        self.control_frame = tk.Frame(self.window)
        self.control_frame.pack()

        self.set_start_button = tk.Button(self.control_frame, text="Set Start", command=self.set_start_mode)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_end_button = tk.Button(self.control_frame, text="Set End", command=self.set_end_mode)
        self.set_end_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_obstacles_button = tk.Button(self.control_frame, text="Set Obstacles", command=self.set_obstacles_mode)
        self.set_obstacles_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = tk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_map)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.message_label = tk.Label(self.window, text="")
        self.message_label.pack()

        self.obstacles = set()
        self.start_position = None
        self.end_position = None
        self.mode = None  # Modes: 'set_start', 'set_end', 'set_obstacles', None

        self.canvas.bind("<Button-1>", self.handle_click)

    def draw_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.draw_tile((i, j), "white")

    def draw_tile(self, position, color):
        x, y = position
        x1 = y * self.grid_size
        y1 = x * self.grid_size
        x2 = x1 + self.grid_size
        y2 = y1 + self.grid_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def handle_click(self, event):
        col = event.x // self.grid_size
        row = event.y // self.grid_size
        position = (row, col)

        if self.mode == 'set_start':
            if position in self.obstacles:
                self.message_label.config(text="Cannot set start on an obstacle.")
                return
            if self.start_position:
                self.draw_tile(self.start_position, "white")
            self.start_position = position
            self.draw_tile(position, "yellow")
            self.mode = None
            self.message_label.config(text="Start position set.")
        elif self.mode == 'set_end':
            if position in self.obstacles:
                self.message_label.config(text="Cannot set end on an obstacle.")
                return
            if self.end_position:
                self.draw_tile(self.end_position, "white")
            self.end_position = position
            self.draw_tile(position, "green")
            self.mode = None
            self.message_label.config(text="End position set.")
        elif self.mode == 'set_obstacles':
            self.toggle_obstacle(position)
        else:
            pass

    def toggle_obstacle(self, position):
        if position == self.start_position or position == self.end_position:
            self.message_label.config(text="Cannot place an obstacle on start/end position.")
            return
        if position in self.obstacles:
            self.obstacles.remove(position)
            self.draw_tile(position, "white")
            self.message_label.config(text=f"Obstacle removed at {position}.")
        else:
            self.obstacles.add(position)
            self.draw_tile(position, "red")
            self.message_label.config(text=f"Obstacle added at {position}.")

    def set_start_mode(self):
        self.mode = 'set_start'
        self.message_label.config(text="Click on the grid to set the start position.")

    def set_end_mode(self):
        self.mode = 'set_end'
        self.message_label.config(text="Click on the grid to set the end position.")

    def set_obstacles_mode(self):
        self.mode = 'set_obstacles'
        self.message_label.config(text="Click on the grid to add/remove obstacles.")

    def reset_map(self):
        if self.simulation_running :
            self.message_label.config(text="Cannot reset the map during the simulation.")
            return

        self.obstacles.clear()
        self.start_position = None
        self.end_position = None
        self.message_label.config(text="Map reset.")
        self.draw_grid()

    def update_tile(self, position, color):
        self.draw_tile(position, color)

    def draw_x(self):
        x1 = 0
        y1 = 0
        x2 = self.cols * self.grid_size
        y2 = self.rows * self.grid_size
        self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
        self.canvas.create_line(x1, y2, x2, y1, fill="red", width=2)

    def refresh(self):
        self.window.update()

    def wait(self, ms):
        self.window.after(ms)

    def keep_open(self):
        self.window.mainloop()

    def run_simulation(self):
        if not self.start_position or not self.end_position:
            self.message_label.config(text="Please set both start and end positions.")
            return
        if self.start_position == self.end_position:
            self.message_label.config(text="Start and end positions cannot be the same.")
            return
        self.message_label.config(text="Simulation running...")
        self.window.update()

        robot = Robot(self.start_position)
        simulator = RobotSimulator(self.rows, self.cols, self)
        simulator.simulate(robot, self.start_position, self.end_position)

class Robot:
    def __init__(self, start_position):
        self.position = start_position
        self.path = []

    def find_path(self, start, goal, rows, cols, obstacles):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}

        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            _, current = frontier.get()

            if current == goal:
                break

            for dx, dy in [(-1,  0), (1,  0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                next_node = (current[0] + dx, current[1] + dy)
                if (0 <= next_node[0] < rows and 0 <= next_node[1] < cols and
                    next_node not in obstacles):
                    new_cost = cost_so_far[current] + (1.414 if dx != 0 and dy != 0 else 1)
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + heuristic(goal, next_node)
                        frontier.put((priority, next_node))
                        came_from[next_node] = current

        # Reconstruct path
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                return []
        path.append(start)
        path.reverse()
        return path

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

if __name__ == "__main__":
    rows, cols = 15, 15

    map_instance = Map(rows, cols)
    map_instance.draw_grid()
    map_instance.keep_open()
