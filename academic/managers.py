"""
Managers personnalisés pour le filtrage des données selon les rôles (RBAC)
Module Academic
"""
from django.db import models
from django.db.models import Q


class GradeQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les notes"""
    
    def filter_for_teacher(self, teacher_user):
        """Filtre les notes pour un enseignant - seulement ses notes"""
        if hasattr(teacher_user, 'teacher_profile'):
            return self.filter(teacher=teacher_user.teacher_profile)
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les notes pour un élève - seulement ses notes"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(student=student_user.student_profile)
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les notes pour un parent - notes de ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            # Récupérer les enfants du parent
            children = parent_user.parent_profile.children.all()
            return self.filter(student__in=children)
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


class GradeManager(models.Manager):
    """Manager personnalisé pour les notes"""
    
    def get_queryset(self):
        return GradeQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)


class ClassRoomQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les classes"""
    
    def filter_for_teacher(self, teacher_user):
        """Filtre les classes pour un enseignant - seulement ses classes assignées"""
        if hasattr(teacher_user, 'teacher_profile'):
            # Classes où l'enseignant a des attributions
            return self.filter(
                teacherassignment__teacher=teacher_user.teacher_profile
            ).distinct()
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les classes pour un élève - seulement ses classes"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(
                enrollments__student=student_user.student_profile,
                enrollments__is_active=True
            ).distinct()
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les classes pour un parent - classes de ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            children = parent_user.parent_profile.children.all()
            return self.filter(
                enrollments__student__in=children,
                enrollments__is_active=True
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


class ClassRoomManager(models.Manager):
    """Manager personnalisé pour les classes"""
    
    def get_queryset(self):
        return ClassRoomQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)


class EnrollmentQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les inscriptions"""
    
    def filter_for_teacher(self, teacher_user):
        """Filtre les inscriptions pour un enseignant - élèves de ses classes"""
        if hasattr(teacher_user, 'teacher_profile'):
            return self.filter(
                classroom__teacherassignment__teacher=teacher_user.teacher_profile,
                withdrawal_date__isnull=True
            ).distinct()
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les inscriptions pour un élève - ses propres inscriptions"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(
                student=student_user.student_profile,
                withdrawal_date__isnull=True
            )
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les inscriptions pour un parent - inscriptions de ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            children = parent_user.parent_profile.children.all()
            return self.filter(
                student__in=children,
                withdrawal_date__isnull=True
            )
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


class EnrollmentManager(models.Manager):
    """Manager personnalisé pour les inscriptions"""
    
    def get_queryset(self):
        return EnrollmentQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)
