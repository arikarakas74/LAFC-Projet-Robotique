import math

class RobotView:
    def __init__(self, map_view):
        """Initializes the RobotView with a reference to the MapView."""
        self.map_view = map_view

    def draw(self, x, y, direction_angle):
        """Draws the robot on the canvas at the current position."""
        self.map_view.canvas.delete("robot")
        cx, cy = round(x), round(y)
        size = 15
        angle = math.radians(direction_angle)

        # Calculate the points of the triangle representing the robot
        p1 = (cx + size * math.cos(angle), cy + size * math.sin(angle))
        p2 = (cx + size * math.cos(angle + 2.5), cy + size * math.sin(angle + 2.5))
        p3 = (cx + size * math.cos(angle - 2.5), cy + size * math.sin(angle - 2.5))

        # Draw the robot as a blue triangle
        self.map_view.canvas.create_polygon(p1, p2, p3, fill="blue", tags="robot")

    def clear_robot(self):
        """Clears the robot from the canvas."""
        self.map_view.canvas.delete("robot")
        if self.map_view.speed_label:
            self.map_view.speed_label.config(text="")
