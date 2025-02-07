import tkinter as tk
from model.map_model import MapModel
from view.map_view import MapView

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simulation Robot")

    map_model = MapModel(600, 600)
    map_view = MapView(root, map_model)

    root.mainloop()
