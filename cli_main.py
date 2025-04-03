import time
import math
from controller.simulation_controller import SimulationController
from model.map_model import MapModel
from model.robot import RobotModel

class HeadlessSimulation:
    """Class for running the simulation in CLI mode (without a GUI)."""
    def __init__(self):
        self.map_model = MapModel()
        self.robot_model = RobotModel(self.map_model)
        # By default, RobotController in SimulationController will launch its CLI input thread.
        self.sim_controller = SimulationController(self.map_model, self.robot_model, True)
        self.sim_controller.add_state_listener(self.print_state)
    
    def print_state(self, state):
        """Print the robot state to the console."""
        print(f"Position: ({state['x']:.1f}, {state['y']:.1f}) | "
              f"Angle: {math.degrees(state['angle']):.1f}° | "
              f"Speeds: L={state['left_speed']}°/s R={state['right_speed']}°/s")
    
    def run(self):
        """Run the simulation in CLI mode."""
        print("Starting simulation (Ctrl+C to stop)")
        self.sim_controller.run_simulation()
        
        # Example of an automatic command
        self.sim_controller.robot_model.set_motor_speed("left", 0)
        self.sim_controller.robot_model.set_motor_speed("right", 0)
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.sim_controller.stop_simulation()
            print("\nSimulation stopped")

def run_cli():
    simulation = HeadlessSimulation()
    simulation.run()

if __name__ == "__main__":
    run_cli()
