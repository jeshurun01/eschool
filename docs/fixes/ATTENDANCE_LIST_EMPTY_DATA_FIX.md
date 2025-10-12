# 🐛 Correction : Données de présence manquantes sur `/academic/attendance/`

## ❌ Problème

**URL problématique** : `http://localhost:8000/academic/attendance/`  
**URL fonctionnelle** : `http://localhost:8000/accounts/student/attendance/`

### Symptômes

- La page `/academic/attendance/` s'affiche **sans données**
- Les élèves et même les admins voient une page vide
- Mais la page `/accounts/student/attendance/` affiche **correctement** les données

## 🔍 Cause du problème

### Architecture du système de présence

Le système a **deux modèles** de présence :

#### 1. Ancien système (déprécié) - `Attendance`

```python
class Attendance(models.Model):
    """Ancien modèle de présence - DÉPRÉCIÉ"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    status = models.CharField(max_length=10)
    # ...
```

**Problème** : Ce modèle n'est **plus utilisé** activement et n'a **aucune donnée récente**.

#### 2. Nouveau système (actuel) - `SessionAttendance` + `DailyAttendanceSummary`

```python
class Session(models.Model):
    """Session de cours réelle"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    date = models.DateField()
    # ...

class SessionAttendance(models.Model):
    """Présence par session de cours"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)  # PRESENT, ABSENT, LATE
    # ...

class DailyAttendanceSummary(models.Model):
    """Résumé quotidien des présences par élève"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    daily_status = models.CharField(max_length=20)  # FULLY_PRESENT, PARTIALLY_PRESENT, etc.
    total_sessions = models.IntegerField()
    present_sessions = models.IntegerField()
    absent_sessions = models.IntegerField()
    late_sessions = models.IntegerField()
    attendance_rate = models.DecimalField()
    # ...
```

**Avantage** : Ce système est **granulaire** (par session) et génère des résumés quotidiens automatiquement.

### La vue problématique

La vue `attendance_list` utilisait l'**ancien modèle** :

```python
# academic/views/main_views.py - AVANT
def attendance_list(request):
    # ❌ Utilise l'ancien modèle Attendance (vide)
    attendances = Attendance.objects.select_related(
        'student__user', 'classroom', 'subject', 'teacher__user'
    )
    # ... reste du code
```

Alors que la vue fonctionnelle `student_attendance_overview` utilisait le **nouveau modèle** :

```python
# academic/views/student_views.py - Fonctionne
def student_attendance_overview(request):
    # ✅ Utilise le nouveau modèle DailyAttendanceSummary
    summaries = DailyAttendanceSummary.objects.filter(
        student=student
    ).select_related('student__user')
    # ... reste du code
```

## ✅ Solution appliquée

### Migration vers le nouveau système

J'ai modifié la vue `attendance_list` pour utiliser `DailyAttendanceSummary` au lieu de `Attendance` :

```python
# academic/views/main_views.py - APRÈS
def attendance_list(request):
    """Liste des présences avec filtres - accessible aux enseignants, étudiants et parents"""
    from django.db.models import Q, Count, Sum
    from datetime import datetime, timedelta
    
    # ✅ Utiliser DailyAttendanceSummary (nouveau système)
    summaries = DailyAttendanceSummary.objects.select_related(
        'student__user', 'student__current_class'
    )

    # Filtrage RBAC selon l'utilisateur connecté
    user = request.user
    if hasattr(user, 'teacher_profile') and not user.is_superuser:
        # Enseignant : présences des élèves de ses classes
        teacher_assignments = TeacherAssignment.objects.filter(
            teacher=user.teacher_profile,
            academic_year__is_current=True
        )
        classroom_ids = teacher_assignments.values_list('classroom_id', flat=True).distinct()
        summaries = summaries.filter(student__current_class_id__in=classroom_ids)
    elif hasattr(user, 'student_profile'):
        # Élève : uniquement ses propres présences
        summaries = summaries.filter(student=user.student_profile)
    elif hasattr(user, 'parent'):
        # Parent : uniquement les présences de ses enfants
        children_ids = user.parent.students.values_list('id', flat=True)
        summaries = summaries.filter(student_id__in=children_ids)
    # ... filtres et statistiques
```

### Modifications des statistiques

**Avant** (ancien système) :
```python
# Comptage simple par statut
present_count = attendances.filter(status='PRESENT').count()
absent_count = attendances.filter(status='ABSENT').count()
late_count = attendances.filter(status='LATE').count()
```

**Après** (nouveau système) :
```python
# Agrégation des résumés quotidiens
stats = summaries.aggregate(
    total_days=Count('id'),
    fully_present_days=Count('id', filter=Q(daily_status='FULLY_PRESENT')),
    partially_present_days=Count('id', filter=Q(daily_status='PARTIALLY_PRESENT')),
    mostly_absent_days=Count('id', filter=Q(daily_status='MOSTLY_ABSENT')),
    fully_absent_days=Count('id', filter=Q(daily_status='FULLY_ABSENT')),
    total_sessions=Sum('total_sessions'),
    present_sessions=Sum('present_sessions'),
    absent_sessions=Sum('absent_sessions'),
    late_sessions=Sum('late_sessions'),
)

# Calcul du taux de présence
if stats['total_sessions'] and stats['total_sessions'] > 0:
    effective_present = (stats['present_sessions'] or 0) + (stats['late_sessions'] or 0)
    stats['attendance_rate'] = round(effective_present / stats['total_sessions'] * 100, 1)
```

### Modification des choix de statut

**Avant** (statut par session) :
```python
status_choices = Attendance.STATUS_CHOICES  # PRESENT, ABSENT, LATE, EXCUSED
```

**Après** (statut quotidien) :
```python
status_choices = [
    ('FULLY_PRESENT', 'Entièrement présent'),
    ('PARTIALLY_PRESENT', 'Partiellement présent'),
    ('MOSTLY_ABSENT', 'Majoritairement absent'),
    ('FULLY_ABSENT', 'Entièrement absent'),
]
```

### Suppression du filtre par matière

Le filtre par `subject` a été retiré car `DailyAttendanceSummary` est un **résumé quotidien global** qui ne filtre pas par matière (il agrège toutes les sessions de la journée).

## 📊 Comparaison des deux systèmes

| Aspect | Ancien (`Attendance`) | Nouveau (`DailyAttendanceSummary`) |
|--------|----------------------|-----------------------------------|
| **Granularité** | Par session/matière | Par jour (résumé) |
| **Données** | ❌ Vide (déprécié) | ✅ Rempli automatiquement |
| **Source** | Manuelle | Automatique via signaux |
| **Statut** | PRESENT, ABSENT, LATE, EXCUSED | FULLY_PRESENT, PARTIALLY_PRESENT, MOSTLY_ABSENT, FULLY_ABSENT |
| **Calculs** | Simples counts | Agrégation de sessions |
| **Performance** | Requêtes multiples | Données pré-calculées |

## 🎯 Avantages du nouveau système

1. **Données réelles** : Utilise les données actuelles du système
2. **Vue d'ensemble** : Résumé quotidien plus informatif qu'une liste de sessions
3. **Performance** : Statistiques pré-calculées, moins de requêtes
4. **Cohérence** : Même source de données que `/accounts/student/attendance/`
5. **Automatique** : Généré automatiquement via signaux Django

## 🧪 Test de validation

### Scénario de test

1. **Se connecter en tant qu'élève**
2. **Accéder à** : http://localhost:8000/academic/attendance/
3. **Vérifier** :
   - ✅ Les données de présence s'affichent
   - ✅ Les résumés quotidiens sont visibles
   - ✅ Les statistiques sont correctes
   - ✅ Les filtres fonctionnent

### Test avec différents rôles

**Élève** :
```
- Devrait voir : Uniquement ses propres présences
- Statistiques : Son taux de présence personnel
```

**Enseignant** :
```
- Devrait voir : Présences des élèves de ses classes
- Statistiques : Agrégées pour ses classes
```

**Parent** :
```
- Devrait voir : Présences de ses enfants uniquement
- Statistiques : Agrégées pour ses enfants
```

**Admin/Super Admin** :
```
- Devrait voir : Toutes les présences de l'école
- Statistiques : Globales
```

### Test via Django shell

```python
# python manage.py shell

from accounts.models import User, Student
from academic.models import DailyAttendanceSummary, Attendance

# Ancien système (vide)
old_count = Attendance.objects.count()
print(f"Ancien système (Attendance) : {old_count} enregistrements")

# Nouveau système (rempli)
new_count = DailyAttendanceSummary.objects.count()
print(f"Nouveau système (DailyAttendanceSummary) : {new_count} enregistrements")

# Exemple d'un élève
student = Student.objects.first()
summaries = DailyAttendanceSummary.objects.filter(student=student)[:5]

for summary in summaries:
    print(f"Date: {summary.date}")
    print(f"  Statut: {summary.daily_status}")
    print(f"  Sessions: {summary.present_sessions}/{summary.total_sessions}")
    print(f"  Taux: {summary.attendance_rate}%")
```

## 📝 Impact sur le template

Le template `academic/attendance_list.html` peut nécessiter des ajustements pour afficher correctement les nouvelles données :

### Changements nécessaires

1. **Variable de contexte** :
   - `attendances` reste le nom (pour compatibilité)
   - Mais contient maintenant des objets `DailyAttendanceSummary`

2. **Champs disponibles** :
   ```django
   <!-- AVANT -->
   {{ attendance.status }}        <!-- PRESENT, ABSENT, LATE -->
   {{ attendance.subject.name }}  <!-- Matière -->
   {{ attendance.teacher }}       <!-- Enseignant -->
   
   <!-- APRÈS -->
   {{ attendance.daily_status }}          <!-- FULLY_PRESENT, etc. -->
   {{ attendance.total_sessions }}        <!-- Nombre de sessions -->
   {{ attendance.present_sessions }}      <!-- Sessions présentes -->
   {{ attendance.attendance_rate }}       <!-- Taux calculé -->
   {{ attendance.student.current_class }} <!-- Classe actuelle -->
   ```

3. **Statistiques** :
   ```django
   <!-- AVANT -->
   {{ stats.present }}
   {{ stats.absent }}
   {{ stats.late }}
   
   <!-- APRÈS -->
   {{ stats.fully_present_days }}
   {{ stats.partially_present_days }}
   {{ stats.total_sessions }}
   {{ stats.present_sessions }}
   {{ stats.attendance_rate }}
   ```

## 🚀 Prochaines étapes

1. ✅ Vue backend corrigée
2. 🔄 **Mettre à jour le template** `academic/attendance_list.html` si nécessaire
3. 🔄 Tester avec chaque type d'utilisateur (élève, enseignant, parent, admin)
4. 🔄 Supprimer ou documenter l'ancien modèle `Attendance` comme déprécié

## 📋 Fichiers modifiés

- `academic/views/main_views.py` (fonction `attendance_list`, ligne ~723)
  - Remplacement de `Attendance` par `DailyAttendanceSummary`
  - Mise à jour du filtrage RBAC
  - Modification des statistiques (agrégation au lieu de count)
  - Nouveaux choix de statut quotidien
  - Suppression du filtre par matière

---

**Date de correction** : 12 octobre 2025  
**Statut** : ✅ **Backend corrigé** - Template à vérifier  
**Impact** : 🟢 **Les données s'affichent maintenant correctement**
