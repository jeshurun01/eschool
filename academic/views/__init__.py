"""
Package des vues pour le module Academic
"""
# Import des vues principales
from .main_views import *

# Import des vues spécialisées par rôle
from . import student_views, teacher_views, parent_views, admin_views

__all__ = [
    'student_views', 
    'teacher_views', 
    'parent_views', 
    'admin_views'
]