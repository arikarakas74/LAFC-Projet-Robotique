import argparse
from view.app_view import AppView
from controller.simulation_controller import SimulationController
from model.map_model import MapModel
from model.robot import Robot

def run_cli():
    """Lancer le mode CLI"""
    print("Starting Robot Simulation in CLI mode...")

    #Initialiser le modèle de carte
    map_model = MapModel(20, 20)

    # Demander à l'utilisateur d'entrer les coordonnées du point de départ
    while True:
        try:
            x = int(input("Enter start position X (0-800): "))
            y = int(input("Enter start position Y (0-600): "))
            
            # Vérifier si l'entrée est dans les limites de la carte
            if 0 <= x <= 800 and 0 <= y <= 600:
                map_model.start_position = (x, y)
                break
            else:
                print("Error: Coordinates out of bounds. Please enter values within (0-800, 0-600).")
        except ValueError:
            print("Error: Invalid input. Please enter integer values.")

    print(f"Start position set to: ({x}, {y})")

    # creater robot
    robot = Robot(map_model)

    # Exécuter la simulation
    sim_controller = SimulationController(None, map_model, None, None, cli_mode=True)
    sim_controller.run_simulation_cli(robot)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot Simulator")
    parser.add_argument("--gui", action="store_true", help="Run with graphical interface")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")

    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        app = AppView(20, 20)
        app.run()
