from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Import des managers RBAC
from .managers import GradeManager, ClassRoomManager, EnrollmentManager

User = get_user_model()

# Helper functions for default values
def get_current_date():
    """Retourne la date actuelle (sans heure)"""
    return timezone.now().date()

def get_current_datetime():
    """Retourne la date et heure actuelles avec timezone"""
    return timezone.now()


class AcademicYear(models.Model):
    """Année scolaire"""
    name = models.CharField(max_length=50, verbose_name='Nom de l\'année scolaire')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    is_current = models.BooleanField(default=False, verbose_name='Année courante')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Année scolaire'
        verbose_name_plural = 'Années scolaires'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            # S'assurer qu'une seule année est marquée comme courante
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Level(models.Model):
    """Niveau d'enseignement (Primaire, Secondaire, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nom du niveau')
    description = models.TextField(blank=True, verbose_name='Description')
    order = models.PositiveIntegerField(default=1, verbose_name='Ordre')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Niveau'
        verbose_name_plural = 'Niveaux'
        ordering = ['order']

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Matière"""
    name = models.CharField(max_length=100, verbose_name='Nom de la matière')
    code = models.CharField(max_length=10, unique=True, verbose_name='Code')
    description = models.TextField(blank=True, verbose_name='Description')
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('1.0'), verbose_name='Coefficient')
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name='Couleur')  # Hex color
    
    # Relations
    levels = models.ManyToManyField(Level, related_name='subjects', verbose_name='Niveaux')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassRoom(models.Model):
    """Classe"""
    name = models.CharField(max_length=50, verbose_name='Nom de la classe')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='classrooms', verbose_name='Niveau')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='classrooms', verbose_name='Année scolaire')
    
    # Enseignants
    head_teacher = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='head_classes', verbose_name='Professeur principal')
    teachers = models.ManyToManyField('accounts.Teacher', through='TeacherAssignment', 
                                    related_name='assigned_classes', verbose_name='Enseignants')
    
    # Capacité et informations
    capacity = models.PositiveIntegerField(default=30, verbose_name='Capacité')
    room_number = models.CharField(max_length=20, blank=True, verbose_name='Numéro de salle')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager RBAC
    objects = ClassRoomManager()

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        unique_together = ['name', 'level', 'academic_year']
        ordering = ['level__order', 'name']

    def __str__(self):
        return f"{self.name} - {self.level.name} ({self.academic_year.name})"

    @property
    def current_enrollment(self):
        return self.students.count()

    @property
    def is_full(self):
        return self.current_enrollment >= self.capacity


class TeacherAssignment(models.Model):
    """Attribution d'un enseignant à une classe pour une matière"""
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Enseignant')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, verbose_name='Classe')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Matière')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name='Année scolaire')
    
    # Horaires hebdomadaires
    hours_per_week = models.PositiveIntegerField(default=1, verbose_name='Heures par semaine')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attribution enseignant'
        verbose_name_plural = 'Attributions enseignants'
        unique_together = ['teacher', 'classroom', 'subject', 'academic_year']

    def __str__(self):
        return f"{self.teacher.user.full_name} - {self.subject.name} - {self.classroom.name}"


class Enrollment(models.Model):
    """Inscription d'un élève dans une classe"""
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='enrollments', verbose_name='Élève')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Classe')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name='Année scolaire')
    
    enrollment_date = models.DateField(default=get_current_date, verbose_name='Date d\'inscription')
    withdrawal_date = models.DateField(blank=True, null=True, verbose_name='Date de retrait')
    is_active = models.BooleanField(default=True, verbose_name='Inscription active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager RBAC
    objects = EnrollmentManager()

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        # Permettre les inscriptions multiples mais pas d'inscription active multiple
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'academic_year'],
                condition=models.Q(is_active=True),
                name='unique_active_enrollment_per_year'
            )
        ]

    def __str__(self):
        return f"{self.student.user.full_name} - {self.classroom.name} ({self.academic_year.name})"


class Timetable(models.Model):
    """Emploi du temps"""
    WEEKDAY_CHOICES = [
        (1, 'Lundi'),
        (2, 'Mardi'),
        (3, 'Mercredi'),
        (4, 'Jeudi'),
        (5, 'Vendredi'),
        (6, 'Samedi'),
        (7, 'Dimanche'),
    ]

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timetables', verbose_name='Classe')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Matière')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Enseignant')
    
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name='Jour de la semaine')
    start_time = models.TimeField(verbose_name='Heure de début')
    end_time = models.TimeField(verbose_name='Heure de fin')
    
    room = models.CharField(max_length=50, blank=True, verbose_name='Salle')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Emploi du temps'
        verbose_name_plural = 'Emplois du temps'
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f"{self.classroom.name} - {self.subject.name} - {self.get_weekday_display()} {self.start_time}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError('L\'heure de début doit être antérieure à l\'heure de fin.')


class Attendance(models.Model):
    """Présence/Absence - MODÈLE TEMPORAIRE POUR MIGRATION"""
    STATUS_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('LATE', 'En retard'),
        ('EXCUSED', 'Absent excusé'),
    ]

    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='attendances', verbose_name='Élève')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, verbose_name='Classe')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Matière')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Enseignant')
    
    date = models.DateField(verbose_name='Date')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Statut')
    justification = models.TextField(blank=True, verbose_name='Justification')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Présence (Ancien)'
        verbose_name_plural = 'Présences (Ancien)'
        unique_together = ['student', 'date', 'subject']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.user.full_name} - {self.date} - {self.get_status_display()}"


class Grade(models.Model):
    """Note/Évaluation"""
    EVALUATION_TYPE_CHOICES = [
        ('HOMEWORK', 'Devoir'),
        ('TEST', 'Interrogation'),
        ('EXAM', 'Examen'),
        ('PROJECT', 'Projet'),
        ('PARTICIPATION', 'Participation'),
        ('OTHER', 'Autre'),
    ]

    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='grades', verbose_name='Élève')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades', verbose_name='Matière')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Enseignant')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, verbose_name='Classe')
    
    # Relation optionnelle avec une session (pour les notes données pendant une session)
    session = models.ForeignKey('Session', on_delete=models.SET_NULL, null=True, blank=True, related_name='grades', verbose_name='Session associée')
    
    evaluation_name = models.CharField(max_length=100, verbose_name='Nom de l\'évaluation')
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES, verbose_name='Type d\'évaluation')
    
    score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Note obtenue')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20'), validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Note maximale')
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('1.0'), verbose_name='Coefficient')
    
    date = models.DateField(verbose_name='Date d\'évaluation')
    comments = models.TextField(blank=True, verbose_name='Commentaires')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager RBAC
    objects = GradeManager()

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.user.full_name} - {self.subject.name} - {self.evaluation_name}: {self.score}/{self.max_score}"

    @property
    def percentage(self):
        """Pourcentage de la note"""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0

    @property
    def weighted_score(self):
        """Note pondérée par le coefficient"""
        return self.score * self.coefficient


class Document(models.Model):
    """Document pédagogique pour une matière"""
    DOCUMENT_TYPE_CHOICES = [
        ('COURSE', 'Cours'),
        ('EXERCISE', 'Exercices'),
        ('EXAM', 'Examen'),
        ('CORRECTION', 'Correction'),
        ('REFERENCE', 'Référence'),
        ('OTHER', 'Autre'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre du document')
    description = models.TextField(blank=True, verbose_name='Description')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='COURSE', verbose_name='Type de document')
    
    # Relations
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents', verbose_name='Matière')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, related_name='documents', verbose_name='Enseignant')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='documents', blank=True, null=True, verbose_name='Classe spécifique')
    
    # Liaison optionnelle avec une session (pour les documents partagés pendant une session)
    session = models.ForeignKey('Session', on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_documents', verbose_name='Session associée')
    
    # Fichier
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name='Fichier')
    file_size = models.PositiveIntegerField(blank=True, null=True, verbose_name='Taille du fichier (bytes)')
    file_type = models.CharField(max_length=50, blank=True, verbose_name='Type de fichier')
    
    # Paramètres de visibilité et d'accès
    is_public = models.BooleanField(default=True, verbose_name='Visible par les étudiants')
    is_downloadable = models.BooleanField(default=True, verbose_name='Téléchargeable')
    access_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de mise à disposition')
    expiry_date = models.DateTimeField(blank=True, null=True, verbose_name='Date d\'expiration')
    
    # Statistiques
    download_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de téléchargements')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

    def save(self, *args, **kwargs):
        # Obtenir la taille et le type de fichier automatiquement
        if self.file:
            self.file_size = self.file.size
            self.file_type = self.file.name.split('.')[-1].lower() if '.' in self.file.name else ''
        
        # Définir la date d'accès par défaut si non spécifiée
        if not self.access_date:
            self.access_date = timezone.now()
            
        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        """Taille du fichier en MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    @property
    def is_accessible(self):
        """Vérifie si le document est accessible maintenant"""
        now = timezone.now()
        if self.access_date and self.access_date > now:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return True

    @property
    def file_icon(self):
        """Retourne l'icône appropriée selon le type de fichier"""
        icons = {
            'pdf': 'fas fa-file-pdf text-red-500',
            'doc': 'fas fa-file-word text-blue-500',
            'docx': 'fas fa-file-word text-blue-500',
            'xls': 'fas fa-file-excel text-green-500',
            'xlsx': 'fas fa-file-excel text-green-500',
            'ppt': 'fas fa-file-powerpoint text-orange-500',
            'pptx': 'fas fa-file-powerpoint text-orange-500',
            'txt': 'fas fa-file-alt text-gray-500',
            'jpg': 'fas fa-file-image text-purple-500',
            'jpeg': 'fas fa-file-image text-purple-500',
            'png': 'fas fa-file-image text-purple-500',
            'gif': 'fas fa-file-image text-purple-500',
            'zip': 'fas fa-file-archive text-yellow-500',
            'rar': 'fas fa-file-archive text-yellow-500',
        }
        return icons.get(self.file_type, 'fas fa-file text-gray-400')


class DocumentAccess(models.Model):
    """Suivi des accès aux documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='accesses', verbose_name='Document')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    access_type = models.CharField(max_length=20, choices=[('VIEW', 'Vue'), ('DOWNLOAD', 'Téléchargement')], verbose_name='Type d\'accès')
    accessed_at = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'accès')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP')

    class Meta:
        verbose_name = 'Accès document'
        verbose_name_plural = 'Accès documents'
        ordering = ['-accessed_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.document.title} - {self.get_access_type_display()}"


class Period(models.Model):
    """Période d'évaluation (trimestre, semestre, etc.)"""
    name = models.CharField(max_length=50, verbose_name='Nom de la période')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='periods', verbose_name='Année scolaire')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    is_current = models.BooleanField(default=False, verbose_name='Période courante')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Période'
        verbose_name_plural = 'Périodes'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.academic_year.name})"

    def save(self, *args, **kwargs):
        if self.is_current:
            # S'assurer qu'une seule période est marquée comme courante par année
            Period.objects.filter(academic_year=self.academic_year, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Session(models.Model):
    """Session de cours - Instance d'un créneau d'emploi du temps"""
    SESSION_STATUS_CHOICES = [
        ('SCHEDULED', 'Programmée'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
        ('POSTPONED', 'Reportée'),
    ]

    # Relations de base
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='sessions', verbose_name='Créneau d\'emploi du temps')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='sessions', verbose_name='Période')
    
    # Informations de la session
    date = models.DateField(verbose_name='Date de la session')
    actual_start_time = models.TimeField(blank=True, null=True, verbose_name='Heure de début réelle')
    actual_end_time = models.TimeField(blank=True, null=True, verbose_name='Heure de fin réelle')
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='SCHEDULED', verbose_name='Statut')
    
    # Contenu de la leçon
    lesson_title = models.CharField(max_length=200, blank=True, verbose_name='Titre de la leçon')
    lesson_objectives = models.TextField(blank=True, verbose_name='Objectifs de la leçon')
    lesson_content = models.TextField(blank=True, verbose_name='Contenu de la leçon')
    lesson_summary = models.TextField(blank=True, verbose_name='Résumé de ce qui a été enseigné')
    
    # Notes et observations de l'enseignant
    teacher_notes = models.TextField(blank=True, verbose_name='Notes de l\'enseignant')
    homework_given = models.TextField(blank=True, verbose_name='Devoirs donnés')
    next_lesson_preparation = models.TextField(blank=True, verbose_name='Préparation pour la prochaine leçon')
    
    # Présences
    attendance_taken = models.BooleanField(default=False, verbose_name='Appel effectué')
    attendance_taken_at = models.DateTimeField(blank=True, null=True, verbose_name='Heure de l\'appel')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Session de cours'
        verbose_name_plural = 'Sessions de cours'
        ordering = ['-date', '-timetable__start_time']
        unique_together = ['timetable', 'date']

    def __str__(self):
        return f"{self.timetable.subject.name} - {self.timetable.classroom.name} - {self.date}"

    @property
    def classroom(self):
        """Raccourci vers la classe"""
        return self.timetable.classroom

    @property
    def subject(self):
        """Raccourci vers la matière"""
        return self.timetable.subject

    @property
    def teacher(self):
        """Raccourci vers l'enseignant"""
        return self.timetable.teacher

    @property
    def planned_start_time(self):
        """Heure de début planifiée"""
        return self.timetable.start_time

    @property
    def planned_end_time(self):
        """Heure de fin planifiée"""
        return self.timetable.end_time

    @property
    def duration_planned(self):
        """Durée planifiée en minutes"""
        from datetime import datetime, date
        planned_start = datetime.combine(date.today(), self.planned_start_time)
        planned_end = datetime.combine(date.today(), self.planned_end_time)
        return int((planned_end - planned_start).total_seconds() / 60)

    @property
    def duration_actual(self):
        """Durée réelle en minutes"""
        if self.actual_start_time and self.actual_end_time:
            from datetime import datetime, date
            actual_start = datetime.combine(date.today(), self.actual_start_time)
            actual_end = datetime.combine(date.today(), self.actual_end_time)
            return int((actual_end - actual_start).total_seconds() / 60)
        return None

    @property
    def is_today(self):
        """Vérifie si la session est aujourd'hui"""
        return self.date == timezone.now().date()

    @property
    def is_past(self):
        """Vérifie si la session est passée"""
        return self.date < timezone.now().date()

    @property
    def students_count(self):
        """Nombre d'étudiants dans la classe"""
        return self.classroom.students.count()

    @property
    def present_students_count(self):
        """Nombre d'étudiants présents"""
        return self.attendances.filter(status='PRESENT').count()

    @property
    def absent_students_count(self):
        """Nombre d'étudiants absents"""
        return self.attendances.filter(status='ABSENT').count()

    @property
    def attendance_rate(self):
        """Taux de présence en pourcentage"""
        total = self.students_count
        if total == 0:
            return 0
        present = self.present_students_count
        return round((present / total) * 100, 1)

    def can_be_edited_by(self, user):
        """Vérifie si l'utilisateur peut modifier cette session"""
        return user == self.teacher.user or user.role in ['ADMIN', 'SUPER_ADMIN']

    def mark_as_completed(self):
        """Marquer la session comme terminée"""
        self.status = 'COMPLETED'
        if not self.actual_end_time:
            self.actual_end_time = timezone.now().time()
        self.save()

    def start_session(self):
        """Démarrer la session"""
        self.status = 'IN_PROGRESS'
        if not self.actual_start_time:
            self.actual_start_time = timezone.now().time()
        self.save()


class SessionAttendance(models.Model):
    """Présence pour une session spécifique"""
    STATUS_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('LATE', 'En retard'),
        ('EXCUSED', 'Absent excusé'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances', verbose_name='Session')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='session_attendances', verbose_name='Élève')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Statut')
    
    # Détails supplémentaires
    arrival_time = models.TimeField(blank=True, null=True, verbose_name='Heure d\'arrivée')
    justification = models.TextField(blank=True, verbose_name='Justification')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    # Qui a pris l'appel
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Enregistré par')
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name='Enregistré le')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Présence de session'
        verbose_name_plural = 'Présences de session'
        unique_together = ['session', 'student']
        ordering = ['student__user__last_name', 'student__user__first_name']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.session.date} - {self.get_status_display()}"

    @property
    def is_late(self):
        """Vérifie si l'étudiant est arrivé en retard"""
        if self.arrival_time and self.session.planned_start_time:
            return self.arrival_time > self.session.planned_start_time
        return False

    @property
    def minutes_late(self):
        """Nombre de minutes de retard"""
        if self.is_late and self.arrival_time:
            from datetime import datetime, date
            planned = datetime.combine(date.today(), self.session.planned_start_time)
            actual = datetime.combine(date.today(), self.arrival_time)
            return int((actual - planned).total_seconds() / 60)
        return 0


class DailyAttendanceSummary(models.Model):
    """Vue agrégée automatique des présences journalières"""
    DAILY_STATUS_CHOICES = [
        ('FULLY_PRESENT', 'Entièrement présent'),
        ('PARTIALLY_PRESENT', 'Partiellement présent'),
        ('MOSTLY_ABSENT', 'Majoritairement absent'),
        ('FULLY_ABSENT', 'Entièrement absent'),
    ]

    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='daily_summaries', verbose_name='Élève')
    date = models.DateField(verbose_name='Date')
    
    # Statistiques calculées automatiquement
    total_sessions = models.PositiveIntegerField(default=0, verbose_name='Total de sessions')
    present_sessions = models.PositiveIntegerField(default=0, verbose_name='Sessions présentes')
    absent_sessions = models.PositiveIntegerField(default=0, verbose_name='Sessions absentes')
    late_sessions = models.PositiveIntegerField(default=0, verbose_name='Sessions en retard')
    excused_sessions = models.PositiveIntegerField(default=0, verbose_name='Sessions excusées')
    
    # Statut global de la journée (calculé automatiquement)
    daily_status = models.CharField(max_length=20, choices=DAILY_STATUS_CHOICES, verbose_name='Statut journalier')
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name='Taux de présence (%)')
    
    # Informations additionnelles
    first_arrival_time = models.TimeField(blank=True, null=True, verbose_name='Première arrivée')
    total_late_minutes = models.PositiveIntegerField(default=0, verbose_name='Total minutes de retard')
    justification_provided = models.BooleanField(default=False, verbose_name='Justification fournie')
    
    # Métadonnées
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Résumé quotidien de présence'
        verbose_name_plural = 'Résumés quotidiens de présence'
        unique_together = ['student', 'date']
        ordering = ['-date', 'student__user__last_name']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} - {self.get_daily_status_display()}"

    @classmethod
    def calculate_for_student_date(cls, student, date):
        """Calcule et met à jour le résumé pour un étudiant et une date donnée"""
        # Récupérer toutes les présences de session pour cette date
        session_attendances = SessionAttendance.objects.filter(
            student=student,
            session__date=date
        ).select_related('session')
        
        if not session_attendances.exists():
            # Pas de sessions ce jour-là, supprimer le résumé s'il existe
            cls.objects.filter(student=student, date=date).delete()
            return None
        
        # Calculer les statistiques
        total_sessions = session_attendances.count()
        present_sessions = session_attendances.filter(status='PRESENT').count()
        absent_sessions = session_attendances.filter(status='ABSENT').count()
        late_sessions = session_attendances.filter(status='LATE').count()
        excused_sessions = session_attendances.filter(status='EXCUSED').count()
        
        # Calculer le taux de présence (présent + en retard = présent)
        effective_present = present_sessions + late_sessions
        attendance_rate = (effective_present / total_sessions * 100) if total_sessions > 0 else 0
        
        # Déterminer le statut journalier
        if attendance_rate == 100:
            daily_status = 'FULLY_PRESENT'
        elif attendance_rate >= 75:
            daily_status = 'PARTIALLY_PRESENT'
        elif attendance_rate >= 25:
            daily_status = 'MOSTLY_ABSENT'
        else:
            daily_status = 'FULLY_ABSENT'
        
        # Calculer les détails supplémentaires
        arrival_times = session_attendances.filter(
            arrival_time__isnull=False
        ).values_list('arrival_time', flat=True)
        first_arrival_time = min(arrival_times) if arrival_times else None
        
        # Calculer le total des minutes de retard
        total_late_minutes = 0
        for attendance in session_attendances.filter(status='LATE'):
            if attendance.minutes_late:
                total_late_minutes += attendance.minutes_late
        
        # Vérifier si une justification a été fournie
        justification_provided = session_attendances.filter(
            justification__isnull=False,
            justification__gt=''
        ).exists()
        
        # Créer ou mettre à jour le résumé
        summary, created = cls.objects.update_or_create(
            student=student,
            date=date,
            defaults={
                'total_sessions': total_sessions,
                'present_sessions': present_sessions,
                'absent_sessions': absent_sessions,
                'late_sessions': late_sessions,
                'excused_sessions': excused_sessions,
                'daily_status': daily_status,
                'attendance_rate': Decimal(str(round(attendance_rate, 2))),
                'first_arrival_time': first_arrival_time,
                'total_late_minutes': total_late_minutes,
                'justification_provided': justification_provided,
            }
        )
        
        return summary

    @property
    def is_problematic(self):
        """Vérifie si cette journée nécessite une attention particulière"""
        return (
            self.daily_status in ['MOSTLY_ABSENT', 'FULLY_ABSENT'] or
            self.total_late_minutes > 30 or
            (self.absent_sessions > 0 and not self.justification_provided)
        )

    @property
    def attendance_percentage_display(self):
        """Affichage formaté du pourcentage de présence"""
        return f"{self.attendance_rate}%"

    def get_detailed_status(self):
        """Retourne un statut détaillé pour l'affichage"""
        if self.total_sessions == 0:
            return "Aucune session"
        
        details = []
        if self.present_sessions > 0:
            details.append(f"{self.present_sessions} présent(es)")
        if self.late_sessions > 0:
            details.append(f"{self.late_sessions} en retard")
        if self.absent_sessions > 0:
            details.append(f"{self.absent_sessions} absent(es)")
        if self.excused_sessions > 0:
            details.append(f"{self.excused_sessions} excusé(es)")
        
        return " • ".join(details)


class SessionDocument(models.Model):
    """Document lié à une session spécifique"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='documents', verbose_name='Session')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='session_links', verbose_name='Document')
    
    # Informations sur la liaison
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name='Partagé le')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Partagé par')
    purpose = models.TextField(blank=True, verbose_name='Objectif du partage')
    
    # Options de partage
    is_mandatory = models.BooleanField(default=False, verbose_name='Lecture obligatoire')
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Date limite de consultation')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Document de session'
        verbose_name_plural = 'Documents de session'
        unique_together = ['session', 'document']
        ordering = ['-shared_at']

    def __str__(self):
        return f"{self.document.title} - Session {self.session.date}"

    @property
    def is_overdue(self):
        """Vérifie si la date limite est dépassée"""
        if self.deadline:
            return timezone.now() > self.deadline
        return False


class SessionAssignment(models.Model):
    """Devoir donné pendant une session"""
    ASSIGNMENT_TYPE_CHOICES = [
        ('HOMEWORK', 'Devoir maison'),
        ('EXERCISE', 'Exercice'),
        ('PROJECT', 'Projet'),
        ('RESEARCH', 'Recherche'),
        ('READING', 'Lecture'),
        ('PREPARATION', 'Préparation'),
        ('OTHER', 'Autre'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
        ('URGENT', 'Urgente'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='assignments', verbose_name='Session')
    
    # Informations du devoir
    title = models.CharField(max_length=200, verbose_name='Titre du devoir')
    description = models.TextField(verbose_name='Description détaillée')
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES, default='HOMEWORK', verbose_name='Type de devoir')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM', verbose_name='Priorité')
    
    # Dates importantes
    due_date = models.DateTimeField(verbose_name='Date limite de rendu')
    estimated_duration = models.PositiveIntegerField(help_text='En minutes', verbose_name='Durée estimée')
    
    # Évaluation
    will_be_graded = models.BooleanField(default=True, verbose_name='Sera noté')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Note maximale')
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('1.0'), verbose_name='Coefficient')
    
    # Instructions et ressources
    instructions = models.TextField(blank=True, verbose_name='Instructions spécifiques')
    resources_needed = models.TextField(blank=True, verbose_name='Ressources nécessaires')
    submission_format = models.CharField(max_length=100, blank=True, verbose_name='Format de rendu')
    
    # Visibilité et accès
    is_published = models.BooleanField(default=True, verbose_name='Publié aux étudiants')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Publié le')
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Devoir de session'
        verbose_name_plural = 'Devoirs de session'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.session.subject.name} - Échéance: {self.due_date.strftime('%d/%m/%Y')}"

    @property
    def is_overdue(self):
        """Vérifie si le devoir est en retard"""
        return timezone.now() > self.due_date

    @property
    def days_until_due(self):
        """Nombre de jours avant l'échéance"""
        now = timezone.now()
        if self.due_date > now:
            return (self.due_date - now).days
        return 0

    @property
    def time_until_due(self):
        """Temps restant avant l'échéance (format lisible)"""
        now = timezone.now()
        if self.due_date > now:
            delta = self.due_date - now
            if delta.days > 0:
                return f"{delta.days} jour(s)"
            else:
                hours = delta.seconds // 3600
                return f"{hours} heure(s)"
        return "Échéance dépassée"

    @property
    def classroom(self):
        """Raccourci vers la classe"""
        return self.session.classroom

    @property
    def subject(self):
        """Raccourci vers la matière"""
        return self.session.subject

    @property
    def teacher(self):
        """Raccourci vers l'enseignant"""
        return self.session.teacher

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class SessionNote(models.Model):
    """Notes et observations spécifiques à une session"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='notes', verbose_name='Session')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Auteur')
    
    # Contenu de la note
    title = models.CharField(max_length=200, blank=True, verbose_name='Titre')
    content = models.TextField(verbose_name='Contenu')
    note_type = models.CharField(max_length=20, choices=[
        ('GENERAL', 'Générale'),
        ('BEHAVIOR', 'Comportement'),
        ('PARTICIPATION', 'Participation'),
        ('DIFFICULTY', 'Difficulté'),
        ('ACHIEVEMENT', 'Réussite'),
        ('REMINDER', 'Rappel'),
    ], default='GENERAL', verbose_name='Type de note')
    
    # Visibilité
    is_private = models.BooleanField(default=False, verbose_name='Note privée (enseignant seulement)')
    visible_to_students = models.BooleanField(default=False, verbose_name='Visible aux étudiants')
    visible_to_parents = models.BooleanField(default=False, verbose_name='Visible aux parents')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Note de session'
        verbose_name_plural = 'Notes de session'
        ordering = ['-created_at']

    def __str__(self):
        title = self.title if self.title else f"Note {self.note_type}"
        return f"{title} - {self.session.date}"


# ===== SIGNAUX POUR LA MISE À JOUR AUTOMATIQUE DES RÉSUMÉS =====

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=SessionAttendance)
def update_daily_summary_on_attendance_save(sender, instance, **kwargs):
    """Met à jour le résumé quotidien quand une présence de session est sauvegardée"""
    DailyAttendanceSummary.calculate_for_student_date(
        student=instance.student,
        date=instance.session.date
    )

@receiver(post_delete, sender=SessionAttendance)
def update_daily_summary_on_attendance_delete(sender, instance, **kwargs):
    """Met à jour le résumé quotidien quand une présence de session est supprimée"""
    DailyAttendanceSummary.calculate_for_student_date(
        student=instance.student,
        date=instance.session.date
    )
