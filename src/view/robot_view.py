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
        x = state['x']
        y = state['y']
        angle = state['angle']
        pen_down = state.get('pen_down', False)
        pen_color = state.get('pen_color', 'blue') # Get pen color, default blue

        self.canvas.delete("robot") # Remove previous robot representation

        # Draw path segment only if pen is down and we have a previous position
        if pen_down and self.last_x is not None and self.last_y is not None:
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=pen_color, tags="path")
        elif not pen_down:
             # If pen is up, ensure we don't draw a connecting line on the next step
             self.last_x = None
             self.last_y = None

        # Only update last position if the pen is down, otherwise path segments will jump
        if pen_down:
            self.last_x = x
            self.last_y = y

        size = 30
        front = (x + size * math.cos(angle),y + size * math.sin(angle))
        left = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(angle + math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(angle + math.pi / 2))
        right = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(angle - math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(angle - math.pi / 2))
        
        self.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def _update_labels(self, state):
        angle_deg = math.degrees(state['angle'])
        text = f"Left: {state['left_speed']:.1f}°/s | Right: {state['right_speed']:.1f}°/s | Angle: {angle_deg:.2f}°"
        self.speed_label.config(text=text)

    def clear_robot(self):
        """Clears the robot and its path from the canvas."""
        self.canvas.delete("robot")
        self.canvas.delete("path") # Also delete path lines
        self.last_x = None
        self.last_y = None
        self.speed_label.config(text="")
