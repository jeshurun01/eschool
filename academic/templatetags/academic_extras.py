from django import template
from academic.models import SessionAttendance

register = template.Library()

@register.filter
def subtract(value, arg):
    """Soustrait arg de value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def get_student_attendance(session, student):
    """Récupère la présence d'un étudiant pour une session donnée"""
    try:
        return SessionAttendance.objects.get(session=session, student=student)
    except SessionAttendance.DoesNotExist:
        return None


@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par clé"""
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)
