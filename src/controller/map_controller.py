class MapController:
    """Gère les actions de l'utilisateur sur la carte."""

    def __init__(self, map_model, map_view):
        self.map_model = map_model
        self.map_view = map_view

    def add_obstacle(self, x, y):
        """Ajoute un obstacle et met à jour l'affichage."""
        self.map_model.add_obstacle(x, y)
        self.map_view.draw_obstacles()
