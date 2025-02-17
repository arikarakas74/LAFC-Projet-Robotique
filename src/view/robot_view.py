import math
# robot_view.py
class RobotView:
    def __init__(self, map_view):
        self.map_view = map_view
        self.WHEEL_BASE_WIDTH = 20.0


    def draw(self, x, y, direction_angle):
        # Dessiner le robot avec self.x et self.y
        self.map_view.canvas.delete("robot")
        size = 30
        front = (x + size * math.cos(direction_angle),y + size * math.sin(direction_angle))
        left = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_angle + math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_angle + math.pi / 2))
        right = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_angle - math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_angle - math.pi / 2))
       
        # Draw the robot as a blue triangle
        self.map_view.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def clear_robot(self):
        """Clears the robot from the canvas."""
        self.map_view.canvas.delete("robot")
        if self.map_view.speed_label:
            self.map_view.speed_label.config(text="")





    def set_robot_position(self, x, y):
        """Met à jour la position initiale du robot."""
        self.cx = x
        self.cy = y

