import tkinter as tk
from Robot import Robot
from RobotSimulator import RobotSimulator

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

if __name__ == "__main__":
    rows, cols = 15, 15

    map_instance = Map(rows, cols)
    map_instance.draw_grid()
    map_instance.keep_open()
