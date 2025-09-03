#!/usr/bin/env python3
"""
Tests unitaires pour les routes des capteurs
"""
import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Ajouter le répertoire src au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from routes.capteurs import capteurs_bp


class TestRoutesCapteurs:
    """Tests pour les routes des capteurs"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.app = Flask(__name__)
        self.app.register_blueprint(capteurs_bp, url_prefix='/api/capteurs')
        self.client = self.app.test_client()
        
        # Mock des données de test
        self.mock_salles = [
            {'id': 1, 'nom': 'A01', 'batiment': 'A', 'etage': 0},
            {'id': 2, 'nom': 'A02', 'batiment': 'A', 'etage': 0}
        ]
        
        self.mock_capteurs = [
            {'id': 1, 'nom': '305822513', 'type_capteur': 'temperature'},
            {'id': 2, 'nom': '305822514', 'type_capteur': 'humidite'}
        ]
        
        self.mock_moyennes = {
            'salle_id': 1,
            'salle_nom': 'A01',
            'moyenne_temperature': 25.5,
            'moyenne_humidite': 60.2,
            'moyenne_pression': 1013.25,
            'unite_temperature': '°C',
            'unite_humidite': '%',
            'unite_pression': 'hPa'
        }

    # ========== TESTS GET SALLES ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_salles_success(self, mock_service):
        """Test GET /api/capteurs/salles - succès"""
        # Arrange
        mock_service.get_salles_actives.return_value = self.mock_salles
        
        # Act
        response = self.client.get('/api/capteurs/salles')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == self.mock_salles
        assert 'Salles récupérées avec succès' in data['message']

    @patch('routes.capteurs.capteur_service')
    def test_get_salles_empty(self, mock_service):
        """Test GET /api/capteurs/salles - aucune salle"""
        # Arrange
        mock_service.get_salles_actives.return_value = []
        
        # Act
        response = self.client.get('/api/capteurs/salles')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []

    @patch('routes.capteurs.capteur_service')
    def test_get_salles_exception(self, mock_service):
        """Test GET /api/capteurs/salles - exception"""
        # Arrange
        mock_service.get_salles_actives.side_effect = Exception("Erreur DB")
        
        # Act
        response = self.client.get('/api/capteurs/salles')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Erreur DB' in data['message']

    # ========== TESTS GET CAPTEURS BY SALLE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_capteurs_by_salle_success(self, mock_service):
        """Test GET /api/capteurs/salles/:id/capteurs - succès"""
        # Arrange
        mock_service.get_capteurs_by_salle.return_value = self.mock_capteurs
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/capteurs')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == self.mock_capteurs
        mock_service.get_capteurs_by_salle.assert_called_once_with(1)

    @patch('routes.capteurs.capteur_service')
    def test_get_capteurs_by_salle_not_found(self, mock_service):
        """Test GET /api/capteurs/salles/:id/capteurs - salle inexistante"""
        # Arrange
        mock_service.get_capteurs_by_salle.return_value = []
        
        # Act
        response = self.client.get('/api/capteurs/salles/999/capteurs')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []

    # ========== TESTS GET MOYENNES ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_moyennes_by_salle_success(self, mock_service):
        """Test GET /api/capteurs/salles/:id/moyennes - succès"""
        # Arrange
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = self.mock_moyennes
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/moyennes')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == self.mock_moyennes
        mock_service.get_moyennes_dernieres_donnees_by_salle.assert_called_once_with(1, 10)

    @patch('routes.capteurs.capteur_service')
    def test_get_moyennes_by_salle_with_limit(self, mock_service):
        """Test GET /api/capteurs/salles/:id/moyennes?limit=5 - avec limite"""
        # Arrange
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = self.mock_moyennes
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/moyennes?limit=5')
        
        # Assert
        assert response.status_code == 200
        mock_service.get_moyennes_dernieres_donnees_by_salle.assert_called_once_with(1, 5)

    @patch('routes.capteurs.capteur_service')
    def test_get_moyennes_by_salle_not_found(self, mock_service):
        """Test GET /api/capteurs/salles/:id/moyennes - aucune donnée"""
        # Arrange
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = None
        
        # Act
        response = self.client.get('/api/capteurs/salles/999/moyennes')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Aucune donnée trouvée pour la salle 999' in data['message']

    # ========== TESTS GET DONNEES BY CAPTEUR ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_donnees_by_capteur_success(self, mock_service):
        """Test GET /api/capteurs/:id/donnees - succès"""
        # Arrange
        mock_donnees = {
            'capteur': {'id': 1, 'nom': '305822513', 'type_capteur': 'temperature'},
            'donnees': [{'valeur': 25.5, 'unite': '°C', 'date_update': '2025-01-01 12:00:00'}]
        }
        mock_service.get_dernieres_donnees_by_capteur.return_value = mock_donnees
        
        # Act
        response = self.client.get('/api/capteurs/1/donnees')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == mock_donnees
        mock_service.get_dernieres_donnees_by_capteur.assert_called_once_with(1, 1)

    @patch('routes.capteurs.capteur_service')
    def test_get_donnees_by_capteur_with_limit(self, mock_service):
        """Test GET /api/capteurs/:id/donnees?limit=5 - avec limite"""
        # Arrange
        mock_donnees = {'capteur': {}, 'donnees': []}
        mock_service.get_dernieres_donnees_by_capteur.return_value = mock_donnees
        
        # Act
        response = self.client.get('/api/capteurs/1/donnees?limit=5')
        
        # Assert
        assert response.status_code == 200
        mock_service.get_dernieres_donnees_by_capteur.assert_called_once_with(1, 5)

    @patch('routes.capteurs.capteur_service')
    def test_get_donnees_by_capteur_not_found(self, mock_service):
        """Test GET /api/capteurs/:id/donnees - capteur inexistant"""
        # Arrange
        mock_service.get_dernieres_donnees_by_capteur.return_value = None
        
        # Act
        response = self.client.get('/api/capteurs/999/donnees')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Capteur 999 non trouvé ou inactif' in data['message']

    # ========== TESTS GET TEMPERATURE BY SALLE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_temperature_by_salle_success(self, mock_service):
        """Test GET /api/capteurs/salles/:id/temperature - succès"""
        # Arrange
        mock_temperatures = [
            {'capteur_id': 1, 'nom': '305822513', 'valeur': 25.5, 'unite': '°C'}
        ]
        mock_service.get_temperature_by_salle.return_value = mock_temperatures
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/temperature')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == mock_temperatures
        mock_service.get_temperature_by_salle.assert_called_once_with(1, 10)

    @patch('routes.capteurs.capteur_service')
    def test_get_temperature_by_salle_empty(self, mock_service):
        """Test GET /api/capteurs/salles/:id/temperature - aucune donnée"""
        # Arrange
        mock_service.get_temperature_by_salle.return_value = []
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/temperature')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []

    # ========== TESTS GET HUMIDITE BY SALLE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_humidite_by_salle_success(self, mock_service):
        """Test GET /api/capteurs/salles/:id/humidite - succès"""
        # Arrange
        mock_humidites = [
            {'capteur_id': 2, 'nom': '305822514', 'valeur': 60.2, 'unite': '%'}
        ]
        mock_service.get_humidite_by_salle.return_value = mock_humidites
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/humidite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == mock_humidites

    # ========== TESTS GET PRESSION BY SALLE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_pression_by_salle_success(self, mock_service):
        """Test GET /api/capteurs/salles/:id/pression - succès"""
        # Arrange
        mock_pressions = [
            {'capteur_id': 3, 'nom': '305822515', 'valeur': 1013.25, 'unite': 'hPa'}
        ]
        mock_service.get_pression_by_salle.return_value = mock_pressions
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/pression')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == mock_pressions

    # ========== TESTS GET TEMPERATURE BY CAPTEUR ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_temperature_by_capteur_success(self, mock_service):
        """Test GET /api/capteurs/:id/temperature - succès"""
        # Arrange
        mock_temperatures = [
            {'valeur': 25.5, 'unite': '°C', 'date_update': '2025-01-01 12:00:00'}
        ]
        mock_service.get_temperature_by_capteur.return_value = mock_temperatures
        
        # Act
        response = self.client.get('/api/capteurs/1/temperature')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == mock_temperatures
        mock_service.get_temperature_by_capteur.assert_called_once_with(1, 10)

    # ========== TESTS PARAMETRES DE REQUETE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_parametres_limit_valides(self, mock_service):
        """Test des paramètres limit valides"""
        mock_service.get_temperature_by_salle.return_value = []
        
        # Test différentes valeurs de limit
        for limit in [1, 5, 10, 50, 100]:
            response = self.client.get(f'/api/capteurs/salles/1/temperature?limit={limit}')
            assert response.status_code == 200
            mock_service.get_temperature_by_salle.assert_called_with(1, limit)

    @patch('routes.capteurs.capteur_service')
    def test_parametres_limit_invalides(self, mock_service):
        """Test des paramètres limit invalides (utilisent la valeur par défaut)"""
        mock_service.get_temperature_by_salle.return_value = []
        
        # Test avec des valeurs invalides (Flask convertit en défaut)
        response = self.client.get('/api/capteurs/salles/1/temperature?limit=abc')
        assert response.status_code == 200
        # Flask utilise la valeur par défaut (10) si la conversion échoue
        mock_service.get_temperature_by_salle.assert_called_with(1, 10)

    # ========== TESTS GESTION ERREURS ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_gestion_exception_generale(self, mock_service):
        """Test de la gestion d'exception générale"""
        # Arrange
        mock_service.get_salles_actives.side_effect = Exception("Erreur inattendue")
        
        # Act
        response = self.client.get('/api/capteurs/salles')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Erreur inattendue' in data['message']

    def test_routes_inexistantes(self):
        """Test des routes inexistantes"""
        # Act
        response = self.client.get('/api/capteurs/route_inexistante')
        
        # Assert
        assert response.status_code == 404

    def test_methodes_non_autorisees(self):
        """Test des méthodes HTTP non autorisées"""
        # Act - POST sur une route GET
        response = self.client.post('/api/capteurs/salles')
        
        # Assert
        assert response.status_code == 405  # Method Not Allowed

    # ========== TESTS FORMAT REPONSE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_format_reponse_succes(self, mock_service):
        """Test du format de réponse en cas de succès"""
        # Arrange
        mock_service.get_salles_actives.return_value = self.mock_salles
        
        # Act
        response = self.client.get('/api/capteurs/salles')
        
        # Assert
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
        assert 'message' in data
        assert data['success'] is True

    @patch('routes.capteurs.capteur_service')
    def test_format_reponse_erreur(self, mock_service):
        """Test du format de réponse en cas d'erreur"""
        # Arrange
        mock_service.get_salles_actives.side_effect = Exception("Erreur test")
        
        # Act
        response = self.client.get('/api/capteurs/salles')
        
        # Assert
        data = json.loads(response.data)
        assert 'success' in data
        assert 'message' in data
        assert data['success'] is False
        assert 'data' not in data or data['data'] is None

    # ========== TESTS ROUTES CONFORMITE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salles_success(self, mock_service):
        """Test GET /api/capteurs/conformite - succès"""
        # Arrange
        mock_resultats = [
            {
                'salle': {'id': 1, 'nom': 'A01', 'batiment': 'A', 'etage': 0},
                'moyennes': {
                    'moyenne_temperature': 25.0,
                    'moyenne_humidite': 60.0,
                    'moyenne_pression': 1013.0
                },
                'conformite': {
                    'temperature_haute': 28.0,
                    'temperature_basse': 18.0,
                    'humidite_haute': 70.0,
                    'humidite_basse': 40.0
                },
                'statut': 'CONFORME',
                'alertes': [],
                'details_verification': {
                    'temperature': {'valeur': 25.0, 'conforme': True},
                    'humidite': {'valeur': 60.0, 'conforme': True}
                }
            },
            {
                'salle': {'id': 2, 'nom': 'A02', 'batiment': 'A', 'etage': 0},
                'moyennes': {
                    'moyenne_temperature': 30.0,
                    'moyenne_humidite': 80.0
                },
                'conformite': {
                    'temperature_haute': 28.0,
                    'humidite_haute': 70.0
                },
                'statut': 'NON_CONFORME',
                'alertes': ['Température trop élevée: 30.0°C > 28.0°C', 'Humidité trop élevée: 80.0% > 70.0%'],
                'details_verification': {
                    'temperature': {'valeur': 30.0, 'conforme': False},
                    'humidite': {'valeur': 80.0, 'conforme': False}
                }
            }
        ]
        mock_service.verifier_conformite_salles.return_value = mock_resultats
        
        # Act
        response = self.client.get('/api/capteurs/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['salles']) == 2
        assert data['data']['statistiques']['total'] == 2
        assert data['data']['statistiques']['conformes'] == 1
        assert data['data']['statistiques']['non_conformes'] == 1
        assert data['data']['statistiques']['pourcentage_conformite'] == 50.0
        assert len(data['data']['alertes_par_type']['temperature']) == 1
        assert len(data['data']['alertes_par_type']['humidite']) == 1
        mock_service.verifier_conformite_salles.assert_called_once_with(10)

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salles_with_limit(self, mock_service):
        """Test GET /api/capteurs/conformite?limit=5 - avec paramètre limit"""
        # Arrange
        mock_service.verifier_conformite_salles.return_value = []
        
        # Act
        response = self.client.get('/api/capteurs/conformite?limit=5')
        
        # Assert
        assert response.status_code == 200
        mock_service.verifier_conformite_salles.assert_called_once_with(5)

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salles_aucune_salle(self, mock_service):
        """Test GET /api/capteurs/conformite - aucune salle"""
        # Arrange
        mock_service.verifier_conformite_salles.return_value = []
        
        # Act
        response = self.client.get('/api/capteurs/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['salles'] == []
        assert data['data']['statistiques']['total'] == 0
        assert data['data']['statistiques']['pourcentage_conformite'] == 0

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salles_exception(self, mock_service):
        """Test GET /api/capteurs/conformite - exception"""
        # Arrange
        mock_service.verifier_conformite_salles.side_effect = Exception("Erreur de conformité")
        
        # Act
        response = self.client.get('/api/capteurs/conformite')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Erreur de conformité' in data['message']

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salle_success(self, mock_service):
        """Test GET /api/capteurs/salles/:id/conformite - succès"""
        # Arrange
        mock_moyennes = {
            'moyenne_temperature': 25.0,
            'moyenne_humidite': 60.0,
            'moyenne_pression': 1013.0
        }
        mock_conformite = {
            'temperature_haute': 28.0,
            'temperature_basse': 18.0,
            'humidite_haute': 70.0,
            'humidite_basse': 40.0,
            'pression_haute': 1020.0,
            'pression_basse': 1000.0
        }
        mock_verification = {
            'statut': 'CONFORME',
            'alertes': [],
            'details': {
                'temperature': {'valeur': 25.0, 'conforme': True},
                'humidite': {'valeur': 60.0, 'conforme': True},
                'pression': {'valeur': 1013.0, 'conforme': True}
            }
        }
        
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = mock_moyennes
        mock_service.get_seuils_conformite_by_salle.return_value = mock_conformite
        mock_service.verifier_seuils.return_value = mock_verification
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['salle_id'] == 1
        assert data['data']['moyennes'] == mock_moyennes
        assert data['data']['conformite'] == mock_conformite
        assert data['data']['statut'] == 'CONFORME'
        assert data['data']['alertes'] == []
        mock_service.get_moyennes_dernieres_donnees_by_salle.assert_called_once_with(1, 10)
        mock_service.get_seuils_conformite_by_salle.assert_called_once_with(1)
        mock_service.verifier_seuils.assert_called_once_with(mock_moyennes, mock_conformite)

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salle_with_limit(self, mock_service):
        """Test GET /api/capteurs/salles/:id/conformite?limit=5 - avec paramètre limit"""
        # Arrange
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = {'moyenne_temperature': 25.0}
        mock_service.get_seuils_conformite_by_salle.return_value = {'temperature_haute': 28.0}
        mock_service.verifier_seuils.return_value = {'statut': 'CONFORME', 'alertes': [], 'details': {}}
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/conformite?limit=5')
        
        # Assert
        assert response.status_code == 200
        mock_service.get_moyennes_dernieres_donnees_by_salle.assert_called_once_with(1, 5)

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salle_aucune_donnee(self, mock_service):
        """Test GET /api/capteurs/salles/:id/conformite - aucune donnée"""
        # Arrange
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = None
        
        # Act
        response = self.client.get('/api/capteurs/salles/999/conformite')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Aucune donnée trouvée pour la salle 999' in data['message']
        mock_service.get_seuils_conformite_by_salle.assert_not_called()

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salle_seuils_non_definis(self, mock_service):
        """Test GET /api/capteurs/salles/:id/conformite - seuils non définis"""
        # Arrange
        mock_moyennes = {'moyenne_temperature': 25.0}
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = mock_moyennes
        mock_service.get_seuils_conformite_by_salle.return_value = None
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['statut'] == 'SEUILS_NON_DEFINIS'
        assert 'Seuils de conformité non définis pour cette salle' in data['data']['alertes']
        assert data['data']['moyennes'] == mock_moyennes
        assert data['data']['conformite'] is None
        mock_service.verifier_seuils.assert_not_called()

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salle_non_conforme(self, mock_service):
        """Test GET /api/capteurs/salles/:id/conformite - salle non conforme"""
        # Arrange
        mock_moyennes = {
            'moyenne_temperature': 30.0,
            'moyenne_humidite': 80.0
        }
        mock_conformite = {
            'temperature_haute': 28.0,
            'humidite_haute': 70.0
        }
        mock_verification = {
            'statut': 'NON_CONFORME',
            'alertes': ['Température trop élevée: 30.0°C > 28.0°C', 'Humidité trop élevée: 80.0% > 70.0%'],
            'details': {
                'temperature': {'valeur': 30.0, 'conforme': False},
                'humidite': {'valeur': 80.0, 'conforme': False}
            }
        }
        
        mock_service.get_moyennes_dernieres_donnees_by_salle.return_value = mock_moyennes
        mock_service.get_seuils_conformite_by_salle.return_value = mock_conformite
        mock_service.verifier_seuils.return_value = mock_verification
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['statut'] == 'NON_CONFORME'
        assert len(data['data']['alertes']) == 2
        assert 'Température trop élevée' in data['data']['alertes'][0]
        assert 'Humidité trop élevée' in data['data']['alertes'][1]

    @patch('routes.capteurs.capteur_service')
    def test_get_conformite_salle_exception(self, mock_service):
        """Test GET /api/capteurs/salles/:id/conformite - exception"""
        # Arrange
        mock_service.get_moyennes_dernieres_donnees_by_salle.side_effect = Exception("Erreur calcul moyennes")
        
        # Act
        response = self.client.get('/api/capteurs/salles/1/conformite')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Erreur calcul moyennes' in data['message']

    # ========== TESTS STATISTIQUES CONFORMITE ==========
    
    @patch('routes.capteurs.capteur_service')
    def test_conformite_statistiques_calcul(self, mock_service):
        """Test du calcul des statistiques de conformité"""
        # Arrange
        mock_resultats = [
            {'statut': 'CONFORME', 'salle': {'nom': 'A01'}, 'alertes': []},
            {'statut': 'NON_CONFORME', 'salle': {'nom': 'A02'}, 'alertes': ['Température trop élevée: 30.0°C > 28.0°C']},
            {'statut': 'AUCUNE_DONNEE', 'salle': {'nom': 'A03'}, 'alertes': ['Aucune donnée']},
            {'statut': 'SEUILS_NON_DEFINIS', 'salle': {'nom': 'A04'}, 'alertes': ['Seuils non définis']},
            {'statut': 'CONFORME', 'salle': {'nom': 'A05'}, 'alertes': []}
        ]
        mock_service.verifier_conformite_salles.return_value = mock_resultats
        
        # Act
        response = self.client.get('/api/capteurs/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        stats = data['data']['statistiques']
        assert stats['total'] == 5
        assert stats['conformes'] == 2
        assert stats['non_conformes'] == 1
        assert stats['sans_donnees'] == 1
        assert stats['sans_seuils'] == 1
        assert stats['pourcentage_conformite'] == 40.0  # 2/5 * 100

    @patch('routes.capteurs.capteur_service')
    def test_conformite_alertes_par_type(self, mock_service):
        """Test du regroupement des alertes par type"""
        # Arrange
        mock_resultats = [
            {
                'statut': 'NON_CONFORME',
                'salle': {'nom': 'A01'},
                'alertes': [
                    'Température trop élevée: 30.0°C > 28.0°C',
                    'Humidité trop basse: 30.0% < 40.0%'
                ]
            },
            {
                'statut': 'NON_CONFORME',
                'salle': {'nom': 'A02'},
                'alertes': [
                    'Pression trop élevée: 1025.0hPa > 1020.0hPa'
                ]
            }
        ]
        mock_service.verifier_conformite_salles.return_value = mock_resultats
        
        # Act
        response = self.client.get('/api/capteurs/conformite')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        alertes = data['data']['alertes_par_type']
        
        assert len(alertes['temperature']) == 1
        assert alertes['temperature'][0]['salle'] == 'A01'
        assert 'Température trop élevée' in alertes['temperature'][0]['message']
        
        assert len(alertes['humidite']) == 1
        assert alertes['humidite'][0]['salle'] == 'A01'
        assert 'Humidité trop basse' in alertes['humidite'][0]['message']
        
        assert len(alertes['pression']) == 1
        assert alertes['pression'][0]['salle'] == 'A02'
        assert 'Pression trop élevée' in alertes['pression'][0]['message']