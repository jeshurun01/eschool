# 🐛 Correction : TypeError dans le calendrier étudiant

## ❌ Erreur

**URL** : `http://localhost:8000/accounts/student/calendar/`

**Message d'erreur** :
```
TypeError at /accounts/student/calendar/
can't compare datetime.datetime to datetime.date
```

## 🔍 Cause du problème

Le code comparait des objets `datetime.date` avec des objets `datetime.datetime`, ce qui n'est pas autorisé en Python.

### Contexte technique

Dans le modèle `Document`, les champs `access_date` et `expiry_date` sont définis comme `DateTimeField` :

```python
# academic/models.py
class Document(models.Model):
    access_date = models.DateTimeField(blank=True, null=True)  # DateTime, pas Date
    expiry_date = models.DateTimeField(blank=True, null=True)  # DateTime, pas Date
```

Mais dans la vue `student_academic_calendar`, le code créait des dates (`date`) pour la comparaison :

```python
# accounts/views.py - AVANT
start_date = today - timedelta(days=7)      # date
end_date = today + timedelta(days=30)       # date

# Erreur : compare date avec datetime
documents = Document.objects.filter(
    access_date__gte=start_date,   # ❌ date comparé avec DateTimeField
    access_date__lte=end_date       # ❌ date comparé avec DateTimeField
)
```

### Ligne problématique

```python
# Ligne ~2445
documents = Document.objects.filter(
    Q(subject_id__in=subject_ids) | Q(is_public=True),
    document_type__in=['EXERCISE', 'EXAM'],
    access_date__gte=start_date,    # ❌ ERREUR ICI
    access_date__lte=end_date       # ❌ ET ICI
)
```

## ✅ Solution appliquée

### 1. Conversion des dates en datetime

```python
# accounts/views.py - APRÈS
from django.utils import timezone

# Plage de dates : 7 jours passés + 30 jours futurs
start_date = today - timedelta(days=7)
end_date = today + timedelta(days=30)

# Convertir en datetime pour les comparaisons avec DateTimeField
start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
```

**Explication** :
- `datetime.combine(start_date, datetime.min.time())` → Crée un datetime à 00:00:00
- `datetime.combine(end_date, datetime.max.time())` → Crée un datetime à 23:59:59.999999
- `timezone.make_aware()` → Ajoute le timezone pour être compatible avec Django

### 2. Utilisation des datetime dans les requêtes

```python
documents = Document.objects.filter(
    Q(subject_id__in=subject_ids) | Q(is_public=True),
    document_type__in=['EXERCISE', 'EXAM'],
    access_date__gte=start_datetime,  # ✅ datetime comparé avec DateTimeField
    access_date__lte=end_datetime     # ✅ datetime comparé avec DateTimeField
)
```

### 3. Conversion pour l'affichage

```python
for doc in documents:
    # Convertir access_date (datetime) en date pour l'événement
    event_date = doc.access_date.date() if doc.access_date else doc.created_at.date()
    
    events.append({
        'date': event_date,  # ✅ Converti en date
        'time': doc.access_date.strftime('%H:%M') if doc.access_date else '08:00',  # ✅ Utilise l'heure réelle
        # ...
    })
```

## 📊 Impact de la correction

### Avant

- ❌ **Crash complet** de la page calendrier
- ❌ Erreur `TypeError` à chaque accès
- ❌ Élèves ne peuvent pas voir leur calendrier

### Après

- ✅ **Page calendrier fonctionne** correctement
- ✅ Dates et heures affichées correctement
- ✅ Comparaisons datetime/date correctes
- ✅ Respect des heures d'accès des documents

## 🧪 Test de validation

### Étapes de test

1. **Se connecter** en tant qu'élève
2. **Accéder au calendrier** : http://localhost:8000/accounts/student/calendar/
3. **Vérifier** :
   - ✅ La page se charge sans erreur
   - ✅ Les événements s'affichent correctement
   - ✅ Les dates et heures sont correctes
   - ✅ Les devoirs/examens apparaissent aux bonnes dates

### Test manuel via Django shell

```python
# python manage.py shell

from accounts.models import User
from academic.models import Document
from datetime import datetime, timedelta, date
from django.utils import timezone

# Récupérer un élève
student_user = User.objects.filter(role='STUDENT').first()

# Créer les plages de dates (comme dans le code corrigé)
today = date.today()
start_date = today - timedelta(days=7)
end_date = today + timedelta(days=30)

# Convertir en datetime
start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

# Requête qui ne devrait plus causer d'erreur
documents = Document.objects.filter(
    document_type__in=['EXERCISE', 'EXAM'],
    access_date__gte=start_datetime,
    access_date__lte=end_datetime
)

print(f"Documents trouvés : {documents.count()}")
for doc in documents[:5]:
    print(f"  - {doc.title} : {doc.access_date}")
```

## 🔧 Améliorations techniques

### Respect des heures

Avant, tous les événements de documents utilisaient une heure fixe `'08:00'`. Maintenant, le code utilise l'heure réelle de `access_date` :

```python
# AVANT
'time': '08:00',  # Heure fixe

# APRÈS
'time': doc.access_date.strftime('%H:%M') if doc.access_date else '08:00',  # Heure réelle
```

### Meilleure couverture temporelle

- `datetime.min.time()` (00:00:00) → Capture tous les événements du début de la journée
- `datetime.max.time()` (23:59:59.999999) → Capture tous les événements jusqu'à la fin de la journée

## 📝 Fichiers modifiés

- `accounts/views.py` (fonction `student_academic_calendar`, ligne ~2377)
  - Ajout de `from django.utils import timezone`
  - Création de `start_datetime` et `end_datetime`
  - Modification de la requête `Document.objects.filter()`
  - Amélioration de la conversion `access_date` → `event_date`

## 💡 Leçons apprises

### Règle : Toujours comparer des types identiques

En Python/Django :
- ❌ **NE PAS** comparer `date` avec `datetime`
- ✅ **TOUJOURS** comparer `datetime` avec `datetime`
- ✅ **TOUJOURS** comparer `date` avec `date`

### Conversion correcte

```python
# Date → DateTime (début de journée)
datetime.combine(my_date, datetime.min.time())  # 00:00:00

# Date → DateTime (fin de journée)
datetime.combine(my_date, datetime.max.time())  # 23:59:59.999999

# DateTime → Date
my_datetime.date()

# Ajouter timezone pour Django
timezone.make_aware(my_datetime)
```

## 🔍 Prévention future

Pour éviter ce genre d'erreur à l'avenir :

1. **Vérifier les types de champs** dans les modèles avant de faire des comparaisons
2. **Utiliser `DateTimeField`** pour les champs nécessitant heure + date
3. **Utiliser `DateField`** pour les champs nécessitant uniquement la date
4. **Toujours convertir** explicitement entre `date` et `datetime` quand nécessaire

## 🎯 Résultat

La page calendrier étudiant fonctionne maintenant **parfaitement** et affiche :
- ✅ Cours réguliers
- ✅ Sessions réelles
- ✅ Devoirs avec leur heure réelle d'accès
- ✅ Examens avec leur heure réelle
- ✅ Sans aucune erreur de comparaison de types

---

**Date de correction** : 12 octobre 2025  
**Statut** : ✅ **CORRIGÉ et testé**  
**Type d'erreur** : TypeError (comparaison date/datetime)
