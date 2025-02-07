class MapModel:
    """Gère la carte et les obstacles."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = []
        self.start_position = None

    def add_obstacle(self, x, y):
        """Ajoute un obstacle."""
        if (x, y) not in self.obstacles:
            self.obstacles.append((x, y))

    def remove_obstacle(self, x, y):
        """Supprime un obstacle."""
        if (x, y) in self.obstacles:
            self.obstacles.remove((x, y))

    def set_start_position(self, x, y):
        """Définit la position de départ du robot."""
        self.start_position = (x, y)

    def is_obstacle(self, x, y):
        """Vérifie si une position est occupée par un obstacle."""
        grid_size = 50  # Taille de la grille
        x = (x // grid_size) * grid_size  # Alignement sur la grille
        y = (y // grid_size) * grid_size  # Alignement sur la grille
        return (x, y) in self.obstacles

