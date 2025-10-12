# ✅ Amélioration : Documents de session dans la liste par matière

## 📋 Problème

**URL** : `http://localhost:8000/academic/documents/subject/164/`

Les documents partagés via les **sessions de cours** (modèle `SessionDocument`) n'apparaissaient **pas** dans la liste des documents d'une matière.

### Contexte

Dans le système, il existe **deux façons** de créer des documents :

1. **Documents directs** : Créés directement et liés à une matière via `Document.subject`
2. **Documents de session** : Partagés pendant une session de cours via `SessionDocument`

Le problème est que la vue `document_subject_list` affichait **seulement les documents directs**, ignorant complètement les documents partagés dans les sessions.

## 🔍 Architecture des modèles

### Modèle Document

```python
class Document(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Lien direct
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, null=True, blank=True)
    # ...
```

### Modèle SessionDocument (lien intermédiaire)

```python
class SessionDocument(models.Model):
    """Document lié à une session spécifique"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='documents')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='session_links')
    
    shared_at = models.DateTimeField(auto_now_add=True)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_mandatory = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
```

### Modèle Session

```python
class Session(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    date = models.DateField()
    # ...
```

### Modèle Timetable

```python
class Timetable(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Lien vers la matière
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    # ...
```

### Chaîne de relations

```
SessionDocument → Session → Timetable → Subject
     ↓
  Document
```

## ❌ Code avant (incomplet)

```python
@teacher_or_student_required
def document_subject_list(request, subject_id):
    """Liste des documents d'une matière (pour étudiants et enseignants)"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Vérifier les permissions
    can_access = False
    
    # ❌ Récupère SEULEMENT les documents avec subject=subject_id
    documents = Document.objects.filter(subject=subject)
    
    # ... reste du code
```

**Problème** : Cette requête ne récupère que les documents où `Document.subject = subject`, ignorant les documents liés via `SessionDocument`.

## ✅ Code après (complet)

```python
@teacher_or_student_required
def document_subject_list(request, subject_id):
    """Liste des documents d'une matière (pour étudiants et enseignants)"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Vérifier les permissions
    can_access = False
    
    # ✅ 1. Récupérer les documents directs de la matière
    documents = Document.objects.filter(subject=subject)
    
    # ✅ 2. Récupérer aussi les documents partagés via les sessions de cette matière
    from academic.models import SessionDocument, Session
    session_document_ids = SessionDocument.objects.filter(
        session__timetable__subject=subject  # Suivre la chaîne : SessionDocument → Session → Timetable → Subject
    ).values_list('document_id', flat=True).distinct()
    
    # ✅ 3. Combiner les deux sources de documents
    all_document_ids = set(documents.values_list('id', flat=True)) | set(session_document_ids)
    documents = Document.objects.filter(id__in=all_document_ids)
    
    # ... reste du code (permissions, etc.)
```

## 🔍 Explication technique

### Étape 1 : Documents directs

```python
documents = Document.objects.filter(subject=subject)
```

Récupère tous les documents où `Document.subject` pointe directement vers la matière.

### Étape 2 : Documents de session

```python
session_document_ids = SessionDocument.objects.filter(
    session__timetable__subject=subject
).values_list('document_id', flat=True).distinct()
```

**Requête SQL générée** (simplifié) :
```sql
SELECT DISTINCT sd.document_id
FROM academic_sessiondocument sd
JOIN academic_session s ON sd.session_id = s.id
JOIN academic_timetable t ON s.timetable_id = t.id
WHERE t.subject_id = 164
```

Suit la chaîne de relations :
1. `SessionDocument` → `session` (ForeignKey)
2. `Session` → `timetable` (ForeignKey)
3. `Timetable` → `subject` (ForeignKey)

### Étape 3 : Combinaison

```python
all_document_ids = set(documents.values_list('id', flat=True)) | set(session_document_ids)
documents = Document.objects.filter(id__in=all_document_ids)
```

Utilise un **set union** (`|`) pour combiner les deux sources sans doublons, puis récupère tous les documents en une seule requête.

## 📊 Impact

### Avant

| Type de document | Affiché ? |
|------------------|-----------|
| Documents directs (Document.subject) | ✅ Oui |
| Documents de session (SessionDocument) | ❌ **Non** |

**Exemple** :
- Un enseignant partage un PDF pendant un cours de Mathématiques via une Session
- L'élève ne peut **pas** le retrouver dans `/academic/documents/subject/164/` (Mathématiques)
- L'élève doit aller dans la page de la Session spécifique

### Après

| Type de document | Affiché ? |
|------------------|-----------|
| Documents directs (Document.subject) | ✅ Oui |
| Documents de session (SessionDocument) | ✅ **Oui** |

**Exemple** :
- Un enseignant partage un PDF pendant un cours de Mathématiques via une Session
- L'élève **peut** le retrouver dans `/academic/documents/subject/164/` (Mathématiques)
- Tous les documents de la matière sont centralisés au même endroit

## 🧪 Test

### Scénario de test

1. **Créer une session de cours** (Mathématiques, 6ème A)
2. **Partager un document** dans cette session via `SessionDocument`
3. **Vérifier** que le document n'a **pas** `subject=Mathématiques` directement
4. **Accéder** à `/academic/documents/subject/<mathématiques_id>/`
5. **Vérifier** que le document apparaît maintenant dans la liste

### Test via Django shell

```python
# python manage.py shell

from academic.models import Subject, Document, SessionDocument, Session

# Récupérer une matière
math = Subject.objects.get(name='Mathématiques')

# Documents directs
direct_docs = Document.objects.filter(subject=math)
print(f"Documents directs : {direct_docs.count()}")

# Documents de session
session_doc_ids = SessionDocument.objects.filter(
    session__timetable__subject=math
).values_list('document_id', flat=True).distinct()
print(f"Documents de session : {len(session_doc_ids)}")

# Total combiné (nouvelle logique)
all_doc_ids = set(direct_docs.values_list('id', flat=True)) | set(session_doc_ids)
all_docs = Document.objects.filter(id__in=all_doc_ids)
print(f"Total documents : {all_docs.count()}")

# Afficher quelques exemples
for doc in all_docs[:5]:
    is_session_doc = doc.id in session_doc_ids
    print(f"  - {doc.title} {'[Session]' if is_session_doc else '[Direct]'}")
```

## 💡 Avantages de cette amélioration

1. **Centralisation** : Tous les documents d'une matière sont accessibles au même endroit
2. **Cohérence** : Peu importe comment un document a été partagé, il apparaît dans la liste
3. **UX améliorée** : Les élèves n'ont plus besoin de naviguer dans chaque session pour trouver les documents
4. **Recherche facilitée** : Un seul point d'entrée pour tous les documents d'une matière

## 🔧 Performance

### Nombre de requêtes

**Avant** : 1 requête
```sql
SELECT * FROM academic_document WHERE subject_id = 164
```

**Après** : 3 requêtes optimisées
```sql
-- 1. Documents directs (IDs)
SELECT id FROM academic_document WHERE subject_id = 164

-- 2. Documents de session (IDs)
SELECT DISTINCT document_id FROM academic_sessiondocument sd
JOIN academic_session s ON sd.session_id = s.id
JOIN academic_timetable t ON s.timetable_id = t.id
WHERE t.subject_id = 164

-- 3. Récupération finale (avec prefetch)
SELECT * FROM academic_document WHERE id IN (...)
```

**Optimisation** : Utilisation de `values_list('id', flat=True)` pour récupérer uniquement les IDs, puis une seule requête finale avec `id__in`.

## 📝 Fichiers modifiés

- `academic/views/main_views.py` (fonction `document_subject_list`, ligne ~1950)
  - Ajout de l'import `SessionDocument` et `Session`
  - Récupération des documents de session via la chaîne de relations
  - Combinaison des deux sources avec un set union

## 🎯 Résultat

La page `/academic/documents/subject/<id>/` affiche maintenant **tous les documents** liés à la matière :
- ✅ Documents créés directement avec `subject=<matière>`
- ✅ Documents partagés via les sessions de cours de cette matière
- ✅ Sans doublons
- ✅ Avec les bonnes permissions (élèves voient seulement leur classe)

---

**Date** : 12 octobre 2025  
**Statut** : ✅ **Implémenté et testé**  
**Impact** : 🟢 **Amélioration significative de l'UX**
