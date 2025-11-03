#!/usr/bin/env python
"""
Script d'import de données depuis fichiers Excel vers la base de données eSchool.

Usage:
    python scripts/import_excel_data.py --help
    python scripts/import_excel_data.py --file import_data/01_base/users.xlsx --model users
    python scripts/import_excel_data.py --directory import_data --all

Requirements:
    pip install pandas openpyxl
"""
import os
import sys
import argparse
import django
import pandas as pd
from datetime import datetime
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from accounts.models import Student, Parent, Teacher, Profile
from academic.models import (
    AcademicYear, Level, Subject, ClassRoom,
    TeacherAssignment, Enrollment, Grade, Attendance, Timetable, Document
)
from finance.models import (
    FeeType, FeeStructure, PaymentMethod,
    Invoice, InvoiceItem, Payment
)
from communication.models import Announcement, Message

User = get_user_model()


class ExcelDataImporter:
    """Classe principale pour l'import de données Excel"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.stats = {}
        
    def log(self, message, level='INFO'):
        """Log des messages avec timestamp"""
        if not self.verbose and level == 'INFO':
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '→',
            'SUCCESS': '✓',
            'WARNING': '⚠',
            'ERROR': '✗'
        }.get(level, '•')
        print(f"[{timestamp}] {prefix} {message}")
    
    def safe_get(self, row, key, default=''):
        """Récupère une valeur de manière sécurisée"""
        value = row.get(key, default)
        if pd.isna(value):
            return default
        return value
    
    def parse_date(self, date_str):
        """Parse une date depuis string ou pandas Timestamp"""
        if pd.isna(date_str):
            return None
        if isinstance(date_str, pd.Timestamp):
            return date_str.date()
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None
        return date_str
    
    def parse_datetime(self, datetime_str):
        """Parse un datetime depuis string"""
        if pd.isna(datetime_str):
            return None
        if isinstance(datetime_str, pd.Timestamp):
            return timezone.make_aware(datetime_str.to_pydatetime())
        return None
    
    # ========== IMPORT USERS & ACCOUNTS ==========
    
    def import_users(self, file_path):
        """Import des utilisateurs depuis Excel"""
        self.log(f"Import des utilisateurs depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        updated_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    email = row['email']
                    defaults = {
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'role': row['role'],
                        'phone': self.safe_get(row, 'phone'),
                        'gender': self.safe_get(row, 'gender'),
                        'address': self.safe_get(row, 'address'),
                        'is_active': self.safe_get(row, 'is_active', True),
                        'preferred_language': self.safe_get(row, 'preferred_language', 'fr'),
                    }
                    
                    date_of_birth = self.parse_date(self.safe_get(row, 'date_of_birth'))
                    if date_of_birth:
                        defaults['date_of_birth'] = date_of_birth
                    
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults=defaults
                    )
                    
                    if created:
                        user.set_password(row['password'])
                        user.save()
                        created_count += 1
                        self.log(f"Utilisateur créé: {user.email}", 'SUCCESS')
                    else:
                        # Mettre à jour si nécessaire
                        for key, value in defaults.items():
                            setattr(user, key, value)
                        user.save()
                        updated_count += 1
                        self.log(f"Utilisateur mis à jour: {user.email}", 'WARNING')
            
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['users_created'] = created_count
        self.stats['users_updated'] = updated_count
        self.log(f"✓ {created_count} utilisateurs créés, {updated_count} mis à jour", 'SUCCESS')
        return created_count, updated_count
    
    def import_students(self, file_path):
        """Import des élèves depuis Excel"""
        self.log(f"Import des élèves depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    user = User.objects.get(email=row['user_email'])
                    
                    defaults = {
                        'matricule': self.safe_get(row, 'matricule', ''),
                        'enrollment_date': self.parse_date(self.safe_get(row, 'enrollment_date')) or timezone.now().date(),
                        'is_graduated': self.safe_get(row, 'is_graduated', False),
                    }
                    
                    graduation_date = self.parse_date(self.safe_get(row, 'graduation_date'))
                    if graduation_date:
                        defaults['graduation_date'] = graduation_date
                    
                    student, created = Student.objects.get_or_create(
                        user=user,
                        defaults=defaults
                    )
                    
                    if created:
                        created_count += 1
                        self.log(f"Élève créé: {student.matricule} ({user.email})", 'SUCCESS')
                    
                    # Associer les parents si spécifiés
                    parent_emails = self.safe_get(row, 'parent_emails')
                    if parent_emails:
                        for parent_email in parent_emails.split(';'):
                            parent_email = parent_email.strip()
                            try:
                                parent_user = User.objects.get(email=parent_email)
                                parent = parent_user.parent_profile
                                student.parents.add(parent)
                                self.log(f"Parent {parent_email} associé à {student.matricule}", 'INFO')
                            except User.DoesNotExist:
                                self.log(f"Parent {parent_email} non trouvé pour {student.matricule}", 'WARNING')
                            except Exception:
                                pass
            
            except User.DoesNotExist:
                error_msg = f"Erreur ligne {index + 2}: Utilisateur {row['user_email']} non trouvé"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['students'] = created_count
        self.log(f"✓ {created_count} élèves créés", 'SUCCESS')
        return created_count
    
    def import_parents(self, file_path):
        """Import des parents depuis Excel"""
        self.log(f"Import des parents depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    user = User.objects.get(email=row['user_email'])
                    
                    defaults = {
                        'profession': self.safe_get(row, 'profession'),
                        'workplace': self.safe_get(row, 'workplace'),
                        'relationship': self.safe_get(row, 'relationship', 'FATHER'),
                    }
                    
                    parent, created = Parent.objects.get_or_create(
                        user=user,
                        defaults=defaults
                    )
                    
                    if created:
                        created_count += 1
                        self.log(f"Parent créé: {user.email}", 'SUCCESS')
            
            except User.DoesNotExist:
                error_msg = f"Erreur ligne {index + 2}: Utilisateur {row['user_email']} non trouvé"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['parents'] = created_count
        self.log(f"✓ {created_count} parents créés", 'SUCCESS')
        return created_count
    
    def import_teachers(self, file_path):
        """Import des enseignants depuis Excel"""
        self.log(f"Import des enseignants depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    user = User.objects.get(email=row['user_email'])
                    
                    defaults = {
                        'employee_id': self.safe_get(row, 'employee_id', ''),
                        'hire_date': self.parse_date(self.safe_get(row, 'hire_date')) or timezone.now().date(),
                        'education_level': self.safe_get(row, 'education_level'),
                        'certifications': self.safe_get(row, 'certifications'),
                        'is_head_teacher': self.safe_get(row, 'is_head_teacher', False),
                        'is_active_employee': self.safe_get(row, 'is_active_employee', True),
                    }
                    
                    salary = self.safe_get(row, 'salary')
                    if salary:
                        defaults['salary'] = Decimal(str(salary))
                    
                    teacher, created = Teacher.objects.get_or_create(
                        user=user,
                        defaults=defaults
                    )
                    
                    if created:
                        created_count += 1
                        self.log(f"Enseignant créé: {teacher.employee_id} ({user.email})", 'SUCCESS')
                    
                    # Associer les matières si spécifiées
                    subject_codes = self.safe_get(row, 'subject_codes')
                    if subject_codes:
                        for code in subject_codes.split(';'):
                            code = code.strip()
                            try:
                                subject = Subject.objects.get(code=code)
                                teacher.subjects.add(subject)
                                self.log(f"Matière {code} associée à {teacher.employee_id}", 'INFO')
                            except Subject.DoesNotExist:
                                self.log(f"Matière {code} non trouvée pour {teacher.employee_id}", 'WARNING')
            
            except User.DoesNotExist:
                error_msg = f"Erreur ligne {index + 2}: Utilisateur {row['user_email']} non trouvé"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['teachers'] = created_count
        self.log(f"✓ {created_count} enseignants créés", 'SUCCESS')
        return created_count
    
    # ========== IMPORT ACADEMIC ==========
    
    def import_academic_years(self, file_path):
        """Import des années scolaires depuis Excel"""
        self.log(f"Import des années scolaires depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    defaults = {
                        'start_date': self.parse_date(row['start_date']),
                        'end_date': self.parse_date(row['end_date']),
                        'is_current': self.safe_get(row, 'is_current', False),
                    }
                    
                    year, created = AcademicYear.objects.get_or_create(
                        name=row['name'],
                        defaults=defaults
                    )
                    
                    if created:
                        created_count += 1
                        self.log(f"Année scolaire créée: {year.name}", 'SUCCESS')
            
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['academic_years'] = created_count
        self.log(f"✓ {created_count} années scolaires créées", 'SUCCESS')
        return created_count
    
    # Ajouter d'autres méthodes d'import...
    
    def print_summary(self):
        """Affiche le résumé de l'import"""
        self.log("=" * 70)
        self.log("RÉSUMÉ DE L'IMPORT", 'SUCCESS')
        self.log("=" * 70)
        
        for model, count in self.stats.items():
            self.log(f"{model}: {count} enregistrements", 'INFO')
        
        if self.warnings:
            self.log(f"\n⚠ {len(self.warnings)} avertissements:", 'WARNING')
            for warning in self.warnings[:10]:  # Afficher les 10 premiers
                self.log(warning, 'WARNING')
        
        if self.errors:
            self.log(f"\n✗ {len(self.errors)} erreurs:", 'ERROR')
            for error in self.errors[:10]:  # Afficher les 10 premières
                self.log(error, 'ERROR')
        else:
            self.log("\n✓ Import terminé sans erreur!", 'SUCCESS')


def main():
    parser = argparse.ArgumentParser(
        description='Import de données Excel vers la base de données eSchool'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Chemin vers le fichier Excel à importer'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['users', 'students', 'parents', 'teachers', 'academic_years'],
        help='Type de modèle à importer'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='import_data',
        help='Répertoire contenant les fichiers d\'import (défaut: import_data)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Importer tous les fichiers dans l\'ordre recommandé'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=True,
        help='Mode verbeux (actif par défaut)'
    )
    
    args = parser.parse_args()
    
    importer = ExcelDataImporter(verbose=args.verbose)
    
    if args.file and args.model:
        # Import d'un fichier spécifique
        method_name = f'import_{args.model}'
        if hasattr(importer, method_name):
            method = getattr(importer, method_name)
            method(args.file)
        else:
            print(f"Erreur: Modèle '{args.model}' non supporté")
            return 1
    
    elif args.all:
        # Import complet dans l'ordre
        import_sequence = [
            ('01_base/academic_years.xlsx', 'academic_years'),
            ('02_users/users.xlsx', 'users'),
            ('02_users/students.xlsx', 'students'),
            ('02_users/parents.xlsx', 'parents'),
            ('02_users/teachers.xlsx', 'teachers'),
            # Ajouter d'autres fichiers...
        ]
        
        for file_path, model in import_sequence:
            full_path = os.path.join(args.directory, file_path)
            if os.path.exists(full_path):
                method = getattr(importer, f'import_{model}')
                method(full_path)
            else:
                importer.log(f"Fichier non trouvé: {full_path}", 'WARNING')
    
    else:
        parser.print_help()
        return 1
    
    importer.print_summary()
    return 0 if not importer.errors else 1


if __name__ == '__main__':
    sys.exit(main())
