"""
Managers personnalisés pour le filtrage des données selon les rôles (RBAC)
Module Accounts
"""
from django.db import models
from django.db.models import Q


class StudentQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les élèves"""
    
    def filter_for_teacher(self, teacher_user):
        """Filtre les élèves pour un enseignant - élèves de ses classes"""
        if hasattr(teacher_user, 'teacher_profile'):
            return self.filter(
                enrollments__classroom__teacherassignment__teacher=teacher_user.teacher_profile,
                enrollments__withdrawal_date__isnull=True
            ).distinct()
        return self.none()
    
    def filter_for_student(self, student_user):
        """Un élève ne peut voir que lui-même"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(id=student_user.student_profile.id)
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les élèves pour un parent - seulement ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            return self.filter(parents=parent_user.parent_profile)
        return self.none()
    
    def filter_for_role(self, user):
        """Filtre automatiquement selon le rôle de l'utilisateur"""
        if user.role == 'TEACHER':
            return self.filter_for_teacher(user)
        elif user.role == 'STUDENT':
            return self.filter_for_student(user)
        elif user.role == 'PARENT':
            return self.filter_for_parent(user)
        elif user.role in ['ADMIN', 'SUPER_ADMIN']:
            return self  # Accès total
        else:
            return self.none()


class StudentManager(models.Manager):
    """Manager personnalisé pour les élèves"""
    
    def get_queryset(self):
        return StudentQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)


class ParentQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les parents"""
    
    def filter_for_teacher(self, teacher_user):
        """Filtre les parents pour un enseignant - parents de ses élèves"""
        if hasattr(teacher_user, 'teacher_profile'):
            return self.filter(
                children__enrollments__classroom__teacherassignment__teacher=teacher_user.teacher_profile,
                children__enrollments__withdrawal_date__isnull=True
            ).distinct()
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les parents pour un élève - ses propres parents"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(children=student_user.student_profile)
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Un parent ne peut voir que lui-même"""
        if hasattr(parent_user, 'parent_profile'):
            return self.filter(id=parent_user.parent_profile.id)
        return self.none()
    
    def filter_for_role(self, user):
        """Filtre automatiquement selon le rôle de l'utilisateur"""
        if user.role == 'TEACHER':
            return self.filter_for_teacher(user)
        elif user.role == 'STUDENT':
            return self.filter_for_student(user)
        elif user.role == 'PARENT':
            return self.filter_for_parent(user)
        elif user.role in ['ADMIN', 'SUPER_ADMIN']:
            return self  # Accès total
        else:
            return self.none()


class ParentManager(models.Manager):
    """Manager personnalisé pour les parents"""
    
    def get_queryset(self):
        return ParentQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)


class TeacherQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les enseignants"""
    
    def filter_for_teacher(self, teacher_user):
        """Un enseignant ne peut voir que lui-même (ou collègues selon business rules)"""
        if hasattr(teacher_user, 'teacher_profile'):
            return self.filter(id=teacher_user.teacher_profile.id)
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les enseignants pour un élève - ses enseignants"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(
                teacherassignment__classroom__enrollments__student=student_user.student_profile,
                teacherassignment__classroom__enrollments__withdrawal_date__isnull=True
            ).distinct()
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les enseignants pour un parent - enseignants de ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            return self.filter(
                teacherassignment__classroom__enrollments__student__parents=parent_user.parent_profile,
                teacherassignment__classroom__enrollments__withdrawal_date__isnull=True
            ).distinct()
        return self.none()
    
    def filter_for_role(self, user):
        """Filtre automatiquement selon le rôle de l'utilisateur"""
        if user.role == 'TEACHER':
            return self.filter_for_teacher(user)
        elif user.role == 'STUDENT':
            return self.filter_for_student(user)
        elif user.role == 'PARENT':
            return self.filter_for_parent(user)
        elif user.role in ['ADMIN', 'SUPER_ADMIN']:
            return self  # Accès total
        else:
            return self.none()


class TeacherManager(models.Manager):
    """Manager personnalisé pour les enseignants"""
    
    def get_queryset(self):
        return TeacherQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)
