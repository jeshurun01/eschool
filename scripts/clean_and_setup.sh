#!/bin/bash
# Script de nettoyage complet et configuration
# Usage: bash scripts/clean_and_setup.sh

echo "================================================================================"
echo "🧹 NETTOYAGE COMPLET ET RÉINITIALISATION - eSchool"
echo "================================================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/jeshurun-nasser/dev/py/django-app/eschool"
cd "$PROJECT_DIR" || exit 1

echo -e "${BLUE}📂 Répertoire: ${PROJECT_DIR}${NC}"
echo ""

# ============================================================================
# 1. SUPPRESSION DE LA BASE DE DONNÉES
# ============================================================================
echo -e "${YELLOW}🗄️  ÉTAPE 1/5 : Suppression de la base de données...${NC}"
echo "--------------------------------------------------------------------------------"

if [ -f "db.sqlite3" ]; then
    rm -f db.sqlite3
    echo -e "   ${GREEN}✅ db.sqlite3 supprimée${NC}"
else
    echo "   ℹ️  Pas de base de données trouvée"
fi

echo ""

# ============================================================================
# 2. NETTOYAGE DES CACHES
# ============================================================================
echo -e "${YELLOW}🗑️  ÉTAPE 2/5 : Nettoyage des caches...${NC}"
echo "--------------------------------------------------------------------------------"

# Cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
echo -e "   ${GREEN}✅ Cache Python nettoyé${NC}"

# Logs
> logs/django.log 2>/dev/null || touch logs/django.log
echo -e "   ${GREEN}✅ Logs nettoyés${NC}"

# Fichiers média (garder .gitkeep)
find media/avatars -type f ! -name ".gitkeep" -delete 2>/dev/null
find media/documents -type f ! -name ".gitkeep" -delete 2>/dev/null
echo -e "   ${GREEN}✅ Fichiers média nettoyés${NC}"

echo ""

# ============================================================================
# 3. SUPPRESSION DES MIGRATIONS (SAUF INITIALES)
# ============================================================================
echo -e "${YELLOW}📋 ÉTAPE 3/5 : Nettoyage des migrations...${NC}"
echo "--------------------------------------------------------------------------------"

for app in accounts academic communication finance; do
    if [ -d "$app/migrations" ]; then
        # Supprimer tous les fichiers sauf __init__.py
        find "$app/migrations" -type f -name "*.py" ! -name "__init__.py" -delete 2>/dev/null
        find "$app/migrations" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        echo -e "   ${GREEN}✅ Migrations de $app nettoyées${NC}"
    fi
done

echo ""

# ============================================================================
# 4. CRÉATION DES NOUVELLES MIGRATIONS
# ============================================================================
echo -e "${YELLOW}🔨 ÉTAPE 4/5 : Création des nouvelles migrations...${NC}"
echo "--------------------------------------------------------------------------------"

uv run python manage.py makemigrations

if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ Migrations créées${NC}"
else
    echo -e "   ${RED}❌ Erreur lors de la création des migrations${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 5. APPLICATION DES MIGRATIONS
# ============================================================================
echo -e "${YELLOW}🚀 ÉTAPE 5/5 : Application des migrations...${NC}"
echo "--------------------------------------------------------------------------------"

uv run python manage.py migrate --noinput

if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ Migrations appliquées${NC}"
else
    echo -e "   ${RED}❌ Erreur lors de l'application des migrations${NC}"
    exit 1
fi

echo ""

# ============================================================================
# RÉSUMÉ
# ============================================================================
echo "================================================================================"
echo -e "${GREEN}✅ BASE DE DONNÉES RÉINITIALISÉE AVEC SUCCÈS${NC}"
echo "================================================================================"
echo ""
echo "📝 Prochaines étapes :"
echo "   1. uv run python scripts/reset_and_populate.py"
echo "   2. uv run python manage.py runserver"
echo ""
echo "================================================================================"
