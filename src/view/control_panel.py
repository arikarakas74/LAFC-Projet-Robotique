import tkinter as tk

class ControlPanel:
    def __init__(self, root, controller):
        self.controller = controller
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.start_button = tk.Button(self.frame, text="Start", command=self.controller.start_simulation)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.frame, text="Stop", command=self.controller.stop_simulation)
        self.stop_button.pack(side=tk.LEFT)
