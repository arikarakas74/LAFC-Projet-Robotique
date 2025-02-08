class MapController:
    """Handles user input and updates the map model and view."""

    def __init__(self, map_instance):
        self.map = map_instance
        self.mode = None
        self.current_shape = None

    # Modes for setting start, and obstacles
    def set_start_mode(self):
        """Activates start position setting mode."""
        self.mode = 'set_start'
        self.map.map_view.update_message_label(text="Click on the grid to set the start position.") # Access map_view

    def set_obstacles_mode(self):
        """Activates obstacle placement mode."""
        self.mode = 'set_obstacles'
        self.map.map_model.current_points = []  # Clear current obstacle points
        self.map.map_model.current_lines = []  # Clear current obstacle lines
        self.map.map_view.update_message_label(text="Click and drag to draw obstacles. Double-click to finish.")  # Access map_view

    def handle_click(self, event):
        """Handles mouse clicks based on active mode."""
        x, y = event.x, event.y
        if self.mode == 'set_start':
            self.map.map_model.set_start_position((x, y))  # Call set_start_position on the map model
            self.map.map_view.draw_start((x, y))  # Draw the start position on the map view
        elif self.mode == 'set_obstacles':
            if not self.map.map_model.current_shape: # Access map_model
                # Check if the user clicked on an existing obstacle to start dragging
                for obstacle_id, (points, polygon_id, line_ids) in self.map.map_model.obstacles.items(): # Access map_model
                    if self.point_in_polygon(x, y, points):
                        self.map.map_model.dragging_obstacle = polygon_id # Access map_model
                        self.map.map_model.drag_start = (x, y) # Access map_model
                        return
                # Otherwise, start drawing a new obstacle
                self.map.map_model.current_points = [(x, y)] # Access map_model
                self.map.map_model.current_shape = self.map.map_view.create_line((x, y), (x, y), fill="red", width=2) # Access map_view
            else:
                self.map.map_model.current_points.append((x, y)) # Access map_model
                line_id = self.map.map_view.create_line(self.map.map_model.current_points[-2], (x, y), fill="red", width=2) # Access map_view, map_model
                self.map.map_model.current_lines.append(line_id) # Access map_model

    def add_obstacle(self):
        """Adds an obstacle to the map model."""
        if self.map.map_model.current_points:
            points = self.map.map_model.current_points
            polygon_id = self.map.map_view.create_polygon(points, fill="red", outline="black")  # Access map_view
            obstacle_id = f"obstacle_{len(self.map.map_model.obstacles)}"  # Access map_model
            self.map.map_model.add_obstacle(obstacle_id, points, polygon_id, [])  # Call add_obstacle on the map model
            self.map.map_model.current_points = []  # Clear current points
            self.map.map_model.current_shape = None  # Clear current shape
            self.map.map_view.update_message_label(text="Obstacle added.")  # Access map_view

    def handle_drag(self, event):
        """Handles mouse drag to draw or move obstacles."""
        x, y = event.x, event.y
        if self.mode == 'set_obstacles' and self.map.map_model.current_shape: # Access map_model
            # Drawing a new obstacle
            self.map.map_model.current_points.append((x, y)) # Access map_model
            line_id = self.map.map_view.create_line(self.map.map_model.current_points[-2], self.map.map_model.current_points[-1], fill="red", width=2) # Access map_view, map_model
            self.map.map_model.current_lines.append(line_id) # Access map_model
        elif self.map.map_model.dragging_obstacle: # Access map_model
            # Moving an existing obstacle
            dx = x - self.map.map_model.drag_start[0] # Access map_model
            dy = y - self.map.map_model.drag_start[1] # Access map_model
            self.map.map_model.drag_start = (x, y) # Access map_model
            self.map.map_view.move_item(self.map.map_model.dragging_obstacle, dx, dy) # Access map_view, map_model
            # Update the obstacle's points in the dictionary
            for obstacle_id, (points, polygon_id, line_ids) in self.map.map_model.obstacles.items(): # Access map_model
                if polygon_id == self.map.map_model.dragging_obstacle: # Access map_model
                    new_points = [(p[0] + dx, p[1] + dy) for p in points]
                    self.map.map_model.obstacles[obstacle_id] = (new_points, polygon_id, line_ids) # Access map_model
                    break

    def is_shape_closed(self):
        """Checks if the drawn shape is closed."""
        if len(self.map.map_model.current_points) < 3: # Access map_model
            return False
        start = self.map.map_model.current_points[0] # Access map_model
        end = self.map.map_model.current_points[-1] # Access map_model
        # Allow some room for inaccuracy (e.g., 15 pixels)
        return abs(start[0] - end[0]) < 15 and abs(start[1] - end[1]) < 15

    def finalize_shape(self, event=None):
        """Finalizes the drawn shape and adds it as an obstacle."""
        if self.mode == 'set_obstacles' and self.map.map_model.current_shape: # Access map_model
            if self.is_shape_closed():
                # Delete the temporary lines used for drawing
                for line_id in self.map.map_model.current_lines: # Access map_model
                    self.map.map_view.delete_item(line_id) # Access map_view
                self.map.map_model.current_lines = [] # Access map_model

                # Create the filled polygon
                self.add_obstacle()  # Call add_obstacle method
            else:
                self.map.map_view.update_message_label(text="Shape is not closed. Please double-click near the starting point.") # Access map_view

    def delete_obstacle(self, event):
        """Deletes an obstacle when right-clicked."""
        x, y = event.x, event.y
        for obstacle_id, (points, polygon_id, line_ids) in self.map.map_model.obstacles.items(): # Access map_model
            if self.point_in_polygon(x, y, points):
                # Delete the polygon and any associated lines
                self.map.map_view.delete_obstacle_visual(polygon_id, line_ids) # Access map_view
                del self.map.map_model.obstacles[obstacle_id] # Access map_model
                self.map.map_view.update_message_label(text="Obstacle deleted.") # Access map_view
                break

    def point_in_polygon(self, x, y, polygon):
        """Determines if a point is inside a polygon using the ray casting algorithm."""
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

    def stop_drag(self, event):
        """Stops dragging an obstacle."""
        self.map.map_model.dragging_obstacle = None # Access map_model
        self.map.map_model.drag_start = None # Access map_model