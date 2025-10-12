"""
Utilitaires pour le système de suivi d'activité
"""
import threading

_thread_locals = threading.local()


def get_current_user():
    """Récupère l'utilisateur actuel du thread local"""
    return getattr(_thread_locals, 'user', None)


def get_current_request():
    """Récupère la requête actuelle du thread local"""
    return getattr(_thread_locals, 'request', None)


def set_current_user(user):
    """Définit l'utilisateur actuel dans le thread local"""
    _thread_locals.user = user


def set_current_request(request):
    """Définit la requête actuelle dans le thread local"""
    _thread_locals.request = request


def clear_thread_locals():
    """Nettoie les données du thread local"""
    _thread_locals.user = None
    _thread_locals.request = None
