#!/usr/bin/env python3

# Test simple de la fonction announcement_list

import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print("=== Test du module communication.views ===")

try:
    # Import du module
    from communication import views
    print("✓ Module importé avec succès")
    
    # Vérification des fonctions
    functions = [name for name in dir(views) if not name.startswith('_')]
    print(f"✓ Fonctions disponibles ({len(functions)}): {functions}")
    
    # Test spécifique de announcement_list
    if hasattr(views, 'announcement_list'):
        print("✓ announcement_list existe")
        print(f"✓ Type: {type(views.announcement_list)}")
    else:
        print("✗ announcement_list n'existe pas")
        
    # Test d'import direct
    try:
        from communication.views import announcement_list
        print("✓ Import direct de announcement_list réussi")
    except ImportError as e:
        print(f"✗ Import direct échoué: {e}")
        
except Exception as e:
    print(f"✗ Erreur lors de l'import: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test d'exécution directe du fichier ===")
try:
    # Lecture et exécution du contenu du fichier
    with open('/home/jeshurun-nasser/dev/py/django-app/eschool/communication/views.py', 'r') as f:
        content = f.read()
    
    print(f"✓ Fichier lu ({len(content)} caractères)")
    
    # Créer un namespace pour l'exécution
    namespace = {}
    exec(content, namespace)
    
    functions_in_namespace = [name for name in namespace.keys() if not name.startswith('_') and callable(namespace.get(name))]
    print(f"✓ Fonctions définies dans le namespace ({len(functions_in_namespace)}): {functions_in_namespace}")
    
    if 'announcement_list' in namespace:
        print("✓ announcement_list définie dans le namespace")
    else:
        print("✗ announcement_list non définie dans le namespace")
        
except Exception as e:
    print(f"✗ Erreur lors de l'exécution: {e}")
    import traceback
    traceback.print_exc()
