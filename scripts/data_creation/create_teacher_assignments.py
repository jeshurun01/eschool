#!/usr/bin/env python3
"""
Script pour créer des affectations d'enseignants aux cours (TeacherAssignment)
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academic.models import TeacherAssignment, AcademicYear, Subject, ClassRoom
from accounts.models import Teacher

User = get_user_model()

def create_teacher_assignments():
    """Crée des affectations d'enseignants aux cours"""
    
    print("🎯 Création des affectations enseignants aux cours...")
    
    # Récupérer l'année courante ou la première disponible
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        current_year = AcademicYear.objects.first()
        if not current_year:
            print("❌ Aucune année scolaire trouvée")
            return
    
    print(f"📅 Année scolaire: {current_year.name}")
    
    # Récupérer les enseignants
    teachers = Teacher.objects.all()
    if not teachers.exists():
        print("❌ Aucun enseignant trouvé")
        return
    
    # Récupérer les matières
    subjects = Subject.objects.all()
    if not subjects.exists():
        print("❌ Aucune matière trouvée")
        return
    
    # Récupérer les classes
    classrooms = ClassRoom.objects.all()
    if not classrooms.exists():
        print("❌ Aucune classe trouvée")
        return
    
    assignments_created = 0
    
    # Créer des affectations pour chaque enseignant
    for teacher in teachers:
        print(f"\n👨‍🏫 Enseignant: {teacher.user.get_full_name()}")
        
        # Assigner quelques matières et classes à chaque enseignant
        teacher_subjects = list(subjects)[:3]  # Maximum 3 matières par enseignant
        teacher_classrooms = list(classrooms)[:2]  # Maximum 2 classes par enseignant
        
        for subject in teacher_subjects:
            for classroom in teacher_classrooms:
                # Vérifier si l'affectation existe déjà
                existing = TeacherAssignment.objects.filter(
                    teacher=teacher,
                    classroom=classroom,
                    subject=subject,
                    academic_year=current_year
                ).first()
                
                if not existing:
                    # Créer l'affectation
                    assignment = TeacherAssignment.objects.create(
                        teacher=teacher,
                        classroom=classroom,
                        subject=subject,
                        academic_year=current_year,
                        hours_per_week=3  # 3 heures par semaine par défaut
                    )
                    print(f"  ✅ {subject.name} - {classroom.name} (3h/semaine)")
                    assignments_created += 1
                else:
                    print(f"  ⚠️  {subject.name} - {classroom.name} (déjà existant)")
    
    print(f"\n🎉 Création terminée! {assignments_created} nouvelles affectations créées.")
    
    # Afficher un résumé
    total_assignments = TeacherAssignment.objects.filter(academic_year=current_year).count()
    print(f"📊 Total des affectations pour {current_year.name}: {total_assignments}")
    
    # Détails par enseignant
    print(f"\n📋 Résumé par enseignant:")
    for teacher in teachers:
        teacher_assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=current_year
        ).count()
        print(f"  👨‍🏫 {teacher.user.get_full_name()}: {teacher_assignments} cours")

if __name__ == '__main__':
    create_teacher_assignments()
