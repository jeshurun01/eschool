#!/usr/bin/env python
"""
Test du système de prise de présence avec RBAC
Vérifier que seuls les enseignants peuvent prendre les présences
pour leurs propres élèves.
"""

import os
import django
import sys
from datetime import datetime, date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from accounts.models import Teacher, Student
from academic.models import (
    ClassRoom, Subject, TeacherAssignment, Enrollment, 
    Attendance, Level, AcademicYear
)

User = get_user_model()

def test_attendance_take_rbac():
    """Test du système de prise de présence avec contrôle d'accès"""
    
    print("=== Test du système de prise de présence avec RBAC ===\n")
    
    # Créer un client de test
    client = Client()
    
    # Test 1: Accès sans authentification
    print("1. Test d'accès sans authentification...")
    response = client.get('/academic/attendance/take/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirection vers: {response.url}")
        print("   ✅ Redirection vers login (sécurisé)")
    else:
        print("   ❌ Accès autorisé sans authentification")
    print()
    
    # Test 2: Authentification en tant qu'enseignant
    print("2. Test d'authentification en tant qu'enseignant...")
    try:
        # Prendre le premier enseignant disponible
        teacher = Teacher.objects.select_related('user').first()
        if not teacher:
            print("   ❌ Aucun enseignant trouvé")
            return
            
        print(f"   Enseignant: {teacher.user.get_full_name()} ({teacher.user.username})")
        
        # Se connecter
        login_success = client.login(username=teacher.user.username, password='password123')
        print(f"   Login réussi: {login_success}")
        
        if login_success:
            # Accéder à la page de prise de présence
            response = client.get('/academic/attendance/take/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Accès autorisé pour l'enseignant")
            else:
                print(f"   ❌ Accès refusé: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()
    
    # Test 3: Vérification du filtrage des classes
    print("3. Test du filtrage des classes par enseignant...")
    try:
        if teacher and login_success:
            # Récupérer les assignations de l'enseignant
            assignments = TeacherAssignment.objects.filter(
                teacher=teacher,
                academic_year__is_current=True
            ).select_related('classroom', 'subject')
            
            print(f"   Assignations de l'enseignant {teacher.user.get_full_name()}:")
            for assignment in assignments:
                print(f"     - {assignment.classroom.name} - {assignment.subject.name}")
            
            # Accéder à la page et vérifier le contenu
            response = client.get('/academic/attendance/take/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Vérifier que seules les classes de l'enseignant sont affichées
                all_classrooms = ClassRoom.objects.filter(academic_year__is_current=True)
                teacher_classrooms = [a.classroom for a in assignments]
                
                print(f"   Total des classes dans le système: {all_classrooms.count()}")
                print(f"   Classes assignées à l'enseignant: {len(teacher_classrooms)}")
                
                # Test simple de présence du nom des classes
                for classroom in teacher_classrooms:
                    if classroom.name in content:
                        print(f"     ✅ Classe {classroom.name} visible")
                    else:
                        print(f"     ❌ Classe {classroom.name} non visible")
                        
            else:
                print(f"   ❌ Impossible d'accéder à la page: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()
    
    # Test 4: Test de soumission d'un appel pour une classe non autorisée
    print("4. Test de soumission pour une classe non autorisée...")
    try:
        if teacher and login_success:
            # Trouver une classe où l'enseignant n'enseigne pas
            assigned_classroom_ids = assignments.values_list('classroom_id', flat=True)
            other_classroom = ClassRoom.objects.filter(
                academic_year__is_current=True
            ).exclude(id__in=assigned_classroom_ids).first()
            
            if other_classroom:
                print(f"   Tentative d'appel pour la classe non autorisée: {other_classroom.name}")
                
                # Tenter de soumettre un appel
                post_data = {
                    'classroom': other_classroom.id,
                    'subject': Subject.objects.first().id if Subject.objects.exists() else '',
                    'date': date.today().strftime('%Y-%m-%d'),
                }
                
                response = client.post('/academic/attendance/take/', data=post_data)
                print(f"   Status de la soumission: {response.status_code}")
                
                # Vérifier la redirection et les messages
                if response.status_code == 302:
                    print("   ✅ Redirection effectuée (probablement avec message d'erreur)")
                else:
                    print(f"   ❌ Réponse inattendue: {response.status_code}")
                    
            else:
                print("   ℹ️  Aucune classe non autorisée trouvée (enseignant enseigne partout)")
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()
    
    # Test 5: Test avec un étudiant
    print("5. Test d'accès en tant qu'étudiant...")
    try:
        # Se déconnecter
        client.logout()
        
        # Prendre un étudiant
        student = Student.objects.select_related('user').first()
        if student:
            print(f"   Étudiant: {student.user.get_full_name()} ({student.user.username})")
            
            # Se connecter en tant qu'étudiant
            login_success = client.login(username=student.user.username, password='password123')
            print(f"   Login réussi: {login_success}")
            
            if login_success:
                response = client.get('/academic/attendance/take/')
                print(f"   Status: {response.status_code}")
                if response.status_code == 403:
                    print("   ✅ Accès refusé pour l'étudiant (correct)")
                elif response.status_code == 302:
                    print("   ✅ Redirection (probablement vers une page d'erreur)")
                else:
                    print(f"   ❌ Accès autorisé pour l'étudiant: {response.status_code}")
        else:
            print("   ❌ Aucun étudiant trouvé")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()

if __name__ == '__main__':
    test_attendance_take_rbac()
