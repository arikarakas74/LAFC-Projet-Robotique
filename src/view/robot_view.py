import math

class RobotView:
    def __init__(self, map_view):
        """Initializes the RobotView with a reference to the MapView."""
        self.map_view = map_view

    def draw(self, x, y, direction_angle):
        """Draws the robot on the canvas at the current position."""
        self.map_view.canvas.delete("robot")
        cx, cy = x, y
        size = 15
        angle = direction_angle 

        # Calculate the points of the triangle representing the robot
        front = (cx + size * math.cos(angle), cy + size * math.sin(angle))
        left = (cx + size * math.cos(angle + 2.2), cy + size * math.sin(angle + 2.2))
        right = (cx + size * math.cos(angle - 2.2), cy + size * math.sin(angle - 2.2))

        # Draw the robot as a blue triangle
        self.map_view.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def clear_robot(self):
        """Clears the robot from the canvas."""
        self.map_view.canvas.delete("robot")
        if self.map_view.speed_label:
            self.map_view.speed_label.config(text="")
