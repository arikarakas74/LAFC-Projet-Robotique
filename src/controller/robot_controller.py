import math
import threading


class RobotController:
    SPEED_STEP = 30.0
    def __init__(self, robot_model, map_model, cli_mode=False):
        self.robot_model = robot_model
        self.map_model = map_model

        # Démarrage du thread de saisie uniquement en mode CLI
        if cli_mode:
            self._start_input_thread()

    def _start_input_thread(self):
        threading.Thread(target=self._read_input, daemon=True).start()

    def _read_input(self):
        while True:
            key = input("Press a key (q/a/e/d/w/s): ").strip()
            if key == 'q':
                self.increase_left_speed()
            elif key == 'a':
                self.decrease_left_speed()
            elif key == 'e':
                self.increase_right_speed()
            elif key == 'd':
                self.decrease_right_speed()
            elif key == 'w':
                self.move_forward()
            elif key == 's':
                self.move_backward()

    def stop(self):
        self.robot_model.set_motor_speed("left", 0)
        self.robot_model.set_motor_speed("right", 0)

    def increase_left_speed(self):
        new_speed = self.robot_model.motor_speeds["left"] + self.SPEED_STEP
        self.robot_model.set_motor_speed("left", new_speed)

    def decrease_left_speed(self):
        new_speed = self.robot_model.motor_speeds["left"] - self.SPEED_STEP
        self.robot_model.set_motor_speed("left", new_speed)

    def increase_right_speed(self):
        new_speed = self.robot_model.motor_speeds["right"] + self.SPEED_STEP
        self.robot_model.set_motor_speed("right", new_speed)

    def decrease_right_speed(self):
        new_speed = self.robot_model.motor_speeds["right"] - self.SPEED_STEP
        self.robot_model.set_motor_speed("right", new_speed)

    def move_forward(self):
        self.robot_model.set_motor_speed("left", self.robot_model.motor_speeds["left"] + self.SPEED_STEP)
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] + self.SPEED_STEP)

    def move_backward(self):
        self.robot_model.set_motor_speed("left", self.robot_model.motor_speeds["left"] - self.SPEED_STEP)
        self.robot_model.set_motor_speed("right", self.robot_model.motor_speeds["right"] - self.SPEED_STEP)
    def strategie(self):
            self.robot_model.x = 0 
            self.robot_model.y = 600
            for i in range(10):
                self.move_forward()
