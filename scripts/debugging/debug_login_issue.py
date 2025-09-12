#!/usr/bin/env python
"""
Script de débogage pour identifier le problème de connexion
"""

import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import authenticate, login
from accounts.models import User
from accounts.forms import CustomLoginForm
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.middleware.csrf import CsrfViewMiddleware

def test_custom_login_form():
    """Test du formulaire de connexion personnalisé"""
    print("🔍 Test du formulaire CustomLoginForm...")
    
    # Données de test
    form_data = {
        'email': 'nasser@eschool.com',
        'password': 'admin123'
    }
    
    # Test 1: Créer une requête mock
    factory = RequestFactory()
    request = factory.post('/accounts/login/', form_data)
    
    # Ajouter les middlewares nécessaires
    SessionMiddleware(lambda x: None).process_request(request)
    request.session.save()
    
    # Test 2: Initialiser le formulaire avec la requête
    print(f"📝 Données du formulaire: {form_data}")
    
    try:
        form = CustomLoginForm(request, data=form_data)
        print(f"✅ Formulaire créé: {form}")
        print(f"📊 Form.is_bound: {form.is_bound}")
        print(f"📊 Form.data: {form.data}")
        
        # Validation
        is_valid = form.is_valid()
        print(f"✅ Form.is_valid(): {is_valid}")
        
        if not is_valid:
            print(f"❌ Erreurs du formulaire:")
            for field, errors in form.errors.items():
                print(f"   - {field}: {errors}")
            
            if form.non_field_errors():
                print(f"   - Erreurs non-field: {form.non_field_errors()}")
        else:
            user = form.get_user()
            print(f"✅ Utilisateur récupéré: {user}")
            print(f"📊 User.is_active: {user.is_active}")
            print(f"📊 User.backend: {getattr(user, 'backend', 'Non défini')}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du formulaire: {e}")
        import traceback
        traceback.print_exc()

def test_with_django_client():
    """Test avec le client Django"""
    print("\n🔍 Test avec le client Django...")
    
    client = Client()
    
    # Test GET sur la page de connexion
    response = client.get('/accounts/login/')
    print(f"📊 GET /accounts/login/ - Status: {response.status_code}")
    
    # Test POST avec les données de connexion
    form_data = {
        'email': 'nasser@eschool.com',
        'password': 'admin123'
    }
    
    response = client.post('/accounts/login/', form_data)
    print(f"📊 POST /accounts/login/ - Status: {response.status_code}")
    print(f"📊 Response redirect: {response.get('Location', 'Pas de redirection')}")
    
    if response.status_code == 200:
        print("❌ Connexion échouée - Reste sur la page de login")
        # Chercher des erreurs dans le contexte
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and form.errors:
                print(f"❌ Erreurs du formulaire dans la réponse:")
                for field, errors in form.errors.items():
                    print(f"   - {field}: {errors}")
    elif response.status_code == 302:
        print("✅ Connexion réussie - Redirection")

def test_user_details():
    """Affiche les détails de l'utilisateur"""
    print("\n🔍 Détails de l'utilisateur...")
    
    try:
        user = User.objects.get(email='nasser@eschool.com')
        print(f"✅ Utilisateur trouvé: {user}")
        print(f"📊 ID: {user.id}")
        print(f"📊 Email: {user.email}")
        print(f"📊 Is_active: {user.is_active}")
        print(f"📊 Is_staff: {user.is_staff}")
        print(f"📊 Is_superuser: {user.is_superuser}")
        print(f"📊 Role: {user.role}")
        print(f"📊 Password starts with: {user.password[:10]}...")
        
        # Test du mot de passe
        from django.contrib.auth.hashers import check_password
        password_ok = check_password('admin123', user.password)
        print(f"📊 Mot de passe correct: {password_ok}")
        
    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")

if __name__ == '__main__':
    print("🚀 Démarrage du débogage de connexion")
    print("=" * 50)
    
    test_user_details()
    test_custom_login_form()
    test_with_django_client()
    
    print("\n" + "=" * 50)
    print("✅ Débogage terminé")
