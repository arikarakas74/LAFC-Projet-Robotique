import math
# robot_view.py
class RobotView:
    def __init__(self, map_view):
        self.map_view = map_view


    def draw(self, x, y, direction_angle):
        # Dessiner le robot avec self.x et self.y
        self.map_view.canvas.delete("robot")
        size = 15
        front = (x + size * math.cos(direction_angle),y + size * math.sin(direction_angle))
        left = (x + size * math.cos(direction_angle + 2.2), y + size * math.sin(direction_angle + 2.2))
        right = (x + size * math.cos(direction_angle - 2.2), y + size * math.sin(direction_angle - 2.2))
       
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

