import math

class Robot:
    """Represents the robot and its movement logic."""
    
    def __init__(self, start_position, map_instance, collision_radius=10):
        self.x, self.y = start_position
        self.map = map_instance
        self.collision_radius = collision_radius  # Defines the area around obstacles where collisions occur
    
    def is_collision(self, new_x, new_y):
        """Checks if the new position collides with any obstacle's border."""
        for obs_x, obs_y in self.map.obstacles:
            if abs(new_x - obs_x) < self.collision_radius and abs(new_y - obs_y) < self.collision_radius:
                return True
        return False

    def move_towards(self, target, speed=5):
        """Moves the robot towards the target position while avoiding obstacles."""
        target_x, target_y = target
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < speed:
            new_x, new_y = target
        else:
            new_x = self.x + (dx / distance) * speed
            new_y = self.y + (dy / distance) * speed

        # Check for collision before moving
        if self.is_collision(new_x, new_y):
            return False  # Stop movement if an obstacle is detected

        self.x, self.y = new_x, new_y

        # Correctly tag robot so it can be removed
        self.map.canvas.delete("robot")
        self.map.canvas.create_oval(self.x-5, self.y-5, self.x+5, self.y+5, fill="blue", tags="robot")

        return distance < speed  # Return True if the robot has reached the target

    def stop(self):
        """Stops the robot's movement and removes it from the canvas."""
        self.map.canvas.delete("robot")