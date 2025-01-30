import tkinter as tk
from robot import Robot
from simulator import RobotSimulator

class Map:
    """Handles the grid representation, user interactions, and visualization."""
    
    def __init__(self, rows, cols, grid_size=30):
        """Initializes the simulation window, control buttons, and grid parameters."""
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.window = tk.Tk()
        self.window.title("Robot Simulator")
        self.canvas = tk.Canvas(self.window, width=cols * grid_size, height=rows * grid_size)
        self.canvas.pack()
        self.control_frame = tk.Frame(self.window)
        self.control_frame.pack()

        # Buttons for user interaction
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
        self.message_label.pack(pady=10)

        self.obstacles = set()
        self.start_position = None
        self.end_position = None
        self.mode = None
        self.canvas.bind("<Button-1>", self.handle_click)
    
    # Modes for setting start, end, and obstacles
    def set_start_mode(self):
        """Activates start position setting mode."""
        self.mode = 'set_start'
        self.message_label.config(text="Click on the grid to set the start position.")
    
    def set_end_mode(self):
        """Activates end position setting mode."""
        self.mode = 'set_end'
        self.message_label.config(text="Click on the grid to set the end position.")
    
    def set_obstacles_mode(self):
        """Activates obstacle placement mode."""
        self.mode = 'set_obstacles'
        self.message_label.config(text="Click on the grid to add/remove obstacles.")
    
    def reset_map(self):
        """Resets the entire grid, clearing start, end, and obstacle positions."""
        self.canvas.delete("all")
        self.start_position = None
        self.end_position = None
        self.obstacles.clear()
        self.message_label.config(text="Map reset.")
    
    def handle_click(self, event):
        """Handles mouse clicks to set start, end, or obstacles based on active mode."""
        x, y = event.x, event.y
        if self.mode == 'set_start':
            if self.start_position:
                self.canvas.delete("start")
            self.start_position = (x, y)
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="yellow", tags="start")
        elif self.mode == 'set_end':
            if self.end_position:
                self.canvas.delete("end")
            self.end_position = (x, y)
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="green", tags="end")
        elif self.mode == 'set_obstacles':
            if (x, y) not in self.obstacles:
                self.obstacles.add((x, y))
                self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="red", tags=f"obstacle_{x}_{y}")
    
    def run_simulation(self):
        """Runs the robot simulation if start and end positions are set."""
        if not self.start_position or not self.end_position:
            self.message_label.config(text="Please set both start and end positions.")
            return
        robot = Robot(self.start_position, self)
        simulator = RobotSimulator(self)
        simulator.simulate(robot, self.end_position)

