import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.admin_service import AdminService


class TestAdminService:
    """Tests pour le service d'administration"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        print("\n" + "="*50)
        print("DÉBUT DES TESTS ADMIN SERVICE")
        print("="*50)
        self.service = AdminService()
        
        self.mock_capteur_complet = {
            'id': 1,
            'nom': '305822513',
            'type_capteur': 'temperature',
            'date_installation': '2025-01-01 10:00:00',
            'is_active': True,
            'id_salle': 1,
            'salle_nom': 'A01',
            'batiment': 'A',
            'etage': 0,
            'statut': 'Actif'
        }
        
        self.mock_salle = {
            'id': 1,
            'nom': 'A01',
            'batiment': 'A',
            'etage': 0
        }
        
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

    
    @patch('services.admin_service.execute_query')
    def test_get_all_capteurs_success(self, mock_execute_query):
        """Test récupération de tous les capteurs - succès"""
        # Arrange
        mock_execute_query.return_value = [self.mock_capteur_complet]
        
        # Act
        result = self.service.get_all_capteurs()
        
        # Assert
        assert result == [self.mock_capteur_complet]
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args[0]
        assert "FROM capteur c" in call_args[0]
        assert "LEFT JOIN salle s ON c.id_salle = s.id" in call_args[0]

    @patch('services.admin_service.execute_query')
    def test_get_all_capteurs_empty(self, mock_execute_query):
        """Test récupération de tous les capteurs - aucun capteur"""
        # Arrange
        mock_execute_query.return_value = []
        
        # Act
        result = self.service.get_all_capteurs()
        
        # Assert
        assert result == []

    @patch('services.admin_service.execute_query')
    def test_get_all_capteurs_exception(self, mock_execute_query):
        """Test récupération de tous les capteurs - exception"""
        # Arrange
        mock_execute_query.side_effect = Exception("Erreur DB")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.get_all_capteurs()
        assert "Erreur lors de la récupération des capteurs" in str(exc_info.value)

    
    @patch('services.admin_service.execute_single_query')
    @patch('services.admin_service.engine')
    def test_ajouter_capteur_success(self, mock_engine, mock_execute_single_query):
        """Test ajout de capteur - succès"""
        print("TEST: Ajout capteur - DÉBUT")
        # Arrange
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_result = MagicMock()
        mock_result.lastrowid = 4
        mock_conn.execute.return_value = mock_result
        
        mock_execute_single_query.side_effect = [
            self.mock_salle, 
            None, 
            self.mock_capteur_cree 
        ]
        
        # Act
        result = self.service.ajouter_capteur('NOUVEAU_CAPTEUR', 'temperature', 1)
        
        # Assert
        assert result == self.mock_capteur_cree
        assert mock_execute_single_query.call_count == 3
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        print("TEST: Ajout capteur - RÉUSSI")

    @patch('services.admin_service.execute_single_query')
    def test_ajouter_capteur_type_invalide(self, mock_execute_single_query):
        """Test ajout de capteur - type invalide"""
        print("TEST: Type capteur invalide - DÉBUT")
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.ajouter_capteur('TEST', 'type_invalide', 1)
        assert "Type de capteur invalide" in str(exc_info.value)
        assert "temperature, humidite, pression" in str(exc_info.value)
        print("TEST: Type capteur invalide - RÉUSSI")

    @patch('services.admin_service.execute_single_query')
    def test_ajouter_capteur_salle_inexistante(self, mock_execute_single_query):
        """Test ajout de capteur - salle inexistante"""
        # Arrange
        mock_execute_single_query.return_value = None 
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.ajouter_capteur('TEST', 'temperature', 999)
        assert "Salle 999 introuvable ou inactive" in str(exc_info.value)

    @patch('services.admin_service.execute_single_query')
    def test_ajouter_capteur_doublon(self, mock_execute_single_query):
        """Test ajout de capteur - capteur existant"""
        # Arrange
        mock_execute_single_query.side_effect = [
            self.mock_salle, 
            {'id': 1} 
        ]
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.ajouter_capteur('TEST', 'temperature', 1)
        assert "Un capteur de type 'temperature' existe déjà" in str(exc_info.value)

    def test_ajouter_capteur_tous_types_valides(self):
        """Test que tous les types de capteurs valides sont acceptés"""
        types_valides = ['temperature', 'humidite', 'pression']
        
        for type_capteur in types_valides:
            with patch('services.admin_service.execute_single_query') as mock_single:
                with patch('services.admin_service.engine') as mock_engine:
                    # Arrange
                    mock_conn = MagicMock()
                    mock_engine.connect.return_value.__enter__.return_value = mock_conn
                    mock_result = MagicMock()
                    mock_result.lastrowid = 1
                    mock_conn.execute.return_value = mock_result
                    
                    mock_single.side_effect = [
                        self.mock_salle, 
                        None, 
                        self.mock_capteur_cree  
                    ]
                    
                    result = self.service.ajouter_capteur('TEST', type_capteur, 1)
                    assert result is not None

    
    @patch('services.admin_service.execute_single_query')
    @patch('services.admin_service.engine')
    def test_desactiver_capteur_success(self, mock_engine, mock_execute_single_query):
        """Test désactivation de capteur - succès"""
        # Arrange
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        capteur_actif = self.mock_capteur_complet.copy()
        mock_execute_single_query.return_value = capteur_actif
        
        # Act
        result = self.service.desactiver_capteur(1)
        
        # Assert
        assert result['is_active'] is False
        assert result['id'] == 1
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('services.admin_service.execute_single_query')
    def test_desactiver_capteur_inexistant(self, mock_execute_single_query):
        """Test désactivation de capteur - capteur inexistant"""
        # Arrange
        mock_execute_single_query.return_value = None
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.desactiver_capteur(999)
        assert "Capteur 999 introuvable" in str(exc_info.value)

    @patch('services.admin_service.execute_single_query')
    def test_desactiver_capteur_deja_inactif(self, mock_execute_single_query):
        """Test désactivation de capteur - déjà inactif"""
        # Arrange
        capteur_inactif = self.mock_capteur_complet.copy()
        capteur_inactif['is_active'] = False
        mock_execute_single_query.return_value = capteur_inactif
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.desactiver_capteur(1)
        assert "Le capteur 1 est déjà désactivé" in str(exc_info.value)

    
    @patch('services.admin_service.execute_single_query')
    @patch('services.admin_service.engine')
    def test_reactiver_capteur_success(self, mock_engine, mock_execute_single_query):
        """Test réactivation de capteur - succès"""
        # Arrange
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        capteur_inactif = self.mock_capteur_complet.copy()
        capteur_inactif['is_active'] = False
        
        mock_execute_single_query.side_effect = [
            capteur_inactif, 
            None  
        ]
        
        # Act
        result = self.service.reactiver_capteur(1)
        
        # Assert
        assert result['is_active'] is True
        assert result['id'] == 1
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('services.admin_service.execute_single_query')
    def test_reactiver_capteur_inexistant(self, mock_execute_single_query):
        """Test réactivation de capteur - capteur inexistant"""
        # Arrange
        mock_execute_single_query.return_value = None
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.reactiver_capteur(999)
        assert "Capteur 999 introuvable" in str(exc_info.value)

    @patch('services.admin_service.execute_single_query')
    def test_reactiver_capteur_deja_actif(self, mock_execute_single_query):
        """Test réactivation de capteur - déjà actif"""
        # Arrange
        mock_execute_single_query.return_value = self.mock_capteur_complet
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.reactiver_capteur(1)
        assert "Le capteur 1 est déjà actif" in str(exc_info.value)

    @patch('services.admin_service.execute_single_query')
    def test_reactiver_capteur_conflit_type(self, mock_execute_single_query):
        """Test réactivation de capteur - conflit de type dans la salle"""
        # Arrange
        capteur_inactif = self.mock_capteur_complet.copy()
        capteur_inactif['is_active'] = False
        
        mock_execute_single_query.side_effect = [
            capteur_inactif,  
            {'id': 2}  
        ]
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.reactiver_capteur(1)
        assert "Un capteur de type 'temperature' est déjà actif" in str(exc_info.value)

    @patch('services.admin_service.execute_single_query')
    @patch('services.admin_service.engine')
    def test_reactiver_capteur_sans_salle(self, mock_engine, mock_execute_single_query):
        """Test réactivation de capteur - capteur sans salle assignée"""
        # Arrange
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        capteur_sans_salle = self.mock_capteur_complet.copy()
        capteur_sans_salle['is_active'] = False
        capteur_sans_salle['id_salle'] = None
        
        mock_execute_single_query.return_value = capteur_sans_salle
        
        # Act
        result = self.service.reactiver_capteur(1)
        
        # Assert
        assert result['is_active'] is True
        assert mock_execute_single_query.call_count == 1

    
    @patch('services.admin_service.execute_single_query')
    @patch('services.admin_service.engine')
    def test_supprimer_capteur_success(self, mock_engine, mock_execute_single_query):
        """Test suppression de capteur - succès"""
        # Arrange
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        mock_execute_single_query.return_value = self.mock_capteur_complet
        
        # Act
        result = self.service.supprimer_capteur(1)
        
        # Assert
        assert result is True
        assert mock_conn.execute.call_count == 4
        mock_conn.commit.assert_called_once()

    @patch('services.admin_service.execute_single_query')
    def test_supprimer_capteur_inexistant(self, mock_execute_single_query):
        """Test suppression de capteur - capteur inexistant"""
        # Arrange
        mock_execute_single_query.return_value = None
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.supprimer_capteur(999)
        assert "Capteur 999 introuvable" in str(exc_info.value)

    @patch('services.admin_service.execute_single_query')
    @patch('services.admin_service.engine')
    def test_supprimer_capteur_exception_db(self, mock_engine, mock_execute_single_query):
        """Test suppression de capteur - exception base de données"""
        # Arrange
        mock_execute_single_query.return_value = self.mock_capteur_complet
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("Erreur DB")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.supprimer_capteur(1)
        assert "Erreur lors de la suppression du capteur" in str(exc_info.value)

    
    def test_workflow_complet_capteur(self):
        """Test du workflow complet : ajouter -> désactiver -> réactiver -> supprimer"""
        with patch('services.admin_service.execute_single_query') as mock_single:
            with patch('services.admin_service.engine') as mock_engine:
                mock_conn = MagicMock()
                mock_engine.connect.return_value.__enter__.return_value = mock_conn
                mock_result = MagicMock()
                mock_result.lastrowid = 1
                mock_conn.execute.return_value = mock_result
                
                mock_single.side_effect = [
                    self.mock_salle,  
                    None,  
                    self.mock_capteur_cree  
                ]
                
                result_ajout = self.service.ajouter_capteur('TEST', 'temperature', 1)
                assert result_ajout is not None
                
                mock_single.reset_mock()
                mock_conn.reset_mock()
                
                capteur_actif = self.mock_capteur_complet.copy()
                mock_single.side_effect = [capteur_actif]  
                
                result_desactivation = self.service.desactiver_capteur(1)
                assert result_desactivation['is_active'] is False
                
                mock_single.reset_mock()
                mock_conn.reset_mock()
                
                capteur_inactif = self.mock_capteur_complet.copy()
                capteur_inactif['is_active'] = False
                mock_single.side_effect = [
                    capteur_inactif,  
                    None  
                ]
                
                result_reactivation = self.service.reactiver_capteur(1)
                assert result_reactivation['is_active'] is True
                
                mock_single.reset_mock()
                mock_conn.reset_mock()
                mock_single.side_effect = [self.mock_capteur_complet]  
                
                result_suppression = self.service.supprimer_capteur(1)
                assert result_suppression is True

    def test_validation_types_capteurs(self):
        """Test de validation des types de capteurs"""
        types_invalides = ['temp', 'humidity', 'pressure', '', None, 123]
        
        for type_invalide in types_invalides:
            with pytest.raises(Exception) as exc_info:
                self.service.ajouter_capteur('TEST', type_invalide, 1)
            assert "Type de capteur invalide" in str(exc_info.value)

    def test_gestion_parametres_none(self):
        """Test de la gestion des paramètres None ou invalides"""
        with pytest.raises(Exception):
            self.service.ajouter_capteur(None, 'temperature', 1)
        
        with pytest.raises(Exception):
            self.service.ajouter_capteur('TEST', 'temperature', None)
        
        with pytest.raises(Exception):
            self.service.desactiver_capteur(None)