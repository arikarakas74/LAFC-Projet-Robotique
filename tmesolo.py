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

def q2_2():
    """
    Lance la simulation avec deux robots exécutant des stratégies distinctes:
    - Souris (bleue): Dessine un carré sur le côté gauche.
    - Chat (rouge): Fait un aller-retour vertical sur le côté droit.
    """
    print("Lancement de la simulation avec stratégies Q2.2...")
    try:
        app = run_gui() 
        
        # Importer les stratégies nécessaires
        from controller.StrategyAsync import PolygonStrategy, UpDownStrategy
        import threading
        import time

        # Obtenir les modèles des robots
        mouse_model = app.sim_controller.get_robot_model(0)
        cat_model = app.sim_controller.get_robot_model(1)

        if not mouse_model or not cat_model:
            print("Erreur: Impossible de trouver les modèles de la souris et/ou du chat.")
            return

        # -- Configuration de la stratégie de la souris (Carré) --
        # S'assurer que la souris commence dans une position et orientation adéquate
        mouse_start_pos = (100, 100) # Exemple: coin supérieur gauche
        mouse_model.x, mouse_model.y = mouse_start_pos
        mouse_model.direction_angle = 0 # Orienté vers la droite
        mouse_model.dessine(True) # Activer le dessin pour la souris
        square_strategy = PolygonStrategy(n=4, adapter=mouse_model, side_length_cm=150, vitesse_avance=50, vitesse_rotation=90)
        
        # -- Configuration de la stratégie du chat (Aller-retour) --
        # S'assurer que le chat commence dans une position et orientation adéquate
        cat_start_pos = (700, 500) # Exemple: coin inférieur droit
        cat_model.x, cat_model.y = cat_start_pos
        cat_model.direction_angle = -90 # Orienté vers le haut
        cat_model.dessine(True) # Activer le dessin pour le chat
        up_down_strategy = UpDownStrategy(adapter=cat_model, distance_cm=400, vitesse_avance=60, vitesse_rotation=100)

        # Fonction pour exécuter une stratégie dans un thread
        def run_strategy_in_thread(strategy, name):
            print(f"Démarrage du thread pour la stratégie: {name}")
            delta_time = 0.02  # Intervalle de mise à jour
            strategy.start()
            # We need to call step() here for the strategy to progress
            while not strategy.is_finished() and app.sim_controller.simulation_running:
                strategy.step(delta_time) # Call step directly
                time.sleep(delta_time) # Adjust sleep if needed
            print(f"Thread terminé pour la stratégie: {name}")

        # Lancer la simulation principale si elle n'est pas déjà active
        if not app.sim_controller.simulation_running:
            app.sim_controller.run_simulation()

        # Créer et démarrer les threads pour chaque stratégie
        mouse_thread = threading.Thread(target=run_strategy_in_thread, args=(square_strategy, "Souris Carré"), daemon=True)
        cat_thread = threading.Thread(target=run_strategy_in_thread, args=(up_down_strategy, "Chat AllerRetour"), daemon=True)
        
        mouse_thread.start()
        cat_thread.start()
        
        print("Stratégies lancées dans des threads séparés.")
        # Laisser la boucle principale Tkinter (ou run_gui) gérer l'application
        # app.mainloop() # Ne pas démarrer ici si run_gui ou autre le fait

    except ImportError as ie:
         print(f"Erreur d'importation pour les stratégies: {ie}. Assurez-vous que controller/StrategyAsync.py existe et contient les classes.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution de q2_2 : {e}")
        import traceback
        traceback.print_exc()

# --- Fin des fonctions restaurées/ajoutées ---

# --- Exécution ---

if __name__ == "__main__":
    # Instructions: Pour tester une fonction, décommentez la ligne correspondante
    # ci-dessous et exécutez le script: python tmesolo.py
    # Assurez-vous de fermer la fenêtre de simulation avant de tester la suivante.
    
    print("--- Prêt à tester les fonctions de tmesolo.py ---")

    # print("\n Test de q1_1 - Lance la GUI simple")
    # q1_1()

    # print("\n Test de q1_2 - Stratégie Mur (Souris)")
    # q1_2()

    # print("\n Test de q1_3 - Activation Dessin Bleu (Souris)")
    # q1_3()

    # print("\n Test de q1_4 - Activation Dessin Rouge (Souris)")
    # q1_4()

    # print("\n Test de q1_5 - Stratégie Mur Couleur (Souris)")
    # q1_5()

    # print("\n Test de q2_1 - Deux Robots Contrôle Manuel")
    # q2_1()

    # print("\n Test de q2_2 - Deux Robots Stratégies Concurrentes")
    # q2_2()

    print("\n--- Fin des tests (décommentez les lignes ci-dessus pour exécuter) ---")



