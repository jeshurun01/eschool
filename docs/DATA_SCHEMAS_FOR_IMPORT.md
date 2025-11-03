# 📊 Schémas de Données pour Import Excel

Ce document décrit les schémas de données pour tous les modèles du projet eSchool. Utilisez ces structures pour préparer vos fichiers Excel/CSV en vue d'un import massif dans la base de données.

## 📑 Table des Matières

1. [Comptes & Utilisateurs](#1-comptes--utilisateurs)
2. [Académique](#2-académique)
3. [Finance](#3-finance)
4. [Communication](#4-communication)
5. [Scripts d'Import](#5-scripts-dimport)

---

## 1. Comptes & Utilisateurs

### 1.1 User (Utilisateurs)

**Fichier Excel**: `users.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| email | texte | ✅ | email valide | Adresse email unique | jean.dupont@eschool.cd |
| first_name | texte | ✅ | - | Prénom | Jean |
| last_name | texte | ✅ | - | Nom de famille | Dupont |
| password | texte | ✅ | - | Mot de passe (sera hashé) | Password123! |
| phone | texte | ❌ | - | Numéro de téléphone | +243 812 345 678 |
| role | texte | ✅ | STUDENT, PARENT, TEACHER, ADMIN, FINANCE, SUPER_ADMIN | Rôle de l'utilisateur | STUDENT |
| gender | texte | ❌ | M, F | Genre | M |
| date_of_birth | date | ❌ | YYYY-MM-DD | Date de naissance | 2010-05-15 |
| address | texte | ❌ | - | Adresse complète | 123 Avenue de la Paix, Lubumbashi |
| is_active | booléen | ❌ | TRUE/FALSE | Compte actif | TRUE |
| preferred_language | texte | ❌ | fr, en | Langue préférée | fr |

**Notes importantes:**
- L'email doit être unique
- Le mot de passe sera automatiquement hashé lors de l'import
- Pour créer un super admin, utilisez role="SUPER_ADMIN"

---

### 1.2 Student (Élèves)

**Fichier Excel**: `students.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| user_email | texte | ✅ | Email de l'utilisateur associé | eleve1@eschool.cd |
| matricule | texte | ❌ | Matricule (auto-généré si vide) | STU20250001 |
| enrollment_date | date | ❌ | Date d'inscription | 2025-09-01 |
| current_class_name | texte | ❌ | Nom de la classe actuelle | 6ème A |
| parent_emails | texte | ❌ | Emails des parents (séparés par ;) | parent1@email.com;parent2@email.com |
| is_graduated | booléen | ❌ | Élève diplômé | FALSE |
| graduation_date | date | ❌ | Date de diplôme | - |

**Format matricule auto-généré**: `STU{ANNÉE}{NUMÉRO}` (ex: STU20250001)

---

### 1.3 Parent (Parents/Tuteurs)

**Fichier Excel**: `parents.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| user_email | texte | ✅ | - | Email de l'utilisateur associé | parent1@eschool.cd |
| profession | texte | ❌ | - | Profession | Ingénieur |
| workplace | texte | ❌ | - | Lieu de travail | Gécamines |
| relationship | texte | ❌ | FATHER, MOTHER, GUARDIAN, OTHER | Lien de parenté | FATHER |

---

### 1.4 Teacher (Enseignants)

**Fichier Excel**: `teachers.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| user_email | texte | ✅ | Email de l'utilisateur associé | prof1@eschool.cd |
| employee_id | texte | ❌ | ID employé (auto-généré si vide) | TEA20250001 |
| hire_date | date | ❌ | Date d'embauche | 2025-01-15 |
| salary | décimal | ❌ | Salaire mensuel | 5000.00 |
| subject_codes | texte | ❌ | Codes des matières enseignées (séparés par ;) | MATH;PHYS |
| education_level | texte | ❌ | Niveau d'éducation | Licence en Mathématiques |
| certifications | texte | ❌ | Certifications | CAPES, Formation continue |
| is_head_teacher | booléen | ❌ | Professeur principal | FALSE |
| is_active_employee | booléen | ❌ | Employé actif | TRUE |

**Format employee_id auto-généré**: `TEA{ANNÉE}{NUMÉRO}` (ex: TEA20250001)

---

## 2. Académique

### 2.1 AcademicYear (Années Scolaires)

**Fichier Excel**: `academic_years.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| name | texte | ✅ | Nom de l'année scolaire | 2024-2025 |
| start_date | date | ✅ | Date de début | 2024-09-01 |
| end_date | date | ✅ | Date de fin | 2025-06-30 |
| is_current | booléen | ❌ | Année courante (une seule à TRUE) | TRUE |

**Note**: Une seule année scolaire peut être marquée comme courante à la fois.

---

### 2.2 Level (Niveaux)

**Fichier Excel**: `levels.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| name | texte | ✅ | Nom du niveau | Primaire |
| description | texte | ❌ | Description | Classes de 1ère à 6ème année |
| order | entier | ❌ | Ordre d'affichage | 1 |

**Exemples de niveaux**:
- Primaire (order: 1)
- Secondaire (order: 2)
- Humanités (order: 3)

---

### 2.3 Subject (Matières)

**Fichier Excel**: `subjects.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| name | texte | ✅ | Nom de la matière | Mathématiques |
| code | texte | ✅ | Code unique | MATH |
| description | texte | ❌ | Description | Algèbre, géométrie, calcul |
| coefficient | décimal | ❌ | Coefficient | 2.0 |
| color | texte | ❌ | Couleur hex | #3B82F6 |
| level_names | texte | ❌ | Niveaux (séparés par ;) | Primaire;Secondaire |

**Codes de matières recommandés**:
- MATH (Mathématiques)
- FR (Français)
- EN (Anglais)
- PHYS (Physique)
- CHEM (Chimie)
- BIO (Biologie)
- HIST (Histoire)
- GEO (Géographie)
- EPS (Éducation Physique)

---

### 2.4 ClassRoom (Classes)

**Fichier Excel**: `classrooms.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| name | texte | ✅ | Nom de la classe | 6ème A |
| level_name | texte | ✅ | Nom du niveau | Primaire |
| academic_year_name | texte | ✅ | Nom de l'année scolaire | 2024-2025 |
| head_teacher_email | texte | ❌ | Email du professeur principal | prof.principal@eschool.cd |
| capacity | entier | ❌ | Capacité maximale | 30 |
| room_number | texte | ❌ | Numéro de salle | A101 |

**Note**: La combinaison (name, level, academic_year) doit être unique.

---

### 2.5 TeacherAssignment (Attribution Enseignant-Classe-Matière)

**Fichier Excel**: `teacher_assignments.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| teacher_email | texte | ✅ | Email de l'enseignant | prof1@eschool.cd |
| classroom_name | texte | ✅ | Nom de la classe | 6ème A |
| subject_code | texte | ✅ | Code de la matière | MATH |
| academic_year_name | texte | ✅ | Nom de l'année scolaire | 2024-2025 |
| hours_per_week | entier | ❌ | Heures par semaine | 4 |

**Note**: La combinaison (teacher, classroom, subject, academic_year) doit être unique.

---

### 2.6 Enrollment (Inscriptions)

**Fichier Excel**: `enrollments.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| student_matricule | texte | ✅ | Matricule de l'élève | STU20250001 |
| classroom_name | texte | ✅ | Nom de la classe | 6ème A |
| academic_year_name | texte | ✅ | Nom de l'année scolaire | 2024-2025 |
| enrollment_date | date | ❌ | Date d'inscription | 2024-09-01 |
| is_active | booléen | ❌ | Inscription active | TRUE |
| withdrawal_date | date | ❌ | Date de retrait | - |

**Contrainte**: Un élève ne peut avoir qu'une seule inscription active par année scolaire.

---

### 2.7 Timetable (Emploi du temps)

**Fichier Excel**: `timetables.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| classroom_name | texte | ✅ | - | Nom de la classe | 6ème A |
| subject_code | texte | ✅ | - | Code de la matière | MATH |
| teacher_email | texte | ✅ | - | Email de l'enseignant | prof1@eschool.cd |
| weekday | entier | ✅ | 1-7 | Jour (1=Lundi, 7=Dimanche) | 1 |
| start_time | heure | ✅ | HH:MM | Heure de début | 08:00 |
| end_time | heure | ✅ | HH:MM | Heure de fin | 09:00 |
| room | texte | ❌ | - | Salle | A101 |

---

### 2.8 Grade (Notes)

**Fichier Excel**: `grades.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| student_matricule | texte | ✅ | Matricule de l'élève | STU20250001 |
| subject_code | texte | ✅ | Code de la matière | MATH |
| teacher_email | texte | ✅ | Email de l'enseignant | prof1@eschool.cd |
| classroom_name | texte | ✅ | Nom de la classe | 6ème A |
| academic_year_name | texte | ✅ | Nom de l'année scolaire | 2024-2025 |
| period_name | texte | ✅ | Nom de la période | Trimestre 1 |
| assignment_name | texte | ✅ | Nom de l'évaluation | Examen de Mathématiques |
| score | décimal | ✅ | Note obtenue | 15.5 |
| max_score | décimal | ✅ | Note maximale | 20.0 |
| weight | décimal | ❌ | Poids/coefficient | 2.0 |
| grade_date | date | ❌ | Date de notation | 2024-10-15 |
| comments | texte | ❌ | Commentaires | Bon travail |

---

### 2.9 Attendance (Présences)

**Fichier Excel**: `attendances.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| student_matricule | texte | ✅ | - | Matricule de l'élève | STU20250001 |
| classroom_name | texte | ✅ | - | Nom de la classe | 6ème A |
| date | date | ✅ | - | Date | 2024-10-15 |
| period | texte | ❌ | MORNING, AFTERNOON, FULL_DAY | Période | FULL_DAY |
| status | texte | ✅ | PRESENT, ABSENT, LATE, EXCUSED | Statut | PRESENT |
| time_in | heure | ❌ | HH:MM | Heure d'arrivée | 08:00 |
| time_out | heure | ❌ | HH:MM | Heure de sortie | 15:00 |
| reason | texte | ❌ | - | Raison (si absent/retard) | Malade |
| teacher_email | texte | ❌ | - | Email de l'enseignant | prof1@eschool.cd |

---

### 2.10 Document (Documents Académiques)

**Fichier Excel**: `documents.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| title | texte | ✅ | - | Titre du document | Devoir de Mathématiques |
| document_type | texte | ✅ | SYLLABUS, LECTURE_NOTE, EXERCISE, EXAM, RESOURCE, OTHER | Type | EXERCISE |
| subject_code | texte | ✅ | - | Code de la matière | MATH |
| teacher_email | texte | ✅ | - | Email de l'enseignant | prof1@eschool.cd |
| classroom_name | texte | ❌ | - | Nom de la classe (si spécifique) | 6ème A |
| description | texte | ❌ | - | Description | Exercices chapitre 5 |
| file_path | texte | ❌ | - | Chemin du fichier | documents/math_ex5.pdf |
| is_public | booléen | ❌ | - | Document public | FALSE |
| due_date | date | ❌ | - | Date limite (pour devoirs) | 2024-10-20 |
| max_score | décimal | ❌ | - | Note maximale | 20.0 |

---

## 3. Finance

### 3.1 FeeType (Types de Frais)

**Fichier Excel**: `fee_types.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| name | texte | ✅ | Nom du type de frais | Frais de scolarité |
| description | texte | ❌ | Description | Frais annuels de scolarité |
| is_recurring | booléen | ❌ | Frais récurrent | TRUE |
| is_mandatory | booléen | ❌ | Frais obligatoire | TRUE |

**Exemples de types de frais**:
- Frais de scolarité
- Frais d'inscription
- Frais de transport
- Frais de cantine
- Frais d'uniforme
- Frais d'examen

---

### 3.2 FeeStructure (Structure des Frais)

**Fichier Excel**: `fee_structures.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| fee_type_name | texte | ✅ | Nom du type de frais | Frais de scolarité |
| level_name | texte | ✅ | Nom du niveau | Primaire |
| academic_year_name | texte | ✅ | Nom de l'année scolaire | 2024-2025 |
| amount | décimal | ✅ | Montant | 500000.00 |
| due_date | date | ❌ | Date d'échéance | 2024-10-31 |

**Note**: La combinaison (fee_type, level, academic_year) doit être unique.

---

### 3.3 PaymentMethod (Méthodes de Paiement)

**Fichier Excel**: `payment_methods.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| name | texte | ✅ | Nom de la méthode | Mobile Money |
| code | texte | ✅ | Code unique | MOBILE_MONEY |
| description | texte | ❌ | Description | Paiement via M-Pesa, Airtel Money |
| is_active | booléen | ❌ | Méthode active | TRUE |
| requires_reference | booléen | ❌ | Nécessite référence | TRUE |

**Exemples de méthodes**:
- CASH (Espèces)
- BANK_TRANSFER (Virement bancaire)
- MOBILE_MONEY (Mobile Money)
- CHEQUE (Chèque)
- CARD (Carte bancaire)

---

### 3.4 Invoice (Factures)

**Fichier Excel**: `invoices.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| invoice_number | texte | ❌ | - | Numéro (auto-généré si vide) | INV202410001 |
| student_matricule | texte | ✅ | - | Matricule de l'élève | STU20250001 |
| parent_email | texte | ❌ | - | Email du parent responsable | parent1@eschool.cd |
| issue_date | date | ❌ | - | Date d'émission | 2024-10-01 |
| due_date | date | ✅ | - | Date d'échéance | 2024-10-31 |
| discount | décimal | ❌ | - | Remise | 0.00 |
| status | texte | ❌ | DRAFT, SENT, PAID, OVERDUE, CANCELLED | Statut | SENT |
| notes | texte | ❌ | - | Notes | Paiement en 3 fois possible |

**Format invoice_number auto-généré**: `INV{ANNÉE}{MOIS}{NUMÉRO}` (ex: INV202410001)

**Note**: Les montants (subtotal, total_amount) sont calculés automatiquement à partir des InvoiceItem.

---

### 3.5 InvoiceItem (Lignes de Facture)

**Fichier Excel**: `invoice_items.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| invoice_number | texte | ✅ | Numéro de facture | INV202410001 |
| fee_type_name | texte | ✅ | Nom du type de frais | Frais de scolarité |
| description | texte | ✅ | Description | Scolarité Trimestre 1 |
| quantity | décimal | ❌ | Quantité | 1.00 |
| unit_price | décimal | ✅ | Prix unitaire | 500000.00 |

**Note**: Le total est calculé automatiquement (quantity × unit_price).

---

### 3.6 Payment (Paiements)

**Fichier Excel**: `payments.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| payment_reference | texte | ✅ | - | Référence unique | PAY202410001 |
| invoice_number | texte | ✅ | - | Numéro de facture | INV202410001 |
| payment_method_code | texte | ✅ | - | Code méthode de paiement | MOBILE_MONEY |
| amount | décimal | ✅ | - | Montant payé | 250000.00 |
| payment_date | date | ❌ | - | Date de paiement | 2024-10-15 |
| status | texte | ❌ | PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED | Statut | COMPLETED |
| transaction_id | texte | ❌ | - | ID de transaction externe | TXN123456 |
| receipt_number | texte | ❌ | - | Numéro de reçu | REC202410001 |
| notes | texte | ❌ | - | Notes | Paiement partiel |

---

## 4. Communication

### 4.1 Announcement (Annonces)

**Fichier Excel**: `announcements.xlsx`

| Colonne | Type | Requis | Valeurs | Description | Exemple |
|---------|------|--------|---------|-------------|---------|
| title | texte | ✅ | - | Titre | Réunion des parents |
| content | texte | ✅ | - | Contenu | Réunion le 20/10 à 14h |
| author_email | texte | ✅ | - | Email de l'auteur | admin@eschool.cd |
| priority | texte | ❌ | LOW, MEDIUM, HIGH, URGENT | Priorité | HIGH |
| target_roles | texte | ❌ | - | Rôles cibles (séparés par ;) | PARENT;STUDENT |
| is_active | booléen | ❌ | - | Annonce active | TRUE |
| publish_date | datetime | ❌ | - | Date de publication | 2024-10-01 08:00 |
| expiry_date | datetime | ❌ | - | Date d'expiration | 2024-10-20 17:00 |

---

### 4.2 Message (Messages Privés)

**Fichier Excel**: `messages.xlsx`

| Colonne | Type | Requis | Description | Exemple |
|---------|------|--------|-------------|---------|
| sender_email | texte | ✅ | Email de l'expéditeur | prof1@eschool.cd |
| recipient_email | texte | ✅ | Email du destinataire | parent1@eschool.cd |
| subject | texte | ✅ | Sujet | Résultats de votre enfant |
| content | texte | ✅ | Contenu du message | Votre enfant a obtenu... |
| parent_message_id | entier | ❌ | ID message parent (réponse) | - |
| is_read | booléen | ❌ | Message lu | FALSE |

---

## 5. Scripts d'Import

### 5.1 Structure Recommandée des Fichiers

```
import_data/
├── 01_base/
│   ├── academic_years.xlsx
│   ├── levels.xlsx
│   ├── subjects.xlsx
│   └── payment_methods.xlsx
├── 02_users/
│   ├── users.xlsx
│   ├── students.xlsx
│   ├── parents.xlsx
│   └── teachers.xlsx
├── 03_academic/
│   ├── classrooms.xlsx
│   ├── enrollments.xlsx
│   └── teacher_assignments.xlsx
├── 04_finance/
│   ├── fee_types.xlsx
│   ├── fee_structures.xlsx
│   ├── invoices.xlsx
│   └── invoice_items.xlsx
└── 05_operational/
    ├── timetables.xlsx
    ├── grades.xlsx
    ├── attendances.xlsx
    └── announcements.xlsx
```

### 5.2 Ordre d'Import Recommandé

L'ordre est crucial pour respecter les dépendances entre modèles:

```python
# Ordre d'import à suivre:
1. AcademicYear (années scolaires)
2. Level (niveaux)
3. Subject (matières)
4. PaymentMethod (méthodes de paiement)
5. FeeType (types de frais)

6. User (utilisateurs - tous les rôles)
7. Profile (profils étendus)
8. Student (élèves)
9. Parent (parents)
10. Teacher (enseignants)

11. ClassRoom (classes)
12. TeacherAssignment (attributions enseignants)
13. Enrollment (inscriptions élèves)

14. FeeStructure (structures de frais)
15. Invoice (factures)
16. InvoiceItem (lignes de facture)
17. Payment (paiements)

18. Timetable (emplois du temps)
19. Grade (notes)
20. Attendance (présences)
21. Document (documents)

22. Announcement (annonces)
23. Message (messages)
```

### 5.3 Script d'Import Générique (Python)

Créez un fichier `scripts/import_from_excel.py`:

```python
#!/usr/bin/env python
"""
Script d'import de données depuis fichiers Excel
Usage: python scripts/import_from_excel.py
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from accounts.models import Student, Parent, Teacher
from academic.models import (
    AcademicYear, Level, Subject, ClassRoom, 
    TeacherAssignment, Enrollment, Grade, Attendance
)
from finance.models import (
    FeeType, FeeStructure, PaymentMethod, 
    Invoice, InvoiceItem, Payment
)
from communication.models import Announcement, Message

User = get_user_model()

class DataImporter:
    def __init__(self, base_path='import_data'):
        self.base_path = base_path
        self.errors = []
        self.stats = {}
    
    def log(self, message, level='INFO'):
        """Log des messages avec timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def import_users(self, file_path):
        """Import des utilisateurs"""
        self.log(f"Import des utilisateurs depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    user, created = User.objects.get_or_create(
                        email=row['email'],
                        defaults={
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'role': row['role'],
                            'phone': row.get('phone', ''),
                            'gender': row.get('gender', ''),
                            'address': row.get('address', ''),
                            'is_active': row.get('is_active', True),
                        }
                    )
                    
                    if created:
                        user.set_password(row['password'])
                        user.save()
                        created_count += 1
                        self.log(f"✓ Utilisateur créé: {user.email}")
                    else:
                        self.log(f"→ Utilisateur existant: {user.email}", 'WARNING')
            
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['users'] = created_count
        self.log(f"✓ {created_count} utilisateurs créés")
    
    def import_students(self, file_path):
        """Import des élèves"""
        self.log(f"Import des élèves depuis {file_path}")
        df = pd.read_excel(file_path)
        created_count = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    user = User.objects.get(email=row['user_email'])
                    
                    student, created = Student.objects.get_or_create(
                        user=user,
                        defaults={
                            'matricule': row.get('matricule', ''),
                            'enrollment_date': row.get('enrollment_date', timezone.now().date()),
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.log(f"✓ Élève créé: {student.matricule}")
            
            except User.DoesNotExist:
                error_msg = f"Erreur ligne {index + 2}: Utilisateur {row['user_email']} non trouvé"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.log(error_msg, 'ERROR')
                self.errors.append(error_msg)
        
        self.stats['students'] = created_count
        self.log(f"✓ {created_count} élèves créés")
    
    # Ajouter d'autres méthodes pour chaque modèle...
    
    def run_import(self):
        """Exécute l'import complet dans l'ordre"""
        self.log("=" * 70)
        self.log("DÉMARRAGE DE L'IMPORT DE DONNÉES")
        self.log("=" * 70)
        
        import_sequence = [
            ('01_base/academic_years.xlsx', self.import_academic_years),
            ('01_base/levels.xlsx', self.import_levels),
            ('01_base/subjects.xlsx', self.import_subjects),
            ('02_users/users.xlsx', self.import_users),
            ('02_users/students.xlsx', self.import_students),
            # ... ajouter tous les autres imports
        ]
        
        for file_path, import_func in import_sequence:
            full_path = os.path.join(self.base_path, file_path)
            if os.path.exists(full_path):
                import_func(full_path)
            else:
                self.log(f"⚠ Fichier non trouvé: {full_path}", 'WARNING')
        
        self.log("=" * 70)
        self.log("RÉSUMÉ DE L'IMPORT")
        self.log("=" * 70)
        for model, count in self.stats.items():
            self.log(f"{model}: {count} enregistrements créés")
        
        if self.errors:
            self.log(f"\n⚠ {len(self.errors)} erreurs rencontrées:")
            for error in self.errors:
                self.log(error, 'ERROR')
        else:
            self.log("\n✓ Import terminé sans erreur!")

if __name__ == '__main__':
    importer = DataImporter()
    importer.run_import()
```

### 5.4 Validation des Données

Avant l'import, validez vos fichiers Excel:

```python
# scripts/validate_import_data.py
def validate_users(df):
    """Valide le fichier users.xlsx"""
    errors = []
    
    # Vérifier les colonnes requises
    required_cols = ['email', 'first_name', 'last_name', 'password', 'role']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Colonnes manquantes: {missing_cols}")
    
    # Vérifier les emails uniques
    if df['email'].duplicated().any():
        duplicates = df[df['email'].duplicated()]['email'].tolist()
        errors.append(f"Emails en double: {duplicates}")
    
    # Vérifier les rôles valides
    valid_roles = ['STUDENT', 'PARENT', 'TEACHER', 'ADMIN', 'FINANCE', 'SUPER_ADMIN']
    invalid_roles = df[~df['role'].isin(valid_roles)]['role'].unique()
    if len(invalid_roles) > 0:
        errors.append(f"Rôles invalides: {invalid_roles}")
    
    return errors
```

### 5.5 Template Excel avec Formules

Créez des templates Excel avec validation de données:

**users_template.xlsx**:
- Colonne `role`: Liste déroulante (STUDENT, PARENT, TEACHER, ADMIN, FINANCE, SUPER_ADMIN)
- Colonne `gender`: Liste déroulante (M, F)
- Colonne `email`: Format email (validation)
- Colonne `is_active`: Liste déroulante (TRUE, FALSE)

---

## 📋 Checklist Avant Import

- [ ] Fichiers Excel au format .xlsx
- [ ] Encodage UTF-8
- [ ] Noms de colonnes exacts (respecter majuscules/minuscules)
- [ ] Dates au format YYYY-MM-DD
- [ ] Heures au format HH:MM
- [ ] Pas de cellules fusionnées
- [ ] Pas de lignes vides
- [ ] Valeurs booléennes: TRUE/FALSE
- [ ] Emails uniques et valides
- [ ] Références valides entre fichiers
- [ ] Backup de la base de données avant import

---

## 🛠️ Dépannage

### Erreurs Communes

**1. "User matching query does not exist"**
- Vérifiez que l'utilisateur existe avant de créer un Student/Parent/Teacher
- Importez les users en premier

**2. "IntegrityError: UNIQUE constraint failed"**
- Vérifiez les champs uniques (email, matricule, employee_id, invoice_number, etc.)
- Supprimez les doublons dans vos fichiers Excel

**3. "DoesNotExist: ClassRoom matching query does not exist"**
- Importez les classes avant les inscriptions
- Vérifiez les noms de classes (respecter majuscules)

**4. "Invalid date format"**
- Utilisez le format YYYY-MM-DD
- Vérifiez les cellules vides dans les colonnes de dates optionnelles

---

## 📞 Support

Pour toute question concernant l'import de données:
1. Consultez ce document
2. Vérifiez les logs d'erreur du script
3. Testez avec un petit échantillon d'abord
4. Créez une issue sur GitHub avec les logs d'erreur

---

**Dernière mise à jour**: 3 novembre 2025  
**Version**: 1.0
