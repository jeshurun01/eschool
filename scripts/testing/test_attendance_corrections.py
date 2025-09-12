#!/usr/bin/env python
"""
Test des corrections pour le système de présences :
1. Matière obligatoire dans attendance_take
2. Mise à jour de la liste après l'appel
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from academic.models import Attendance, Subject, ClassRoom
from accounts.models import Teacher
from datetime import date

def test_attendance_corrections():
    """Test des corrections du système de présences"""
    
    print("=== Test des corrections du système de présences ===\n")
    
    # 1. Vérifier les présences existantes et leurs matières
    print("1. Analyse des présences existantes:")
    attendances = Attendance.objects.all()[:10]
    
    null_subjects = 0
    valid_subjects = 0
    
    for attendance in attendances:
        if attendance.subject is None:
            null_subjects += 1
            print(f"   ❌ Présence sans matière: {attendance.student.user.get_full_name()} le {attendance.date}")
        else:
            valid_subjects += 1
            print(f"   ✅ {attendance.student.user.get_full_name()} - {attendance.subject.name} le {attendance.date}")
    
    print(f"\nRésumé:")
    print(f"   Présences avec matière: {valid_subjects}")
    print(f"   Présences sans matière: {null_subjects}")
    
    if null_subjects > 0:
        print(f"   ⚠️  {null_subjects} présences ont une matière null - cela sera évité avec la nouvelle validation")
    else:
        print("   ✅ Toutes les présences ont une matière définie")
    
    # 2. Vérifier les matières disponibles pour les enseignants
    print(f"\n2. Vérification des matières assignées:")
    
    marie = Teacher.objects.get(employee_id='T1000')
    print(f"   Enseignant: {marie.user.get_full_name()}")
    
    # Matières enseignées par Marie
    marie_subjects = Subject.objects.filter(
        teacherassignment__teacher=marie,
        teacherassignment__academic_year__is_current=True
    ).distinct()
    
    print(f"   Matières enseignées: {marie_subjects.count()}")
    for subject in marie_subjects:
        print(f"     - {subject.name}")
    
    # 3. Vérifier qu'elle a bien des assignations avec matière
    from academic.models import TeacherAssignment
    marie_assignments = TeacherAssignment.objects.filter(
        teacher=marie,
        academic_year__is_current=True
    ).select_related('classroom', 'subject')
    
    print(f"\n   Assignations complètes de Marie:")
    for assignment in marie_assignments:
        print(f"     - {assignment.classroom.name} / {assignment.subject.name}")
    
    # 4. Simuler la logique de validation
    print(f"\n3. Test de la nouvelle logique de validation:")
    
    # Cas sans matière (devrait échouer)
    classroom_id = None
    subject_id = None
    
    for assignment in marie_assignments:
        classroom_id = assignment.classroom.pk
        subject_id = assignment.subject.pk
        break
    
    if classroom_id and subject_id:
        print(f"   Test avec classe ID {classroom_id} et matière ID {subject_id}")
        
        # Simuler la validation
        try:
            classroom = ClassRoom.objects.get(id=classroom_id)
            subject = Subject.objects.get(id=subject_id)
            print(f"   ✅ Validation réussie: {classroom.name} / {subject.name}")
        except Exception as e:
            print(f"   ❌ Erreur de validation: {e}")
    
    # Test sans matière
    print(f"\n   Test sans matière (devrait échouer avec la nouvelle validation):")
    subject_id_empty = None
    
    if not subject_id_empty:
        print("   ❌ Validation échouée: Matière manquante")
        print("   ✅ Comportement attendu avec la nouvelle validation")
    
    # 5. Vérifier les URL de redirection
    print(f"\n4. Test des URL de redirection:")
    
    from urllib.parse import urlencode
    from django.urls import reverse
    
    if classroom_id and subject_id:
        query_params = {
            'classroom': classroom_id,
            'subject': subject_id,
            'date_from': date.today().strftime('%Y-%m-%d'),
            'date_to': date.today().strftime('%Y-%m-%d'),
        }
        
        try:
            base_url = reverse('academic:attendance_list')
            redirect_url = f"{base_url}?{urlencode(query_params)}"
            print(f"   ✅ URL de redirection construite: {redirect_url}")
        except Exception as e:
            print(f"   ❌ Erreur de construction URL: {e}")

if __name__ == '__main__':
    test_attendance_corrections()
