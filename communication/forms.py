from django import forms
from .models import Announcement
from academic.models import ClassRoom, Level


class AnnouncementForm(forms.ModelForm):
    """Formulaire pour créer/modifier une annonce"""
    
    ROLE_CHOICES = [
        ('STUDENT', 'Élèves'),
        ('PARENT', 'Parents'),
        ('TEACHER', 'Enseignants'),
        ('ADMIN', 'Administrateurs'),
    ]
    
    target_roles = forms.MultipleChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Rôles ciblés',
        help_text='Sélectionnez un ou plusieurs rôles (laisser vide pour tous)'
    )
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'type', 'audience',
            'target_classes', 'target_levels',
            'priority', 'is_pinned', 'expiry_date',
            'send_email', 'send_sms'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Titre de l\'annonce'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Contenu de l\'annonce'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'audience': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'target_classes': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'target_levels': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'expiry_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'send_email': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'send_sms': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si l'annonce existe déjà, charger les rôles ciblés
        if self.instance and self.instance.pk:
            roles = self.instance.target_roles_list
            if roles:
                self.initial['target_roles'] = roles
    
    def clean(self):
        cleaned_data = super().clean()
        audience = cleaned_data.get('audience')
        target_classes = cleaned_data.get('target_classes')
        target_levels = cleaned_data.get('target_levels')
        
        # Validation: si audience est CLASS, au moins une classe doit être sélectionnée
        if audience == 'CLASS' and not target_classes:
            self.add_error('target_classes', 'Veuillez sélectionner au moins une classe.')
        
        # Validation: si audience est LEVEL, au moins un niveau doit être sélectionné
        if audience == 'LEVEL' and not target_levels:
            self.add_error('target_levels', 'Veuillez sélectionner au moins un niveau.')
        
        return cleaned_data
