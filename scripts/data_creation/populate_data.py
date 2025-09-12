#!/usr/bin/env python
"""
Script pour créer des données de test pour l'application eSchool
Usage: python manage.py shell < populate_data.py
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from decimal import Decimal
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher, Parent
from academic.models import AcademicYear, Level, ClassRoom, Subject, Enrollment, Attendance
from finance.models import FeeType, FeeStructure, Invoice, PaymentMethod, Payment

print("🚀 Début de la création des données de test...")

# 1. Créer l'année scolaire actuelle
print("📅 Création de l'année scolaire...")
academic_year, created = AcademicYear.objects.get_or_create(
    name="2024-2025",
    defaults={
        'start_date': date(2024, 9, 1),
        'end_date': date(2025, 6, 30),
        'is_current': True
    }
)
if created:
    print(f"✅ Année scolaire créée: {academic_year.name}")

# 2. Créer les niveaux
print("📚 Création des niveaux...")
levels_data = [
    ("CP", "Cours Préparatoire", 1),
    ("CE1", "Cours Élémentaire 1", 2),
    ("CE2", "Cours Élémentaire 2", 3),
    ("CM1", "Cours Moyen 1", 4),
    ("CM2", "Cours Moyen 2", 5),
    ("6ème", "Sixième", 6),
    ("5ème", "Cinquième", 7),
    ("4ème", "Quatrième", 8),
    ("3ème", "Troisième", 9),
]

levels = []
for name, description, order in levels_data:
    level, created = Level.objects.get_or_create(
        name=name,
        defaults={'description': description, 'order': order}
    )
    levels.append(level)
    if created:
        print(f"✅ Niveau créé: {level.name}")

# 3. Créer les matières
print("📖 Création des matières...")
subjects_data = [
    ("Français", "FR", "Cours de Français"),
    ("Mathématiques", "MATH", "Cours de Mathématiques"),
    ("Histoire-Géographie", "HG", "Cours d'Histoire-Géographie"),
    ("Sciences", "SCI", "Cours de Sciences"),
    ("Anglais", "ANG", "Cours d'Anglais"),
    ("Sport", "EPS", "Éducation Physique et Sportive"),
    ("Arts Plastiques", "ART", "Cours d'Arts Plastiques"),
    ("Musique", "MUS", "Cours de Musique"),
    ("Informatique", "INFO", "Cours d'Informatique")
]

subjects = []
for subject_name, code, description in subjects_data:
    subject, created = Subject.objects.get_or_create(
        code=code,
        defaults={
            'name': subject_name,
            'description': description,
            'coefficient': 1.0
        }
    )
    subjects.append(subject)
    if created:
        print(f"✅ Matière créée: {subject.name}")

# 4. Créer les enseignants
print("👨‍🏫 Création des enseignants...")
teachers_data = [
    ("Marie", "Dupont", "marie.dupont@eschool.com", "F"),
    ("Jean", "Martin", "jean.martin@eschool.com", "M"),
    ("Sophie", "Bernard", "sophie.bernard@eschool.com", "F"),
    ("Pierre", "Durand", "pierre.durand@eschool.com", "M"),
    ("Isabelle", "Moreau", "isabelle.moreau@eschool.com", "F"),
    ("Thomas", "Laurent", "thomas.laurent@eschool.com", "M"),
    ("Catherine", "Simon", "catherine.simon@eschool.com", "F"),
    ("Nicolas", "Michel", "nicolas.michel@eschool.com", "M"),
]

teachers = []
for first_name, last_name, email, gender in teachers_data:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': 'TEACHER',
            'gender': gender,
            'phone': f"0{6}{hash(email) % 100000000:08d}",
            'date_of_birth': date(1980 + hash(email) % 15, 1 + hash(email) % 12, 1 + hash(email) % 28),
            'is_active': True,
        }
    )
    if created:
        user.set_password('teacher123')
        user.save()
        print(f"✅ Enseignant créé: {user.full_name}")
    
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={
            'employee_id': f"T{1000 + len(teachers)}",
            'hire_date': date(2020, 9, 1),
            'education_level': 'Master en Éducation',
            'certifications': f'Certification en {subjects[len(teachers) % len(subjects)].name}'
        }
    )
    teachers.append(teacher)

# 5. Créer les classes
print("🏫 Création des classes...")
classrooms = []
for level in levels:
    for section in ['A', 'B']:
        classroom, created = ClassRoom.objects.get_or_create(
            name=f"{level.name} {section}",
            level=level,
            academic_year=academic_year,
            defaults={
                'capacity': 30,
                'room_number': f"{level.order}{section}",
                'head_teacher': teachers[hash(f"{level.name}{section}") % len(teachers)]
            }
        )
        classrooms.append(classroom)
        if created:
            print(f"✅ Classe créée: {classroom.name}")

# 6. Créer les parents
print("👨‍👩‍👧‍👦 Création des parents...")
parents_data = [
    ("Robert", "Leroy", "robert.leroy@gmail.com", "M"),
    ("Sylvie", "Leroy", "sylvie.leroy@gmail.com", "F"),
    ("Michel", "Blanc", "michel.blanc@gmail.com", "M"),
    ("Anne", "Blanc", "anne.blanc@gmail.com", "F"),
    ("François", "Garnier", "francois.garnier@gmail.com", "M"),
    ("Patricia", "Garnier", "patricia.garnier@gmail.com", "F"),
    ("Alain", "Faure", "alain.faure@gmail.com", "M"),
    ("Christine", "Faure", "christine.faure@gmail.com", "F"),
    ("Daniel", "Andre", "daniel.andre@gmail.com", "M"),
    ("Brigitte", "Andre", "brigitte.andre@gmail.com", "F"),
]

parents = []
for first_name, last_name, email, gender in parents_data:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': 'PARENT',
            'gender': gender,
            'phone': f"0{6}{hash(email) % 100000000:08d}",
            'date_of_birth': date(1975 + hash(email) % 15, 1 + hash(email) % 12, 1 + hash(email) % 28),
            'is_active': True,
        }
    )
    if created:
        user.set_password('parent123')
        user.save()
        print(f"✅ Parent créé: {user.full_name}")
    
    parent, created = Parent.objects.get_or_create(
        user=user,
        defaults={
            'profession': ['Ingénieur', 'Médecin', 'Professeur', 'Commerçant', 'Avocat'][hash(email) % 5],
            'workplace': f"Entreprise {last_name}",
        }
    )
    parents.append(parent)

# 7. Créer les élèves
print("👨‍🎓 Création des élèves...")
students_data = [
    ("Lucas", "Leroy", "lucas.leroy@student.eschool.com", "M", 0, 0),  # Parents: Robert & Sylvie
    ("Emma", "Leroy", "emma.leroy@student.eschool.com", "F", 0, 1),
    ("Hugo", "Blanc", "hugo.blanc@student.eschool.com", "M", 2, 3),    # Parents: Michel & Anne
    ("Léa", "Blanc", "lea.blanc@student.eschool.com", "F", 2, 3),
    ("Tom", "Garnier", "tom.garnier@student.eschool.com", "M", 4, 5),  # Parents: François & Patricia
    ("Sarah", "Garnier", "sarah.garnier@student.eschool.com", "F", 4, 5),
    ("Nathan", "Faure", "nathan.faure@student.eschool.com", "M", 6, 7), # Parents: Alain & Christine
    ("Chloé", "Faure", "chloe.faure@student.eschool.com", "F", 6, 7),
    ("Maxime", "Andre", "maxime.andre@student.eschool.com", "M", 8, 9), # Parents: Daniel & Brigitte
    ("Manon", "Andre", "manon.andre@student.eschool.com", "F", 8, 9),
    ("Antoine", "Petit", "antoine.petit@student.eschool.com", "M", None, None),
    ("Julie", "Roux", "julie.roux@student.eschool.com", "F", None, None),
    ("Clément", "Morel", "clement.morel@student.eschool.com", "M", None, None),
    ("Camille", "Fournier", "camille.fournier@student.eschool.com", "F", None, None),
    ("Alexandre", "Girard", "alexandre.girard@student.eschool.com", "M", None, None),
]

students = []
for i, (first_name, last_name, email, gender, father_idx, mother_idx) in enumerate(students_data):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': 'STUDENT',
            'gender': gender,
            'date_of_birth': date(2010 + i % 10, 1 + i % 12, 1 + i % 28),
            'is_active': True,
        }
    )
    if created:
        user.set_password('student123')
        user.save()
        print(f"✅ Élève créé: {user.full_name}")
    
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'enrollment_date': date(2024, 9, 1),
            'current_class': classrooms[i % len(classrooms)],
        }
    )
    
    # Add parent relationships
    if father_idx is not None and mother_idx is not None:
        student.parents.add(parents[father_idx], parents[mother_idx])
    
    students.append(student)

# 8. Créer les inscriptions
print("📝 Création des inscriptions...")
for student in students:
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        academic_year=academic_year,
        defaults={
            'classroom': student.current_class,
            'enrollment_date': date(2024, 9, 1),
            'is_active': True
        }
    )
    if created:
        print(f"✅ Inscription créée: {student.user.full_name} en {enrollment.classroom.name}")

# 9. Créer les types de frais
print("💰 Création des types de frais...")
fee_types_data = [
    ("Scolarité", "Frais de scolarité mensuels", True, True),
    ("Inscription", "Frais d'inscription annuels", False, True),
    ("Transport", "Frais de transport scolaire", True, False),
    ("Cantine", "Frais de restauration", True, False),
    ("Activités", "Frais d'activités extra-scolaires", False, False),
]

fee_types = []
for name, description, is_recurring, is_mandatory in fee_types_data:
    fee_type, created = FeeType.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'is_recurring': is_recurring,
            'is_mandatory': is_mandatory
        }
    )
    fee_types.append(fee_type)
    if created:
        print(f"✅ Type de frais créé: {fee_type.name}")

# 10. Créer les structures de frais
print("💳 Création des structures de frais...")
for fee_type in fee_types:
    for level in levels:
        amount = Decimal('50000') if fee_type.name == 'Scolarité' else \
                 Decimal('25000') if fee_type.name == 'Inscription' else \
                 Decimal('15000') if fee_type.name == 'Transport' else \
                 Decimal('20000') if fee_type.name == 'Cantine' else \
                 Decimal('10000')
        
        fee_structure, created = FeeStructure.objects.get_or_create(
            fee_type=fee_type,
            level=level,
            academic_year=academic_year,
            defaults={
                'amount': amount,
                'due_date': date(2024, 10, 15) if fee_type.name == 'Inscription' else None
            }
        )
        if created:
            print(f"✅ Structure de frais créée: {fee_type.name} - {level.name}")

# 11. Créer les méthodes de paiement
print("💳 Création des méthodes de paiement...")
payment_methods_data = [
    ("Espèces", "CASH", "Paiement en espèces", True),
    ("Chèque", "CHECK", "Paiement par chèque", True),
    ("Virement", "BANK", "Virement bancaire", True),
    ("Mobile Money", "MOBILE", "Paiement mobile", True),
]

payment_methods = []
for name, code, description, is_active in payment_methods_data:
    method, created = PaymentMethod.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'description': description,
            'is_active': is_active
        }
    )
    payment_methods.append(method)
    if created:
        print(f"✅ Méthode de paiement créée: {method.name}")

# 12. Créer quelques factures et paiements
print("📄 Création des factures et paiements...")
for i, student in enumerate(students[:10]):  # Seulement pour 10 étudiants
    # Facture de scolarité
    invoice, created = Invoice.objects.get_or_create(
        student=student,
        defaults={
            'parent': student.parents.first() if student.parents.exists() else None,
            'issue_date': date(2024, 9, 15),
            'due_date': date(2024, 10, 15),
            'subtotal': Decimal('50000'),
            'total_amount': Decimal('50000'),
            'status': 'PAID' if i < 7 else 'PENDING',
            'notes': f"Facture de scolarité pour {student.user.full_name}"
        }
    )
    
    if created and invoice.status == 'PAID':
        # Créer un paiement pour les factures payées
        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=payment_methods[i % len(payment_methods)],
            amount=invoice.total_amount,
            payment_date=timezone.now() - timedelta(days=i),
            status='COMPLETED',
            notes=f"Paiement reçu pour {student.user.full_name}"
        )
        print(f"✅ Facture et paiement créés: {student.user.full_name}")
    elif created:
        print(f"✅ Facture créée (en attente): {student.user.full_name}")

# 13. Créer quelques présences
print("✅ Création des données de présence...")
today = date.today()
for day_offset in range(7):  # 7 derniers jours
    attendance_date = today - timedelta(days=day_offset)
    for student in students[:8]:  # Pour 8 étudiants
        status = 'PRESENT' if hash(f"{student.id}{day_offset}") % 10 < 8 else 'ABSENT'
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            date=attendance_date,
            defaults={
                'classroom': student.current_class,
                'teacher': student.current_class.head_teacher if student.current_class.head_teacher else teachers[0],
                'status': status,
                'justification': 'Présence normale' if status == 'PRESENT' else 'Absence justifiée'
            }
        )
        if created:
            print(f"✅ Présence créée: {student.user.full_name} - {attendance_date} - {status}")

print("\n🎉 Création des données de test terminée avec succès!")
print("\n📊 Résumé des données créées:")
print(f"- Utilisateurs: {User.objects.count()}")
print(f"- Étudiants: {Student.objects.count()}")
print(f"- Enseignants: {Teacher.objects.count()}")
print(f"- Parents: {Parent.objects.count()}")
print(f"- Classes: {ClassRoom.objects.count()}")
print(f"- Matières: {Subject.objects.count()}")
print(f"- Inscriptions: {Enrollment.objects.count()}")
print(f"- Factures: {Invoice.objects.count()}")
print(f"- Paiements: {Payment.objects.count()}")
print(f"- Présences: {Attendance.objects.count()}")

print("\n🔑 Comptes de test créés:")
print("Admin: admin@eschool.com / admin123")
print("Enseignants: [nom.prenom]@eschool.com / teacher123")
print("Parents: [nom.prenom]@gmail.com / parent123")
print("Étudiants: [nom.prenom]@student.eschool.com / student123")
