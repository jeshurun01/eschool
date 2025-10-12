# Application Activity Log

Application Django pour le suivi des activités utilisateurs dans eSchool.

## Description

Cette application enregistre automatiquement toutes les actions importantes effectuées par les utilisateurs :
- **Notes** : Création, modification, suppression de notes par les enseignants
- **Finances** : Gestion des factures et paiements par les administrateurs
- **Documents** : Ajout, modification, suppression de documents
- **Sessions** : Gestion des sessions académiques
- **Utilisateurs** : Connexions, déconnexions, et gestion des comptes

## Structure

```
activity_log/
├── models.py           # Modèle ActivityLog avec 16 types d'actions
├── signals.py          # Signaux Django pour tracking automatique
├── views.py            # Vues pour consultation des logs
├── admin.py            # Interface d'administration
├── urls.py             # Routes URL
├── utils.py            # Utilitaires thread-local
├── middleware.py       # Middleware pour capturer le contexte
└── migrations/         # Migrations de base de données
```

## Installation

### 1. Configuration dans settings.py

```python
LOCAL_APPS = [
    'core.apps.CoreConfig',
    'activity_log.apps.ActivityLogConfig',  # Système de suivi d'activité
    'accounts',
    'academic',
    'finance',
    'communication',
]

MIDDLEWARE = [
    # ... autres middlewares
    "activity_log.middleware.ActivityTrackingMiddleware",  # Après AuthenticationMiddleware
]
```

### 2. Configuration des URLs

Dans `core/urls.py` :

```python
urlpatterns = [
    # ... autres URLs
    path('activity-logs/', include('activity_log.urls')),
]
```

### 3. Migrations

```bash
python manage.py migrate activity_log
```

## Utilisation

### Tracking Automatique

Le tracking est automatique pour :
- Grades (notes) : via signaux sur le modèle `Grade`
- Invoices (factures) : via signaux sur le modèle `Invoice`
- Payments (paiements) : via signaux sur le modèle `Payment`
- Connexions/déconnexions : via signaux Django `user_logged_in` et `user_logged_out`

### Tracking Manuel

```python
from activity_log.models import log_activity

log_activity(
    user=request.user,
    action_type='DOCUMENT_CREATE',
    description='Document ajouté : contrat-2024.pdf',
    content_type='Document',
    object_id=document.id,
    object_repr=str(document),
    new_values={'filename': 'contrat-2024.pdf', 'size': 1024},
    request=request
)
```

### Consultation des Logs

**Interface Web :**
- Liste complète : `http://localhost:8000/activity-logs/`
- Détails d'un log : `http://localhost:8000/activity-logs/<id>/`
- Logs d'un utilisateur : `http://localhost:8000/activity-logs/user/<user_id>/`

**Interface Admin :**
- `http://localhost:8000/admin/activity_log/activitylog/`

**Par code :**
```python
from activity_log.models import ActivityLog

# Tous les logs d'aujourd'hui
today_logs = ActivityLog.objects.filter(timestamp__date=timezone.now().date())

# Logs d'un utilisateur
user_logs = ActivityLog.objects.filter(user=user)

# Logs d'un type d'action
grade_creates = ActivityLog.objects.filter(action_type='GRADE_CREATE')

# Logs avec changements
logs_with_changes = ActivityLog.objects.exclude(old_values__isnull=True)
```

## Types d'Actions

### Notes (GRADE)
- `GRADE_CREATE` : Note créée
- `GRADE_UPDATE` : Note modifiée
- `GRADE_DELETE` : Note supprimée

### Factures (INVOICE)
- `INVOICE_CREATE` : Facture créée
- `INVOICE_UPDATE` : Facture modifiée
- `INVOICE_DELETE` : Facture supprimée
- `INVOICE_SEND` : Facture envoyée
- `INVOICE_CANCEL` : Facture annulée

### Paiements (PAYMENT)
- `PAYMENT_CREATE` : Paiement créé
- `PAYMENT_UPDATE` : Paiement modifié
- `PAYMENT_DELETE` : Paiement supprimé
- `PAYMENT_APPROVE` : Paiement approuvé
- `PAYMENT_REJECT` : Paiement rejeté

### Présences (ATTENDANCE)
- `ATTENDANCE_CREATE` : Présence enregistrée
- `ATTENDANCE_UPDATE` : Présence modifiée
- `ATTENDANCE_DELETE` : Présence supprimée

### Documents (DOCUMENT)
- `DOCUMENT_CREATE` : Document ajouté
- `DOCUMENT_UPDATE` : Document modifié
- `DOCUMENT_DELETE` : Document supprimé

### Sessions (SESSION)
- `SESSION_CREATE` : Session créée
- `SESSION_UPDATE` : Session modifiée
- `SESSION_DELETE` : Session supprimée

### Utilisateurs (USER)
- `USER_CREATE` : Utilisateur créé
- `USER_UPDATE` : Utilisateur modifié
- `USER_DELETE` : Utilisateur supprimé
- `USER_LOGIN` : Connexion
- `USER_LOGOUT` : Déconnexion

## Modèle ActivityLog

### Champs

- `user` : L'utilisateur qui a effectué l'action
- `action_type` : Type d'action (choix parmi ACTION_TYPES)
- `timestamp` : Date et heure de l'action
- `description` : Description détaillée
- `content_type` : Type d'objet concerné (ex: "Grade", "Invoice")
- `object_id` : ID de l'objet concerné
- `object_repr` : Représentation textuelle de l'objet
- `old_values` : Valeurs avant modification (JSON)
- `new_values` : Valeurs après modification (JSON)
- `ip_address` : Adresse IP de l'utilisateur
- `user_agent` : Navigateur utilisé

### Propriétés

- `action_category` : Catégorie (GRADE, INVOICE, PAYMENT, etc.)
- `action_verb` : Verbe (CREATE, UPDATE, DELETE, etc.)
- `icon_class` : Classe d'icône Material Icons
- `color_class` : Classes de couleur Tailwind CSS

### Méthodes

- `get_changes()` : Retourne un dictionnaire des changements (avant/après)

## Vues

### activity_log_list

Liste paginée des logs avec :
- Filtres : recherche, type d'action, utilisateur, période, catégorie
- Statistiques : total, aujourd'hui, cette semaine, ce mois
- Répartition par catégorie
- Top 10 des utilisateurs les plus actifs

### activity_log_detail

Détails d'un log spécifique avec :
- Informations complètes
- Tableau des changements (avant/après)
- Logs liés (même objet)
- Métadonnées (IP, user agent)

### user_activity_log

Historique d'activité d'un utilisateur avec :
- Statistiques personnelles
- Répartition par type d'action
- Liste paginée de ses activités

## Sécurité

- **Lecture seule** : Les logs ne peuvent pas être modifiés ou supprimés via l'interface
- **Permission admin** : Toutes les vues nécessitent `@admin_required`
- **Traçabilité** : Capture de l'IP et du user agent
- **Intégrité** : Signaux automatiques, pas de manipulation manuelle possible

## Performances

- **Indexes** : Sur timestamp, user, action_type, content_type+object_id
- **Pagination** : 25 logs par page
- **Select related** : Optimisation des requêtes pour éviter N+1

## Extensions Futures

Pour ajouter le tracking sur un nouveau modèle :

```python
# Dans activity_log/signals.py

from django.db.models.signals import post_save, pre_save, post_delete
from myapp.models import MyModel

_mymodel_cache = {}

@receiver(pre_save, sender=MyModel)
def mymodel_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            _mymodel_cache[instance.pk] = MyModel.objects.get(pk=instance.pk)
        except MyModel.DoesNotExist:
            pass

@receiver(post_save, sender=MyModel)
def mymodel_post_save(sender, instance, created, **kwargs):
    from activity_log.utils import get_current_user, get_current_request
    
    user = get_current_user()
    request = get_current_request()
    
    if created:
        log_activity(
            user=user,
            action_type='MYMODEL_CREATE',
            description=f'MyModel créé : {instance}',
            content_type='MyModel',
            object_id=instance.id,
            object_repr=str(instance),
            new_values={
                'field1': instance.field1,
                'field2': instance.field2,
            },
            request=request
        )
    else:
        old_instance = _mymodel_cache.pop(instance.pk, None)
        if old_instance:
            log_activity(
                user=user,
                action_type='MYMODEL_UPDATE',
                description=f'MyModel modifié : {instance}',
                content_type='MyModel',
                object_id=instance.id,
                object_repr=str(instance),
                old_values={
                    'field1': old_instance.field1,
                    'field2': old_instance.field2,
                },
                new_values={
                    'field1': instance.field1,
                    'field2': instance.field2,
                },
                request=request
            )

@receiver(post_delete, sender=MyModel)
def mymodel_post_delete(sender, instance, **kwargs):
    from activity_log.utils import get_current_user, get_current_request
    
    user = get_current_user()
    request = get_current_request()
    
    log_activity(
        user=user,
        action_type='MYMODEL_DELETE',
        description=f'MyModel supprimé : {instance}',
        content_type='MyModel',
        object_id=instance.id,
        object_repr=str(instance),
        old_values={
            'field1': instance.field1,
            'field2': instance.field2,
        },
        request=request
    )
```

N'oubliez pas d'ajouter les nouveaux types d'actions dans `ActivityLog.ACTION_TYPES` !

## Migration depuis core

Cette application a été migrée depuis `core` vers une application dédiée pour :
- Meilleure séparation des préoccupations
- Réutilisabilité
- Maintenance facilitée
- Organisation plus claire du code

Les données existantes ont été préservées via les migrations Django.
