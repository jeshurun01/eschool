#!/usr/bin/env python3
"""
Test de la nouvelle fonctionnalité de vue détaillée des cours pour les enseignants.
Ce script vérifie que les enseignants peuvent maintenant accéder à une vue spécifique 
de leurs cours au lieu de la vue générale de la classe.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Teacher
from academic.models import TeacherAssignment, Subject, ClassRoom, Level, AcademicYear

User = get_user_model()

def test_course_detail_functionality():
    """Test de la fonctionnalité de détail de cours"""
    
    print("🧪 Test de la vue détaillée des cours enseignant")
    print("=" * 60)
    
    # Créer un client de test
    client = Client()
    
    try:
        # Récupérer un enseignant existant
        teacher = Teacher.objects.select_related('user').first()
        if not teacher:
            print("❌ Aucun enseignant trouvé dans la base de données")
            return False
            
        print(f"👨‍🏫 Enseignant de test: {teacher.user.first_name} {teacher.user.last_name}")
        
        # Se connecter en tant qu'enseignant
        login_success = client.login(
            email=teacher.user.email,  # Utiliser email au lieu de username
            password='teacher123'  # Mot de passe par défaut
        )
        
        if not login_success:
            print("❌ Échec de la connexion de l'enseignant")
            return False
            
        print("✅ Connexion réussie")
        
        # Récupérer les cours de cet enseignant
        assignments = TeacherAssignment.objects.filter(
            teacher=teacher
        ).select_related('subject', 'classroom', 'academic_year')
        
        if not assignments.exists():
            print("❌ Aucun cours assigné à cet enseignant")
            return False
            
        print(f"📚 {assignments.count()} cours trouvés pour cet enseignant")
        
        # Tester l'accès au dashboard enseignant
        dashboard_url = reverse('accounts:teacher_dashboard')
        response = client.get(dashboard_url)
        
        if response.status_code != 200:
            print(f"❌ Erreur d'accès au dashboard: {response.status_code}")
            return False
            
        print("✅ Dashboard enseignant accessible")
        
        # Vérifier que les cours sont listés dans le dashboard
        content = response.content.decode('utf-8')
        if 'Mes Cours' not in content:
            print("❌ Section 'Mes Cours' non trouvée dans le dashboard")
            return False
            
        print("✅ Section 'Mes Cours' trouvée dans le dashboard")
        
        # Tester l'accès à la vue détaillée d'un cours
        first_assignment = assignments.first()
        course_detail_url = reverse('academic:course_detail', args=[first_assignment.id])
        
        print(f"🔍 Test de l'URL: {course_detail_url}")
        print(f"📖 Cours: {first_assignment.subject.name} - {first_assignment.classroom.name}")
        
        response = client.get(course_detail_url)
        
        if response.status_code != 200:
            print(f"❌ Erreur d'accès à la vue de cours: {response.status_code}")
            if hasattr(response, 'context') and response.context and 'exception' in response.context:
                print(f"   Détails: {response.context['exception']}")
            return False
            
        print("✅ Vue détaillée du cours accessible")
        
        # Vérifier le contenu de la page
        content = response.content.decode('utf-8')
        
        # Vérifications du contenu
        checks = [
            (first_assignment.subject.name, "Nom de la matière"),
            (first_assignment.classroom.name, "Nom de la classe"),
            ("Étudiants du cours", "Section étudiants"),
            ("Notes récentes", "Section notes récentes"),
            ("Présences récentes", "Section présences récentes"),
            ("Statistiques du mois", "Section statistiques"),
        ]
        
        all_checks_passed = True
        for check_text, description in checks:
            if check_text in content:
                print(f"✅ {description} trouvée")
            else:
                print(f"❌ {description} manquante")
                all_checks_passed = False
        
        # Tester la sécurité : un enseignant ne peut pas voir les cours d'un autre
        other_assignment = TeacherAssignment.objects.exclude(
            teacher=teacher
        ).first()
        
        if other_assignment:
            unauthorized_url = reverse('academic:course_detail', args=[other_assignment.id])
            response = client.get(unauthorized_url)
            
            if response.status_code == 404:
                print("✅ Sécurité: Accès refusé aux cours d'autres enseignants")
            else:
                print(f"❌ Problème de sécurité: Status {response.status_code} au lieu de 404")
                all_checks_passed = False
        
        # Récapitulatif des tests
        print("\n" + "=" * 60)
        if all_checks_passed:
            print("🎉 TOUS LES TESTS RÉUSSIS!")
            print("✅ La nouvelle fonctionnalité de vue détaillée des cours fonctionne correctement")
            print("✅ Les enseignants peuvent maintenant voir une page spécifique à leurs cours")
            print("✅ La sécurité RBAC est maintenue")
            return True
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
            return False
            
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_navigation_improvements():
    """Test des améliorations de navigation"""
    
    print("\n🔗 Test des améliorations de navigation")
    print("=" * 60)
    
    client = Client()
    
    try:
        # Récupérer un enseignant
        teacher = Teacher.objects.select_related('user').first()
        if not teacher:
            print("❌ Aucun enseignant trouvé")
            return False
        
        # Se connecter
        client.login(email=teacher.user.email, password='teacher123')
        
        # Accéder au dashboard
        dashboard_url = reverse('accounts:teacher_dashboard')
        response = client.get(dashboard_url)
        content = response.content.decode('utf-8')
        
        # Vérifier que les liens "Voir" pointent vers course_detail et non classroom_detail
        assignments = TeacherAssignment.objects.filter(teacher=teacher)
        
        navigation_correct = True
        for assignment in assignments:
            expected_url = reverse('academic:course_detail', args=[assignment.id])
            old_url = reverse('academic:classroom_detail', args=[assignment.classroom.id])
            
            if expected_url in content:
                print(f"✅ Lien correct trouvé pour {assignment.subject.name}")
            else:
                print(f"❌ Lien course_detail manquant pour {assignment.subject.name}")
                navigation_correct = False
                
            if old_url in content and 'Voir' in content:
                print(f"⚠️  Ancien lien classroom_detail encore présent pour {assignment.subject.name}")
                # Ce n'est pas forcément une erreur car il peut y avoir d'autres liens
        
        if navigation_correct:
            print("✅ Navigation mise à jour correctement")
            return True
        else:
            print("❌ Problèmes de navigation détectés")
            return False
            
    except Exception as e:
        print(f"❌ Erreur durant le test de navigation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTS DE LA NOUVELLE FONCTIONNALITÉ COURSE DETAIL")
    print("=" * 70)
    
    # Test principal
    test1_success = test_course_detail_functionality()
    
    # Test de navigation
    test2_success = test_navigation_improvements()
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS FINAUX:")
    
    if test1_success and test2_success:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ La fonctionnalité est prête pour la production")
        sys.exit(0)
    else:
        print("❌ ÉCHEC DE CERTAINS TESTS")
        print("⚠️  Vérification manuelle recommandée")
        sys.exit(1)
