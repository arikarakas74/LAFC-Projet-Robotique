import tkinter as tk
from model.robot import Robot
from model.simulator import RobotSimulator

class MapView:
    """Affichage de la carte et interaction utilisateur."""

    def __init__(self, root, map_model):
        self.map_model = map_model
        self.canvas = tk.Canvas(root, width=map_model.width, height=map_model.height, bg="white")
        self.canvas.pack()
        self.robot = None
        self.simulator = None

        # Boutons
        self.set_start_button = tk.Button(root, text="Set Start Position", command=self.set_start_position)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = tk.Button(root, text="Run Simulation", command=self.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_map)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.message_label = tk.Label(root, text="")
        self.message_label.pack(pady=10)
        self.canvas.bind("<Button-1>", self.add_obstacle)

        self.clear_obstacles_button = tk.Button(root, text="Clear Obstacles", command=self.clear_obstacles)
        self.clear_obstacles_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.distance_label = tk.Label(root, text="Distance : -- cm")
        self.distance_label.pack(pady=5)

        # Dessiner la grille au démarrage
        self.draw_grid()

        # Lier les touches du clavier
        self.bind_keys()

    def draw_grid(self):
        """Dessine une grille pour la carte."""
        grid_size = 50  # Taille des cases
        for i in range(0, self.map_model.width, grid_size):
            self.canvas.create_line(i, 0, i, self.map_model.height, fill="gray")
        for j in range(0, self.map_model.height, grid_size):
            self.canvas.create_line(0, j, self.map_model.width, j, fill="gray")

    def set_start_position(self):
        """Définit la position initiale du robot."""
        self.map_model.set_start_position(50, 50)  # Par défaut en haut à gauche
        self.robot = Robot(self.map_model.start_position, self.map_model)  # Créer le robot
        self.draw_robot()
        self.message_label.config(text="🚀 Position de départ définie !", fg="green")

    def bind_keys(self):
        """Lie les touches du clavier aux mouvements du robot."""
        print("🔄 Clavier lié avec succès !")  # DEBUG : Vérifier si la méthode est appelée
        self.canvas.bind_all("<Up>", lambda event: self.move_robot("up"))
        self.canvas.bind_all("<Down>", lambda event: self.move_robot("down"))
        self.canvas.bind_all("<Left>", lambda event: self.move_robot("left"))
        self.canvas.bind_all("<Right>", lambda event: self.move_robot("right"))

        self.canvas.bind_all("<z>", lambda event: self.move_robot("up"))
        self.canvas.bind_all("<s>", lambda event: self.move_robot("down"))
        self.canvas.bind_all("<q>", lambda event: self.move_robot("left"))
        self.canvas.bind_all("<d>", lambda event: self.move_robot("right"))



    def draw_robot(self):
        """Dessine le robot sur la carte à sa nouvelle position."""
        self.canvas.delete("robot")  # Supprime l'ancien dessin
        if self.robot:
            x, y = self.robot.x, self.robot.y
            print(f"🚀 Nouvelle position : ({x}, {y})")  # DEBUG : Vérifier si les coordonnées changent
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="blue", tags="robot")
            self.canvas.update()  # Force la mise à jour de l'affichage

    def reset_map(self):
        """Réinitialise la carte et le robot."""
        self.canvas.delete("all")
        self.map_model.obstacles.clear()
        self.map_model.start_position = None
        self.robot = None
        self.simulator = None
        self.draw_grid()
        self.message_label.config(text="🗺️ Carte réinitialisée.", fg="black")
    def run_simulation(self):
        """Prépare la simulation en mode manuel (le robot ne bouge pas automatiquement)."""
        if self.map_model.start_position is None:
            self.message_label.config(text="⚠️ Définissez une position de départ avant de lancer la simulation.", fg="red")
            return

        self.robot = Robot(self.map_model.start_position, self.map_model)
        self.message_label.config(text="Simulation prête ! Déplacez le robot avec ZQSD ou Flèches.", fg="blue")
    def add_obstacle(self, event):
        """Ajoute un obstacle à l'endroit où l'utilisateur clique."""
        grid_size = 50  # Taille de chaque case de la grille
        x = (event.x // grid_size) * grid_size
        y = (event.y // grid_size) * grid_size

        if not self.map_model.is_obstacle(x, y):
            self.map_model.add_obstacle(x, y)
            self.canvas.create_rectangle(x, y, x + grid_size, y + grid_size, fill="black", tags="obstacle")
    def move_robot(self, direction):
        """Déplace le robot en fonction de la touche pressée, en évitant les obstacles."""
        if self.robot:
            new_x, new_y = self.robot.x, self.robot.y

            if direction == "up":
                new_y -= 10
            elif direction == "down":
                new_y += 10
            elif direction == "left":
                new_x -= 10
            elif direction == "right":
                new_x += 10

            # Vérification des obstacles
            if not self.map_model.is_obstacle(new_x, new_y):
                self.robot.x, self.robot.y = new_x, new_y
                self.draw_robot()
            else:
                print("🚧 Mouvement bloqué ! Un obstacle est présent.")
      

    def clear_obstacles(self):
        """Supprime tous les obstacles."""
        self.map_model.obstacles.clear()
        self.canvas.delete("obstacle")
        print("🗑️ Tous les obstacles ont été supprimés.")


