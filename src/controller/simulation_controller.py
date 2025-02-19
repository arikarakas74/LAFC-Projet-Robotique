from model.robot import Robot  # Adjusted the import path
from view.control_panel import ControlPanel
from controller.map_controller import MapController  # Import MapController
from controller.robot_controller import RobotController  # Import RobotController
from model.map_model import MapModel
from view.robot_view import RobotView
import time
import threading
from model.robot import Robot
from model.clock import Clock

class SimulationController:
    """Handles the simulation flow and interactions between model and view."""

    def __init__(self, map_instance, map_model, robot_view, control_panel=None,cli_mode=False):
        self.map_model = map_model
        self.robot_view = robot_view
        self.simulation_running = False
        self.robot = None

        if not cli_mode:  
            self.map = map_instance
            self.map_controller = MapController(self.map.map_model, self.map.map_view, self.map.window)
            self.robot_controller = None

        self.control_panel = control_panel  # Use the provided control_panel
        self.cli_mode = cli_mode
    
    def update_view(self):
        pass 

    def run_simulation_cli(self, robot):
        """Mode CLI pour exécuter la simulation et mettre à jour la position après chaque mouvement"""
        self.robot = robot
        self.simulation_running = True

        print("Simulation started in CLI mode.")
        print("Use 'w' to move forward, 's' to move backward, 'a' to turn left, 'd' to turn right, 'q' to quit.")

        last_time = time.time()

        while self.simulation_running:
            command = input("Enter command: ").strip().lower()
            
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            if command == 'w':
                self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 50)
                self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 50)
            elif command == 's':
                self.robot.set_motor_dps(self.robot.MOTOR_LEFT, -50)
                self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, -50)
            elif command == 'a':
                self.robot.set_motor_dps(self.robot.MOTOR_LEFT, -30)
                self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, 30)
            elif command == 'd':
                self.robot.set_motor_dps(self.robot.MOTOR_LEFT, 30)
                self.robot.set_motor_dps(self.robot.MOTOR_RIGHT, -30)
            elif command == 'q':
                print("Stopping simulation.")
                self.simulation_running = False
                break
            else:
                print("Invalid command! Use w/s/a/d/q.")
                continue  
            
            self.robot.move_motors(delta_time)
            print(f" Robot Position: x={self.robot.x:.2f}, y={self.robot.y:.2f}, angle={self.robot.direction_angle:.2f}°")

    
    def run_simulation(self):
        """Starts the robot simulation."""
        if self.map_model.start_position:
            print("Simulation started")
            start_x, start_y = self.map_model.start_position
            self.robot_view.x = start_x
            self.robot_view.y = start_y
        if self.simulation_running:
            self.map.map_view.update_message_label(text="Simulation already running.") # Access map_view
            return

        if not self.map.map_model.start_position: # Access map_model
            self.map.map_view.update_message_label(text="Please set the start position.") # Access map_view
            return

        self.map.robot = Robot(self.map.map_model)  # Create robot instance with map dimensions
        self.update_view()
        self.map.robot.add_event_listener(lambda event, **kwargs: self.update_view())
        self.map.robot.start_movement()
        self.map.map_view.create_speed_label()  # Create speed label in the view
        self.control_panel.set_speed_label(self.map.map_view.speed_label)  # Set the speed label to control panel
        self.robot_controller = RobotController(self.map.robot, self.map.map_view.robot_view, self.control_panel, self.map.window,self.map_model)  # Pass window to RobotController
        self.map.map_view.update_message_label(text="Use W/S to move forward/backward and A/D to turn left/right.") # Access map_view
        self.simulation_running = True

    def reset_map(self, include_robot=False):

        self.simulation_running = False
        self.map.map_view.delete_all()  # Access map_view
        self.map.map_model.reset()  # Access map_model
        self.map.map_view.update_message_label(text="Map reset.")  # Access map_view
        if self.map.map_view.speed_label:
            self.map.map_view.speed_label.destroy()
            self.map.map_view.speed_label = None
        self.map.window.update()

        self.map.map_view.robot_view.clear_robot()  # Clear the robot from the canvas

        if include_robot:
            self.reset_robot()

    def reset_robot(self):
        """Resets the robot to its initial state."""
        if self.map.robot:
            self.map.robot.stop_simulation()
            self.map.robot = None

        if self.robot_controller:
            self.robot_controller.cleanup()
            self.robot_controller = None

        self.map.map_view.robot_view.clear_robot()
        self.map.map_view.canvas.delete("robot")

    def draw_square(self):
        """Starts the robot drawing a square."""
        if not self.map.robot:
            self.map.map_view.update_message_label(text="Start the simulation first.") # Access map_view
            return
        self.robot_controller.start_draw_square()

    def update_simulation_cli(self, delta_time):
        """Mode CLI met à jour l'émulation"""
        if not self.simulation_running:
            return

        last_x, last_y = self.robot.x, self.robot.y
        self.robot.move_motors(delta_time)

        if (self.robot.x, self.robot.y) != (last_x, last_y):
            print(f"Robot Position: x={self.robot.x:.2f}, y={self.robot.y:.2f}, angle={self.robot.direction_angle:.2f}°")


