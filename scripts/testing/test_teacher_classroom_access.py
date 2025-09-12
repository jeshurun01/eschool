#!/usr/bin/env python3
"""
Test d'accès aux classes pour les enseignants
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import Teacher
from academic.models import TeacherAssignment

def test_teacher_classroom_access():
    """Test que les enseignants peuvent accéder aux classes où ils enseignent"""
    
    print("🧪 Test d'accès aux classes pour les enseignants")
    print("=" * 60)
    
    client = Client()
    
    try:
        # Récupérer un enseignant avec des assignments
        teacher = Teacher.objects.prefetch_related('teacherassignment_set').first()
        if not teacher:
            print("❌ Aucun enseignant trouvé")
            return False
            
        print(f"👨‍🏫 Enseignant: {teacher.user.first_name} {teacher.user.last_name}")
        
        # Se connecter
        login_success = client.login(email=teacher.user.email, password='teacher123')
        if not login_success:
            print("❌ Échec de connexion")
            return False
            
        print("✅ Connexion réussie")
        
        # Récupérer les classes où cet enseignant enseigne
        assignments = TeacherAssignment.objects.filter(teacher=teacher)
        
        if not assignments.exists():
            print("❌ Aucun assignment trouvé pour cet enseignant")
            return False
            
        print(f"📚 {assignments.count()} classes assignées")
        
        # Tester l'accès à chaque classe
        all_access_ok = True
        
        for assignment in assignments[:3]:  # Tester max 3 classes
            classroom = assignment.classroom
            classroom_url = reverse('academic:classroom_detail', args=[classroom.id])
            
            print(f"🏫 Test classe: {classroom.name}")
            print(f"   URL: {classroom_url}")
            
            response = client.get(classroom_url)
            
            if response.status_code == 200:
                print(f"   ✅ Accès autorisé (200)")
            elif response.status_code == 302:
                print(f"   ⚠️  Redirection (302) - vérifier la destination")
                print(f"       Redirect to: {response.get('Location', 'Unknown')}")
                if 'dashboard' in response.get('Location', ''):
                    print("   ❌ Redirection vers dashboard - accès refusé")
                    all_access_ok = False
            elif response.status_code == 403:
                print(f"   ❌ Accès interdit (403)")
                all_access_ok = False
            elif response.status_code == 404:
                print(f"   ❌ Classe non trouvée (404)")
                all_access_ok = False
            else:
                print(f"   ❌ Erreur inattendue ({response.status_code})")
                all_access_ok = False
        
        # Tester l'accès à une classe où l'enseignant n'enseigne PAS
        other_classrooms = TeacherAssignment.objects.exclude(
            teacher=teacher
        ).values_list('classroom_id', flat=True).distinct()
        
        if other_classrooms:
            unauthorized_classroom_id = other_classrooms[0]
            unauthorized_url = reverse('academic:classroom_detail', args=[unauthorized_classroom_id])
            
            print(f"\n🚫 Test accès non autorisé à la classe ID {unauthorized_classroom_id}")
            response = client.get(unauthorized_url)
            
            if response.status_code in [302, 403]:
                print("   ✅ Accès correctement refusé")
            else:
                print(f"   ❌ Accès autorisé alors qu'il ne devrait pas ({response.status_code})")
                all_access_ok = False
        
        print("\n" + "=" * 60)
        if all_access_ok:
            print("🎉 TOUS LES TESTS RÉUSSIS!")
            print("✅ Les enseignants peuvent accéder à leurs classes")
            print("✅ L'accès est correctement refusé aux autres classes")
            return True
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
            print("⚠️  Problème d'accès détecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_teacher_classroom_access()
    sys.exit(0 if success else 1)
