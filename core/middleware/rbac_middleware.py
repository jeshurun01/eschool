"""
Middleware pour le contrôle d'accès basé sur les rôles (RBAC)
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class RBACMiddleware(MiddlewareMixin):
    """
    Middleware pour contrôler l'accès aux vues selon le rôle de l'utilisateur
    """
    
    # URLs publiques accessibles sans authentification
    PUBLIC_URLS = [
        '/',
        '/accounts/login/',
        '/accounts/register/',
        '/accounts/logout/',
        '/admin/',
    ]
    
    # Mappage des rôles vers les URL patterns autorisés
    ROLE_URL_PERMISSIONS = {
        'STUDENT': [
            '/accounts/student/',
            '/academic/student/',
            '/communication/student/',
        ],
        'TEACHER': [
            '/accounts/teacher/',
            '/academic/teacher/',
            '/communication/teacher/',
        ],
        'PARENT': [
            '/accounts/parent/',
            '/academic/parent/',
            '/finance/parent/',
            '/communication/parent/',
        ],
        'ADMIN': [
            '/accounts/',
            '/academic/',
            '/finance/',
            '/communication/',
        ],
        'FINANCE': [
            '/accounts/finance/',
            '/finance/',
        ],
        'SUPER_ADMIN': [
            '*',  # Accès total
        ]
    }
    
    def process_request(self, request):
        """
        Vérifie les permissions avant le traitement de la requête
        """
        # Ignorer les URLs publiques
        if any(request.path.startswith(url) for url in self.PUBLIC_URLS):
            return None
            
        # Ignorer les URLs d'assets (CSS, JS, images)
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
            
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('accounts:login')
        
        # Super admin a accès à tout
        if request.user.role == 'SUPER_ADMIN' or request.user.is_superuser:
            return None
            
        # Vérifier les permissions selon le rôle
        user_role = request.user.role
        allowed_urls = self.ROLE_URL_PERMISSIONS.get(user_role, [])
        
        # Vérifier si l'URL actuelle est autorisée pour ce rôle
        path_allowed = False
        for allowed_pattern in allowed_urls:
            if allowed_pattern == '*':  # Accès total
                path_allowed = True
                break
            elif request.path.startswith(allowed_pattern):
                path_allowed = True
                break
                
        if not path_allowed:
            messages.error(
                request, 
                f"Accès refusé. Votre rôle '{request.user.get_role_display()}' "
                f"ne permet pas d'accéder à cette section."
            )
            # Rediriger vers le dashboard approprié
            return redirect(self.get_role_dashboard(user_role))
            
        return None
    
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
        return reverse(dashboard_urls.get(role, 'accounts:login'))
