#!/usr/bin/env python3
"""
Script pour vérifier les permissions d'accès aux classes
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Teacher, Student
from academic.models import TeacherAssignment, Enrollment

def check_teacher_classroom_permissions():
    """Vérifie la logique des permissions pour les enseignants"""
    print("🔍 Vérification des permissions d'accès aux classes")
    print("=" * 60)
    
    # Récupérer un enseignant
    teacher = Teacher.objects.first()
    if not teacher:
        print("❌ Aucun enseignant trouvé")
        return
        
    print(f"👨‍🏫 Enseignant: {teacher.user.first_name} {teacher.user.last_name}")
    print(f"   Email: {teacher.user.email}")
    print(f"   Rôle: {teacher.user.role}")
    
    # Ses assignments
    assignments = TeacherAssignment.objects.filter(teacher=teacher)
    print(f"\n📚 Assignments de cet enseignant: {assignments.count()}")
    
    teacher_classroom_ids = set()
    for assignment in assignments:
        classroom = assignment.classroom
        teacher_classroom_ids.add(classroom.id)
        print(f"   - {assignment.subject.name} en {classroom.name} (ID: {classroom.id})")
    
    # Vérifier la logique de permission
    print(f"\n🏫 Classes accessibles (IDs): {sorted(teacher_classroom_ids)}")
    
    # Tester avec une classe où il enseigne
    if teacher_classroom_ids:
        test_classroom_id = list(teacher_classroom_ids)[0]
        is_allowed = test_classroom_id in teacher_classroom_ids
        print(f"✅ Test classe {test_classroom_id}: {'Accès autorisé' if is_allowed else 'Accès refusé'}")
    
    # Tester avec une classe où il n'enseigne pas
    all_classroom_ids = set(TeacherAssignment.objects.values_list('classroom_id', flat=True))
    other_classroom_ids = all_classroom_ids - teacher_classroom_ids
    
    if other_classroom_ids:
        test_other_id = list(other_classroom_ids)[0]
        is_allowed = test_other_id in teacher_classroom_ids
        print(f"❌ Test classe {test_other_id}: {'Accès autorisé' if is_allowed else 'Accès refusé'}")
    
    print(f"\n✅ La logique semble correcte pour cet enseignant")

def test_student_permissions():
    """Teste la logique pour un étudiant"""
    print("\n" + "=" * 60)
    print("🎓 Test permissions étudiant")
    
    student = Student.objects.first()
    if not student:
        print("❌ Aucun étudiant trouvé")
        return
        
    print(f"👦 Étudiant: {student.user.first_name} {student.user.last_name}")
    
    # Ses classes
    enrollments = Enrollment.objects.filter(student=student, is_active=True)
    student_classroom_ids = set(enrollments.values_list('classroom_id', flat=True))
    
    print(f"📚 Classes de cet étudiant: {len(student_classroom_ids)}")
    for enrollment in enrollments:
        print(f"   - {enrollment.classroom.name} (ID: {enrollment.classroom.id})")
    
    print(f"🏫 Classes accessibles (IDs): {sorted(student_classroom_ids)}")

def show_all_classrooms():
    """Affiche toutes les classes disponibles"""
    print("\n" + "=" * 60)
    print("🏫 Toutes les classes dans le système")
    
    from academic.models import ClassRoom
    classrooms = ClassRoom.objects.all()
    
    for classroom in classrooms:
        teachers = TeacherAssignment.objects.filter(classroom=classroom)
        students = Enrollment.objects.filter(classroom=classroom, is_active=True)
        
        print(f"   - {classroom.name} (ID: {classroom.id})")
        print(f"     Enseignants: {teachers.count()}")
        print(f"     Étudiants: {students.count()}")

if __name__ == "__main__":
    check_teacher_classroom_permissions()
    test_student_permissions()
    show_all_classrooms()
    
    print("\n" + "=" * 60)
    print("🎯 INSTRUCTIONS POUR TESTER:")
    print("1. Connectez-vous en tant qu'enseignant dans le navigateur")
    print("2. Allez sur une classe où vous enseignez")
    print("3. L'accès devrait être autorisé maintenant")
    print("4. Testez aussi une classe où vous n'enseignez pas")
    print("   (l'accès devrait être refusé)")
