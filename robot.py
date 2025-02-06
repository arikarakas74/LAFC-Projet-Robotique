import tkinter as tk
import math

class Robot:
    def __init__(self, start_position, map_instance, collision_radius=10):
        self.x, self.y = start_position
        self.map = map_instance
        self.collision_radius = collision_radius 
        self.direction_angle = 0  
        self.velocity = 0 
        self.acceleration = 0  
        self.max_speed = 8  
        self.friction = 0.1  
        self.acceleration_rate = 0.2 
        self.current_after = None 
        self.speed_label = tk.Label(self.map.window, text="velocity: 0.00 | direction_angle: 0°")
        self.speed_label.pack()    
        self.update_motion()

    def draw(self):
        """Dessine le robot à l'écran dans sa position actuelle."""
        self.map.canvas.delete("robot")  
        cx, cy = round(self.x), round(self.y) 
        size = 15
        angle = math.radians(self.direction_angle)

        p1 = (cx + size * math.cos(angle), cy + size * math.sin(angle))
        p2 = (cx + size * math.cos(angle + 2.5), cy + size * math.sin(angle + 2.5))
        p3 = (cx + size * math.cos(angle - 2.5), cy + size * math.sin(angle - 2.5))

        self.map.canvas.create_polygon(p1, p2, p3, fill="blue", tags="robot")
    
    def is_collision(self, new_x, new_y):
        """Checks if the new position collides with any obstacle."""
        for obstacle_id, (points, _, _) in self.map.obstacles.items():
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

    def stop(self):
        """Stops the robot's movement and removes it from the canvas."""
        if self.current_after:
            self.map.window.after_cancel(self.current_after)
        self.acceleration = 0
        self.velocity = 0
        self.map.canvas.delete("robot")  

    def turn_left(self):
        self.direction_angle -= 10
        self.direction_angle %= 360
        self.draw()
        self.speed_label.config(text=f"velocity: {self.velocity:.2f} | direction_angle: {self.direction_angle}°")

    def turn_right(self):
        self.direction_angle += 10
        self.direction_angle %= 360
        self.draw()
        self.speed_label.config(text=f"velocity: {self.velocity:.2f} | direction_angle: {self.direction_angle}°")

    def move_forward(self, event=None):
        self.apply_acceleration(1)

    def move_backward(self, event=None):
        self.apply_acceleration(-1)
            
    def apply_acceleration(self, direction):
        self.acceleration = direction * self.acceleration_rate
    
    def stop_acceleration(self, event=None):
        self.apply_acceleration(0)

    def update_motion(self):
        """Update the speed and execute the movement."""
        if self.map.robot is None:
            self.map.robot = self  

        self.velocity += self.acceleration

        if self.velocity > self.max_speed:
            self.velocity = self.max_speed
        elif self.velocity < -self.max_speed:
            self.velocity = -self.max_speed

        if self.acceleration == 0:
            if self.velocity > 0:
                self.velocity -= self.friction
                if self.velocity < 0:
                    self.velocity = 0
            elif self.velocity < 0:
                self.velocity += self.friction
                if self.velocity > 0:
                    self.velocity = 0

        angle_rad = math.radians(self.direction_angle)
        new_x = self.x + self.velocity * math.cos(angle_rad)
        new_y = self.y + self.velocity * math.sin(angle_rad)

        if new_x < 10:
            new_x = 10
        elif new_x > self.map.width - 10:
            new_x = self.map.width - 10

        if new_y < 10:
            new_y = 10
        elif new_y > self.map.height - 10:
            new_y = self.map.height - 10

        if not self.is_collision(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.draw()

        self.speed_label.config(text=f"velocity: {self.velocity:.2f} | direction_angle: {self.direction_angle}°")
        self.current_after = self.map.window.after(16, self.update_motion)

    def turn_right90(self):
        self.direction_angle += 90
        self.direction_angle %= 360 
        self.draw()

    def draw_square(self, side_length=200, step_size=5):
        """Makes the robot to draw a square step by step."""
        self.acceleration = 0
        self.velocity = 0

        self.square_steps = side_length // step_size
        self.current_side = 0
        self.steps_moved = 0

        def move_step():
            if self.current_side < 4:
                angle_rad = math.radians(self.direction_angle)
                new_x = self.x + step_size * math.cos(angle_rad)
                new_y = self.y + step_size * math.sin(angle_rad)

                if not self.is_collision(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    self.draw()
                    self.steps_moved += 1

                if self.steps_moved >= self.square_steps:
                    self.steps_moved = 0
                    self.current_side += 1
                    self.turn_right90() 

                self.current_after = self.map.window.after(20, move_step)
            else:
                self.acceleration = 0
                self.velocity = 0
                return

        move_step()
