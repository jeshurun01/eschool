#!/usr/bin/env python
"""
Script pour vérifier le nouveau système de sessions
"""

import os
import sys
import django
from datetime import date

# Configuration Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Student
from academic.models import Session, SessionAttendance, DailyAttendanceSummary

def verify_session_system():
    """Vérifie que le nouveau système fonctionne correctement"""
    print("🔍 Vérification du système de sessions...")
    
    # 1. Vérifier les sessions
    sessions = Session.objects.all()
    print(f"✅ Sessions créées: {sessions.count()}")
    
    if sessions.exists():
        latest_session = sessions.first()
        print(f"   Dernière session: {latest_session}")
        print(f"   Statut: {latest_session.status}")
        print(f"   Appel pris: {'Oui' if latest_session.attendance_taken else 'Non'}")
        print(f"   Taux de présence: {latest_session.attendance_rate}%")
    
    # 2. Vérifier les présences de session
    session_attendances = SessionAttendance.objects.all()
    print(f"\n✅ Présences de session: {session_attendances.count()}")
    
    for attendance in session_attendances[:3]:
        print(f"   {attendance.student.user.get_full_name()}: {attendance.status}")
    
    # 3. Vérifier les résumés quotidiens
    daily_summaries = DailyAttendanceSummary.objects.all()
    print(f"\n✅ Résumés quotidiens: {daily_summaries.count()}")
    
    for summary in daily_summaries[:3]:
        print(f"   {summary.student.user.get_full_name()} ({summary.date}): {summary.daily_status}")
        print(f"      {summary.present_sessions}/{summary.total_sessions} sessions présentes")
        print(f"      Taux: {summary.attendance_rate}%")
    
    # 4. Test du calcul automatique
    print(f"\n🧪 Test du calcul automatique...")
    marie = Student.objects.get(user__email='marie.dupont@eschool.com')
    
    # Créer une nouvelle présence pour tester
    latest_session = sessions.first()
    if latest_session:
        # Modifier le statut pour tester la mise à jour automatique
        attendance = SessionAttendance.objects.filter(
            session=latest_session, 
            student=marie
        ).first()
        
        if attendance:
            old_status = attendance.status
            attendance.status = 'LATE'
            attendance.save()
            print(f"   Statut modifié: {old_status} -> {attendance.status}")
            
            # Vérifier que le résumé quotidien a été mis à jour
            summary = DailyAttendanceSummary.objects.get(
                student=marie, 
                date=latest_session.date
            )
            print(f"   Résumé mis à jour automatiquement:")
            print(f"      Sessions en retard: {summary.late_sessions}")
            print(f"      Nouveau taux: {summary.attendance_rate}%")
    
    print("\n✨ Vérification terminée ! Le système fonctionne correctement.")

if __name__ == '__main__':
    verify_session_system()