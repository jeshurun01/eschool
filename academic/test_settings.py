"""
Configuration de test pour le module academic
"""
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test.utils import override_settings

# Configuration de test optimisée
TEST_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'PASSWORD_HASHERS': [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ],
    'MEDIA_ROOT': '/tmp/test_media',
    'STATIC_ROOT': '/tmp/test_static',
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    'USE_TZ': True,
    'TIME_ZONE': 'UTC',
}


class AcademicTestMixin:
    """Mixin pour les tests académiques avec configuration commune"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer les tables de test
        call_command('migrate', verbosity=0, interactive=False)
    
    @classmethod
    def tearDownClass(cls):
        # Nettoyer les tables de test
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS academic_academicyear CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_level CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_subject CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_classroom CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_enrollment CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_grade CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_attendance CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_document CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_timetable CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_teacherassignment CASCADE")
            cursor.execute("DROP TABLE IF EXISTS academic_period CASCADE")
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        # Configuration commune pour tous les tests
        self.maxDiff = None  # Pour voir les différences complètes dans les assertions


class AcademicTestCase(AcademicTestMixin, TestCase):
    """Classe de base pour tous les tests académiques"""
    pass


def run_academic_tests():
    """Fonction utilitaire pour exécuter tous les tests académiques"""
    import subprocess
    import sys
    
    test_files = [
        'academic.test_models',
        'academic.test_managers', 
        'academic.test_views',
        'academic.test_integration'
    ]
    
    results = []
    for test_file in test_files:
        try:
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', test_file,
                '--verbosity=2', '--keepdb'
            ], capture_output=True, text=True)
            results.append({
                'file': test_file,
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr
            })
        except Exception as e:
            results.append({
                'file': test_file,
                'success': False,
                'output': '',
                'errors': str(e)
            })
    
    return results


def print_test_results(results):
    """Affiche les résultats des tests de manière formatée"""
    print("\n" + "="*80)
    print("RÉSULTATS DES TESTS ACADÉMIQUES")
    print("="*80)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    
    print(f"\nTotal des fichiers de test: {total_tests}")
    print(f"Tests réussis: {successful_tests}")
    print(f"Tests échoués: {total_tests - successful_tests}")
    print(f"Taux de réussite: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n" + "-"*80)
    print("DÉTAIL PAR FICHIER")
    print("-"*80)
    
    for result in results:
        status = "✅ RÉUSSI" if result['success'] else "❌ ÉCHOUÉ"
        print(f"\n{result['file']}: {status}")
        
        if result['output']:
            print("Sortie:")
            print(result['output'][-500:])  # Derniers 500 caractères
        
        if result['errors']:
            print("Erreurs:")
            print(result['errors'][-500:])  # Derniers 500 caractères
    
    print("\n" + "="*80)
    return successful_tests == total_tests


if __name__ == "__main__":
    # Exécuter les tests si le script est appelé directement
    results = run_academic_tests()
    success = print_test_results(results)
    exit(0 if success else 1)
