"""
Décorateurs et mixins pour le contrôle d'accès basé sur les rôles
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404


def get_role_dashboard(role):
    """
    Retourne l'URL du dashboard approprié selon le rôle
    """
    dashboard_urls = {
        'STUDENT': 'accounts:student_dashboard',
        'TEACHER': 'accounts:teacher_dashboard', 
        'PARENT': 'accounts:parent_dashboard',
        'ADMIN': 'accounts:dashboard',
        'FINANCE': 'accounts:dashboard',
        'SUPER_ADMIN': 'accounts:dashboard',
    }
    try:
        return reverse(dashboard_urls.get(role, 'accounts:login'))
    except:
        return reverse('accounts:login')


def role_required(allowed_roles):
    """
    Décorateur générique pour vérifier les rôles autorisés
    
    Args:
        allowed_roles (list): Liste des rôles autorisés
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request,
                    f"Accès refusé. Votre rôle '{request.user.get_role_display()}' "
                    f"ne permet pas d'accéder à cette page."
                )
                return redirect(get_role_dashboard(request.user.role))
        return _wrapped_view
    return decorator


def teacher_required(view_func):
    """
    Décorateur pour les vues réservées aux enseignants
    """
    return role_required(['TEACHER', 'ADMIN', 'SUPER_ADMIN'])(view_func)


def student_required(view_func):
    """
    Décorateur pour les vues réservées aux élèves
    """
    return role_required(['STUDENT', 'ADMIN', 'SUPER_ADMIN'])(view_func)


def parent_required(view_func):
    """
    Décorateur pour les vues réservées aux parents
    """
    return role_required(['PARENT', 'ADMIN', 'SUPER_ADMIN'])(view_func)


def admin_required(view_func):
    """
    Décorateur pour les vues réservées aux administrateurs
    """
    return role_required(['ADMIN', 'SUPER_ADMIN'])(view_func)


def finance_required(view_func):
    """
    Décorateur pour les vues réservées au personnel financier
    """
    return role_required(['FINANCE', 'ADMIN', 'SUPER_ADMIN'])(view_func)


def staff_required(view_func):
    """
    Décorateur pour les vues réservées au personnel (enseignants + admin)
    """
    return role_required(['TEACHER', 'ADMIN', 'SUPER_ADMIN', 'FINANCE'])(view_func)


# Mixins pour les vues basées sur les classes
class RoleRequiredMixin(LoginRequiredMixin):
    """Mixin pour les vues basées sur les classes avec contrôle de rôle"""
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not self.allowed_roles:
            raise ValueError("allowed_roles doit être défini")
        
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.role not in self.allowed_roles and not request.user.is_superuser:
            raise PermissionDenied(f"Accès refusé. Rôles requis : {', '.join(self.allowed_roles)}")
        
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues réservées aux étudiants"""
    allowed_roles = ['STUDENT', 'ADMIN', 'SUPER_ADMIN']


class TeacherRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues réservées aux enseignants"""
    allowed_roles = ['TEACHER', 'ADMIN', 'SUPER_ADMIN']


class ParentRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues réservées aux parents"""
    allowed_roles = ['PARENT', 'ADMIN', 'SUPER_ADMIN']


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues réservées aux administrateurs"""
    allowed_roles = ['ADMIN', 'SUPER_ADMIN']


class StaffRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues accessibles au personnel"""
    allowed_roles = ['TEACHER', 'ADMIN', 'SUPER_ADMIN', 'FINANCE']


# Mixins pour l'accès aux données
class StudentDataAccessMixin:
    """
    Mixin pour contrôler l'accès aux données d'étudiants selon le rôle
    """
    def get_accessible_students(self, user):
        """Retourne les étudiants accessibles selon le rôle de l'utilisateur"""
        from accounts.models import Student
        return Student.objects.for_role(user)
    
    def check_student_access(self, user, student):
        """Vérifie si l'utilisateur peut accéder aux données de cet étudiant"""
        accessible_students = self.get_accessible_students(user)
        if student not in accessible_students:
            raise PermissionDenied("Accès refusé à cet étudiant")
        return True


class SessionAccessMixin:
    """
    Mixin pour contrôler l'accès aux sessions selon le rôle
    """
    def get_accessible_sessions(self, user):
        """Retourne les sessions accessibles selon le rôle de l'utilisateur"""
        from academic.models import Session
        
        if user.role == 'STUDENT':
            # Étudiant : sessions de sa classe
            if hasattr(user, 'student_profile') and user.student_profile.current_class:
                return Session.objects.filter(
                    timetable__classroom=user.student_profile.current_class
                )
        elif user.role == 'TEACHER':
            # Enseignant : sessions qu'il enseigne
            if hasattr(user, 'teacher_profile'):
                return Session.objects.filter(
                    timetable__teacher=user.teacher_profile
                )
        elif user.role == 'PARENT':
            # Parent : sessions des classes de ses enfants
            if hasattr(user, 'parent_profile'):
                return Session.objects.filter(
                    timetable__classroom__students__parents=user.parent_profile
                ).distinct()
        elif user.role in ['ADMIN', 'SUPER_ADMIN']:
            # Admin : toutes les sessions
            return Session.objects.all()
        
        return Session.objects.none()
    
    def check_session_access(self, user, session):
        """Vérifie si l'utilisateur peut accéder à cette session"""
        accessible_sessions = self.get_accessible_sessions(user)
        if session not in accessible_sessions:
            raise PermissionDenied("Accès refusé à cette session")
        return True


class TimetableAccessMixin:
    """
    Mixin pour contrôler l'accès aux créneaux selon le rôle
    """
    def get_accessible_timetables(self, user):
        """Retourne les créneaux accessibles selon le rôle de l'utilisateur"""
        from academic.models import Timetable
        
        if user.role == 'STUDENT':
            # Étudiant : créneaux de sa classe
            if hasattr(user, 'student_profile') and user.student_profile.current_class:
                return Timetable.objects.filter(
                    classroom=user.student_profile.current_class
                )
        elif user.role == 'TEACHER':
            # Enseignant : créneaux qu'il enseigne
            if hasattr(user, 'teacher_profile'):
                return Timetable.objects.filter(
                    teacher=user.teacher_profile
                )
        elif user.role == 'PARENT':
            # Parent : créneaux des classes de ses enfants
            if hasattr(user, 'parent_profile'):
                return Timetable.objects.filter(
                    classroom__students__parents=user.parent_profile
                ).distinct()
        elif user.role in ['ADMIN', 'SUPER_ADMIN']:
            # Admin : tous les créneaux
            return Timetable.objects.all()
        
        return Timetable.objects.none()


# Décorateurs combinés
def teacher_or_student_required(view_func):
    """Décorateur pour les vues accessibles aux enseignants, étudiants ET administrateurs"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        if request.user.role not in ['TEACHER', 'STUDENT', 'ADMIN', 'SUPER_ADMIN']:
            raise PermissionDenied("Accès réservé aux enseignants, étudiants et administrateurs")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def parent_or_student_required(view_func):
    """Décorateur pour les vues accessibles aux parents, étudiants ET administrateurs"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        if request.user.role not in ['PARENT', 'STUDENT', 'ADMIN', 'SUPER_ADMIN']:
            raise PermissionDenied("Accès réservé aux parents, étudiants et administrateurs")
        
        return view_func(request, *args, **kwargs)
    return wrapper