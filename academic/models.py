from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

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
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name='Coefficient')
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
    """Présence/Absence"""
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
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
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
    
    evaluation_name = models.CharField(max_length=100, verbose_name='Nom de l\'évaluation')
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES, verbose_name='Type d\'évaluation')
    
    score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Note obtenue')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20, validators=[MinValueValidator(0.01)], verbose_name='Note maximale')
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name='Coefficient')
    
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
