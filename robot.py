import math

class Robot:
    """Represents the robot and its movement logic."""
    
    def __init__(self, start_position, map_instance):
        self.x, self.y = start_position
        self.map = map_instance
    
    def move_towards(self, target, speed=5):
        """Moves the robot towards the target position in small increments."""
        target_x, target_y = target
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < speed:
            self.x, self.y = target
            return True
        self.x += (dx / distance) * speed
        self.y += (dy / distance) * speed
        self.map.canvas.delete("robot")
        self.map.canvas.create_oval(self.x-5, self.y-5, self.x+5, self.y+5, fill="blue", tags="robot")
        return False
