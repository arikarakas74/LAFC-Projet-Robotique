from vpython import *
import threading
import time
import math

class VpythonView:
    def __init__(self, simulation_controller):
        """ 初始化 3D 视图 """
        self.simulation_controller = simulation_controller

        # 创建 3D 场景
        self.scene = canvas(title="3D Robot Simulation", width=800, height=600)
        self.scene.center = vector(0, 0, 0)
        self.scene.background = color.white
        self.scene.forward = vector(0, -1, -1)  # 调整视角角度

        # 创建 地面
        self.floor = box(pos=vector(0, 0, 0), size=vector(400, 1, 300), color=color.green)

        # 创建 机器人主体
        self.robot_body = cylinder(pos=vector(0, 5, 0), axis=vector(0, 10, 0), radius=10, color=color.blue)

        # 机器人轮子
        self.wheel_left = cylinder(pos=vector(-10, 3, 0), axis=vector(0, 6, 0), radius=3, color=color.black)
        self.wheel_right = cylinder(pos=vector(10, 3, 0), axis=vector(0, 6, 0), radius=3, color=color.black)

        # 监听机器人状态
        self.simulation_controller.add_state_listener(self.update_robot)

        # 启动渲染线程
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def update_robot(self, state):
        """更新机器人在3D场景中的位置"""
        x, y = state['x'], state['y']
        angle = state['angle']  # 弧度制

        # 更新 机器人位置
        self.robot_body.pos = vector(x, 5, y)
        
        # 旋转机器人
        self.robot_body.axis = vector(10 * math.cos(angle), 0, 10 * math.sin(angle))

        # 轮子跟随旋转
        self.wheel_left.pos = vector(x - 10 * math.sin(angle), 3, y + 10 * math.cos(angle))
        self.wheel_right.pos = vector(x + 10 * math.sin(angle), 3, y - 10 * math.cos(angle))

    def run(self):
        """ 持续刷新 3D 画面 """
        while self.running:
            rate(50)  # 50 FPS

    def stop(self):
        """ 停止 3D 视图更新 """
        self.running = False
