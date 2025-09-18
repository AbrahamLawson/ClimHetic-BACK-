import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from routes.admin import admin_bp


class TestRoutesAdmin:
    """Tests pour les routes d'administration"""
    
    def setup_method(self):
        print("\n" + "="*50)
        print("DÉBUT DES TESTS ROUTES ADMIN")
        print("="*50)
        """Setup avant chaque test"""
        self.app = Flask(__name__)
        self.app.register_blueprint(admin_bp, url_prefix='/api/admin')
        self.client = self.app.test_client()
        
        self.mock_capteur_cree = {
            'id': 4,
            'nom': 'NOUVEAU_CAPTEUR',
            'type_capteur': 'temperature',
            'date_installation': '2025-01-01 15:00:00',
            'is_active': True,
            'salle_nom': 'A01',
            'batiment': 'A',
            'etage': 0
        }
        
        self.mock_capteur_modifie = {
            'id': 1,
            'nom': '305822513',
            'type_capteur': 'temperature',
            'is_active': False,
            'salle_nom': 'A01'
        }
        
        self.mock_capteurs_liste = [
            {
                'id': 1,
                'nom': '305822513',
                'type_capteur': 'temperature',
                'is_active': True,
                'salle_nom': 'A01'
            },
            {
                'id': 2,
                'nom': '305822514',
                'type_capteur': 'humidite',
                'is_active': False,
                'salle_nom': 'A02'
            }
        ]

    
    @patch('routes.admin.admin_service')
    def test_ajouter_capteur_success(self, mock_service):
        """Test POST /api/admin/capteurs - succès"""
        print("TEST ROUTE: POST /capteurs - DÉBUT")
        # Arrange
        mock_service.ajouter_capteur.return_value = self.mock_capteur_cree
        payload = {
            'nom': 'NOUVEAU_CAPTEUR',
            'type_capteur': 'temperature',
            'id_salle': 1
        }
        
        # Act
        response = self.client.post('/api/admin/capteurs', 
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == self.mock_capteur_cree
        assert 'Capteur temperature "NOUVEAU_CAPTEUR" ajouté avec succès' in data['message']
        mock_service.ajouter_capteur.assert_called_once_with('NOUVEAU_CAPTEUR', 'temperature', 1)
        print("TEST ROUTE: POST /capteurs - RÉUSSI")

    @patch('routes.admin.admin_service')
    def test_ajouter_capteur_sans_json(self, mock_service):
        """Test POST /api/admin/capteurs - sans données JSON"""
        # Act
        response = self.client.post('/api/admin/capteurs')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Content-Type doit être application/json' in data['message']

    @patch('routes.admin.admin_service')
    def test_ajouter_capteur_champs_manquants(self, mock_service):
        """Test POST /api/admin/capteurs - champs manquants"""
        # Arrange
        payloads_invalides = [
            {'nom': 'TEST'},  
            {'type_capteur': 'temperature'},  
            {'id_salle': 1},  
            {'nom': 'TEST', 'type_capteur': 'temperature'},  
        ]
        
        for payload in payloads_invalides:
            # Act
            response = self.client.post('/api/admin/capteurs',
                                      data=json.dumps(payload),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Champs requis: nom, type_capteur, id_salle' in data['message']

    @patch('routes.admin.admin_service')
    def test_ajouter_capteur_type_invalide(self, mock_service):
        """Test POST /api/admin/capteurs - type de capteur invalide"""
        # Arrange
        payload = {
            'nom': 'TEST',
            'type_capteur': 'type_invalide',
            'id_salle': 1
        }
        
        # Act
        response = self.client.post('/api/admin/capteurs',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Type de capteur invalide' in data['message']
        assert 'temperature, humidite, pression' in data['message']

    @patch('routes.admin.admin_service')
    def test_ajouter_capteur_tous_types_valides(self, mock_service):
        """Test POST /api/admin/capteurs - tous les types valides"""
        # Arrange
        mock_service.ajouter_capteur.return_value = self.mock_capteur_cree
        types_valides = ['temperature', 'humidite', 'pression']
        
        for type_capteur in types_valides:
            payload = {
                'nom': 'TEST',
                'type_capteur': type_capteur,
                'id_salle': 1
            }
            
            # Act
            response = self.client.post('/api/admin/capteurs',
                                      data=json.dumps(payload),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True

    @patch('routes.admin.admin_service')
    def test_ajouter_capteur_exception_service(self, mock_service):
        """Test POST /api/admin/capteurs - exception du service"""
        # Arrange
        mock_service.ajouter_capteur.side_effect = Exception("Salle inexistante")
        payload = {
            'nom': 'TEST',
            'type_capteur': 'temperature',
            'id_salle': 999
        }
        
        # Act
        response = self.client.post('/api/admin/capteurs',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Salle inexistante' in data['message']

    
    @patch('routes.admin.admin_service')
    def test_desactiver_capteur_success(self, mock_service):
        """Test PUT /api/admin/capteurs/:id/desactiver - succès"""
        # Arrange
        mock_service.desactiver_capteur.return_value = self.mock_capteur_modifie
        
        # Act
        response = self.client.put('/api/admin/capteurs/1/desactiver')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == self.mock_capteur_modifie
        assert 'Capteur 1 désactivé avec succès' in data['message']
        mock_service.desactiver_capteur.assert_called_once_with(1)

    @patch('routes.admin.admin_service')
    def test_desactiver_capteur_inexistant(self, mock_service):
        """Test PUT /api/admin/capteurs/:id/desactiver - capteur inexistant"""
        # Arrange
        mock_service.desactiver_capteur.side_effect = Exception("Capteur 999 introuvable")
        
        # Act
        response = self.client.put('/api/admin/capteurs/999/desactiver')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Capteur 999 introuvable' in data['message']

    @patch('routes.admin.admin_service')
    def test_desactiver_capteur_deja_inactif(self, mock_service):
        """Test PUT /api/admin/capteurs/:id/desactiver - déjà inactif"""
        # Arrange
        mock_service.desactiver_capteur.side_effect = Exception("Le capteur 1 est déjà désactivé")
        
        # Act
        response = self.client.put('/api/admin/capteurs/1/desactiver')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Le capteur 1 est déjà désactivé' in data['message']

    
    @patch('routes.admin.admin_service')
    def test_reactiver_capteur_success(self, mock_service):
        """Test PUT /api/admin/capteurs/:id/reactiver - succès"""
        # Arrange
        capteur_reactive = self.mock_capteur_modifie.copy()
        capteur_reactive['is_active'] = True
        mock_service.reactiver_capteur.return_value = capteur_reactive
        
        # Act
        response = self.client.put('/api/admin/capteurs/1/reactiver')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == capteur_reactive
        assert 'Capteur 1 réactivé avec succès' in data['message']
        mock_service.reactiver_capteur.assert_called_once_with(1)

    @patch('routes.admin.admin_service')
    def test_reactiver_capteur_conflit(self, mock_service):
        """Test PUT /api/admin/capteurs/:id/reactiver - conflit de type"""
        # Arrange
        mock_service.reactiver_capteur.side_effect = Exception("Un capteur de type 'temperature' est déjà actif")
        
        # Act
        response = self.client.put('/api/admin/capteurs/1/reactiver')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert "Un capteur de type 'temperature' est déjà actif" in data['message']

    
    @patch('routes.admin.admin_service')
    def test_supprimer_capteur_success(self, mock_service):
        """Test DELETE /api/admin/capteurs/:id?confirmer=true - succès"""
        # Arrange
        mock_service.supprimer_capteur.return_value = True
        
        # Act
        response = self.client.delete('/api/admin/capteurs/1?confirmer=true')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Capteur 1 supprimé définitivement' in data['message']
        mock_service.supprimer_capteur.assert_called_once_with(1)

    @patch('routes.admin.admin_service')
    def test_supprimer_capteur_sans_confirmation(self, mock_service):
        """Test DELETE /api/admin/capteurs/:id - sans confirmation"""
        # Act
        response = self.client.delete('/api/admin/capteurs/1')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Suppression non confirmée' in data['message']
        assert 'confirmer=true' in data['message']

    @patch('routes.admin.admin_service')
    def test_supprimer_capteur_confirmation_invalide(self, mock_service):
        """Test DELETE /api/admin/capteurs/:id?confirmer=false - confirmation invalide"""
        # Act
        response = self.client.delete('/api/admin/capteurs/1?confirmer=false')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Suppression non confirmée' in data['message']

    @patch('routes.admin.admin_service')
    def test_supprimer_capteur_echec_service(self, mock_service):
        """Test DELETE /api/admin/capteurs/:id?confirmer=true - échec du service"""
        # Arrange
        mock_service.supprimer_capteur.return_value = False
        
        # Act
        response = self.client.delete('/api/admin/capteurs/1?confirmer=true')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Échec de la suppression du capteur 1' in data['message']

    @patch('routes.admin.admin_service')
    def test_supprimer_capteur_exception(self, mock_service):
        """Test DELETE /api/admin/capteurs/:id?confirmer=true - exception"""
        # Arrange
        mock_service.supprimer_capteur.side_effect = Exception("Capteur introuvable")
        
        # Act
        response = self.client.delete('/api/admin/capteurs/1?confirmer=true')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Capteur introuvable' in data['message']

    
    @patch('routes.admin.admin_service')
    def test_get_all_capteurs_admin_success(self, mock_service):
        """Test GET /api/admin/capteurs - succès"""
        # Arrange
        mock_service.get_all_capteurs.return_value = self.mock_capteurs_liste
        
        # Act
        response = self.client.get('/api/admin/capteurs')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['capteurs'] == self.mock_capteurs_liste
        assert 'statistiques' in data['data']
        assert data['data']['statistiques']['total'] == 2
        assert data['data']['statistiques']['actifs'] == 1
        assert data['data']['statistiques']['inactifs'] == 1
        assert '2 capteur(s) récupéré(s) (1 actifs, 1 inactifs)' in data['message']

    @patch('routes.admin.admin_service')
    def test_get_all_capteurs_admin_empty(self, mock_service):
        """Test GET /api/admin/capteurs - aucun capteur"""
        # Arrange
        mock_service.get_all_capteurs.return_value = []
        
        # Act
        response = self.client.get('/api/admin/capteurs')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['capteurs'] == []
        assert data['data']['statistiques']['total'] == 0
        assert data['data']['statistiques']['actifs'] == 0
        assert data['data']['statistiques']['inactifs'] == 0

    @patch('routes.admin.admin_service')
    def test_get_all_capteurs_admin_exception(self, mock_service):
        """Test GET /api/admin/capteurs - exception"""
        # Arrange
        mock_service.get_all_capteurs.side_effect = Exception("Erreur DB")
        
        # Act
        response = self.client.get('/api/admin/capteurs')
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Erreur DB' in data['message']

    
    def test_methodes_non_autorisees(self):
        """Test des méthodes HTTP non autorisées"""
        response = self.client.patch('/api/admin/capteurs', 
                                   data=json.dumps({'nom': 'TEST'}),
                                   content_type='application/json')
        assert response.status_code == 405
        
        response = self.client.post('/api/admin/capteurs/1/desactiver')
        assert response.status_code == 405
        
        response = self.client.get('/api/admin/capteurs/1?confirmer=true')
        assert response.status_code == 405

    
    @patch('routes.admin.admin_service')
    def test_parametres_url_valides(self, mock_service):
        """Test des paramètres URL valides"""
        mock_service.desactiver_capteur.return_value = self.mock_capteur_modifie
        
        for capteur_id in [1, 10, 999]:
            response = self.client.put(f'/api/admin/capteurs/{capteur_id}/desactiver')
            if response.status_code == 200:
                mock_service.desactiver_capteur.assert_called_with(capteur_id)

    def test_parametres_url_invalides(self):
        """Test des paramètres URL invalides"""
        response = self.client.put('/api/admin/capteurs/abc/desactiver')
        assert response.status_code == 404  
        
        response = self.client.put('/api/admin/capteurs/-1/desactiver')
        assert response.status_code == 404  

    
    @patch('routes.admin.admin_service')
    def test_format_reponse_succes_creation(self, mock_service):
        """Test du format de réponse pour création (201)"""
        # Arrange
        mock_service.ajouter_capteur.return_value = self.mock_capteur_cree
        payload = {
            'nom': 'TEST',
            'type_capteur': 'temperature',
            'id_salle': 1
        }
        
        # Act
        response = self.client.post('/api/admin/capteurs',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 201  
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
        assert 'message' in data
        assert data['success'] is True

    @patch('routes.admin.admin_service')
    def test_format_reponse_succes_modification(self, mock_service):
        """Test du format de réponse pour modification (200)"""
        # Arrange
        mock_service.desactiver_capteur.return_value = self.mock_capteur_modifie
        
        # Act
        response = self.client.put('/api/admin/capteurs/1/desactiver')
        
        # Assert
        assert response.status_code == 200  
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
        assert 'message' in data
        assert data['success'] is True

    @patch('routes.admin.admin_service')
    def test_format_reponse_erreur_validation(self, mock_service):
        """Test du format de réponse pour erreur de validation (400)"""
        # Act
        response = self.client.post('/api/admin/capteurs',
                                  data=json.dumps({'nom': 'TEST'}),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 400  
        data = json.loads(response.data)
        assert 'success' in data
        assert 'message' in data
        assert data['success'] is False

    @patch('routes.admin.admin_service')
    def test_format_reponse_erreur_serveur(self, mock_service):
        """Test du format de réponse pour erreur serveur (500)"""
        # Arrange
        mock_service.ajouter_capteur.side_effect = Exception("Erreur interne")
        payload = {
            'nom': 'TEST',
            'type_capteur': 'temperature',
            'id_salle': 1
        }
        
        # Act
        response = self.client.post('/api/admin/capteurs',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 500  
        data = json.loads(response.data)
        assert 'success' in data
        assert 'message' in data
        assert data['success'] is False

    
    @patch('routes.admin.admin_service')
    def test_workflow_complet_capteur(self, mock_service):
        """Test du workflow complet via les routes"""
        mock_service.ajouter_capteur.return_value = self.mock_capteur_cree
        payload = {
            'nom': 'WORKFLOW_TEST',
            'type_capteur': 'temperature',
            'id_salle': 1
        }
        
        response = self.client.post('/api/admin/capteurs',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        assert response.status_code == 201
        
        mock_service.desactiver_capteur.return_value = self.mock_capteur_modifie
        response = self.client.put('/api/admin/capteurs/4/desactiver')
        assert response.status_code == 200
        
        capteur_reactive = self.mock_capteur_modifie.copy()
        capteur_reactive['is_active'] = True
        mock_service.reactiver_capteur.return_value = capteur_reactive
        response = self.client.put('/api/admin/capteurs/4/reactiver')
        assert response.status_code == 200
        
        mock_service.supprimer_capteur.return_value = True
        response = self.client.delete('/api/admin/capteurs/4?confirmer=true')
        assert response.status_code == 200