# 🚀 Guide de Déploiement sur Vercel

Ce guide vous explique comment déployer votre application AI Image Generator sur Vercel.

## ⚠️ Limitations importantes

**Note critique :** Stable Diffusion ne fonctionnera probablement **PAS** sur Vercel à cause des limitations suivantes :
- Limite de mémoire des fonctions serverless (1GB max)
- Limite de taille des packages (50MB)
- Temps d'exécution limité (30s max)
- Pas de GPU disponible

L'application fonctionnera en **mode démonstration** qui génère des images placeholder.

## 📋 Prérequis

1. **Compte Vercel** : [Créer un compte gratuit](https://vercel.com)
2. **Repository Git** : Code poussé sur GitHub/GitLab/Bitbucket
3. **Cloudinary** (recommandé) : [Compte gratuit](https://cloudinary.com) pour les images
4. **PostgreSQL** (optionnel) : Base de données pour la production

## 🔧 Configuration avant déploiement

### 1. Variables d'environnement

Créez un fichier `.env` basé sur `.env.example` :

```bash
cp .env.example .env
```

Remplissez les variables essentielles :

```env
# Django Configuration
SECRET_KEY=your-super-secret-key-here-min-50-chars
DEBUG=False
DJANGO_SETTINGS_MODULE=image_generator.settings_production

# Database (optionnel - SQLite par défaut)
DATABASE_URL=postgresql://user:password@host:port/database

# Cloudinary pour les images (recommandé)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# AI Generation (mettre à true si vous voulez essayer)
ENABLE_AI_GENERATION=false
```

### 2. Génération de SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🌐 Déploiement sur Vercel

### Méthode 1 : Via l'interface Vercel (Recommandée)

1. **Connectez votre repository** :
   - Allez sur [vercel.com](https://vercel.com)
   - Cliquez sur "New Project"
   - Sélectionnez votre repository

2. **Configuration du projet** :
   - Framework Preset : `Other`
   - Root Directory : `./` (racine)
   - Build Command : `bash build_files.sh`
   - Output Directory : `staticfiles_build/static`

3. **Variables d'environnement** :
   - Ajoutez toutes les variables de votre `.env`
   - Dans Project Settings > Environment Variables

4. **Déployez** :
   - Cliquez sur "Deploy"

### Méthode 2 : Via CLI Vercel

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel --prod
```

## 🗄️ Configuration Base de données

### Option 1 : PostgreSQL (Recommandée)

Services recommandés :
- **Neon** : [neon.tech](https://neon.tech) (gratuit)
- **Supabase** : [supabase.com](https://supabase.com) (gratuit)
- **Railway** : [railway.app](https://railway.app)

```env
DATABASE_URL=postgresql://username:password@hostname:port/database
```

### Option 2 : SQLite (Par défaut)

SQLite fonctionne mais les données seront perdues à chaque redéploiement.

```env
# Pas de DATABASE_URL nécessaire pour SQLite
```

## 📁 Configuration Cloudinary

1. **Créer un compte** : [cloudinary.com](https://cloudinary.com)

2. **Récupérer l'URL** :
   - Dashboard > Account Details
   - Copiez l'URL Cloudinary

3. **Configurer** :
```env
CLOUDINARY_URL=cloudinary://123456789012345:abcdefghijklmnopqrstuvwxyz@your-cloud-name
```

## 🚨 Résolution des problèmes

### Erreur de build

```bash
# Si les dépendances sont trop lourdes
# Modifiez requirements.txt pour retirer :
# torch
# torchvision  
# diffusers
# transformers
```

### Erreur de mémoire

```python
# Dans settings_production.py
ENABLE_AI_GENERATION = False  # Forcer le mode démo
```

### Erreur de fichiers statiques

```bash
# Vérifiez que build_files.sh est exécutable
chmod +x build_files.sh
```

### Erreur de base de données

```python
# Migration sur Vercel
python manage.py migrate --run-syncdb
```

## 🔒 Sécurité en production

### Variables d'environnement obligatoires

```env
SECRET_KEY=your-very-long-secret-key-minimum-50-characters
DEBUG=False
ALLOWED_HOSTS=your-app.vercel.app,localhost
```

### Headers de sécurité

Déjà configurés dans `settings_production.py` :
- HTTPS forcé
- Protection XSS
- Protection CSRF
- Cookies sécurisés

## 📊 Monitoring et logs

### Voir les logs Vercel

```bash
vercel logs your-project-url
```

### Debug en local

```bash
# Tester avec les settings de production
export DJANGO_SETTINGS_MODULE=image_generator.settings_production
python manage.py runserver
```

## 🎯 Post-déploiement

### 1. Créer un superutilisateur

Via Vercel CLI :
```bash
vercel exec python manage.py createsuperuser
```

### 2. Tester l'application

- **Page principale** : `https://your-app.vercel.app`
- **Admin** : `https://your-app.vercel.app/admin`
- **API** : `https://your-app.vercel.app/generate/`

### 3. Configuration du domaine (optionnel)

Dans Vercel Dashboard :
- Project Settings > Domains
- Ajouter votre domaine personnalisé

## 🔄 Mises à jour

```bash
# Push sur la branche principale
git push origin main

# Vercel redéploiera automatiquement
```

## 💡 Alternatives pour l'IA

Si vous voulez vraiment utiliser Stable Diffusion :

### Option 1 : Railway
- Plus de mémoire disponible
- Support GPU possible
- [railway.app](https://railway.app)

### Option 2 : Google Cloud Run
- Jusqu'à 8GB de mémoire
- GPU optionnel
- Pay-per-use

### Option 3 : Hugging Face Spaces
- GPU gratuit limité
- Optimisé pour l'IA
- [huggingface.co/spaces](https://huggingface.co/spaces)

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifiez les logs** : `vercel logs`
2. **Testez en local** avec les settings de production
3. **Variables d'environnement** : Vérifiez qu'elles sont bien définies
4. **Documentation Vercel** : [vercel.com/docs](https://vercel.com/docs)

---

## 🎉 Félicitations !

Votre application AI Image Generator est maintenant déployée sur Vercel ! 

Même en mode démonstration, vous avez une base solide pour :
- Présenter votre travail
- Tester l'interface utilisateur
- Développer d'autres fonctionnalités
- Migrer vers une plateforme avec plus de ressources quand nécessaire