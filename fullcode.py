import tkinter as tk
from queue import PriorityQueue

class Map:
    def __init__(self, rows, cols, grid_size=30):

        #initialiser la longueur, la largeur,la taille et le titre de GUI
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.window = tk.Tk()
        self.window.title("Robot Simulator")

        #Créer un Canvas pour dessiner et un Frame pour les contrôles, puis les ajouter à la fenêtre
        self.canvas = tk.Canvas(self.window, width=cols * grid_size, height=rows * grid_size)
        self.canvas.pack()

        self.control_frame = tk.Frame(self.window)
        self.control_frame.pack()

        # Créer plusieurs boutons : définir le point de départ, le point d'arrivée, les obstacles, 
        # exécuter la simulation et réinitialiser la carte, puis les ajouter au cadre de contrôle
        self.set_start_button = tk.Button(self.control_frame, text="Set Start", command=self.set_start_mode)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_end_button = tk.Button(self.control_frame, text="Set End", command=self.set_end_mode)
        self.set_end_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_obstacles_button = tk.Button(self.control_frame, text="Set Obstacles", command=self.set_obstacles_mode)
        self.set_obstacles_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = tk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_map)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_start_button = tk.Button(self.control_frame, text="+", command=self.Enlarge)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_start_button = tk.Button(self.control_frame, text="-", command=self.Shrink)
        self.set_start_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Créer un Label pour afficher des messages
        self.message_label = tk.Label(self.window, text="")
        self.message_label.pack(pady=10)

        # initialiser l'ensemble des obstacles, les positions de départ et d'arrivée, ainsi que la variable de mode
        self.obstacles = set()
        self.start_position = None
        self.end_position = None
        self.mode = None  # Modes: 'set_start', 'set_end', 'set_obstacles', None

        # Associer l'événement de clic gauche de la souris à la méthode handle_click
        self.canvas.bind("<Button-1>", self.handle_click)

    def draw_grid(self):
        # Dessiner la grille en initialisant toutes les cellules en blanc
        for i in range(self.rows):
            for j in range(self.cols):
                self.draw_tile((i, j), "white")

    def draw_tile(self, position, color):
        # Dessiner une cellule de la grille avec la position et la couleur spécifiées
        x, y = position
        x1 = y * self.grid_size
        y1 = x * self.grid_size
        x2 = x1 + self.grid_size
        y2 = y1 + self.grid_size
        #Effacer les rectangles existants en les recouvrant.
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def handle_click(self, event):
        # Calculer la colonne et la ligne de la grille à partir des coordonnées du clic de la souris
        col = event.x // self.grid_size
        row = event.y // self.grid_size
        position = (row, col)

        if self.mode == 'set_start':
            # Si le mode actuel est 'set_start', définir le point de départ
            if position in self.obstacles:
                self.message_label.config(text="Cannot set start on an obstacle.")
                self.window.update()
                return
            if self.start_position:
                self.draw_tile(self.start_position, "white") # Effacer l'ancien point de départ
            self.start_position = position
            self.draw_tile(position, "yellow") # Marquer le point de départ en jaune
            self.mode = None
            self.message_label.config(text="Start position set.") # Mettre à jour le message
            self.window.update()
        elif self.mode == 'set_end':
            # Si le mode actuel est 'set_end', définir le point d'arrivée
            if position in self.obstacles:
                self.message_label.config(text="Cannot set end on an obstacle.")
                self.window.update()
                return
            if self.end_position:
                self.draw_tile(self.end_position, "white") # Effacer l'ancien point d'arrivée
            self.end_position = position
            self.draw_tile(position, "green") # Marquer le point d'arrivée en vert
            self.mode = None
            self.message_label.config(text="End position set.") # Mettre à jour le message
            self.window.update()
        elif self.mode == 'set_obstacles':
            # Si le mode actuel est 'set_obstacles', ajouter ou supprimer des obstacles
            self.toggle_obstacle(position)
        else:
            # Le mode par défaut peut être utilisé pour la visualisation ou d'autres interactions.
            pass

    def toggle_obstacle(self, position):
        # Basculer l'état de l'obstacle à une position donnée : supprimer s'il existe, sinon ajouter
        if position == self.start_position or position == self.end_position:
            # Ne pas autoriser le placement d'un obstacle sur le point de départ ou d'arrivée
            self.message_label.config(text="Cannot place an obstacle on start/end position.")
            self.window.update()
            return
        if position in self.obstacles:
            # Si un obstacle existe à cette position, le supprimer et le redessiner en blanc
            self.obstacles.remove(position)
            self.draw_tile(position, "white")
            self.message_label.config(text=f"Obstacle removed at {position}.")
            self.window.update()
        else:
            # Sinon, ajouter un obstacle et le redessiner en rouge
            self.obstacles.add(position)
            self.draw_tile(position, "red")
            self.message_label.config(text=f"Obstacle added at {position}.")
            self.window.update()

    def Enlarge(self):
        # Définir un mode pour agrandir la taille de la toile.
        self.grid_size += 2  
        self.canvas.config(width=self.cols * self.grid_size, height=self.rows * self.grid_size) 
        self.draw_grid()
        self.message_label.config(text="agrandir la taille de la toile.") 
        self.window.update()

    def Shrink(self):
        # Définir un mode pour réduire la taille de la toile.
        if self.grid_size > 2: 
            self.grid_size -= 2  
            self.canvas.config(width=self.cols * self.grid_size, height=self.rows * self.grid_size) 
            self.draw_grid()
            self.message_label.config(text="réduire la taille de la toile.") 
            self.window.update()

    def set_start_mode(self):
        # Définir le mode sur 'set_start' et inviter l'utilisateur à cliquer sur la grille pour définir le point de départ
        self.mode = 'set_start'
        self.message_label.config(text="Click on the grid to set the start position.")
        self.window.update()

    def set_end_mode(self):
        # Définir le mode sur 'set_end' et inviter l'utilisateur à cliquer sur la grille pour définir le point d'arrivée
        self.mode = 'set_end'
        self.message_label.config(text="Click on the grid to set the end position.")
        self.window.update()

    def set_obstacles_mode(self):
        # Définir le mode sur 'set_obstacles' et inviter l'utilisateur à cliquer sur la grille pour ajouter/supprimer des obstacles
        self.mode = 'set_obstacles'
        self.message_label.config(text="Click on the grid to add/remove obstacles.")
        self.window.update()

    def reset_map(self):
        # Empêcher la réinitialisation de la carte si la simulation est en cours et informer l'utilisateur
        if self.simulation_running :
            self.message_label.config(text="Cannot reset the map during the simulation.")
            self.window.update()
            return

        # Effacer les obstacles, réinitialiser le point de départ et d'arrivée, et redessiner la grille
        self.obstacles.clear()
        self.start_position = None
        self.end_position = None
        self.message_label.config(text="Map reset.")
        self.window.update()
        self.draw_grid()

    def update_tile(self, position, color):
        # Mettre à jour la couleur de la cellule spécifiée
        self.draw_tile(position, color)

    def draw_x(self):
        # Dessiner un "X" rouge sur la grille (généralement pour indiquer un échec ou une invalidité)
        x1 = 0
        y1 = 0
        x2 = self.cols * self.grid_size
        y2 = self.rows * self.grid_size
        self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
        self.canvas.create_line(x1, y2, x2, y1, fill="red", width=2)

    def refresh(self):
        # Rafraîchir la fenêtre pour mettre à jour l'interface utilisateur
        self.window.update()

    def wait(self, ms):
        # Attendre pendant un nombre spécifié de millisecondes
        self.window.after(ms)

    def keep_open(self):
        # Garder la fenêtre ouverte pour exécuter la boucle d'événements
        self.window.mainloop()

    def run_simulation(self):
        if not self.start_position or not self.end_position:
            # Vérifier si le point de départ et le point d'arrivée sont définis, sinon informer l'utilisateur
            self.message_label.config(text="Please set both start and end positions.")
            self.window.update()
            return
        if self.start_position == self.end_position:
            # Vérifier si le point de départ et le point d'arrivée sont définis, sinon informer l'utilisateur
            self.message_label.config(text="Start and end positions cannot be the same.")
            self.window.update()
            return
        # Mettre à jour le message à "Simulation running..." et rafraîchir la fenêtre
        self.message_label.config(text="Simulation running...")
        self.window.update()

        # Initialiser le robot et le simulateur, puis lancer la simulation
        robot = Robot(self.start_position)
        simulator = RobotSimulator(self.rows, self.cols, self)
        simulator.simulate(robot, self.start_position, self.end_position)

class Robot:
    def __init__(self, start_position):
        # Initialiser le robot avec sa position de départ et son chemin enregistré
        self.position = start_position
        self.path = []

    def find_path(self, start, goal, rows, cols, obstacles):
        # Trouver le chemin le plus court du départ à l'objectif
        def heuristic(a, b):
            # Calculer la fonction heuristique
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        frontier = PriorityQueue()# File de priorité pour les nœuds à explorer
        frontier.put((0, start))# Définir la priorité de départ à 0
        came_from = {}# Enregistrer les nœuds précédents
        cost_so_far = {}# Enregistrer le coût total depuis le départ

        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            # Extraire le nœud avec la plus haute priorité
            _, current = frontier.get()

            if current == goal:
                # Si l'objectif est atteint, quitter la boucle
                break

            for dx, dy in [(-1,  0), (1,  0), (0, -1), (0, 1),(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                # Vérifier si le voisin est dans la grille et n'est pas un obstacle
                next_node = (current[0] + dx, current[1] + dy)
                if (0 <= next_node[0] < rows and 0 <= next_node[1] < cols and next_node not in obstacles):
                    # Mettre à jour le coût et la priorité du voisin
                    new_cost = cost_so_far[current] + (1.414 if dx != 0 and dy != 0 else 1)
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + heuristic(goal, next_node)
                        frontier.put((priority, next_node))
                        came_from[next_node] = current

        # Reconstruire le chemin
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                # Retourner un chemin vide si le chemin est interrompu
                return []
        path.append(start)
        path.reverse()
        # Inverser le chemin pour qu'il soit du départ à l'objectif
        return path

class RobotSimulator:
    def __init__(self, rows, cols, map_instance):
        # Initialiser le simulateur avec le nombre de lignes et de colonnes de la grille, ainsi que l'instance de la carte
        self.rows = rows
        self.cols = cols
        self.map = map_instance

    def simulate(self, robot, start_position, end_position):
        # Démarrer la simulation et définir l'état de simulation sur True
        self.map.simulation_running = True
        # Utiliser le robot pour calculer le chemin entre le point de départ et d'arrivée
        path = robot.find_path(start_position, end_position, self.rows, self.cols, self.map.obstacles)

        if not path:
            # Si aucun chemin n'est trouvé, informer l'utilisateur et dessiner un "X" rouge sur la grille
            print("No path found!")
            self.map.message_label.config(text="No path found!")
            self.map.refresh()
            self.map.simulation_running = False
            self.map.draw_x()
            self.map.keep_open()
            return
        
        # Parcourir le chemin et mettre à jour l'affichage de la grille
        for step in path:
            if step == end_position:
                # Si le robot atteint l'objectif, marquer en bleu et informer l'utilisateur
                self.map.update_tile(step, "blue")  # Robot's color at goal
                self.map.message_label.config(text="Robot reached goal!")
            else:
                # Pendant le trajet, mettre à jour en bleu étape par étape avec un effet d'animation
                self.map.update_tile(step, "blue")
                self.map.refresh()
                self.map.wait(500)
                self.map.update_tile(step, "lightblue")
                self.map.refresh()
                self.map.wait(500)

        print("Path Taken:", path)
        # Afficher le chemin pris et terminer la simulation
        self.map.simulation_running = False
        self.map.keep_open()

if __name__ == "__main__":
    # Define the size of the grid
    rows, cols = 15, 15  # Change as needed

    # Create the map and start the GUI
    map_instance = Map(rows, cols)
    map_instance.draw_grid()
    map_instance.keep_open()
