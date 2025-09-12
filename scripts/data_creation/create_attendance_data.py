#!/usr/bin/env python3
"""
Script pour créer des données de présence avec les enseignants corrects
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from academic.models import Attendance, TeacherAssignment
from accounts.models import Teacher, Student

def create_attendance_data():
    """Crée des données de présence liées aux enseignants"""
    
    print("🎯 Création de données de présence avec enseignants...")
    
    # Récupérer les affectations d'enseignants
    assignments = TeacherAssignment.objects.select_related(
        'teacher', 'classroom', 'subject'
    ).all()
    
    if not assignments.exists():
        print("❌ Aucune affectation d'enseignant trouvée")
        return
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    attendance_created = 0
    
    # Pour chaque affectation, créer des présences
    for assignment in assignments[:10]:  # Limiter pour les tests
        teacher = assignment.teacher
        classroom = assignment.classroom
        subject = assignment.subject
        
        print(f"\n👨‍🏫 {teacher.user.get_full_name()} - {subject.name} - {classroom.name}")
        
        # Récupérer les étudiants de cette classe
        students = Student.objects.filter(
            enrollments__classroom=classroom,
            enrollments__is_active=True
        ).distinct()[:5]  # Limiter à 5 étudiants pour les tests
        
        # Créer des présences pour les 7 derniers jours
        for i in range(7):
            date = today - timedelta(days=i)
            
            for student in students:
                # Vérifier si la présence existe déjà
                existing = Attendance.objects.filter(
                    student=student,
                    date=date,
                    subject=subject,
                    teacher=teacher
                ).first()
                
                if not existing:
                    # Status aléatoire pondéré (plus de présents)
                    import random
                    status_weights = {
                        'PRESENT': 0.8,
                        'ABSENT': 0.1,
                        'LATE': 0.08,
                        'EXCUSED': 0.02
                    }
                    status = random.choices(
                        list(status_weights.keys()),
                        weights=list(status_weights.values())
                    )[0]
                    
                    try:
                        attendance = Attendance.objects.create(
                            student=student,
                            classroom=classroom,
                            subject=subject,
                            teacher=teacher,
                            date=date,
                            status=status
                        )
                        attendance_created += 1
                        
                        if attendance_created <= 10:  # Afficher seulement les 10 premiers
                            print(f"  ✅ {student.user.get_full_name()} - {date} - {status}")
                    except Exception as e:
                        # Ignorer les doublons
                        pass
    
    print(f"\n🎉 Création terminée! {attendance_created} présences créées.")
    
    # Statistiques par enseignant
    print(f"\n📊 Résumé par enseignant:")
    for teacher in Teacher.objects.all()[:5]:
        teacher_attendances = Attendance.objects.filter(
            teacher=teacher,
            date__gte=week_ago
        ).count()
        if teacher_attendances > 0:
            print(f"  👨‍🏫 {teacher.user.get_full_name()}: {teacher_attendances} présences")

if __name__ == '__main__':
    create_attendance_data()
