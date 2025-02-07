import math

class RobotView:
    def __init__(self, map_instance):
        self.map = map_instance
        self.speed_label = None

    def set_speed_label(self, label):
        """Sets the speed label created in view."""
        self.speed_label = label

    def draw(self, x, y, direction_angle):
        """Draws the robot on the canvas at the current position."""
        self.map.map_view.canvas.delete("robot")
        cx, cy = round(x), round(y)
        size = 15
        angle = math.radians(direction_angle)

        p1 = (cx + size * math.cos(angle), cy + size * math.sin(angle))
        p2 = (cx + size * math.cos(angle + 2.5), cy + size * math.sin(angle + 2.5))
        p3 = (cx + size * math.cos(angle - 2.5), cy + size * math.sin(angle - 2.5))

        self.map.map_view.canvas.create_polygon(p1, p2, p3, fill="blue", tags="robot")

    def update_speed_label(self, velocity, direction_angle):
        """Updates the speed label text."""
        if self.speed_label:
            self.speed_label.config(text=f"velocity: {velocity:.2f} | direction_angle: {direction_angle}°")
