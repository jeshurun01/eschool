#!/usr/bin/env python3
"""
Script pour tester le dashboard avec différents enseignants
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Teacher

def test_dashboard_differences():
    """Affiche les informations pour tester avec différents enseignants"""
    
    print("🔐 Informations de connexion pour tester le dashboard enseignant:")
    print("   (Mot de passe pour tous: password123)")
    print()
    
    teachers = Teacher.objects.all()[:4]
    
    for i, teacher in enumerate(teachers, 1):
        print(f"👨‍🏫 ENSEIGNANT {i}: {teacher.user.get_full_name()}")
        print(f"   📧 Email: {teacher.user.email}")
        
        # Informations sur ses cours
        from academic.models import TeacherAssignment, AcademicYear
        current_year = AcademicYear.objects.filter(is_current=True).first() or AcademicYear.objects.first()
        
        courses = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=current_year
        )
        
        subjects = list(set([c.subject.name for c in courses]))
        classes = list(set([c.classroom.name for c in courses]))
        
        print(f"   📚 Ses matières: {', '.join(subjects)}")
        print(f"   🏫 Ses classes: {', '.join(classes)}")
        print(f"   📊 Total cours: {courses.count()}")
        print()
    
    print("🌐 Pour tester:")
    print("   1. Allez sur: http://127.0.0.1:8000/accounts/login/")
    print("   2. Connectez-vous avec un email ci-dessus et le mot de passe 'password123'")
    print("   3. Observez la section 'Mes Cours' qui devrait être différente pour chaque enseignant")

if __name__ == '__main__':
    test_dashboard_differences()
