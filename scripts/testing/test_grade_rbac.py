#!/usr/bin/env python3
"""
Test du filtrage RBAC pour le système de notes
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Teacher, Student, Parent
from academic.models import Grade

def test_grade_rbac_filtering():
    """Test du filtrage RBAC pour les notes"""
    print("🔍 Test du filtrage RBAC pour les notes")
    print("=" * 60)
    
    # Test Enseignant
    teacher = Teacher.objects.first()
    if teacher:
        print(f"👨‍🏫 Enseignant: {teacher.user.first_name} {teacher.user.last_name}")
        
        # Test du manager RBAC
        try:
            teacher_grades = Grade.objects.for_role(teacher.user)
            print(f"   Notes accessibles: {teacher_grades.count()}")
            
            # Vérifier que toutes les notes sont bien de cet enseignant
            all_teacher_grades = teacher_grades.all()
            teacher_owns_all = all(grade.teacher == teacher for grade in all_teacher_grades)
            
            if teacher_owns_all:
                print("   ✅ Toutes les notes appartiennent bien à cet enseignant")
            else:
                print("   ❌ Certaines notes ne lui appartiennent pas!")
                
        except Exception as e:
            print(f"   ❌ Erreur manager RBAC: {e}")
    
    # Test Étudiant
    student = Student.objects.first()
    if student:
        print(f"\n🎓 Étudiant: {student.user.first_name} {student.user.last_name}")
        
        try:
            student_grades = Grade.objects.for_role(student.user)
            print(f"   Notes accessibles: {student_grades.count()}")
            
            # Vérifier que toutes les notes sont bien de cet étudiant
            all_student_grades = student_grades.all()
            student_owns_all = all(grade.student == student for grade in all_student_grades)
            
            if student_owns_all:
                print("   ✅ Toutes les notes appartiennent bien à cet étudiant")
            else:
                print("   ❌ Certaines notes ne lui appartiennent pas!")
                
        except Exception as e:
            print(f"   ❌ Erreur manager RBAC: {e}")
    
    # Test Parent
    parent = Parent.objects.first()
    if parent:
        print(f"\n👨‍👩‍👧‍👦 Parent: {parent.user.first_name} {parent.user.last_name}")
        
        try:
            parent_grades = Grade.objects.for_role(parent.user)
            print(f"   Notes accessibles: {parent_grades.count()}")
            
            # Vérifier que toutes les notes sont bien de ses enfants
            children = parent.students.all()
            children_ids = set(child.id for child in children)
            
            all_parent_grades = parent_grades.all()
            parent_owns_all = all(grade.student.id in children_ids for grade in all_parent_grades)
            
            if parent_owns_all:
                print("   ✅ Toutes les notes appartiennent bien aux enfants de ce parent")
            else:
                print("   ❌ Certaines notes ne correspondent pas aux enfants!")
                
        except Exception as e:
            print(f"   ❌ Erreur manager RBAC: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("Le système de notes utilise le manager RBAC Grade.objects.for_role()")
    print("qui filtre automatiquement selon le rôle de l'utilisateur.")
    print("✅ Le filtrage devrait fonctionner correctement.")

def test_grade_counts_by_role():
    """Affiche le nombre de notes par rôle"""
    print("\n📊 Statistiques des notes par rôle")
    print("=" * 60)
    
    total_grades = Grade.objects.count()
    print(f"📝 Total des notes dans le système: {total_grades}")
    
    # Par enseignant
    teachers = Teacher.objects.all()[:3]  # Premier 3 enseignants
    for teacher in teachers:
        teacher_grades = Grade.objects.filter(teacher=teacher).count()
        print(f"👨‍🏫 {teacher.user.first_name} {teacher.user.last_name}: {teacher_grades} notes")
    
    # Par étudiant
    students = Student.objects.all()[:3]  # Premier 3 étudiants
    for student in students:
        student_grades = Grade.objects.filter(student=student).count()
        print(f"🎓 {student.user.first_name} {student.user.last_name}: {student_grades} notes")

if __name__ == "__main__":
    test_grade_rbac_filtering()
    test_grade_counts_by_role()
    
    print("\n" + "=" * 60)
    print("🌐 Pour tester manuellement:")
    print("1. Connectez-vous en tant qu'enseignant")
    print("2. Allez sur http://127.0.0.1:8000/academic/grades/")
    print("3. Vérifiez que vous ne voyez que VOS notes")
    print("4. Testez avec un compte étudiant/parent")
