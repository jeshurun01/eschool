"""
Models pour le système de suivi d'activité
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class ActivityLog(models.Model):
    """
    Système de suivi des activités des utilisateurs
    Enregistre toutes les actions importantes (CRUD) dans l'application
    """
    
    ACTION_TYPES = [
        # Notes
        ('GRADE_CREATE', 'Note créée'),
        ('GRADE_UPDATE', 'Note modifiée'),
        ('GRADE_DELETE', 'Note supprimée'),
        
        # Finance - Factures
        ('INVOICE_CREATE', 'Facture créée'),
        ('INVOICE_UPDATE', 'Facture modifiée'),
        ('INVOICE_DELETE', 'Facture supprimée'),
        ('INVOICE_SEND', 'Facture envoyée'),
        ('INVOICE_CANCEL', 'Facture annulée'),
        
        # Finance - Paiements
        ('PAYMENT_CREATE', 'Paiement créé'),
        ('PAYMENT_UPDATE', 'Paiement modifié'),
        ('PAYMENT_DELETE', 'Paiement supprimé'),
        ('PAYMENT_APPROVE', 'Paiement approuvé'),
        ('PAYMENT_REJECT', 'Paiement rejeté'),
        
        # Présences
        ('ATTENDANCE_CREATE', 'Présence enregistrée'),
        ('ATTENDANCE_UPDATE', 'Présence modifiée'),
        ('ATTENDANCE_DELETE', 'Présence supprimée'),
        
        # Documents
        ('DOCUMENT_CREATE', 'Document ajouté'),
        ('DOCUMENT_UPDATE', 'Document modifié'),
        ('DOCUMENT_DELETE', 'Document supprimé'),
        
        # Sessions
        ('SESSION_CREATE', 'Session créée'),
        ('SESSION_UPDATE', 'Session modifiée'),
        ('SESSION_DELETE', 'Session supprimée'),
        
        # Utilisateurs
        ('USER_CREATE', 'Utilisateur créé'),
        ('USER_UPDATE', 'Utilisateur modifié'),
        ('USER_DELETE', 'Utilisateur supprimé'),
        ('USER_LOGIN', 'Connexion'),
        ('USER_LOGOUT', 'Déconnexion'),
        
        # Autres
        ('OTHER', 'Autre action'),
    ]
    
    # Informations de base
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='activity_logs',
        verbose_name='Utilisateur'
    )
    action_type = models.CharField(
        max_length=30, 
        choices=ACTION_TYPES,
        verbose_name='Type d\'action',
        db_index=True
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date et heure',
        db_index=True
    )
    
    # Détails de l'action
    description = models.TextField(
        verbose_name='Description',
        help_text='Description détaillée de l\'action'
    )
    
    # Informations sur l'objet modifié
    content_type = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name='Type d\'objet',
        help_text='Ex: Grade, Invoice, Payment'
    )
    object_id = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name='ID de l\'objet'
    )
    object_repr = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Représentation de l\'objet'
    )
    
    # Données avant/après (JSON)
    old_values = models.JSONField(
        null=True, 
        blank=True,
        verbose_name='Anciennes valeurs',
        help_text='État avant modification (JSON)'
    )
    new_values = models.JSONField(
        null=True, 
        blank=True,
        verbose_name='Nouvelles valeurs',
        help_text='État après modification (JSON)'
    )
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name='Adresse IP'
    )
    user_agent = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='User Agent',
        help_text='Navigateur utilisé'
    )
    
    class Meta:
        verbose_name = 'Journal d\'activité'
        verbose_name_plural = 'Journal des activités'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'user']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Système'
        return f"{user_name} - {self.get_action_type_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def action_category(self):
        """Retourne la catégorie de l'action (GRADE, INVOICE, etc.)"""
        return self.action_type.split('_')[0] if '_' in self.action_type else 'OTHER'
    
    @property
    def action_verb(self):
        """Retourne le verbe de l'action (CREATE, UPDATE, DELETE)"""
        parts = self.action_type.split('_')
        return parts[1] if len(parts) > 1 else 'OTHER'
    
    @property
    def icon_class(self):
        """Retourne l'icône Material appropriée selon le type d'action"""
        icons = {
            'GRADE': 'grade',
            'INVOICE': 'receipt',
            'PAYMENT': 'payment',
            'ATTENDANCE': 'check_circle',
            'DOCUMENT': 'description',
            'SESSION': 'event',
            'USER': 'person',
        }
        return icons.get(self.action_category, 'info')
    
    @property
    def color_class(self):
        """Retourne la classe de couleur selon le type d'action"""
        colors = {
            'CREATE': 'text-green-600 bg-green-50',
            'UPDATE': 'text-blue-600 bg-blue-50',
            'DELETE': 'text-red-600 bg-red-50',
            'SEND': 'text-purple-600 bg-purple-50',
            'APPROVE': 'text-green-600 bg-green-50',
            'REJECT': 'text-red-600 bg-red-50',
            'LOGIN': 'text-gray-600 bg-gray-50',
            'LOGOUT': 'text-gray-600 bg-gray-50',
        }
        return colors.get(self.action_verb, 'text-gray-600 bg-gray-50')
    
    def get_changes(self):
        """Retourne un dictionnaire des changements (avant/après)"""
        if not self.old_values or not self.new_values:
            return {}
        
        changes = {}
        for key in self.new_values.keys():
            old_val = self.old_values.get(key)
            new_val = self.new_values.get(key)
            if old_val != new_val:
                changes[key] = {
                    'old': old_val,
                    'new': new_val
                }
        return changes


def log_activity(user, action_type, description, content_type=None, object_id=None, 
                 object_repr=None, old_values=None, new_values=None, 
                 request=None, timestamp=None):
    """
    Fonction utilitaire pour créer un log d'activité
    
    Usage:
        log_activity(
            user=request.user,
            action_type='GRADE_CREATE',
            description='Note ajoutée pour Marie Dupont en Mathématiques',
            content_type='Grade',
            object_id=grade.id,
            object_repr=str(grade),
            new_values={'score': 15, 'coefficient': 2},
            request=request
        )
    """
    log_data = {
        'user': user,
        'action_type': action_type,
        'description': description,
        'content_type': content_type,
        'object_id': object_id,
        'object_repr': object_repr,
        'old_values': old_values,
        'new_values': new_values,
    }
    
    # S'assurer que le timestamp est timezone-aware
    if timestamp:
        from django.utils.timezone import is_aware, make_aware
        if not is_aware(timestamp):
            timestamp = make_aware(timestamp)
        log_data['timestamp'] = timestamp
    
    # Ajouter les infos de la requête si disponible
    if request:
        log_data['ip_address'] = request.META.get('REMOTE_ADDR')
        log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    return ActivityLog.objects.create(**log_data)
