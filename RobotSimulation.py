import tkinter as tk
from Robot import Robot  # Robot sınıfını içe aktar
from RobotSimulator import RobotSimulator  # RobotSimulator'u içe aktar

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
        self.mode = None
        self.simulation_running = False  # Simülasyonun çalışıp çalışmadığını kontrol için

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

    def run_simulation(self):
        """ Simülasyonu başlatır """
        if not self.start_position or not self.end_position:
            self.message_label.config(text="Please set both start and end positions.")
            return
        if self.start_position == self.end_position:
            self.message_label.config(text="Start and end positions cannot be the same.")
            return
        self.message_label.config(text="Simulation running...")
        self.window.update()

        # Robot ve Simülatör nesnelerini oluştur
        robot = Robot(self.start_position)
        simulator = RobotSimulator(self.rows, self.cols, self)

        # Simülasyonu başlat
        simulator.simulate(robot, self.start_position, self.end_position)

if __name__ == "__main__":
    rows, cols = 15, 15
    map_instance = Map(rows, cols)
    map_instance.draw_grid()
    map_instance.keep_open()
