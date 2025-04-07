import math
import tkinter as tk
from tkinter import ttk

class RobotView:
    def __init__(self, parent, sim_controller):

        self.parent = parent
        self.canvas = tk.Canvas(parent, width=800, height=600)
        self.canvas.pack()
        
        self.speed_label = tk.Label(parent)
        self.speed_label.pack()
        self.WHEEL_BASE_WIDTH = sim_controller.robot_model.WHEEL_BASE_WIDTH
        sim_controller.add_state_listener(self.update_display)
        self.last_x = None
        self.last_y = None

    def update_display(self, state):
        self.parent.after(0, self._safe_update, state)

    def _safe_update(self, state):
        self._draw_robot(state)
        self._update_labels(state)

    def _draw_robot(self, state):
        """Dessiner le robot avec self.x et self.y"""
        self.canvas.delete("robot")
        x, y = state['x'], state['y']
        direction_angle = state['angle']

        if self.last_x is not None and self.last_y is not None:
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill="blue", width=2, tags="trace")
        
        self.last_x = x
        self.last_y = y
        
        size = 30
        front = (x + size * math.cos(direction_angle),y + size * math.sin(direction_angle))
        left = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_angle + math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_angle + math.pi / 2))
        right = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_angle - math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_angle - math.pi / 2))
        
        self.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def _update_labels(self, state):
        angle_deg = math.degrees(state['angle'])
        text = f"Left: {state['left_speed']:.1f}°/s | Right: {state['right_speed']:.1f}°/s | Angle: {angle_deg:.2f}°"
        self.speed_label.config(text=text)

    def clear_robot(self):
        """Clears the robot from the canvas."""
        self.canvas.delete("robot")
        self.canvas.delete("trace")
        self.last_x = None
        self.last_y = None

        if self.speed_label:
            self.speed_label.config(text="")
