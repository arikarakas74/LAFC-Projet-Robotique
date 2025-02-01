import tkinter as tk
from robot import Robot
from simulator import RobotSimulator

class Map:
    """Handles the grid representation, user interactions, and visualization."""
    
    def __init__(self, rows, cols, grid_size=50):
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

        self.obstacles = {}  # Store obstacles as {id: (points, polygon_id, line_ids)}
        self.start_position = None
        self.end_position = None
        self.mode = None
        self.current_shape = None
        self.current_points = []
        self.current_lines = []  # Track lines created during drawing
        self.dragging_obstacle = None  # Track which obstacle is being dragged
        self.drag_start = None  # Track the starting point of the drag

        self.window.bind("<w>", self.move_forward)
        self.window.bind("<s>", self.move_backward)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<Double-Button-1>", self.finalize_shape)
        self.canvas.bind("<Button-3>", self.delete_obstacle)  # Right-click to delete obstacle
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)  # Stop dragging on mouse release

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
        self.current_lines = []  # Reset lines when entering obstacle mode
    
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
                # Check if the user clicked on an existing obstacle to start dragging
                for obstacle_id, (points, polygon_id, line_ids) in self.obstacles.items():
                    if self.point_in_polygon(x, y, points):
                        self.dragging_obstacle = polygon_id
                        self.drag_start = (x, y)
                        return
                # Otherwise, start drawing a new obstacle
                self.current_points = [(x, y)]
                self.current_shape = self.canvas.create_line(x, y, x, y, fill="red", width=2)
            else:
                self.current_points.append((x, y))
                line_id = self.canvas.create_line(self.current_points[-2], self.current_points[-1], fill="red", width=2)
                self.current_lines.append(line_id)  # Track the line
    
    def handle_drag(self, event):
        """Handles mouse drag to draw or move obstacles."""
        x, y = event.x, event.y
        if self.mode == 'set_obstacles' and self.current_shape:
            # Drawing a new obstacle
            self.current_points.append((x, y))
            line_id = self.canvas.create_line(self.current_points[-2], self.current_points[-1], fill="red", width=2)
            self.current_lines.append(line_id)  # Track the line
        elif self.dragging_obstacle:
            # Moving an existing obstacle
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            self.drag_start = (x, y)
            self.canvas.move(self.dragging_obstacle, dx, dy)
            # Update the obstacle's points in the dictionary
            for obstacle_id, (points, polygon_id, line_ids) in self.obstacles.items():
                if polygon_id == self.dragging_obstacle:
                    new_points = [(p[0] + dx, p[1] + dy) for p in points]
                    self.obstacles[obstacle_id] = (new_points, polygon_id, line_ids)
                    break
    
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
                # Delete the temporary lines used for drawing
                for line_id in self.current_lines:
                    self.canvas.delete(line_id)
                self.current_lines = []  # Clear the list of lines

                # Create the filled polygon
                polygon_id = self.canvas.create_polygon(self.current_points, fill="red", outline="black")
                obstacle_id = f"obstacle_{len(self.obstacles)}"
                self.obstacles[obstacle_id] = (self.current_points, polygon_id, [])
                self.current_points = []
                self.current_shape = None
                self.message_label.config(text="Obstacle added.")
            else:
                self.message_label.config(text="Shape is not closed. Please double-click near the starting point.")
    
    def delete_obstacle(self, event):
        """Deletes an obstacle when right-clicked."""
        x, y = event.x, event.y
        for obstacle_id, (points, polygon_id, line_ids) in self.obstacles.items():
            if self.point_in_polygon(x, y, points):
                # Delete the polygon and any associated lines
                self.canvas.delete(polygon_id)
                for line_id in line_ids:
                    self.canvas.delete(line_id)
                del self.obstacles[obstacle_id]
                self.message_label.config(text="Obstacle deleted.")
                break
    
    def point_in_polygon(self, x, y, polygon):
        """Determines if a point is inside a polygon using the ray casting algorithm."""
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def stop_drag(self, event):
        """Stops dragging an obstacle."""
        self.dragging_obstacle = None
        self.drag_start = None
    
    def run_simulation(self):
        if not self.start_position or not self.end_position:
            self.message_label.config(text="Please set both start and end positions.")
            return
        self.robot = Robot(self.start_position, self)  # Create robot instance
        self.simulator = RobotSimulator(self)
        self.simulator.simulate(self.robot, self.end_position)

    def move_forward(self, event=None):
        if self.robot:
            self.robot.manual_move(1)

    def move_backward(self, event=None):
        if self.robot:
            self.robot.manual_move(-1)

    def reset_map(self):
        if self.simulator:
            self.simulator.stop()
            self.simulator = None
        
        if self.robot:
            self.robot.stop()
            self.robot = None
            
        self.canvas.delete("all")
        self.start_position = None
        self.end_position = None
        self.obstacles.clear()
        self.current_points = []
        self.current_shape = None
        self.current_lines = []
        self.dragging_obstacle = None
        self.drag_start = None
        self.message_label.config(text="Map reset.")
        self.canvas.update()


        
