#!/usr/bin/env python3
"""
Tests unitaires pour le service capteur
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire src au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.capteur_service import CapteurService


class TestCapteurService:
    """Tests pour le service de gestion des capteurs"""
    
    def setup_method(self):
        """Setup avant chaque test"""  
        print("\n" + "="*50)
        print("DÉBUT DES TESTS CAPTEUR SERVICE")  
        print("="*50)
        self.service = CapteurService()
        
        # Mock des données de test
        self.mock_salle = {
            'id': 1,
            'nom': 'A01',
            'batiment': 'A',
            'etage': 0,
            'capacite': 30,
            'etat': 'active'
        }
        
        self.mock_capteur = {
            'id': 1,
            'nom': '305822513',
            'type_capteur': 'temperature',
            'id_salle': 1,
            'date_installation': '2025-01-01 10:00:00',
            'is_active': True,
            'salle_nom': 'A01'
        }
        
        self.mock_temperature = {
            'capteur_id': 1,
            'nom': '305822513',
            'valeur': 25.5,
            'unite': '°C',
            'date_update': '2025-01-01 12:00:00',
            'salle_nom': 'A01',
            'batiment': 'A',
            'etage': 0
        }

    @patch('services.capteur_service.execute_query')
    def test_get_salles_actives_success(self, mock_execute_query):
        """Test récupération des salles actives - succès"""
        print("TEST: Récupération salles actives - DÉBUT")
        # Arrange
        mock_execute_query.return_value = [self.mock_salle]
        
        # Act
        result = self.service.get_salles_actives()
        
        # Assert
        assert result == [self.mock_salle]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "SELECT id, nom, batiment, etage, capacite, date_creation" in call_args[0]
        assert "WHERE etat = 'active'" in call_args[0]
        print("TEST: Récupération salles actives - RÉUSSI")

    @patch('services.capteur_service.execute_query')
    def test_get_salles_actives_empty(self, mock_execute_query):
        """Test récupération des salles actives - aucune salle"""
        # Arrange
        mock_execute_query.return_value = []
        
        # Act
        result = self.service.get_salles_actives()
        
        # Assert
        assert result == []

    @patch('services.capteur_service.execute_query')
    def test_get_salles_actives_exception(self, mock_execute_query):
        """Test récupération des salles actives - exception"""
        # Arrange
        mock_execute_query.side_effect = Exception("Erreur DB")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.get_salles_actives()
        assert "Erreur lors de la récupération des salles" in str(exc_info.value)

    @patch('services.capteur_service.execute_query')
    def test_get_capteurs_by_salle_success(self, mock_execute_query):
        """Test récupération des capteurs d'une salle - succès"""
        # Arrange
        mock_execute_query.return_value = [self.mock_capteur]
        
        # Act
        result = self.service.get_capteurs_by_salle(1)
        
        # Assert
        assert result == [self.mock_capteur]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "WHERE c.id_salle = %s AND c.is_active = TRUE" in call_args[0]
        assert call_args[1] == (1,)

    @patch('services.capteur_service.execute_single_query')
    def test_get_moyennes_dernieres_donnees_by_salle_success(self, mock_execute_single_query):
        """Test récupération des moyennes - succès"""
        # Arrange
        mock_moyennes = {
            'salle_id': 1,
            'salle_nom': 'A01',
            'batiment': 'A',
            'etage': 0,
            'moyenne_temperature': 25.5,
            'moyenne_humidite': 60.2,
            'moyenne_pression': 1013.25,
            'unite_temperature': '°C',
            'unite_humidite': '%',
            'unite_pression': 'hPa'
        }
        mock_execute_single_query.return_value = mock_moyennes
        
        # Act
        result = self.service.get_moyennes_dernieres_donnees_by_salle(1, 10)
        
        # Assert
        assert result == mock_moyennes
        mock_execute_single_query.assert_called_once()
        call_args = mock_execute_single_query.call_args[0]
        assert "AVG(t_data.valeur) as moyenne_temperature" in call_args[0]
        assert call_args[1] == (10, 10, 10, 1)

    @patch('services.capteur_service.execute_single_query')
    def test_get_moyennes_dernieres_donnees_by_salle_not_found(self, mock_execute_single_query):
        """Test récupération des moyennes - salle introuvable"""
        # Arrange
        mock_execute_single_query.return_value = None
        
        # Act
        result = self.service.get_moyennes_dernieres_donnees_by_salle(999, 10)
        
        # Assert
        assert result is None

    @patch('services.capteur_service.execute_query')
    def test_get_temperature_by_salle_success(self, mock_execute_query):
        """Test récupération des températures d'une salle - succès"""
        # Arrange
        mock_execute_query.return_value = [self.mock_temperature]
        
        # Act
        result = self.service.get_temperature_by_salle(1, 5)
        
        # Assert
        assert result == [self.mock_temperature]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "JOIN temperature t ON c.id = t.capteur_id" in call_args[0]
        assert "WHERE s.id = %s AND c.type_capteur = 'temperature'" in call_args[0]
        assert call_args[1] == (1, 5)

    @patch('services.capteur_service.execute_query')
    def test_get_humidite_by_salle_success(self, mock_execute_query):
        """Test récupération de l'humidité d'une salle - succès"""
        # Arrange
        mock_humidite = {
            'capteur_id': 2,
            'nom': '305822514',
            'valeur': 65.0,
            'unite': '%',
            'date_update': '2025-01-01 12:00:00',
            'salle_nom': 'A01',
            'batiment': 'A',
            'etage': 0
        }
        mock_execute_query.return_value = [mock_humidite]
        
        # Act
        result = self.service.get_humidite_by_salle(1, 5)
        
        # Assert
        assert result == [mock_humidite]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "JOIN humidite h ON c.id = h.capteur_id" in call_args[0]
        assert "WHERE s.id = %s AND c.type_capteur = 'humidite'" in call_args[0]

    @patch('services.capteur_service.execute_query')
    def test_get_pression_by_salle_success(self, mock_execute_query):
        """Test récupération de la pression d'une salle - succès"""
        # Arrange
        mock_pression = {
            'capteur_id': 3,
            'nom': '305822515',
            'valeur': 1013.25,
            'unite': 'hPa',
            'date_update': '2025-01-01 12:00:00',
            'salle_nom': 'A01',
            'batiment': 'A',
            'etage': 0
        }
        mock_execute_query.return_value = [mock_pression]
        
        # Act
        result = self.service.get_pression_by_salle(1, 5)
        
        # Assert
        assert result == [mock_pression]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "JOIN pression p ON c.id = p.capteur_id" in call_args[0]
        assert "WHERE s.id = %s AND c.type_capteur = 'pression'" in call_args[0]

    @patch('services.capteur_service.execute_query')
    def test_get_temperature_by_capteur_success(self, mock_execute_query):
        """Test récupération des températures d'un capteur - succès"""
        # Arrange
        mock_execute_query.return_value = [self.mock_temperature]
        
        # Act
        result = self.service.get_temperature_by_capteur(1, 10)
        
        # Assert
        assert result == [self.mock_temperature]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "FROM temperature t" in call_args[0]
        assert "WHERE c.id = %s AND c.is_active = TRUE" in call_args[0]
        assert call_args[1] == (1, 10)

    @patch('services.capteur_service.execute_single_query')
    @patch('services.capteur_service.execute_query')
    def test_get_dernieres_donnees_by_capteur_success(self, mock_execute_query, mock_execute_single_query):
        """Test récupération des données d'un capteur - succès"""
        # Arrange
        mock_execute_single_query.return_value = self.mock_capteur
        mock_donnees = [
            {
                'valeur': 25.5,
                'unite': '°C',
                'date_update': '2025-01-01 12:00:00'
            }
        ]
        mock_execute_query.return_value = mock_donnees
        
        # Act
        result = self.service.get_dernieres_donnees_by_capteur(1, 2)
        
        # Assert
        assert result['capteur'] == self.mock_capteur
        assert result['donnees'] == mock_donnees
        assert mock_execute_single_query.call_count == 1
        assert mock_execute_query.call_count == 1

    @patch('services.capteur_service.execute_single_query')
    def test_get_dernieres_donnees_by_capteur_not_found(self, mock_execute_single_query):
        """Test récupération des données d'un capteur - capteur introuvable"""
        # Arrange
        mock_execute_single_query.return_value = None
        
        # Act
        result = self.service.get_dernieres_donnees_by_capteur(999, 2)
        
        # Assert
        assert result is None

    @patch('services.capteur_service.execute_single_query')
    @patch('services.capteur_service.execute_query')
    def test_get_dernieres_donnees_by_capteur_humidite(self, mock_execute_query, mock_execute_single_query):
        """Test récupération des données d'un capteur humidité"""
        # Arrange
        capteur_humidite = self.mock_capteur.copy()
        capteur_humidite['type_capteur'] = 'humidite'
        mock_execute_single_query.return_value = capteur_humidite
        
        mock_donnees = [
            {
                'valeur': 65.0,
                'unite': '%',
                'date_update': '2025-01-01 12:00:00'
            }
        ]
        mock_execute_query.return_value = mock_donnees
        
        # Act
        result = self.service.get_dernieres_donnees_by_capteur(1, 2)
        
        # Assert
        assert result['capteur']['type_capteur'] == 'humidite'
        assert result['donnees'] == mock_donnees
        # Vérifier que la requête humidité a été appelée
        call_args = mock_execute_query.call_args[0]
        assert "FROM humidite" in call_args[0]

    @patch('services.capteur_service.execute_single_query')
    @patch('services.capteur_service.execute_query')
    def test_get_dernieres_donnees_by_capteur_pression(self, mock_execute_query, mock_execute_single_query):
        """Test récupération des données d'un capteur pression"""
        # Arrange
        capteur_pression = self.mock_capteur.copy()
        capteur_pression['type_capteur'] = 'pression'
        mock_execute_single_query.return_value = capteur_pression
        
        mock_donnees = [
            {
                'valeur': 1013.25,
                'unite': 'hPa',
                'date_update': '2025-01-01 12:00:00'
            }
        ]
        mock_execute_query.return_value = mock_donnees
        
        # Act
        result = self.service.get_dernieres_donnees_by_capteur(1, 2)
        
        # Assert
        assert result['capteur']['type_capteur'] == 'pression'
        assert result['donnees'] == mock_donnees
        # Vérifier que la requête pression a été appelée
        call_args = mock_execute_query.call_args[0]
        assert "FROM pression" in call_args[0]

    def test_parametres_par_defaut(self):
        """Test des paramètres par défaut des méthodes"""
        with patch('services.capteur_service.execute_single_query') as mock_single:
            mock_single.return_value = {'test': 'data'}
            
            # Test limite par défaut pour moyennes
            self.service.get_moyennes_dernieres_donnees_by_salle(1)
            call_args = mock_single.call_args[0]
            assert call_args[1] == (10, 10, 10, 1)  # limit par défaut = 10

        with patch('services.capteur_service.execute_query') as mock_query:
            mock_query.return_value = []
            
            # Test limite par défaut pour température
            self.service.get_temperature_by_salle(1)
            call_args = mock_query.call_args[0]
            assert call_args[1] == (1, 10)  # limit par défaut = 10

    # ========== TESTS VERIFICATION CONFORMITE ==========
    
    @patch('services.capteur_service.execute_single_query')
    def test_get_seuils_conformite_by_salle_success(self, mock_execute_single_query):
        """Test récupération des seuils de conformité - succès"""
        # Arrange
        mock_conformite = {
            'id': 1,
            'salle_id': 1,
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0,
            'date_debut': '2025-01-01 00:00:00',
            'date_fin': None
        }
        mock_execute_single_query.return_value = mock_conformite
        
        # Act
        result = self.service.get_seuils_conformite_by_salle(1)
        
        # Assert
        assert result == mock_conformite
        mock_execute_single_query.assert_called_once()
        call_args = mock_execute_single_query.call_args[0]
        assert "FROM conformite" in call_args[0]
        assert "WHERE salle_id = %s" in call_args[0]
        assert "date_fin IS NULL OR date_fin > NOW()" in call_args[0]
        assert call_args[1] == (1,)

    @patch('services.capteur_service.execute_single_query')
    def test_get_seuils_conformite_by_salle_not_found(self, mock_execute_single_query):
        """Test récupération des seuils de conformité - aucun seuil"""
        # Arrange
        mock_execute_single_query.return_value = None
        
        # Act
        result = self.service.get_seuils_conformite_by_salle(999)
        
        # Assert
        assert result is None

    def test_verifier_seuils_conforme(self):
        """Test vérification des seuils - toutes valeurs conformes"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1013.0
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['statut'] == 'CONFORME'
        assert result['alertes'] == []
        assert result['details']['temperature']['conforme'] is True
        assert result['details']['humidite']['conforme'] is True
        assert result['details']['pression']['conforme'] is True
        assert result['score_conformite'] == 1
        assert result['niveau_conformite'] == "EXCELLENT"

    def test_verifier_seuils_temperature_trop_haute(self):
        """Test vérification des seuils - température trop élevée"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 30.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1013.0
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['statut'] == 'NON_CONFORME'
        assert len(result['alertes']) == 1
        assert 'Température trop élevée: 30.0°C > 28.0°C' in result['alertes'][0]
        assert result['details']['temperature']['conforme'] is False
        assert result['details']['humidite']['conforme'] is True
        assert result['score_conformite'] == 2  # 1 paramètre sur 3 non conforme
        assert result['niveau_conformite'] == "BON"

    def test_verifier_seuils_humidite_trop_basse(self):
        """Test vérification des seuils - humidité trop basse"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 30.0,
            'moyenne_pression': 1013.0
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['statut'] == 'NON_CONFORME'
        assert 'Humidité trop basse: 30.0% < 40.0%' in result['alertes'][0]
        assert result['details']['humidite']['conforme'] is False

    def test_verifier_seuils_pression_trop_haute(self):
        """Test vérification des seuils - pression trop élevée"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1025.0
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['statut'] == 'NON_CONFORME'
        assert 'Pression trop élevée: 1025.0hPa > 1020.0hPa' in result['alertes'][0]
        assert result['details']['pression']['conforme'] is False

    def test_verifier_seuils_multiples_alertes(self):
        """Test vérification des seuils - plusieurs alertes"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 15.0,  # Trop basse
            'moyenne_humidite': 80.0,     # Trop haute
            'moyenne_pression': 990.0     # Trop basse
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['statut'] == 'NON_CONFORME'
        assert len(result['alertes']) == 3
        assert any('Température trop basse' in alerte for alerte in result['alertes'])
        assert any('Humidité trop élevée' in alerte for alerte in result['alertes'])
        assert any('Pression trop basse' in alerte for alerte in result['alertes'])

    def test_verifier_seuils_avec_seuils_null(self):
        """Test vérification des seuils - certains seuils non définis"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1013.0
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': None,  # Seuil non défini
            'humidite_haute': None,     # Seuil non défini
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['statut'] == 'CONFORME'
        assert result['details']['temperature']['seuil_min'] is None
        assert result['details']['humidite']['seuil_max'] is None

    @patch('services.capteur_service.CapteurService.get_seuils_conformite_by_salle')
    @patch('services.capteur_service.CapteurService.get_moyennes_dernieres_donnees_by_salle')
    @patch('services.capteur_service.CapteurService.get_salles_actives')
    def test_verifier_conformite_salles_success(self, mock_get_salles, mock_get_moyennes, mock_get_seuils):
        """Test vérification conformité de toutes les salles - succès"""
        # Arrange
        mock_get_salles.return_value = [self.mock_salle]
        mock_get_moyennes.return_value = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1013.0
        }
        mock_get_seuils.return_value = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_conformite_salles(5)
        
        # Assert
        assert len(result) == 1
        assert result[0]['salle'] == self.mock_salle
        assert result[0]['statut'] == 'CONFORME'
        assert result[0]['alertes'] == []
        mock_get_moyennes.assert_called_once_with(1, 5)
        mock_get_seuils.assert_called_once_with(1)

    @patch('services.capteur_service.CapteurService.get_seuils_conformite_by_salle')
    @patch('services.capteur_service.CapteurService.get_moyennes_dernieres_donnees_by_salle')
    @patch('services.capteur_service.CapteurService.get_salles_actives')
    def test_verifier_conformite_salles_aucune_donnee(self, mock_get_salles, mock_get_moyennes, mock_get_seuils):
        """Test vérification conformité - aucune donnée"""
        # Arrange
        mock_get_salles.return_value = [self.mock_salle]
        mock_get_moyennes.return_value = None
        
        # Act
        result = self.service.verifier_conformite_salles()
        
        # Assert
        assert len(result) == 1
        assert result[0]['statut'] == 'AUCUNE_DONNEE'
        assert 'Aucune donnée de capteur disponible' in result[0]['alertes']
        mock_get_seuils.assert_not_called()

    @patch('services.capteur_service.CapteurService.get_seuils_conformite_by_salle')
    @patch('services.capteur_service.CapteurService.get_moyennes_dernieres_donnees_by_salle')
    @patch('services.capteur_service.CapteurService.get_salles_actives')
    def test_verifier_conformite_salles_seuils_non_definis(self, mock_get_salles, mock_get_moyennes, mock_get_seuils):
        """Test vérification conformité - seuils non définis"""
        # Arrange
        mock_get_salles.return_value = [self.mock_salle]
        mock_get_moyennes.return_value = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0
        }
        mock_get_seuils.return_value = None
        
        # Act
        result = self.service.verifier_conformite_salles()
        
        # Assert
        assert len(result) == 1
        assert result[0]['statut'] == 'SEUILS_NON_DEFINIS'
        assert 'Seuils de conformité non définis' in result[0]['alertes']

    @patch('services.capteur_service.CapteurService.get_salles_actives')
    def test_verifier_conformite_salles_aucune_salle(self, mock_get_salles):
        """Test vérification conformité - aucune salle active"""
        # Arrange
        mock_get_salles.return_value = []
        
        # Act
        result = self.service.verifier_conformite_salles()
        
        # Assert
        assert result == []

    @patch('services.capteur_service.CapteurService.get_salles_actives')
    def test_verifier_conformite_salles_exception(self, mock_get_salles):
        """Test vérification conformité - exception"""
        # Arrange
        mock_get_salles.side_effect = Exception("Erreur DB")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.verifier_conformite_salles()
        assert "Erreur lors de la vérification de conformité" in str(exc_info.value)

    # ========== TESTS SYSTEME DE SCORING ==========
    
    def test_scoring_excellent_tout_conforme(self):
        """Test scoring - Score 1 (EXCELLENT) : tous paramètres conformes"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1013.0
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['score_conformite'] == 1
        assert result['niveau_conformite'] == "EXCELLENT"
        assert result['parametres_testes'] == 3
        assert result['parametres_non_conformes'] == 0
        assert result['pourcentage_conformite'] == 100.0

    def test_scoring_bon_un_parametre_non_conforme(self):
        """Test scoring - Score 2 (BON) : 1 paramètre sur 3 non conforme (33% < 50%)"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 30.0,  # Non conforme
            'moyenne_humidite': 60.0,     # Conforme
            'moyenne_pression': 1013.0    # Conforme
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['score_conformite'] == 2
        assert result['niveau_conformite'] == "BON"
        assert result['parametres_testes'] == 3
        assert result['parametres_non_conformes'] == 1
        assert result['pourcentage_conformite'] == 66.7

    def test_scoring_moyen_deux_parametres_non_conformes(self):
        """Test scoring - Score 3 (MOYEN) : 2 paramètres sur 3 non conformes (66% < 75%)"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 30.0,  # Non conforme
            'moyenne_humidite': 80.0,     # Non conforme
            'moyenne_pression': 1013.0    # Conforme
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['score_conformite'] == 3
        assert result['niveau_conformite'] == "MOYEN"
        assert result['parametres_testes'] == 3
        assert result['parametres_non_conformes'] == 2
        assert result['pourcentage_conformite'] == 33.3

    def test_scoring_mauvais_tous_parametres_non_conformes(self):
        """Test scoring - Score 4 (MAUVAIS) : tous paramètres non conformes (100%)"""
        # Arrange
        moyennes = {
            'moyenne_temperature': 35.0,  # Non conforme (trop haute)
            'moyenne_humidite': 20.0,     # Non conforme (trop basse)
            'moyenne_pression': 950.0     # Non conforme (trop basse)
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['score_conformite'] == 4
        assert result['niveau_conformite'] == "MAUVAIS"
        assert result['parametres_testes'] == 3
        assert result['parametres_non_conformes'] == 3
        assert result['pourcentage_conformite'] == 0.0

    def test_scoring_avec_un_seul_parametre(self):
        """Test scoring avec un seul paramètre disponible"""
        # Arrange - Seulement température
        moyennes = {
            'moyenne_temperature': 30.0  # Non conforme
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0
        }
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['score_conformite'] == 4  # 100% non conforme
        assert result['niveau_conformite'] == "MAUVAIS"
        assert result['parametres_testes'] == 1
        assert result['parametres_non_conformes'] == 1

    def test_scoring_aucun_parametre(self):
        """Test scoring sans aucun paramètre à tester"""
        # Arrange
        moyennes = {}
        conformite = {}
        
        # Act
        result = self.service.verifier_seuils(moyennes, conformite)
        
        # Assert
        assert result['score_conformite'] == 1
        assert result['niveau_conformite'] == "EXCELLENT"
        assert result['parametres_testes'] == 0
        assert result['parametres_non_conformes'] == 0
        assert result['pourcentage_conformite'] == 100.0

    def test_scoring_seuils_limites(self):
        """Test des seuils exacts pour le calcul du score"""
        # Test limite entre BON (2) et MOYEN (3) : exactement 50%
        moyennes = {
            'moyenne_temperature': 30.0,  # Non conforme
            'moyenne_humidite': 60.0      # Conforme
        }
        conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0
        }
        
        result = self.service.verifier_seuils(moyennes, conformite)
        assert result['score_conformite'] == 3  # 50% non conforme = MOYEN
        
        # Test limite entre MOYEN (3) et MAUVAIS (4) : exactement 75%
        moyennes_limite = {
            'moyenne_temperature': 30.0,  # Non conforme
            'moyenne_humidite': 80.0,     # Non conforme  
            'moyenne_pression': 950.0,    # Non conforme
            'moyenne_co2': 25.0           # Conforme (ajouté pour avoir 75%)
        }
        conformite_limite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0,
            'co2_max': 30.0
        }
        
        # Note: Ce test ne fonctionnera pas car notre service ne gère que temp/hum/pression
        # Testons plutôt avec 3 paramètres où 3/4 = 75%