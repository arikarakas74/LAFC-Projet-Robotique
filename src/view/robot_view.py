import math

class RobotView:
    def __init__(self, map_view):
        """Initializes the RobotView with a reference to the MapView."""
        self.map_view = map_view

    def draw(self, x, y, direction_angle, left_speed, right_speed):
        """Draws the robot on the canvas at the current position."""
        self.map_view.canvas.delete("robot")
        cx, cy = x, y
        size = 15
        angle = math.radians(direction_angle)

        if left_speed == right_speed:
            R = float('inf')
            Cx, Cy = None, None
        else:
            # Dönüş yarıçapını hesapla
            WHEEL_BASE_WIDTH = 10.0  # cm (İki tekerlek arası mesafe)
            R = (WHEEL_BASE_WIDTH / 2) * (left_speed + right_speed) / (right_speed - left_speed)

            # Dönüş merkezini hesapla
            Cx = cx - R * math.sin(angle)
            Cy = cy + R * math.cos(angle)

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
