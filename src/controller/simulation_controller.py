class SimulationController:
    def __init__(self, simulator, map_view):
        self.simulator = simulator
        self.map_view = map_view

    def start_simulation(self):
        self.simulator.start_simulation((9, 9))  # Objectif arbitraire

    def stop_simulation(self):
        self.simulator.stop_simulation()
