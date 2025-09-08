from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class CustomAccountAdapter(DefaultAccountAdapter):
    """Adaptateur personnalisé pour Allauth"""
    
    def get_login_redirect_url(self, request):
        """Redirection après connexion basée sur le rôle"""
        user = request.user
        if user.is_authenticated:
            # Redirection basée sur le rôle
            if user.role in ['ADMIN', 'SUPER_ADMIN'] or user.is_staff:
                return '/accounts/admin-dashboard/'
            elif user.role == 'TEACHER':
                return '/accounts/teacher-dashboard/'
            elif user.role == 'PARENT':
                return '/accounts/parent-dashboard/'
            else:
                return '/accounts/'
        return '/accounts/'


class CustomLoginForm(LoginForm):
    """Formulaire de connexion personnalisé compatible avec Allauth"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les widgets pour correspondre à notre design
        self.fields['login'].widget = forms.EmailInput(attrs={
            'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 placeholder-gray-400',
            'placeholder': 'votre@email.com',
            'autofocus': True
        })
        
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 placeholder-gray-400',
            'placeholder': '••••••••'
        })
        
        # Ajouter le champ "Se souvenir de moi"
        self.fields['remember'] = forms.BooleanField(
            required=False,
            widget=forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        )
        
        # Personnaliser les labels
        self.fields['login'].label = 'Adresse email'
        self.fields['password'].label = 'Mot de passe'
        self.fields['remember'].label = 'Se souvenir de moi'
