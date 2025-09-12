#!/usr/bin/env python
"""
Test du filtrage des classes dans attendance_list
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Teacher
from academic.models import TeacherAssignment, ClassRoom

User = get_user_model()

def test_attendance_list_filtering():
    """Test du filtrage des classes dans attendance_list"""
    
    print("=== Test du filtrage des classes dans attendance_list ===\n")
    
    # Test avec différents enseignants
    teachers = Teacher.objects.select_related('user').all()[:3]
    
    for teacher in teachers:
        print(f"Enseignant: {teacher.user.get_full_name()}")
        
        # Toutes les classes du système
        all_classrooms = ClassRoom.objects.filter(academic_year__is_current=True)
        print(f"  Total des classes dans le système: {all_classrooms.count()}")
        
        # Classes de l'enseignant selon la logique corrigée
        teacher_assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year__is_current=True
        ).select_related('classroom', 'subject')
        
        classroom_ids = teacher_assignments.values_list('classroom_id', flat=True).distinct()
        filtered_classrooms = all_classrooms.filter(id__in=classroom_ids)
        
        print(f"  Classes accessibles après filtrage: {filtered_classrooms.count()}")
        for classroom in filtered_classrooms:
            print(f"    - {classroom.name}")
        
        # Matières de l'enseignant
        subject_ids = teacher_assignments.values_list('subject_id', flat=True).distinct()
        from academic.models import Subject
        filtered_subjects = Subject.objects.filter(id__in=subject_ids)
        print(f"  Matières accessibles: {filtered_subjects.count()}")
        for subject in filtered_subjects:
            print(f"    - {subject.name}")
        
        print(f"  Filtrage effectif: {'✅ OUI' if all_classrooms.count() > filtered_classrooms.count() else '⚠️  NON (accès à toutes les classes)'}")
        print()

if __name__ == '__main__':
    test_attendance_list_filtering()
