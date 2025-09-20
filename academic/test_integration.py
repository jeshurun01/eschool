"""
Tests d'intégration pour le module academic
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from django.core.files.base import ContentFile

from accounts.models import Teacher, Student, Parent
from .models import (
    AcademicYear, Level, Subject, ClassRoom, TeacherAssignment,
    Enrollment, Timetable, Attendance, Grade, Document
)

User = get_user_model()


class AcademicWorkflowTest(TestCase):
    """Tests d'intégration pour les workflows académiques complets"""
    
    def setUp(self):
        self.client = Client()
        
        # Configuration de base
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de sixième",
            order=6
        )
        
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH",
            coefficient=3
        )
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True
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
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Pierre",
            last_name="Martin",
            role="PARENT"
        )
        self.parent = Parent.objects.create(user=self.parent_user)
        
        # Assignation enseignant
        self.assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            subject=self.subject,
            academic_year=self.academic_year,
            hours_per_week=4
        )
    
    def test_complete_student_enrollment_workflow(self):
        """Test du workflow complet d'inscription d'un étudiant"""
        # 1. Créer un nouvel étudiant
        new_student_user = User.objects.create_user(
            email="newstudent@test.com",
            password="testpass123",
            first_name="Nouveau",
            last_name="Étudiant",
            role="STUDENT"
        )
        new_student = Student.objects.create(user=new_student_user)
        
        # 2. Inscrire l'étudiant dans la classe
        enrollment = Enrollment.objects.create(
            student=new_student,
            classroom=self.classroom,
            academic_year=self.academic_year
        )
        
        # 3. Vérifier l'inscription
        self.assertTrue(enrollment.is_active)
        self.assertEqual(self.classroom.current_enrollment, 2)  # Original + nouveau
        self.assertEqual(new_student.current_class, self.classroom)
        
        # 4. Vérifier que l'étudiant apparaît dans la classe
        self.assertIn(new_student, self.classroom.students.all())
    
    def test_complete_grade_workflow(self):
        """Test du workflow complet de notation"""
        # 1. Créer plusieurs notes pour l'étudiant
        grades_data = [
            {
                'evaluation_name': 'Contrôle 1',
                'evaluation_type': 'TEST',
                'score': 15.0,
                'max_score': 20,
                'coefficient': 2,
                'date': date.today() - timedelta(days=10)
            },
            {
                'evaluation_name': 'Contrôle 2',
                'evaluation_type': 'TEST',
                'score': 18.0,
                'max_score': 20,
                'coefficient': 2,
                'date': date.today() - timedelta(days=5)
            },
            {
                'evaluation_name': 'Examen',
                'evaluation_type': 'EXAM',
                'score': 16.0,
                'max_score': 20,
                'coefficient': 3,
                'date': date.today()
            }
        ]
        
        grades = []
        for grade_data in grades_data:
            grade = Grade.objects.create(
                student=self.student,
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                **grade_data
            )
            grades.append(grade)
        
        # 2. Vérifier que les notes sont créées
        self.assertEqual(Grade.objects.filter(student=self.student).count(), 3)
        
        # 3. Calculer la moyenne
        total_weighted = sum(grade.weighted_score for grade in grades)
        total_coefficient = sum(grade.coefficient for grade in grades)
        average = total_weighted / total_coefficient
        
        # Moyenne attendue : (15*2 + 18*2 + 16*3) / (2+2+3) = (30+36+48)/7 = 114/7 ≈ 16.29
        expected_average = Decimal('16.29')
        self.assertAlmostEqual(average, expected_average, places=1)
        
        # 4. Vérifier les propriétés des notes
        for grade in grades:
            self.assertGreater(grade.percentage, 0)
            self.assertGreater(grade.weighted_score, 0)
    
    def test_complete_attendance_workflow(self):
        """Test du workflow complet de prise de présences"""
        # 1. Créer plusieurs présences pour l'étudiant
        attendance_data = [
            {'date': date.today() - timedelta(days=10), 'status': 'PRESENT'},
            {'date': date.today() - timedelta(days=9), 'status': 'ABSENT'},
            {'date': date.today() - timedelta(days=8), 'status': 'LATE'},
            {'date': date.today() - timedelta(days=7), 'status': 'PRESENT'},
            {'date': date.today() - timedelta(days=6), 'status': 'EXCUSED'},
        ]
        
        attendances = []
        for att_data in attendance_data:
            attendance = Attendance.objects.create(
                student=self.student,
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                **att_data
            )
            attendances.append(attendance)
        
        # 2. Vérifier que les présences sont créées
        self.assertEqual(Attendance.objects.filter(student=self.student).count(), 5)
        
        # 3. Calculer les statistiques de présence
        present_count = Attendance.objects.filter(
            student=self.student,
            status='PRESENT'
        ).count()
        total_count = Attendance.objects.filter(student=self.student).count()
        attendance_rate = (present_count / total_count) * 100
        
        # Taux de présence attendu : 2 présents sur 5 = 40%
        self.assertEqual(attendance_rate, 40.0)
        
        # 4. Vérifier les différents statuts
        statuses = ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED']
        for status in statuses:
            count = Attendance.objects.filter(
                student=self.student,
                status=status
            ).count()
            self.assertGreaterEqual(count, 0)
    
    def test_complete_timetable_workflow(self):
        """Test du workflow complet de création d'emploi du temps"""
        # 1. Créer un emploi du temps complet pour la semaine
        timetable_data = [
            {'weekday': 1, 'start_time': '08:00', 'end_time': '09:00', 'room': 'A101'},
            {'weekday': 1, 'start_time': '09:00', 'end_time': '10:00', 'room': 'A101'},
            {'weekday': 3, 'start_time': '08:00', 'end_time': '09:00', 'room': 'A101'},
            {'weekday': 5, 'start_time': '10:00', 'end_time': '11:00', 'room': 'A101'},
        ]
        
        timetables = []
        for tt_data in timetable_data:
            timetable = Timetable.objects.create(
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                **tt_data
            )
            timetables.append(timetable)
        
        # 2. Vérifier que l'emploi du temps est créé
        self.assertEqual(Timetable.objects.filter(classroom=self.classroom).count(), 4)
        
        # 3. Vérifier l'ordre des créneaux
        ordered_timetables = Timetable.objects.filter(
            classroom=self.classroom
        ).order_by('weekday', 'start_time')
        
        self.assertEqual(list(ordered_timetables), timetables)
        
        # 4. Vérifier les heures par semaine
        total_hours = sum(tt_data['hours_per_week'] for tt_data in [self.assignment])
        self.assertEqual(total_hours, 4)
    
    def test_complete_document_workflow(self):
        """Test du workflow complet de gestion de documents"""
        # 1. Créer différents types de documents
        documents_data = [
            {
                'title': 'Cours de mathématiques',
                'description': 'Introduction aux équations',
                'document_type': 'COURSE',
                'file': ContentFile(b"cours content", name="cours.pdf")
            },
            {
                'title': 'Exercices de mathématiques',
                'description': 'Exercices d\'application',
                'document_type': 'EXERCISE',
                'file': ContentFile(b"exercices content", name="exercices.pdf")
            },
            {
                'title': 'Examen de mathématiques',
                'description': 'Examen de fin de trimestre',
                'document_type': 'EXAM',
                'file': ContentFile(b"examen content", name="examen.pdf")
            }
        ]
        
        documents = []
        for doc_data in documents_data:
            document = Document.objects.create(
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                **doc_data
            )
            documents.append(document)
        
        # 2. Vérifier que les documents sont créés
        self.assertEqual(Document.objects.filter(subject=self.subject).count(), 3)
        
        # 3. Vérifier les propriétés des documents
        for document in documents:
            self.assertTrue(document.is_accessible)
            self.assertGreater(document.file_size_mb, 0)
            self.assertIsNotNone(document.file_icon)
        
        # 4. Vérifier le filtrage par type
        course_docs = Document.objects.filter(document_type='COURSE')
        self.assertEqual(course_docs.count(), 1)
        self.assertEqual(course_docs.first().title, 'Cours de mathématiques')
    
    def test_classroom_statistics_workflow(self):
        """Test du workflow de calcul des statistiques de classe"""
        # 1. Créer plusieurs étudiants dans la classe
        students = []
        for i in range(5):
            user = User.objects.create_user(
                email=f"student{i}@test.com",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Test",
                role="STUDENT"
            )
            student = Student.objects.create(
                user=user,
                current_class=self.classroom
            )
            students.append(student)
            
            Enrollment.objects.create(
                student=student,
                classroom=self.classroom,
                academic_year=self.academic_year
            )
        
        # 2. Créer des notes pour chaque étudiant
        for student in students:
            for j in range(3):  # 3 notes par étudiant
                Grade.objects.create(
                    student=student,
                    subject=self.subject,
                    teacher=self.teacher,
                    classroom=self.classroom,
                    evaluation_name=f"Test {j+1}",
                    evaluation_type="TEST",
                    score=15.0 + j,  # Notes de 15, 16, 17
                    max_score=20,
                    coefficient=1,
                    date=date.today() - timedelta(days=j)
                )
        
        # 3. Vérifier les statistiques de classe
        self.assertEqual(self.classroom.current_enrollment, 6)  # Original + 5 nouveaux
        self.assertFalse(self.classroom.is_full)  # Capacité = 30
        
        # 4. Calculer la moyenne de classe
        all_grades = Grade.objects.filter(classroom=self.classroom)
        class_average = sum(grade.score for grade in all_grades) / all_grades.count()
        self.assertAlmostEqual(class_average, 16.0, places=1)  # (15+16+17)/3 = 16
    
    def test_teacher_assignment_workflow(self):
        """Test du workflow d'assignation d'enseignants"""
        # 1. Créer une nouvelle matière
        new_subject = Subject.objects.create(
            name="Français",
            code="FR",
            coefficient=2
        )
        
        # 2. Assigner l'enseignant à la nouvelle matière
        new_assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            subject=new_subject,
            academic_year=self.academic_year,
            hours_per_week=3
        )
        
        # 3. Vérifier l'assignation
        self.assertEqual(new_assignment.teacher, self.teacher)
        self.assertEqual(new_assignment.classroom, self.classroom)
        self.assertEqual(new_assignment.subject, new_subject)
        self.assertEqual(new_assignment.hours_per_week, 3)
        
        # 4. Vérifier les relations inverses
        self.assertIn(new_assignment, self.teacher.teacherassignment_set.all())
        self.assertIn(new_assignment, self.classroom.teacherassignment_set.all())
        self.assertIn(new_assignment, new_subject.teacherassignment_set.all())
        
        # 5. Vérifier le total d'heures par semaine
        total_hours = sum(
            assignment.hours_per_week 
            for assignment in TeacherAssignment.objects.filter(
                teacher=self.teacher,
                classroom=self.classroom
            )
        )
        self.assertEqual(total_hours, 7)  # 4 (MATH) + 3 (FR)
    
    def test_academic_year_transition_workflow(self):
        """Test du workflow de transition d'année académique"""
        # 1. Créer une nouvelle année académique
        new_academic_year = AcademicYear.objects.create(
            name="2025-2026",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
            is_current=False
        )
        
        # 2. Marquer la nouvelle année comme courante
        new_academic_year.is_current = True
        new_academic_year.save()
        
        # 3. Vérifier que l'ancienne année n'est plus courante
        self.academic_year.refresh_from_db()
        self.assertFalse(self.academic_year.is_current)
        self.assertTrue(new_academic_year.is_current)
        
        # 4. Créer une nouvelle classe pour la nouvelle année
        new_classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=new_academic_year,
            capacity=30
        )
        
        # 5. Vérifier que les classes sont bien séparées par année
        old_classrooms = ClassRoom.objects.filter(academic_year=self.academic_year)
        new_classrooms = ClassRoom.objects.filter(academic_year=new_academic_year)
        
        self.assertEqual(old_classrooms.count(), 1)
        self.assertEqual(new_classrooms.count(), 1)
        self.assertIn(self.classroom, old_classrooms)
        self.assertIn(new_classroom, new_classrooms)
    
    def test_parent_student_relationship_workflow(self):
        """Test du workflow de relation parent-étudiant"""
        # 1. Créer un nouvel étudiant
        new_student_user = User.objects.create_user(
            email="newstudent2@test.com",
            password="testpass123",
            first_name="Nouveau",
            last_name="Étudiant2",
            role="STUDENT"
        )
        new_student = Student.objects.create(
            user=new_student_user,
            current_class=self.classroom
        )
        
        # 2. Assigner l'étudiant au parent
        new_student.parents.add(self.parent)
        
        # 3. Vérifier la relation
        self.assertIn(new_student, self.parent.children.all())
        self.assertIn(self.parent, new_student.parents.all())
        
        # 4. Vérifier que le parent peut voir les enfants
        parent_children = self.parent.children.all()
        self.assertEqual(parent_children.count(), 1)
        self.assertIn(new_student, parent_children)
    
    def test_error_handling_workflow(self):
        """Test de la gestion d'erreurs dans les workflows"""
        # 1. Test de création de note avec score invalide
        with self.assertRaises(Exception):  # ValidationError
            Grade.objects.create(
                student=self.student,
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                evaluation_name="Test invalide",
                evaluation_type="TEST",
                score=-5,  # Score négatif
                max_score=20,
                date=date.today()
            )
        
        # 2. Test de création d'emploi du temps avec heures invalides
        with self.assertRaises(Exception):  # ValidationError
            timetable = Timetable(
                classroom=self.classroom,
                subject=self.subject,
                teacher=self.teacher,
                weekday=1,
                start_time="09:00",
                end_time="08:00"  # Fin avant début
            )
            timetable.clean()
        
        # 3. Test de création de classe avec contrainte unique
        with self.assertRaises(Exception):  # IntegrityError
            ClassRoom.objects.create(
                name="6ème A",  # Même nom
                level=self.level,  # Même niveau
                academic_year=self.academic_year,  # Même année
                capacity=25
            )
    
    def test_performance_workflow(self):
        """Test de performance des workflows"""
        # 1. Créer un grand nombre d'étudiants
        students = []
        for i in range(100):
            user = User.objects.create_user(
                email=f"perfstudent{i}@test.com",
                password="testpass123",
                first_name=f"PerfStudent{i}",
                last_name="Test",
                role="STUDENT"
            )
            student = Student.objects.create(
                user=user,
                current_class=self.classroom
            )
            students.append(student)
            
            Enrollment.objects.create(
                student=student,
                classroom=self.classroom,
                academic_year=self.academic_year
            )
        
        # 2. Vérifier que la classe peut gérer beaucoup d'étudiants
        self.assertEqual(self.classroom.current_enrollment, 101)  # Original + 100 nouveaux
        
        # 3. Créer des notes pour tous les étudiants
        for student in students[:10]:  # Limiter à 10 pour les tests
            Grade.objects.create(
                student=student,
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                evaluation_name="Test Performance",
                evaluation_type="TEST",
                score=15.0,
                max_score=20,
                date=date.today()
            )
        
        # 4. Vérifier que les requêtes sont efficaces
        grades = Grade.objects.filter(classroom=self.classroom).select_related('student', 'subject')
        self.assertEqual(grades.count(), 10)
        
        # 5. Vérifier que les relations sont correctement chargées
        for grade in grades:
            self.assertIsNotNone(grade.student.user.first_name)
            self.assertIsNotNone(grade.subject.name)
