import math
# robot_view.py
class RobotView:
    def __init__(self, map_view):
        self.map_view = map_view
        self.x = 0  # Remplace cx
        self.y = 0  # Remplace cy
        self.direction_angle = 0.0

    def draw(self, x, y, direction_angle):
        self.x = x
        self.y = y
        self.direction_angle = direction_angle
        # Dessiner le robot avec self.x et self.y
        self.map_view.canvas.delete("robot")
        size = 15
        front = (self.x + size * math.cos(self.direction_angle),self.y + size * math.sin(self.direction_angle))
        left = (self.x + size * math.cos(self.direction_angle + 2.2), self.y + size * math.sin(self.direction_angle + 2.2))
        right = (self.x + size * math.cos(self.direction_angle - 2.2), self.y + size * math.sin(self.direction_angle - 2.2))
       
        # Draw the robot as a blue triangle
        self.map_view.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def clear_robot(self):
        """Clears the robot from the canvas."""
        self.map_view.canvas.delete("robot")
        if self.map_view.speed_label:
            self.map_view.speed_label.config(text="")


    def update_position(self, x, y, direction_angle):
        """
        Met à jour la position visuelle du robot et redessine le robot sur le canvas.
        
        Args:
            x (float): Nouvelle position X.
            y (float): Nouvelle position Y.
            direction_angle (float): Nouvel angle de direction en radians.
        """
        # Met à jour la position interne
        print(self.cx -x, self.cy -y)
        self.cx = x
        self.cy = y
        self.direction_angle = direction_angle
        print(self.direction_angle)
        self.draw(self.cx,self.cy,self.direction_angle)

    def get_position(self):
        return self.x, self.y ,self.direction_angle
    def set_robot_position(self, x, y):
        """Met à jour la position initiale du robot."""
        self.cx = x
        self.cy = y

