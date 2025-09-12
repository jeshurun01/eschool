#!/usr/bin/env python
"""
Test final du filtrage RBAC pour attendance_list
Vérifier que les enseignants ne voient que leurs classes
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from accounts.models import Teacher
from academic.models import TeacherAssignment, ClassRoom

User = get_user_model()

def test_attendance_list_filtering():
    """Test final du filtrage des classes dans attendance_list"""
    
    print("=== Test final du filtrage RBAC attendance_list ===\n")
    
    # Créer un client de test
    client = Client()
    
    # Test avec Marie Dupont
    teacher = Teacher.objects.get(employee_id='T1000')  # Marie Dupont
    print(f"Test avec l'enseignant: {teacher.user.get_full_name()}")
    
    # Se connecter
    login_success = client.login(username=teacher.user.email, password='password123')
    print(f"Connexion réussie: {login_success}")
    
    if login_success:
        # Accéder à la page de présences
        response = client.get('/academic/attendance/')
        print(f"Status de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            # Analyser le contenu HTML pour voir quelles classes sont affichées
            content = response.content.decode('utf-8')
            
            # Classes assignées à Marie Dupont
            marie_assignments = TeacherAssignment.objects.filter(
                teacher=teacher,
                academic_year__is_current=True
            ).select_related('classroom')
            
            marie_classrooms = [a.classroom for a in marie_assignments]
            
            print(f"Classes assignées à Marie Dupont: {len(marie_classrooms)}")
            for classroom in marie_classrooms:
                print(f"  - {classroom.name}")
            
            # Toutes les autres classes
            all_classrooms = ClassRoom.objects.filter(academic_year__is_current=True)
            other_classrooms = all_classrooms.exclude(
                id__in=[c.id for c in marie_classrooms]
            )
            
            print(f"Autres classes dans le système: {other_classrooms.count()}")
            
            # Vérifier que seules les classes de Marie sont dans le HTML
            print("\nVérification du contenu HTML:")
            marie_classes_found = 0
            other_classes_found = 0
            
            for classroom in marie_classrooms:
                if classroom.name in content:
                    marie_classes_found += 1
                    print(f"  ✅ Classe de Marie trouvée: {classroom.name}")
                else:
                    print(f"  ❌ Classe de Marie manquante: {classroom.name}")
            
            for classroom in other_classrooms[:5]:  # Test 5 autres classes
                if classroom.name in content:
                    other_classes_found += 1
                    print(f"  ❌ Classe non autorisée trouvée: {classroom.name}")
            
            # Résultat du test
            print(f"\nRésultat du filtrage:")
            print(f"  Classes de Marie visibles: {marie_classes_found}/{len(marie_classrooms)}")
            print(f"  Classes non autorisées visibles: {other_classes_found}")
            
            if marie_classes_found == len(marie_classrooms) and other_classes_found == 0:
                print("  ✅ FILTRAGE RBAC PARFAIT!")
            elif marie_classes_found == len(marie_classrooms):
                print("  ✅ Toutes les classes de Marie sont visibles")
                print("  ⚠️  Vérifier si d'autres classes non autorisées sont visibles")
            else:
                print("  ❌ Problème de filtrage détecté")
        
        else:
            print(f"❌ Erreur d'accès à la page: {response.status_code}")
    
    else:
        print("❌ Échec de la connexion")

if __name__ == '__main__':
    test_attendance_list_filtering()
