import tkinter as tk
from tkinter import ttk
from controller.map_controller import MapController
from view.robot_view import RobotView
from view.map_view import MapView
from view.control_panel import ControlPanel
from model.map_model import MapModel
from model.robot import RobotModel
from controller.simulation_controller import SimulationController
import threading
import math
import time

#Exercice1
class Exercice1:
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

        self.dessine = True

        self.canvas.create_rectangle(395,295,405,305,fill='blue')
        self.canvas.create_rectangle(395,590,405,600,fill='green')
        self.canvas.create_rectangle(395,0,405,10,fill='red')

    def update_display(self, state):
        self.parent.after(0, self._safe_update, state)

    def _safe_update(self, state):
        self._draw_robot(state)

    def _draw_robot(self, state):
        """Dessiner le robot avec self.x et self.y"""
        self.canvas.delete("robot")
        x, y = state['x'], state['y']
        direction_angle = state['angle']

        if self.last_x is not None and self.last_y is not None and self.dessine==True:
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill="blue", width=2, tags="trace")
        
        self.last_x = x
        self.last_y = y
        
        size = 30
        front = (x + size * math.cos(direction_angle),y + size * math.sin(direction_angle))
        left = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_angle + math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_angle + math.pi / 2))
        right = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_angle - math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_angle - math.pi / 2))
        
        self.canvas.create_polygon(front, left, right, fill="blue", tags="robot")

    def q13(self, state):
        self.dessine = False

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Simulation MVC")
        self._create_menu()

        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Canvas frame (for drawing)
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side="top", fill="both", expand=True)

        # Controls frame
        controls_frame = ttk.Frame(main_frame, padding=10)
        controls_frame.pack(side="bottom", fill="x")

        # Initialize models and simulation controller
        self.map_model = MapModel()
        self.robot_model = RobotModel(self.map_model)
        # Pass cli_mode=False to avoid launching the CLI input thread.
        self.sim_controller = SimulationController(self.map_model, self.robot_model, False)

        # Create the views
        self.ex1 = Exercice1(canvas_frame, self.sim_controller)
        self.map_view = MapView(
            parent=canvas_frame,
            robot_view=self.ex1
        )
        self.ex1.canvas.pack(fill="both", expand=True)


        # Create the map controller
        self.map_controller = MapController(self.map_model, self.map_view, self)

        # Create a sub-frame to center the control panel
        inner_frame = ttk.Frame(controls_frame)
        inner_frame.pack(anchor='center')

        # Control panel for simulation commands (start, reset, etc.)
        self.control_panel = ControlPanel(inner_frame, self.map_controller, self.sim_controller)
        self.control_panel.control_frame.pack(pady=5)

        # Optionally add a listener to update GUI elements in real time
        self.sim_controller.add_state_listener(self.on_state_update)

        # Bind keyboard events to robot control actions
        self.bind("<q>", lambda event: self.sim_controller.robot_controller.increase_left_speed())
        self.bind("<a>", lambda event: self.sim_controller.robot_controller.decrease_left_speed())
        self.bind("<e>", lambda event: self.sim_controller.robot_controller.increase_right_speed())
        self.bind("<d>", lambda event: self.sim_controller.robot_controller.decrease_right_speed())
        self.bind("<w>", lambda event: self.sim_controller.robot_controller.move_forward())
        self.bind("<s>", lambda event: self.sim_controller.robot_controller.move_backward())

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Quit", command=self.quit)

    def on_state_update(self, state):
        # Update GUI components based on simulation state, if needed.
        pass

def run_gui():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
