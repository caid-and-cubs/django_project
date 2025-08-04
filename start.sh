#!/bin/bash

# Script de démarrage pour AI Image Generator

echo "🚀 Démarrage d'AI Image Generator..."

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si un superutilisateur existe
echo "📋 Vérification du superutilisateur..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superutilisateur créé: admin/admin123')
else:
    print('✅ Superutilisateur déjà existant')
"

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Démarrer le serveur
echo "🌐 Démarrage du serveur sur http://localhost:8000"
echo "📊 Interface admin disponible sur http://localhost:8000/admin"
echo "🎨 Application disponible sur http://localhost:8000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python manage.py runserver 0.0.0.0:8000