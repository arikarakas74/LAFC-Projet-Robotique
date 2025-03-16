import time
import math
from controller.simulation_controller import SimulationController
from model.map_model import MapModel
from model.robot import RobotModel

class HeadlessSimulation:
    """Class for running the simulation in CLI mode (without a GUI)."""
    def __init__(self):
        self.map_model = MapModel()
        
        # Set default starting position
        self.map_model.set_start_position((400, 300))
        
        # Create sample 3D obstacle
        self.map_model.add_obstacle_3d(
            "cube1", 
            (100, 100, 0),   # min point
            (150, 150, 50),  # max point
        )
        
        self.robot_model = RobotModel(self.map_model)
        
        # By default, RobotController in SimulationController will launch its CLI input thread.
        self.sim_controller = SimulationController(self.map_model, self.robot_model, True)
        
        # Add state listener to print robot state
        self.sim_controller.add_state_listener(self.print_state)
    
    def print_state(self, state):
        """Print the robot state to the console."""
        # 3D state
        print(f"Position: ({state['x']:.1f}, {state['y']:.1f}, {state['z']:.1f}) | "
              f"Orientation: Pitch={math.degrees(state['pitch']):.1f}° "
              f"Yaw={math.degrees(state['yaw']):.1f}° "
              f"Roll={math.degrees(state['roll']):.1f}° | "
              f"Speeds: L={state['left_speed']}°/s R={state['right_speed']}°/s")
    
    def run(self):
        """Run the simulation in CLI mode."""
        print("Starting simulation (Ctrl+C to stop)")
        print("Use these keys to control the robot:")
        print("  w/s: Move forward/backward")
        print("  q/a: Increase/decrease left wheel speed")
        print("  e/d: Increase/decrease right wheel speed")
        print("  r/f: Move up/down (3D only)")
        print("  up/down/left/right arrows: Rotate in 3D (pitch/roll)")
        print("  Ctrl+C: Stop simulation")
        
        self.sim_controller.run_simulation()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.sim_controller.stop_simulation()
            print("\nSimulation stopped")

def run_cli():
    """Run the simulation in CLI mode."""
    sim = HeadlessSimulation()
    sim.run()

if __name__ == "__main__":
    run_cli()
