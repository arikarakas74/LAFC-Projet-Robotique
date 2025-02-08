import tkinter as tk
from view.robot_view import RobotView

class MapView:
    """Handles the visual representation of the map."""

    def __init__(self, parent, rows, cols, grid_size):
        self.parent = parent # 'parent' is now the Map class instance
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.canvas = tk.Canvas(parent.window, width=cols * grid_size, height=rows * grid_size)
        self.canvas.pack()
        self.width = cols * grid_size
        self.height = rows * grid_size
        self.message_label = tk.Label(parent.window, text="")
        self.message_label.pack(pady=10)
        self.speed_label = None
        self.robot_view = RobotView(self)  # Initialize robot_view

    def draw_grid(self): # Example, grid drawing might not be needed based on original code.
        """Draws the grid lines on the canvas."""
        for i in range(self.rows + 1):
            self.canvas.create_line(0, i * self.grid_size, self.width, i * self.grid_size, fill="lightgrey")
        for j in range(self.cols + 1):
            self.canvas.create_line(j * self.grid_size, 0, j * self.grid_size, self.height, fill="lightgrey")

    def draw_start(self, position):
        """Draws the start position marker."""
        if position:
            x, y = position
            self.canvas.delete("start")
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="yellow", tags="start")

    def draw_end(self, position):
        """Draws the end position marker."""
        if position:
            x, y = position
            self.canvas.delete("end")
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="green", tags="end")

    def draw_obstacle(self, points):
         """Draws an obstacle polygon."""
         return self.canvas.create_polygon(points, fill="red", outline="black")

    def delete_item(self, tag_or_id):
        """Deletes an item from the canvas by tag or ID."""
        self.canvas.delete(tag_or_id)

    def move_item(self, item_id, dx, dy):
        """Moves an item on the canvas."""
        self.canvas.move(item_id, dx, dy)

    def create_line(self, p1, p2, fill="red", width=2):
        """Creates a line on the canvas."""
        return self.canvas.create_line(p1, p2, fill=fill, width=width)

    def create_polygon(self, points, fill="red", outline="black"):
        """Creates a polygon on the canvas."""
        return self.canvas.create_polygon(points, fill=fill, outline=outline)

    def delete_obstacle_visual(self, polygon_id, line_ids):
        """Deletes the visual representation of an obstacle."""
        self.canvas.delete(polygon_id)
        for line_id in line_ids:
            self.canvas.delete(line_id)

    def delete_all(self):
        """Deletes all items on the canvas."""
        self.canvas.delete("all")
        if self.speed_label:
            self.speed_label.config(text="")
        self.robot_view.clear_robot()  # Clear the robot from the canvas

    def update_message_label(self, text):
        """Updates the message label text."""
        self.message_label.config(text=text)

    def create_speed_label(self):
        """Creates the speed label."""
        self.speed_label = tk.Label(self.parent.window, text="velocity: 0.00 | direction_angle: 0°")
        self.speed_label.pack()