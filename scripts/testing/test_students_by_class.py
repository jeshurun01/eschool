#!/usr/bin/env python
"""
Test simple pour vérifier les élèves par classe
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from academic.models import ClassRoom, Enrollment
from accounts.models import Teacher, Student

def test_students_by_classroom():
    """Test pour vérifier la répartition des élèves par classe"""
    
    print("=== Répartition des élèves par classe ===\n")
    
    # Toutes les classes actives
    classrooms = ClassRoom.objects.filter(academic_year__is_current=True)[:5]
    
    for classroom in classrooms:
        print(f"Classe: {classroom.name}")
        
        # Élèves inscrits dans cette classe
        enrollments = Enrollment.objects.filter(
            classroom=classroom,
            is_active=True
        ).select_related('student__user')
        
        print(f"  Élèves inscrits: {enrollments.count()}")
        
        for enrollment in enrollments[:3]:  # Afficher 3 premiers
            student = enrollment.student
            print(f"    - {student.user.get_full_name()}")
        
        if enrollments.count() > 3:
            print(f"    ... et {enrollments.count() - 3} autres")
        
        print()
    
    # Test avec Marie Dupont
    print("=== Classes de Marie Dupont ===")
    marie = Teacher.objects.get(employee_id='T1000')
    marie_classrooms = ClassRoom.objects.filter(
        teacherassignment__teacher=marie,
        teacherassignment__academic_year__is_current=True
    ).distinct()
    
    for classroom in marie_classrooms:
        students_count = Enrollment.objects.filter(
            classroom=classroom,
            is_active=True
        ).count()
        print(f"  {classroom.name}: {students_count} élèves")

if __name__ == '__main__':
    test_students_by_classroom()
