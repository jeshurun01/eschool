#!/usr/bin/env python
"""
Script pour créer des données de test pour le calendrier académique
"""

import os
import sys
import django
from datetime import date, time, timedelta

# Configuration Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher
from academic.models import AcademicYear, Level, Subject, ClassRoom, Timetable, Grade, Enrollment

def create_calendar_test_data():
    print("🚀 Création des données de test pour le calendrier...")
    
    # 1. Créer/récupérer l'année académique courante
    current_year, created = AcademicYear.objects.get_or_create(
        name="2024-2025",
        defaults={
            'start_date': date(2024, 9, 1),
            'end_date': date(2025, 7, 31),
            'is_current': True
        }
    )
    if created:
        print(f"✅ Année académique créée: {current_year.name}")
    else:
        current_year.is_current = True
        current_year.save()
        print(f"✅ Année académique mise à jour: {current_year.name}")
    
    # 2. Créer/récupérer un niveau
    level, created = Level.objects.get_or_create(
        name="6ème",
        defaults={'description': 'Sixième année', 'order': 6}
    )
    if created:
        print(f"✅ Niveau créé: {level.name}")
    
    # 3. Créer/récupérer des matières
    subjects_data = [
        {'name': 'Mathématiques', 'code': 'MATH', 'coefficient': 4, 'color': '#FF9800'},
        {'name': 'Français', 'code': 'FR', 'coefficient': 4, 'color': '#2196F3'},
        {'name': 'Histoire-Géographie', 'code': 'HIST', 'coefficient': 3, 'color': '#4CAF50'},
        {'name': 'Sciences', 'code': 'SCI', 'coefficient': 3, 'color': '#9C27B0'},
        {'name': 'Anglais', 'code': 'EN', 'coefficient': 3, 'color': '#F44336'},
    ]
    
    subjects = []
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults=subject_data
        )
        subject.levels.add(level)
        subjects.append(subject)
        if created:
            print(f"✅ Matière créée: {subject.name}")
    
    # 4. Créer/récupérer une classe
    classroom, created = ClassRoom.objects.get_or_create(
        name="6ème A",
        level=level,
        academic_year=current_year,
        defaults={'capacity': 30, 'room_number': 'A101'}
    )
    if created:
        print(f"✅ Classe créée: {classroom.name}")
    
    # 5. Créer/récupérer un enseignant
    teacher_user, created = User.objects.get_or_create(
        email="prof.martin@eschool.com",
        defaults={
            'first_name': 'Jean',
            'last_name': 'Martin',
            'role': 'TEACHER'
        }
    )
    if created:
        teacher_user.set_password('password123')
        teacher_user.save()
        print(f"✅ Utilisateur enseignant créé: {teacher_user.email}")
    
    teacher, created = Teacher.objects.get_or_create(
        user=teacher_user,
        defaults={
            'employee_id': 'PROF001',
            'hire_date': date(2020, 9, 1),
            'education_level': 'Master en Mathématiques'
        }
    )
    if created:
        print(f"✅ Enseignant créé: {teacher.user.get_full_name()}")
    
    # 6. Créer/récupérer un étudiant
    student_user, created = User.objects.get_or_create(
        email="marie.dupont@eschool.com",
        defaults={
            'first_name': 'Marie',
            'last_name': 'Dupont',
            'role': 'STUDENT'
        }
    )
    if created:
        student_user.set_password('password123')
        student_user.save()
        print(f"✅ Utilisateur étudiant créé: {student_user.email}")
    
    student, created = Student.objects.get_or_create(
        user=student_user,
        defaults={
            'matricule': 'STU001',
            'current_class': classroom,
            'enrollment_date': date(2024, 9, 1)
        }
    )
    if created:
        print(f"✅ Étudiant créé: {student.user.get_full_name()}")
    
    # Mettre à jour la classe courante si nécessaire
    if student.current_class != classroom:
        student.current_class = classroom
        student.save()
        print(f"✅ Classe de l'étudiant mise à jour: {classroom.name}")
    
    # 7. Créer l'inscription
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        classroom=classroom,
        academic_year=current_year,
        defaults={
            'enrollment_date': date(2024, 9, 1),
            'is_active': True
        }
    )
    if created:
        print(f"✅ Inscription créée: {student.user.get_full_name()} -> {classroom.name}")
    
    # 8. Créer les emplois du temps (cours réguliers)
    timetable_data = [
        {'subject': subjects[0], 'weekday': 1, 'start_time': time(8, 0), 'end_time': time(9, 0), 'room': 'A101'},  # Lundi Math
        {'subject': subjects[1], 'weekday': 1, 'start_time': time(9, 0), 'end_time': time(10, 0), 'room': 'A102'},  # Lundi Français
        {'subject': subjects[2], 'weekday': 2, 'start_time': time(8, 0), 'end_time': time(9, 0), 'room': 'A103'},  # Mardi Histoire
        {'subject': subjects[3], 'weekday': 3, 'start_time': time(10, 0), 'end_time': time(11, 0), 'room': 'B101'},  # Mercredi Sciences
        {'subject': subjects[4], 'weekday': 4, 'start_time': time(14, 0), 'end_time': time(15, 0), 'room': 'A104'},  # Jeudi Anglais
        {'subject': subjects[0], 'weekday': 5, 'start_time': time(9, 0), 'end_time': time(10, 0), 'room': 'A101'},  # Vendredi Math
    ]
    
    for tt_data in timetable_data:
        timetable, created = Timetable.objects.get_or_create(
            classroom=classroom,
            subject=tt_data['subject'],
            weekday=tt_data['weekday'],
            start_time=tt_data['start_time'],
            defaults={
                'teacher': teacher,
                'end_time': tt_data['end_time'],
                'room': tt_data['room']
            }
        )
        if created:
            print(f"✅ Emploi du temps créé: {tt_data['subject'].name} {['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'][tt_data['weekday']-1]} {tt_data['start_time']}")
    
    # 9. Créer des examens à venir (dans les 30 prochains jours)
    today = date.today()
    exam_dates = [
        today + timedelta(days=3),   # Dans 3 jours
        today + timedelta(days=7),   # Dans 1 semaine
        today + timedelta(days=14),  # Dans 2 semaines
        today + timedelta(days=21),  # Dans 3 semaines
    ]
    
    exam_data = [
        {'subject': subjects[0], 'name': 'Contrôle Algèbre', 'type': 'EXAM'},
        {'subject': subjects[1], 'name': 'Dictée Préparée', 'type': 'TEST'},
        {'subject': subjects[2], 'name': 'Évaluation Géographie', 'type': 'EXAM'},
        {'subject': subjects[3], 'name': 'Contrôle Sciences', 'type': 'TEST'},
    ]
    
    for i, exam_info in enumerate(exam_data):
        if i < len(exam_dates):
            grade, created = Grade.objects.get_or_create(
                student=student,
                subject=exam_info['subject'],
                classroom=classroom,
                evaluation_name=exam_info['name'],
                date=exam_dates[i],
                defaults={
                    'teacher': teacher,
                    'evaluation_type': exam_info['type'],
                    'score': 0,  # Note pas encore attribuée
                    'max_score': 20,
                    'coefficient': 2.0,
                    'comments': 'Examen à venir'
                }
            )
            if created:
                print(f"✅ Examen créé: {exam_info['name']} le {exam_dates[i]}")
    
    # 10. Créer des devoirs à venir
    homework_dates = [
        today + timedelta(days=2),   # Dans 2 jours
        today + timedelta(days=5),   # Dans 5 jours
        today + timedelta(days=12),  # Dans 12 jours
        today + timedelta(days=19),  # Dans 19 jours
    ]
    
    homework_data = [
        {'subject': subjects[1], 'name': 'Rédaction - Mon animal préféré', 'type': 'HOMEWORK'},
        {'subject': subjects[0], 'name': 'Exercices page 45-47', 'type': 'HOMEWORK'},
        {'subject': subjects[4], 'name': 'Dialogue en anglais', 'type': 'PROJECT'},
        {'subject': subjects[2], 'name': 'Carte de France', 'type': 'PROJECT'},
    ]
    
    for i, hw_info in enumerate(homework_data):
        if i < len(homework_dates):
            grade, created = Grade.objects.get_or_create(
                student=student,
                subject=hw_info['subject'],
                classroom=classroom,
                evaluation_name=hw_info['name'],
                date=homework_dates[i],
                defaults={
                    'teacher': teacher,
                    'evaluation_type': hw_info['type'],
                    'score': 0,  # Note pas encore attribuée
                    'max_score': 20,
                    'coefficient': 1.0,
                    'comments': 'Devoir à rendre'
                }
            )
            if created:
                print(f"✅ Devoir créé: {hw_info['name']} le {homework_dates[i]}")
    
    print("\n🎉 Données de test créées avec succès !")
    print(f"📚 Classes: {ClassRoom.objects.count()}")
    print(f"👨‍🎓 Étudiants: {Student.objects.count()}")
    print(f"👨‍🏫 Enseignants: {Teacher.objects.count()}")
    print(f"📅 Emplois du temps: {Timetable.objects.count()}")
    print(f"📝 Notes/Examens: {Grade.objects.count()}")
    print(f"🎯 Matières: {Subject.objects.count()}")

if __name__ == '__main__':
    create_calendar_test_data()