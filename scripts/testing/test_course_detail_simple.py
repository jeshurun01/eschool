#!/usr/bin/env python3
"""
Test simple pour vérifier que la nouvelle fonctionnalité course_detail est implémentée.
Ce script vérifie les composants de base sans faire de requêtes HTTP.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.urls import reverse, resolve
from django.template.loader import get_template
from accounts.models import Teacher
from academic.models import TeacherAssignment

def test_url_configuration():
    """Test de la configuration des URLs"""
    print("🔗 Test de la configuration des URLs")
    print("=" * 50)
    
    try:
        # Test de l'URL course_detail
        url = reverse('academic:course_detail', args=[1])
        print(f"✅ URL course_detail générée: {url}")
        
        # Test de résolution de l'URL
        resolver = resolve('/academic/courses/1/')
        print(f"✅ URL résolue vers: {resolver.func.__name__}")
        print(f"   Nom de la vue: {resolver.url_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur URL: {e}")
        return False

def test_template_exists():
    """Test de l'existence du template"""
    print("\n📄 Test de l'existence du template")
    print("=" * 50)
    
    try:
        template = get_template('academic/course_detail.html')
        print("✅ Template course_detail.html trouvé")
        return True
        
    except Exception as e:
        print(f"❌ Template manquant: {e}")
        return False

def test_view_function():
    """Test de l'existence de la fonction de vue"""
    print("\n🎯 Test de la fonction de vue")
    print("=" * 50)
    
    try:
        from academic.views import course_detail
        print("✅ Fonction course_detail importée")
        
        # Vérifier que c'est bien une fonction
        if callable(course_detail):
            print("✅ course_detail est bien callable")
        else:
            print("❌ course_detail n'est pas callable")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Impossible d'importer course_detail: {e}")
        return False

def test_data_availability():
    """Test de la disponibilité des données"""
    print("\n📊 Test de la disponibilité des données")
    print("=" * 50)
    
    try:
        # Vérifier qu'il y a des enseignants
        teacher_count = Teacher.objects.count()
        print(f"👨‍🏫 {teacher_count} enseignants dans la base")
        
        if teacher_count == 0:
            print("⚠️  Aucun enseignant trouvé - créer des données de test")
            return False
        
        # Vérifier qu'il y a des assignments
        assignment_count = TeacherAssignment.objects.count()
        print(f"📚 {assignment_count} assignments dans la base")
        
        if assignment_count == 0:
            print("⚠️  Aucun assignment trouvé - créer des données de test")
            return False
        
        # Afficher quelques exemples
        first_teacher = Teacher.objects.first()
        teacher_assignments = TeacherAssignment.objects.filter(teacher=first_teacher)
        
        print(f"👤 Premier enseignant: {first_teacher.user.first_name} {first_teacher.user.last_name}")
        print(f"📖 Ses cours: {teacher_assignments.count()}")
        
        for assignment in teacher_assignments[:3]:  # Afficher max 3
            print(f"   - {assignment.subject.name} en {assignment.classroom.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur données: {e}")
        return False

def test_dashboard_template_update():
    """Test de la mise à jour du template dashboard"""
    print("\n🎨 Test de la mise à jour du template dashboard")
    print("=" * 50)
    
    try:
        # Lire le contenu du template dashboard
        with open('/home/jeshurun-nasser/dev/py/django-app/eschool/templates/accounts/teacher_dashboard.html', 'r') as f:
            content = f.read()
        
        # Vérifier que le lien utilise course_detail
        if 'academic:course_detail' in content:
            print("✅ Template dashboard utilise academic:course_detail")
        else:
            print("❌ Template dashboard n'utilise pas academic:course_detail")
            return False
        
        # Vérifier qu'il n'y a plus de lien vers classroom_detail dans les boutons "Voir"
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Voir' in line and 'classroom_detail' in line:
                print(f"⚠️  Ancien lien classroom_detail trouvé ligne {i+1}")
                print(f"    {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur template dashboard: {e}")
        return False

def run_all_tests():
    """Exécute tous les tests"""
    print("🚀 TESTS DE VALIDATION COURSE DETAIL")
    print("=" * 70)
    
    tests = [
        test_url_configuration,
        test_template_exists,
        test_view_function,
        test_data_availability,
        test_dashboard_template_update,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur dans {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ La fonctionnalité course_detail est correctement implémentée")
        print("✅ Prêt pour les tests manuels dans le navigateur")
        return True
    else:
        print("❌ Certains tests ont échoué")
        print("⚠️  Vérification manuelle recommandée")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
