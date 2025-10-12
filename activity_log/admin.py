"""
Administration du système de suivi d'activité
"""
from django.contrib import admin
from django.utils.html import format_html
from activity_log.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'colored_action_type',
        'user_display',
        'description_short',
        'content_type',
        'timestamp',
        'ip_address'
    ]
    list_filter = [
        'action_type',
        'content_type',
        'timestamp',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        'description',
        'user__first_name',
        'user__last_name',
        'user__email',
        'object_repr',
        'ip_address'
    ]
    readonly_fields = [
        'user',
        'action_type',
        'timestamp',
        'description',
        'content_type',
        'object_id',
        'object_repr',
        'old_values',
        'new_values',
        'ip_address',
        'user_agent',
        'changes_display'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def colored_action_type(self, obj):
        """Affiche le type d'action avec une couleur"""
        colors = {
            'CREATE': '#10B981',  # green
            'UPDATE': '#3B82F6',  # blue
            'DELETE': '#EF4444',  # red
            'SEND': '#8B5CF6',    # purple
            'APPROVE': '#10B981', # green
            'REJECT': '#EF4444',  # red
            'LOGIN': '#6B7280',   # gray
            'LOGOUT': '#6B7280',  # gray
        }
        verb = obj.action_verb
        color = colors.get(verb, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_action_type_display()
        )
    colored_action_type.short_description = 'Action'
    
    def user_display(self, obj):
        """Affiche l'utilisateur avec un lien"""
        if obj.user:
            return format_html(
                '<a href="/accounts/users/{}/">{}</a>',
                obj.user.id,
                obj.user.get_full_name()
            )
        return 'Système'
    user_display.short_description = 'Utilisateur'
    
    def description_short(self, obj):
        """Description tronquée"""
        if len(obj.description) > 60:
            return obj.description[:60] + '...'
        return obj.description
    description_short.short_description = 'Description'
    
    def changes_display(self, obj):
        """Affiche les changements de manière lisible"""
        changes = obj.get_changes()
        if not changes:
            return 'Aucun changement'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr><th style="border: 1px solid #ddd; padding: 8px;">Champ</th><th style="border: 1px solid #ddd; padding: 8px;">Avant</th><th style="border: 1px solid #ddd; padding: 8px;">Après</th></tr>'
        
        for field, change in changes.items():
            html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;"><strong>{field}</strong></td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px; background-color: #fee; color: #c00;">{change["old"]}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px; background-color: #efe; color: #0a0;">{change["new"]}</td></tr>'
        
        html += '</table>'
        return format_html(html)
    changes_display.short_description = 'Modifications'
    
    def has_add_permission(self, request):
        """Empêcher l'ajout manuel de logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêcher la modification des logs"""
        return False
