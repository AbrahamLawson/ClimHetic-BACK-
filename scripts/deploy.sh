#!/bin/bash

# Script de déploiement ClimHetic Backend
# Usage: ./scripts/deploy.sh

set -e

echo "🚀 Déploiement ClimHetic Backend"

# Nettoyage
docker stop climhetic-backend 2>/dev/null || true
docker rm climhetic-backend 2>/dev/null || true
docker stop $(docker ps -q --filter "publish=5001") 2>/dev/null || true
docker rm $(docker ps -aq --filter "publish=5001") 2>/dev/null || true

# Vérification .env
[ ! -f ".env" ] && cp .env.example .env && echo "⚠️ Configurez le fichier .env"

# Build et démarrage
docker build -t climhetic-backend:latest .
docker run -d \
  --name climhetic-backend \
  --restart unless-stopped \
  -p 5001:5000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  climhetic-backend:latest

# Vérification
sleep 15
if curl -f http://localhost:5001/api/health >/dev/null 2>&1; then
    echo "✅ Backend déployé avec succès sur http://localhost:5001"
else
    echo "❌ Échec du déploiement"
    docker logs climhetic-backend --tail 20
    exit 1
fi
