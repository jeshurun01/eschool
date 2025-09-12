#!/usr/bin/env python
"""
Test de l'API AJAX pour récupérer les élèves d'une classe
Vérifier que chaque classe retourne ses propres élèves
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from accounts.models import Teacher
from academic.models import ClassRoom, TeacherAssignment, Enrollment

User = get_user_model()

def test_classroom_students_api():
    """Test de l'API pour récupérer les élèves par classe"""
    
    print("=== Test de l'API get_classroom_students ===\n")
    
    # Créer un client de test
    client = Client()
    
    # Prendre Marie Dupont
    teacher = Teacher.objects.get(employee_id='T1000')  # Marie Dupont
    print(f"Test avec l'enseignant: {teacher.user.get_full_name()}")
    
    # Se connecter
    login_success = client.login(username=teacher.user.email, password='password123')
    print(f"Connexion réussie: {login_success}")
    
    if not login_success:
        print("❌ Échec de la connexion - Impossible de continuer le test")
        return
    
    # Récupérer les classes assignées à Marie
    marie_assignments = TeacherAssignment.objects.filter(
        teacher=teacher,
        academic_year__is_current=True
    ).select_related('classroom')
    
    marie_classrooms = [a.classroom for a in marie_assignments]
    print(f"\nClasses assignées à Marie Dupont: {len(marie_classrooms)}")
    
    for classroom in marie_classrooms:
        print(f"\n--- Test de la classe: {classroom.name} (ID: {classroom.id}) ---")
        
        # Appel API
        response = client.get(f'/academic/api/classroom/{classroom.id}/students/')
        print(f"Status de l'API: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    students = data.get('students', [])
                    print(f"✅ API réussie - {len(students)} élèves récupérés")
                    
                    # Afficher quelques élèves
                    for i, student in enumerate(students[:3]):
                        print(f"  {i+1}. {student['name']} (Matricule: {student['matricule']})")
                    
                    if len(students) > 3:
                        print(f"  ... et {len(students) - 3} autres élèves")
                    
                    # Vérifier contre les enrollments réels
                    real_enrollments = Enrollment.objects.filter(
                        classroom=classroom,
                        is_active=True
                    ).count()
                    
                    if len(students) == real_enrollments:
                        print(f"  ✅ Nombre d'élèves cohérent avec les enrollments ({real_enrollments})")
                    else:
                        print(f"  ⚠️  Incohérence: API={len(students)}, DB={real_enrollments}")
                    
                else:
                    print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
                    
            except json.JSONDecodeError:
                print("❌ Réponse JSON invalide")
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    
    # Test avec une classe non autorisée
    print(f"\n--- Test d'accès non autorisé ---")
    marie_classroom_ids = [c.id for c in marie_classrooms]
    unauthorized_classroom = ClassRoom.objects.filter(
        academic_year__is_current=True
    ).exclude(id__in=marie_classroom_ids).first()
    
    if unauthorized_classroom:
        print(f"Test d'accès à la classe non autorisée: {unauthorized_classroom.name}")
        response = client.get(f'/academic/api/classroom/{unauthorized_classroom.id}/students/')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Accès refusé correctement (403 Forbidden)")
        else:
            print(f"❌ Accès autorisé de manière inattendue: {response.status_code}")
            
    else:
        print("ℹ️  Aucune classe non autorisée trouvée (Marie enseigne partout)")

    # Test avec Jean Martin pour comparaison
    print(f"\n--- Test comparatif avec Jean Martin ---")
    jean = Teacher.objects.get(employee_id='T1001')  # Jean Martin
    client.logout()
    jean_login = client.login(username=jean.user.email, password='password123')
    
    if jean_login:
        jean_assignments = TeacherAssignment.objects.filter(
            teacher=jean,
            academic_year__is_current=True
        ).select_related('classroom')
        
        jean_classrooms = [a.classroom for a in jean_assignments]
        print(f"Classes de Jean Martin: {[c.name for c in jean_classrooms]}")
        
        if jean_classrooms:
            test_classroom = jean_classrooms[0]
            response = client.get(f'/academic/api/classroom/{test_classroom.id}/students/')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    jean_students = data.get('students', [])
                    print(f"Jean voit {len(jean_students)} élèves dans {test_classroom.name}")
                    
                    # Comparer avec Marie
                    marie_test_classroom = marie_classrooms[0] if marie_classrooms else None
                    if marie_test_classroom and marie_test_classroom.id != test_classroom.id:
                        print("✅ Jean et Marie voient des classes différentes (bon isolement)")
                    else:
                        print("ℹ️  Jean et Marie partagent des classes")

if __name__ == '__main__':
    test_classroom_students_api()
