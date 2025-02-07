import tkinter as tk
from model.map_model import MapModel
from view.map_view import MapView
from view.control_panel import ControlPanel
from controller.map_controller import MapController
from controller.simulation_controller import SimulationController

class Map: # Main Map class to orchestrate MVC components
    def __init__(self, rows, cols, grid_size=30):
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.window = tk.Tk()
        self.window.title("Robot Simulator")

        self.map_model = MapModel(rows, cols)
        self.map_view = MapView(self, rows, cols, grid_size)
        self.map_controller = MapController(self)
        self.simulation_controller = SimulationController(self)
        self.control_panel = ControlPanel(self, self.map_controller, self.simulation_controller)

        self.robot = None # Robot instance is managed by simulation controller

        # Bind events - these should mostly call controller methods
        self.map_view.canvas.bind("<Button-1>", self.map_controller.handle_click)
        self.map_view.canvas.bind("<B1-Motion>", self.map_controller.handle_drag)
        self.map_view.canvas.bind("<Double-Button-1>", self.map_controller.finalize_shape)
        self.map_view.canvas.bind("<Button-3>", self.map_controller.delete_obstacle)
        self.map_view.canvas.bind("<ButtonRelease-1>", self.map_controller.stop_drag)

        self.window.bind("<w>", lambda event: self.robot.move_forward() if self.robot else None)
        self.window.bind("<s>", lambda event: self.robot.move_backward()if self.robot else None)
        self.window.bind("<KeyRelease-w>", lambda event: self.robot.stop_acceleration()if self.robot else None)
        self.window.bind("<KeyRelease-s>", lambda event: self.robot.stop_acceleration()if self.robot else None)
        self.window.bind("<a>", lambda event: self.robot.turn_left()if self.robot else None)
        self.window.bind("<d>", lambda event: self.robot.turn_right()if self.robot else None)
        self.window.bind("<Up>", lambda event: self.robot.move_forward()if self.robot else None)
        self.window.bind("<Down>", lambda event: self.robot.move_backward()if self.robot else None)
        self.window.bind("<Left>", lambda event: self.robot.turn_left()if self.robot else None)
        self.window.bind("<Right>", lambda event: self.robot.turn_right()if self.robot else None)
        self.window.bind("<KeyRelease-Up>", lambda event: self.robot.stop_acceleration()if self.robot else None)
        self.window.bind("<KeyRelease-Down>", lambda event: self.robot.stop_acceleration()if self.robot else None)


if __name__ == "__main__":
    map_instance = Map(30, 30)
    map_instance.window.mainloop()