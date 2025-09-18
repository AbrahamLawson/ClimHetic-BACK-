from typing import Dict, Any, List, Optional
from app.queries import execute_query, execute_single_query
from app.database import engine
from sqlalchemy import text

class AdminService:
    
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
                    c.nom,
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
                    END as statut,
                    CASE 
                        WHEN c.type_capteur = 'temperature' THEN 
                            (SELECT CONCAT(t.valeur, ' ', t.unite, ' (', DATE_FORMAT(t.date_update, '%d/%m/%Y %H:%i'), ')')
                             FROM temperature t 
                             WHERE t.capteur_id = c.id AND t.date_update >= c.date_installation
                             ORDER BY t.date_update DESC 
                             LIMIT 1)
                        WHEN c.type_capteur = 'humidite' THEN 
                            (SELECT CONCAT(h.valeur, ' ', h.unite, ' (', DATE_FORMAT(h.date_update, '%d/%m/%Y %H:%i'), ')')
                             FROM humidite h 
                             WHERE h.capteur_id = c.id AND h.date_update >= c.date_installation
                             ORDER BY h.date_update DESC 
                             LIMIT 1)
                        WHEN c.type_capteur = 'pression' THEN 
                            (SELECT CONCAT(p.valeur, ' ', p.unite, ' (', DATE_FORMAT(p.date_update, '%d/%m/%Y %H:%i'), ')')
                             FROM pression p 
                             WHERE p.capteur_id = c.id AND p.date_update >= c.date_installation
                             ORDER BY p.date_update DESC 
                             LIMIT 1)
                        ELSE NULL
                    END as derniere_mesure
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                ORDER BY c.is_active DESC, c.nom
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
                    c.nom,
                    c.type_capteur,
                    c.date_installation
                FROM capteur c
                WHERE c.is_active = TRUE AND c.id_salle IS NULL
                ORDER BY c.type_capteur, c.nom
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
                    c.nom,
                    c.type_capteur,
                    c.date_installation,
                    c.id_salle,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.is_active = FALSE
                ORDER BY c.nom
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
                        CONCAT(c.nom, ' (', c.type_capteur, ')')
                        ORDER BY c.type_capteur, c.nom
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
            capteur = self.get_capteur_by_id(capteur_id)
            if not capteur:
                raise Exception("Capteur introuvable")
            
            if not capteur['is_active']:
                raise Exception("Le capteur n'est pas actif")
            
            if capteur['id_salle'] is not None:
                raise Exception("Le capteur est déjà associé à une salle")
            
            salle = self.get_salle_by_id(salle_id)
            if not salle:
                raise Exception("Salle introuvable")
            
            with engine.connect() as conn:
                query = """
                    UPDATE capteur 
                    SET id_salle = :salle_id 
                    WHERE id = :capteur_id AND is_active = TRUE
                """
                result = conn.execute(text(query), {'salle_id': salle_id, 'capteur_id': capteur_id})
                conn.commit()
                
                if result.rowcount == 0:
                    raise Exception("Impossible d'associer le capteur")
            
            return {
                'success': True,
                'message': f'Capteur {capteur["nom"]} associé à la salle {salle["nom"]} avec succès'
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
            capteur = self.get_capteur_by_id(capteur_id)
            if not capteur:
                raise Exception("Capteur introuvable")
            
            if capteur['id_salle'] is None:
                raise Exception("Le capteur n'est associé à aucune salle")
            
            with engine.connect() as conn:
                query = """
                    UPDATE capteur 
                    SET id_salle = NULL 
                    WHERE id = :capteur_id
                """
                result = conn.execute(text(query), {'capteur_id': capteur_id})
                conn.commit()
                
                if result.rowcount == 0:
                    raise Exception("Impossible de dissocier le capteur")
            
            return {
                'success': True,
                'message': f'Capteur {capteur["nom"]} dissocié avec succès'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la dissociation: {str(e)}")
    
    def changer_salle_capteur(self, capteur_id: int, nouvelle_salle_id: int):
        """
        Changer la salle d'un capteur déjà affilié
        
        Args:
            capteur_id (int): ID du capteur
            nouvelle_salle_id (int): ID de la nouvelle salle
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            capteur = self.get_capteur_by_id(capteur_id)
            if not capteur:
                raise Exception("Capteur introuvable")
            
            if not capteur['is_active']:
                raise Exception("Le capteur n'est pas actif")
            
            nouvelle_salle = self.get_salle_by_id(nouvelle_salle_id)
            if not nouvelle_salle:
                raise Exception("Nouvelle salle introuvable")
            
            if capteur['id_salle'] == nouvelle_salle_id:
                raise Exception("Le capteur est déjà dans cette salle")
            
            query_update = """
                UPDATE capteur 
                SET id_salle = :id_salle, date_installation = NOW() 
                WHERE id = :id AND is_active = TRUE
            """
            
            with engine.connect() as connection:
                result = connection.execute(text(query_update), {"id_salle": nouvelle_salle_id, "id": capteur_id})
                connection.commit()
                
                if result.rowcount == 0:
                    raise Exception("Impossible de changer la salle du capteur")
            
            ancienne_salle_nom = "aucune salle"
            if capteur['id_salle']:
                ancienne_salle = self.get_salle_by_id(capteur['id_salle'])
                if ancienne_salle:
                    ancienne_salle_nom = ancienne_salle['nom']
            
            return {
                'success': True,
                'message': f'Capteur {capteur["nom"]} déplacé de "{ancienne_salle_nom}" vers "{nouvelle_salle["nom"]}" avec succès. Date d\'installation mise à jour.'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors du changement de salle: {str(e)}")
    
    def activer_capteur(self, capteur_id: int):
        """
        Activer un capteur
        
        Args:
            capteur_id (int): ID du capteur
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            with engine.connect() as conn:
                query = """
                    UPDATE capteur 
                    SET is_active = TRUE 
                    WHERE id = :capteur_id
                """
                result = conn.execute(text(query), {'capteur_id': capteur_id})
                conn.commit()
                
                if result.rowcount == 0:
                    raise Exception("Capteur introuvable")
            
            return {
                'success': True,
                'message': 'Capteur activé avec succès'
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'activation: {str(e)}")
    
    def desactiver_capteur(self, capteur_id: int):
        try:
            capteur_query = """
                SELECT c.id, c.nom, c.type_capteur, c.is_active, s.nom as salle_nom
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s
            """
            capteur = execute_single_query(capteur_query, (capteur_id,))
            
            if not capteur:
                raise Exception(f"Capteur {capteur_id} introuvable")
            
            if not capteur['is_active']:
                raise Exception(f"Le capteur {capteur_id} est déjà désactivé")
            
            with engine.connect() as conn:
                query = """
                    UPDATE capteur 
                    SET is_active = FALSE, id_salle = NULL 
                    WHERE id = :capteur_id
                """
                result = conn.execute(text(query), {'capteur_id': capteur_id})
                conn.commit()
                
                if result.rowcount == 0:
                    raise Exception("Capteur introuvable")
            
            capteur['is_active'] = False
            return capteur
            
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
                    c.nom,
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

    def ajouter_capteur(self, nom, type_capteur, id_salle):
        """
        Ajouter un nouveau capteur (fonction d'administration)
        
        Args:
            nom (str): Nom/identifiant du capteur
            type_capteur (str): Type de capteur ('temperature', 'humidite', 'pression')
            id_salle (int): ID de la salle où installer le capteur
            
        Returns:
            dict: Informations du capteur créé ou None si erreur
        """
        try:
            if nom is None or str(nom).strip() == '':
                raise Exception("Le nom du capteur est obligatoire")
            if id_salle is None:
                raise Exception("L'ID de la salle est obligatoire")
            
            types_valides = ['temperature', 'humidite', 'pression']
            if type_capteur is None or type_capteur == '' or type_capteur not in types_valides:
                raise Exception(f"Type de capteur invalide. Types autorisés: {', '.join(types_valides)}")
            
            salle_query = """
                SELECT id, nom FROM salle 
                WHERE id = %s AND etat = 'active'
            """
            salle = execute_single_query(salle_query, (id_salle,))
            
            if not salle:
                raise Exception(f"Salle {id_salle} introuvable ou inactive")
            
            capteur_existant_query = """
                SELECT id FROM capteur 
                WHERE nom = %s AND type_capteur = %s AND id_salle = %s
            """
            capteur_existant = execute_single_query(capteur_existant_query, (nom, type_capteur, id_salle))
            
            if capteur_existant:
                raise Exception(f"Un capteur de type '{type_capteur}' existe déjà dans cette salle")
            
            insert_query = """
                INSERT INTO capteur (nom, type_capteur, id_salle, date_installation, is_active)
                VALUES (%s, %s, %s, NOW(), TRUE)
            """
            
            with engine.connect() as conn:
                params = (nom, type_capteur, id_salle)
                param_dict = {f'param_{i}': param for i, param in enumerate(params)}
                query_with_params = insert_query
                for i in range(len(params)):
                    query_with_params = query_with_params.replace('%s', f':param_{i}', 1)
                
                result = conn.execute(text(query_with_params), param_dict)
                conn.commit()
                
                capteur_id = result.lastrowid
            
            capteur_cree_query = """
                SELECT 
                    c.id,
                    c.nom,
                    c.type_capteur,
                    c.date_installation,
                    c.is_active,
                    s.nom as salle_nom,
                    s.batiment,
                    s.etage
                FROM capteur c
                JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s
            """
            
            capteur_cree = execute_single_query(capteur_cree_query, (capteur_id,))
            
            return capteur_cree
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'ajout du capteur: {str(e)}")


    def reactiver_capteur(self, capteur_id):
        """
        Réactiver un capteur désactivé (fonction d'administration)
        
        Args:
            capteur_id (int): ID du capteur à réactiver
            
        Returns:
            dict: Informations du capteur réactivé
        """
        try:
            capteur_query = """
                SELECT c.id, c.nom, c.type_capteur, c.id_salle, c.is_active, s.nom as salle_nom
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s
            """
            capteur = execute_single_query(capteur_query, (capteur_id,))
            
            if not capteur:
                raise Exception(f"Capteur {capteur_id} introuvable")
                
            if capteur['is_active']:
                raise Exception(f"Le capteur {capteur_id} est déjà actif")
            
            if capteur['id_salle'] is not None:
                conflit_query = """
                    SELECT id FROM capteur 
                    WHERE id_salle = %s AND type_capteur = %s AND is_active = TRUE AND id != %s
                """
                conflit = execute_single_query(conflit_query, (capteur['id_salle'], capteur['type_capteur'], capteur_id))
                
                if conflit:
                    raise Exception(f"Un capteur de type '{capteur['type_capteur']}' est déjà actif dans cette salle")
            
            update_query = """
                UPDATE capteur 
                SET is_active = TRUE 
                WHERE id = %s
            """
            
            with engine.connect() as conn:
                param_dict = {'param_0': capteur_id}
                query_with_params = update_query.replace('%s', ':param_0')
                conn.execute(text(query_with_params), param_dict)
                conn.commit()
            
            capteur['is_active'] = True
            return capteur
            
        except Exception as e:
            raise Exception(f"Erreur lors de la réactivation du capteur: {str(e)}")

    def supprimer_capteur(self, capteur_id):
        """
        Supprimer définitivement un capteur (fonction d'administration critique)
        
        Args:
            capteur_id (int): ID du capteur à supprimer
            
        Returns:
            bool: True si succès
        """
        try:
            capteur_query = """
                SELECT c.id, c.nom, c.type_capteur, s.nom as salle_nom
                FROM capteur c
                LEFT JOIN salle s ON c.id_salle = s.id
                WHERE c.id = %s
            """
            capteur = execute_single_query(capteur_query, (capteur_id,))
            
            if not capteur:
                raise Exception(f"Capteur {capteur_id} introuvable")
            
            delete_temp_query = "DELETE FROM temperature WHERE capteur_id = %s"
            delete_hum_query = "DELETE FROM humidite WHERE capteur_id = %s"
            delete_press_query = "DELETE FROM pression WHERE capteur_id = %s"
            delete_capteur_query = "DELETE FROM capteur WHERE id = %s"
            
            with engine.connect() as conn:
                for query in [delete_temp_query, delete_hum_query, delete_press_query]:
                    param_dict = {'param_0': capteur_id}
                    query_with_params = query.replace('%s', ':param_0')
                    conn.execute(text(query_with_params), param_dict)
                
                param_dict = {'param_0': capteur_id}
                query_with_params = delete_capteur_query.replace('%s', ':param_0')
                conn.execute(text(query_with_params), param_dict)
                
                conn.commit()
            
            return True
            
        except Exception as e:
            raise Exception(f"Erreur lors de la suppression du capteur: {str(e)}")

admin_service = AdminService()