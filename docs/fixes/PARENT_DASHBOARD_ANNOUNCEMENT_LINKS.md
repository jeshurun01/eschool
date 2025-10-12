# Ajout de Liens Cliquables sur les Annonces - Dashboard Parent

**Date:** 12 octobre 2025  
**Fichier modifié:** `templates/accounts/parent_dashboard.html`  
**Lignes modifiées:** 366-402

## Problème Identifié

Dans la section "Annonces importantes" du dashboard parent, les annonces étaient affichées mais **non cliquables** :
- Parents voyaient le titre et un extrait du contenu (20 premiers mots)
- Pas de moyen de lire l'annonce complète
- Pas d'indication que l'annonce était cliquable

### Code Avant

```html
<div class="border border-gray-200 rounded-lg p-4 hover:bg-purple-50 transition-colors duration-200">
    <div class="flex items-start">
        <!-- Icône et contenu -->
        <h4 class="font-medium text-gray-900 mr-3">{{ announcement.title }}</h4>
        <p class="text-gray-600 text-sm mb-2">{{ announcement.content|truncatewords:20 }}</p>
        <div class="text-xs text-gray-500 flex items-center">
            <span class="material-icons mr-1">schedule</span>
            {{ announcement.publish_date|date:"d/m/Y" }}
        </div>
    </div>
</div>
```

**Problème :**
- Élément `<div>` statique, non cliquable
- Contenu tronqué à 20 mots sans moyen de voir la suite
- Pas d'indication visuelle de lien possible

## Solution Implémentée

Transformation des annonces en **liens cliquables** vers la page de détail complète.

### Code Après

```html
<a href="{% url 'communication:announcement_detail' announcement.id %}" 
   class="block border border-gray-200 rounded-lg p-4 hover:bg-purple-50 hover:border-purple-300 transition-all duration-200 cursor-pointer">
    <div class="flex items-start">
        <!-- Icône et contenu -->
        <h4 class="font-medium text-gray-900 mr-3">{{ announcement.title }}</h4>
        <p class="text-gray-600 text-sm mb-2">{{ announcement.content|truncatewords:20 }}</p>
        <div class="text-xs text-gray-500 flex items-center justify-between">
            <div class="flex items-center">
                <span class="material-icons mr-1">schedule</span>
                {{ announcement.publish_date|date:"d/m/Y" }}
            </div>
            <span class="text-purple-600 font-medium flex items-center">
                Voir détails
                <span class="material-icons ml-1">arrow_forward</span>
            </span>
        </div>
    </div>
</a>
```

**Changements :**
1. **`<div>` → `<a>`** : Élément cliquable avec lien vers détails
2. **URL** : `{% url 'communication:announcement_detail' announcement.id %}`
3. **Classes CSS ajoutées** :
   - `block` : Lien prend toute la largeur
   - `cursor-pointer` : Curseur main au survol
   - `hover:border-purple-300` : Bordure change au survol
   - `transition-all` : Animation fluide
4. **Indicateur visuel ajouté** :
   - Texte "Voir détails" avec icône flèche
   - Couleur purple-600 pour indiquer l'action
   - Positionné en bas à droite

## Fonctionnalité de la Page de Détail

### Vue : `announcement_detail` (communication/views.py)

```python
def announcement_detail(request, announcement_id):
    """Détails d'une annonce"""
    announcement = get_object_or_404(Announcement, id=announcement_id, is_published=True)
    
    # Marquer comme lu automatiquement
    read_obj, created = AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    context = {
        'announcement': announcement,
        'is_read': not created,
    }
    
    return render(request, 'communication/announcement_detail.html', context)
```

**Fonctionnalités :**
- Affiche le contenu complet de l'annonce
- Marque automatiquement l'annonce comme lue
- Accessible à tous les utilisateurs connectés
- Pas de restriction RBAC spécifique

### URL Pattern

```python
# communication/urls.py
path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail')
```

**URL exemple :** `/communication/announcements/42/`

## Améliorations UX Apportées

### 1. Indicateurs Visuels

**Avant :**
- Carte statique
- Hover change le fond légèrement
- Aucune indication qu'on peut cliquer

**Après :**
- ✅ Carte entière cliquable
- ✅ Hover change fond + bordure (purple-300)
- ✅ Curseur devient main (pointer)
- ✅ Texte "Voir détails" + icône flèche
- ✅ Animation fluide (transition-all)

### 2. Expérience Utilisateur

**Parcours utilisateur :**
```
1. Parent voit annonce avec contenu tronqué (20 mots)
2. Survole l'annonce → Fond change + bordure colorée + curseur main
3. Voit "Voir détails →" en bas à droite
4. Clique n'importe où sur la carte
5. Redirigé vers page de détail complète
6. L'annonce est automatiquement marquée comme lue
```

### 3. Accessibilité

- ✅ **Lien sémantique** : Utilisation de `<a>` au lieu de JavaScript
- ✅ **Navigation clavier** : Tab pour naviguer, Enter pour ouvrir
- ✅ **Indication claire** : Texte "Voir détails" explicite
- ✅ **Zone cliquable large** : Toute la carte est cliquable
- ✅ **Feedback visuel** : Changements au survol

## Cohérence avec les Autres Sections

Cette amélioration aligne la section "Annonces importantes" avec d'autres éléments cliquables du dashboard :

### Cartes des Enfants
```html
<a href="{% url 'accounts:parent_child_detail' child_data.student.id %}" ...>
    <!-- Carte enfant cliquable -->
</a>
```

### Activités Récentes
```html
<a href="..." class="hover:bg-gray-50 cursor-pointer">
    <!-- Activité cliquable -->
</a>
```

### Annonces (maintenant)
```html
<a href="{% url 'communication:announcement_detail' announcement.id %}" ...>
    <!-- Annonce cliquable -->
</a>
```

**Principe de cohérence :** Tout élément avec détails disponibles est cliquable et indique visuellement cette possibilité.

## Détails Techniques

### Structure HTML

```html
<a href="..." class="block ...">                    <!-- Lien wrapper -->
    <div class="flex items-start">                  <!-- Container flex -->
        <div class="flex-shrink-0">                 <!-- Icône -->
            <div class="w-10 h-10 bg-purple-100 ...">
                <span class="material-icons ...">...</span>
            </div>
        </div>
        <div class="ml-4 flex-1">                   <!-- Contenu -->
            <div class="flex items-center mb-2">    <!-- Titre + badge -->
                <h4>{{ announcement.title }}</h4>
                <span class="badge">Urgent</span>
            </div>
            <p>{{ announcement.content|truncatewords:20 }}</p>
            <div class="flex items-center justify-between">  <!-- Footer -->
                <div>                               <!-- Date -->
                    <span class="material-icons">schedule</span>
                    {{ announcement.publish_date|date:"d/m/Y" }}
                </div>
                <span class="text-purple-600">      <!-- Indicateur -->
                    Voir détails
                    <span class="material-icons">arrow_forward</span>
                </span>
            </div>
        </div>
    </div>
</a>
```

### Classes CSS Utilisées

| Classe | Rôle |
|--------|------|
| `block` | Lien prend toute la largeur disponible |
| `border border-gray-200` | Bordure grise par défaut |
| `rounded-lg` | Coins arrondis |
| `p-4` | Padding interne |
| `hover:bg-purple-50` | Fond mauve clair au survol |
| `hover:border-purple-300` | Bordure mauve au survol |
| `transition-all` | Animation fluide de tous les changements |
| `duration-200` | Durée animation 200ms |
| `cursor-pointer` | Curseur main au survol |

### Layout Responsive

```
┌─────────────────────────────────────────────┐
│ [Icône] Titre de l'annonce    [Badge]       │
│         Description tronquée (20 mots)...   │
│         📅 12/10/2025    Voir détails →     │
└─────────────────────────────────────────────┘
      ↑ Toute la carte est cliquable ↑
```

## Tests de Vérification

### Test 1 : Clic sur Annonce
```
1. Se connecter en tant que parent
2. Aller sur /accounts/ (dashboard)
3. Section "Annonces importantes"
4. Cliquer n'importe où sur une annonce
   ✓ Redirection vers /communication/announcements/{id}/
   ✓ Page de détail complète affichée
   ✓ Annonce marquée comme lue
```

### Test 2 : Indicateurs Visuels
```
1. Survoler une annonce
   ✓ Fond change (blanc → purple-50)
   ✓ Bordure change (gray-200 → purple-300)
   ✓ Curseur devient main
   ✓ "Voir détails →" visible en bas à droite
```

### Test 3 : Navigation Clavier
```
1. Utiliser Tab pour naviguer
   ✓ Focus visible sur les annonces
2. Appuyer Enter sur une annonce focalisée
   ✓ Ouverture de la page de détail
```

### Test 4 : Vérifier Toutes les Annonces
```
1. Dashboard affiche 5 annonces maximum
2. Cliquer sur chaque annonce
   ✓ Toutes redirigent vers leur détail respectif
   ✓ URLs différentes : /announcements/1/, /announcements/2/, etc.
```

## Modèle Announcement

Pour référence, voici la structure du modèle :

```python
# communication/models.py
class Announcement(models.Model):
    TYPE_CHOICES = [
        ('INFO', 'Information'),
        ('EVENT', 'Événement'),
        ('URGENT', 'Urgent'),
        ('GENERAL', 'Général'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Basse'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Haute'),
    ]
    
    AUDIENCE_CHOICES = [
        ('ALL', 'Tous'),
        ('STUDENTS', 'Étudiants'),
        ('TEACHERS', 'Enseignants'),
        ('PARENTS', 'Parents'),
        ('STAFF', 'Personnel'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
```

## Impact sur la Base de Données

L'ouverture d'une annonce crée ou récupère un enregistrement `AnnouncementRead` :

```python
# Modèle AnnouncementRead
class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['announcement', 'user']
```

**Avantage :** Permet de tracker quelles annonces ont été lues par chaque utilisateur.

## Améliorations Futures Possibles

### 1. Badge "Non lu"
```html
{% if not announcement.is_read_by_user %}
    <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
        Nouveau
    </span>
{% endif %}
```

### 2. Compteur d'annonces non lues
```python
# Dans la vue parent_dashboard
unread_count = Announcement.objects.filter(
    audience__in=['ALL', 'PARENTS'],
    is_published=True
).exclude(
    announcementread__user=request.user
).count()

context['unread_announcements_count'] = unread_count
```

### 3. Prévisualisation au survol (tooltip)
```html
<div class="tooltip">
    <!-- Afficher plus de contenu au survol -->
</div>
```

### 4. Filtrage par Type
```html
<select name="type_filter">
    <option value="">Tous</option>
    <option value="URGENT">Urgent</option>
    <option value="EVENT">Événements</option>
    <option value="INFO">Informations</option>
</select>
```

## Fichiers Modifiés

- `templates/accounts/parent_dashboard.html` : Lignes 366-402

## Documentation Associée

- `communication/views.py` : Vue `announcement_detail`
- `communication/urls.py` : Route vers détails annonces
- `communication/models.py` : Modèles Announcement et AnnouncementRead

## Notes de Développement

**Important :** La vue `announcement_detail` ne vérifie pas si l'utilisateur fait partie de l'audience ciblée. Elle vérifie uniquement que l'annonce est publiée (`is_published=True`).

**Amélioration possible :**
```python
# Ajouter vérification d'audience
def announcement_detail(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id, is_published=True)
    
    # Vérifier que l'utilisateur fait partie de l'audience
    if announcement.audience == 'PARENTS' and request.user.role != 'PARENT':
        raise PermissionDenied
    # ... autres vérifications
```
