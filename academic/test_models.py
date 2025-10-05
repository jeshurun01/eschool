"""
Tests complets pour les modèles du module academic
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from django.core.files.base import ContentFile

from accounts.models import Teacher, Student, Parent
from .models import (
    AcademicYear, Level, Subject, ClassRoom, TeacherAssignment,
    Enrollment, Timetable, Attendance, Grade, Document, DocumentAccess,
    Period
)

User = get_user_model()


class AcademicYearModelTest(TestCase):
    """Tests pour le modèle AcademicYear"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.academic_year), "2024-2025")
    
    def test_creation(self):
        """Test de création d'une année académique"""
        self.assertEqual(self.academic_year.name, "2024-2025")
        self.assertEqual(self.academic_year.start_date, date(2024, 9, 1))
        self.assertEqual(self.academic_year.end_date, date(2025, 7, 31))
        self.assertTrue(self.academic_year.is_current)
    
    def test_unique_current_year(self):
        """Test qu'une seule année peut être courante"""
        # Créer une nouvelle année courante
        new_year = AcademicYear.objects.create(
            name="2025-2026",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
            is_current=True
        )
        
        # Vérifier que l'ancienne n'est plus courante
        self.academic_year.refresh_from_db()
        self.assertFalse(self.academic_year.is_current)
        self.assertTrue(new_year.is_current)
    
    def test_ordering(self):
        """Test de l'ordre par défaut"""
        year1 = AcademicYear.objects.create(
            name="2023-2024",
            start_date=date(2023, 9, 1),
            end_date=date(2024, 7, 31)
        )
        year2 = AcademicYear.objects.create(
            name="2022-2023",
            start_date=date(2022, 9, 1),
            end_date=date(2023, 7, 31)
        )
        
        years = list(AcademicYear.objects.all())
        # Doit être ordonné par start_date décroissant
        self.assertEqual(years[0], self.academic_year)  # 2024-2025
        self.assertEqual(years[1], year1)  # 2023-2024
        self.assertEqual(years[2], year2)  # 2022-2023


class LevelModelTest(TestCase):
    """Tests pour le modèle Level"""
    
    def setUp(self):
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de sixième",
            order=6
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.level), "6ème")
    
    def test_creation(self):
        """Test de création d'un niveau"""
        self.assertEqual(self.level.name, "6ème")
        self.assertEqual(self.level.description, "Classe de sixième")
        self.assertEqual(self.level.order, 6)
    
    def test_ordering(self):
        """Test de l'ordre par défaut"""
        level1 = Level.objects.create(name="5ème", order=5)
        level2 = Level.objects.create(name="4ème", order=4)
        
        levels = list(Level.objects.all())
        self.assertEqual(levels[0], level2)  # 4ème (order=4)
        self.assertEqual(levels[1], level1)  # 5ème (order=5)
        self.assertEqual(levels[2], self.level)  # 6ème (order=6)


class SubjectModelTest(TestCase):
    """Tests pour le modèle Subject"""
    
    def setUp(self):
        self.level = Level.objects.create(name="6ème", order=6)
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH",
            description="Cours de mathématiques",
            coefficient=3,
            color="#3B82F6"
        )
        self.subject.levels.add(self.level)
    
    def test_str_representation(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.subject), "Mathématiques (MATH)")
    
    def test_creation(self):
        """Test de création d'une matière"""
        self.assertEqual(self.subject.name, "Mathématiques")
        self.assertEqual(self.subject.code, "MATH")
        self.assertEqual(self.subject.description, "Cours de mathématiques")
        self.assertEqual(self.subject.coefficient, 3)
        self.assertEqual(self.subject.color, "#3B82F6")
        self.assertIn(self.level, self.subject.levels.all())
    
    def test_unique_code(self):
        """Test que le code doit être unique"""
        with self.assertRaises(Exception):  # IntegrityError
            Subject.objects.create(
                name="Autre Math",
                code="MATH",  # Code déjà existant
                coefficient=2
            )
    
    def test_default_values(self):
        """Test des valeurs par défaut"""
        subject = Subject.objects.create(
            name="Français",
            code="FR"
        )
        self.assertEqual(subject.coefficient, 1.0)
        self.assertEqual(subject.color, "#3B82F6")


class ClassRoomModelTest(TestCase):
    """Tests pour le modèle ClassRoom"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.level = Level.objects.create(name="6ème", order=6)
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30,
            room_number="A101"
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"6ème A - 6ème ({self.academic_year.name})"
        self.assertEqual(str(self.classroom), expected)
    
    def test_creation(self):
        """Test de création d'une classe"""
        self.assertEqual(self.classroom.name, "6ème A")
        self.assertEqual(self.classroom.level, self.level)
        self.assertEqual(self.classroom.academic_year, self.academic_year)
        self.assertEqual(self.classroom.capacity, 30)
        self.assertEqual(self.classroom.room_number, "A101")
    
    def test_current_enrollment_property(self):
        """Test de la propriété current_enrollment"""
        # Créer des étudiants et les inscrire
        for i in range(3):
            user = User.objects.create_user(
                email=f"student{i}@test.com",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Test",
                role="STUDENT"
            )
            student = Student.objects.create(user=user)
            Enrollment.objects.create(
                student=student,
                classroom=self.classroom,
                academic_year=self.academic_year
            )
        
        self.assertEqual(self.classroom.current_enrollment, 3)
    
    def test_is_full_property(self):
        """Test de la propriété is_full"""
        # Classe vide
        self.assertFalse(self.classroom.is_full)
        
        # Remplir la classe
        for i in range(30):
            user = User.objects.create_user(
                email=f"student{i}@test.com",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Test",
                role="STUDENT"
            )
            student = Student.objects.create(user=user)
            Enrollment.objects.create(
                student=student,
                classroom=self.classroom,
                academic_year=self.academic_year
            )
        
        self.assertTrue(self.classroom.is_full)
    
    def test_unique_constraint(self):
        """Test de la contrainte unique sur name, level, academic_year"""
        with self.assertRaises(Exception):  # IntegrityError
            ClassRoom.objects.create(
                name="6ème A",  # Même nom
                level=self.level,  # Même niveau
                academic_year=self.academic_year,  # Même année
                capacity=25
            )


class EnrollmentModelTest(TestCase):
    """Tests pour le modèle Enrollment"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.level = Level.objects.create(name="6ème", order=6)
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        self.user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Martin",
            role="STUDENT"
        )
        self.student = Student.objects.create(user=self.user)
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
            academic_year=self.academic_year
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"{self.student.user.full_name} - {self.classroom.name} ({self.academic_year.name})"
        self.assertEqual(str(self.enrollment), expected)
    
    def test_creation(self):
        """Test de création d'une inscription"""
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.classroom, self.classroom)
        self.assertEqual(self.enrollment.academic_year, self.academic_year)
        self.assertTrue(self.enrollment.is_active)
        self.assertEqual(self.enrollment.enrollment_date, date.today())
    
    def test_unique_active_enrollment_constraint(self):
        """Test de la contrainte unique active enrollment per year"""
        # Créer une autre classe
        classroom2 = ClassRoom.objects.create(
            name="6ème B",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        
        # L'étudiant ne peut pas être inscrit dans deux classes actives la même année
        with self.assertRaises(Exception):  # IntegrityError
            Enrollment.objects.create(
                student=self.student,
                classroom=classroom2,
                academic_year=self.academic_year,
                is_active=True
            )
    
    def test_multiple_inactive_enrollments(self):
        """Test qu'un étudiant peut avoir plusieurs inscriptions inactives"""
        classroom2 = ClassRoom.objects.create(
            name="6ème B",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        
        # Désactiver l'inscription actuelle
        self.enrollment.is_active = False
        self.enrollment.save()
        
        # Créer une nouvelle inscription active
        enrollment2 = Enrollment.objects.create(
            student=self.student,
            classroom=classroom2,
            academic_year=self.academic_year,
            is_active=True
        )
        
        self.assertTrue(enrollment2.is_active)
        self.assertFalse(self.enrollment.is_active)


class GradeModelTest(TestCase):
    """Tests pour le modèle Grade"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.level = Level.objects.create(name="6ème", order=6)
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH",
            coefficient=3
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role="TEACHER"
        )
        self.teacher = Teacher.objects.create(user=self.teacher_user)
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Martin",
            role="STUDENT"
        )
        self.student = Student.objects.create(user=self.student_user)
        
        self.grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Contrôle 1",
            evaluation_type="TEST",
            score=15.5,
            max_score=20,
            coefficient=2,
            date=date.today(),
            comments="Très bien"
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"{self.student.user.full_name} - {self.subject.name} - Contrôle 1: 15.5/20"
        self.assertEqual(str(self.grade), expected)
    
    def test_creation(self):
        """Test de création d'une note"""
        self.assertEqual(self.grade.student, self.student)
        self.assertEqual(self.grade.subject, self.subject)
        self.assertEqual(self.grade.teacher, self.teacher)
        self.assertEqual(self.grade.classroom, self.classroom)
        self.assertEqual(self.grade.evaluation_name, "Contrôle 1")
        self.assertEqual(self.grade.evaluation_type, "TEST")
        self.assertEqual(self.grade.score, Decimal('15.5'))
        self.assertEqual(self.grade.max_score, Decimal('20'))
        self.assertEqual(self.grade.coefficient, Decimal('2'))
        self.assertEqual(self.grade.date, date.today())
        self.assertEqual(self.grade.comments, "Très bien")
    
    def test_percentage_property(self):
        """Test de la propriété percentage"""
        self.assertEqual(self.grade.percentage, 77.5)  # 15.5/20 * 100
        
        # Test avec max_score = 0
        grade_zero = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Test",
            evaluation_type="TEST",
            score=10,
            max_score=0,
            date=date.today()
        )
        self.assertEqual(grade_zero.percentage, 0)
    
    def test_weighted_score_property(self):
        """Test de la propriété weighted_score"""
        self.assertEqual(self.grade.weighted_score, Decimal('31'))  # 15.5 * 2
    
    def test_validation_score_positive(self):
        """Test de validation que le score doit être positif"""
        with self.assertRaises(ValidationError):
            grade = Grade(
                student=self.student,
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                evaluation_name="Test",
                evaluation_type="TEST",
                score=-5,  # Score négatif
                max_score=20,
                date=date.today()
            )
            grade.full_clean()


class AttendanceModelTest(TestCase):
    """Tests pour le modèle Attendance"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.level = Level.objects.create(name="6ème", order=6)
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH"
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role="TEACHER"
        )
        self.teacher = Teacher.objects.create(user=self.teacher_user)
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Martin",
            role="STUDENT"
        )
        self.student = Student.objects.create(user=self.student_user)
        
        self.attendance = Attendance.objects.create(
            student=self.student,
            classroom=self.classroom,
            subject=self.subject,
            teacher=self.teacher,
            date=date.today(),
            status='PRESENT',
            justification=""
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"{self.student.user.full_name} - {date.today()} - Présent"
        self.assertEqual(str(self.attendance), expected)
    
    def test_creation(self):
        """Test de création d'une présence"""
        self.assertEqual(self.attendance.student, self.student)
        self.assertEqual(self.attendance.classroom, self.classroom)
        self.assertEqual(self.attendance.subject, self.subject)
        self.assertEqual(self.attendance.teacher, self.teacher)
        self.assertEqual(self.attendance.date, date.today())
        self.assertEqual(self.attendance.status, 'PRESENT')
        self.assertEqual(self.attendance.justification, "")
    
    def test_status_choices(self):
        """Test des choix de statut"""
        statuses = ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED']
        for status in statuses:
            attendance = Attendance.objects.create(
                student=self.student,
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                date=date.today(),
                status=status
            )
            self.assertEqual(attendance.status, status)
    
    def test_unique_constraint(self):
        """Test de la contrainte unique sur student, date, subject"""
        with self.assertRaises(Exception):  # IntegrityError
            Attendance.objects.create(
                student=self.student,
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                date=date.today(),  # Même date
                status='ABSENT'
            )


class DocumentModelTest(TestCase):
    """Tests pour le modèle Document"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.level = Level.objects.create(name="6ème", order=6)
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH"
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role="TEACHER"
        )
        self.teacher = Teacher.objects.create(user=self.teacher_user)
        
        self.document = Document.objects.create(
            title="Cours de mathématiques",
            description="Introduction aux équations",
            document_type="COURSE",
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            file=ContentFile(b"fake file content", name="math_intro.pdf"),
            is_public=True,
            is_downloadable=True
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"{self.document.title} - {self.subject.name}"
        self.assertEqual(str(self.document), expected)
    
    def test_creation(self):
        """Test de création d'un document"""
        self.assertEqual(self.document.title, "Cours de mathématiques")
        self.assertEqual(self.document.description, "Introduction aux équations")
        self.assertEqual(self.document.document_type, "COURSE")
        self.assertEqual(self.document.subject, self.subject)
        self.assertEqual(self.document.teacher, self.teacher)
        self.assertEqual(self.document.classroom, self.classroom)
        self.assertTrue(self.document.is_public)
        self.assertTrue(self.document.is_downloadable)
    
    def test_file_size_property(self):
        """Test de la propriété file_size_mb"""
        # Le fichier fait 18 bytes, donc 0.02 MB
        self.assertAlmostEqual(self.document.file_size_mb, 0.02, places=2)
    
    def test_is_accessible_property(self):
        """Test de la propriété is_accessible"""
        # Document sans dates de restriction
        self.assertTrue(self.document.is_accessible)
        
        # Document avec date d'accès future
        future_doc = Document.objects.create(
            title="Document futur",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="future.pdf"),
            access_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(future_doc.is_accessible)
        
        # Document expiré
        expired_doc = Document.objects.create(
            title="Document expiré",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="expired.pdf"),
            expiry_date=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(expired_doc.is_accessible)
    
    def test_file_icon_property(self):
        """Test de la propriété file_icon"""
        # PDF
        self.assertEqual(self.document.file_icon, 'fas fa-file-pdf text-red-500')
        
        # Document Word
        word_doc = Document.objects.create(
            title="Document Word",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="document.docx")
        )
        self.assertEqual(word_doc.file_icon, 'fas fa-file-word text-blue-500')
        
        # Document inconnu
        unknown_doc = Document.objects.create(
            title="Document inconnu",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="document.xyz")
        )
        self.assertEqual(unknown_doc.file_icon, 'fas fa-file text-gray-400')


class TimetableModelTest(TestCase):
    """Tests pour le modèle Timetable"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.level = Level.objects.create(name="6ème", order=6)
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH"
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role="TEACHER"
        )
        self.teacher = Teacher.objects.create(user=self.teacher_user)
        
        self.timetable = Timetable.objects.create(
            classroom=self.classroom,
            subject=self.subject,
            teacher=self.teacher,
            weekday=1,  # Lundi
            start_time="08:00",
            end_time="09:00",
            room="A101"
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"{self.classroom.name} - {self.subject.name} - Lundi 08:00"
        self.assertEqual(str(self.timetable), expected)
    
    def test_creation(self):
        """Test de création d'un emploi du temps"""
        self.assertEqual(self.timetable.classroom, self.classroom)
        self.assertEqual(self.timetable.subject, self.subject)
        self.assertEqual(self.timetable.teacher, self.teacher)
        self.assertEqual(self.timetable.weekday, 1)
        self.assertEqual(str(self.timetable.start_time), "08:00:00")
        self.assertEqual(str(self.timetable.end_time), "09:00:00")
        self.assertEqual(self.timetable.room, "A101")
    
    def test_weekday_choices(self):
        """Test des choix de jour de la semaine"""
        weekdays = [1, 2, 3, 4, 5, 6, 7]
        for day in weekdays:
            timetable = Timetable.objects.create(
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                weekday=day,
                start_time="08:00",
                end_time="09:00"
            )
            self.assertEqual(timetable.weekday, day)
    
    def test_clean_validation(self):
        """Test de la validation clean()"""
        # Heure de début >= heure de fin
        with self.assertRaises(ValidationError):
            timetable = Timetable(
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                weekday=1,
                start_time="09:00",
                end_time="08:00"  # Fin avant début
            )
            timetable.clean()


class PeriodModelTest(TestCase):
    """Tests pour le modèle Period"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        self.period = Period.objects.create(
            name="1er Trimestre",
            academic_year=self.academic_year,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 20),
            is_current=True
        )
    
    def test_str_representation(self):
        """Test de la représentation string"""
        expected = f"1er Trimestre ({self.academic_year.name})"
        self.assertEqual(str(self.period), expected)
    
    def test_creation(self):
        """Test de création d'une période"""
        self.assertEqual(self.period.name, "1er Trimestre")
        self.assertEqual(self.period.academic_year, self.academic_year)
        self.assertEqual(self.period.start_date, date(2024, 9, 1))
        self.assertEqual(self.period.end_date, date(2024, 12, 20))
        self.assertTrue(self.period.is_current)
    
    def test_unique_current_period_per_year(self):
        """Test qu'une seule période peut être courante par année"""
        # Créer une nouvelle période courante
        new_period = Period.objects.create(
            name="2ème Trimestre",
            academic_year=self.academic_year,
            start_date=date(2024, 12, 21),
            end_date=date(2025, 3, 20),
            is_current=True
        )
        
        # Vérifier que l'ancienne n'est plus courante
        self.period.refresh_from_db()
        self.assertFalse(self.period.is_current)
        self.assertTrue(new_period.is_current)


class AcademicModelRelationsTest(TestCase):
    """Tests des relations entre modèles académiques"""
    
    def setUp(self):
        # Créer la hiérarchie complète
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(name="6ème", order=6)
        
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH",
            coefficient=3
        )
        self.subject.levels.add(self.level)
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            role="TEACHER"
        )
        self.teacher = Teacher.objects.create(user=self.teacher_user)
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Martin",
            role="STUDENT"
        )
        self.student = Student.objects.create(
            user=self.student_user,
            current_class=self.classroom
        )
        
        # Créer les relations
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
            academic_year=self.academic_year
        )
        
        self.assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            subject=self.subject,
            academic_year=self.academic_year,
            hours_per_week=4
        )
    
    def test_level_subject_relationship(self):
        """Test de la relation many-to-many Level-Subject"""
        self.assertIn(self.subject, self.level.subjects.all())
        self.assertIn(self.level, self.subject.levels.all())
    
    def test_classroom_level_relationship(self):
        """Test de la relation ForeignKey ClassRoom-Level"""
        self.assertEqual(self.classroom.level, self.level)
        self.assertIn(self.classroom, self.level.classrooms.all())
    
    def test_classroom_academic_year_relationship(self):
        """Test de la relation ForeignKey ClassRoom-AcademicYear"""
        self.assertEqual(self.classroom.academic_year, self.academic_year)
        self.assertIn(self.classroom, self.academic_year.classrooms.all())
    
    def test_enrollment_relationships(self):
        """Test des relations Enrollment"""
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.classroom, self.classroom)
        self.assertEqual(self.enrollment.academic_year, self.academic_year)
        
        # Vérifier les relations inverses
        self.assertIn(self.enrollment, self.student.enrollments.all())
        self.assertIn(self.enrollment, self.classroom.enrollments.all())
    
    def test_teacher_assignment_relationships(self):
        """Test des relations TeacherAssignment"""
        self.assertEqual(self.assignment.teacher, self.teacher)
        self.assertEqual(self.assignment.classroom, self.classroom)
        self.assertEqual(self.assignment.subject, self.subject)
        self.assertEqual(self.assignment.academic_year, self.academic_year)
        
        # Vérifier les relations inverses
        self.assertIn(self.assignment, self.teacher.teacherassignment_set.all())
        self.assertIn(self.assignment, self.classroom.teacherassignment_set.all())
        self.assertIn(self.assignment, self.subject.teacherassignment_set.all())
    
    def test_cascade_deletions(self):
        """Test des suppressions en cascade"""
        # Supprimer l'année académique
        self.academic_year.delete()
        
        # Vérifier que les classes sont supprimées
        self.assertFalse(ClassRoom.objects.filter(id=self.classroom.id).exists())
        
        # Vérifier que les inscriptions sont supprimées
        self.assertFalse(Enrollment.objects.filter(id=self.enrollment.id).exists())
        
        # Vérifier que les assignations sont supprimées
        self.assertFalse(TeacherAssignment.objects.filter(id=self.assignment.id).exists())
    
    def test_student_classroom_relationship(self):
        """Test de la relation Student-ClassRoom"""
        self.assertEqual(self.student.current_class, self.classroom)
        self.assertIn(self.student, self.classroom.students.all())

