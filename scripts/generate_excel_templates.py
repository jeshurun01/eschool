#!/usr/bin/env python
"""
Génération de fichiers Excel templates pour l'import de données eSchool.

Usage:
    python scripts/generate_excel_templates.py
"""
import os
import sys
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import pandas as pd
except ImportError:
    print("❌ pandas non installé. Installez-le avec: pip install pandas openpyxl")
    sys.exit(1)


def create_directory_structure():
    """Crée la structure de répertoires pour l'import"""
    base_dir = BASE_DIR / 'import_data'
    directories = [
        'templates',
        '01_base',
        '02_users',
        '03_academic',
        '04_enrollment',
        '05_assessment',
        '06_finance',
        '07_communication'
    ]
    
    for directory in directories:
        path = base_dir / directory
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoire créé: {path}")


def generate_users_template():
    """Génère le template pour les utilisateurs"""
    data = {
        'email': ['jean.dupont@example.com', 'marie.martin@example.com'],
        'password': ['Welcome@2025', 'Welcome@2025'],
        'first_name': ['Jean', 'Marie'],
        'last_name': ['Dupont', 'Martin'],
        'role': ['STUDENT', 'TEACHER'],
        'phone': ['+243 99 123 4567', '+243 99 123 4568'],
        'gender': ['M', 'F'],
        'date_of_birth': ['2010-05-15', '1985-03-22'],
        'address': ['123 Avenue Kasaï, Lubumbashi', '456 Rue Lumumba, Lubumbashi'],
        'is_active': [True, True],
        'preferred_language': ['fr', 'fr']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'users_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Users')
    print(f"✓ Template créé: {output_path}")


def generate_students_template():
    """Génère le template pour les élèves"""
    data = {
        'user_email': ['jean.dupont@example.com', 'marie.martin@example.com'],
        'matricule': ['STU-2024-0001', 'STU-2024-0002'],
        'enrollment_date': ['2024-09-01', '2024-09-01'],
        'parent_emails': ['papa.dupont@example.com;maman.dupont@example.com', 'papa.martin@example.com'],
        'is_graduated': [False, False],
        'graduation_date': ['', '']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'students_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Students')
    print(f"✓ Template créé: {output_path}")


def generate_parents_template():
    """Génère le template pour les parents"""
    data = {
        'user_email': ['papa.dupont@example.com', 'maman.dupont@example.com'],
        'profession': ['Ingénieur', 'Enseignante'],
        'workplace': ['SNEL', 'École Primaire'],
        'relationship': ['FATHER', 'MOTHER']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'parents_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Parents')
    print(f"✓ Template créé: {output_path}")


def generate_teachers_template():
    """Génère le template pour les enseignants"""
    data = {
        'user_email': ['prof.math@example.com', 'prof.francais@example.com'],
        'employee_id': ['TEACH-2024-0001', 'TEACH-2024-0002'],
        'hire_date': ['2024-01-15', '2023-09-01'],
        'education_level': ['Licence en Mathématiques', 'Master en Lettres'],
        'certifications': ['Certifié enseignement secondaire', 'Certifié enseignement secondaire'],
        'salary': [850.00, 900.00],
        'is_head_teacher': [False, True],
        'is_active_employee': [True, True],
        'subject_codes': ['MATH-SEC;GEOM-SEC', 'FRAN-SEC']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'teachers_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Teachers')
    print(f"✓ Template créé: {output_path}")


def generate_academic_years_template():
    """Génère le template pour les années scolaires"""
    data = {
        'name': ['2024-2025', '2025-2026'],
        'start_date': ['2024-09-01', '2025-09-01'],
        'end_date': ['2025-06-30', '2026-06-30'],
        'is_current': [True, False]
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'academic_years_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Academic Years')
    print(f"✓ Template créé: {output_path}")


def generate_levels_template():
    """Génère le template pour les niveaux"""
    data = {
        'name': ['6ème Primaire', '1ère Secondaire', '2ème Secondaire'],
        'code': ['6P', '1S', '2S'],
        'section': ['PRIMAIRE', 'SECONDAIRE', 'SECONDAIRE'],
        'order': [6, 7, 8],
        'description': ['Sixième année primaire', 'Première année secondaire', 'Deuxième année secondaire']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'levels_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Levels')
    print(f"✓ Template créé: {output_path}")


def generate_subjects_template():
    """Génère le template pour les matières"""
    data = {
        'name': ['Mathématiques', 'Français', 'Sciences'],
        'code': ['MATH-SEC', 'FRAN-SEC', 'SCIE-SEC'],
        'description': ['Cours de mathématiques', 'Cours de français', 'Cours de sciences'],
        'coefficient': [3, 2, 2]
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'subjects_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Subjects')
    print(f"✓ Template créé: {output_path}")


def generate_classrooms_template():
    """Génère le template pour les classes"""
    data = {
        'name': ['6ème A', '1ère S A', '2ème S B'],
        'code': ['6PA-2024', '1SA-2024', '2SB-2024'],
        'level_code': ['6P', '1S', '2S'],
        'academic_year_name': ['2024-2025', '2024-2025', '2024-2025'],
        'capacity': [30, 35, 32],
        'head_teacher_email': ['prof.math@example.com', 'prof.francais@example.com', '']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'classrooms_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Classrooms')
    print(f"✓ Template créé: {output_path}")


def generate_enrollments_template():
    """Génère le template pour les inscriptions"""
    data = {
        'student_email': ['jean.dupont@example.com', 'marie.martin@example.com'],
        'classroom_code': ['6PA-2024', '1SA-2024'],
        'academic_year_name': ['2024-2025', '2024-2025'],
        'enrollment_date': ['2024-09-01', '2024-09-01'],
        'status': ['ACTIVE', 'ACTIVE']
    }
    
    df = pd.DataFrame(data)
    output_path = BASE_DIR / 'import_data' / 'templates' / 'enrollments_template.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Enrollments')
    print(f"✓ Template créé: {output_path}")


def generate_readme():
    """Génère un README dans le dossier import_data"""
    readme_content = """# Import Data - Templates Excel

Ce dossier contient les templates Excel pour importer des données dans eSchool.

## Structure

- `templates/` : Fichiers Excel templates avec exemples
- `01_base/` : Années scolaires (à importer en premier)
- `02_users/` : Utilisateurs, élèves, parents, enseignants
- `03_academic/` : Niveaux, matières, classes
- `04_enrollment/` : Inscriptions
- `05_assessment/` : Notes et présences
- `06_finance/` : Frais et paiements
- `07_communication/` : Annonces et messages

## Ordre d'import

1. Années scolaires (`01_base/academic_years.xlsx`)
2. Utilisateurs (`02_users/users.xlsx`)
3. Élèves, Parents, Enseignants (`02_users/students.xlsx`, etc.)
4. Niveaux et Matières (`03_academic/levels.xlsx`, `subjects.xlsx`)
5. Classes (`03_academic/classrooms.xlsx`)
6. Inscriptions (`04_enrollment/enrollments.xlsx`)
7. etc.

## Utilisation

Voir le guide complet: `docs/EXCEL_IMPORT_GUIDE.md`

```bash
# Import d'un fichier unique
python scripts/import_excel_data.py --file import_data/02_users/users.xlsx --model users

# Import complet
python scripts/import_excel_data.py --directory import_data --all
```

## Templates disponibles

Les templates dans `templates/` contiennent:
- Les colonnes requises
- Des exemples de données
- Le format attendu

Copiez ces templates dans les bons répertoires et modifiez les données selon vos besoins.
"""
    
    readme_path = BASE_DIR / 'import_data' / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ README créé: {readme_path}")


def main():
    print("=" * 70)
    print("GÉNÉRATION DES TEMPLATES EXCEL POUR IMPORT DE DONNÉES")
    print("=" * 70)
    print()
    
    # Créer la structure de répertoires
    print("📁 Création de la structure de répertoires...")
    create_directory_structure()
    print()
    
    # Générer les templates
    print("📄 Génération des templates Excel...")
    generate_users_template()
    generate_students_template()
    generate_parents_template()
    generate_teachers_template()
    generate_academic_years_template()
    generate_levels_template()
    generate_subjects_template()
    generate_classrooms_template()
    generate_enrollments_template()
    print()
    
    # Générer le README
    print("📝 Génération du README...")
    generate_readme()
    print()
    
    print("=" * 70)
    print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 70)
    print()
    print("📍 Les templates sont disponibles dans: import_data/templates/")
    print("📖 Consultez import_data/README.md pour les instructions")
    print("📚 Guide complet: docs/EXCEL_IMPORT_GUIDE.md")
    print()
    print("Pour importer des données:")
    print("  1. Copiez les templates dans les bons répertoires (01_base/, 02_users/, etc.)")
    print("  2. Modifiez les données selon vos besoins")
    print("  3. Exécutez: python scripts/import_excel_data.py --directory import_data --all")


if __name__ == '__main__':
    main()
