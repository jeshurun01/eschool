# Système de Suivi d'Activité - Documentation

## 📋 Vue d'ensemble

Le système de suivi d'activité (Activity Log) enregistre automatiquement toutes les actions importantes effectuées par les utilisateurs dans l'application eSchool.

## ✨ Fonctionnalités

### Actions trackées automatiquement :

1. **Notes (Grades)**
   - Création d'une note
   - Modification d'une note
   - Suppression d'une note

2. **Factures (Invoices)**
   - Création d'une facture
   - Modification d'une facture
   - Suppression d'une facture

3. **Paiements (Payments)**
   - Création d'un paiement
   - Modification d'un paiement
   - Suppression d'un paiement

4. **Connexion/Déconnexion**
   - Connexion utilisateur
   - Déconnexion utilisateur

## 🔧 Utilisation

### Tracking automatique (via signaux)

Le système utilise des signaux Django pour tracker automatiquement les modifications. Aucune action n'est requise de votre part pour les modèles `Grade`, `Invoice`, et `Payment`.

### Tracking manuel

Pour tracker d'autres actions, utilisez la fonction `log_activity` :

```python
from core.models import log_activity

# Exemple simple
log_activity(
    user=request.user,
    action_type='DOCUMENT_CREATE',
    description='Document "Cours de Math" ajouté',
    request=request
)

# Exemple avec détails complets
log_activity(
    user=request.user,
    action_type='SESSION_UPDATE',
    description='Session de Mathématiques modifiée',
    content_type='Session',
    object_id=session.id,
    object_repr=str(session),
    old_values={'date': '2025-10-10', 'duration': 60},
    new_values={'date': '2025-10-11', 'duration': 90},
    request=request
)
```

### Types d'actions disponibles

```python
# Notes
'GRADE_CREATE', 'GRADE_UPDATE', 'GRADE_DELETE'

# Finance - Factures
'INVOICE_CREATE', 'INVOICE_UPDATE', 'INVOICE_DELETE', 
'INVOICE_SEND', 'INVOICE_CANCEL'

# Finance - Paiements
'PAYMENT_CREATE', 'PAYMENT_UPDATE', 'PAYMENT_DELETE',
'PAYMENT_APPROVE', 'PAYMENT_REJECT'

# Présences
'ATTENDANCE_CREATE', 'ATTENDANCE_UPDATE', 'ATTENDANCE_DELETE'

# Documents
'DOCUMENT_CREATE', 'DOCUMENT_UPDATE', 'DOCUMENT_DELETE'

# Sessions
'SESSION_CREATE', 'SESSION_UPDATE', 'SESSION_DELETE'

# Utilisateurs
'USER_CREATE', 'USER_UPDATE', 'USER_DELETE',
'USER_LOGIN', 'USER_LOGOUT'
```

## 📊 Consultation des logs

### Interface Web

Accessible aux administrateurs :
- **Liste complète** : http://localhost:8000/activity-logs/
- **Détails d'un log** : http://localhost:8000/activity-logs/{log_id}/
- **Logs d'un utilisateur** : http://localhost:8000/activity-logs/user/{user_id}/

### Admin Django

Les logs sont également visibles dans l'interface d'administration Django :
- http://localhost:8000/admin/core/activitylog/

### Filtres disponibles

- Recherche par texte (description, utilisateur, objet)
- Filtrage par type d'action
- Filtrage par catégorie (GRADE, INVOICE, PAYMENT, etc.)
- Filtrage par utilisateur
- Filtrage par date (début/fin)

## 🎯 Informations enregistrées

Pour chaque action, le système enregistre :

1. **Qui** : Utilisateur ayant effectué l'action
2. **Quoi** : Type d'action et description détaillée
3. **Quand** : Date et heure précises
4. **Où** : Adresse IP et navigateur utilisé
5. **Détails** : 
   - Type d'objet modifié
   - ID de l'objet
   - Anciennes valeurs (avant modification)
   - Nouvelles valeurs (après modification)

## 📈 Statistiques

Le système fournit des statistiques :
- Nombre total d'activités
- Activités du jour
- Activités de la semaine
- Activités du mois
- Répartition par catégorie
- Top utilisateurs les plus actifs

## 🔒 Sécurité

- Les logs ne peuvent pas être modifiés (readonly)
- Les logs ne peuvent pas être supprimés via l'interface
- Seuls les administrateurs peuvent consulter les logs
- Les données sensibles sont stockées en JSON

## 🚀 Extension

### Ajouter un nouveau modèle à tracker

1. **Créer les signaux** dans `core/signals.py` :

```python
@receiver(pre_save, sender=MonModele)
def mon_modele_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = MonModele.objects.get(pk=instance.pk)
        except MonModele.DoesNotExist:
            instance._old_instance = None

@receiver(post_save, sender=MonModele)
def mon_modele_post_save(sender, instance, created, **kwargs):
    user = get_current_user()
    if not user or not user.is_authenticated:
        return
    
    if created:
        log_activity(
            user=user,
            action_type='MON_MODELE_CREATE',
            description=f"Mon modèle créé: {instance}",
            content_type='MonModele',
            object_id=instance.id,
            object_repr=str(instance),
            request=get_current_request()
        )
```

2. **Ajouter les types d'actions** dans `core/models.py` :

```python
ACTION_TYPES = [
    ...
    ('MON_MODELE_CREATE', 'Mon modèle créé'),
    ('MON_MODELE_UPDATE', 'Mon modèle modifié'),
    ('MON_MODELE_DELETE', 'Mon modèle supprimé'),
]
```

## 📝 Exemples d'utilisation

### Voir les dernières activités d'un enseignant

```python
from core.models import ActivityLog

teacher_logs = ActivityLog.objects.filter(
    user__teacher_profile__isnull=False,
    action_type__startswith='GRADE'
).order_by('-timestamp')[:10]
```

### Voir toutes les modifications d'une facture

```python
invoice_logs = ActivityLog.objects.filter(
    content_type='Invoice',
    object_id=invoice_id
).order_by('timestamp')
```

### Générer un rapport mensuel

```python
from django.utils import timezone
from datetime import timedelta

month_ago = timezone.now() - timedelta(days=30)
monthly_stats = ActivityLog.objects.filter(
    timestamp__gte=month_ago
).values('action_type').annotate(
    count=Count('id')
)
```

## 🐛 Dépannage

### Les logs ne sont pas créés

1. Vérifier que le middleware est activé dans `settings.py`
2. Vérifier que l'utilisateur est authentifié
3. Vérifier que les signaux sont importés dans `apps.py`

### Erreur "user is None"

- S'assurer que le middleware `ActivityTrackingMiddleware` est bien dans `MIDDLEWARE`
- Vérifier que la requête passe par le middleware

## 📚 Ressources

- Modèle : `core/models.py` - `ActivityLog`
- Signaux : `core/signals.py`
- Vues : `core/activity_views.py`
- Templates : `templates/core/activity_log_*.html`
- Admin : `core/admin.py`

---

**Version** : 1.0  
**Dernière mise à jour** : 12 octobre 2025
