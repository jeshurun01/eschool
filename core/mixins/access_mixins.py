"""
Mixins pour le contrôle d'accès basé sur les rôles dans les vues basées sur les classes
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin de base pour vérifier les rôles dans les vues basées sur les classes
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if (request.user.role in self.allowed_roles or 
            request.user.is_superuser or 
            request.user.role == 'SUPER_ADMIN'):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(
                request,
                f"Accès refusé. Votre rôle '{request.user.get_role_display()}' "
                f"ne permet pas d'accéder à cette page."
            )
            return redirect(self.get_role_dashboard(request.user.role))
    
    def get_role_dashboard(self, role):
        """
        Retourne l'URL du dashboard approprié selon le rôle
        """
        dashboard_urls = {
            'STUDENT': 'accounts:student_dashboard',
            'TEACHER': 'accounts:teacher_dashboard',
            'PARENT': 'accounts:parent_dashboard', 
            'ADMIN': 'accounts:admin_dashboard',
            'FINANCE': 'accounts:admin_dashboard',
            'SUPER_ADMIN': 'accounts:admin_dashboard',
        }
        try:
            return reverse(dashboard_urls.get(role, 'accounts:login'))
        except:
            return reverse('accounts:login')


class TeacherAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues réservées aux enseignants
    """
    allowed_roles = ['TEACHER', 'ADMIN', 'SUPER_ADMIN']


class StudentAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues réservées aux élèves
    """
    allowed_roles = ['STUDENT', 'ADMIN', 'SUPER_ADMIN']


class ParentAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues réservées aux parents
    """
    allowed_roles = ['PARENT', 'ADMIN', 'SUPER_ADMIN']


class StaffAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues réservées au personnel (admin/finance)
    """
    allowed_roles = ['ADMIN', 'FINANCE', 'SUPER_ADMIN']


class AdminAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues réservées aux administrateurs
    """
    allowed_roles = ['ADMIN', 'SUPER_ADMIN']


class SuperuserAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues réservées aux super administrateurs
    """
    allowed_roles = ['SUPER_ADMIN']


class TeacherOrStudentAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues accessibles aux enseignants ET élèves
    """
    allowed_roles = ['TEACHER', 'STUDENT', 'ADMIN', 'SUPER_ADMIN']


class ParentOrStudentAccessMixin(RoleRequiredMixin):
    """
    Mixin pour les vues accessibles aux parents ET élèves  
    """
    allowed_roles = ['PARENT', 'STUDENT', 'ADMIN', 'SUPER_ADMIN']
