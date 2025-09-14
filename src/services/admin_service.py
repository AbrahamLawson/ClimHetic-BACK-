from typing import Dict, Any, List, Optional
from config.database import execute_query, get_db_connection

class AdminService:
    """Service pour la gestion administrative des capteurs et salles"""
    
    def get_all_capteurs(self):
        """
        Récupérer tous les capteurs (actifs et inactifs) avec leur affiliation
        
        Returns:
            list: Liste de tous les capteurs avec leurs informations
        """
        try:
            query = """
                SELECT 
                    c.id,
                    c.nom_capteur,
                    c.type_capteur,
                    c.date_installation,
                    c.is_active,
                    c.id_salle,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage,
                    CASE 
                        WHEN c.id_salle IS NULL THEN 'Non affilié'
                        WHEN c.is_active = 0 THEN 'Inactif'
                        ELSE 'Actif'
                    END as statut
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                ORDER BY c.is_active DESC, c.nom_capteur
            """
            
            return execute_query(query)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des capteurs: {str(e)}")
    
    def get_capteurs_disponibles(self):
        """
        Récupérer les capteurs disponibles (actifs mais non affiliés)
        
        Returns:
            list: Liste des capteurs disponibles
        """
        try:
            query = """
                SELECT 
                    c.id,
                    c.nom_capteur,
                    c.type_capteur,
                    c.date_installation
                FROM capteur c
                WHERE c.is_active = TRUE AND c.id_salle IS NULL
                ORDER BY c.type_capteur, c.nom_capteur
            """
            
            return execute_query(query)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des capteurs disponibles: {str(e)}")
    
    def get_capteurs_indisponibles(self):
        """
        Récupérer les capteurs indisponibles (inactifs ou en panne)
        
        Returns:
            list: Liste des capteurs indisponibles
        """
        try:
            query = """
                SELECT 
                    c.id,
                    c.nom_capteur,
                    c.type_capteur,
                    c.date_installation,
                    c.id_salle,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.is_active = FALSE
                ORDER BY c.nom_capteur
            """
            
            return execute_query(query)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des capteurs indisponibles: {str(e)}")
    
    def get_capteurs_par_salle(self):
        """
        Récupérer les capteurs groupés par salle
        
        Returns:
            dict: Dictionnaire avec les salles et leurs capteurs
        """
        try:
            query = """
                SELECT 
                    s.id as salle_id,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage,
                    s.capacite,
                    COUNT(c.id) as nb_capteurs,
                    GROUP_CONCAT(
                        CONCAT(c.nom_capteur, ' (', c.type_capteur, ')')
                        ORDER BY c.type_capteur, c.nom_capteur
                        SEPARATOR ', '
                    ) as liste_capteurs
                FROM salle s
                LEFT JOIN capteur c ON s.id = c.id_salle AND c.is_active = TRUE
                WHERE s.etat = 'active'
                GROUP BY s.id, s.nom, s.batiment, s.etage, s.capacite
                ORDER BY s.batiment, s.etage, s.nom
            """
            
            return execute_query(query)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des capteurs par salle: {str(e)}")
    
    def associer_capteur_salle(self, capteur_id: int, salle_id: int):
        """
        Associer un capteur à une salle
        
        Args:
            capteur_id (int): ID du capteur
            salle_id (int): ID de la salle
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            # Vérifier que le capteur existe et est disponible
            capteur = self.get_capteur_by_id(capteur_id)
            if not capteur:
                raise Exception("Capteur introuvable")
            
            if not capteur['is_active']:
                raise Exception("Le capteur n'est pas actif")
            
            if capteur['id_salle'] is not None:
                raise Exception("Le capteur est déjà associé à une salle")
            
            # Vérifier que la salle existe
            salle = self.get_salle_by_id(salle_id)
            if not salle:
                raise Exception("Salle introuvable")
            
            # Effectuer l'association
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        UPDATE capteur 
                        SET id_salle = %s 
                        WHERE id = %s AND is_active = TRUE
                    """
                    cursor.execute(query, (salle_id, capteur_id))
                    connection.commit()
                    
                    if cursor.rowcount == 0:
                        raise Exception("Impossible d'associer le capteur")
            
            return {
                'success': True,
                'message': f'Capteur {capteur["nom_capteur"]} associé à la salle {salle["nom"]} avec succès'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'association: {str(e)}")
    
    def dissocier_capteur_salle(self, capteur_id: int):
        """
        Dissocier un capteur de sa salle
        
        Args:
            capteur_id (int): ID du capteur
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            # Vérifier que le capteur existe et est associé
            capteur = self.get_capteur_by_id(capteur_id)
            if not capteur:
                raise Exception("Capteur introuvable")
            
            if capteur['id_salle'] is None:
                raise Exception("Le capteur n'est associé à aucune salle")
            
            # Effectuer la dissociation
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        UPDATE capteur 
                        SET id_salle = NULL 
                        WHERE id = %s
                    """
                    cursor.execute(query, (capteur_id,))
                    connection.commit()
                    
                    if cursor.rowcount == 0:
                        raise Exception("Impossible de dissocier le capteur")
            
            return {
                'success': True,
                'message': f'Capteur {capteur["nom_capteur"]} dissocié avec succès'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la dissociation: {str(e)}")
    
    def activer_capteur(self, capteur_id: int):
        """
        Activer un capteur
        
        Args:
            capteur_id (int): ID du capteur
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        UPDATE capteur 
                        SET is_active = TRUE 
                        WHERE id = %s
                    """
                    cursor.execute(query, (capteur_id,))
                    connection.commit()
                    
                    if cursor.rowcount == 0:
                        raise Exception("Capteur introuvable")
            
            return {
                'success': True,
                'message': 'Capteur activé avec succès'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'activation: {str(e)}")
    
    def desactiver_capteur(self, capteur_id: int):
        """
        Désactiver un capteur (et le dissocier automatiquement)
        
        Args:
            capteur_id (int): ID du capteur
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        UPDATE capteur 
                        SET is_active = FALSE, id_salle = NULL 
                        WHERE id = %s
                    """
                    cursor.execute(query, (capteur_id,))
                    connection.commit()
                    
                    if cursor.rowcount == 0:
                        raise Exception("Capteur introuvable")
            
            return {
                'success': True,
                'message': 'Capteur désactivé et dissocié avec succès'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la désactivation: {str(e)}")
    
    def get_capteur_by_id(self, capteur_id: int):
        """
        Récupérer un capteur par son ID
        
        Args:
            capteur_id (int): ID du capteur
            
        Returns:
            dict: Informations du capteur
        """
        try:
            query = """
                SELECT 
                    c.id,
                    c.nom_capteur,
                    c.type_capteur,
                    c.date_installation,
                    c.is_active,
                    c.id_salle,
                    s.nom as salle_nom
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s
            """
            
            result = execute_query(query, (capteur_id,))
            return result[0] if result else None
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération du capteur: {str(e)}")
    
    def get_salle_by_id(self, salle_id: int):
        """
        Récupérer une salle par son ID
        
        Args:
            salle_id (int): ID de la salle
            
        Returns:
            dict: Informations de la salle
        """
        try:
            query = """
                SELECT id, nom, batiment, etage, capacite
                FROM salle
                WHERE id = %s AND etat = 'active'
            """
            
            result = execute_query(query, (salle_id,))
            return result[0] if result else None
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de la salle: {str(e)}")
    
    def get_statistiques(self):
        """
        Récupérer les statistiques générales
        
        Returns:
            dict: Statistiques des capteurs et salles
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_capteurs,
                    SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as capteurs_actifs,
                    SUM(CASE WHEN is_active = FALSE THEN 1 ELSE 0 END) as capteurs_inactifs,
                    SUM(CASE WHEN is_active = TRUE AND id_salle IS NOT NULL THEN 1 ELSE 0 END) as capteurs_associes,
                    SUM(CASE WHEN is_active = TRUE AND id_salle IS NULL THEN 1 ELSE 0 END) as capteurs_disponibles
                FROM capteur
            """
            
            stats_capteurs = execute_query(query)[0]
            
            query_salles = """
                SELECT 
                    COUNT(*) as total_salles,
                    COUNT(DISTINCT c.id_salle) as salles_avec_capteurs
                FROM salle s
                LEFT JOIN capteur c ON s.id = c.id_salle AND c.is_active = TRUE
                WHERE s.etat = 'active'
            """
            
            stats_salles = execute_query(query_salles)[0]
            
            return {
                **stats_capteurs,
                **stats_salles,
                'salles_sans_capteurs': stats_salles['total_salles'] - stats_salles['salles_avec_capteurs']
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des statistiques: {str(e)}")

# Instance globale du service admin
admin_service = AdminService()
