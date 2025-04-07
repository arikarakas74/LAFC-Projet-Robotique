# tmesolo.py - Regroupement des fonctions pour les questions X.Y

# Importation de la fonction pour lancer l'interface graphique Tkinter
from gui_main import run_gui

# --- Fonctions pour les questions ---

def q1_1():
    """
    Lance la simulation graphique Tkinter (provenant de gui_main.py).
    """
    print("Lancement de la simulation graphique Tkinter (q1_1)...")
    try:
        run_gui()
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q1_1 : {e}")
        

def q1_2():
    """
    Lance la simulation et active la stratégie Q1.2 pour la souris:
    - Déplace la souris vers la droite.
    - Fait un demi-tour (180°) lors de la détection d'un mur/obstacle.
    - Répète 10 fois.
    """
    print("Lancement de la simulation graphique avec stratégie Q1.2 (souris)...")
    try:
        app = run_gui() 
        if hasattr(app, 'control_panel') and hasattr(app.control_panel, 'start_q1_2_strategy'):
            print("Démarrage de la stratégie Q1.2...")
            app.control_panel.start_q1_2_strategy()
            # Main loop is usually started within run_gui or by the strategy start
        else:
            print("Erreur: Impossible de trouver control_panel ou start_q1_2_strategy.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q1_2 : {e}")

def q1_3():
    """
    Lance la simulation et active le mode dessin pour la souris (trace bleue par défaut).
    """
    print("Lancement de la simulation graphique avec mode dessin (Q1.3 - souris)...")
    try:
        app = run_gui()
        # Access the first robot model (mouse) via sim_controller
        mouse_model = app.sim_controller.get_robot_model(0) 
        if mouse_model and hasattr(mouse_model, 'dessine'):
            print("Activation du mode dessin pour la souris...")
            mouse_model.dessine(True)
            # Make sure simulation runs if not started automatically
            if not app.sim_controller.simulation_running:
                 app.sim_controller.run_simulation()
            # Optional: Start mainloop here if run_gui doesn't
            # app.mainloop()
        else:
            print("Erreur: Impossible de trouver le modèle de la souris ou la méthode dessine.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q1_3 : {e}")

def q1_4():
    """
    Lance la simulation, définit la couleur de trace de la souris sur rouge et active le dessin.
    """
    print("Lancement de la simulation graphique avec trace rouge (Q1.4 - souris)...")
    try:
        app = run_gui()
        mouse_model = app.sim_controller.get_robot_model(0)
        if mouse_model and hasattr(mouse_model, 'rouge') and hasattr(mouse_model, 'dessine'):
            print("Définition de la couleur de trace de la souris sur rouge...")
            mouse_model.rouge()  # Définit la couleur
            print("Activation du mode dessin pour la souris...")
            mouse_model.dessine(True) # Active le dessin
            if not app.sim_controller.simulation_running:
                 app.sim_controller.run_simulation()
            # app.mainloop()
        else:
            print("Erreur: Impossible de trouver le modèle de la souris ou les méthodes rouge/dessine.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q1_4 : {e}")

def q1_5():
    """
    Lance la simulation et active la stratégie Q1.5 pour la souris:
    - Trace rouge en allant vers la droite.
    - Trace bleue en tournant de 180 degrés.
    - Répète 10 fois.
    """
    print("Lancement de la simulation graphique avec stratégie Q1.5 (souris)...")
    try:
        app = run_gui() 
        if hasattr(app, 'control_panel') and hasattr(app.control_panel, 'start_q1_5_strategy'):
            print("Démarrage de la stratégie Q1.5...")
            app.control_panel.start_q1_5_strategy()
        else:
            print("Erreur: Impossible de trouver control_panel ou start_q1_5_strategy.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q1_5 : {e}")

def q2_1():
    """
    Lance la simulation graphique avec les deux robots (souris et chat).
    Leurs contrôleurs sont indépendants (clavier).
    """
    print("Lancement de la simulation graphique avec deux robots (Q2.1)...")
    try:
        app = run_gui() 
        # Just running the GUI is enough, as MainApplication creates both robots
        print("Simulation lancée. Contrôlez la souris avec WASDQE, le chat avec les flèches/IJKL.")
        # Ensure simulation is running
        if not app.sim_controller.simulation_running:
             app.sim_controller.run_simulation()
        # If run_gui doesn't start the loop, uncomment the line below
        # app.mainloop() 
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q2_1 : {e}")

# --- Fin des fonctions restaurées/ajoutées ---

# --- Exécution ---

if __name__ == "__main__":
    pass # Add pass to fix indentation error
    # print("Fichier tmesolo.py exécuté.")
    # print("Pour exécuter une question spécifique, appelez sa fonction, par exemple :")
    # print("import tmesolo")
    # print("tmesolo.q2_1()")
    # Ou, décommentez la ligne suivante pour lancer une fonction par défaut:
    # q2_1()



