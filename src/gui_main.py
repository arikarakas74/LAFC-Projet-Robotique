import tkinter as tk
from tkinter import ttk

from src.controller.map_controller import MapController
from src.view.robot_view import RobotView
from src.view.map_view import MapView
from src.view.control_panel import ControlPanel
from src.model.map_model import MapModel
from src.model.robot import RobotModel
from src.controller.simulation_controller import SimulationController

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
        self.robot_view = RobotView(canvas_frame, self.sim_controller)
        self.map_view = MapView(
            parent=canvas_frame,
            robot_view=self.robot_view
        )
        self.robot_view.canvas.pack(fill="both", expand=True)

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
