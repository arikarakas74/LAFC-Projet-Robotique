import time
import math
import logging
from utils.geometry import normalize_angle

# Interface de commande asynchrone
class AsyncCommande:
    def start(self, robot):
        raise NotImplementedError
    def step(self, robot, delta_time):
        raise NotImplementedError
    def is_finished(self):
        raise NotImplementedError

class Accelerer(AsyncCommande):
    def __init__(self, target_speed, duration):
        self.target_speed = target_speed
        self.duration = duration
        self.elapsed = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Accelerer")
    def start(self, robot):
        self.interval = self.duration / 10.0
        self.started = True
        self.logger.info("Acceleration started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        self.elapsed += delta_time
        fraction = min(self.elapsed / self.duration, 1.0)
        speed = self.target_speed * fraction
        robot.set_motor_speed("left", speed)
        robot.set_motor_speed("right", speed)
        if self.elapsed >= self.duration:
            self.finished = True
            self.logger.info("Acceleration finished.")
        return self.finished
    def is_finished(self):
        return self.finished

class Freiner(AsyncCommande):
    def __init__(self, current_speed, duration):
        self.current_speed = current_speed
        self.duration = duration
        self.elapsed = 0
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Freiner")
    def start(self, robot):
        self.started = True
        self.logger.info("Deceleration started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        self.elapsed += delta_time
        fraction = max(1 - self.elapsed / self.duration, 0)
        speed = self.current_speed * fraction
        robot.set_motor_speed("left", speed)
        robot.set_motor_speed("right", speed)
        if self.elapsed >= self.duration:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Deceleration finished.")
        return self.finished
    def is_finished(self):
        return self.finished

class Avancer(AsyncCommande):
    def __init__(self, distance_cm, vitesse):
        self.distance_cm = distance_cm
        self.vitesse = vitesse
        self.started = False
        self.finished = False
        self.start_x = None
        self.start_y = None
        self.logger = logging.getLogger("strategy.Avancer")
    def start(self, robot):
        self.start_x, self.start_y = robot.x, robot.y
        robot.set_motor_speed("left", self.vitesse)
        robot.set_motor_speed("right", self.vitesse)
        self.started = True
        self.logger.info("Avancer started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        current_distance = math.hypot(robot.x - self.start_x, robot.y - self.start_y)
        if current_distance >= self.distance_cm:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Avancer finished.")
        return self.finished
    def is_finished(self):
        return self.finished

class Tourner(AsyncCommande):
    def __init__(self, angle_rad, vitesse_deg_s):
        self.angle_rad = angle_rad
        self.vitesse_deg_s = vitesse_deg_s
        self.started = False
        self.finished = False
        self.logger = logging.getLogger("strategy.Tourner")
    def start(self, robot):
        self.target_angle = normalize_angle(robot.direction_angle + self.angle_rad)
        self.started = True
        self.logger.info("Tourner started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        tol = math.radians(0.1)
        current_angle = normalize_angle(robot.direction_angle)
        error = normalize_angle(self.target_angle - current_angle)
        if abs(error) < tol:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.finished = True
            self.logger.info("Tourner finished.")
        else:
            Kp = 5.0
            correction_speed = Kp * math.degrees(error)
            correction_speed = max(-self.vitesse_deg_s, min(self.vitesse_deg_s, correction_speed))
            robot.set_motor_speed("left", correction_speed)
            robot.set_motor_speed("right", -correction_speed)
        return self.finished
    def is_finished(self):
        return self.finished

class Arreter(AsyncCommande):
    def __init__(self):
        self.finished = False
        self.started = False
        self.logger = logging.getLogger("strategy.Arreter")
    def start(self, robot):
        robot.set_motor_speed("left", 0)
        robot.set_motor_speed("right", 0)
        self.started = True
        self.finished = True
        self.logger.info("Arreter executed.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        return self.finished
    def is_finished(self):
        return self.finished

class PolygonStrategy(AsyncCommande):
    def __init__(self, n, side_length_cm, vitesse_avance, vitesse_rotation):
        if n < 3:
            raise ValueError("At least 3 sides required.")
        self.logger = logging.getLogger("strategy.PolygonStrategy")
        self.commands = []
        turning_angle = 2 * math.pi / n
        for i in range(n):
            self.commands.append(Avancer(side_length_cm, vitesse_avance))
            self.commands.append(Tourner(turning_angle, vitesse_rotation))
            self.logger.info(f"Side {i+1} added.")
        self.commands.append(Arreter())
        self.current_index = 0
        self.finished = False
    def start(self, robot):
        if self.commands:
            self.commands[0].start(robot)
    def step(self, robot, delta_time):
        if self.current_index < len(self.commands):
            cmd = self.commands[self.current_index]
            if not cmd.is_finished():
                cmd.step(robot, delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commands):
                    self.commands[self.current_index].start(robot)
        else:
            self.finished = True
        return self.finished
    def is_finished(self):
        return self.finished

class FollowMovingBeaconStrategy(AsyncCommande):
    def __init__(self, vitesse_rotation, vitesse_avance, tolerance_distance=5, step_distance=5):
        self.vitesse_rotation = vitesse_rotation  
        self.vitesse_avance = vitesse_avance          
        self.tolerance_distance = tolerance_distance  
        self.step_distance = step_distance            
        self.logger = logging.getLogger("strategy.FollowMovingBeaconStrategy")
        self.started = False
        self.finished = False
    def start(self, robot):
        self.started = True
        self.logger.info("FollowMovingBeacon started.")
    def step(self, robot, delta_time):
        if not self.started:
            self.start(robot)
        end_pos = robot.map_model.end_position  # Beacon position
        if end_pos is None:
            self.logger.error("Beacon position not defined.")
            self.finished = True
            return self.finished
        target_x, target_y = end_pos
        current_x, current_y = robot.x, robot.y
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)
        if distance <= self.tolerance_distance:
            robot.set_motor_speed("left", 0)
            robot.set_motor_speed("right", 0)
            self.logger.info("Beacon reached.")
            self.finished = True
        else:
            target_angle = math.atan2(dy, dx)
            angle_to_turn = normalize_angle(target_angle - robot.direction_angle)
            if abs(math.degrees(angle_to_turn)) > 2:
                turn_cmd = Tourner(angle_to_turn, self.vitesse_rotation)
                turn_cmd.start(robot)
                turn_cmd.step(robot, delta_time)
            else:
                advance_cmd = Avancer(min(self.step_distance, distance), self.vitesse_avance)
                advance_cmd.start(robot)
                advance_cmd.step(robot, delta_time)
        return self.finished
    def is_finished(self):
        return self.finished

class CommandeComposite(AsyncCommande):
    def __init__(self):
        self.commandes = []
        self.current_index = 0
    def ajouter_commande(self, commande):
        self.commandes.append(commande)
    def start(self, robot):
        if self.commandes:
            self.commandes[0].start(robot)
    def step(self, robot, delta_time):
        if self.current_index < len(self.commandes):
            cmd = self.commandes[self.current_index]
            if not cmd.is_finished():
                cmd.step(robot, delta_time)
            if cmd.is_finished():
                self.current_index += 1
                if self.current_index < len(self.commandes):
                    self.commandes[self.current_index].start(robot)
        return self.current_index >= len(self.commandes)
    def is_finished(self):
        return self.current_index >= len(self.commandes)
