from app.queries import execute_query, execute_single_query
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
            
            # Récupérer la date d'installation pour filtrer les données
            date_installation = capteur.get('date_installation')
            
            if type_capteur == 'temperature':
                temp_query = """
                    SELECT valeur, unite, date_update
                    FROM temperature
                    WHERE capteur_id = %s AND date_update >= %s
                    ORDER BY date_update DESC
                    LIMIT %s
                """
                donnees = execute_query(temp_query, (capteur_id, date_installation, limit))
                
            elif type_capteur == 'humidite':
                hum_query = """
                    SELECT valeur, unite, date_update
                    FROM humidite
                    WHERE capteur_id = %s AND date_update >= %s
                    ORDER BY date_update DESC
                    LIMIT %s
                """
                donnees = execute_query(hum_query, (capteur_id, date_installation, limit))
                
            elif type_capteur == 'pression':
                press_query = """
                    SELECT valeur, unite, date_update
                    FROM pression
                    WHERE capteur_id = %s AND date_update >= %s
                    ORDER BY date_update DESC
                    LIMIT %s
                """
                donnees = execute_query(press_query, (capteur_id, date_installation, limit))
            
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

    def get_derniere_mesure_date_by_salle(self, salle_id):
        """
        Récupérer la date de dernière mesure pour une salle (toutes mesures confondues)
        
        Args:
            salle_id (int): ID de la salle
            
        Returns:
            datetime: Date de la dernière mesure ou None
        """
        try:
            query = """
                SELECT MAX(derniere_mesure) as derniere_mesure_globale
                FROM (
                    SELECT MAX(t.date_update) as derniere_mesure
                    FROM capteur c
                    JOIN temperature t ON c.id = t.capteur_id
                    WHERE c.id_salle = %s AND c.is_active = TRUE
                    
                    UNION ALL
                    
                    SELECT MAX(h.date_update) as derniere_mesure
                    FROM capteur c
                    JOIN humidite h ON c.id = h.capteur_id
                    WHERE c.id_salle = %s AND c.is_active = TRUE
                    
                    UNION ALL
                    
                    SELECT MAX(p.date_update) as derniere_mesure
                    FROM capteur c
                    JOIN pression p ON c.id = p.capteur_id
                    WHERE c.id_salle = %s AND c.is_active = TRUE
                ) AS toutes_mesures
            """
            
            result = execute_single_query(query, (salle_id, salle_id, salle_id))
            return result['derniere_mesure_globale'] if result else None
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de la dernière mesure pour la salle {salle_id}: {str(e)}")

    def verifier_conformite_salles(self, limit=10):
        """
        Vérifier la conformité de toutes les salles actives
        Calcule les moyennes et compare avec les seuils de conformité
        
        Args:
            limit (int): Nombre de dernières mesures pour calculer la moyenne
            
        Returns:
            list: Liste des salles avec leur statut de conformité
        """
        try:
            # 1. Récupérer toutes les salles actives
            salles = self.get_salles_actives()
            
            if not salles:
                return []
            
            resultats = []
            
            for salle in salles:
                salle_id = salle['id']
                
                # 2. Calculer les moyennes pour cette salle
                moyennes = self.get_moyennes_dernieres_donnees_by_salle(salle_id, limit)
                
                # Récupérer les capteurs de la salle (pour tous les cas)
                capteurs_salle = self.get_capteurs_by_salle(salle_id)
                noms_capteurs = list(set([capteur['nom'] for capteur in capteurs_salle])) if capteurs_salle else []
                
                # Récupérer la date de dernière mesure pour cette salle
                derniere_mesure_date = self.get_derniere_mesure_date_by_salle(salle_id)
                
                if not moyennes:
                    # Pas de données pour cette salle
                    resultats.append({
                        'salle': salle,
                        'moyennes': None,
                        'conformite': None,
                        'statut': 'AUCUNE_DONNEE',
                        'alertes': ['Aucune donnée de capteur disponible'],
                        'capteurs': noms_capteurs,
                        'derniere_mesure_date': derniere_mesure_date
                    })
                    continue
                
                # 3. Récupérer les seuils de conformité pour cette salle
                conformite = self.get_seuils_conformite_by_salle(salle_id)
                
                if not conformite:
                    # Pas de seuils définis pour cette salle
                    resultats.append({
                        'salle': salle,
                        'moyennes': moyennes,
                        'conformite': None,
                        'statut': 'SEUILS_NON_DEFINIS',
                        'alertes': ['Seuils de conformité non définis'],
                        'capteurs': noms_capteurs,
                        'derniere_mesure_date': derniere_mesure_date
                    })
                    continue
                
                # 4. Vérifier la conformité
                verification = self.verifier_seuils(moyennes, conformite)
                
                resultats.append({
                    'salle': salle,
                    'moyennes': moyennes,
                    'conformite': conformite,
                    'statut': verification['statut'],
                    'alertes': verification['alertes'],
                    'capteurs': noms_capteurs,  # Noms uniques des capteurs
                    'derniere_mesure_date': derniere_mesure_date,  # Date de dernière mesure
                    'details_verification': {
                        'details': verification['details'],
                        'score_conformite': verification['score_conformite'],
                        'niveau_conformite': verification['niveau_conformite'],
                        'parametres_testes': verification['parametres_testes'],
                        'parametres_non_conformes': verification['parametres_non_conformes'],
                        'pourcentage_conformite': verification['pourcentage_conformite']
                    }
                })
            
            return resultats
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification de conformité: {str(e)}")

    def get_seuils_conformite_by_salle(self, salle_id):
        """
        Récupérer les seuils de conformité actifs pour une salle
        
        Args:
            salle_id (int): ID de la salle
            
        Returns:
            dict: Seuils de conformité ou None si aucun seuil défini
        """
        try:
            query = """
                SELECT 
                    id,
                    salle_id,
                    temperature_haute,
                    temperature_basse,
                    humidite_haute,
                    humidite_basse,
                    pression_haute,
                    pression_basse,
                    date_debut,
                    date_fin
                FROM conformite
                WHERE salle_id = %s 
                AND (date_fin IS NULL OR date_fin > NOW())
                ORDER BY date_debut DESC
                LIMIT 1
            """
            
            return execute_single_query(query, (salle_id,))
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des seuils de conformité pour la salle {salle_id}: {str(e)}")

    def verifier_seuils(self, moyennes, conformite):
        """
        Vérifier si les moyennes respectent les seuils de conformité
        
        Args:
            moyennes (dict): Moyennes calculées
            conformite (dict): Seuils de conformité
            
        Returns:
            dict: Résultat de la vérification avec score de conformité
        """
        alertes = []
        details = {}
        score_conformite = 1  # Score de base : tout est conforme
        parametres_testes = 0
        parametres_non_conformes = 0
        
        # Vérification température
        if moyennes.get('moyenne_temperature') is not None:
            parametres_testes += 1
            temp = float(moyennes['moyenne_temperature'])
            temp_min = float(conformite['temperature_basse']) if conformite['temperature_basse'] else None
            temp_max = float(conformite['temperature_haute']) if conformite['temperature_haute'] else None
            
            conforme_temp = True
            if temp_min is not None and temp < temp_min:
                alertes.append(f"Température trop basse: {temp}°C < {temp_min}°C")
                conforme_temp = False
                parametres_non_conformes += 1
            if temp_max is not None and temp > temp_max:
                alertes.append(f"Température trop élevée: {temp}°C > {temp_max}°C")
                conforme_temp = False
                parametres_non_conformes += 1
                
            details['temperature'] = {
                'valeur': temp,
                'seuil_min': temp_min,
                'seuil_max': temp_max,
                'conforme': conforme_temp
            }
        
        # Vérification humidité
        if moyennes.get('moyenne_humidite') is not None:
            parametres_testes += 1
            hum = float(moyennes['moyenne_humidite'])
            hum_min = float(conformite['humidite_basse']) if conformite['humidite_basse'] else None
            hum_max = float(conformite['humidite_haute']) if conformite['humidite_haute'] else None
            
            conforme_hum = True
            if hum_min is not None and hum < hum_min:
                alertes.append(f"Humidité trop basse: {hum}% < {hum_min}%")
                conforme_hum = False
                parametres_non_conformes += 1
            if hum_max is not None and hum > hum_max:
                alertes.append(f"Humidité trop élevée: {hum}% > {hum_max}%")
                conforme_hum = False
                parametres_non_conformes += 1
                
            details['humidite'] = {
                'valeur': hum,
                'seuil_min': hum_min,
                'seuil_max': hum_max,
                'conforme': conforme_hum
            }
        
        # Vérification pression
        if moyennes.get('moyenne_pression') is not None:
            parametres_testes += 1
            pres = float(moyennes['moyenne_pression'])
            pres_min = float(conformite['pression_basse']) if conformite['pression_basse'] else None
            pres_max = float(conformite['pression_haute']) if conformite['pression_haute'] else None
            
            conforme_pres = True
            if pres_min is not None and pres < pres_min:
                alertes.append(f"Pression trop basse: {pres}hPa < {pres_min}hPa")
                conforme_pres = False
                parametres_non_conformes += 1
            if pres_max is not None and pres > pres_max:
                alertes.append(f"Pression trop élevée: {pres}hPa > {pres_max}hPa")
                conforme_pres = False
                parametres_non_conformes += 1
                
            details['pression'] = {
                'valeur': pres,
                'seuil_min': pres_min,
                'seuil_max': pres_max,
                'conforme': conforme_pres
            }
        
        # Calcul du score de conformité basé sur le pourcentage de paramètres non conformes
        if parametres_testes > 0:
            pourcentage_non_conforme = (parametres_non_conformes / parametres_testes) * 100
            
            if pourcentage_non_conforme == 0:
                score_conformite = 1  # Excellent : 100% conforme
                niveau_conformite = "EXCELLENT"
            elif pourcentage_non_conforme < 50:
                score_conformite = 2  # Bon : moins de 50% non conforme
                niveau_conformite = "BON"
            elif pourcentage_non_conforme < 75:
                score_conformite = 3  # Moyen : 50-74% non conforme
                niveau_conformite = "MOYEN"
            else:
                score_conformite = 4  # Mauvais : 75%+ non conforme
                niveau_conformite = "MAUVAIS"
        else:
            # Aucun paramètre testé
            score_conformite = 1
            niveau_conformite = "EXCELLENT"
        
        # Déterminer le statut global
        if not alertes:
            statut = 'CONFORME'
        else:
            statut = 'NON_CONFORME'
        
        return {
            'statut': statut,
            'alertes': alertes,
            'details': details,
            'score_conformite': score_conformite,
            'niveau_conformite': niveau_conformite,
            'parametres_testes': parametres_testes,
            'parametres_non_conformes': parametres_non_conformes,
            'pourcentage_conformite': round((parametres_testes - parametres_non_conformes) / parametres_testes * 100, 1) if parametres_testes > 0 else 100.0
        }


# Instance globale du service
capteur_service = CapteurService() 