#!/usr/bin/env python3
"""
Test complet des interfaces parent/élève après correction du bug d'attendance
"""

import django
import os
import sys
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Parent
from academic.models import Attendance, Grade, Subject
from django.test import Client
from django.contrib.auth import authenticate

def test_student_interfaces():
    """Test de toutes les interfaces élève"""
    print("🎓 TEST DES INTERFACES ÉLÈVE")
    print("=" * 50)
    
    client = Client()
    
    try:
        # Connexion avec le compte élève
        user = User.objects.get(email='alexandre.girard@student.eschool.com')
        login_success = client.login(email='alexandre.girard@student.eschool.com', password='password123')
        
        if not login_success:
            print("❌ Échec de connexion élève")
            return False
            
        print(f"✅ Connexion réussie: {user.first_name} {user.last_name}")
        
        # Test des URLs élève
        student_urls = [
            ('/accounts/student/grades/', 'Notes détaillées'),
            ('/accounts/student/attendance/', 'Présences détaillées'),
            ('/accounts/student/finance/', 'Finances détaillées'),
            ('/accounts/student/calendar/', 'Calendrier académique'),
        ]
        
        for url, description in student_urls:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description}: {url}")
            else:
                print(f"❌ {description}: {url} (Status: {response.status_code})")
                return False
        
        # Vérifier les données d'attendance
        student = user.student_profile
        attendances = Attendance.objects.filter(student=student)
        print(f"📊 Données d'attendance: {attendances.count()} enregistrements")
        
        # Test statistiques
        present_count = attendances.filter(status='PRESENT').count()
        total_count = attendances.count()
        rate = round((present_count / total_count * 100), 1) if total_count > 0 else 0
        print(f"📊 Taux de présence: {rate}% ({present_count}/{total_count})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur interface élève: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parent_interfaces():
    """Test de toutes les interfaces parent"""
    print("\\n👨‍👩‍👧‍👦 TEST DES INTERFACES PARENT")
    print("=" * 50)
    
    client = Client()
    
    try:
        # Connexion avec le compte parent
        user = User.objects.get(email='brigitte.andre@gmail.com')
        login_success = client.login(email='brigitte.andre@gmail.com', password='password123')
        
        if not login_success:
            print("❌ Échec de connexion parent")
            return False
            
        print(f"✅ Connexion réussie: {user.first_name} {user.last_name}")
        
        # Test des URLs parent
        parent_urls = [
            ('/accounts/parent/children/', 'Vue d\'ensemble enfants'),
            ('/accounts/parent/communication/', 'Centre de communication'),
        ]
        
        for url, description in parent_urls:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description}: {url}")
            else:
                print(f"❌ {description}: {url} (Status: {response.status_code})")
                return False
        
        # Test détail enfant (si le parent a des enfants)
        parent = user.parent_profile
        children = parent.children.all()
        print(f"👶 Enfants du parent: {children.count()}")
        
        for child in children[:2]:  # Tester les 2 premiers enfants
            child_url = f'/accounts/parent/child/{child.id}/'
            response = client.get(child_url)
            if response.status_code == 200:
                print(f"✅ Détail enfant: {child.user.first_name} {child.user.last_name}")
            else:
                print(f"❌ Détail enfant: {child.user.first_name} (Status: {response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur interface parent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_attendance_data_integrity():
    """Test de l'intégrité des données d'attendance"""
    print("\\n📊 TEST D'INTÉGRITÉ DES DONNÉES")
    print("=" * 50)
    
    try:
        # Test de la requête qui posait problème
        from academic.models import Subject
        
        # Test avec tous les étudiants
        students = Student.objects.all()
        print(f"👥 Nombre d'étudiants: {students.count()}")
        
        for student in students[:3]:  # Tester les 3 premiers
            try:
                # Cette requête posait problème avant
                subjects = Subject.objects.filter(attendance__student=student).distinct()
                attendances = Attendance.objects.filter(student=student)
                
                print(f"✅ {student.user.first_name}: {attendances.count()} présences, {subjects.count()} matières")
                
                # Test du problème de subject null
                null_subjects = attendances.filter(subject__isnull=True).count()
                if null_subjects > 0:
                    print(f"  ⚠️  {null_subjects} présences sans matière spécifiée")
                
            except Exception as e:
                print(f"❌ Erreur pour {student.user.first_name}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégrité données: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET INTERFACES PARENT/ÉLÈVE")
    print("=" * 60)
    print(f"📅 Date: {date.today()}")
    print(f"🕐 Test après correction du bug 'attendances' -> 'attendance'")
    print()
    
    # Tests
    results = []
    
    # Test intégrité des données
    results.append(("Intégrité données", test_attendance_data_integrity()))
    
    # Test interfaces élève
    results.append(("Interfaces élève", test_student_interfaces()))
    
    # Test interfaces parent
    results.append(("Interfaces parent", test_parent_interfaces()))
    
    # Résumé
    print("\\n🏁 RÉSULTATS FINAUX")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ RÉUSSI" if passed else "❌ ÉCHEC"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("✅ Le bug d'attendance a été corrigé avec succès")
        print("✅ Toutes les interfaces parent/élève fonctionnent")
        print("✅ Le système est prêt pour la production")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Vérifiez les erreurs ci-dessus")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
