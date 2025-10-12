"""
Middleware pour le tracking automatique des modifications
"""
from activity_log.utils import set_current_user, set_current_request, clear_thread_locals


class ActivityTrackingMiddleware:
    """
    Middleware pour stocker l'utilisateur et la requête dans le thread local
    Permet aux signaux d'accéder à ces informations
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Stocker l'utilisateur et la requête dans le thread local
        set_current_user(getattr(request, 'user', None))
        set_current_request(request)
        
        response = self.get_response(request)
        
        # Nettoyer après la requête
        clear_thread_locals()
        
        return response
