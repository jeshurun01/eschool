from django.test import TestCase, Client
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages
from datetime import date, timedelta

from .models import Teacher, Student, Parent
from academic.models import AcademicYear, Grade, ClassRoom, Subject, Enrollment, Level

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests pour le modèle User personnalisé"""
    
    def test_create_user(self):
        """Test de création d'un utilisateur standard"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            role="STUDENT"
        )
        
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "STUDENT")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test de création d'un superutilisateur"""
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User"
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, "SUPER_ADMIN")

    def test_user_str_method(self):
        """Test de la méthode __str__ du modèle User"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            role="STUDENT"
        )
        
        self.assertEqual(str(user), "John Doe (test@example.com)")

    def test_user_roles(self):
        """Test des différents rôles utilisateur"""
        roles = ["ADMIN", "TEACHER", "STUDENT", "PARENT"]
        
        for role in roles:
            user = User.objects.create_user(
                email=f"{role.lower()}@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User",
                role=role
            )
            self.assertEqual(user.role, role)

    def test_email_uniqueness(self):
        """Test de l'unicité de l'email"""
        User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            role="STUDENT"
        )
        
        # Tentative de création avec le même email
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                first_name="Jane",
                last_name="Smith",
                role="PARENT"
            )

    def test_full_name_property(self):
        """Test de la propriété full_name"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            role="STUDENT"
        )
        
        self.assertEqual(user.full_name, "John Doe")
        self.assertEqual(user.get_full_name(), "John Doe")

    def test_is_admin_property(self):
        """Test de la propriété is_admin"""
        admin_user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN"
        )
        
        student_user = User.objects.create_user(
            email="student@example.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.assertTrue(admin_user.is_admin)
        self.assertFalse(student_user.is_admin)


class TeacherModelTest(TestCase):
    """Tests pour le modèle Teacher"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="teacher@example.com",
            password="testpass123",
            first_name="Marie",
            last_name="Dubois",
            role="TEACHER"
        )

    def test_create_teacher(self):
        """Test de création d'un enseignant"""
        teacher = Teacher.objects.create(
            user=self.user,
            employee_id="TEA20250001",
            hire_date=date.today(),
            salary=50000.00
        )
        
        self.assertEqual(teacher.user, self.user)
        self.assertEqual(teacher.employee_id, "TEA20250001")
        self.assertEqual(str(teacher), "Marie Dubois (TEA20250001)")

    def test_teacher_auto_employee_id(self):
        """Test de génération automatique de l'ID employé"""
        teacher = Teacher.objects.create(
            user=self.user,
            hire_date=date.today()
        )
        
        # L'ID employé devrait être généré automatiquement
        self.assertTrue(teacher.employee_id.startswith("TEA2025"))
        self.assertEqual(len(teacher.employee_id), 11)  # TEA + 4 chiffres année + 4 chiffres numéro

    def test_teacher_unique_employee_id(self):
        """Test de l'unicité de l'ID employé"""
        Teacher.objects.create(
            user=self.user,
            employee_id="TEA20250001"
        )
        
        # Créer un autre utilisateur
        user2 = User.objects.create_user(
            email="teacher2@example.com",
            password="testpass123",
            first_name="Paul",
            last_name="Martin",
            role="TEACHER"
        )
        
        # Tentative de création avec le même employee_id
        with self.assertRaises(Exception):
            Teacher.objects.create(
                user=user2,
                employee_id="TEA20250001"
            )


class StudentModelTest(TestCase):
    """Tests pour le modèle Student"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="testpass123",
            first_name="Alexandre",
            last_name="Girard",
            role="STUDENT",
            date_of_birth=date(2010, 5, 15)
        )

    def test_create_student(self):
        """Test de création d'un étudiant"""
        student = Student.objects.create(
            user=self.user,
            matricule="STU20250001",
            enrollment_date=date.today()
        )
        
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.matricule, "STU20250001")
        self.assertEqual(str(student), "Alexandre Girard (STU20250001)")

    def test_student_auto_matricule(self):
        """Test de génération automatique du matricule"""
        student = Student.objects.create(
            user=self.user,
            enrollment_date=date.today()
        )
        
        # Le matricule devrait être généré automatiquement
        self.assertTrue(student.matricule.startswith("STU2025"))
        self.assertEqual(len(student.matricule), 11)  # STU + 4 chiffres année + 4 chiffres numéro

    def test_student_unique_matricule(self):
        """Test de l'unicité du matricule"""
        Student.objects.create(
            user=self.user,
            matricule="STU20250001"
        )
        
        user2 = User.objects.create_user(
            email="student2@example.com",
            password="testpass123",
            first_name="Sophie",
            last_name="Durand",
            role="STUDENT"
        )
        
        with self.assertRaises(Exception):
            Student.objects.create(
                user=user2,
                matricule="STU20250001"
            )


class ParentModelTest(TestCase):
    """Tests pour le modèle Parent"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="parent@example.com",
            password="testpass123",
            first_name="Brigitte",
            last_name="Andre",
            role="PARENT"
        )

    def test_create_parent(self):
        """Test de création d'un parent"""
        parent = Parent.objects.create(
            user=self.user,
            profession="Ingénieur",
            workplace="TechCorp",
            relationship="FATHER"
        )
        
        self.assertEqual(parent.user, self.user)
        self.assertEqual(parent.profession, "Ingénieur")
        self.assertEqual(parent.relationship, "FATHER")
        self.assertEqual(str(parent), "Brigitte Andre (Père)")

    def test_parent_children_relationship(self):
        """Test de la relation parent-enfants"""
        parent = Parent.objects.create(
            user=self.user,
            profession="Ingénieur"
        )
        
        # Créer des étudiants enfants
        student_user1 = User.objects.create_user(
            email="child1@example.com",
            password="testpass123",
            first_name="Pierre",
            last_name="Andre",
            role="STUDENT"
        )
        
        student1 = Student.objects.create(
            user=student_user1,
            matricule="STU20250001"
        )
        
        student_user2 = User.objects.create_user(
            email="child2@example.com",
            password="testpass123",
            first_name="Marie",
            last_name="Andre",
            role="STUDENT"
        )
        
        student2 = Student.objects.create(
            user=student_user2,
            matricule="STU20250002"
        )
        
        # Ajouter les enfants au parent
        student1.parents.add(parent)
        student2.parents.add(parent)
        
        self.assertEqual(parent.children.count(), 2)
        self.assertIn(student1, parent.children.all())
        self.assertIn(student2, parent.children.all())


class AuthenticationTest(TestCase):
    """Tests pour l'authentification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role="STUDENT"
        )

    def test_user_login(self):
        """Test de connexion utilisateur"""
        user = authenticate(username="test@example.com", password="testpass123")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_invalid_login(self):
        """Test de connexion avec mauvais mot de passe"""
        user = authenticate(username="test@example.com", password="wrongpassword")
        self.assertIsNone(user)

    def test_login_view(self):
        """Test de la vue de connexion"""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirect(self):
        """Test de redirection après connexion"""
        response = self.client.post(reverse('account_login'), {
            'login': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Devrait rediriger
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """Test de déconnexion"""
        self.client.force_login(self.user)
        response = self.client.post(reverse('account_logout'))
        
        # Devrait rediriger
        self.assertEqual(response.status_code, 302)


class DashboardViewsTest(TestCase):
    """Tests pour les vues de tableau de bord"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer les données de base
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
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year,
            capacity=30
        )
        
        # Créer les utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True,
            is_superuser=True
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@example.com",
            password="testpass123",
            first_name="Teacher",
            last_name="User",
            role="TEACHER"
        )
        
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@example.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )
        
        # Créer les profils
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id="TEA20250001"
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            matricule="STU20250001"
        )
        
        self.parent = Parent.objects.create(
            user=self.parent_user,
            profession="Ingénieur"
        )
        
        # Créer l'inscription
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
            academic_year=self.academic_year,
            enrollment_date=date.today()
        )

    def test_admin_dashboard(self):
        """Test du tableau de bord administrateur"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('accounts:admin_dashboard'))
        
        self.assertEqual(response.status_code, 200)

    def test_teacher_dashboard(self):
        """Test du tableau de bord enseignant"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('accounts:teacher_dashboard'))
        
        self.assertEqual(response.status_code, 200)

    def test_student_dashboard(self):
        """Test du tableau de bord étudiant"""
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('accounts:student_dashboard'))
        
        self.assertEqual(response.status_code, 200)

    def test_parent_dashboard(self):
        """Test du tableau de bord parent"""
        # Associer l'enfant au parent
        self.student.parents.add(self.parent)
        
        self.client.force_login(self.parent_user)
        response = self.client.get(reverse('accounts:parent_dashboard'))
        
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirect_unauthenticated(self):
        """Test de redirection pour utilisateur non authentifié"""
        response = self.client.get(reverse('accounts:admin_dashboard'))
        
        # Devrait rediriger vers la page de login
        self.assertEqual(response.status_code, 302)


class RBACTest(TestCase):
    """Tests pour le contrôle d'accès basé sur les rôles (RBAC)"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer des utilisateurs avec différents rôles
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True,
            is_superuser=True
        )
        
        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            password="testpass123",
            first_name="Teacher",
            last_name="User",
            role="TEACHER"
        )
        
        self.student = User.objects.create_user(
            email="student@example.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent = User.objects.create_user(
            email="parent@example.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )

    def test_admin_access_all_views(self):
        """Test que l'admin peut accéder à toutes les vues"""
        self.client.force_login(self.admin)
        
        urls_to_test = [
            reverse('accounts:admin_dashboard'),
            reverse('accounts:parent_list'),
        ]
        
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])  # 200 OK ou 302 redirection

    def test_role_based_dashboard_access(self):
        """Test de l'accès aux dashboards selon le rôle"""
        role_dashboard_mapping = [
            (self.admin, 'accounts:admin_dashboard'),
            (self.teacher, 'accounts:teacher_dashboard'),
            (self.student, 'accounts:student_dashboard'),
            (self.parent, 'accounts:parent_dashboard'),
        ]
        
        for user, dashboard_name in role_dashboard_mapping:
            self.client.force_login(user)
            response = self.client.get(reverse(dashboard_name))
            
            # Devrait pouvoir accéder à son propre dashboard
            self.assertIn(response.status_code, [200, 302])

    def test_cross_role_dashboard_access_denied(self):
        """Test que les utilisateurs ne peuvent pas accéder aux dashboards d'autres rôles"""
        # Un étudiant ne devrait pas pouvoir accéder au dashboard admin
        self.client.force_login(self.student)
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 403)
        
        # Un parent ne devrait pas pouvoir accéder au dashboard enseignant
        self.client.force_login(self.parent)
        response = self.client.get(reverse('accounts:teacher_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_student_limited_access(self):
        """Test que les étudiants ont un accès limité"""
        self.client.force_login(self.student)
        
        # Ne devrait pas pouvoir accéder à la gestion des parents
        response = self.client.get(reverse('accounts:parent_list'))
        self.assertEqual(response.status_code, 403)

    def test_parent_limited_access(self):
        """Test que les parents ont un accès limité"""
        self.client.force_login(self.parent)
        
        # Ne devrait pas pouvoir accéder à la gestion des parents
        response = self.client.get(reverse('accounts:parent_list'))
        self.assertEqual(response.status_code, 403)
        
        # Ne devrait pas pouvoir accéder aux vues administratives
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 403)
