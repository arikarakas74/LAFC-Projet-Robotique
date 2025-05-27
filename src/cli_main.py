#!/usr/bin/env python3
import time
import math
from robot.robot import MockRobot2IN013            # ← bibliothèque matérielle
from controller.adapter import RealRobotAdapter
from controller.StrategyAsync import PolygonStrategy

def run_cli():
    # 1) Création de l’objet matériel
    gpg3 = MockRobot2IN013()                         # ou EasyGoPiGo() selon votre version

    # 2) Wrapper hardware → adapter
    robot_adapter = RealRobotAdapter(gpg3)

    # 3) Instanciation de la stratégie « carré »
    square = PolygonStrategy(
        n=4,
        adapter=robot_adapter,
        side_length_cm=50,        # longueur du côté en cm
        vitesse_avance=200,       # vitesse en dps
        vitesse_rotation=100      # vitesse de rotation en dps
    )
    square.start()

    # 4) Boucle d’exécution CLI sur le vrai robot
    dt = 0.02  # 20 ms entre chaque step()
    try:
        while not square.is_finished():
            square.step(dt)
            time.sleep(dt)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel, stoppage immédiat.")
    finally:
        # 5) Assurez-vous d’arrêter les moteurs
        robot_adapter.robot.set_motor_dps("MOTOR_LEFT",  0)
        robot_adapter.robot.set_motor_dps("MOTOR_RIGHT", 0)
        print("✅ Moteurs coupés, fin du programme.")

if __name__ == "__main__":
    run_cli()
