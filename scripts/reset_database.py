#!/usr/bin/env python
"""
Script simple pour nettoyer la base de données SQLite
Usage: python scripts/reset_database.py
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

print("=" * 80)
print("🗑️  NETTOYAGE COMPLET DE LA BASE DE DONNÉES")
print("=" * 80)
print()
print("⚠️  ATTENTION: Cette opération va SUPPRIMER toutes les données!")
print()

response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")

if response.lower() not in ['oui', 'yes', 'y']:
    print("❌ Opération annulée.")
    sys.exit(0)

print()
print("🧹 Nettoyage en cours...")
print()

# Obtenir toutes les tables
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Désactiver les contraintes de clés étrangères temporairement
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Supprimer le contenu de toutes les tables sauf django_migrations
    for table in tables:
        table_name = table[0]
        if not table_name.startswith('sqlite_') and table_name != 'django_migrations':
            try:
                cursor.execute(f"DELETE FROM {table_name};")
                print(f"   ✅ Table '{table_name}' vidée")
            except Exception as e:
                print(f"   ⚠️  Erreur lors du nettoyage de '{table_name}': {str(e)}")
    
    # Réactiver les contraintes
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Commit les changements
    connection.commit()

print()
print("✅ Base de données nettoyée avec succès!")
print()
print("📝 Prochaines étapes:")
print("   1. Exécutez: python scripts/reset_and_populate.py")
print("   2. Ou créez un superutilisateur: python manage.py createsuperuser")
print()
