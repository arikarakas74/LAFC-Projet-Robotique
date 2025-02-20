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
        
        sim_controller.add_state_listener(self.update_display)

    def update_display(self, state):
        self.parent.after(0, self._safe_update, state)

    def _safe_update(self, state):
        self._draw_robot(state)
        self._update_labels(state)

    def _draw_robot(self, state):
        """Dessiner le robot avec self.x et self.y"""
        self.canvas.delete("robot")
        size = 15
        x, y = state['x'], state['y']
        angle = state['angle']
        
        front = (
            x + size * math.cos(angle),
            y + size * math.sin(angle)
        )
        left = (
            x + size * math.cos(angle + 2.2),
            y + size * math.sin(angle + 2.2)
        )
        right = (
            x + size * math.cos(angle - 2.2),
            y + size * math.sin(angle - 2.2)
        )
        
        self.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def _update_labels(self, state):
        text = f"Left: {state['left_speed']}°/s | Right: {state['right_speed']}°/s"
        self.speed_label.config(text=text)

    def clear_robot(self):
        """Clears the robot from the canvas."""
        self.canvas.delete("robot")

        if self.speed_label:
            self.speed_label.config(text="")
