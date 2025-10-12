# Remplacement des Événements Hardcodés par des Annonces Réelles

**Date:** 12 octobre 2025  
**Fichiers modifiés:** 
- `accounts/views.py` (parent_dashboard)
- `templates/accounts/parent_dashboard.html`

## Problème Identifié

La section "Événements à venir" du dashboard parent affichait **3 événements hardcodés** (simulés) :
```python
upcoming_events = [
    {'title': 'Réunion parents-enseignants', 'date': today + timedelta(days=7), ...},
    {'title': 'Remise des bulletins', 'date': today + timedelta(days=14), ...},
    {'title': 'Journée portes ouvertes', 'date': today + timedelta(days=21), ...}
]
```

**Problèmes :**
- Données fictives toujours affichées
- Impossibilité pour les admins de gérer les événements
- Pas de lien vers les détails de l'événement
- Informations pas à jour avec la réalité de l'école

## Solution Implémentée

Utilisation du système d'**annonces existant** avec le type `EVENT` pour gérer les événements.

### 1. Modification de la Vue (accounts/views.py)

**Avant (Lignes 938-959) :**
```python
# Événements à venir (simulés)
upcoming_events = [
    {
        'title': 'Réunion parents-enseignants',
        'date': today + timedelta(days=7),
        'time': '14:00',
        'type': 'meeting'
    },
    # ... autres événements hardcodés
]
```

**Après (Lignes 938-963) :**
```python
# Événements à venir - Utiliser les annonces de type EVENT
from communication.models import Announcement
upcoming_events_announcements = Announcement.objects.filter(
    type='EVENT',
    audience__in=['ALL', 'PARENTS'],
    is_published=True,
    publish_date__lte=timezone.now()
).filter(
    Q(expiry_date__gte=timezone.now()) | Q(expiry_date__isnull=True)
).order_by('publish_date')[:5]

# Formater les événements pour le template
upcoming_events = []
for event in upcoming_events_announcements:
    upcoming_events.append({
        'id': event.id,
        'title': event.title,
        'date': event.publish_date.date(),
        'time': event.publish_date.strftime('%H:%M'),
        'type': 'event',
        'description': event.content[:100] if len(event.content) > 100 else event.content,
    })
```

**Logique de filtrage :**
1. **Type** : Uniquement les annonces de type `EVENT`
2. **Audience** : Ciblées pour `ALL` ou `PARENTS`
3. **Publiées** : `is_published=True`
4. **Date de publication** : Déjà publiées (`publish_date__lte=now`)
5. **Non expirées** : `expiry_date >= now` OU `expiry_date IS NULL`
6. **Tri** : Par date de publication (les plus proches en premier)
7. **Limite** : Maximum 5 événements

### 2. Modification du Template (parent_dashboard.html)

**Améliorations visuelles :**

```html
<!-- Avant : Carte statique -->
<div class="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
    <div class="w-6 h-6 bg-blue-500 rounded-full">...</div>
    <div class="flex-1 min-w-0">
        <p>{{ event.title }}</p>
        <p>{{ event.date|date:"d/m/Y" }} à {{ event.time }}</p>
    </div>
</div>

<!-- Après : Carte cliquable avec détails -->
<a href="{% url 'communication:announcement_detail' event.id %}" 
   class="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg hover:bg-blue-100 
          hover:border hover:border-blue-300 transition-all duration-200 cursor-pointer">
    <div class="w-8 h-8 bg-blue-500 rounded-full">
        <span class="material-icons text-white">event</span>
    </div>
    <div class="flex-1 min-w-0">
        <p class="text-sm font-medium">{{ event.title }}</p>
        <p class="text-xs text-gray-500">{{ event.date|date:"d/m/Y" }} à {{ event.time }}</p>
        {% if event.description %}
            <p class="text-xs text-gray-600">{{ event.description }}</p>
        {% endif %}
    </div>
    <span class="material-icons text-blue-600">arrow_forward</span>
</a>
```

**Changements :**
1. **Titre avec icône** : Ajout icône `event` à côté du titre de section
2. **Carte cliquable** : `<div>` → `<a>` avec lien vers détails
3. **Icône améliorée** : Material icon `event` au lieu de point blanc
4. **Description** : Affichage d'un extrait du contenu (100 caractères max)
5. **Flèche d'action** : Icône `arrow_forward` à droite
6. **Hover effect** : Fond + bordure change au survol
7. **Message vide amélioré** : Grande icône + message si aucun événement

## Modèle Announcement Utilisé

```python
class Announcement(models.Model):
    TYPE_CHOICES = [
        ('GENERAL', 'Générale'),
        ('ACADEMIC', 'Académique'),
        ('EVENT', 'Événement'),      # ← Type utilisé pour événements
        ('URGENT', 'Urgent'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    AUDIENCE_CHOICES = [
        ('ALL', 'Tous'),
        ('STUDENTS', 'Élèves'),
        ('PARENTS', 'Parents'),       # ← Audience ciblée
        ('TEACHERS', 'Enseignants'),
        ('STAFF', 'Personnel'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(choices=TYPE_CHOICES)
    audience = models.CharField(choices=AUDIENCE_CHOICES)
    
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField()      # Date de l'événement
    expiry_date = models.DateTimeField()       # Fin de l'événement (optionnel)
    
    is_pinned = models.BooleanField(default=False)
    priority = models.IntegerField(default=1)
```

## Gestion des Événements par les Admins

### Créer un Événement

```python
# Dans Django Admin ou via une vue dédiée
event = Announcement.objects.create(
    title="Réunion parents-enseignants",
    content="Réunion importante avec tous les enseignants pour discuter des progrès de vos enfants. Présence obligatoire.",
    type='EVENT',
    audience='PARENTS',
    author=request.user,
    is_published=True,
    publish_date=timezone.datetime(2025, 10, 20, 14, 0),  # 20 oct 2025 à 14h
    expiry_date=timezone.datetime(2025, 10, 20, 17, 0),   # Fin à 17h
    priority=2  # Élevée
)
```

### Types d'Événements Possibles

1. **Réunions parents-enseignants**
   - `type='EVENT'`, `audience='PARENTS'`
   - Date précise avec heure de début et fin

2. **Remise des bulletins**
   - `type='EVENT'`, `audience='ALL'` ou `'PARENTS'`
   - Date de disponibilité

3. **Journées portes ouvertes**
   - `type='EVENT'`, `audience='ALL'`
   - Événement public

4. **Examens importants**
   - `type='EVENT'`, `audience='STUDENTS'` ou `'PARENTS'`
   - Dates des examens

5. **Activités parascolaires**
   - `type='EVENT'`, `audience='ALL'`
   - Sorties, spectacles, sports

6. **Vacances scolaires**
   - `type='EVENT'`, `audience='ALL'`
   - Dates de début et fin

## Avantages de la Solution

### 1. Gestion Centralisée
- ✅ Tous les événements gérés dans Django Admin
- ✅ Création, modification, suppression facile
- ✅ Pas besoin de modifier le code pour ajouter un événement

### 2. Filtrage Intelligent
- ✅ Affichage automatique des événements pertinents
- ✅ Gestion des dates d'expiration
- ✅ Ciblage par audience (parents, étudiants, tous)

### 3. Détails Complets
- ✅ Clic sur événement → Page de détail complète
- ✅ Contenu riche (description longue possible)
- ✅ Suivi de lecture automatique

### 4. Flexibilité
- ✅ Épingler les événements importants (`is_pinned`)
- ✅ Définir la priorité (normale, élevée, urgente)
- ✅ Cibler des classes ou niveaux spécifiques
- ✅ Envoyer notifications email/SMS

### 5. Cohérence
- ✅ Même système que les annonces
- ✅ Pas de duplication de code
- ✅ Interface admin familière

## Exemples d'Utilisation

### Exemple 1 : Créer un Événement via Django Admin

```
1. Se connecter à Django Admin
2. Communication → Announcements → Add Announcement
3. Remplir :
   - Title: "Réunion parents-enseignants"
   - Content: "Réunion importante pour discuter des progrès..."
   - Type: EVENT
   - Audience: PARENTS
   - Is published: ✓
   - Publish date: 20/10/2025 14:00
   - Expiry date: 20/10/2025 17:00
4. Save
5. L'événement apparaît automatiquement dans le dashboard parent
```

### Exemple 2 : Événement pour Classe Spécifique

```python
event = Announcement.objects.create(
    title="Sortie scolaire - Classe CM2",
    content="Visite du musée national. Départ à 8h, retour à 16h.",
    type='EVENT',
    audience='CLASS',
    author=request.user,
    is_published=True,
    publish_date=timezone.datetime(2025, 10, 25, 8, 0),
)
# Cibler la classe
event.target_classes.add(cm2_class)
```

### Exemple 3 : Événement Récurrent

```python
# Créer plusieurs événements pour une série
for week in range(4):
    Announcement.objects.create(
        title=f"Cours de rattrapage - Semaine {week+1}",
        content="Cours de mathématiques tous les mercredis",
        type='EVENT',
        audience='STUDENTS',
        publish_date=timezone.datetime(2025, 10, 7 + (week*7), 15, 0),
        is_published=True,
    )
```

## Requête SQL Générée

```sql
SELECT * FROM communication_announcement
WHERE type = 'EVENT'
  AND audience IN ('ALL', 'PARENTS')
  AND is_published = TRUE
  AND publish_date <= NOW()
  AND (expiry_date >= NOW() OR expiry_date IS NULL)
ORDER BY publish_date ASC
LIMIT 5;
```

**Performance :**
- Index sur `type`, `audience`, `is_published`, `publish_date`
- Requête simple et rapide
- Limite de 5 résultats

## Migration des Données Existantes

Si des événements étaient stockés ailleurs, script de migration :

```python
# Script de migration
from communication.models import Announcement
from django.utils import timezone

events_to_migrate = [
    {
        'title': 'Réunion parents-enseignants',
        'date': timezone.datetime(2025, 10, 19, 14, 0),
        'content': 'Réunion avec tous les enseignants...'
    },
    # ... autres événements
]

admin_user = User.objects.filter(role='ADMIN').first()

for event_data in events_to_migrate:
    Announcement.objects.create(
        title=event_data['title'],
        content=event_data['content'],
        type='EVENT',
        audience='PARENTS',
        author=admin_user,
        is_published=True,
        publish_date=event_data['date'],
    )
```

## Tests de Vérification

### Test 1 : Créer et Afficher un Événement
```python
# 1. Créer un événement
event = Announcement.objects.create(
    title="Test Événement",
    content="Ceci est un test",
    type='EVENT',
    audience='PARENTS',
    author=admin_user,
    is_published=True,
    publish_date=timezone.now() + timedelta(days=1),
)

# 2. Se connecter en tant que parent
# 3. Aller sur /accounts/
# 4. Section "Événements à venir"
# ✓ L'événement doit apparaître
# ✓ Cliquer → Redirige vers détails
```

### Test 2 : Vérifier le Filtrage par Audience
```python
# Créer événement pour étudiants uniquement
student_event = Announcement.objects.create(
    title="Événement Étudiants Seulement",
    type='EVENT',
    audience='STUDENTS',  # Pas PARENTS
    is_published=True,
    publish_date=timezone.now() + timedelta(days=1),
)

# Se connecter en tant que parent
# ✓ Ne doit PAS apparaître dans dashboard parent
```

### Test 3 : Vérifier Expiration
```python
# Créer événement expiré
expired_event = Announcement.objects.create(
    title="Événement Passé",
    type='EVENT',
    audience='PARENTS',
    is_published=True,
    publish_date=timezone.now() - timedelta(days=10),
    expiry_date=timezone.now() - timedelta(days=1),  # Expiré hier
)

# Se connecter en tant que parent
# ✓ Ne doit PAS apparaître (expiré)
```

### Test 4 : Ordre des Événements
```python
# Créer 3 événements à différentes dates
for i in range(3):
    Announcement.objects.create(
        title=f"Événement {i+1}",
        type='EVENT',
        audience='PARENTS',
        is_published=True,
        publish_date=timezone.now() + timedelta(days=i*7),
    )

# Se connecter en tant que parent
# ✓ Les événements doivent être triés par date (le plus proche en premier)
```

## Améliorations Futures

### 1. Compteur d'Événements à Venir
```python
# Dans la vue
upcoming_count = upcoming_events_announcements.count()
context['upcoming_events_count'] = upcoming_count

# Dans le template
<h3>Événements à venir ({{ upcoming_events_count }})</h3>
```

### 2. Filtrage par Type d'Événement
```python
# Ajouter sous-catégories
EVENT_SUBTYPES = [
    ('MEETING', 'Réunion'),
    ('EXAM', 'Examen'),
    ('ACTIVITY', 'Activité'),
    ('VACATION', 'Vacances'),
]
```

### 3. Calendrier Visuel
```html
<!-- Affichage en calendrier au lieu de liste -->
<div id="calendar"></div>
<script>
    // Utiliser FullCalendar.js
    var events = {{ upcoming_events|safe }};
    $('#calendar').fullCalendar({events: events});
</script>
```

### 4. Rappels Automatiques
```python
# Envoyer email/SMS X jours avant événement
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self):
        tomorrow_events = Announcement.objects.filter(
            type='EVENT',
            publish_date__date=timezone.now().date() + timedelta(days=1),
            send_email=True
        )
        for event in tomorrow_events:
            # Envoyer email de rappel
            send_event_reminder(event)
```

### 5. Inscription aux Événements
```python
# Modèle pour suivre les participants
class EventRegistration(models.Model):
    event = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=[('GOING', 'Présent'), ('MAYBE', 'Peut-être'), ('NOT_GOING', 'Absent')])
```

## Fichiers Modifiés

- `accounts/views.py` : Fonction `parent_dashboard()` (lignes 938-963)
- `templates/accounts/parent_dashboard.html` : Section événements (lignes 328-365)

## Documentation Associée

- `communication/models.py` : Modèle `Announcement`
- `communication/admin.py` : Interface d'administration
- Django Admin : Gestion des événements
