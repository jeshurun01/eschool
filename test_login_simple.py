#!/usr/bin/env python
"""
Test simple de connexion par étapes
"""

import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class LoginTestCase(TestCase):
    def setUp(self):
        """Créer un utilisateur de test"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='STUDENT'
        )

    def test_login_page_loads(self):
        """Test que la page de connexion se charge"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'email')
        print("✅ Page de connexion chargée")

    def test_login_with_valid_credentials(self):
        """Test connexion avec des identifiants valides"""
        response = self.client.post('/accounts/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        print(f"📊 Status code: {response.status_code}")
        if response.status_code == 302:
            print("✅ Connexion réussie - Redirection")
            print(f"📊 Redirect location: {response['Location']}")
        else:
            print("❌ Connexion échouée")
            if hasattr(response, 'context') and response.context:
                form = response.context.get('form')
                if form and form.errors:
                    print("❌ Erreurs du formulaire:")
                    for field, errors in form.errors.items():
                        print(f"   - {field}: {errors}")

    def test_login_with_invalid_credentials(self):
        """Test connexion avec des identifiants invalides"""
        response = self.client.post('/accounts/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        print("✅ Échec de connexion avec mauvais mot de passe - Reste sur la page")

if __name__ == '__main__':
    import unittest
    
    # Configurer Django pour les tests
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Créer un test runner
    test_runner = get_runner(settings)()
    
    # Exécuter les tests
    suite = unittest.TestLoader().loadTestsFromTestCase(LoginTestCase)
    result = test_runner.run_tests(['__main__'])
    
    if result == 0:
        print("\n✅ Tous les tests sont passés")
    else:
        print(f"\n❌ {result} test(s) ont échoué")
