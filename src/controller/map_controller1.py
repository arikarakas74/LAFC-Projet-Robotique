from model.map_model import MapModel
from view.map_view import MapView
from utils.geometry import point_in_polygon
import uuid

class MapController:
    """Gère les interactions utilisateur et met à jour le modèle."""

    def __init__(self, map_model: MapModel, map_view: MapView, window):
        self.map_model = map_model
        self.map_view = map_view
        self.window = window
        self.mode = None
        self.current_points = []
        self.temp_lines = []
        self.dragging_obstacle = None
        self.drag_offset = (0, 0)
        self._bind_events()

    def _bind_events(self):
        self.map_view.canvas.bind("<Button-1>", self.handle_click)
        self.map_view.canvas.bind("<B1-Motion>", self.handle_drag)
        self.map_view.canvas.bind("<Double-Button-1>", self.finalize_shape)
        self.map_view.canvas.bind("<Button-3>", self.delete_obstacle)
        self.map_view.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def set_start_mode(self):
        self.mode = "set_start"
        self.map_view.message_label.config(text="Cliquez pour définir la position de départ.")

    def set_obstacles_mode(self):
        self.mode = "set_obstacles"
        self.current_points = []
        self.map_view.message_label.config(text="Cliquez et glissez pour dessiner un obstacle. Double-cliquez pour terminer.")

    def handle_click(self, event):
        x, y = event.x, event.y
        if self.mode == "set_start":
            self.map_model.set_start_position((x, y))
        elif self.mode == "set_obstacles":
            for obstacle_id, points in self.map_model.obstacles.items():
                if point_in_polygon((x, y), points):
                    self.dragging_obstacle = obstacle_id
                    self.drag_offset = (x - points[0][0], y - points[0][1])
                    return
            self.current_points = [(x, y)]
            self.temp_lines.append(self.map_view.create_temp_line((x, y), (x, y)))

    def handle_drag(self, event):
        x, y = event.x, event.y
        if self.mode == "set_obstacles":
            if self.dragging_obstacle:
                obstacle_points = self.map_model.obstacles[self.dragging_obstacle]
                new_points = [(p[0] + (x - self.drag_offset[0]), p[1] + (y - self.drag_offset[1])) for p in obstacle_points]
                self.map_model.move_obstacle(self.dragging_obstacle, new_points)
            elif self.current_points:
                self.current_points.append((x, y))
                self.temp_lines.append(self.map_view.create_temp_line(self.current_points[-2], (x, y)))

    def finalize_shape(self, event):
        if self.mode == "set_obstacles" and self.current_points:
            if len(self.current_points) >= 3 and self._is_shape_closed():
                obstacle_id = f"obstacle_{uuid.uuid4()}"
                self.map_model.add_obstacle(obstacle_id, self.current_points)
                self.map_view.clear_temp_lines()
                self.current_points = []
                self.temp_lines = []
            else:
                self.map_view.message_label.config(text="Forme non fermée !")
                self.map_view.clear_temp_lines()

    def _is_shape_closed(self):
        start = self.current_points[0]
        end = self.current_points[-1]
        return abs(start[0] - end[0]) < 15 and abs(start[1] - end[1]) < 15

    def delete_obstacle(self, event):
        x, y = event.x, event.y
        for obstacle_id, points in self.map_model.obstacles.items():
            if point_in_polygon((x, y), points):
                self.map_model.remove_obstacle(obstacle_id)
                break

    def stop_drag(self, event):
        self.dragging_obstacle = None
        self.drag_offset = (0, 0)