# Correction de la page de détail d'un élève pour les parents

## Problème identifié

La vue `parent_child_detail` affichait des données simulées/fictives au lieu des vraies données de l'élève :

1. **Événements simulés** : Les prochains examens et devoirs étaient hardcodés avec des titres fictifs ("Examen de Mathématiques", "Devoir de Français")
2. **Statistiques académiques incomplètes** : Manquaient le rang en classe, le nombre de matières, la tendance des notes
3. **Incohérence template/vue** : Le template utilisait `academic_stats.average_grade` mais la vue fournissait `average_grade` séparément
4. **Attributs Student incorrects** : Le template utilisait `child.first_name` au lieu de `child.user.first_name`

## Corrections apportées

### 1. Statistiques académiques complètes (`accounts/views.py`, ligne ~2764-2823)

**Ajouté** :
- Calcul du rang en classe (basé sur les moyennes de tous les élèves)
- Nombre de matières dans lesquelles l'élève a des notes
- Tendance des notes (comparaison des 5 dernières notes vs 5 précédentes)
- Description de la tendance ("Les notes progressent", "diminuent", "restent stables")
- Notes moyennes par matière avec nombre de notes

**Code** :
```python
academic_stats = {
    'average_grade': round(average_grade, 2) if average_grade else 0,
    'class_rank': class_rank,                # Rang en classe (1er, 2ème, etc.)
    'class_size': class_size,                # Nombre total d'élèves
    'subject_count': grades_by_subject.count(),  # Nombre de matières
    'trend': trend,                          # 'up', 'down', ou 'stable'
    'trend_description': trend_description,   # Description textuelle
    'grades_by_subject': grades_by_subject,  # QuerySet avec avg_score et count
}
```

### 2. Événements réels à partir des documents (`accounts/views.py`, ligne ~2868-2904)

**Remplacé** :
```python
# AVANT (données simulées)
upcoming_events = [
    {'type': 'exam', 'title': 'Examen de Mathématiques', ...},
    {'type': 'assignment', 'title': 'Devoir de Français', ...}
]
```

**Par** :
```python
# APRÈS (données réelles)
upcoming_docs = Document.objects.filter(
    classroom=child.current_class,
    access_date__gte=today,
    is_public=True
).select_related('subject', 'teacher').order_by('access_date')[:10]

for doc in upcoming_docs:
    upcoming_events.append({
        'type': event_type,       # 'exam' ou 'assignment' selon doc.document_type
        'title': doc.title,       # Vrai titre du document
        'subject': doc.subject.name,
        'date': doc.access_date,
        'importance': importance,  # 'high', 'medium', 'low'
        'document_id': doc.pk,
    })
```

### 3. Corrections du template (`templates/accounts/parent_child_detail.html`)

#### Attributs de l'élève
```html
<!-- AVANT -->
{{ child.first_name }} {{ child.last_name }}
{{ child.classroom.name }}

<!-- APRÈS -->
{{ child.user.first_name }} {{ child.user.last_name }}
{{ child.current_class.name }} - {{ child.current_class.level.name }}
```

#### Statistiques académiques
```html
<!-- AVANT -->
{{ average_grade }}
(pas de rang, pas de tendance)

<!-- APRÈS -->
{{ academic_stats.average_grade }}
{{ academic_stats.class_rank }} / {{ academic_stats.class_size }}
{{ academic_stats.trend_description }}
```

#### Prochaines échéances
```html
<!-- AVANT -->
{% for assignment in upcoming_assignments %}
    {{ assignment.title }}
    {{ assignment.subject.name }}

<!-- APRÈS -->
{% for event in upcoming_events %}
    {{ event.title }}
    {{ event.subject }}
    {% if event.importance == 'high' %}
        <span class="bg-red-100 text-red-800">Important</span>
    {% endif %}
```

#### Notes par matière
```html
<!-- AVANT -->
{% for subject, data in grades_by_subject.items %}
    {{ subject }}
    {{ data.average }}

<!-- APRÈS -->
{% for subject in academic_stats.grades_by_subject %}
    {{ subject.subject__name }}
    {{ subject.avg_score|floatformat:1 }}
    {{ subject.count }} note(s)
```

#### Assiduité
```html
<!-- AVANT -->
{{ attendance_stats.presence_rate }}%
{{ attendance_stats.present_days }}/{{ attendance_stats.total_days }} jours

{% for attendance in recent_attendance %}
    {{ attendance.date }}
    {{ attendance.subject.name }}
    {{ attendance.status }}

<!-- APRÈS -->
{{ attendance_rate }}%

{% for summary in recent_attendances %}
    {{ summary.date }}
    {{ summary.total_sessions }}
    {{ summary.present_sessions }}
    {{ summary.absent_sessions }}
    {{ summary.late_sessions }}
```

## Impact

### Avant
- ❌ Parents voyaient des données fictives
- ❌ Impossible de suivre la progression réelle
- ❌ Pas d'information sur le rang en classe
- ❌ Pas de vue des vrais devoirs à venir

### Après
- ✅ Toutes les données sont réelles
- ✅ Calcul automatique du rang en classe
- ✅ Tendance des notes visible
- ✅ Vrais documents/devoirs à venir affichés
- ✅ Statistiques d'assiduité précises

## Tests recommandés

1. **Test avec un élève ayant des notes** :
   - Vérifier que le rang s'affiche correctement
   - Vérifier que la tendance est calculée ("progressent", "diminuent", "stables")
   - Vérifier que les notes par matière sont réelles

2. **Test avec un élève ayant des documents à venir** :
   - Créer un document avec `access_date` future
   - Vérifier qu'il apparaît dans "Prochaines échéances"
   - Vérifier que le type (exam/assignment) et l'importance sont corrects

3. **Test avec un élève n'ayant pas de classe** :
   - Vérifier que la page ne crash pas
   - Vérifier le message "Non assigné à une classe"

4. **Test de performance** :
   - Classe avec beaucoup d'élèves (calcul du rang)
   - Vérifier que les requêtes sont optimisées avec `select_related`

## URL de test

```
/accounts/parent/child/<student_id>/
```

Exemple : `/accounts/parent/child/483/`

## Fichiers modifiés

- `accounts/views.py` : Fonction `parent_child_detail` (lignes 2741-2925)
- `templates/accounts/parent_child_detail.html` : Corrections des variables template
