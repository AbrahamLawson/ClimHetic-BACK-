# 🌡️ ClimHetic Backend API

API REST pour la gestion des données climatiques et capteurs IoT de ClimHetic.

## 🚀 Déploiement

### Configuration GitHub Secrets
```bash
HOST=admin-hetic.arcplex.tech
USERNAME=abraham
SSH_KEY=[votre-clé-ssh]
PORT=2326
```

### Configuration Serveur
```bash
# Sur le serveur
mkdir -p /home/abraham/climhetic-backend
cd /home/abraham/climhetic-backend

# Créer .env
cp .env.example .env
# Éditer avec vos paramètres DB
```

### Déploiement Automatique
```bash
git push origin main
# Le déploiement se fait automatiquement via GitHub Actions
```

## 🏗️ Architecture

### Structure du Projet
```
src/
├── main.py              # Point d'entrée
├── requirements.txt     # Dépendances
├── routes/             # Endpoints API
└── services/           # Logique métier
```

### Configuration
```bash
# Variables d'environnement (.env)
DB_DIALECT=mysql
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=63306
DB_NAME=climhetic_db
DB_SSL=0

FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

### Endpoints
- `GET /api/health` - Vérification de santé
- `GET /api/admin/*` - Administration
- `GET /api/capteurs/*` - Gestion des capteurs

## 🔧 Développement Local

```bash
# Installation
pip install -r src/requirements.txt

# Configuration
cp .env.example .env

# Démarrage
cd src && python main.py
```

## 🐳 Docker

```bash
# Build
docker build -t climhetic-backend .

# Run
docker run -p 5001:5000 --env-file .env climhetic-backend
```

---

**Backend URL:** `http://admin-hetic.arcplex.tech:5001`  
**Status:** ✅ Production Ready
# Test
