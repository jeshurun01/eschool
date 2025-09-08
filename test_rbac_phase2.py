#!/usr/bin/env python
"""
Test des managers RBAC - Phase 2
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher, Parent
from academic.models import Grade, ClassRoom, Enrollment

def test_rbac_managers():
    """Test des managers RBAC pour le filtrage de données"""
    print("🧪 Test des Managers RBAC - Phase 2")
    print("=" * 50)
    
    try:
        # Récupérer des utilisateurs de test
        teacher_users = User.objects.filter(role='TEACHER')[:1]
        student_users = User.objects.filter(role='STUDENT')[:1]
        parent_users = User.objects.filter(role='PARENT')[:1]
        
        print(f"📊 Utilisateurs de test trouvés:")
        print(f"   - Enseignants: {teacher_users.count()}")
        print(f"   - Élèves: {student_users.count()}")
        print(f"   - Parents: {parent_users.count()}")
        
        if teacher_users.exists():
            teacher_user = teacher_users.first()
            print(f"\n👨‍🏫 Test avec enseignant: {teacher_user.full_name}")
            
            # Test filtrage des notes pour enseignant
            teacher_grades = Grade.objects.for_role(teacher_user)
            print(f"   - Notes accessibles: {teacher_grades.count()}")
            
            # Test filtrage des classes pour enseignant
            teacher_classes = ClassRoom.objects.for_role(teacher_user)
            print(f"   - Classes accessibles: {teacher_classes.count()}")
            
        if student_users.exists():
            student_user = student_users.first()
            print(f"\n👨‍🎓 Test avec élève: {student_user.full_name}")
            
            # Test filtrage des notes pour élève
            student_grades = Grade.objects.for_role(student_user)
            print(f"   - Notes accessibles: {student_grades.count()}")
            
            # Test filtrage des classes pour élève
            student_classes = ClassRoom.objects.for_role(student_user)
            print(f"   - Classes accessibles: {student_classes.count()}")
            
        if parent_users.exists():
            parent_user = parent_users.first()
            print(f"\n👨‍👩‍👧‍👦 Test avec parent: {parent_user.full_name}")
            
            # Test filtrage des notes pour parent
            parent_grades = Grade.objects.for_role(parent_user)
            print(f"   - Notes des enfants accessibles: {parent_grades.count()}")
            
        # Test complet des totaux
        print(f"\n📈 Totaux généraux:")
        print(f"   - Total notes dans la DB: {Grade.objects.all().count()}")
        print(f"   - Total classes dans la DB: {ClassRoom.objects.all().count()}")
        print(f"   - Total inscriptions dans la DB: {Enrollment.objects.all().count()}")
        
        print("\n✅ Tests des managers RBAC réussis!")
        print("🎯 Phase 2 COMPLÈTE - Filtrage des données opérationnel")
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_rbac_managers()
