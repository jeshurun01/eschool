#!/usr/bin/env python3
"""
Script pour créer des affectations d'enseignants plus réalistes et diversifiées
"""

import os
import sys
import django
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academic.models import TeacherAssignment, AcademicYear, Subject, ClassRoom
from accounts.models import Teacher

User = get_user_model()

def create_realistic_teacher_assignments():
    """Crée des affectations d'enseignants plus réalistes et diversifiées"""
    
    print("🎯 Création d'affectations enseignants RÉALISTES et DIVERSIFIÉES...")
    
    # Supprimer les anciennes affectations pour recommencer
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        current_year = AcademicYear.objects.first()
        if not current_year:
            print("❌ Aucune année scolaire trouvée")
            return
    
    print(f"📅 Année scolaire: {current_year.name}")
    
    # Supprimer les anciennes affectations
    old_assignments = TeacherAssignment.objects.filter(academic_year=current_year)
    deleted_count = old_assignments.count()
    old_assignments.delete()
    print(f"🗑️  Suppression de {deleted_count} anciennes affectations")
    
    # Récupérer les données
    teachers = list(Teacher.objects.all())
    subjects = list(Subject.objects.all())
    classrooms = list(ClassRoom.objects.all())
    
    if not teachers or not subjects or not classrooms:
        print("❌ Données manquantes (enseignants, matières ou classes)")
        return
    
    print(f"👥 {len(teachers)} enseignants, 📚 {len(subjects)} matières, 🏫 {len(classrooms)} classes")
    
    # Stratégies de spécialisation par enseignant
    specializations = {
        'LANGUAGE': ['Français', 'Anglais'],
        'SCIENCE': ['Mathématiques', 'Sciences', 'Informatique'],
        'ARTS': ['Arts Plastiques', 'Musique'],
        'SPORT': ['Sport', 'EPS'],
        'GENERAL': subjects  # Généraliste
    }
    
    assignments_created = 0
    
    # Assigner des spécialisations aux enseignants
    spec_keys = list(specializations.keys())
    
    for i, teacher in enumerate(teachers):
        # Choisir une spécialisation (avec variété)
        if i < len(spec_keys):
            spec = spec_keys[i]
        else:
            spec = random.choice(spec_keys)
        
        # Récupérer les matières de la spécialisation
        spec_subject_names = specializations[spec]
        if spec == 'GENERAL':
            teacher_subjects = random.sample(subjects, min(3, len(subjects)))
        else:
            # Filtrer les matières disponibles pour cette spécialisation
            teacher_subjects = [s for s in subjects if s.name in spec_subject_names]
            # Si pas assez de matières dans la spécialisation, ajouter d'autres
            if len(teacher_subjects) < 2:
                other_subjects = [s for s in subjects if s not in teacher_subjects]
                teacher_subjects.extend(random.sample(other_subjects, min(2, len(other_subjects))))
        
        # Assigner 1-2 classes par enseignant (variation)
        num_classes = random.randint(1, min(2, len(classrooms)))
        teacher_classrooms = random.sample(classrooms, num_classes)
        
        print(f"\n👨‍🏫 {teacher.user.get_full_name()} - Spécialisation: {spec}")
        print(f"  📚 Matières: {[s.name for s in teacher_subjects]}")
        print(f"  🏫 Classes: {[c.name for c in teacher_classrooms]}")
        
        # Créer les affectations
        for subject in teacher_subjects:
            for classroom in teacher_classrooms:
                # Variation des heures par semaine selon la matière
                hours_map = {
                    'Français': random.randint(4, 6),
                    'Mathématiques': random.randint(4, 5),
                    'Anglais': random.randint(2, 3),
                    'Sciences': random.randint(2, 3),
                    'Arts Plastiques': random.randint(1, 2),
                    'Musique': random.randint(1, 2),
                    'Sport': random.randint(2, 3),
                    'EPS': random.randint(2, 3),
                    'Informatique': random.randint(1, 2),
                }
                hours = hours_map.get(subject.name, 2)
                
                try:
                    assignment = TeacherAssignment.objects.create(
                        teacher=teacher,
                        classroom=classroom,
                        subject=subject,
                        academic_year=current_year,
                        hours_per_week=hours
                    )
                    print(f"    ✅ {subject.name} - {classroom.name} ({hours}h/semaine)")
                    assignments_created += 1
                except Exception as e:
                    print(f"    ❌ Erreur pour {subject.name} - {classroom.name}: {e}")
    
    print(f"\n🎉 Création terminée! {assignments_created} nouvelles affectations créées.")
    
    # Vérification de la diversité
    print(f"\n📊 VÉRIFICATION DE LA DIVERSITÉ:")
    for teacher in teachers:
        teacher_assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=current_year
        )
        subjects_taught = [a.subject.name for a in teacher_assignments]
        classes_taught = [a.classroom.name for a in teacher_assignments]
        
        print(f"  👨‍🏫 {teacher.user.get_full_name()}: {len(teacher_assignments)} cours")
        print(f"     Matières: {', '.join(set(subjects_taught))}")
        print(f"     Classes: {', '.join(set(classes_taught))}")

if __name__ == '__main__':
    create_realistic_teacher_assignments()
