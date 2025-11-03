# Guide d'Import de Données Excel - eSchool

## Vue d'ensemble

Ce guide explique comment importer en masse des données dans eSchool depuis des fichiers Excel.

## Prérequis

### 1. Installation des dépendances

```bash
pip install pandas openpyxl
```

Ou avec uv:
```bash
uv pip install pandas openpyxl
```

### 2. Structure des répertoires

Créer l'arborescence suivante:

```
import_data/
├── 01_base/
│   └── academic_years.xlsx
├── 02_users/
│   ├── users.xlsx
│   ├── students.xlsx
│   ├── parents.xlsx
│   └── teachers.xlsx
├── 03_academic/
│   ├── levels.xlsx
│   ├── subjects.xlsx
│   ├── classrooms.xlsx
│   └── teacher_assignments.xlsx
├── 04_enrollment/
│   ├── enrollments.xlsx
│   └── timetables.xlsx
├── 05_assessment/
│   ├── grades.xlsx
│   └── attendance.xlsx
└── 06_finance/
    ├── fee_types.xlsx
    ├── fee_structures.xlsx
    └── invoices.xlsx
```

## Ordre d'import recommandé

**IMPORTANT**: Respecter cet ordre pour éviter les erreurs de clés étrangères.

1. **Années scolaires** (`academic_years.xlsx`)
2. **Utilisateurs** (`users.xlsx`)
3. **Élèves, Parents, Enseignants** (`students.xlsx`, `parents.xlsx`, `teachers.xlsx`)
4. **Niveaux, Matières** (`levels.xlsx`, `subjects.xlsx`)
5. **Classes** (`classrooms.xlsx`)
6. **Affectations enseignants** (`teacher_assignments.xlsx`)
7. **Inscriptions** (`enrollments.xlsx`)
8. **Emplois du temps** (`timetables.xlsx`)
9. **Notes et présences** (`grades.xlsx`, `attendance.xlsx`)
10. **Finances** (`fee_types.xlsx`, `fee_structures.xlsx`, `invoices.xlsx`)

## Utilisation du script d'import

### Import d'un fichier unique

```bash
python scripts/import_excel_data.py \
    --file import_data/02_users/users.xlsx \
    --model users
```

### Import complet (tous les fichiers)

```bash
python scripts/import_excel_data.py --directory import_data --all
```

### Options disponibles

- `--file`: Chemin vers le fichier Excel
- `--model`: Type de modèle (users, students, parents, teachers, academic_years)
- `--directory`: Répertoire contenant les fichiers (défaut: import_data)
- `--all`: Importer tous les fichiers dans l'ordre recommandé
- `--verbose`: Mode verbeux (actif par défaut)

## Format des fichiers Excel

### 1. users.xlsx

| Colonne | Type | Requis | Exemple |
|---------|------|--------|---------|
| email | Email | Oui | jean.dupont@example.com |
| password | Texte | Oui | Welcome@2025 |
| first_name | Texte | Oui | Jean |
| last_name | Texte | Oui | Dupont |
| role | Choix | Oui | STUDENT / PARENT / TEACHER / ADMIN |
| phone | Texte | Non | +243 99 123 4567 |
| gender | Choix | Non | M / F / O |
| date_of_birth | Date | Non | 2010-05-15 |
| address | Texte | Non | 123 Avenue Kasaï |
| is_active | Booléen | Non | TRUE / FALSE |
| preferred_language | Texte | Non | fr / en |

**Note**: Le mot de passe sera hashé automatiquement lors de l'import.

### 2. students.xlsx

| Colonne | Type | Requis | Exemple |
|---------|------|--------|---------|
| user_email | Email | Oui | jean.dupont@example.com |
| matricule | Texte | Non | STU-2024-0001 |
| enrollment_date | Date | Non | 2024-09-01 |
| parent_emails | Texte | Non | papa@example.com;maman@example.com |
| is_graduated | Booléen | Non | FALSE |
| graduation_date | Date | Non | 2030-06-30 |

**Note**: `parent_emails` peut contenir plusieurs emails séparés par `;`

### 3. parents.xlsx

| Colonne | Type | Requis | Exemple |
|---------|------|--------|---------|
| user_email | Email | Oui | papa.dupont@example.com |
| profession | Texte | Non | Ingénieur |
| workplace | Texte | Non | SNEL |
| relationship | Choix | Non | FATHER / MOTHER / GUARDIAN |

### 4. teachers.xlsx

| Colonne | Type | Requis | Exemple |
|---------|------|--------|---------|
| user_email | Email | Oui | prof.math@example.com |
| employee_id | Texte | Non | TEACH-2024-0001 |
| hire_date | Date | Non | 2024-01-15 |
| education_level | Texte | Non | Licence en Mathématiques |
| certifications | Texte | Non | Certifié enseignement secondaire |
| salary | Nombre | Non | 850.00 |
| is_head_teacher | Booléen | Non | FALSE |
| is_active_employee | Booléen | Non | TRUE |
| subject_codes | Texte | Non | MATH-SEC;PHYS-SEC |

**Note**: `subject_codes` peut contenir plusieurs codes séparés par `;`

### 5. academic_years.xlsx

| Colonne | Type | Requis | Exemple |
|---------|------|--------|---------|
| name | Texte | Oui | 2024-2025 |
| start_date | Date | Oui | 2024-09-01 |
| end_date | Date | Oui | 2025-06-30 |
| is_current | Booléen | Non | TRUE |

## Conseils pour la préparation des données

### 1. Format des dates

Utiliser le format **YYYY-MM-DD** (ISO 8601):
- ✅ Correct: `2024-09-01`
- ❌ Incorrect: `01/09/2024` ou `1-9-24`

### 2. Format des booléens

- Valeurs acceptées: `TRUE`, `FALSE`, `1`, `0`, `true`, `false`
- Laisser vide = FALSE par défaut

### 3. Emails

- Tous les emails doivent être uniques
- Format valide requis: `utilisateur@domaine.com`
- Les emails sont la clé primaire pour les utilisateurs

### 4. Codes et identifiants

- Respecter les formats suggérés:
  - Matricule élève: `STU-2024-0001`
  - ID enseignant: `TEACH-2024-0001`
  - Code matière: `MATH-SEC`, `PHYS-PRI`
  - Code classe: `6A-2024`

### 5. Relations multiples

Pour les champs acceptant plusieurs valeurs (parents, matières):
- Séparer par point-virgule: `valeur1;valeur2;valeur3`
- Pas d'espace avant/après le point-virgule

### 6. Cellules vides

- Les colonnes "Non requis" peuvent être laissées vides
- Les valeurs par défaut seront appliquées automatiquement

## Validation des données

### Vérifications automatiques

Le script effectue les validations suivantes:

1. **Unicité des emails**: Vérifie qu'aucun email n'est dupliqué
2. **Format des dates**: Valide le format ISO 8601
3. **Clés étrangères**: Vérifie l'existence des relations (user, parent, subject, etc.)
4. **Choix valides**: Vérifie que les valeurs correspondent aux choix définis

### Gestion des erreurs

- **Erreurs bloquantes**: L'import s'arrête pour les erreurs critiques
- **Avertissements**: L'import continue mais signale les problèmes
- **Transactions**: Chaque ligne est importée dans une transaction (rollback en cas d'erreur)

## Exemples de fichiers

### Exemple: users.xlsx

```
email                          | password      | first_name | last_name | role    | phone           | gender | date_of_birth
jean.dupont@example.com        | Welcome@2025  | Jean       | Dupont    | STUDENT | +243991234567   | M      | 2010-05-15
marie.martin@example.com       | Welcome@2025  | Marie      | Martin    | STUDENT | +243991234568   | F      | 2011-03-22
papa.dupont@example.com        | Welcome@2025  | Pierre     | Dupont    | PARENT  | +243991234569   | M      | 1980-08-10
prof.math@example.com          | Welcome@2025  | Sophie     | Lambert   | TEACHER | +243991234570   | F      | 1985-11-05
```

### Exemple: students.xlsx

```
user_email              | matricule      | enrollment_date | parent_emails                              | is_graduated
jean.dupont@example.com | STU-2024-0001  | 2024-09-01      | papa.dupont@example.com;maman.dupont@...  | FALSE
marie.martin@example.com| STU-2024-0002  | 2024-09-01      | papa.martin@example.com                    | FALSE
```

## Dépannage

### Erreur: "Utilisateur non trouvé"

**Cause**: Le fichier students/parents/teachers fait référence à un email inexistant.

**Solution**: 
1. Vérifier que `users.xlsx` a été importé en premier
2. Vérifier l'orthographe de l'email dans les deux fichiers

### Erreur: "Invalid date format"

**Cause**: Format de date non reconnu.

**Solution**: Utiliser le format `YYYY-MM-DD` (exemple: `2024-09-01`)

### Erreur: "Duplicate entry"

**Cause**: Email ou identifiant déjà existant dans la base.

**Solution**: 
1. Vérifier les doublons dans le fichier Excel
2. Supprimer les entrées existantes en base (si souhaité)
3. Le script mettra à jour les enregistrements existants au lieu de créer des doublons

### Avertissement: "Parent non trouvé"

**Cause**: L'email du parent n'existe pas dans la base.

**Solution**: 
1. Importer d'abord `parents.xlsx`
2. Vérifier l'orthographe de l'email

### Performance lente

**Cause**: Grand volume de données.

**Conseils**:
1. Importer par lots de 1000 lignes maximum
2. Diviser les grands fichiers en plusieurs petits fichiers
3. Désactiver les signaux Django temporairement (si nombreuses règles métier)

## Après l'import

### 1. Vérification

```bash
# Se connecter au shell Django
python manage.py shell

# Vérifier les statistiques
from accounts.models import User, Student, Teacher, Parent
print(f"Utilisateurs: {User.objects.count()}")
print(f"Élèves: {Student.objects.count()}")
print(f"Parents: {Parent.objects.count()}")
print(f"Enseignants: {Teacher.objects.count()}")
```

### 2. Tests de connexion

- Essayer de se connecter avec quelques comptes importés
- Vérifier que les relations parent-élève sont correctes
- Vérifier les affectations enseignant-matière

### 3. Nettoyage

Si des erreurs subsistent:

```bash
# Supprimer toutes les données importées (ATTENTION: irréversible!)
python manage.py shell

from accounts.models import User
User.objects.filter(is_superuser=False).delete()
```

## Scripts additionnels

### Génération de fichiers Excel templates

```python
# scripts/generate_excel_templates.py
import pandas as pd

# Template users
users_template = pd.DataFrame({
    'email': ['exemple@example.com'],
    'password': ['Welcome@2025'],
    'first_name': ['Prénom'],
    'last_name': ['Nom'],
    'role': ['STUDENT'],
    'phone': ['+243 99 123 4567'],
    'gender': ['M'],
    'date_of_birth': ['2010-01-01'],
    'address': ['Adresse complète'],
    'is_active': [True],
    'preferred_language': ['fr']
})

users_template.to_excel('import_data/templates/users_template.xlsx', index=False)
print("✓ Template users créé")
```

### Export des données existantes

```python
# scripts/export_to_excel.py
from accounts.models import User
import pandas as pd

users = User.objects.values(
    'email', 'first_name', 'last_name', 'role',
    'phone', 'gender', 'date_of_birth', 'address'
)

df = pd.DataFrame(list(users))
df.to_excel('export_data/users_export.xlsx', index=False)
print(f"✓ {len(df)} utilisateurs exportés")
```

## Support

En cas de problème:

1. Consulter les logs générés par le script
2. Vérifier le fichier `docs/DATA_SCHEMAS_FOR_IMPORT.md` pour les spécifications complètes
3. Contacter l'équipe de développement avec:
   - Le fichier Excel problématique
   - Les messages d'erreur complets
   - La version de Python et pandas utilisée

## Sécurité

⚠️ **Important**:

- **Mots de passe**: Changez tous les mots de passe après l'import initial
- **Données sensibles**: Ne partagez pas les fichiers Excel contenant des données réelles
- **Backup**: Sauvegardez la base de données avant un import massif
- **Test**: Testez d'abord sur un environnement de développement

```bash
# Backup avant import
python manage.py dumpdata > backup_before_import.json

# Restauration si nécessaire
python manage.py loaddata backup_before_import.json
```
