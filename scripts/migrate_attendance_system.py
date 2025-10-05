#!/usr/bin/env python
"""
Script pour migrer les données de l'ancien système Attendance vers SessionAttendance + DailyAttendanceSummary
"""

import os
import sys
import django
from datetime import date, timedelta, datetime, time

# Configuration Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher
from academic.models import (
    AcademicYear, Period, Timetable, Session, 
    Attendance, SessionAttendance, DailyAttendanceSummary
)

def migrate_attendance_data():
    """Migre les données de l'ancien système vers le nouveau"""
    print("🔄 Migration des données de présence...")
    
    # 1. Récupérer la période courante
    try:
        current_period = Period.objects.get(is_current=True)
        print(f"✅ Période courante trouvée: {current_period.name}")
    except Period.DoesNotExist:
        # Créer une période par défaut
        current_year = AcademicYear.objects.get(is_current=True)
        current_period = Period.objects.create(
            name="Période 1",
            academic_year=current_year,
            start_date=current_year.start_date,
            end_date=current_year.end_date,
            is_current=True
        )
        print(f"✅ Période créée: {current_period.name}")
    
    # 2. Créer des sessions pour tous les créneaux d'emploi du temps
    print("📅 Création des sessions...")
    sessions_created = 0
    
    # Pour chaque créneau d'emploi du temps
    for timetable in Timetable.objects.all():
        print(f"   Traitement: {timetable}")
        
        # Générer les sessions pour les 30 derniers jours
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        current_date = start_date
        while current_date <= end_date:
            # Vérifier si c'est le bon jour de la semaine
            if current_date.isoweekday() == timetable.weekday:
                session, created = Session.objects.get_or_create(
                    timetable=timetable,
                    date=current_date,
                    defaults={
                        'period': current_period,
                        'status': 'COMPLETED' if current_date < date.today() else 'SCHEDULED',
                        'lesson_title': f"Cours de {timetable.subject.name}",
                        'attendance_taken': True
                    }
                )
                if created:
                    sessions_created += 1
            
            current_date += timedelta(days=1)
    
    print(f"✅ {sessions_created} sessions créées")
    
    # 3. Migrer les données d'attendance existantes vers SessionAttendance
    print("👥 Migration des présences...")
    
    old_attendances = Attendance.objects.all()
    migrated_count = 0
    
    for old_attendance in old_attendances:
        # Trouver la session correspondante
        matching_sessions = Session.objects.filter(
            date=old_attendance.date,
            timetable__classroom=old_attendance.classroom,
            timetable__subject=old_attendance.subject,
            timetable__teacher=old_attendance.teacher
        )
        
        if matching_sessions.exists():
            session = matching_sessions.first()
            
            # Créer la nouvelle présence de session
            session_attendance, created = SessionAttendance.objects.get_or_create(
                session=session,
                student=old_attendance.student,
                defaults={
                    'status': old_attendance.status,
                    'justification': old_attendance.justification,
                    'recorded_by': old_attendance.teacher.user,
                    'arrival_time': session.planned_start_time if old_attendance.status != 'ABSENT' else None
                }
            )
            
            if created:
                migrated_count += 1
        else:
            print(f"   ⚠️  Pas de session trouvée pour: {old_attendance}")
    
    print(f"✅ {migrated_count} présences migrées")
    
    # 4. Calculer les résumés quotidiens
    print("📊 Calcul des résumés quotidiens...")
    
    # Pour chaque étudiant et chaque jour avec des sessions
    students = Student.objects.all()
    summaries_created = 0
    
    for student in students:
        # Récupérer toutes les dates où l'étudiant a des sessions
        session_dates = SessionAttendance.objects.filter(
            student=student
        ).values_list('session__date', flat=True).distinct()
        
        for session_date in session_dates:
            summary = DailyAttendanceSummary.calculate_for_student_date(student, session_date)
            if summary:
                summaries_created += 1
    
    print(f"✅ {summaries_created} résumés quotidiens créés")
    
    # 5. Statistiques finales
    print("\n📈 Statistiques de migration:")
    print(f"   Sessions créées: {Session.objects.count()}")
    print(f"   Présences de session: {SessionAttendance.objects.count()}")
    print(f"   Résumés quotidiens: {DailyAttendanceSummary.objects.count()}")
    print(f"   Anciennes présences (à supprimer): {Attendance.objects.count()}")
    
    print("\n✨ Migration terminée avec succès !")

def create_test_sessions():
    """Crée quelques sessions de test pour démonstration"""
    print("🧪 Création de sessions de test...")
    
    # Récupérer les données de test existantes
    try:
        marie = Student.objects.get(user__email='marie.dupont@eschool.com')
        teacher = Teacher.objects.get(user__email='prof.martin@eschool.com')
        
        # Récupérer ou créer une période courante
        try:
            current_period = Period.objects.get(is_current=True)
        except Period.DoesNotExist:
            # Créer une période par défaut
            current_year = AcademicYear.objects.get(is_current=True)
            current_period = Period.objects.create(
                name="Trimestre 1",
                academic_year=current_year,
                start_date=current_year.start_date,
                end_date=date.today() + timedelta(days=90),
                is_current=True
            )
            print(f"✅ Période créée: {current_period.name}")
        
        # Récupérer un créneau d'emploi du temps
        timetable = Timetable.objects.filter(classroom=marie.current_class).first()
        
        if not timetable:
            print("❌ Aucun emploi du temps trouvé")
            return
        
        # Créer une session pour aujourd'hui
        today_session, created = Session.objects.get_or_create(
            timetable=timetable,
            date=date.today(),
            defaults={
                'period': current_period,
                'status': 'COMPLETED',
                'lesson_title': 'Les fractions - Leçon 3',
                'lesson_objectives': 'Apprendre à additionner et soustraire les fractions',
                'lesson_content': 'Explication des règles d\'addition de fractions avec dénominateurs différents',
                'lesson_summary': 'Les élèves ont bien compris la méthode pour mettre au même dénominateur',
                'teacher_notes': 'Marie a bien participé. Quelques difficultés pour Paul.',
                'homework_given': 'Exercices page 45-47 pour demain',
                'attendance_taken': True,
                'attendance_taken_at': datetime.now()
            }
        )
        
        if created:
            print(f"✅ Session créée: {today_session}")
            
            # Créer les présences pour tous les élèves de la classe
            students_in_class = Student.objects.filter(current_class=marie.current_class)
            for student in students_in_class:
                SessionAttendance.objects.get_or_create(
                    session=today_session,
                    student=student,
                    defaults={
                        'status': 'PRESENT',
                        'arrival_time': timetable.start_time,
                        'recorded_by': teacher.user
                    }
                )
            
            print(f"✅ Présences créées pour {students_in_class.count()} élèves")
            
            # Calculer les résumés quotidiens
            for student in students_in_class:
                DailyAttendanceSummary.calculate_for_student_date(student, date.today())
            
            print("✅ Résumés quotidiens calculés")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        create_test_sessions()
    else:
        migrate_attendance_data()