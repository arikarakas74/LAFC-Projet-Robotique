import tkinter as tk
from tkinter import ttk
from controller.map_controller import MapController
from view.robot_view import RobotView
from view.map_view import MapView
from view.control_panel import ControlPanel
from model.map_model import MapModel
from model.robot import RobotModel
from controller.simulation_controller import SimulationController

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
        # --- Set start position for q1.1 ---
        # Assuming canvas size around 800x600, place near bottom-left
        mouse_start_pos = (50, 50)
        cat_start_pos = (100, 100) # Different start for the cat
        self.map_model.set_start_position(mouse_start_pos) # Keep original start for compatibility?

        # Create multiple robot models
        self.mouse_model = RobotModel(self.map_model, mouse_start_pos, name="mouse", initial_color="blue")
        self.cat_model = RobotModel(self.map_model, cat_start_pos, name="cat", initial_color="red")
        self.robot_models = [self.mouse_model, self.cat_model]

        # Pass the LIST of models to SimulationController
        self.sim_controller = SimulationController(self.map_model, self.robot_models, False)

        # Create the views (RobotView now handles multiple robots)
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
        
        # --- Give SimulationController a reference to ControlPanel ---
        self.sim_controller.set_control_panel(self.control_panel)
        # --- End reference passing ---

        # Bind keyboard events to robot control actions (Now targets the first robot - mouse)
        # Consider adding keys for the second robot (cat) if needed
        mouse_controller = self.sim_controller.get_robot_controller(0)
        if mouse_controller:
            self.bind("<q>", lambda event: mouse_controller.increase_left_speed())
            self.bind("<a>", lambda event: mouse_controller.decrease_left_speed())
            self.bind("<e>", lambda event: mouse_controller.increase_right_speed())
            self.bind("<d>", lambda event: mouse_controller.decrease_right_speed())
            self.bind("<w>", lambda event: mouse_controller.move_forward())
            self.bind("<s>", lambda event: mouse_controller.move_backward())
        
        # Example bindings for second robot (cat) - using arrow keys
        cat_controller = self.sim_controller.get_robot_controller(1)
        if cat_controller:
            self.bind("<Left>", lambda event: cat_controller.turn_left())
            self.bind("<Right>", lambda event: cat_controller.turn_right())
            self.bind("<Up>", lambda event: cat_controller.move_forward())
            self.bind("<Down>", lambda event: cat_controller.move_backward())

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
    
    return app

if __name__ == "__main__":
    # run_gui() # Don't run directly when script is main
    app = run_gui()
    app.mainloop() # Start loop only if run as main script
