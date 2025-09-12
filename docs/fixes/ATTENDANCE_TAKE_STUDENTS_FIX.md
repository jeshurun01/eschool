# Correction Prise de Présence - Élèves par Classe

## Problème Identifié
À l'URL `http://127.0.0.1:8000/academic/attendance/take/`, tous les enseignants voyaient toujours les mêmes 5 élèves fictifs (Dupont Jean, Martin Sophie, etc.) peu importe la classe sélectionnée.

## Cause Racine
Le template `attendance_take.html` utilisait des données JavaScript simulées (mockStudents) au lieu de faire un appel AJAX au serveur pour récupérer les vrais élèves de la classe sélectionnée.

**Code problématique :**
```javascript
const mockStudents = [
    {id: 1, name: 'Dupont Jean', matricule: 'ETU001'},
    {id: 2, name: 'Martin Sophie', matricule: 'ETU002'},
    {id: 3, name: 'Moreau Pierre', matricule: 'ETU003'},
    {id: 4, name: 'Leroy Emma', matricule: 'ETU004'},
    {id: 5, name: 'Blanc Lucas', matricule: 'ETU005'},
];
```

## Solution Implémentée

### 1. Nouvelle Vue API AJAX (`academic/views.py`)

**Ajout de `get_classroom_students()`:**
```python
@teacher_required
def get_classroom_students(request, classroom_id):
    """API AJAX pour récupérer les élèves d'une classe - réservé aux enseignants"""
    try:
        classroom = get_object_or_404(ClassRoom, id=classroom_id)
        
        # Vérifier que l'enseignant a accès à cette classe
        if not request.user.is_superuser and hasattr(request.user, 'teacher_profile'):
            if not TeacherAssignment.objects.filter(
                teacher=request.user.teacher_profile,
                classroom=classroom
            ).exists():
                return JsonResponse({'error': 'Accès non autorisé à cette classe'}, status=403)
        
        # Récupérer les vrais élèves de la classe
        students = Student.objects.filter(
            enrollments__classroom=classroom,
            enrollments__is_active=True
        ).select_related('user').order_by('user__last_name', 'user__first_name')
        
        # Convertir en format JSON
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'name': student.user.get_full_name(),
                'matricule': getattr(student, 'student_id', f'ETU{student.id:03d}'),
                'email': student.user.email
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data,
            'classroom_name': classroom.name,
            'total_students': len(students_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### 2. Nouvelle Route URL (`academic/urls.py`)

**Ajout de l'endpoint API:**
```python
path('api/classroom/<int:classroom_id>/students/', views.get_classroom_students, name='get_classroom_students'),
```

### 3. JavaScript Amélioré (`templates/academic/attendance_take.html`)

**Remplacement du code simulé par un vrai appel AJAX:**
```javascript
function loadStudents(classroomId) {
    // Afficher un indicateur de chargement
    studentsContainer.innerHTML = `
        <div class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-gray-600">Chargement des élèves...</p>
        </div>
    `;
    studentsSection.classList.remove('hidden');
    
    // Appel AJAX pour récupérer les vrais élèves
    fetch(`/academic/api/classroom/${classroomId}/students/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayStudents(data.students, data.classroom_name);
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            // Gestion d'erreur avec retry
        });
}
```

### 4. Fonctionnalités Ajoutées

- **Indicateur de chargement** avec spinner
- **Gestion d'erreurs** avec bouton de retry
- **Validation RBAC** : les enseignants ne peuvent charger que leurs classes
- **Message informatif** : affichage du nom de la classe et nombre d'élèves
- **Cas vide** : message approprié si aucun élève inscrit

## Tests de Validation

### Test 1: Répartition Réelle des Élèves
```
Classe: CP A
  Élèves inscrits: 1
    - Lucas Leroy

Classe: CP B  
  Élèves inscrits: 1
    - Emma Leroy

Classe: CE1 A
  Élèves inscrits: 1  
    - Hugo Blanc
```

### Test 2: Classes de Marie Dupont
```
=== Classes de Marie Dupont ===
  CP A: 1 élèves
  CP B: 1 élèves
```

### Test 3: API avec Sécurité RBAC
- ✅ **200 OK** : Pour les classes autorisées
- ✅ **403 Forbidden** : Pour les classes non autorisées
- ✅ **Données réelles** : Élèves effectivement inscrits

## Comportement Attendu Maintenant

### 👨‍🏫 Pour Marie Dupont (Enseignante CP)
1. Sélectionne "CP A" → Voit Lucas Leroy (son élève réel)
2. Sélectionne "CP B" → Voit Emma Leroy (son élève réel)
3. Tente d'accéder à "4ème A" → Erreur 403 (non autorisée)

### 👨‍🏫 Pour Jean Martin (Enseignant collège)
1. Sélectionne "4ème A" → Voit ses élèves de 4ème A
2. Sélectionne "5ème B" → Voit ses élèves de 5ème B
3. Tente d'accéder à "CP A" → Erreur 403 (non autorisée)

### Terminé : Plus de Données Simulées
- ❌ Avant : 5 élèves fictifs identiques pour toutes les classes
- ✅ Après : Élèves réels différents selon la classe sélectionnée

## Interface Utilisateur Améliorée

1. **Chargement** : Spinner pendant la récupération des données
2. **Erreur** : Message clair avec bouton "Réessayer"
3. **Vide** : Message informatif si aucun élève inscrit
4. **Succès** : Affichage du nom de la classe et nombre d'élèves

## Vérification

Pour vérifier la correction :

1. Se connecter en tant qu'enseignant
2. Aller sur `/academic/attendance/take/`
3. Sélectionner différentes classes autorisées
4. Vérifier que chaque classe affiche ses propres élèves
5. Constater que les noms ne sont plus les mêmes 5 fictifs

## Statut Final

✅ **PROBLÈME RÉSOLU** - Chaque classe affiche maintenant ses propres élèves réels avec sécurité RBAC complète.

Les enseignants voient les vrais élèves inscrits dans chaque classe, et ne peuvent accéder qu'aux classes où ils enseignent.

---

**Date de correction :** 9 septembre 2025  
**Fichiers modifiés :** 
- `academic/views.py` (nouvelle vue `get_classroom_students`)
- `academic/urls.py` (nouvel endpoint API)  
- `templates/academic/attendance_take.html` (JavaScript AJAX réel)
**Impact :** Données réelles au lieu de simulation, sécurité RBAC renforcée
