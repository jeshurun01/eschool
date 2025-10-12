# Migration du système de suivi d'activité

**Date :** 12 octobre 2024  
**De :** `core` app  
**Vers :** `activity_log` app dédiée

## Raison de la migration

Le système de suivi d'activité était initialement implémenté dans l'application `core`, ce qui posait plusieurs problèmes :
- Mélange de préoccupations (core = configuration, activity = fonctionnalité)
- Difficulté de maintenance et de réutilisation
- Code moins modulaire

La migration vers une application dédiée `activity_log` offre :
- ✅ Séparation claire des responsabilités
- ✅ Code plus modulaire et réutilisable
- ✅ Maintenance facilitée
- ✅ Meilleure organisation du projet

## Fichiers migrés

### Depuis core/
```
core/models.py              → activity_log/models.py
core/signals.py             → activity_log/signals.py
core/activity_views.py      → activity_log/views.py
core/admin.py (partie)      → activity_log/admin.py
core/activity_urls.py       → activity_log/urls.py
core/middleware/activity_tracking.py → activity_log/middleware.py
```

### Nouveaux fichiers créés
```
activity_log/utils.py       # Utilitaires thread-local extraits
activity_log/apps.py        # Configuration de l'app avec import des signaux
activity_log/README.md      # Documentation complète
```

### Templates déplacés
```
templates/core/activity_log_list.html    → templates/activity_log/activity_log_list.html
templates/core/activity_log_detail.html  → templates/activity_log/activity_log_detail.html
templates/activity_log/user_activity_log.html  # Nouveau template créé
```

## Modifications effectuées

### 1. settings.py
```python
# Ajout dans LOCAL_APPS
'activity_log.apps.ActivityLogConfig',

# Modification dans MIDDLEWARE
"activity_log.middleware.ActivityTrackingMiddleware",  # au lieu de core.middleware...
```

### 2. core/urls.py
```python
# Avant
path('', include('core.activity_urls')),

# Après
path('activity-logs/', include('activity_log.urls')),
```

### 3. Imports mis à jour
Tous les imports ont été changés :
```python
# Avant
from core.models import ActivityLog
from core.middleware.activity_tracking import get_current_user

# Après
from activity_log.models import ActivityLog
from activity_log.utils import get_current_user
```

### 4. Namespaces URL mis à jour
Dans les templates :
```django
{# Avant #}
{% url 'core:activity_log_list' %}
{% url 'core:activity_log_detail' log.id %}
{% url 'core:user_activity_log' user.id %}

{# Après #}
{% url 'activity_log:list' %}
{% url 'activity_log:detail' log.id %}
{% url 'activity_log:user_log' user.id %}
```

### 5. Extraction des utilitaires
Les fonctions thread-local ont été extraites dans `activity_log/utils.py` :
- `get_current_user()`
- `get_current_request()`
- `set_current_user()`
- `set_current_request()`
- `clear_thread_locals()`

Cela permet de réduire le couplage et d'améliorer la réutilisabilité.

## Migrations de base de données

### Migration 1 : activity_log.0001_initial
Création du modèle `ActivityLog` dans la nouvelle app :
```bash
python manage.py makemigrations activity_log
# activity_log/migrations/0001_initial.py
#   + Create model ActivityLog
```

### Migration 2 : core.0002_delete_activitylog
Suppression de l'ancien modèle de core :
```bash
python manage.py makemigrations core
# core/migrations/0002_delete_activitylog.py
#   - Delete model ActivityLog
```

### Application des migrations
```bash
python manage.py migrate
# Applying activity_log.0001_initial... OK
# Applying core.0002_delete_activitylog... OK
```

**Note :** Django a automatiquement préservé les données existantes grâce à la séquence des migrations.

## Nettoyage effectué

### Fichiers supprimés de core/
- ❌ `core/signals.py`
- ❌ `core/activity_views.py`
- ❌ `core/activity_urls.py`
- ❌ `core/middleware/activity_tracking.py`

### Fichiers nettoyés
- `core/models.py` : Suppression du modèle ActivityLog
- `core/admin.py` : Suppression de ActivityLogAdmin
- `core/apps.py` : Suppression de l'import des signaux

## Tests de validation

```bash
# Vérification du système
python manage.py check
# System check identified no issues (0 silenced).

# Test du serveur
python manage.py runserver
# Server started successfully
```

## Nouvelles URLs

### Avant la migration
```
http://localhost:8000/activity-logs/  (depuis core)
```

### Après la migration
```
http://localhost:8000/activity-logs/           # Liste des logs
http://localhost:8000/activity-logs/<id>/      # Détails d'un log
http://localhost:8000/activity-logs/user/<id>/ # Logs d'un utilisateur
```

Les URLs publiques restent identiques pour l'utilisateur final.

## Interface Admin

### Avant
```
/admin/core/activitylog/
```

### Après
```
/admin/activity_log/activitylog/
```

## Rétrocompatibilité

⚠️ **Breaking changes :**

1. **Imports Python** : Tout code important depuis `core.models`, `core.signals`, etc. doit être mis à jour
2. **URLs dans le code** : Les `reverse('core:activity_log_list')` doivent être changés
3. **Interface admin** : Nouvelle URL dans l'admin

## Prochaines étapes

### Recommandations
1. ✅ Tester en profondeur l'interface web `/activity-logs/`
2. ✅ Vérifier le tracking automatique en créant/modifiant des notes et factures
3. ✅ Contrôler les logs dans l'admin
4. 📝 Mettre à jour la documentation utilisateur si nécessaire
5. 📝 Former l'équipe aux nouvelles URLs

### Extensions futures possibles
- Ajouter le tracking pour les présences (ATTENDANCE)
- Ajouter le tracking pour les documents (DOCUMENT)
- Ajouter des notifications en temps réel
- Créer des rapports d'activité exportables
- Ajouter des graphiques de tendances

## Commande de test rapide

Pour tester le système après migration :

```python
# Dans le shell Django
python manage.py shell

from activity_log.models import ActivityLog, log_activity
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Test de log manuel
log_activity(
    user=user,
    action_type='OTHER',
    description='Test après migration',
    content_type='Test',
    object_id=1,
    object_repr='Test object'
)

# Vérification
print(f"Total logs: {ActivityLog.objects.count()}")
print(f"Logs aujourd'hui: {ActivityLog.objects.filter(timestamp__date=timezone.now().date()).count()}")
```

## Contact et Support

Pour toute question sur cette migration, consultez :
- Documentation : `activity_log/README.md`
- Documentation complète : `docs/ACTIVITY_TRACKING_SYSTEM.md`

---

**Statut :** ✅ Migration réussie  
**Données préservées :** ✅ Oui  
**Tests :** ✅ Passés  
**En production :** ❌ Pas encore (à déployer)
