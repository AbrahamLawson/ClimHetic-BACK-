from app.database import execute_query, execute_single_query
from typing import Dict, Any

class CapteurService:
    
    def get_moyennes_dernieres_donnees_by_salle(self, salle_id, limit=10):
        """
        Récupérer la moyenne des dernières données par salle (température, humidité, pression)
        
        Args:
            salle_id (int): ID de la salle
            limit (int): Nombre de dernières mesures à considérer pour la moyenne
            
        Returns:
            dict: Moyennes des données ou None si aucune donnée
        """
        try:
            query = """
                SELECT 
                    s.id as salle_id,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage,
                    -- Moyenne température
                    AVG(t_data.valeur) as moyenne_temperature,
                    -- Moyenne humidité
                    AVG(h_data.valeur) as moyenne_humidite,
                    -- Moyenne pression
                    AVG(p_data.valeur) as moyenne_pression,
                    -- Unités
                    MAX(t_data.unite) as unite_temperature,
                    MAX(h_data.unite) as unite_humidite,
                    MAX(p_data.unite) as unite_pression
                FROM salle s
                LEFT JOIN capteur c ON s.id = c.id_salle
                LEFT JOIN (
                    SELECT capteur_id, valeur, unite, date_update,
                           ROW_NUMBER() OVER (PARTITION BY capteur_id ORDER BY date_update DESC) as rn
                    FROM temperature
                ) t_data ON c.id = t_data.capteur_id AND c.type_capteur = 'temperature' AND t_data.rn <= %s
                LEFT JOIN (
                    SELECT capteur_id, valeur, unite, date_update,
                           ROW_NUMBER() OVER (PARTITION BY capteur_id ORDER BY date_update DESC) as rn
                    FROM humidite
                ) h_data ON c.id = h_data.capteur_id AND c.type_capteur = 'humidite' AND h_data.rn <= %s
                LEFT JOIN (
                    SELECT capteur_id, valeur, unite, date_update,
                           ROW_NUMBER() OVER (PARTITION BY capteur_id ORDER BY date_update DESC) as rn
                    FROM pression
                ) p_data ON c.id = p_data.capteur_id AND c.type_capteur = 'pression' AND p_data.rn <= %s
                WHERE s.id = %s AND s.etat = 'active'
                GROUP BY s.id, s.nom, s.batiment, s.etage
            """
            
            result = execute_single_query(query, (limit, limit, limit, salle_id))
            return result
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des moyennes pour la salle {salle_id}: {str(e)}")

    def get_dernieres_donnees_by_capteur(self, capteur_id, limit=1):
        """
        Récupérer les dernières données d'un capteur spécifique
        
        Args:
            capteur_id (int): ID du capteur
            limit (int): Nombre de dernières mesures à récupérer
            
        Returns:
            dict: Informations du capteur et ses données
        """
        try:
            # D'abord récupérer les infos du capteur
            capteur_query = """
                SELECT c.*, s.nom as salle_nom, s.batiment, s.etage
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s AND c.is_active = TRUE
            """
            
            capteur = execute_single_query(capteur_query, (capteur_id,))
            
            if not capteur:
                return None
            
            donnees = []
            
            # Récupérer les données selon le type de capteur
            type_capteur = capteur.get('type_capteur')  # type: ignore
            
            if type_capteur == 'temperature':
                temp_query = """
                    SELECT valeur, unite, date_update
                    FROM temperature
                    WHERE capteur_id = %s
                    ORDER BY date_update DESC
                    LIMIT %s
                """
                donnees = execute_query(temp_query, (capteur_id, limit))
                
            elif type_capteur == 'humidite':
                hum_query = """
                    SELECT valeur, unite, date_update
                    FROM humidite
                    WHERE capteur_id = %s
                    ORDER BY date_update DESC
                    LIMIT %s
                """
                donnees = execute_query(hum_query, (capteur_id, limit))
                
            elif type_capteur == 'pression':
                press_query = """
                    SELECT valeur, unite, date_update
                    FROM pression
                    WHERE capteur_id = %s
                    ORDER BY date_update DESC
                    LIMIT %s
                """
                donnees = execute_query(press_query, (capteur_id, limit))
            
            return {
                'capteur': capteur,
                'donnees': donnees
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des données du capteur {capteur_id}: {str(e)}")

    def get_temperature_by_salle(self, salle_id, limit=10):
        """
        Récupérer les données de température d'une salle
        
        Args:
            salle_id (int): ID de la salle
            limit (int): Nombre de mesures à récupérer
            
        Returns:
            list: Liste des températures
        """
        try:
            query = """
                SELECT 
                    c.id as capteur_id,
                    c.nom,
                    t.valeur,
                    t.unite,
                    t.date_update,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM capteur c
                JOIN salle s ON c.id_salle = s.id
                JOIN temperature t ON c.id = t.capteur_id
                WHERE s.id = %s AND c.type_capteur = 'temperature' AND c.is_active = TRUE
                ORDER BY t.date_update DESC
                LIMIT %s
            """
            
            return execute_query(query, (salle_id, limit))
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de la température pour la salle {salle_id}: {str(e)}")

    def get_humidite_by_salle(self, salle_id, limit=10):
        """
        Récupérer les données d'humidité d'une salle
        
        Args:
            salle_id (int): ID de la salle
            limit (int): Nombre de mesures à récupérer
            
        Returns:
            list: Liste des humidités
        """
        try:
            query = """
                SELECT 
                    c.id as capteur_id,
                    c.nom,
                    h.valeur,
                    h.unite,
                    h.date_update,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM capteur c
                JOIN salle s ON c.id_salle = s.id
                JOIN humidite h ON c.id = h.capteur_id
                WHERE s.id = %s AND c.type_capteur = 'humidite' AND c.is_active = TRUE
                ORDER BY h.date_update DESC
                LIMIT %s
            """
            
            return execute_query(query, (salle_id, limit))
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de l'humidité pour la salle {salle_id}: {str(e)}")

    def get_pression_by_salle(self, salle_id, limit=10):
        """
        Récupérer les données de pression d'une salle
        
        Args:
            salle_id (int): ID de la salle
            limit (int): Nombre de mesures à récupérer
            
        Returns:
            list: Liste des pressions
        """
        try:
            query = """
                SELECT 
                    c.id as capteur_id,
                    c.nom,
                    p.valeur,
                    p.unite,
                    p.date_update,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM capteur c
                JOIN salle s ON c.id_salle = s.id
                JOIN pression p ON c.id = p.capteur_id
                WHERE s.id = %s AND c.type_capteur = 'pression' AND c.is_active = TRUE
                ORDER BY p.date_update DESC
                LIMIT %s
            """
            
            return execute_query(query, (salle_id, limit))
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de la pression pour la salle {salle_id}: {str(e)}")

    def get_temperature_by_capteur(self, capteur_id, limit=10):
        """
        Récupérer les données de température d'un capteur spécifique
        
        Args:
            capteur_id (int): ID du capteur
            limit (int): Nombre de mesures à récupérer
            
        Returns:
            list: Liste des températures
        """
        try:
            query = """
                SELECT 
                    t.valeur,
                    t.unite,
                    t.date_update,
                    c.nom,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM temperature t
                JOIN capteur c ON t.capteur_id = c.id
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s AND c.is_active = TRUE
                ORDER BY t.date_update DESC
                LIMIT %s
            """
            
            return execute_query(query, (capteur_id, limit))
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de la température pour le capteur {capteur_id}: {str(e)}")

    def get_salles_actives(self):
        """
        Récupérer la liste des salles actives
        
        Returns:
            list: Liste des salles actives
        """
        try:
            query = """
                SELECT id, nom, batiment, etage, capacite, date_creation
                FROM salle
                WHERE etat = 'active'
                ORDER BY batiment, etage, nom
            """
            
            return execute_query(query)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des salles: {str(e)}")

    def get_capteurs_by_salle(self, salle_id):
        """
        Récupérer la liste des capteurs actifs d'une salle
        
        Args:
            salle_id (int): ID de la salle
            
        Returns:
            list: Liste des capteurs de la salle
        """
        try:
            query = """
                SELECT 
                    c.id,
                    c.nom,
                    c.type_capteur,
                    c.date_installation,
                    s.nom as salle_nom
                FROM capteur c
                JOIN salle s ON c.id_salle = s.id
                WHERE c.id_salle = %s AND c.is_active = TRUE
                ORDER BY c.type_capteur, c.nom
            """
            
            return execute_query(query, (salle_id,))
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des capteurs pour la salle {salle_id}: {str(e)}")

# Instance globale du service
capteur_service = CapteurService() 