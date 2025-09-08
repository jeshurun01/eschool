#!/usr/bin/env python3
"""
Script pour obtenir les informations de connexion d'un enseignant
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Teacher

User = get_user_model()

def get_teacher_credentials():
    """Obtient les identifiants d'un enseignant"""
    
    # Récupérer un enseignant
    teacher = Teacher.objects.first()
    if not teacher:
        print("❌ Aucun enseignant trouvé")
        return
    
    user = teacher.user
    print(f"🎯 Enseignant: {user.get_full_name()}")
    print(f"📧 Email: {user.email}")
    print(f" Mot de passe temporaire: password123")
    print(f"📱 Rôle: {user.role}")
    
    # Informations sur les cours
    from academic.models import TeacherAssignment
    
    assignments = TeacherAssignment.objects.filter(teacher=teacher)
    print(f"\n📚 Nombre de cours assignés: {assignments.count()}")
    
    for assignment in assignments[:5]:  # Afficher les 5 premiers
        print(f"  - {assignment.subject.name} ({assignment.classroom.name}) - {assignment.hours_per_week}h/semaine")

if __name__ == '__main__':
    get_teacher_credentials()
