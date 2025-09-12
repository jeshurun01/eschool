#!/usr/bin/env python3
"""
Test de l'authentification requise pour les vues de présence
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_attendance_authentication():
    """Test que l'authentification est requise pour les vues de présence"""
    print("🔐 Test d'authentification pour les vues de présence")
    print("=" * 60)
    
    client = Client()
    
    # URLs à tester
    urls_to_test = [
        ('/academic/attendance/', 'Liste des présences'),
        ('/academic/attendance/take/', 'Faire l\'appel'),
        ('/academic/attendance/class/1/', 'Présences de classe'),
    ]
    
    print("📝 Test sans authentification:")
    for url, description in urls_to_test:
        try:
            response = client.get(url)
            
            if response.status_code == 302:
                # Redirection vers login
                location = response.get('Location', '')
                if 'login' in location:
                    print(f"✅ {description}: Redirection vers login (sécurisé)")
                else:
                    print(f"⚠️  {description}: Redirection vers {location}")
            elif response.status_code == 200:
                print(f"❌ {description}: Accès autorisé sans connexion!")
            elif response.status_code == 403:
                print(f"✅ {description}: Accès interdit (403)")
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: Erreur {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RÉSULTAT:")
    print("Les vues de présence devraient maintenant exiger une authentification.")
    print("Toutes les réponses devraient être des redirections vers /login/")

if __name__ == "__main__":
    test_attendance_authentication()
