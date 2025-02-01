import math

class Robot:
    def __init__(self, start_position, map_instance, collision_radius=10):
        self.x, self.y = start_position
        self.map = map_instance
        self.collision_radius = collision_radius  # Defines the area around obstacles where collisions occur
        self.speed = 5
        self.draw()

    def draw(self):
        """Dessine le robot à l'écran dans sa position actuelle."""
        self.map.canvas.delete("robot")
        self.map.canvas.create_oval(self.x-5, self.y-5, self.x+5, self.y+5, fill="blue", tags="robot")
    
    def is_collision(self, new_x, new_y):
        """Checks if the new position collides with any obstacle."""
        for obstacle_id, (points, _, _) in self.map.obstacles.items():  # Unpack all three values
            if self.point_in_polygon(new_x, new_y, points):
                return True
        return False

    def point_in_polygon(self, x, y, polygon):
        """Ray casting algorithm for point in polygon test."""
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

    def move_towards(self, target, speed=5):
        """Moves the robot towards the target position."""
        target_x, target_y = target
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < speed:
            new_x, new_y = target
        else:
            new_x = self.x + (dx / distance) * speed
            new_y = self.y + (dy / distance) * speed

        if self.is_collision(new_x, new_y):
            return False

        self.x, self.y = new_x, new_y

        # Correctly tag robot so it can be removed
        self.map.canvas.delete("robot")
        self.map.canvas.create_oval(self.x-5, self.y-5, self.x+5, self.y+5, fill="blue", tags="robot")

        return distance < speed  # Return True if the robot has reached the target

    def stop(self):
        """Stops the robot's movement and removes it from the canvas."""
        self.map.canvas.delete("robot")

    def manual_move(self, direction):
        angle = 0
        dx = direction * self.speed * math.cos(angle)
        dy = direction * self.speed * math.sin(angle)

        new_x = self.x + dx
        new_y = self.y + dy

        if not self.is_collision(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.draw()
