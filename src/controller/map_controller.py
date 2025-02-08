from model.map_model import MapModel
from view.map_view import MapView
from utils.geometry import point_in_polygon  # Import point_in_polygon

class MapController:
    """Handles user input and updates the map model and view."""

    def __init__(self, map_model: MapModel, map_view: MapView, window):
        """Initializes the MapController with references to the map model, its view, and the window."""
        self.map_model = map_model
        self.map_view = map_view
        self.window = window  # Store the window object
        self.map_model.add_event_listener(self.handle_map_event)

    def handle_map_event(self, event_type, **kwargs):
        """Handles events from the map model."""
        if event_type == "start_position_changed":
            self.map_view.draw_start(kwargs["position"])
        elif event_type == "end_position_changed":
            self.map_view.draw_end(kwargs["position"])
        elif event_type == "obstacle_added":
            self.map_view.draw_obstacle(kwargs["points"])
        elif event_type == "obstacle_removed":
            self.map_view.delete_item(kwargs["obstacle_id"])
        elif event_type == "map_reset":
            self.map_view.clear_all()

    def set_start_mode(self):
        """Activates start position setting mode."""
        self.mode = 'set_start'
        self.map_view.update_message_label(text="Click on the grid to set the start position.")  # Access map_view

    def set_obstacles_mode(self):
        """Activates obstacle placement mode."""
        self.mode = 'set_obstacles'
        self.map_model.current_points = []  # Clear current obstacle points
        self.map_model.current_lines = []  # Clear current obstacle lines
        self.map_view.update_message_label(text="Click and drag to draw obstacles. Double-click to finish.")  # Access map_view

    def handle_click(self, event):
        """Handles mouse clicks based on active mode."""
        x, y = event.x, event.y
        if self.mode == 'set_start':
            self.map_model.set_start_position((x, y))  # Call set_start_position on the map model
        elif self.mode == 'set_obstacles':
            if not self.map_model.current_shape:  # Access map_model
                # Check if the user clicked on an existing obstacle to start dragging
                for obstacle_id, (points, polygon_id, line_ids) in self.map_model.obstacles.items():  # Access map_model
                    if point_in_polygon(x, y, points):  # Use point_in_polygon from geometry module
                        self.map_model.dragging_obstacle = obstacle_id  # Use obstacle_id instead of polygon_id
                        self.map_model.drag_start = (x, y)  # Access map_model
                        return
                # Otherwise, start drawing a new obstacle
                self.map_model.current_points = [(x, y)]  # Access map_model
                self.map_model.current_shape = self.map_view.create_line((x, y), (x, y), fill="red", width=2)  # Access map_view
            else:
                self.map_model.current_points.append((x, y))  # Access map_model
                if len(self.map_model.current_points) > 1:
                    line_id = self.map_view.create_line(self.map_model.current_points[-2], (x, y), fill="red", width=2)  # Access map_view, map_model
                    self.map_model.current_lines.append(line_id)  # Access map_model

    def add_obstacle(self):
        """Adds an obstacle to the map model."""
        if self.map_model.current_points:
            points = self.map_model.current_points
            polygon_id = self.map_view.create_polygon(points, fill="red", outline="black")  # Access map_view
            obstacle_id = f"obstacle_{len(self.map_model.obstacles)}"  # Access map_model
            self.map_model.add_obstacle(obstacle_id, points, polygon_id, [])  # Call add_obstacle on the map model
            self.map_model.current_points = []  # Clear current points
            self.map_model.current_shape = None  # Clear current shape
            self.map_view.update_message_label(text="Obstacle added.")  # Access map_view

    def handle_drag(self, event):
        """Handles mouse drag to draw or move obstacles."""
        x, y = event.x, event.y
        if self.mode == 'set_obstacles' and self.map_model.current_shape:  # Access map_model
            # Drawing a new obstacle
            self.map_model.current_points.append((x, y))  # Access map_model
            line_id = self.map_view.create_line(self.map_model.current_points[-2], self.map_model.current_points[-1], fill="red", width=2)  # Access map_view, map_model
            self.map_model.current_lines.append(line_id)  # Access map_model
        elif self.map_model.dragging_obstacle:  # Access map_model
            # Moving an existing obstacle
            dx = x - self.map_model.drag_start[0]  # Access map_model
            dy = y - self.map_model.drag_start[1]  # Access map_model
            self.map_model.drag_start = (x, y)  # Access map_model
            obstacle_id = self.map_model.dragging_obstacle  # Get the correct obstacle ID
            points, polygon_id, line_ids = self.map_model.obstacles[obstacle_id]
            self.map_view.delete_item(polygon_id)  # Delete the original obstacle
            for line_id in line_ids:
                self.map_view.delete_item(line_id)  # Delete the original lines
            new_points = [(p[0] + dx, p[1] + dy) for p in points]
            new_polygon_id = self.map_view.create_polygon(new_points, fill="red", outline="black")  # Create the moved obstacle
            new_line_ids = [self.map_view.create_line(new_points[i], new_points[(i + 1) % len(new_points)], fill="red", width=2) for i in range(len(new_points))]
            self.map_model.obstacles[obstacle_id] = (new_points, new_polygon_id, new_line_ids)  # Update the obstacle's points in the dictionary

    def is_shape_closed(self):
        """Checks if the drawn shape is closed."""
        if len(self.map_model.current_points) < 3:  # Access map_model
            return False
        start = self.map_model.current_points[0]  # Access map_model
        end = self.map_model.current_points[-1]  # Access map_model
        # Allow some room for inaccuracy (e.g., 15 pixels)
        return abs(start[0] - end[0]) < 15 and abs(start[1] - end[1]) < 15

    def finalize_shape(self, event=None):
        """Finalizes the drawn shape and adds it as an obstacle."""
        if self.mode == 'set_obstacles' and self.map_model.current_shape:  # Access map_model
            if self.is_shape_closed():
                # Delete the temporary lines used for drawing
                for line_id in self.map_model.current_lines:  # Access map_model
                    self.map_view.delete_item(line_id)  # Access map_view
                self.map_model.current_lines = []  # Access map_model

                # Create the filled polygon
                self.add_obstacle()  # Call add_obstacle method
            else:
                self.map_view.update_message_label(text="Shape is not closed. Please double-click near the starting point.")  # Access map_view

    def delete_obstacle(self, event):
        """Deletes an obstacle when right-clicked."""
        x, y = event.x, event.y
        for obstacle_id, (points, polygon_id, line_ids) in self.map_model.obstacles.items():  # Access map_model
            if point_in_polygon(x, y, points):  # Use point_in_polygon from geometry module
                # Delete the polygon and any associated lines
                self.map_view.delete_obstacle_visual(polygon_id, line_ids)  # Access map_view
                self.map_model.remove_obstacle(obstacle_id)  # Access map_model
                self.map_view.update_message_label(text="Obstacle deleted.")  # Access map_view
                break

    def stop_drag(self, event):
        """Stops dragging an obstacle."""
        self.map_model.dragging_obstacle = None  # Access map_model
        self.map_model.drag_start = None  # Access map_model