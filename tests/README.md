# Tests Unitaires - ClimHetic Backend

## Structure des Tests

```
tests/
├── __init__.py
├── test_capteur_service.py      # Tests du service de consultation des capteurs
├── test_admin_service.py        # Tests du service d'administration
├── test_routes_capteurs.py      # Tests des routes de consultation
├── test_routes_admin.py         # Tests des routes d'administration
└── README.md
```

## Couverture des Tests

### **Service Capteur** (`test_capteur_service.py`)
- ✅ `get_salles_actives()` - Récupération des salles
- ✅ `get_capteurs_by_salle()` - Capteurs d'une salle
- ✅ `get_moyennes_dernieres_donnees_by_salle()` - Moyennes des mesures
- ✅ `get_temperature_by_salle()` - Températures d'une salle
- ✅ `get_humidite_by_salle()` - Humidité d'une salle
- ✅ `get_pression_by_salle()` - Pression d'une salle
- ✅ `get_temperature_by_capteur()` - Températures d'un capteur
- ✅ `get_dernieres_donnees_by_capteur()` - Données d'un capteur
- ✅ Gestion des erreurs et cas limites
- ✅ Paramètres par défaut

### **Service Admin** (`test_admin_service.py`)
- ✅ `get_all_capteurs()` - Liste complète des capteurs
- ✅ `ajouter_capteur()` - Ajout de nouveaux capteurs
- ✅ `desactiver_capteur()` - Désactivation de capteurs
- ✅ `reactiver_capteur()` - Réactivation de capteurs
- ✅ `supprimer_capteur()` - Suppression définitive
- ✅ Validation des types de capteurs
- ✅ Gestion des conflits et doublons
- ✅ Workflow complet d'administration

### **Routes Capteurs** (`test_routes_capteurs.py`)
- ✅ `GET /api/capteurs/salles` - Liste des salles
- ✅ `GET /api/capteurs/salles/:id/capteurs` - Capteurs d'une salle
- ✅ `GET /api/capteurs/salles/:id/moyennes` - Moyennes
- ✅ `GET /api/capteurs/salles/:id/temperature` - Températures
- ✅ `GET /api/capteurs/salles/:id/humidite` - Humidité
- ✅ `GET /api/capteurs/salles/:id/pression` - Pression
- ✅ `GET /api/capteurs/:id/donnees` - Données d'un capteur
- ✅ `GET /api/capteurs/:id/temperature` - Températures d'un capteur
- ✅ Paramètres de requête (limit)
- ✅ Gestion des erreurs HTTP
- ✅ Format des réponses JSON

### **Routes Admin** (`test_routes_admin.py`)
- ✅ `POST /api/admin/capteurs` - Ajout de capteurs
- ✅ `PUT /api/admin/capteurs/:id/desactiver` - Désactivation
- ✅ `PUT /api/admin/capteurs/:id/reactiver` - Réactivation
- ✅ `DELETE /api/admin/capteurs/:id` - Suppression
- ✅ `GET /api/admin/capteurs` - Liste administrative
- ✅ Validation des données JSON
- ✅ Gestion des confirmations de suppression
- ✅ Codes de statut HTTP appropriés
- ✅ Workflow complet d'administration

## Exécution des Tests

### **Tous les tests**
```bash
python run_tests.py
```

### **Tests spécifiques**
```bash
# Service capteur uniquement
python run_tests.py test_capteur_service.py

# Test spécifique
python run_tests.py test_capteur_service.py TestCapteurService::test_get_salles_actives_success

# Avec pytest directement
pytest tests/test_capteur_service.py -v
```

### **Avec couverture de code**
```bash
pytest tests/ --cov=src --cov-report=html
# Voir htmlcov/index.html pour le rapport détaillé
```

## Types de Tests

### **Tests Unitaires**
- **Mocking** complet des dépendances externes
- **Isolation** de chaque méthode
- **Validation** des paramètres et retours
- **Gestion d'erreurs** exhaustive

### **Tests d'Intégration**
- **Workflow complets** (ajouter → modifier → supprimer)
- **Interaction** entre services et routes
- **Validation** des formats de réponse

### **Tests de Validation**
- **Types de capteurs** valides/invalides
- **Paramètres manquants** ou incorrects
- **Conflits métier** (doublons, etc.)

## Cas de Test Couverts

### **Cas de Succès** 
- Récupération normale des données
- Ajout de capteurs valides
- Modifications autorisées
- Suppressions confirmées

### **Cas d'Erreur** 
- Données inexistantes
- Paramètres invalides
- Conflits métier
- Erreurs de base de données

### **Cas Limites** 
- Listes vides
- Valeurs nulles
- Paramètres par défaut
- Types de données incorrects

## 🔧 Configuration

### **Mocking**
- `unittest.mock.patch` pour les dépendances
- Isolation complète des tests
- Pas de connexion DB réelle

### **Fixtures**
- Données de test standardisées
- Setup/teardown automatique
- Réutilisation entre tests

### **Assertions**
- Vérification des valeurs retournées
- Validation des appels de méthodes
- Contrôle des codes de statut HTTP

## Métriques Cibles

- **Couverture de code** : > 80%
- **Tests par méthode** : 3-5 cas minimum
- **Temps d'exécution** : < 30 secondes
- **Taux de réussite** : 100%

## Debugging

### **Tests qui échouent**
```bash
# Mode verbose avec détails
pytest tests/ -v --tb=long

# S'arrêter au premier échec
pytest tests/ -x

# Tests spécifiques en mode debug
pytest tests/test_capteur_service.py::TestCapteurService::test_get_salles_actives_success -v -s
```

### **Couverture manquante**
```bash
# Rapport détaillé
pytest tests/ --cov=src --cov-report=term-missing

# Fichier HTML interactif
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```
