# Architecture optimisée pour les présences

## Proposition d'architecture hybride

### Option recommandée : Une seule table avec vue agrégée

```python
class SessionAttendance(models.Model):
    """Présence pour une session spécifique - Source de vérité unique"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    # Détails temporels
    arrival_time = models.TimeField(blank=True, null=True)
    
    # Métadonnées d'enregistrement
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Notes
    justification = models.TextField(blank=True)
    notes = models.TextField(blank=True)

class DailyAttendanceSummary(models.Model):
    """Vue agrégée automatique des présences journalières"""
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    date = models.DateField()
    
    # Statistiques calculées automatiquement
    total_sessions = models.PositiveIntegerField()
    present_sessions = models.PositiveIntegerField()
    absent_sessions = models.PositiveIntegerField()
    late_sessions = models.PositiveIntegerField()
    
    # Statut global de la journée (calculé)
    daily_status = models.CharField(max_length=20, choices=[
        ('FULLY_PRESENT', 'Entièrement présent'),
        ('PARTIALLY_PRESENT', 'Partiellement présent'),
        ('MOSTLY_ABSENT', 'Majoritairement absent'),
        ('FULLY_ABSENT', 'Entièrement absent'),
    ])
    
    # Mis à jour automatiquement
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date']
```

## Avantages de cette approche

### 1. **Source de vérité unique**
- Toutes les présences sont dans `SessionAttendance`
- `DailyAttendanceSummary` est juste une vue agrégée

### 2. **Flexibilité pédagogique**
- L'enseignant prend l'appel par session
- L'administration voit un résumé journalier
- Les parents voient les deux niveaux

### 3. **Traçabilité complète**
- Qui a pris l'appel
- Quand exactement
- Pour quel cours précis

### 4. **Performance optimisée**
- Requêtes rapides sur les résumés journaliers
- Détails disponibles si nécessaire

## Migration strategy

1. **Phase 1** : Créer `SessionAttendance` et `DailyAttendanceSummary`
2. **Phase 2** : Migrer les données existantes de `Attendance` vers `SessionAttendance`
3. **Phase 3** : Calculer les résumés journaliers
4. **Phase 4** : Supprimer l'ancien modèle `Attendance`

## Cas d'usage pratiques

### Pour l'enseignant
```python
# Prendre l'appel pour une session
session = Session.objects.get(id=session_id)
for student in session.classroom.students.all():
    SessionAttendance.objects.create(
        session=session,
        student=student,
        status='PRESENT',  # ou autre
        recorded_by=teacher.user
    )
```

### Pour l'administration
```python
# Vue d'ensemble des absences du jour
daily_summaries = DailyAttendanceSummary.objects.filter(
    date=today,
    daily_status__in=['MOSTLY_ABSENT', 'FULLY_ABSENT']
)
```

### Pour les parents
```python
# Voir les détails de présence de leur enfant
detailed_attendance = SessionAttendance.objects.filter(
    student=child,
    session__date=today
).select_related('session__timetable__subject')
```