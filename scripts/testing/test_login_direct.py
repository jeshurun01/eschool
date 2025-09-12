#!/usr/bin/env python
"""
Test de connexion direct avec requête POST
"""

import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from accounts.models import User

def test_login_direct():
    """Test direct de connexion"""
    print("🔍 Test de connexion directe...")
    
    # Vérifier que l'utilisateur existe
    try:
        user = User.objects.get(email='nasser@eschool.com')
        print(f"✅ Utilisateur trouvé: {user}")
    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")
        return
    
    # Test d'authentification directe
    auth_user = authenticate(username='nasser@eschool.com', password='admin123')
    if auth_user:
        print("✅ Authentification directe réussie")
    else:
        print("❌ Authentification directe échouée")
        return
    
    # Test avec le client Django
    client = Client()
    
    # D'abord, récupérer la page de connexion pour obtenir le token CSRF
    print("\n🔍 Récupération de la page de connexion...")
    response = client.get('/accounts/login/')
    print(f"📊 GET /accounts/login/ : {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Impossible d'accéder à la page de connexion")
        return
    
    # Extraire le token CSRF
    csrf_token = None
    if hasattr(response, 'context') and response.context:
        csrf_token = response.context.get('csrf_token')
    
    # Si pas de contexte, essayer d'extraire du contenu HTML
    if not csrf_token:
        content = response.content.decode()
        import re
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', content)
        if csrf_match:
            csrf_token = csrf_match.group(1)
    
    print(f"📊 Token CSRF: {'Trouvé' if csrf_token else 'Non trouvé'}")
    
    # Test POST avec données de connexion
    print("\n🔍 Test POST de connexion...")
    post_data = {
        'email': 'nasser@eschool.com',
        'password': 'admin123'
    }
    
    if csrf_token:
        post_data['csrfmiddlewaretoken'] = csrf_token
    
    response = client.post('/accounts/login/', post_data, follow=False)
    print(f"📊 POST /accounts/login/ : {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Connexion réussie - Redirection")
        print(f"📊 Redirection vers: {response['Location']}")
    elif response.status_code == 200:
        print("❌ Connexion échouée - Reste sur la page")
        
        # Essayer d'extraire les erreurs du formulaire
        content = response.content.decode()
        if 'Erreur de connexion' in content:
            print("📊 Message d'erreur détecté dans la page")
        
        # Vérifier si le formulaire a des erreurs
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and hasattr(form, 'errors') and form.errors:
                print("❌ Erreurs du formulaire:")
                for field, errors in form.errors.items():
                    print(f"   - {field}: {errors}")
    else:
        print(f"❌ Erreur inattendue: {response.status_code}")

if __name__ == '__main__':
    test_login_direct()
