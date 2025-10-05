#!/usr/bin/env python
"""
Script pour nettoyer complètement la base de données et créer des données de test réalistes
Usage: python manage.py shell < scripts/reset_and_populate.py
       OU: python scripts/reset_and_populate.py
"""

import os
import sys
import django
from datetime import date, timedelta, time, datetime
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
import random
import unicodedata

# Configuration Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher, Parent
from academic.models import (
    AcademicYear, Level, ClassRoom, Subject, Enrollment, 
    TeacherAssignment, Timetable, Grade, Session, Period,
    SessionAssignment, Document, SessionAttendance, DailyAttendanceSummary
)
from finance.models import FeeType, FeeStructure, Invoice, PaymentMethod, Payment
from communication.models import Announcement, Message

# Fonction pour supprimer les accents des chaînes
def remove_accents(input_str):
    """Supprime les accents d'une chaîne de caractères pour les emails"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

print("=" * 80)
print("🧹 NETTOYAGE ET CRÉATION DE DONNÉES DE TEST - eSchool")
print("=" * 80)
print()

# ============================================================================
# ÉTAPE 1 : NETTOYAGE DE LA BASE DE DONNÉES
# ============================================================================

print("🗑️  ÉTAPE 1/8 : Suppression de toutes les données existantes...")
print("-" * 80)

try:
    with transaction.atomic():
        # Ordre de suppression (important pour les contraintes de clés étrangères)
        models_to_delete = [
            # Communication
            (Message, "Messages"),
            (Announcement, "Annonces"),
            
            # Finance
            (Payment, "Paiements"),
            (Invoice, "Factures"),
            (FeeStructure, "Structures de frais"),
            (FeeType, "Types de frais"),
            (PaymentMethod, "Méthodes de paiement"),
            
            # Academic - Relations et données
            (SessionAttendance, "Présences par session"),
            (DailyAttendanceSummary, "Résumés de présences journalières"),
            (Grade, "Notes"),
            (SessionAssignment, "Devoirs"),
            (Document, "Documents"),
            (Session, "Sessions de cours"),
            (Timetable, "Emplois du temps"),
            (TeacherAssignment, "Attributions enseignants"),
            (Enrollment, "Inscriptions"),
            
            # Academic - Structure
            (ClassRoom, "Classes"),
            (Subject, "Matières"),
            (Level, "Niveaux"),
            (AcademicYear, "Années scolaires"),
            
            # Accounts
            (Student, "Élèves"),
            (Teacher, "Enseignants"),
            (Parent, "Parents"),
        ]
        
        for model, name in models_to_delete:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                print(f"   ✅ {name}: {count} enregistrement(s) supprimé(s)")
        
        # Supprimer les utilisateurs (sauf superuser)
        user_count = User.objects.filter(is_superuser=False).count()
        if user_count > 0:
            User.objects.filter(is_superuser=False).delete()
            print(f"   ✅ Utilisateurs: {user_count} enregistrement(s) supprimé(s)")
        
        print()
        print("✅ Base de données nettoyée avec succès!")
        print()

except Exception as e:
    print(f"❌ Erreur lors du nettoyage: {str(e)}")
    sys.exit(1)

# ============================================================================
# ÉTAPE 2 : CRÉATION DE L'ANNÉE SCOLAIRE
# ============================================================================

print("📅 ÉTAPE 2/8 : Création de l'année scolaire...")
print("-" * 80)

try:
    academic_year = AcademicYear.objects.create(
        name="2024-2025",
        start_date=date(2024, 9, 1),
        end_date=date(2025, 6, 30),
        is_current=True
    )
    print(f"   ✅ Année scolaire créée: {academic_year.name}")
    print()

except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    sys.exit(1)

# ============================================================================
# ÉTAPE 3 : CRÉATION DES NIVEAUX ET MATIÈRES
# ============================================================================

print("📚 ÉTAPE 3/8 : Création des niveaux et matières...")
print("-" * 80)

# Niveaux
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
    ("2nde", "Seconde", 10),
    ("1ère", "Première", 11),
    ("Tle", "Terminale", 12),
]

levels = []
for name, description, order in levels_data:
    level = Level.objects.create(name=name, description=description, order=order)
    levels.append(level)
    print(f"   ✅ Niveau: {level.name}")

print()

# Matières avec couleurs
subjects_data = [
    ("Français", "FR", "Cours de Français", Decimal("2.0"), "#EF4444"),
    ("Mathématiques", "MATH", "Cours de Mathématiques", Decimal("2.0"), "#3B82F6"),
    ("Histoire-Géographie", "HG", "Cours d'Histoire-Géographie", Decimal("1.5"), "#F59E0B"),
    ("Sciences Physiques", "PHY", "Cours de Physique-Chimie", Decimal("2.0"), "#10B981"),
    ("Sciences de la Vie et de la Terre", "SVT", "Cours de SVT", Decimal("1.5"), "#059669"),
    ("Anglais", "ANG", "Cours d'Anglais", Decimal("1.5"), "#8B5CF6"),
    ("Espagnol", "ESP", "Cours d'Espagnol", Decimal("1.0"), "#EC4899"),
    ("Éducation Physique", "EPS", "Éducation Physique et Sportive", Decimal("1.0"), "#F97316"),
    ("Arts Plastiques", "ART", "Cours d'Arts Plastiques", Decimal("1.0"), "#A855F7"),
    ("Musique", "MUS", "Cours de Musique", Decimal("1.0"), "#06B6D4"),
    ("Informatique", "INFO", "Cours d'Informatique", Decimal("1.5"), "#6366F1"),
    ("Philosophie", "PHIL", "Cours de Philosophie", Decimal("2.0"), "#94A3B8"),
]

subjects = []
for name, code, description, coef, color in subjects_data:
    subject = Subject.objects.create(
        name=name, 
        code=code, 
        description=description, 
        coefficient=coef,
        color=color
    )
    # Associer les matières aux niveaux appropriés
    if code in ['FR', 'MATH', 'EPS', 'ART', 'MUS']:
        subject.levels.set(levels[:9])  # Tous les niveaux primaire et collège
    elif code in ['PHY', 'SVT', 'PHIL']:
        subject.levels.set(levels[5:])  # Collège et lycée
    else:
        subject.levels.set(levels)  # Tous les niveaux
    
    subjects.append(subject)
    print(f"   ✅ Matière: {subject.name} ({subject.code})")

print()

# ============================================================================
# ÉTAPE 4 : CRÉATION DES UTILISATEURS
# ============================================================================

print("👥 ÉTAPE 4/8 : Création des utilisateurs...")
print("-" * 80)

# Enseignants
teachers_data = [
    ("Marie", "Dubois", "marie.dubois@eschool.com", "F", "FR"),
    ("Jean", "Martin", "jean.martin@eschool.com", "M", "MATH"),
    ("Sophie", "Bernard", "sophie.bernard@eschool.com", "F", "ANG"),
    ("Pierre", "Durand", "pierre.durand@eschool.com", "M", "HG"),
    ("Isabelle", "Moreau", "isabelle.moreau@eschool.com", "F", "PHY"),
    ("Thomas", "Laurent", "thomas.laurent@eschool.com", "M", "SVT"),
    ("Catherine", "Simon", "catherine.simon@eschool.com", "F", "EPS"),
    ("Nicolas", "Michel", "nicolas.michel@eschool.com", "M", "INFO"),
    ("Émilie", "Lefebvre", "emilie.lefebvre@eschool.com", "F", "ART"),
    ("Alexandre", "Garcia", "alexandre.garcia@eschool.com", "M", "ESP"),
]

teachers = []
for first_name, last_name, email, gender, subject_code in teachers_data:
    user = User.objects.create_user(
        email=email,
        password='password123',
        first_name=first_name,
        last_name=last_name,
        role='TEACHER',
        gender=gender,
        is_active=True
    )
    
    teacher = Teacher.objects.create(
        user=user,
        hire_date=date(2020, 9, 1),
        education_level="Licence/Master"
    )
    # Associer la matière principale
    subject_obj = next((s for s in subjects if s.code == subject_code), None)
    if subject_obj:
        teacher.subjects.add(subject_obj)
    
    teachers.append(teacher)
    print(f"   ✅ Enseignant: {user.full_name} ({subject_obj.name if subject_obj else 'Général'})")

print()

# Parents - Créer 30 couples de parents (60 parents au total)
parents_data = [
    # Format: (Prénom Mère, Prénom Père, Nom de famille, Email base)
    ("Sophie", "Marc", "Dubois"),
    ("Marie", "Pierre", "Martin"),
    ("Claire", "Jean", "Bernard"),
    ("Isabelle", "François", "Petit"),
    ("Catherine", "Philippe", "Robert"),
    ("Nathalie", "Laurent", "Richard"),
    ("Véronique", "Alain", "Durand"),
    ("Sandrine", "Michel", "Leroy"),
    ("Sylvie", "Patrick", "Moreau"),
    ("Christine", "Daniel", "Simon"),
    ("Brigitte", "Thierry", "Laurent"),
    ("Monique", "Gérard", "Lefebvre"),
    ("Annie", "Christian", "Roux"),
    ("Nicole", "Dominique", "Morel"),
    ("Martine", "Pascal", "Fournier"),
    ("Françoise", "Jacques", "Girard"),
    ("Élisabeth", "André", "Bonnet"),
    ("Jacqueline", "Bernard", "Fontaine"),
    ("Chantal", "Christophe", "Rousseau"),
    ("Danielle", "Stéphane", "Vincent"),
    ("Valérie", "Olivier", "Muller"),
    ("Laurence", "Bruno", "Lefèvre"),
    ("Corinne", "Éric", "Mercier"),
    ("Agnès", "Didier", "Blanc"),
    ("Patricia", "Yves", "Guérin"),
    ("Hélène", "Serge", "Boyer"),
    ("Odette", "René", "Garnier"),
    ("Laure", "Henri", "Chevalier"),
    ("Pauline", "Georges", "François"),
    ("Juliette", "Louis", "Legrand"),
]

parents = []
parent_index = 0
for mother_name, father_name, last_name in parents_data:
    # Créer la mère
    mother_email = f"{remove_accents(mother_name.lower())}.{remove_accents(last_name.lower())}@gmail.com"
    mother_user = User.objects.create_user(
        email=mother_email,
        password='password123',
        first_name=mother_name,
        last_name=last_name,
        role='PARENT',
        gender='F',
        is_active=True
    )
    mother = Parent.objects.create(
        user=mother_user,
        relationship='MOTHER',
        profession=f"Profession de {mother_name}"
    )
    parents.append(mother)
    
    # Créer le père
    father_email = f"{remove_accents(father_name.lower())}.{remove_accents(last_name.lower())}@gmail.com"
    father_user = User.objects.create_user(
        email=father_email,
        password='password123',
        first_name=father_name,
        last_name=last_name,
        role='PARENT',
        gender='M',
        is_active=True
    )
    father = Parent.objects.create(
        user=father_user,
        relationship='FATHER',
        profession=f"Profession de {father_name}"
    )
    parents.append(father)
    
    print(f"   ✅ Couple parental {parent_index + 1}: {mother_name} & {father_name} {last_name}")
    parent_index += 1

print()

# Élèves - Générer au moins 5 élèves par classe (12 niveaux × 5 = 60 élèves minimum)
first_names_m = [
    "Alexandre", "Lucas", "Hugo", "Louis", "Nathan", "Tom", "Maxime", "Thomas", "Antoine", "Paul",
    "Léo", "Raphaël", "Arthur", "Jules", "Gabriel", "Noah", "Adam", "Mathis", "Enzo", "Théo",
    "Baptiste", "Victor", "Sacha", "Clément", "Mathéo", "Nicolas", "Julien", "Simon", "Pierre", "Marc",
    "Benjamin", "David", "Alexandre", "Romain", "Valentin", "Adrien", "Damien", "Florian", "Quentin", "Maxence",
    "Kylian", "Dylan", "Ryan", "Nolan", "Ethan", "Liam", "Yanis", "Timéo", "Axel", "Robin",
]

first_names_f = [
    "Marie", "Emma", "Léa", "Chloé", "Camille", "Julie", "Sarah", "Laura", "Clara", "Manon",
    "Jade", "Louise", "Alice", "Lola", "Zoé", "Inès", "Léna", "Anaïs", "Margot", "Nina",
    "Juliette", "Pauline", "Charlotte", "Éléonore", "Céline", "Sophie", "Amélie", "Océane", "Marine", "Lucie",
    "Caroline", "Mélanie", "Aurélie", "Noémie", "Clémence", "Mathilde", "Élise", "Agathe", "Victoire", "Iris",
    "Rose", "Jeanne", "Anna", "Eva", "Mila", "Lily", "Luna", "Chloé", "Maëlys", "Romane",
]

# Créer des élèves - minimum 5 par niveau
students_data = []
parent_couple_index = 0
children_per_couple = {}  # Track number of children per couple

for level in levels:
    # 5 à 7 élèves par classe
    num_students = random.randint(5, 7)
    
    for i in range(num_students):
        # Alterner entre filles et garçons
        gender = 'M' if (i % 2 == 0) else 'F'
        first_name = random.choice(first_names_m if gender == 'M' else first_names_f)
        
        # Assigner des parents (maximum 3 enfants par couple)
        parent_indices = []
        if parent_couple_index < len(parents_data):
            couple_base = parent_couple_index * 2  # Chaque couple = 2 parents consécutifs
            
            # Vérifier combien d'enfants ce couple a déjà
            if couple_base not in children_per_couple:
                children_per_couple[couple_base] = 0
            
            if children_per_couple[couple_base] < 3:
                # Assigner les deux parents
                parent_indices = [couple_base, couple_base + 1]
                children_per_couple[couple_base] += 1
                
                # Si le couple a atteint 3 enfants, passer au suivant
                if children_per_couple[couple_base] >= 3:
                    parent_couple_index += 1
        
        # Obtenir le nom de famille des parents
        if parent_indices:
            last_name = parents_data[parent_indices[0] // 2][2]
        else:
            last_name = random.choice([
                "Dupont", "Garcia", "Rodriguez", "Sanchez", "Fernandez",
                "Martinez", "Lopez", "Gonzalez", "Perez", "Diaz"
            ])
        
        email = f"{remove_accents(first_name.lower())}.{remove_accents(last_name.lower())}{i}@student.eschool.com"
        
        students_data.append((first_name, last_name, email, gender, parent_indices, level.name))

print(f"   📊 Génération de {len(students_data)} élèves répartis sur {len(levels)} niveaux")
print()

students = []
for first_name, last_name, email, gender, parent_indices, level_name in students_data:
    user = User.objects.create_user(
        email=email,
        password='password123',
        first_name=first_name,
        last_name=last_name,
        role='STUDENT',
        gender=gender,
        is_active=True,
        date_of_birth=date(2010, 1, 1)  # Date fictive
    )
    
    student = Student.objects.create(
        user=user,
        enrollment_date=date(2024, 9, 1)
    )
    
    # Associer les parents
    if parent_indices:
        for idx in parent_indices:
            if idx < len(parents):
                student.parents.add(parents[idx])
    
    students.append((student, level_name))
    parent_names = ", ".join([parents[i].user.full_name for i in parent_indices if i < len(parents)])
    print(f"   ✅ Élève: {user.full_name} ({level_name}) - Parents: {parent_names or 'Aucun'}")

print()

# ============================================================================
# ÉTAPE 5 : CRÉATION DES CLASSES ET INSCRIPTIONS
# ============================================================================

print("🏫 ÉTAPE 5/8 : Création des classes et inscriptions...")
print("-" * 80)

# Créer une classe par niveau avec des élèves
classrooms = []
for level in levels:
    # Nom de la classe
    if level.order <= 5:
        class_name = f"Classe {level.name}"
    elif level.order <= 9:
        class_name = f"Classe {level.name}A"
    else:
        class_name = f"Classe {level.name}S"  # Scientifique
    
    # Créer la classe
    classroom = ClassRoom.objects.create(
        name=class_name,
        level=level,
        academic_year=academic_year,
        head_teacher=teachers[level.order % len(teachers)],
        capacity=30,
        room_number=f"Salle {100 + level.order}"
    )
    classrooms.append(classroom)
    print(f"   ✅ Classe créée: {classroom.name} - Prof principal: {classroom.head_teacher.user.full_name}")
    
    # Inscrire les élèves correspondants
    students_in_level = [s for s, l in students if l == level.name]
    for student in students_in_level:
        enrollment = Enrollment.objects.create(
            student=student,
            classroom=classroom,
            academic_year=academic_year,
            enrollment_date=date(2024, 9, 1),
            is_active=True
        )
        # Mettre à jour current_class
        student.current_class = classroom
        student.save()
        print(f"      → Élève inscrit: {student.user.full_name}")

print()

# ============================================================================
# ÉTAPE 6 : ATTRIBUTION DES ENSEIGNANTS AUX CLASSES
# ============================================================================

print("👨‍🏫 ÉTAPE 6/8 : Attribution des enseignants aux classes...")
print("-" * 80)

# Mapper les enseignants à leurs matières
teacher_subject_map = {
    teachers[0]: [s for s in subjects if s.code == 'FR'][0],
    teachers[1]: [s for s in subjects if s.code == 'MATH'][0],
    teachers[2]: [s for s in subjects if s.code == 'ANG'][0],
    teachers[3]: [s for s in subjects if s.code == 'HG'][0],
    teachers[4]: [s for s in subjects if s.code == 'PHY'][0],
    teachers[5]: [s for s in subjects if s.code == 'SVT'][0],
    teachers[6]: [s for s in subjects if s.code == 'EPS'][0],
    teachers[7]: [s for s in subjects if s.code == 'INFO'][0],
    teachers[8]: [s for s in subjects if s.code == 'ART'][0],
    teachers[9]: [s for s in subjects if s.code == 'ESP'][0],
}

assignments_created = 0
for classroom in classrooms:
    # Attribuer plusieurs enseignants par classe
    for teacher, subject in teacher_subject_map.items():
        # Vérifier si la matière est appropriée pour le niveau
        if classroom.level in subject.levels.all():
            assignment = TeacherAssignment.objects.create(
                teacher=teacher,
                classroom=classroom,
                subject=subject,
                academic_year=academic_year,
                hours_per_week=random.randint(2, 4)
            )
            assignments_created += 1
            print(f"   ✅ {teacher.user.full_name} → {subject.name} dans {classroom.name}")

print(f"\n   Total: {assignments_created} attributions créées\n")

# ============================================================================
# ÉTAPE 7 : CRÉATION DES DONNÉES ACADÉMIQUES
# ============================================================================

print("📊 ÉTAPE 7/8 : Création des emplois du temps, sessions, devoirs, notes et présences...")
print("-" * 80)

# Créer une période académique
period = Period.objects.create(
    name="1er Trimestre",
    academic_year=academic_year,
    start_date=date(2024, 9, 1),
    end_date=date(2024, 12, 20),
    is_current=True
)
print(f"   ✅ Période créée: {period.name}")

# Créer des emplois du temps pour chaque classe
timetables_created = 0
for classroom in classrooms:
    assignments = TeacherAssignment.objects.filter(classroom=classroom)
    
    weekday = 1  # Lundi
    start_hour = 8
    
    for assignment in assignments:
        # Créer 2-3 créneaux par semaine pour chaque matière
        for i in range(2):
            if start_hour >= 17:
                weekday += 1
                start_hour = 8
                if weekday > 5:  # Pas de cours le week-end
                    break
            
            timetable = Timetable.objects.create(
                classroom=classroom,
                subject=assignment.subject,
                teacher=assignment.teacher,
                weekday=weekday,
                start_time=time(start_hour, 0),
                end_time=time(start_hour + 1, 0),
                room=classroom.room_number or f"Salle {100 + classroom.level.order}"
            )
            timetables_created += 1
            start_hour += 1

print(f"   ✅ {timetables_created} créneaux d'emploi du temps créés")

# Sessions de cours (derniers 30 jours)
sessions_count = 0
today = timezone.now().date()

# Pour chaque créneau, créer des sessions dans les 30 derniers jours
for timetable in Timetable.objects.all():
    # Calculer les dates où ce créneau a eu lieu
    for days_ago in range(1, 31):
        check_date = today - timedelta(days=days_ago)
        
        # Vérifier si c'est le bon jour de la semaine
        if check_date.isoweekday() == timetable.weekday:
            # Créer la session
            session = Session.objects.create(
                timetable=timetable,
                period=period,
                date=check_date,
                actual_start_time=timetable.start_time,
                actual_end_time=timetable.end_time,
                lesson_title=f"Cours {timetable.subject.name}",
                lesson_content=f"Contenu du cours de {timetable.subject.name}",
                status='COMPLETED',
                attendance_taken=True,
                attendance_taken_at=timezone.make_aware(datetime.combine(check_date, timetable.start_time))
            )
            
            # Créer les présences pour les élèves de la classe
            enrolled_students = Enrollment.objects.filter(
                classroom=timetable.classroom,
                is_active=True
            ).select_related('student')
            
            for enrollment in enrolled_students:
                # 90% de présence, 5% absent, 5% retard
                rand = random.random()
                if rand < 0.90:
                    status = 'PRESENT'
                elif rand < 0.95:
                    status = 'ABSENT'
                else:
                    status = 'LATE'
                
                SessionAttendance.objects.create(
                    session=session,
                    student=enrollment.student,
                    status=status,
                    notes="Présent" if status == 'PRESENT' else "",
                    recorded_by=session.teacher.user
                )
            
            sessions_count += 1

print(f"   ✅ {sessions_count} sessions de cours créées avec présences")

# Devoirs (SessionAssignment)
assignments_count = 0
for session in Session.objects.filter(status='COMPLETED')[:100]:  # Limiter à 100 sessions récentes
    # 30% de chances d'avoir un devoir
    if random.random() < 0.3:
        days_offset = random.randint(3, 14)  # Entre 3 et 14 jours
        due_date = timezone.make_aware(
            datetime.combine(session.date + timedelta(days=days_offset), time(23, 59))
        )
        
        assignment_types = ['HOMEWORK', 'EXERCISE', 'PROJECT', 'RESEARCH']
        
        assignment = SessionAssignment.objects.create(
            session=session,
            title=f"Devoir {session.subject.name}",
            description=f"Description détaillée du devoir en {session.subject.name}",
            assignment_type=random.choice(assignment_types),
            priority='MEDIUM',
            due_date=due_date,
            estimated_duration=random.randint(30, 120),
            will_be_graded=True,
            max_score=Decimal('20.0'),
            coefficient=Decimal('1.0'),
            instructions=f"Instructions pour le devoir de {session.subject.name}",
            is_published=True,
            published_at=timezone.make_aware(datetime.combine(session.date, time(session.actual_start_time.hour if session.actual_start_time else 8, 0))),
            created_by=session.teacher.user
        )
        assignments_count += 1

print(f"   ✅ {assignments_count} devoirs créés")

# Notes
grades_count = 0
for classroom in classrooms:
    enrolled_students = Enrollment.objects.filter(
        classroom=classroom,
        is_active=True
    ).select_related('student')
    
    teacher_assignments = TeacherAssignment.objects.filter(classroom=classroom)
    
    for ta in teacher_assignments:
        # 5-8 notes par matière pour chaque élève
        num_grades = random.randint(5, 8)
        
        for enrollment in enrolled_students:
            for i in range(num_grades):
                days_ago = random.randint(5, 60)
                grade_date = today - timedelta(days=days_ago)
                
                # Score réaliste: entre 8 et 20
                score = Decimal(str(random.uniform(8.0, 20.0)))
                score = round(score, 2)
                
                eval_types = ['HOMEWORK', 'TEST', 'EXAM', 'PROJECT']
                
                grade = Grade.objects.create(
                    student=enrollment.student,
                    subject=ta.subject,
                    teacher=ta.teacher,
                    classroom=classroom,
                    evaluation_name=f"Évaluation {i+1}",
                    evaluation_type=random.choice(eval_types),
                    score=score,
                    max_score=Decimal('20.0'),
                    coefficient=Decimal('1.0'),
                    date=grade_date,
                    comments=f"Bon travail" if score >= 15 else "À améliorer"
                )
                grades_count += 1

print(f"   ✅ {grades_count} notes créées")

# Résumés journaliers de présence
daily_summary_count = 0
for student, _ in students:
    # Créer des résumés pour les 30 derniers jours
    for days_ago in range(1, 31):
        summary_date = today - timedelta(days=days_ago)
        
        # Statistiques réalistes
        rand = random.random()
        if rand < 0.85:  # 85% présence complète
            daily_status = 'FULLY_PRESENT'
            present = random.randint(4, 6)
            absent = 0
            late = 0
        elif rand < 0.95:  # 10% quelques absences
            daily_status = 'PARTIAL'
            present = random.randint(3, 5)
            absent = random.randint(1, 2)
            late = 0
        else:  # 5% absent
            daily_status = 'FULLY_ABSENT'
            present = 0
            absent = random.randint(4, 6)
            late = 0
        
        DailyAttendanceSummary.objects.update_or_create(
            student=student,
            date=summary_date,
            defaults={
                'daily_status': daily_status,
                'present_sessions': present,
                'absent_sessions': absent,
                'late_sessions': late,
                'total_sessions': present + absent + late
            }
        )
        daily_summary_count += 1

print(f"   ✅ {daily_summary_count} résumés journaliers de présence créés")

print()

# ============================================================================
# ÉTAPE 8 : CRÉATION DES DONNÉES FINANCIÈRES
# ============================================================================

print("💰 ÉTAPE 8/8 : Création des données financières...")
print("-" * 80)

# Types de frais
fee_types_data = [
    ("Scolarité", "Frais de scolarité annuels"),
    ("Inscription", "Frais d'inscription"),
    ("Transport", "Frais de transport scolaire"),
    ("Cantine", "Frais de restauration"),
    ("Activités", "Frais d'activités extrascolaires"),
]

fee_types = []
for name, description in fee_types_data:
    fee_type = FeeType.objects.create(name=name, description=description)
    fee_types.append(fee_type)
    print(f"   ✅ Type de frais: {name}")

print()

# Structures de frais par niveau
for level in levels:
    # Frais de scolarité variables selon le niveau
    if level.order <= 5:  # Primaire
        scolarite = Decimal('150000')
    elif level.order <= 9:  # Collège
        scolarite = Decimal('200000')
    else:  # Lycée
        scolarite = Decimal('250000')
    
    FeeStructure.objects.create(
        fee_type=fee_types[0],  # Scolarité
        level=level,
        academic_year=academic_year,
        amount=scolarite
    )
    
    # Transport
    FeeStructure.objects.create(
        fee_type=fee_types[2],
        level=level,
        academic_year=academic_year,
        amount=Decimal('50000')
    )
    
    # Cantine
    FeeStructure.objects.create(
        fee_type=fee_types[3],
        level=level,
        academic_year=academic_year,
        amount=Decimal('30000')
    )

print(f"   ✅ Structures de frais créées pour tous les niveaux")

# Méthodes de paiement
payment_methods_data = [
    ("Espèces", "CASH", "Paiement en espèces"),
    ("Chèque", "CHECK", "Paiement par chèque"),
    ("Virement", "TRANSFER", "Virement bancaire"),
    ("Mobile Money", "MOBILE", "Paiement mobile"),
]

payment_methods = []
for name, code, description in payment_methods_data:
    method = PaymentMethod.objects.create(name=name, code=code, description=description)
    payment_methods.append(method)
    print(f"   ✅ Méthode de paiement: {name}")

print()

# Factures pour chaque élève
invoices_count = 0
payments_count = 0

for student, level_name in students:
    # Récupérer le niveau
    level = next((l for l in levels if l.name == level_name), None)
    if not level:
        continue
    
    # Facture de scolarité
    fee_structure = FeeStructure.objects.filter(
        fee_type=fee_types[0],
        level=level,
        academic_year=academic_year
    ).first()
    
    if fee_structure:
        # Créer la facture
        invoice = Invoice.objects.create(
            student=student,
            issue_date=date(2024, 9, 1),
            due_date=date(2024, 10, 31),
            status='PARTIAL' if random.random() < 0.3 else 'PAID',
            notes="Facture de scolarité 2024-2025"
        )
        
        # Créer un article de facture
        from finance.models import InvoiceItem
        InvoiceItem.objects.create(
            invoice=invoice,
            fee_type=fee_types[0],
            description="Frais de scolarité",
            quantity=Decimal('1.0'),
            unit_price=fee_structure.amount,
            total=fee_structure.amount
        )
        
        # Mettre à jour le total de la facture
        invoice.update_total()
        invoices_count += 1
        
        # Créer des paiements
        if invoice.status in ['PAID', 'PARTIAL']:
            # Paiement partiel ou complet
            num_payments = random.randint(1, 3)
            total_paid = Decimal('0')
            
            for i in range(num_payments):
                if invoice.status == 'PAID':
                    if i == num_payments - 1:
                        amount = invoice.total_amount - total_paid
                    else:
                        amount = invoice.total_amount / num_payments
                else:  # PARTIAL
                    amount = invoice.total_amount * Decimal('0.3')  # 30% payé
                
                if amount > 0:
                    payment = Payment.objects.create(
                        invoice=invoice,
                        amount=amount,
                        payment_method=random.choice(payment_methods),
                        payment_date=timezone.make_aware(datetime.combine(date(2024, 9, random.randint(1, 30)), time(10, 0))),
                        status='COMPLETED',
                        notes=f"Paiement {i+1}/{num_payments}"
                    )
                    total_paid += amount
                    payments_count += 1

print(f"   ✅ {invoices_count} factures créées")
print(f"   ✅ {payments_count} paiements enregistrés")

print()

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================

print("=" * 80)
print("✅ CRÉATION DES DONNÉES DE TEST TERMINÉE AVEC SUCCÈS!")
print("=" * 80)
print()
print("📊 STATISTIQUES FINALES:")
print("-" * 80)
print(f"   Années scolaires    : {AcademicYear.objects.count()}")
print(f"   Niveaux             : {Level.objects.count()}")
print(f"   Matières            : {Subject.objects.count()}")
print(f"   Classes             : {ClassRoom.objects.count()}")
print(f"   Enseignants         : {Teacher.objects.count()}")
print(f"   Parents             : {Parent.objects.count()}")
print(f"   Élèves              : {Student.objects.count()}")
print(f"   Inscriptions        : {Enrollment.objects.count()}")
print(f"   Attributions prof.  : {TeacherAssignment.objects.count()}")
print(f"   Sessions de cours   : {Session.objects.count()}")
print(f"   Présences (session) : {SessionAttendance.objects.count()}")
print(f"   Présences (jour)    : {DailyAttendanceSummary.objects.count()}")
print(f"   Devoirs             : {SessionAssignment.objects.count()}")
print(f"   Notes               : {Grade.objects.count()}")
print(f"   Types de frais      : {FeeType.objects.count()}")
print(f"   Structures frais    : {FeeStructure.objects.count()}")
print(f"   Factures            : {Invoice.objects.count()}")
print(f"   Paiements           : {Payment.objects.count()}")
print()
print("🔑 COMPTES DE TEST:")
print("-" * 80)

# Récupérer quelques comptes existants pour les afficher
sample_teacher = Teacher.objects.first()
sample_parent = Parent.objects.first()
sample_student_6eme = Student.objects.filter(current_class__level__name="6ème").first()
sample_student_1ere = Student.objects.filter(current_class__level__name="1ère").first()

print("   Enseignant    : marie.dubois@eschool.com / password123")
if sample_parent:
    print(f"   Parent        : {sample_parent.user.email} / password123")
if sample_student_6eme:
    print(f"   Élève (6ème)  : {sample_student_6eme.user.email} / password123")
if sample_student_1ere:
    print(f"   Élève (1ère)  : {sample_student_1ere.user.email} / password123")

print()
print("💡 INFO IMPORTANTE:")
print("-" * 80)
print(f"   📚 {Student.objects.count()} élèves créés (5-7 par classe)")
print(f"   👨‍👩‍👧‍👦 {Parent.objects.count()} parents créés (30 couples)")
print(f"   🏠 Maximum 3 enfants par couple de parents")
print(f"   📊 Répartition équitable sur tous les niveaux")
print(f"   ✉️  Les accents sont supprimés des emails pour faciliter la connexion")
print(f"   📧 Exemple: Véronique → veronique, François → francois")
print()
print("🌐 Accès application: http://127.0.0.1:8000/")
print("⚙️  Interface admin : http://127.0.0.1:8000/admin/")
print()
print("=" * 80)
