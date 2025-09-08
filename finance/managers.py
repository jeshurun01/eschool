"""
Managers personnalisés pour le filtrage des données selon les rôles (RBAC)
Module Finance
"""
from django.db import models
from django.db.models import Q


class PaymentQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les paiements"""
    
    def filter_for_teacher(self, teacher_user):
        """Les enseignants n'ont généralement pas accès aux données financières"""
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les paiements pour un élève - ses propres paiements"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(invoice__student=student_user.student_profile)
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les paiements pour un parent - paiements de ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            children = parent_user.parent_profile.children.all()
            return self.filter(invoice__student__in=children)
        return self.none()
    
    def filter_for_finance_staff(self, user):
        """Personnel financier a accès à tous les paiements"""
        return self  # Accès total pour le personnel financier
    
    def filter_for_role(self, user):
        """Filtre automatiquement selon le rôle de l'utilisateur"""
        if user.role == 'TEACHER':
            return self.filter_for_teacher(user)
        elif user.role == 'STUDENT':
            return self.filter_for_student(user)
        elif user.role == 'PARENT':
            return self.filter_for_parent(user)
        elif user.role in ['FINANCE', 'ADMIN', 'SUPER_ADMIN']:
            return self.filter_for_finance_staff(user)
        else:
            return self.none()


class PaymentManager(models.Manager):
    """Manager personnalisé pour les paiements"""
    
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_finance_staff(self, user):
        return self.get_queryset().filter_for_finance_staff(user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)


class InvoiceQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les factures"""
    
    def filter_for_teacher(self, teacher_user):
        """Les enseignants n'ont généralement pas accès aux factures"""
        return self.none()
    
    def filter_for_student(self, student_user):
        """Filtre les factures pour un élève - ses propres factures"""
        if hasattr(student_user, 'student_profile'):
            return self.filter(student=student_user.student_profile)
        return self.none()
    
    def filter_for_parent(self, parent_user):
        """Filtre les factures pour un parent - factures de ses enfants"""
        if hasattr(parent_user, 'parent_profile'):
            children = parent_user.parent_profile.children.all()
            return self.filter(student__in=children)
        return self.none()
    
    def filter_for_finance_staff(self, user):
        """Personnel financier a accès à toutes les factures"""
        return self  # Accès total pour le personnel financier
    
    def filter_for_role(self, user):
        """Filtre automatiquement selon le rôle de l'utilisateur"""
        if user.role == 'TEACHER':
            return self.filter_for_teacher(user)
        elif user.role == 'STUDENT':
            return self.filter_for_student(user)
        elif user.role == 'PARENT':
            return self.filter_for_parent(user)
        elif user.role in ['FINANCE', 'ADMIN', 'SUPER_ADMIN']:
            return self.filter_for_finance_staff(user)
        else:
            return self.none()


class InvoiceManager(models.Manager):
    """Manager personnalisé pour les factures"""
    
    def get_queryset(self):
        return InvoiceQuerySet(self.model, using=self._db)
    
    def for_teacher(self, teacher_user):
        return self.get_queryset().filter_for_teacher(teacher_user)
    
    def for_student(self, student_user):
        return self.get_queryset().filter_for_student(student_user)
    
    def for_parent(self, parent_user):
        return self.get_queryset().filter_for_parent(parent_user)
    
    def for_finance_staff(self, user):
        return self.get_queryset().filter_for_finance_staff(user)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)


class ExpenseQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les dépenses"""
    
    def filter_for_role(self, user):
        """Seuls les admins et personnel financier peuvent voir les dépenses"""
        if user.role in ['FINANCE', 'ADMIN', 'SUPER_ADMIN']:
            return self  # Accès total
        else:
            return self.none()


class ExpenseManager(models.Manager):
    """Manager personnalisé pour les dépenses"""
    
    def get_queryset(self):
        return ExpenseQuerySet(self.model, using=self._db)
    
    def for_role(self, user):
        return self.get_queryset().filter_for_role(user)
