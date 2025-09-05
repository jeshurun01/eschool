from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse e-mail est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPER_ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Un superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Un superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('STUDENT', 'Élève'),
        ('PARENT', 'Parent'),
        ('TEACHER', 'Enseignant'),
        ('ADMIN', 'Administrateur'),
        ('FINANCE', 'Personnel financier'),
        ('SUPER_ADMIN', 'Super administrateur'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    email = models.EmailField(unique=True, verbose_name='Adresse e-mail')
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Photo de profil')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Rôle')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='Genre')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date de naissance')
    address = models.TextField(blank=True, verbose_name='Adresse')
    
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    is_staff = models.BooleanField(default=False, verbose_name='Membre du personnel')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Date d\'inscription')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Dernière connexion')
    email_verified = models.BooleanField(default=False, verbose_name='E-mail vérifié')
    
    # Préférences
    preferred_language = models.CharField(max_length=5, default='fr', verbose_name='Langue préférée')
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """Django method for full name"""
        return f"{self.first_name} {self.last_name}"

    def get_role_display_verbose(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


class Profile(models.Model):
    """Profil étendu pour des informations supplémentaires selon le rôle"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name='Biographie')
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name='Contact d\'urgence (nom)')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Contact d\'urgence (téléphone)')
    national_id = models.CharField(max_length=50, blank=True, verbose_name='Numéro d\'identité nationale')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    def __str__(self):
        return f"Profil de {self.user.full_name}"


class Student(models.Model):
    """Modèle spécifique pour les élèves"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    matricule = models.CharField(max_length=20, unique=True, verbose_name='Matricule')
    enrollment_date = models.DateField(default=timezone.now, verbose_name='Date d\'inscription')
    
    # Relations avec parents
    parents = models.ManyToManyField('Parent', related_name='children', blank=True, verbose_name='Parents/Tuteurs')
    
    # Informations académiques
    current_class = models.ForeignKey('academic.ClassRoom', on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='students', verbose_name='Classe actuelle')
    
    # Statut
    is_graduated = models.BooleanField(default=False, verbose_name='Diplômé')
    graduation_date = models.DateField(blank=True, null=True, verbose_name='Date de diplôme')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Élève'
        verbose_name_plural = 'Élèves'
        ordering = ['matricule']

    def __str__(self):
        return f"{self.user.full_name} ({self.matricule})"

    def save(self, *args, **kwargs):
        if not self.matricule:
            # Générer un matricule automatiquement
            current_year = timezone.now().year
            last_student = Student.objects.filter(
                matricule__startswith=f"STU{current_year}"
            ).order_by('matricule').last()
            
            if last_student:
                last_number = int(last_student.matricule[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.matricule = f"STU{current_year}{new_number:04d}"
        
        super().save(*args, **kwargs)


class Parent(models.Model):
    """Modèle spécifique pour les parents/tuteurs"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    profession = models.CharField(max_length=100, blank=True, verbose_name='Profession')
    workplace = models.CharField(max_length=200, blank=True, verbose_name='Lieu de travail')
    relationship_choices = [
        ('FATHER', 'Père'),
        ('MOTHER', 'Mère'),
        ('GUARDIAN', 'Tuteur'),
        ('OTHER', 'Autre'),
    ]
    relationship = models.CharField(max_length=20, choices=relationship_choices, 
                                  default='FATHER', verbose_name='Lien de parenté')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Parent/Tuteur'
        verbose_name_plural = 'Parents/Tuteurs'

    def __str__(self):
        return f"{self.user.full_name} ({self.get_relationship_display()})"


class Teacher(models.Model):
    """Modèle spécifique pour les enseignants"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='ID Employé')
    hire_date = models.DateField(default=timezone.now, verbose_name='Date d\'embauche')
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Salaire')
    
    # Spécialités/Matières enseignées
    subjects = models.ManyToManyField('academic.Subject', related_name='teachers', blank=True, 
                                    verbose_name='Matières enseignées')
    
    # Qualifications
    education_level = models.CharField(max_length=100, blank=True, verbose_name='Niveau d\'éducation')
    certifications = models.TextField(blank=True, verbose_name='Certifications')
    
    # Statut
    is_head_teacher = models.BooleanField(default=False, verbose_name='Professeur principal')
    is_active_employee = models.BooleanField(default=True, verbose_name='Employé actif')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Générer un ID employé automatiquement
            current_year = timezone.now().year
            last_teacher = Teacher.objects.filter(
                employee_id__startswith=f"TEA{current_year}"
            ).order_by('employee_id').last()
            
            if last_teacher:
                last_number = int(last_teacher.employee_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.employee_id = f"TEA{current_year}{new_number:04d}"
        
        super().save(*args, **kwargs)
