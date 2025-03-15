import tkinter as tk
from tkinter import ttk
from controller.map_controller import MapController
from view.robot_view import RobotView
from view.robot_view_3d import RobotView3D
from view.map_view import MapView
from view.control_panel import ControlPanel
from model.map_model import MapModel
from model.robot import RobotModel
from controller.simulation_controller import SimulationController

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Simulation MVC - 3D")
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
        
        # Set default starting position
        self.map_model.set_start_position((400, 300))
        
        # Create a 3D obstacle for testing
        self.map_model.add_obstacle_3d(
            "cube1", 
            (100, 100, 0),   # min point
            (150, 150, 50),  # max point
        )
        
        # Pass cli_mode=False to avoid launching the CLI input thread.
        self.sim_controller = SimulationController(self.map_model, self.robot_model, False)
        
        # Setting 3D mode to enabled
        self.sim_controller.toggle_3d_mode(True)

        # Create the views - use the 3D view by default
        self.use_3d_view = True
        self.map_controller = None  # Initialize to None
        
        if self.use_3d_view:
            # Create 3D view
            self.robot_view = RobotView3D(canvas_frame, self.sim_controller)
            # In 3D mode we don't need a separate map view or map controller
            self.map_view = None
        else:
            # Create 2D views for backward compatibility
            self.robot_view = RobotView(canvas_frame, self.sim_controller)
            self.robot_view.canvas.pack(fill="both", expand=True)
            self.map_view = MapView(
                parent=canvas_frame,
                robot_view=self.robot_view
            )
            # Create the map controller (only in 2D mode)
            self.map_controller = MapController(self.map_model, self.map_view, self)

        # Create a sub-frame to center the control panel
        inner_frame = ttk.Frame(controls_frame)
        inner_frame.pack(anchor='center')

        # Control panel for simulation commands (start, reset, etc.)
        self.control_panel = ControlPanel(inner_frame, self.map_controller, self.sim_controller)
        self.control_panel.control_frame.pack(pady=5)

        # Create view toggle button
        self.view_toggle_button = ttk.Button(
            inner_frame,
            text="Toggle Follow Mode" if self.use_3d_view else "Switch to 3D View",
            command=self.toggle_view
        )
        self.view_toggle_button.pack(pady=5)

        # Bind keyboard events for the 3D view mode
        self._bind_3d_keys()

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Toggle View", command=self.toggle_view)
        file_menu.add_command(label="Reset", command=self.reset_simulation)
        file_menu.add_command(label="Quit", command=self.quit)

    def toggle_view(self):
        """Toggle between follow mode and free camera mode in 3D view."""
        if self.use_3d_view and hasattr(self.robot_view, 'toggle_follow_mode'):
            self.robot_view.toggle_follow_mode()
            
    def reset_simulation(self):
        """Reset the simulation."""
        # Stop the simulation
        self.sim_controller.stop_simulation()
        
        # Reset all wheel speeds to 0 by updating the robot model directly
        self.robot_model.left_speed = 0
        self.robot_model.right_speed = 0
        
        # Reset 3D orientation if present
        if hasattr(self.robot_model, 'pitch'):
            self.robot_model.pitch = 0
        if hasattr(self.robot_model, 'roll'):
            self.robot_model.roll = 0
            
        # Clear robot view if needed
        if hasattr(self.robot_view, 'clear_robot'):
            self.robot_view.clear_robot()
            
        # Restart the simulation
        self.sim_controller.run_simulation()

    def _bind_3d_keys(self):
        """Bind keyboard events for 3D robot control."""
        # WASD for basic movement
        self.bind("<w>", lambda event: self.sim_controller.robot_controller.move_forward())
        self.bind("<s>", lambda event: self.sim_controller.robot_controller.move_backward())
        self.bind("<a>", lambda event: self.sim_controller.robot_controller.decrease_right_speed())
        self.bind("<d>", lambda event: self.sim_controller.robot_controller.increase_right_speed())
        
        # QE for left wheel control
        self.bind("<q>", lambda event: self.sim_controller.robot_controller.increase_left_speed())
        self.bind("<e>", lambda event: self.sim_controller.robot_controller.decrease_left_speed())
        
        # RF for up/down in 3D
        self.bind("<r>", lambda event: self.sim_controller.robot_controller.move_up())
        self.bind("<f>", lambda event: self.sim_controller.robot_controller.move_down())
        
        # Arrow keys for 3D rotation
        self.bind("<Up>", lambda event: self.sim_controller.robot_controller.pitch_up())
        self.bind("<Down>", lambda event: self.sim_controller.robot_controller.pitch_down())
        self.bind("<Left>", lambda event: self.sim_controller.robot_controller.roll_left())
        self.bind("<Right>", lambda event: self.sim_controller.robot_controller.roll_right())
        
        # Add a key for toggling follow mode (using F1)
        self.bind("<F1>", lambda event: self.toggle_view())

def run_gui():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
