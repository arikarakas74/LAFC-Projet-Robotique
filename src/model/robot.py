import math
from utils.geometry import point_in_polygon  # Import the helper function

class Robot:
    def __init__(self, start_position, map_width, map_height, collision_radius=10):
        """Initializes the robot with its starting position and map dimensions."""
        self.x, self.y = start_position
        self.map_width = map_width
        self.map_height = map_height
        self.collision_radius = collision_radius
        self.direction_angle = 0
        self.velocity = 0
        self.acceleration = 0
        self.max_speed = 8
        self.friction = 0.1
        self.acceleration_rate = 0.2
        self.current_after = None
        self.event_listeners = []

    def add_event_listener(self, listener):
        """Adds an event listener to the robot."""
        self.event_listeners.append(listener)

    def notify_event_listeners(self, event_type, **kwargs):
        """Notifies all event listeners of an event."""
        for listener in self.event_listeners:
            listener(event_type, **kwargs)

    def is_collision(self, new_x, new_y, obstacles):
        """Checks if the new position collides with any obstacle."""
        for obstacle_id, (points, _, _) in obstacles.items():
            if point_in_polygon(new_x, new_y, points):  # Use the helper function
                return True
        return False

    def stop(self):
        """Stops the robot's movement."""
        if self.current_after:
            self.notify_event_listeners("cancel_after", after_id=self.current_after)
        self.acceleration = 0
        self.velocity = 0
        self.notify_event_listeners("robot_stopped")

    def turn_left(self):
        """Turns the robot to the left (counterclockwise)."""
        self.direction_angle -= 10
        self.direction_angle %= 360
        self.notify_event_listeners("update_view", x=self.x, y=self.y, direction_angle=self.direction_angle)
        self.notify_event_listeners("update_speed_label", velocity=self.velocity, direction_angle=self.direction_angle)
        print(f"turn_left: new_angle = {self.direction_angle}°")

    def turn_right(self):
        """Turns the robot to the right (clockwise)."""
        self.direction_angle += 10
        self.direction_angle %= 360
        self.notify_event_listeners("update_view", x=self.x, y=self.y, direction_angle=self.direction_angle)
        self.notify_event_listeners("update_speed_label", velocity=self.velocity, direction_angle=self.direction_angle)
        print(f"turn_right: new_angle = {self.direction_angle}°")

    def move_forward(self, event=None):
        """Starts moving the robot forward."""
        self.apply_acceleration(1)

    def move_backward(self, event=None):
        """Starts moving the robot backward."""
        self.apply_acceleration(-1)

    def apply_acceleration(self, direction):
        """Applies acceleration to the robot in the given direction."""
        self.acceleration = direction * self.acceleration_rate

    def stop_acceleration(self, event=None):
        """Stops the robot's acceleration."""
        self.apply_acceleration(0)

    def update_motion(self, obstacles, goal_position):
        """Updates the robot's motion, checking for collisions and goal position."""
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
        elif new_x > self.map_width - 10:
            new_x = self.map_width - 10

        if new_y < 10:
            new_y = 10
        elif new_y > self.map_height - 10:
            new_y = self.map_height - 10

        if not self.is_collision(new_x, new_y, obstacles):
            self.x = new_x
            self.y = new_y
            self.notify_event_listeners("update_view", x=self.x, y=self.y, direction_angle=self.direction_angle)

        if self.is_at_goal(goal_position):
            self.notify_event_listeners("goal_reached")
            self.stop()
            return

        self.notify_event_listeners("update_speed_label", velocity=self.velocity, direction_angle=self.direction_angle)
        self.current_after = self.notify_event_listeners("after", delay=16, callback=self.update_motion, obstacles=obstacles, goal_position=goal_position)

    def is_at_goal(self, goal_position):
        """Checks if the robot has reached the goal."""
        if not goal_position:
            return False

        goal_x, goal_y = goal_position
        distance = math.sqrt((self.x - goal_x) ** 2 + (self.y - goal_y) ** 2)

        return distance < 10

    def turn_right90(self):
        """Turns the robot 90 degrees to the right."""
        self.direction_angle += 90
        self.direction_angle %= 360
        self.notify_event_listeners("update_view", x=self.x, y=self.y, direction_angle=self.direction_angle)
        print(f"turn_right 90°: new_angle = {self.direction_angle}°")

    def draw_square(self, side_length=200, step_size=5, obstacles=None):
        """Makes the robot draw a square step by step."""
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

                if not self.is_collision(new_x, new_y, obstacles):
                    self.x = new_x
                    self.y = new_y
                    self.notify_event_listeners("update_view", x=self.x, y=self.y, direction_angle=self.direction_angle)
                    self.steps_moved += 1

                if self.steps_moved >= self.square_steps:
                    self.steps_moved = 0
                    self.current_side += 1
                    self.turn_right90()

                self.current_after = self.notify_event_listeners("after", delay=20, callback=move_step)
            else:
                self.acceleration = 0
                self.velocity = 0
                return

        move_step()

    def draw(self):
        """Draws the robot on the map."""
        x, y = self.x, self.y
        self.notify_event_listeners("robot_draw", x=x, y=y, direction_angle=self.direction_angle)