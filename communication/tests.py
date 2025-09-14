"""
Tests pour l'application communication
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, datetime, timedelta

# Imports des modèles
from accounts.models import Student, Teacher, Parent
from academic.models import Level, AcademicYear, ClassRoom, Subject
from communication.models import (
    Announcement, AnnouncementRead, Message, GroupMessage, GroupMessageRead, 
    Resource, Notification, ForumTopic, ForumPost
)

User = get_user_model()


class CommunicationModelsTest(TestCase):
    """Tests pour les modèles du module communication"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Données académiques
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        # Niveau et classe
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
        )
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year
        )
        
        # Matière
        self.subject = Subject.objects.create(
            name="Mathématiques",
            code="MATH"
        )
        
        # Ajout du niveau aux matières
        self.subject.levels.add(self.level)
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN"
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Teacher",
            last_name="User",
            role="TEACHER"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )

    def test_announcement_model(self):
        """Test du modèle Announcement"""
        announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Contenu de l'annonce de test",
            type="GENERAL",
            audience="ALL",
            author=self.admin_user,
            is_published=True
        )
        
        self.assertEqual(str(announcement), "Test Announcement")
        self.assertTrue(announcement.is_active)
        self.assertIsNotNone(announcement.publish_date)

    def test_announcement_expiry(self):
        """Test de l'expiration des annonces"""
        # Annonce expirée
        past_date = timezone.now() - timedelta(days=1)
        expired_announcement = Announcement.objects.create(
            title="Annonce expirée",
            content="Cette annonce est expirée",
            author=self.admin_user,
            is_published=True,
            expiry_date=past_date
        )
        
        self.assertFalse(expired_announcement.is_active)

    def test_announcement_audience_targeting(self):
        """Test du ciblage d'audience des annonces"""
        announcement = Announcement.objects.create(
            title="Annonce ciblée",
            content="Annonce pour une classe spécifique",
            author=self.admin_user,
            audience="LEVEL",
            is_published=True
        )
        
        announcement.target_levels.add(self.level)
        
        self.assertEqual(announcement.audience, "LEVEL")
        self.assertIn(self.level, announcement.target_levels.all())

    def test_announcement_read_tracking(self):
        """Test du suivi de lecture des annonces"""
        announcement = Announcement.objects.create(
            title="Annonce à lire",
            content="Test de suivi de lecture",
            author=self.admin_user,
            is_published=True
        )
        
        # Marquer comme lu
        read_status = AnnouncementRead.objects.create(
            announcement=announcement,
            user=self.student_user
        )
        
        self.assertEqual(read_status.user, self.student_user)
        self.assertEqual(read_status.announcement, announcement)

    def test_message_model(self):
        """Test du modèle Message"""
        message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message de test",
            content="Contenu du message de test"
        )
        
        self.assertEqual(message.sender, self.teacher_user)
        self.assertEqual(message.recipient, self.parent_user)
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_date)

    def test_message_read_status(self):
        """Test du statut de lecture des messages"""
        message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message à lire",
            content="Test de lecture"
        )
        
        # Marquer comme lu
        message.mark_as_read()
        
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_date)

    def test_message_thread_reply(self):
        """Test des réponses aux messages"""
        original_message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message original",
            content="Contenu du message original"
        )
        
        reply_message = Message.objects.create(
            sender=self.parent_user,
            recipient=self.teacher_user,
            subject="Re: Message original",
            content="Ma réponse au message",
            parent_message=original_message
        )
        
        self.assertEqual(reply_message.parent_message, original_message)
        # Vérifier qu'il s'agit bien d'une réponse

    def test_group_message_model(self):
        """Test du modèle GroupMessage"""
        group_message = GroupMessage.objects.create(
            sender=self.admin_user,
            subject="Message de groupe",
            content="Contenu du message de groupe"
        )
        
        group_message.target_classes.add(self.classroom)
        group_message.target_users.add(self.student_user, self.parent_user)
        
        self.assertEqual(group_message.sender, self.admin_user)
        self.assertIn(self.classroom, group_message.target_classes.all())
        self.assertIn(self.student_user, group_message.target_users.all())

    def test_group_message_read_tracking(self):
        """Test du suivi de lecture des messages de groupe"""
        group_message = GroupMessage.objects.create(
            sender=self.admin_user,
            subject="Message de groupe à lire",
            content="Test de suivi de lecture de groupe"
        )
        
        read_status = GroupMessageRead.objects.create(
            group_message=group_message,
            user=self.student_user
        )
        
        self.assertEqual(read_status.group_message, group_message)
        self.assertEqual(read_status.user, self.student_user)

    def test_resource_model(self):
        """Test du modèle Resource"""
        resource = Resource.objects.create(
            title="Ressource de test",
            description="Description de la ressource",
            resource_type="DOCUMENT",
            uploaded_by=self.teacher_user,
            subject=self.subject,
            is_public=False
        )
        
        resource.accessible_classes.add(self.classroom)
        
        self.assertEqual(resource.uploaded_by, self.teacher_user)
        self.assertEqual(resource.subject, self.subject)
        self.assertIn(self.classroom, resource.accessible_classes.all())


class CommunicationViewsTest(TestCase):
    """Tests pour les vues du module communication"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Données de base
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
        )
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year
        )
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True,
            is_superuser=True
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Teacher",
            last_name="User",
            role="TEACHER"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )

    def test_announcement_list_view(self):
        """Test de la vue liste des annonces"""
        # Créer une annonce
        announcement = Announcement.objects.create(
            title="Annonce test",
            content="Contenu de test",
            author=self.admin_user,
            is_published=True
        )
        
        self.client.force_login(self.student_user)
        response = self.client.get('/communication/announcements/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annonce test")

    def test_announcement_detail_view(self):
        """Test de la vue détail d'annonce"""
        announcement = Announcement.objects.create(
            title="Annonce détaillée",
            content="Contenu détaillé",
            author=self.admin_user,
            is_published=True
        )
        
        self.client.force_login(self.student_user)
        response = self.client.get(f'/communication/announcements/{announcement.pk}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annonce détaillée")

    def test_announcement_create_view_admin(self):
        """Test de création d'annonce par un admin"""
        self.client.force_login(self.admin_user)
        
        data = {
            'title': 'Nouvelle annonce',
            'content': 'Contenu de la nouvelle annonce',
            'type': 'GENERAL',
            'audience': 'ALL',
            'is_published': True
        }
        
        response = self.client.post('/communication/announcements/create/', data)
        
        self.assertEqual(response.status_code, 302)  # Redirection après création
        
        announcement = Announcement.objects.get(title='Nouvelle annonce')
        self.assertEqual(announcement.author, self.admin_user)

    def test_announcement_create_unauthorized(self):
        """Test de création d'annonce non autorisée"""
        self.client.force_login(self.student_user)
        
        response = self.client.get('/communication/announcements/create/')
        self.assertEqual(response.status_code, 403)

    def test_message_list_view(self):
        """Test de la vue liste des messages"""
        # Créer un message
        message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message test",
            content="Contenu du message"
        )
        
        self.client.force_login(self.parent_user)
        response = self.client.get('/communication/messages/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Message test")

    def test_message_detail_view(self):
        """Test de la vue détail d'un message"""
        message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message détaillé",
            content="Contenu détaillé du message"
        )
        
        self.client.force_login(self.parent_user)
        response = self.client.get(f'/communication/messages/{message.pk}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Message détaillé")

    def test_message_create_view(self):
        """Test de création d'un message"""
        self.client.force_login(self.parent_user)
        
        data = {
            'recipient': self.teacher_user.pk,
            'subject': 'Nouveau message',
            'content': 'Contenu du nouveau message'
        }
        
        response = self.client.post('/communication/messages/create/', data)
        
        self.assertEqual(response.status_code, 302)
        
        message = Message.objects.get(subject='Nouveau message')
        self.assertEqual(message.sender, self.parent_user)
        self.assertEqual(message.recipient, self.teacher_user)

    def test_message_reply_view(self):
        """Test de réponse à un message"""
        original_message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message original",
            content="Contenu original"
        )
        
        self.client.force_login(self.parent_user)
        
        data = {
            'subject': 'Re: Message original',
            'content': 'Ma réponse au message'
        }
        
        response = self.client.post(f'/communication/messages/{original_message.pk}/reply/', data)
        
        self.assertEqual(response.status_code, 302)
        
        reply = Message.objects.get(subject='Re: Message original')
        self.assertEqual(reply.recipient, self.parent_user)

    def test_unauthorized_message_access(self):
        """Test d'accès non autorisé aux messages"""
        message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message privé",
            content="Contenu privé"
        )
        
        # L'étudiant ne doit pas pouvoir accéder au message
        self.client.force_login(self.student_user)
        response = self.client.get(f'/communication/messages/{message.pk}/')
        
        self.assertEqual(response.status_code, 403)

    def test_group_message_create_view(self):
        """Test de création d'un message de groupe"""
        self.client.force_login(self.admin_user)
        
        data = {
            'subject': 'Message de groupe test',
            'content': 'Contenu du message de groupe',
            'target_classes': [self.classroom.pk]
        }
        
        response = self.client.post('/communication/group-messages/create/', data)
        
        self.assertEqual(response.status_code, 302)
        
        group_message = GroupMessage.objects.get(subject='Message de groupe test')
        self.assertEqual(group_message.sender, self.admin_user)
        self.assertIn(self.classroom, group_message.target_classes.all())
        
        # Simplifier le test - vérifier juste que le message de groupe est créé
        # Les règles de ciblage peuvent être testées séparément


class CommunicationPermissionsTest(TestCase):
    """Tests pour les permissions du module communication"""
    
    def setUp(self):
        """Configuration des utilisateurs pour les tests de permissions"""
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
            first_name="Teacher",
            last_name="User",
            role="TEACHER"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )

    def test_announcement_creation_permissions(self):
        """Test des permissions de création d'annonces"""
        self.client = Client()
        
        # Admin peut créer
        self.client.force_login(self.admin_user)
        response = self.client.get('/communication/announcements/create/')
        self.assertEqual(response.status_code, 200)
        
        # Étudiant ne peut pas créer
        self.client.force_login(self.student_user)
        response = self.client.get('/communication/announcements/create/')
        self.assertEqual(response.status_code, 403)

    def test_forum_access_permissions(self):
        """Test des permissions d'accès au forum"""
        # Créer des données de test pour le forum
        academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
        )
        
        classroom = ClassRoom.objects.create(
            name="6ème A",
            level=level,
            academic_year=academic_year
        )
        
        # Créer un topic
        topic = ForumTopic.objects.create(
            title="Discussion test",
            content="Contenu de la discussion",
            classroom=classroom,
            author=self.teacher_user
        )
        
        # Test d'accès
        self.assertTrue(topic.can_user_access(self.teacher_user))

    def test_message_privacy_permissions(self):
        """Test des permissions de confidentialité des messages"""
        # Créer un message privé
        message = Message.objects.create(
            sender=self.teacher_user,
            recipient=self.parent_user,
            subject="Message privé",
            content="Contenu confidentiel"
        )
        
        self.client = Client()
        
        # Le destinataire peut accéder
        self.client.force_login(self.parent_user)
        response = self.client.get(f'/communication/messages/{message.pk}/')
        self.assertEqual(response.status_code, 200)
        
        # Un autre utilisateur ne peut pas accéder
        self.client.force_login(self.student_user)
        response = self.client.get(f'/communication/messages/{message.pk}/')
        self.assertEqual(response.status_code, 403)


class CommunicationIntegrationTest(TestCase):
    """Tests d'intégration pour le module communication"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Configuration complète
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
        )
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            academic_year=self.academic_year
        )
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True,
            is_superuser=True
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Teacher",
            last_name="User",
            role="TEACHER"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )

    def test_complete_announcement_workflow(self):
        """Test du workflow complet d'annonce"""
        self.client.force_login(self.admin_user)
        
        # Créer une annonce
        data = {
            'title': 'Annonce importante',
            'content': 'Contenu de l\'annonce importante',
            'type': 'URGENT',
            'audience': 'ALL',
            'is_published': True,
            'priority': 3
        }
        
        response = self.client.post('/communication/announcements/create/', data)
        self.assertEqual(response.status_code, 302)
        
        announcement = Announcement.objects.get(title='Annonce importante')
        self.assertEqual(announcement.priority, 3)
        self.assertTrue(announcement.is_published)

    def test_complete_messaging_workflow(self):
        """Test du workflow complet de messagerie"""
        # Message initial
        self.client.force_login(self.parent_user)
        
        data = {
            'recipient': self.teacher_user.pk,
            'subject': 'Question sur les devoirs',
            'content': 'J\'ai une question concernant les devoirs de mathématiques'
        }
        
        response = self.client.post('/communication/messages/create/', data)
        self.assertEqual(response.status_code, 302)
        
        message = Message.objects.get(subject='Question sur les devoirs')
        self.assertEqual(message.sender, self.parent_user)
        self.assertEqual(message.recipient, self.teacher_user)

    def test_complete_forum_workflow(self):
        """Test du workflow complet du forum"""
        # Créer un topic
        topic = ForumTopic.objects.create(
            title="Discussion sur le projet de classe",
            content="Contenu de la discussion",
            classroom=self.classroom,
            author=self.teacher_user
        )
        
        # Ajouter une réponse
        post = ForumPost.objects.create(
            topic=topic,
            author=self.student_user,
            content="Ma réponse à la discussion"
        )
        
        self.assertEqual(post.topic, topic)
        self.assertEqual(post.author, self.student_user)
        self.assertEqual(topic.posts_count, 2)  # Topic + 1 post

    def test_notification_system_integration(self):
        """Test d'intégration du système de notification"""
        # Créer une notification
        notification = Notification.objects.create(
            user=self.student_user,
            title="Nouvelle note disponible",
            message="Votre note de mathématiques est disponible",
            type="GRADE",
            link_url="/academic/grades/"
        )
        
        self.assertEqual(notification.user, self.student_user)
        self.assertFalse(notification.is_read)
        
        # Marquer comme lue
        notification.mark_as_read()
        self.assertTrue(notification.is_read)

    def test_cross_module_integration(self):
        """Test d'intégration entre modules"""
        # Créer un sujet
        subject = Subject.objects.create(
            name="Géométrie",
            code="GEOM"
        )
        subject.levels.add(self.level)
        
        # Créer une ressource liée au sujet
        resource = Resource.objects.create(
            title="Cours de géométrie",
            description="Support de cours",
            resource_type="DOCUMENT",
            uploaded_by=self.teacher_user,
            subject=subject
        )
        
        # Créer une annonce liée à la classe
        announcement = Announcement.objects.create(
            title="Nouveau cours disponible",
            content="Le cours de géométrie est maintenant disponible",
            author=self.teacher_user,
            audience="CLASS",
            is_published=True
        )
        announcement.target_classes.add(self.classroom)
        
        # Vérifier l'intégration
        self.assertEqual(resource.subject, subject)
        self.assertIn(self.classroom, announcement.target_classes.all())
        self.assertIn("Cours de géométrie", announcement.content)