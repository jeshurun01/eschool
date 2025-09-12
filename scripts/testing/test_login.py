#!/usr/bin/env python
"""
Script de test de connexion pour vérifier les credentials
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

def test_login_credentials():
    """Test complet des credentials de connexion"""
    
    print("🧪 Test des credentials de connexion")
    print("=" * 50)
    
    test_emails = [
        "nasser@eschool.com",
        "admin@eschool.com"
    ]
    
    test_password = "admin123"
    
    for email in test_emails:
        print(f"\n📧 Test pour: {email}")
        
        try:
            # Vérifier que l'utilisateur existe
            user = User.objects.get(email=email)
            print(f"  ✅ Utilisateur trouvé: {user.first_name} {user.last_name}")
            print(f"  📋 Role: {user.role}")
            print(f"  🔓 Actif: {user.is_active}")
            print(f"  👑 Staff: {user.is_staff}")
            
            # Vérifier le hash du mot de passe
            password_valid = check_password(test_password, user.password)
            print(f"  🔑 Hash mot de passe valide: {password_valid}")
            
            # Tester l'authentification Django
            auth_user = authenticate(email=email, password=test_password)
            if auth_user:
                print(f"  ✅ Authentification Django: SUCCÈS")
            else:
                print(f"  ❌ Authentification Django: ÉCHEC")
                
        except User.DoesNotExist:
            print(f"  ❌ Utilisateur non trouvé: {email}")
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CREDENTIALS À UTILISER:")
    print("  Email: nasser@eschool.com")
    print("  Mot de passe: admin123")
    print("\n  OU")
    print("  Email: admin@eschool.com")
    print("  Mot de passe: admin123")
    print("=" * 50)

if __name__ == '__main__':
    test_login_credentials()
