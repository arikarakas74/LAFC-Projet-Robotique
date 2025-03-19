from abc import ABC, abstractmethod

class BaseMotorAdapter(ABC):
    """
    Classe abstraite pour la gestion des positions des moteurs.
    Toute classe dérivée devra implémenter ces méthodes.
    """
    
    @abstractmethod
    def get_motor_position(self, motor_id):
        """
        Retourne la position actuelle du moteur identifié par motor_id.
        
        :param motor_id: Identifiant du moteur (ex. "left", "right")
        :return: Position actuelle du moteur
        """
        pass

    @abstractmethod
    def set_motor_position(self, motor_id, position):
        """
        Définit la position du moteur identifié par motor_id.
        
        :param motor_id: Identifiant du moteur (ex. "left", "right")
        :param position: Nouvelle position à définir
        """
        pass

    @abstractmethod
    def zero_motor_position(self, motor_id):
        """
        Remet à zéro la position du moteur identifié par motor_id.
        
        :param motor_id: Identifiant du moteur (ex. "left", "right")
        """
        pass

# Exemple d'implémentation concrète pour un robot ou une simulation

