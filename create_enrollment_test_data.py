#!/usr/bin/env python
"""
Script pour créer des données de test d'inscription d'étudiants
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Student, Teacher
from academic.models import ClassRoom, Enrollment, AcademicYear
from django.contrib.auth import get_user_model

def create_enrollment_test_data():
    """Créer des inscriptions de test"""
    
    # Récupérer l'année académique courante
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        print("❌ Aucune année académique courante trouvée")
        return
    
    print(f"✅ Année courante: {current_year}")
    
    # Récupérer le teacher de test
    try:
        teacher = Teacher.objects.get(id=2)
        print(f"✅ Teacher: {teacher}")
    except Teacher.DoesNotExist:
        print("❌ Teacher ID 2 non trouvé")
        return
    
    # Récupérer les classes enseignées par ce teacher
    classrooms = ClassRoom.objects.filter(timetables__teacher=teacher).distinct()
    print(f"✅ Classes enseignées: {list(classrooms)}")
    
    if not classrooms:
        print("❌ Aucune classe trouvée pour ce teacher")
        return
    
    # Récupérer quelques étudiants
    students = Student.objects.all()[:5]
    print(f"✅ Étudiants disponibles: {list(students)}")
    
    if not students:
        print("❌ Aucun étudiant trouvé")
        return
    
    # Créer des inscriptions
    created_count = 0
    for classroom in classrooms:
        for i, student in enumerate(students[:3]):  # 3 étudiants par classe
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                classroom=classroom,
                academic_year=current_year,
                defaults={'is_active': True}
            )
            if created:
                print(f"✅ Créé inscription: {student.user.get_full_name()} -> {classroom.name}")
                created_count += 1
            else:
                print(f"ℹ️  Inscription existe: {student.user.get_full_name()} -> {classroom.name}")
    
    print(f"\n🎉 {created_count} nouvelles inscriptions créées!")
    
    # Vérifier les inscriptions
    total_enrollments = Enrollment.objects.filter(
        classroom__timetables__teacher=teacher,
        is_active=True
    ).count()
    print(f"📊 Total inscriptions actives pour ce teacher: {total_enrollments}")

if __name__ == "__main__":
    create_enrollment_test_data()