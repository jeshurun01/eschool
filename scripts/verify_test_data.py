#!/usr/bin/env python
"""
Script pour vérifier les données de test créées
"""

import os
import sys
import django
from datetime import date

# Configuration Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student
from academic.models import Grade, Timetable

def verify_test_data():
    print("🔍 Vérification des données de test...")
    
    try:
        # Vérifier que Marie Dupont existe
        marie = User.objects.get(email='marie.dupont@eschool.com')
        print(f'✅ Utilisateur trouvé: {marie.get_full_name()} - Role: {marie.role}')
        
        student = marie.student_profile
        print(f'✅ Étudiant trouvé: {student.matricule} - Classe: {student.current_class}')
        
        # Vérifier les grades
        grades = Grade.objects.filter(student=student, date__gte=date.today()).order_by('date')
        print(f'✅ Examens/Devoirs à venir: {grades.count()}')
        for grade in grades[:3]:
            print(f'   - {grade.evaluation_name} ({grade.subject.name}) le {grade.date}')
        
        # Vérifier les emplois du temps
        if student.current_class:
            timetables = Timetable.objects.filter(classroom=student.current_class)
            print(f'✅ Cours hebdomadaires: {timetables.count()}')
            for tt in timetables[:3]:
                weekdays = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
                day_name = weekdays[tt.weekday - 1] if 1 <= tt.weekday <= 5 else f'Jour {tt.weekday}'
                print(f'   - {tt.subject.name} le {day_name} à {tt.start_time}')
        
        print("\n🎯 Les données sont prêtes pour le test du calendrier !")
        
    except Exception as e:
        print(f'❌ Erreur: {e}')

if __name__ == '__main__':
    verify_test_data()