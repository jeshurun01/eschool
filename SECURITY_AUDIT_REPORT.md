# Rapport d'Audit de Sécurité - Vues Academic

## ⚠️ PROBLÈMES DE SÉCURITÉ CORRIGÉS

### 1. 🔴 CRITIQUE - Accès non autorisé aux documents (12 octobre 2025)
**Problème :** Les élèves pouvaient voir et télécharger les documents de toutes les classes

**Description :**
- Un élève de 6ème A pouvait accéder aux examens, corrections et cours de 6ème B, 6ème C, etc.
- La vérification se faisait uniquement sur la matière, pas sur la classe
- Impact : Violation de confidentialité, fuite de données sensibles

**Vues corrigées :**
- ✅ `document_list()` → Filtre maintenant sur `classroom=current_classroom` OU `classroom=None`
- ✅ `document_view()` → Vérifie que le document appartient à la classe de l'élève
- ✅ `document_subject_list()` → Utilise seulement la classe active (pas l'historique)

**Documentation :** `docs/fixes/DOCUMENT_ACCESS_SECURITY_FIX.md`

### 2. Vues sans protection d'authentification (CRITIQUE)
**Problème :** Plusieurs vues étaient accessibles sans authentification

**Vues corrigées :**
- ✅ `subject_list()` → Ajout de `@login_required`
- ✅ `subject_create()` → Ajout de `@admin_required` 
- ✅ `timetable_list()` → Ajout de `@admin_required`
- ✅ `timetable_create()` → Ajout de `@admin_required`
- ✅ `classroom_students()` → Ajout de `@teacher_or_student_required`
- ✅ `student_bulletin()` → Ajout de `@teacher_or_student_required`
- ✅ `class_report()` → Ajout de `@teacher_required`

### 3. Contrôle d'accès insuffisant par rôle (ÉLEVÉ)
**Problème :** Certaines vues sensibles n'avaient pas de restrictions par rôle appropriées

**Corrections appliquées :**
- **Création de matières** : Maintenant réservée aux administrateurs seulement
- **Gestion emplois du temps** : Maintenant réservée aux administrateurs
- **Rapports de classe** : Maintenant réservés aux enseignants et admins

## 🚨 VULNÉRABILITÉS RESTANTES À CORRIGER

### 1. Vérifications RBAC manquantes dans les vues avec paramètres
**Risque :** Accès non autorisé aux données d'autres utilisateurs

**Vues nécessitant des améliorations :**

```python
# academic/views.py - Lines à améliorer

@teacher_or_student_required
def student_bulletin(request, student_id):
    # ⚠️ MANQUE: Vérifier que l'utilisateur a accès à cet étudiant
    student = get_object_or_404(Student, id=student_id)
    
    # AJOUTER cette vérification:
    if hasattr(request.user, 'student') and request.user.student.id != student_id:
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    elif hasattr(request.user, 'parent'):
        # Vérifier que c'est son enfant
        if not request.user.parent.students.filter(id=student_id).exists():
            messages.error(request, "Accès non autorisé.")
            return redirect('accounts:dashboard')

@teacher_required  
def class_report(request, classroom_id):
    # ⚠️ MANQUE: Vérifier que l'enseignant enseigne dans cette classe
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    
    # AJOUTER cette vérification:
    if hasattr(request.user, 'teacher_profile') and not request.user.is_superuser:
        if not TeacherAssignment.objects.filter(
            teacher=request.user.teacher_profile,
            classroom=classroom
        ).exists():
            messages.error(request, "Vous n'enseignez pas dans cette classe.")
            return redirect('accounts:teacher_dashboard')

@teacher_or_student_required
def classroom_students(request, classroom_id):
    # ⚠️ MANQUE: Vérifier l'accès à la classe
    # Implémenter la même logique que classroom_detail
```

### 2. Vues de grades potentiellement vulnérables
**Problème :** La vue `grade_list` utilise `Grade.objects.for_role()` qui n'existe pas

```python
# Line 1036 - ERREUR
grades = Grade.objects.for_role(request.user).select_related(...)
# ❌ Cette méthode n'existe pas dans le manager
```

**Solution recommandée :**
```python
# Remplacer par:
grades = Grade.objects.select_related(...)

# Puis ajouter le filtrage RBAC manuel:
if hasattr(request.user, 'teacher_profile') and not request.user.is_superuser:
    grades = grades.filter(teacher=request.user.teacher_profile)
elif hasattr(request.user, 'student'):
    grades = grades.filter(student=request.user.student)
elif hasattr(request.user, 'parent'):
    children_ids = request.user.parent.students.values_list('id', flat=True)
    grades = grades.filter(student_id__in=children_ids)
```

### 3. Vérifications d'ID manquantes
**Problème :** Erreurs de linting indiquant des accès à des attributs `id` qui n'existent pas

**Fichiers à vérifier :**
- Modèles `Student`, `ClassRoom`, `Subject` - s'assurer que l'attribut `id` est accessible
- Ou utiliser `pk` au lieu de `id`

## 🔒 RECOMMANDATIONS DE SÉCURITÉ SUPPLÉMENTAIRES

### 1. Middleware de logging d'accès
```python
# Ajouter un middleware pour logger les accès sensibles
class SecurityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Logger les accès aux vues sensibles
        if any(path in request.path for path in ['/academic/', '/accounts/']):
            logger.info(f"Access to {request.path} by {request.user}")
        
        response = self.get_response(request)
        return response
```

### 2. Rate limiting
```python
# Ajouter django-ratelimit pour limiter les tentatives d'accès
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/m', method='GET')
@admin_required
def subject_create(request):
    # ...
```

### 3. Validation des permissions au niveau du modèle
```python
# Ajouter des méthodes de validation dans les modèles
class Grade(models.Model):
    def can_be_viewed_by(self, user):
        if user.is_superuser:
            return True
        if hasattr(user, 'teacher_profile') and self.teacher == user.teacher_profile:
            return True
        if hasattr(user, 'student') and self.student == user.student:
            return True
        if hasattr(user, 'parent') and self.student in user.parent.students.all():
            return True
        return False
```

## 📋 PLAN D'ACTION PRIORITAIRE

1. **URGENT** - Corriger les vérifications RBAC manquantes dans les vues avec paramètres
2. **ÉLEVÉ** - Corriger l'erreur `Grade.objects.for_role()` 
3. **MOYEN** - Résoudre les erreurs d'accès aux attributs `id`
4. **FAIBLE** - Implémenter le logging et rate limiting

## ✅ BONNES PRATIQUES DÉJÀ EN PLACE

- ✅ Utilisation des décorateurs de permission RBAC
- ✅ Filtrage des données selon le rôle utilisateur
- ✅ Vérifications de propriété dans certaines vues (ex: `course_detail`)
- ✅ Messages d'erreur appropriés avec redirections
- ✅ Utilisation de `get_object_or_404` pour éviter les expositions d'information

## 🔍 TESTS DE SÉCURITÉ RECOMMANDÉS

1. **Test d'escalade de privilèges** : Tenter d'accéder à des ressources d'autres utilisateurs
2. **Test d'autorisation horizontale** : Un élève tente de voir les notes d'un autre élève
3. **Test d'autorisation verticale** : Un utilisateur tente d'accéder à des fonctions admin
4. **Test de contournement d'authentification** : Accès direct aux URLs sans connexion