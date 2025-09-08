"""
Décorateurs pour le contrôle d'accès basé sur les rôles
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required


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


def staff_required(view_func):
    """
    Décorateur pour les vues réservées au personnel (admin/finance)
    """
    return role_required(['ADMIN', 'FINANCE', 'SUPER_ADMIN'])(view_func)


def admin_required(view_func):
    """
    Décorateur pour les vues réservées aux administrateurs
    """
    return role_required(['ADMIN', 'SUPER_ADMIN'])(view_func)


def superuser_required(view_func):
    """
    Décorateur pour les vues réservées aux super administrateurs
    """
    return role_required(['SUPER_ADMIN'])(view_func)


def teacher_or_student_required(view_func):
    """
    Décorateur pour les vues accessibles aux enseignants ET élèves
    """
    return role_required(['TEACHER', 'STUDENT', 'ADMIN', 'SUPER_ADMIN'])(view_func)


def parent_or_student_required(view_func):
    """
    Décorateur pour les vues accessibles aux parents ET élèves
    """
    return role_required(['PARENT', 'STUDENT', 'ADMIN', 'SUPER_ADMIN'])(view_func)


def get_role_dashboard(role):
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
