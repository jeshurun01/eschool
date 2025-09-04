#!/usr/bin/env python
"""
Script pour créer des notes de test
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Student, Teacher
from academic.models import Grade, Subject, ClassRoom
from django.db.models import Avg

print("🎯 Création des notes de test...")

# Récupérer quelques étudiants et enseignants
students = Student.objects.all()[:5]
teachers = Teacher.objects.all()
subjects = Subject.objects.all()

if not students.exists() or not teachers.exists() or not subjects.exists():
    print("❌ Pas assez de données de base. Exécutez d'abord populate_data.py")
    sys.exit(1)

# Types d'évaluations
evaluation_types = ['HOMEWORK', 'TEST', 'EXAM', 'PROJECT', 'PARTICIPATION']

# Créer des notes pour chaque étudiant
notes_created = 0
for student in students:
    if not student.current_class:
        continue
        
    # Créer 8-12 notes par étudiant
    num_grades = random.randint(8, 12)
    
    for i in range(num_grades):
        # Sélectionner une matière et un enseignant aléatoirement
        subject = random.choice(subjects)
        teacher = random.choice(teachers)
        
        # Générer une note réaliste (entre 6 et 19)
        score = random.randint(6, 19)
        
        # Sélectionner un type d'évaluation
        eval_type = random.choice(evaluation_types)
        
        # Date aléatoire dans les 2 derniers mois
        days_ago = random.randint(1, 60)
        grade_date = timezone.now() - timedelta(days=days_ago)
        
        try:
            grade, created = Grade.objects.get_or_create(
                student=student,
                subject=subject,
                teacher=teacher,
                evaluation_type=eval_type,
                classroom=student.current_class,
                date=grade_date.date(),
                defaults={
                    'evaluation_name': f"{eval_type} {subject.name}",
                    'score': score,
                    'max_score': 20,
                    'comments': f"Évaluation de {eval_type.lower()} en {subject.name}",
                }
            )
            
            if created:
                notes_created += 1
                print(f"✅ Note créée: {student.user.full_name} - {subject.name} - {score}/20")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création de la note: {e}")
            continue

print(f"\n🎉 {notes_created} notes créées avec succès!")
print("\n📊 Résumé:")
for student in students:
    if student.current_class:
        student_grades = Grade.objects.filter(student=student)
        if student_grades.exists():
            avg = student_grades.aggregate(avg=Avg('score'))['avg']
            print(f"- {student.user.full_name}: {student_grades.count()} notes, moyenne: {avg:.1f}/20")
