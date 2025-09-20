"""
Tests pour les managers personnalisés du module academic
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from accounts.models import Teacher, Student, Parent
from .models import (
    AcademicYear, Level, Subject, ClassRoom, TeacherAssignment,
    Enrollment, Grade, Attendance, Document
)

User = get_user_model()


class GradeManagerTest(TestCase):
    """Tests pour le GradeManager"""
    
    def setUp(self):
        # Configuration de base
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
        
        # Utilisateurs
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
        
        # Créer des notes de test
        self.grade1 = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Contrôle 1",
            evaluation_type="TEST",
            score=15.0,
            max_score=20,
            coefficient=2,
            date=date.today() - timedelta(days=10)
        )
        
        self.grade2 = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Contrôle 2",
            evaluation_type="TEST",
            score=18.0,
            max_score=20,
            coefficient=2,
            date=date.today() - timedelta(days=5)
        )
        
        self.grade3 = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Examen",
            evaluation_type="EXAM",
            score=16.0,
            max_score=20,
            coefficient=3,
            date=date.today()
        )
    
    def test_grade_manager_exists(self):
        """Test que le GradeManager existe"""
        self.assertTrue(hasattr(Grade.objects, 'for_student'))
        self.assertTrue(hasattr(Grade.objects, 'for_subject'))
        self.assertTrue(hasattr(Grade.objects, 'for_classroom'))
    
    def test_for_student_method(self):
        """Test de la méthode for_student"""
        grades = Grade.objects.for_student(self.student)
        self.assertEqual(grades.count(), 3)
        self.assertIn(self.grade1, grades)
        self.assertIn(self.grade2, grades)
        self.assertIn(self.grade3, grades)
    
    def test_for_subject_method(self):
        """Test de la méthode for_subject"""
        grades = Grade.objects.for_subject(self.subject)
        self.assertEqual(grades.count(), 3)
        self.assertIn(self.grade1, grades)
        self.assertIn(self.grade2, grades)
        self.assertIn(self.grade3, grades)
    
    def test_for_classroom_method(self):
        """Test de la méthode for_classroom"""
        grades = Grade.objects.for_classroom(self.classroom)
        self.assertEqual(grades.count(), 3)
        self.assertIn(self.grade1, grades)
        self.assertIn(self.grade2, grades)
        self.assertIn(self.grade3, grades)
    
    def test_average_calculation(self):
        """Test du calcul de moyenne"""
        # Calculer la moyenne manuellement
        total_weighted = (15.0 * 2) + (18.0 * 2) + (16.0 * 3)  # 30 + 36 + 48 = 114
        total_coefficient = 2 + 2 + 3  # 7
        expected_average = total_weighted / total_coefficient  # 114/7 ≈ 16.29
        
        # Vérifier que les notes sont bien calculées
        grades = Grade.objects.for_student(self.student)
        weighted_sum = sum(grade.weighted_score for grade in grades)
        coefficient_sum = sum(grade.coefficient for grade in grades)
        actual_average = weighted_sum / coefficient_sum
        
        self.assertAlmostEqual(actual_average, expected_average, places=2)


class ClassRoomManagerTest(TestCase):
    """Tests pour le ClassRoomManager"""
    
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(name="6ème", order=6)
        
        # Créer plusieurs classes
        self.classroom1 = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        
        self.classroom2 = ClassRoom.objects.create(
            name="6ème B",
            level=self.level,
            academic_year=self.academic_year,
            capacity=25
        )
        
        # Classe d'une autre année
        old_year = AcademicYear.objects.create(
            name="2023-2024",
            start_date=date(2023, 9, 1),
            end_date=date(2024, 7, 31)
        )
        self.old_classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=old_year,
            capacity=30
        )
    
    def test_classroom_manager_exists(self):
        """Test que le ClassRoomManager existe"""
        self.assertTrue(hasattr(ClassRoom.objects, 'for_level'))
        self.assertTrue(hasattr(ClassRoom.objects, 'for_academic_year'))
        self.assertTrue(hasattr(ClassRoom.objects, 'current_year'))
    
    def test_for_level_method(self):
        """Test de la méthode for_level"""
        classrooms = ClassRoom.objects.for_level(self.level)
        self.assertEqual(classrooms.count(), 3)
        self.assertIn(self.classroom1, classrooms)
        self.assertIn(self.classroom2, classrooms)
        self.assertIn(self.old_classroom, classrooms)
    
    def test_for_academic_year_method(self):
        """Test de la méthode for_academic_year"""
        classrooms = ClassRoom.objects.for_academic_year(self.academic_year)
        self.assertEqual(classrooms.count(), 2)
        self.assertIn(self.classroom1, classrooms)
        self.assertIn(self.classroom2, classrooms)
        self.assertNotIn(self.old_classroom, classrooms)
    
    def test_current_year_method(self):
        """Test de la méthode current_year"""
        classrooms = ClassRoom.objects.current_year()
        self.assertEqual(classrooms.count(), 2)
        self.assertIn(self.classroom1, classrooms)
        self.assertIn(self.classroom2, classrooms)
        self.assertNotIn(self.old_classroom, classrooms)


class EnrollmentManagerTest(TestCase):
    """Tests pour le EnrollmentManager"""
    
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
        
        # Créer des étudiants
        self.student1_user = User.objects.create_user(
            email="student1@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Martin",
            role="STUDENT"
        )
        self.student1 = Student.objects.create(
            user=self.student1_user,
            current_class=self.classroom
        )
        
        self.student2_user = User.objects.create_user(
            email="student2@test.com",
            password="testpass123",
            first_name="Pierre",
            last_name="Durand",
            role="STUDENT"
        )
        self.student2 = Student.objects.create(
            user=self.student2_user,
            current_class=self.classroom
        )
        
        # Créer des inscriptions
        self.enrollment1 = Enrollment.objects.create(
            student=self.student1,
            classroom=self.classroom,
            academic_year=self.academic_year,
            is_active=True
        )
        
        self.enrollment2 = Enrollment.objects.create(
            student=self.student2,
            classroom=self.classroom,
            academic_year=self.academic_year,
            is_active=True
        )
        
        # Inscription inactive
        self.inactive_enrollment = Enrollment.objects.create(
            student=self.student1,
            classroom=self.classroom,
            academic_year=self.academic_year,
            is_active=False
        )
    
    def test_enrollment_manager_exists(self):
        """Test que le EnrollmentManager existe"""
        self.assertTrue(hasattr(Enrollment.objects, 'active'))
        self.assertTrue(hasattr(Enrollment.objects, 'for_classroom'))
        self.assertTrue(hasattr(Enrollment.objects, 'for_student'))
    
    def test_active_method(self):
        """Test de la méthode active"""
        active_enrollments = Enrollment.objects.active()
        self.assertEqual(active_enrollments.count(), 2)
        self.assertIn(self.enrollment1, active_enrollments)
        self.assertIn(self.enrollment2, active_enrollments)
        self.assertNotIn(self.inactive_enrollment, active_enrollments)
    
    def test_for_classroom_method(self):
        """Test de la méthode for_classroom"""
        enrollments = Enrollment.objects.for_classroom(self.classroom)
        self.assertEqual(enrollments.count(), 3)
        self.assertIn(self.enrollment1, enrollments)
        self.assertIn(self.enrollment2, enrollments)
        self.assertIn(self.inactive_enrollment, enrollments)
    
    def test_for_student_method(self):
        """Test de la méthode for_student"""
        enrollments = Enrollment.objects.for_student(self.student1)
        self.assertEqual(enrollments.count(), 2)  # 1 active + 1 inactive
        self.assertIn(self.enrollment1, enrollments)
        self.assertIn(self.inactive_enrollment, enrollments)


class AcademicModelMethodsTest(TestCase):
    """Tests pour les méthodes personnalisées des modèles"""
    
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
        self.student = Student.objects.create(
            user=self.student_user,
            current_class=self.classroom
        )
    
    def test_classroom_current_enrollment_property(self):
        """Test de la propriété current_enrollment de ClassRoom"""
        # Classe vide
        self.assertEqual(self.classroom.current_enrollment, 0)
        
        # Ajouter des étudiants
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
    
    def test_classroom_is_full_property(self):
        """Test de la propriété is_full de ClassRoom"""
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
    
    def test_grade_percentage_property(self):
        """Test de la propriété percentage de Grade"""
        grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Test",
            evaluation_type="TEST",
            score=15.0,
            max_score=20,
            date=date.today()
        )
        
        self.assertEqual(grade.percentage, 75.0)  # 15/20 * 100
        
        # Test avec max_score = 0
        grade_zero = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Test Zero",
            evaluation_type="TEST",
            score=10,
            max_score=0,
            date=date.today()
        )
        
        self.assertEqual(grade_zero.percentage, 0)
    
    def test_grade_weighted_score_property(self):
        """Test de la propriété weighted_score de Grade"""
        grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Test",
            evaluation_type="TEST",
            score=15.0,
            max_score=20,
            coefficient=2.5,
            date=date.today()
        )
        
        self.assertEqual(grade.weighted_score, Decimal('37.5'))  # 15 * 2.5
    
    def test_document_file_size_mb_property(self):
        """Test de la propriété file_size_mb de Document"""
        from django.core.files.base import ContentFile
        
        document = Document.objects.create(
            title="Test Document",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"x" * 1024, name="test.txt")  # 1KB
        )
        
        # 1KB = 0.001MB
        self.assertAlmostEqual(document.file_size_mb, 0.001, places=3)
    
    def test_document_is_accessible_property(self):
        """Test de la propriété is_accessible de Document"""
        from django.core.files.base import ContentFile
        
        # Document accessible
        document = Document.objects.create(
            title="Test Document",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="test.txt")
        )
        self.assertTrue(document.is_accessible)
        
        # Document avec date d'accès future
        future_doc = Document.objects.create(
            title="Future Document",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="future.txt"),
            access_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(future_doc.is_accessible)
        
        # Document expiré
        expired_doc = Document.objects.create(
            title="Expired Document",
            subject=self.subject,
            teacher=self.teacher,
            file=ContentFile(b"content", name="expired.txt"),
            expiry_date=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(expired_doc.is_accessible)
    
    def test_document_file_icon_property(self):
        """Test de la propriété file_icon de Document"""
        from django.core.files.base import ContentFile
        
        # Test différents types de fichiers
        test_cases = [
            ("test.pdf", "fas fa-file-pdf text-red-500"),
            ("test.docx", "fas fa-file-word text-blue-500"),
            ("test.xlsx", "fas fa-file-excel text-green-500"),
            ("test.pptx", "fas fa-file-powerpoint text-orange-500"),
            ("test.jpg", "fas fa-file-image text-purple-500"),
            ("test.unknown", "fas fa-file text-gray-400"),
        ]
        
        for filename, expected_icon in test_cases:
            document = Document.objects.create(
                title=f"Test {filename}",
                subject=self.subject,
                teacher=self.teacher,
                file=ContentFile(b"content", name=filename)
            )
            self.assertEqual(document.file_icon, expected_icon)


class AcademicModelValidationTest(TestCase):
    """Tests de validation des modèles académiques"""
    
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
        self.student = Student.objects.create(
            user=self.student_user,
            current_class=self.classroom
        )
    
    def test_timetable_clean_validation(self):
        """Test de la validation clean() de Timetable"""
        from django.core.exceptions import ValidationError
        
        # Heure de début >= heure de fin
        with self.assertRaises(ValidationError):
            timetable = Timetable(
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                weekday=1,
                start_time="09:00",
                end_time="08:00"
            )
            timetable.clean()
        
        # Heure de début = heure de fin
        with self.assertRaises(ValidationError):
            timetable = Timetable(
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                weekday=1,
                start_time="09:00",
                end_time="09:00"
            )
            timetable.clean()
        
        # Heure de début < heure de fin (valide)
        timetable = Timetable(
            classroom=self.classroom,
            subject=self.subject,
            teacher=self.teacher,
            weekday=1,
            start_time="08:00",
            end_time="09:00"
        )
        # Ne doit pas lever d'exception
        timetable.clean()
    
    def test_grade_score_validation(self):
        """Test de la validation du score de Grade"""
        from django.core.exceptions import ValidationError
        
        # Score négatif
        with self.assertRaises(ValidationError):
            grade = Grade(
                student=self.student,
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                evaluation_name="Test",
                evaluation_type="TEST",
                score=-5,
                max_score=20,
                date=date.today()
            )
            grade.full_clean()
        
        # Score valide
        grade = Grade(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            classroom=self.classroom,
            evaluation_name="Test",
            evaluation_type="TEST",
            score=15,
            max_score=20,
            date=date.today()
        )
        # Ne doit pas lever d'exception
        grade.full_clean()
    
    def test_subject_coefficient_validation(self):
        """Test de la validation du coefficient de Subject"""
        from django.core.exceptions import ValidationError
        
        # Coefficient négatif
        with self.assertRaises(ValidationError):
            subject = Subject(
                name="Test Subject",
                code="TEST",
                coefficient=-1
            )
            subject.full_clean()
        
        # Coefficient valide
        subject = Subject(
            name="Test Subject",
            code="TEST",
            coefficient=2.5
        )
        # Ne doit pas lever d'exception
        subject.full_clean()
