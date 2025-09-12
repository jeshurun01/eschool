#!/usr/bin/env python3
"""
Script pour vérifier la différenciation des cours par enseignant
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from academic.models import TeacherAssignment, AcademicYear
from accounts.models import Teacher

def test_teacher_courses():
    """Teste si les cours sont bien différenciés par enseignant"""
    
    print("🔍 Test de différenciation des cours par enseignant...")
    
    # Récupérer l'année courante
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        current_year = AcademicYear.objects.first()
    
    print(f"📅 Année scolaire testée: {current_year.name}")
    
    # Tester avec plusieurs enseignants
    teachers = Teacher.objects.all()[:4]  # Prendre les 4 premiers enseignants
    
    for i, teacher in enumerate(teachers, 1):
        print(f"\n👨‍🏫 ENSEIGNANT {i}: {teacher.user.get_full_name()}")
        
        # Récupérer les cours de cet enseignant (comme dans le dashboard)
        teacher_courses = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=current_year
        ).select_related('classroom', 'subject', 'academic_year').order_by('classroom__name', 'subject__name')
        
        print(f"  📚 Nombre de cours: {teacher_courses.count()}")
        
        for course in teacher_courses:
            print(f"    - {course.subject.name} ({course.classroom.name}) - {course.hours_per_week}h/semaine")
    
    # Vérifier s'il y a des différences
    print(f"\n🔍 ANALYSE DE LA DIFFÉRENCIATION:")
    
    # Récupérer les cours de chaque enseignant
    courses_by_teacher = {}
    for teacher in teachers:
        teacher_courses = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=current_year
        )
        courses_by_teacher[teacher.user.get_full_name()] = [
            f"{course.subject.name}-{course.classroom.name}" 
            for course in teacher_courses
        ]
    
    # Comparer les cours
    teacher_names = list(courses_by_teacher.keys())
    differences_found = False
    
    for i in range(len(teacher_names)):
        for j in range(i+1, len(teacher_names)):
            teacher1 = teacher_names[i]
            teacher2 = teacher_names[j]
            
            courses1 = set(courses_by_teacher[teacher1])
            courses2 = set(courses_by_teacher[teacher2])
            
            if courses1 != courses2:
                differences_found = True
                unique_to_1 = courses1 - courses2
                unique_to_2 = courses2 - courses1
                
                print(f"  ✅ Différence entre {teacher1} et {teacher2}:")
                if unique_to_1:
                    print(f"    🔹 Unique à {teacher1}: {', '.join(unique_to_1)}")
                if unique_to_2:
                    print(f"    🔹 Unique à {teacher2}: {', '.join(unique_to_2)}")
    
    if not differences_found:
        print("  ⚠️  PROBLÈME: Tous les enseignants ont exactement les mêmes cours!")
        print("  🔧 Le script create_teacher_assignments.py assigne peut-être les mêmes cours à tous.")
    else:
        print("  ✅ CORRECT: Les enseignants ont des cours différents.")
    
    # Statistiques globales
    total_assignments = TeacherAssignment.objects.filter(academic_year=current_year).count()
    unique_combinations = TeacherAssignment.objects.filter(
        academic_year=current_year
    ).values('teacher', 'classroom', 'subject').distinct().count()
    
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"  📚 Total des affectations: {total_assignments}")
    print(f"  🔀 Combinaisons uniques enseignant-classe-matière: {unique_combinations}")
    
    if total_assignments == unique_combinations:
        print("  ✅ Chaque affectation est unique (pas de doublons)")
    else:
        print("  ⚠️  Il y a des doublons dans les affectations")

if __name__ == '__main__':
    test_teacher_courses()
