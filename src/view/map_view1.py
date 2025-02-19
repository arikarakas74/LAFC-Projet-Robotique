import tkinter as tk
from view.robot_view import RobotView

class MapView:
    """Gère l'affichage graphique de la carte."""

    def __init__(self, parent, rows, cols, grid_size):
        self.parent = parent
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.canvas = tk.Canvas(parent.window, width=cols * grid_size, height=rows * grid_size)
        self.canvas.pack()
        self.obstacle_visuals = {}  # Format: {obstacle_id: (polygon_id, line_ids)}
        self.message_label = tk.Label(parent.window, text="")
        self.message_label.pack(pady=10)
        self.robot_view = RobotView(self)
        self.parent.map_model.add_event_listener(self.on_map_update)
        

    def on_map_update(self, event_type, **kwargs):
        if event_type == "start_position_changed":
            self.draw_start(kwargs["position"])
        elif event_type == "end_position_changed":
            self.draw_end(kwargs["position"])
        elif event_type == "obstacle_added":
            obstacle_id = kwargs["obstacle_id"]
            points = kwargs["points"]
            polygon_id = self.draw_obstacle(points)
            self.obstacle_visuals[obstacle_id] = (polygon_id, [])
        elif event_type == "obstacle_removed":
            obstacle_id = kwargs["obstacle_id"]
            self.delete_obstacle_visual(obstacle_id)
        elif event_type == "obstacle_moved":
            obstacle_id = kwargs["obstacle_id"]
            new_points = kwargs["new_points"]
            self.update_obstacle_visual(obstacle_id, new_points)
        elif event_type == "map_reset":
            self.clear_all()

    def draw_grid(self):
        for i in range(self.rows + 1):
            self.canvas.create_line(0, i * self.grid_size, self.cols * self.grid_size, i * self.grid_size, fill="lightgrey")
        for j in range(self.cols + 1):
            self.canvas.create_line(j * self.grid_size, 0, j * self.grid_size, self.rows * self.grid_size, fill="lightgrey")

    def draw_start(self, position):
        self.canvas.delete("start")
        if position:
            x, y = position
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="yellow", tags="start")

    def draw_end(self, position):
        self.canvas.delete("end")
        if position:
            x, y = position
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="green", tags="end")

    def draw_obstacle(self, points):
        return self.canvas.create_polygon(points, fill="red", outline="black")

    def update_obstacle_visual(self, obstacle_id, new_points):
        if obstacle_id in self.obstacle_visuals:
            old_polygon_id, _ = self.obstacle_visuals[obstacle_id]
            self.canvas.delete(old_polygon_id)
            new_polygon_id = self.draw_obstacle(new_points)
            self.obstacle_visuals[obstacle_id] = (new_polygon_id, [])

    def delete_obstacle_visual(self, obstacle_id):
        if obstacle_id in self.obstacle_visuals:
            polygon_id, _ = self.obstacle_visuals[obstacle_id]
            self.canvas.delete(polygon_id)
            del self.obstacle_visuals[obstacle_id]

    def create_temp_line(self, p1, p2):
        return self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="red", width=2, tags="temp_line")

    def clear_temp_lines(self):
        self.canvas.delete("temp_line")

    def clear_all(self):
        self.canvas.delete("all")
        self.obstacle_visuals.clear()
        self.robot_view.clear_robot()
        self.message_label.config(text="")