# 🔧 Guide de Référence Rapide - Développeurs

## Date : Octobre 2025

---

## 🎯 Accès au Profil Étudiant

### ✅ CORRECT
```python
# Dans les vues
student = request.user.student_profile

# Vérifier l'existence
if hasattr(request.user, 'student_profile'):
    student = request.user.student_profile
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
student = request.user.student  # ❌ N'existe pas !
```

---

## 🏫 Accès à la Classe Active

### ✅ CORRECT
```python
# Toujours passer par enrollments
active_enrollment = student.enrollments.filter(is_active=True).first()
current_class = active_enrollment.classroom if active_enrollment else None

# Vérifier l'existence
if not current_class:
    messages.warning(request, "Vous n'êtes inscrit dans aucune classe active.")
    return redirect('accounts:dashboard')
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
current_class = student.current_class  # ❌ Peut ne pas exister ou être obsolète
```

---

## 📚 Accès aux Matières par Classe

### ✅ CORRECT
```python
# Related name par défaut en minuscules
subjects = Subject.objects.filter(
    teacherassignment__classroom=current_class
).distinct().order_by('name')
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
subjects = Subject.objects.filter(
    teacher_assignments__classroom=current_class  # ❌ Mauvais related_name
)
```

---

## 📅 Gestion des Dates

### ✅ CORRECT
```python
from django.utils import timezone

# Pour les comparaisons de dates
today = timezone.now().date()
today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

# Filtrage avec DateTimeField
queryset.filter(due_date__gte=today_start)

# Conversion pour comparaison
assignment_due_date = assignment.due_date.date() if hasattr(assignment.due_date, 'date') else assignment.due_date

if assignment_due_date < today:
    # Logique ici
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
today = timezone.now().date()
queryset.filter(due_date__gte=today)  # ❌ Peut échouer avec DateTimeField

if assignment.due_date < today:  # ❌ Comparaison datetime vs date
    # Logique ici
```

---

## 🔍 Filtrage des Sessions

### ✅ CORRECT
```python
# Via timetable (ForeignKey)
sessions = Session.objects.filter(
    timetable__classroom=current_class
).select_related(
    'timetable__subject',
    'timetable__teacher__user',
    'timetable__classroom',
    'period'
)

# Accès aux propriétés
session.timetable.subject.name
session.timetable.teacher.user.get_full_name()
session.timetable.start_time
session.timetable.classroom.name
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
sessions = Session.objects.filter(
    classroom=current_class  # ❌ Session n'a pas de FK directe vers classroom
)

session.subject  # ❌ Accès direct n'existe pas
session.teacher  # ❌ Accès direct n'existe pas
```

---

## 📊 Modèle DailyAttendanceSummary

### ✅ CORRECT
```python
# Champs corrects
stats = summaries.aggregate(
    total_days=Count('id'),
    fully_present_days=Count('id', filter=Q(daily_status='FULLY_PRESENT')),
    present_sessions=Sum('present_sessions'),
    absent_sessions=Sum('absent_sessions'),
    late_sessions=Sum('late_sessions'),
)

# Calcul du taux
if stats['total_sessions'] and stats['total_sessions'] > 0:
    effective_present = (stats['present_sessions'] or 0) + (stats['late_sessions'] or 0)
    attendance_rate = round(effective_present / stats['total_sessions'] * 100, 1)
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
stats = summaries.aggregate(
    present_days=Count('id', filter=Q(status='PRESENT')),  # ❌ Champ status n'existe pas
    attended_sessions=Sum('attended_sessions'),  # ❌ Champ attended_sessions n'existe pas
)
```

---

## 📄 Modèle SessionAttendance

### ✅ CORRECT
```python
# Champs corrects
attendance.status  # 'PRESENT', 'ABSENT', 'LATE', 'EXCUSED'
attendance.get_status_display()  # "Présent", "Absent", etc.
attendance.arrival_time
attendance.notes  # Pas 'remarks' !
attendance.justification
```

### ❌ INCORRECT
```python
# NE JAMAIS UTILISER
attendance.remarks  # ❌ N'existe pas
attendance.comment  # ❌ N'existe pas
```

---

## 🎨 Templates - Héritage

### ✅ CORRECT
```html
<!-- Pour les pages étudiants -->
{% extends 'academic/student/base_student.html' %}

<!-- base_student.html hérite de -->
{% extends 'base_with_sidebar.html' %}
```

### ❌ INCORRECT
```html
<!-- NE JAMAIS UTILISER directement -->
{% extends 'base.html' %}  <!-- ❌ Ancien template sans sidebar -->
```

---

## 🔐 Permissions dans les Templates

### ✅ CORRECT
```html
<!-- Boutons conditionnels -->
{% if request.user.role == 'TEACHER' %}
    <a href="{% url 'academic:document_update' document.id %}">
        <span class="material-icons">edit</span>
        Modifier
    </a>
    <button type="submit" onclick="return confirm('Confirmer ?')">
        <span class="material-icons">delete</span>
        Supprimer
    </button>
{% endif %}
```

### ❌ INCORRECT
```html
<!-- NE JAMAIS laisser visible pour tous -->
<button>Modifier</button>  <!-- ❌ Pas de vérification de rôle -->
<button>Supprimer</button>  <!-- ❌ Problème de sécurité -->
```

---

## 🔍 Filtres de Recherche

### ✅ CORRECT
```python
# Recherche multiple avec Q
from django.db.models import Q

if search_query:
    queryset = queryset.filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(subject__name__icontains=search_query)
    )
```

---

## 📦 Pagination

### ✅ CORRECT
```python
from django.core.paginator import Paginator

# Pagination
paginator = Paginator(queryset, 20)
page_number = request.GET.get('page')
page_obj = paginator.get_page(page_number)

# Contexte
context = {
    'page_obj': page_obj,
    'is_paginated': page_obj.has_other_pages(),  # ✅ Important !
    'items': page_obj.object_list,
}
```

### ❌ INCORRECT
```python
# NE JAMAIS OUBLIER
context = {
    'page_obj': page_obj,
    # ❌ Manque is_paginated
    'items': page_obj.object_list,
}
```

---

## 🎯 Context Standard pour Vue Étudiant

### ✅ Template Complet
```python
context = {
    'student': student,
    'current_class': current_class,
    'subjects': subjects,
    'page_obj': page_obj,
    'is_paginated': page_obj.has_other_pages(),
    'items': page_obj.object_list,
    'stats': stats,
    'today': timezone.now().date(),
}
```

---

## 🌈 Thèmes de Couleur

### Code Couleur par Rôle
```python
ROLE_COLORS = {
    'TEACHER': {
        'primary': 'green-600',
        'light': 'green-50',
        'gradient': 'from-green-50 to-green-100',
    },
    'STUDENT': {
        'primary': 'blue-600',
        'light': 'blue-50',
        'gradient': 'from-blue-50 to-blue-100',
    },
    'PARENT': {
        'primary': 'purple-600',
        'light': 'purple-50',
        'gradient': 'from-purple-50 to-purple-100',
    },
    'ADMIN': {
        'primary': 'red-600',
        'light': 'red-50',
        'gradient': 'from-red-50 to-red-100',
    },
}
```

### Code Couleur par Type
```python
FEATURE_COLORS = {
    'sessions': 'blue',      # Sessions de cours
    'assignments': 'purple', # Devoirs
    'documents': 'indigo',   # Documents
    'grades': 'yellow',      # Notes
    'attendance': 'green',   # Présences
    'warnings': 'orange',    # Avertissements
    'errors': 'red',         # Erreurs
}
```

---

## 🚨 Gestion des Erreurs

### ✅ CORRECT
```python
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib import messages

# Récupération sécurisée
student = get_object_or_404(Student, user=request.user)

# Vérification de classe
if not current_class:
    messages.warning(request, "Vous n'êtes inscrit dans aucune classe active.")
    return redirect('accounts:dashboard')

# Vérification de permission
if request.user.role == 'STUDENT':
    if not has_access:
        raise PermissionDenied("Vous n'avez pas accès à cette ressource.")
```

---

## 📱 Classes CSS Utiles

### Cartes
```html
<!-- Carte standard -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all p-6">

<!-- Carte statistique avec gradient -->
<div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5 border border-blue-200">

<!-- Carte étudiant (legacy) -->
<div class="student-card">  <!-- Défini dans base_student.html -->
```

### Badges
```html
<!-- Badge de statut -->
<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold
             {% if status == 'success' %}bg-green-100 text-green-800{% endif %}">
    ✓ Validé
</span>
```

### Filtres
```html
<!-- Section de filtres -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <form method="get">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
            <!-- Champs de filtres -->
        </div>
        <div class="flex items-center justify-end space-x-4 pt-2 border-t border-gray-100">
            <!-- Boutons -->
        </div>
    </form>
</div>
```

---

## ✅ Checklist Avant Commit

- [ ] Utilise `student_profile` (pas `student`)
- [ ] Récupère la classe via `enrollments.filter(is_active=True)`
- [ ] Vérifie l'existence de `current_class`
- [ ] Utilise les bons `related_name` (vérifier models.py)
- [ ] Gère correctement les dates (datetime vs date)
- [ ] Ajoute `is_paginated` au contexte
- [ ] Gère les valeurs nulles (`or 0` dans agrégations)
- [ ] Template hérite de `base_with_sidebar.html` ou `base_student.html`
- [ ] Permissions vérifiées (côté vue ET template)
- [ ] Design cohérent avec les thèmes de couleur
- [ ] Filtres de recherche fonctionnels
- [ ] Responsive design testé

---

## 🔗 Liens Utiles

- **Documentation complète** : `/docs/STUDENT_INTERFACE_UPDATES_OCT_2025.md`
- **Changelog** : `/CHANGELOG_STUDENT_OCT_2025.md`
- **URLs** : `/URLS_DOCUMENTATION.md`
- **Index docs** : `/docs/INDEX.md`

---

## 💡 Tips

1. **Toujours vérifier les types** : `print(type(variable))` pour déboguer
2. **Utiliser select_related** : Pour optimiser les requêtes
3. **Utiliser distinct()** : Après filtres many-to-many
4. **Tester avec données réelles** : Ne pas supposer que les champs existent
5. **Lire models.py** : Vérifier les vrais noms de champs et relations

---

**📅 Dernière mise à jour** : 5 Octobre 2025  
**🎓 Version** : 2.1.0
