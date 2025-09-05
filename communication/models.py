from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Announcement(models.Model):
    """Annonce publique ou privée"""
    TYPE_CHOICES = [
        ('GENERAL', 'Générale'),
        ('ACADEMIC', 'Académique'),
        ('EVENT', 'Événement'),
        ('URGENT', 'Urgent'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    AUDIENCE_CHOICES = [
        ('ALL', 'Tous'),
        ('STUDENTS', 'Élèves'),
        ('PARENTS', 'Parents'),
        ('TEACHERS', 'Enseignants'),
        ('STAFF', 'Personnel'),
        ('CLASS', 'Classe spécifique'),
        ('LEVEL', 'Niveau spécifique'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre')
    content = models.TextField(verbose_name='Contenu')
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='GENERAL', verbose_name='Type')
    audience = models.CharField(max_length=15, choices=AUDIENCE_CHOICES, default='ALL', verbose_name='Public cible')
    
    # Ciblage spécifique
    target_classes = models.ManyToManyField('academic.ClassRoom', blank=True, verbose_name='Classes ciblées')
    target_levels = models.ManyToManyField('academic.Level', blank=True, verbose_name='Niveaux ciblés')
    
    # Publication
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements', verbose_name='Auteur')
    is_published = models.BooleanField(default=False, verbose_name='Publié')
    publish_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de publication')
    expiry_date = models.DateTimeField(blank=True, null=True, verbose_name='Date d\'expiration')
    
    # Priorité et affichage
    is_pinned = models.BooleanField(default=False, verbose_name='Épinglé')
    priority = models.IntegerField(default=1, choices=[(1, 'Normale'), (2, 'Élevée'), (3, 'Urgente')], verbose_name='Priorité')
    
    # Notifications
    send_email = models.BooleanField(default=False, verbose_name='Envoyer par e-mail')
    send_sms = models.BooleanField(default=False, verbose_name='Envoyer par SMS')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'
        ordering = ['-is_pinned', '-priority', '-publish_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published and not self.publish_date:
            self.publish_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Vérifie si l'annonce est encore active"""
        now = timezone.now()
        if not self.is_published:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return True


class AnnouncementRead(models.Model):
    """Suivi de lecture des annonces"""
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='read_status', verbose_name='Annonce')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    read_date = models.DateTimeField(default=timezone.now, verbose_name='Date de lecture')

    class Meta:
        verbose_name = 'Lecture d\'annonce'
        verbose_name_plural = 'Lectures d\'annonces'
        unique_together = ['announcement', 'user']

    def __str__(self):
        return f"{self.user.full_name} a lu {self.announcement.title}"


class Message(models.Model):
    """Message privé entre utilisateurs"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Expéditeur')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='Destinataire')
    
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    content = models.TextField(verbose_name='Contenu')
    
    # Statut
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    read_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de lecture')
    
    # Suppression
    deleted_by_sender = models.BooleanField(default=False, verbose_name='Supprimé par l\'expéditeur')
    deleted_by_recipient = models.BooleanField(default=False, verbose_name='Supprimé par le destinataire')
    
    # Réponse
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name='Message parent')
    
    sent_date = models.DateTimeField(default=timezone.now, verbose_name='Date d\'envoi')

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_date']

    def __str__(self):
        return f"De {self.sender.full_name} à {self.recipient.full_name}: {self.subject}"

    def mark_as_read(self):
        """Marquer le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_date = timezone.now()
            self.save()


class GroupMessage(models.Model):
    """Message de groupe (classe, niveau, etc.)"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_messages', verbose_name='Expéditeur')
    
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    content = models.TextField(verbose_name='Contenu')
    
    # Destinataires
    target_classes = models.ManyToManyField('academic.ClassRoom', blank=True, verbose_name='Classes destinataires')
    target_levels = models.ManyToManyField('academic.Level', blank=True, verbose_name='Niveaux destinataires')
    target_users = models.ManyToManyField(User, blank=True, related_name='received_group_messages', verbose_name='Utilisateurs destinataires')
    
    sent_date = models.DateTimeField(default=timezone.now, verbose_name='Date d\'envoi')

    class Meta:
        verbose_name = 'Message de groupe'
        verbose_name_plural = 'Messages de groupe'
        ordering = ['-sent_date']

    def __str__(self):
        return f"Message de groupe de {self.sender.full_name}: {self.subject}"


class GroupMessageRead(models.Model):
    """Suivi de lecture des messages de groupe"""
    group_message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name='read_status', verbose_name='Message de groupe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    read_date = models.DateTimeField(default=timezone.now, verbose_name='Date de lecture')

    class Meta:
        verbose_name = 'Lecture de message de groupe'
        verbose_name_plural = 'Lectures de messages de groupe'
        unique_together = ['group_message', 'user']

    def __str__(self):
        return f"{self.user.full_name} a lu le message de groupe"


class Resource(models.Model):
    """Ressource pédagogique partagée"""
    RESOURCE_TYPE_CHOICES = [
        ('DOCUMENT', 'Document'),
        ('VIDEO', 'Vidéo'),
        ('AUDIO', 'Audio'),
        ('IMAGE', 'Image'),
        ('LINK', 'Lien'),
        ('OTHER', 'Autre'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(blank=True, verbose_name='Description')
    resource_type = models.CharField(max_length=15, choices=RESOURCE_TYPE_CHOICES, verbose_name='Type de ressource')
    
    # Fichier ou lien
    file = models.FileField(upload_to='resources/', blank=True, null=True, verbose_name='Fichier')
    url = models.URLField(blank=True, verbose_name='URL')
    
    # Partage
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources', verbose_name='Téléchargé par')
    subject = models.ForeignKey('academic.Subject', on_delete=models.CASCADE, blank=True, null=True, related_name='resources', verbose_name='Matière')
    
    # Accès
    is_public = models.BooleanField(default=False, verbose_name='Public')
    accessible_classes = models.ManyToManyField('academic.ClassRoom', blank=True, verbose_name='Classes autorisées')
    accessible_levels = models.ManyToManyField('academic.Level', blank=True, verbose_name='Niveaux autorisés')
    
    # Métadonnées
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name='Taille du fichier')
    download_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de téléchargements')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ressource'
        verbose_name_plural = 'Ressources'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_download_count(self):
        """Incrémenter le compteur de téléchargements"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class ResourceAccess(models.Model):
    """Suivi d'accès aux ressources"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='access_logs', verbose_name='Ressource')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    access_date = models.DateTimeField(default=timezone.now, verbose_name='Date d\'accès')
    action = models.CharField(max_length=20, choices=[('VIEW', 'Consultation'), ('DOWNLOAD', 'Téléchargement')], verbose_name='Action')

    class Meta:
        verbose_name = 'Accès à la ressource'
        verbose_name_plural = 'Accès aux ressources'
        ordering = ['-access_date']

    def __str__(self):
        return f"{self.user.full_name} - {self.action} - {self.resource.title}"


class Notification(models.Model):
    """Notification système"""
    TYPE_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('ERROR', 'Erreur'),
        ('SUCCESS', 'Succès'),
        ('ANNOUNCEMENT', 'Annonce'),
        ('MESSAGE', 'Message'),
        ('GRADE', 'Note'),
        ('ATTENDANCE', 'Présence'),
        ('PAYMENT', 'Paiement'),
        ('REMINDER', 'Rappel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Utilisateur')
    title = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='INFO', verbose_name='Type')
    
    # Statut
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    read_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de lecture')
    
    # Lien
    link_url = models.URLField(blank=True, verbose_name='Lien')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.user.full_name}: {self.title}"

    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_date = timezone.now()
            self.save()


class EmailTemplate(models.Model):
    """Modèle d'e-mail"""
    name = models.CharField(max_length=100, verbose_name='Nom du modèle')
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    body_text = models.TextField(verbose_name='Corps du message (texte)')
    body_html = models.TextField(blank=True, verbose_name='Corps du message (HTML)')
    
    # Variables disponibles (JSON)
    available_variables = models.JSONField(default=dict, verbose_name='Variables disponibles')
    
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Modèle d\'e-mail'
        verbose_name_plural = 'Modèles d\'e-mail'

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    """Journal d'envoi d'e-mails"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('SENT', 'Envoyé'),
        ('DELIVERED', 'Livré'),
        ('FAILED', 'Échoué'),
        ('BOUNCED', 'Rejeté'),
    ]

    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Modèle utilisé')
    recipient_email = models.EmailField(verbose_name='E-mail destinataire')
    recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Utilisateur destinataire')
    
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    body = models.TextField(verbose_name='Corps du message')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name='Statut')
    error_message = models.TextField(blank=True, verbose_name='Message d\'erreur')
    
    sent_date = models.DateTimeField(default=timezone.now, verbose_name='Date d\'envoi')
    delivered_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de livraison')

    class Meta:
        verbose_name = 'Journal d\'e-mail'
        verbose_name_plural = 'Journaux d\'e-mails'
        ordering = ['-sent_date']

    def __str__(self):
        return f"E-mail à {self.recipient_email} - {self.status}"


# MODÈLES FORUM DE CLASSE

class ForumTopic(models.Model):
    """Sujet de discussion dans le forum d'une classe"""
    
    # Contenu
    title = models.CharField(max_length=200, verbose_name='Titre')
    content = models.TextField(verbose_name='Contenu')
    
    # Relations
    classroom = models.ForeignKey('academic.ClassRoom', on_delete=models.CASCADE, related_name='forum_topics', verbose_name='Classe')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics', verbose_name='Auteur')
    
    # Statut
    is_pinned = models.BooleanField(default=False, verbose_name='Épinglé')
    is_locked = models.BooleanField(default=False, verbose_name='Verrouillé')
    is_approved = models.BooleanField(default=True, verbose_name='Approuvé')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    
    class Meta:
        verbose_name = 'Sujet de forum'
        verbose_name_plural = 'Sujets de forum'
        ordering = ['-is_pinned', '-updated_at']
        permissions = [
            ('can_moderate_forum', 'Peut modérer le forum'),
            ('can_pin_topics', 'Peut épingler des sujets'),
            ('can_lock_topics', 'Peut verrouiller des sujets'),
        ]

    def __str__(self):
        return f"{self.classroom.name} - {self.title}"

    @property
    def posts_count(self):
        """Nombre total de posts (incluant le topic lui-même)"""
        return self.forum_posts.count() + 1

    @property
    def last_post(self):
        """Dernier post du topic"""
        return self.forum_posts.order_by('-created_at').first()

    @property
    def last_activity(self):
        """Date de la dernière activité"""
        last_post = self.last_post
        if last_post:
            return last_post.created_at
        return self.created_at

    def can_user_access(self, user):
        """Vérifie si un utilisateur peut accéder à ce topic"""
        if user.role in ['ADMIN', 'SUPER_ADMIN']:
            return True
        elif user.role == 'TEACHER':
            return user in self.classroom.teachers.all()
        elif user.role == 'STUDENT':
            return hasattr(user, 'student_profile') and user.student_profile.current_class == self.classroom
        elif user.role == 'PARENT':
            if hasattr(user, 'parent_profile'):
                children_classes = [child.current_class for child in user.parent_profile.children.all() if child.current_class]
                return self.classroom in children_classes
        return False

    def increment_views(self):
        """Incrémenter le compteur de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ForumPost(models.Model):
    """Réponse à un sujet de forum"""
    
    # Relations
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='forum_posts', verbose_name='Sujet')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts', verbose_name='Auteur')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name='Réponse à')
    
    # Contenu
    content = models.TextField(verbose_name='Contenu')
    
    # Statut
    is_approved = models.BooleanField(default=True, verbose_name='Approuvé')
    is_edited = models.BooleanField(default=False, verbose_name='Modifié')
    edited_at = models.DateTimeField(blank=True, null=True, verbose_name='Modifié le')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Post de forum'
        verbose_name_plural = 'Posts de forum'
        ordering = ['created_at']

    def __str__(self):
        return f"Post de {self.author.full_name} dans {self.topic.title}"

    def can_user_edit(self, user):
        """Vérifie si un utilisateur peut modifier ce post"""
        if user == self.author:
            return True
        if user.role in ['ADMIN', 'SUPER_ADMIN']:
            return True
        if user.role == 'TEACHER' and user in self.topic.classroom.teachers.all():
            return True
        return False

    def can_user_delete(self, user):
        """Vérifie si un utilisateur peut supprimer ce post"""
        return self.can_user_edit(user)


class ForumModeration(models.Model):
    """Modération des forums"""
    
    ACTION_CHOICES = [
        ('EDIT', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOCK', 'Verrouillage'),
        ('UNLOCK', 'Déverrouillage'),
        ('PIN', 'Épinglage'),
        ('UNPIN', 'Désépinglage'),
        ('APPROVE', 'Approbation'),
        ('REJECT', 'Rejet'),
    ]
    
    # Relations
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_moderations', verbose_name='Modérateur')
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, blank=True, null=True, related_name='moderations', verbose_name='Sujet')
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, blank=True, null=True, related_name='moderations', verbose_name='Post')
    
    # Action
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Action')
    reason = models.TextField(blank=True, verbose_name='Raison')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    
    class Meta:
        verbose_name = 'Modération de forum'
        verbose_name_plural = 'Modérations de forum'
        ordering = ['-created_at']

    def __str__(self):
        target = self.topic.title if self.topic else self.post
        return f"{self.action} par {self.moderator.full_name} - {target}"
