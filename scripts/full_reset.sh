#!/bin/bash
# Script de nettoyage complet : base de données, cache, fichiers temporaires
# Usage: bash scripts/full_reset.sh

echo "================================================================================"
echo "🧹 NETTOYAGE COMPLET DE L'APPLICATION eSchool"
echo "================================================================================"
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Répertoire du projet
PROJECT_DIR="/home/jeshurun-nasser/dev/py/django-app/eschool"
cd "$PROJECT_DIR" || exit 1

echo -e "${BLUE}📂 Répertoire de travail: ${PROJECT_DIR}${NC}"
echo ""

# ============================================================================
# 1. NETTOYAGE DU CACHE DJANGO
# ============================================================================
echo -e "${YELLOW}🗑️  ÉTAPE 1/6 : Nettoyage du cache Django...${NC}"
echo "--------------------------------------------------------------------------------"

if [ -d "__pycache__" ]; then
    echo "   Suppression des fichiers __pycache__..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    echo -e "   ${GREEN}✅ Cache Python nettoyé${NC}"
else
    echo "   ℹ️  Pas de cache Python trouvé"
fi

# Nettoyage des fichiers .pyc
if find . -name "*.pyc" | grep -q .; then
    echo "   Suppression des fichiers .pyc..."
    find . -name "*.pyc" -delete
    echo -e "   ${GREEN}✅ Fichiers .pyc supprimés${NC}"
else
    echo "   ℹ️  Pas de fichiers .pyc trouvés"
fi

# Nettoyage des fichiers .pyo
if find . -name "*.pyo" | grep -q .; then
    echo "   Suppression des fichiers .pyo..."
    find . -name "*.pyo" -delete
    echo -e "   ${GREEN}✅ Fichiers .pyo supprimés${NC}"
else
    echo "   ℹ️  Pas de fichiers .pyo trouvés"
fi

echo ""

# ============================================================================
# 2. NETTOYAGE DES FICHIERS MÉDIA TEMPORAIRES
# ============================================================================
echo -e "${YELLOW}📁 ÉTAPE 2/6 : Nettoyage des fichiers média temporaires...${NC}"
echo "--------------------------------------------------------------------------------"

# Créer les répertoires média s'ils n'existent pas
mkdir -p media/avatars
mkdir -p media/documents

# Supprimer les anciens fichiers (sauf .gitkeep)
if [ -d "media/avatars" ]; then
    find media/avatars -type f ! -name ".gitkeep" -delete 2>/dev/null
    echo -e "   ${GREEN}✅ Avatars nettoyés${NC}"
fi

if [ -d "media/documents" ]; then
    find media/documents -type f ! -name ".gitkeep" -delete 2>/dev/null
    echo -e "   ${GREEN}✅ Documents nettoyés${NC}"
fi

echo ""

# ============================================================================
# 3. NETTOYAGE DES LOGS
# ============================================================================
echo -e "${YELLOW}📋 ÉTAPE 3/6 : Nettoyage des logs...${NC}"
echo "--------------------------------------------------------------------------------"

if [ -f "logs/django.log" ]; then
    > logs/django.log
    echo -e "   ${GREEN}✅ Log Django nettoyé${NC}"
else
    mkdir -p logs
    touch logs/django.log
    echo -e "   ${GREEN}✅ Fichier log créé${NC}"
fi

echo ""

# ============================================================================
# 4. NETTOYAGE DES FICHIERS STATIQUES
# ============================================================================
echo -e "${YELLOW}🎨 ÉTAPE 4/6 : Nettoyage des fichiers statiques...${NC}"
echo "--------------------------------------------------------------------------------"

if [ -d "staticfiles" ]; then
    rm -rf staticfiles/*
    echo -e "   ${GREEN}✅ Fichiers statiques collectés supprimés${NC}"
fi

echo ""

# ============================================================================
# 5. SUPPRESSION DE LA BASE DE DONNÉES SQLite
# ============================================================================
echo -e "${YELLOW}🗄️  ÉTAPE 5/6 : Suppression de la base de données...${NC}"
echo "--------------------------------------------------------------------------------"

if [ -f "db.sqlite3" ]; then
    echo -e "   ${RED}⚠️  Suppression de db.sqlite3...${NC}"
    rm -f db.sqlite3
    echo -e "   ${GREEN}✅ Base de données supprimée${NC}"
else
    echo "   ℹ️  Pas de base de données trouvée"
fi

# Supprimer les fichiers de migration (sauf __init__.py et fichiers initiaux)
echo "   Nettoyage des migrations..."
for app in accounts academic communication finance; do
    if [ -d "$app/migrations" ]; then
        find "$app/migrations" -type f -name "*.py" ! -name "__init__.py" ! -name "0001_initial.py" -delete 2>/dev/null
        find "$app/migrations" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    fi
done
echo -e "   ${GREEN}✅ Migrations nettoyées${NC}"

echo ""

# ============================================================================
# 6. RECRÉATION DE LA BASE DE DONNÉES
# ============================================================================
echo -e "${YELLOW}🏗️  ÉTAPE 6/6 : Recréation de la base de données...${NC}"
echo "--------------------------------------------------------------------------------"

echo "   Exécution des migrations..."
uv run python manage.py migrate --noinput

if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ Migrations appliquées avec succès${NC}"
else
    echo -e "   ${RED}❌ Erreur lors des migrations${NC}"
    exit 1
fi

echo ""

# ============================================================================
# RÉSUMÉ
# ============================================================================
echo "================================================================================"
echo -e "${GREEN}✅ NETTOYAGE COMPLET TERMINÉ${NC}"
echo "================================================================================"
echo ""
echo "📝 Prochaines étapes :"
echo "   1. Créer un superutilisateur : uv run python manage.py createsuperuser"
echo "   2. Générer les données de test : uv run python scripts/reset_and_populate.py"
echo "   3. Lancer le serveur : uv run python manage.py runserver"
echo ""
echo "================================================================================"
