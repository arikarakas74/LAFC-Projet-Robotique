import tkinter as tk
from robot import Robot
from simulator import RobotSimulator

class Map:
    """Handles the grid representation, user interactions, and visualization."""
    
    def __init__(self, rows, cols, grid_size=30):
        """Initializes the simulation window, control buttons, and grid parameters."""
        self.simulator = None  # Add simulator reference
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
        self.canvas.bind("<B1-Motion>", self.handle_drag)  # Bind mouse drag event
        self.canvas.bind("<Double-Button-1>", self.finalize_shape)  # Bind double-click to finalize shape
        self.current_shape = None
        self.current_points = []
        self.window.bind("<w>", self.move_forward)
        self.window.bind("<s>", self.move_backward)

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
        self.message_label.config(text="Click and drag to draw obstacles. Double-click to finish.")
        self.current_points = []
    
    def reset_map(self):
        """Resets both map and simulator states."""
        # Stop simulator first
        if self.simulator:
            self.simulator.stop()
            self.simulator = None  # Clear simulator reference
            
        # Clear canvas and robot
        self.canvas.delete("all")
        self.robot = None
        
        # Reset all variables
        self.start_position = None
        self.end_position = None
        self.obstacles.clear()
        self.current_points = []
        self.current_shape = None
        
        # Update UI
        self.message_label.config(text="Map reset.")
        self.canvas.update()
    
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
            if not self.current_shape:
                self.current_points = [(x, y)]
                self.current_shape = self.canvas.create_line(x, y, x, y, fill="red", width=2)
            else:
                self.current_points.append((x, y))
                self.canvas.create_line(self.current_points[-2], self.current_points[-1], fill="red", width=2)
    
    def handle_drag(self, event):
        """Handles mouse drag to draw obstacles."""
        if self.mode == 'set_obstacles' and self.current_shape:
            x, y = event.x, event.y
            self.current_points.append((x, y))
            self.canvas.create_line(self.current_points[-2], self.current_points[-1], fill="red", width=2)
    
    def is_shape_closed(self):
        """Checks if the drawn shape is closed."""
        if len(self.current_points) < 3:
            return False
        start = self.current_points[0]
        end = self.current_points[-1]
        # Allow some room for inaccuracy (e.g., 15 pixels)
        return abs(start[0] - end[0]) < 15 and abs(start[1] - end[1]) < 15
    
    def finalize_shape(self, event=None):
        """Finalizes the drawn shape and adds it as an obstacle."""
        if self.mode == 'set_obstacles' and self.current_shape:
            if self.is_shape_closed():
                self.canvas.delete(self.current_shape)
                self.current_shape = None
                self.obstacles.add(tuple(self.current_points))
                self.canvas.create_polygon(self.current_points, fill="red", outline="black")
                self.current_points = []
                self.message_label.config(text="Obstacle added.")
            else:
                self.message_label.config(text="Shape is not closed. Please double-click near the starting point.")
    
    def run_simulation(self):
        """Runs the robot simulation if start and end positions are set."""
        if not self.start_position or not self.end_position:
            self.message_label.config(text="Please set both start and end positions.")
            return
        robot = Robot(self.start_position, self)
        self.message_label.config(text="Use W to move forward and S to move backward.")
        #self.simulator = RobotSimulator(self)  # Store simulator reference
        #self.simulator.simulate(robot, self.end_position)

    def move_forward(self, event=None):
        if self.robot :
            self.robot.manual_move(direction=1) 
    
    def move_backward(self, event=None):
        if self.robot:
            self.robot.manual_move(direction=-1)
