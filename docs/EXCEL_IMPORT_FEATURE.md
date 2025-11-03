# Fonctionnalité d'Import Excel - eSchool

## 📋 Vue d'ensemble

Système complet d'import en masse de données depuis fichiers Excel vers la base de données eSchool.

**Date**: Janvier 2025  
**Version**: 1.0  
**État**: ✅ Prêt pour utilisation

---

## 🎯 Objectif

Permettre aux écoles d'importer rapidement leurs données existantes (élèves, enseignants, classes, notes, etc.) depuis des fichiers Excel standardisés, facilitant ainsi:
- La migration depuis d'autres systèmes
- L'initialisation d'une nouvelle installation
- Les imports en masse de données

---

## 📦 Fichiers créés

### 1. Documentation

| Fichier | Description |
|---------|-------------|
| `docs/DATA_SCHEMAS_FOR_IMPORT.md` | Schémas complets des 23+ modèles avec spécifications Excel |
| `docs/EXCEL_IMPORT_GUIDE.md` | Guide utilisateur complet avec exemples et dépannage |
| `docs/EXCEL_IMPORT_FEATURE.md` | Ce fichier - Vue d'ensemble de la fonctionnalité |

### 2. Scripts

| Fichier | Description |
|---------|-------------|
| `scripts/import_excel_data.py` | Script principal d'import avec CLI et validation |
| `scripts/generate_excel_templates.py` | Générateur de templates Excel avec exemples |

### 3. Dépendances ajoutées

```txt
pandas>=2.0.0      # Traitement des fichiers Excel
openpyxl>=3.1.0    # Lecture/écriture Excel (.xlsx)
```

---

## 🚀 Guide de démarrage rapide

### Étape 1: Installation des dépendances

```bash
pip install -r requirements.txt
# ou avec uv
uv pip install pandas openpyxl
```

### Étape 2: Génération des templates

```bash
python scripts/generate_excel_templates.py
```

Cela créera:
- La structure de répertoires `import_data/`
- 9 fichiers Excel templates avec exemples
- Un README avec instructions

### Étape 3: Préparation des données

1. Ouvrir les templates dans `import_data/templates/`
2. Copier le template approprié dans le bon répertoire:
   - `academic_years_template.xlsx` → `import_data/01_base/academic_years.xlsx`
   - `users_template.xlsx` → `import_data/02_users/users.xlsx`
   - etc.
3. Remplacer les données d'exemple par les vraies données

### Étape 4: Import

```bash
# Import d'un fichier unique
python scripts/import_excel_data.py \
    --file import_data/02_users/users.xlsx \
    --model users

# Import complet (tous les fichiers dans l'ordre)
python scripts/import_excel_data.py \
    --directory import_data \
    --all
```

---

## 📊 Modèles supportés

### Comptes utilisateurs (4 modèles)
- ✅ Users (utilisateurs de base)
- ✅ Students (élèves avec matricule)
- ✅ Parents (parents avec profession)
- ✅ Teachers (enseignants avec salaire)

### Académique (10 modèles)
- ✅ AcademicYear (années scolaires)
- ✅ Level (niveaux scolaires)
- ✅ Subject (matières)
- ✅ ClassRoom (classes)
- ⏳ TeacherAssignment (affectations enseignants)
- ⏳ Enrollment (inscriptions élèves)
- ⏳ Timetable (emplois du temps)
- ⏳ Grade (notes)
- ⏳ Attendance (présences)
- ⏳ Document (documents)

### Finance (6 modèles)
- ⏳ FeeType (types de frais)
- ⏳ FeeStructure (structures tarifaires)
- ⏳ PaymentMethod (modes de paiement)
- ⏳ Invoice (factures)
- ⏳ InvoiceItem (lignes de facture)
- ⏳ Payment (paiements)

### Communication (2 modèles)
- ⏳ Announcement (annonces)
- ⏳ Message (messages)

**Légende**:
- ✅ Implémenté et testé
- ⏳ Template fourni, méthode d'import à compléter

---

## 📁 Structure des répertoires

```
import_data/
├── README.md                      # Instructions rapides
├── templates/                     # Templates Excel avec exemples
│   ├── users_template.xlsx
│   ├── students_template.xlsx
│   ├── parents_template.xlsx
│   ├── teachers_template.xlsx
│   ├── academic_years_template.xlsx
│   ├── levels_template.xlsx
│   ├── subjects_template.xlsx
│   ├── classrooms_template.xlsx
│   └── enrollments_template.xlsx
├── 01_base/                       # Données de base (à importer en premier)
│   └── academic_years.xlsx
├── 02_users/                      # Utilisateurs
│   ├── users.xlsx
│   ├── students.xlsx
│   ├── parents.xlsx
│   └── teachers.xlsx
├── 03_academic/                   # Structure académique
│   ├── levels.xlsx
│   ├── subjects.xlsx
│   └── classrooms.xlsx
├── 04_enrollment/                 # Inscriptions
│   ├── enrollments.xlsx
│   └── timetables.xlsx
├── 05_assessment/                 # Évaluation
│   ├── grades.xlsx
│   └── attendance.xlsx
├── 06_finance/                    # Finances
│   ├── fee_types.xlsx
│   ├── fee_structures.xlsx
│   └── invoices.xlsx
└── 07_communication/              # Communication
    ├── announcements.xlsx
    └── messages.xlsx
```

---

## 🔧 Fonctionnalités du script d'import

### Validation automatique
- ✅ Format des emails (RFC 5322)
- ✅ Format des dates (ISO 8601: YYYY-MM-DD)
- ✅ Unicité des clés primaires
- ✅ Existence des clés étrangères
- ✅ Valeurs des champs de choix (ROLE_CHOICES, STATUS_CHOICES, etc.)
- ✅ Types de données (nombre, booléen, texte)

### Gestion des erreurs
- ✅ **Transactions atomiques**: Chaque ligne dans une transaction séparée
- ✅ **Rollback automatique**: Si une ligne échoue, les autres continuent
- ✅ **Logging détaillé**: Affichage de chaque opération avec timestamp
- ✅ **Rapport de synthèse**: Statistiques finales (créés, mis à jour, erreurs)
- ✅ **Messages d'erreur explicites**: Indication de la ligne et du problème

### Performances
- ✅ **Import par lots**: Recommandé max 1000 lignes par fichier
- ✅ **Optimisation des requêtes**: get_or_create pour éviter les doublons
- ✅ **Relations multiples**: Support des champs multi-valeurs (parents, matières)

### Idempotence
- ✅ **Mode mise à jour**: Les enregistrements existants sont mis à jour, pas dupliqués
- ✅ **Détection des doublons**: Basée sur les clés uniques (email, matricule, code)

---

## 💡 Cas d'usage

### 1. Migration depuis un ancien système

```bash
# Exporter les données depuis l'ancien système vers Excel
# (format selon les templates fournis)

# Importer dans eSchool
python scripts/import_excel_data.py --directory import_data --all
```

### 2. Initialisation d'une nouvelle école

```bash
# 1. Générer les templates
python scripts/generate_excel_templates.py

# 2. Remplir les templates avec les données de l'école
# 3. Importer étape par étape
python scripts/import_excel_data.py --file import_data/01_base/academic_years.xlsx --model academic_years
python scripts/import_excel_data.py --file import_data/02_users/users.xlsx --model users
python scripts/import_excel_data.py --file import_data/02_users/students.xlsx --model students
# etc.
```

### 3. Import incrémental (nouveaux élèves)

```bash
# Ajouter les nouveaux élèves au fichier Excel
# L'import ne créera que les nouveaux, sans toucher aux existants
python scripts/import_excel_data.py --file import_data/02_users/new_students.xlsx --model students
```

---

## 📖 Exemple de fichier Excel

### users.xlsx

| email | password | first_name | last_name | role | phone | gender | date_of_birth | address | is_active |
|-------|----------|------------|-----------|------|-------|--------|---------------|---------|-----------|
| jean.dupont@example.com | Welcome@2025 | Jean | Dupont | STUDENT | +243991234567 | M | 2010-05-15 | 123 Ave Kasaï | TRUE |
| prof.math@example.com | Welcome@2025 | Sophie | Lambert | TEACHER | +243991234568 | F | 1985-11-05 | 456 Rue Lumumba | TRUE |

### students.xlsx

| user_email | matricule | enrollment_date | parent_emails | is_graduated |
|------------|-----------|-----------------|---------------|--------------|
| jean.dupont@example.com | STU-2024-0001 | 2024-09-01 | papa.dupont@example.com;maman.dupont@example.com | FALSE |

---

## ⚠️ Points d'attention

### Ordre d'import critique

**⚠️ IMPORTANT**: Respecter impérativement cet ordre pour éviter les erreurs de clés étrangères:

1. **Années scolaires** (aucune dépendance)
2. **Utilisateurs** (aucune dépendance)
3. **Élèves/Parents/Enseignants** (dépend de: Utilisateurs)
4. **Niveaux** (aucune dépendance)
5. **Matières** (aucune dépendance)
6. **Classes** (dépend de: Années scolaires, Niveaux, Enseignants)
7. **Inscriptions** (dépend de: Élèves, Classes)
8. **Notes/Présences** (dépend de: Inscriptions, Matières)
9. **Finances** (dépend de: Élèves, Années scolaires)

### Sécurité

- ⚠️ **Mots de passe**: Changez tous les mots de passe après l'import initial
- ⚠️ **Backup**: Sauvegardez la BD avant un import massif:
  ```bash
  python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
  ```
- ⚠️ **Données sensibles**: Ne partagez pas les fichiers Excel contenant des données réelles

### Performance

Pour de très gros volumes (> 10 000 lignes):
- Diviser en plusieurs fichiers de 1000-5000 lignes
- Importer pendant les heures creuses
- Monitorer la mémoire et l'espace disque

---

## 🔍 Dépannage

### Erreur: "pandas not found"

```bash
pip install pandas openpyxl
```

### Erreur: "User not found"

**Cause**: Référence à un email inexistant dans students/parents/teachers

**Solution**: 
1. Vérifier que `users.xlsx` a bien été importé en premier
2. Vérifier l'orthographe de l'email

### Erreur: "Invalid date format"

**Cause**: Format de date incorrect

**Solution**: Utiliser le format `YYYY-MM-DD` (exemple: `2024-09-01`)

### Import lent

**Solutions**:
1. Diviser le fichier en plusieurs petits fichiers
2. Vérifier qu'il n'y a pas de règles métier coûteuses dans les signaux Django
3. Désactiver temporairement les signaux:
   ```python
   from django.db.models.signals import post_save
   post_save.disconnect(sender=User)
   # ... import ...
   post_save.connect(sender=User)
   ```

---

## 🎓 Ressources

### Documentation
- **Schémas des modèles**: `docs/DATA_SCHEMAS_FOR_IMPORT.md`
- **Guide utilisateur**: `docs/EXCEL_IMPORT_GUIDE.md`
- **Instructions rapides**: `import_data/README.md`

### Support
En cas de problème, fournir:
1. Le fichier Excel problématique (sans données sensibles)
2. Les messages d'erreur complets du script
3. La version de Python et pandas:
   ```bash
   python --version
   pip show pandas openpyxl
   ```

---

## 🔄 Prochaines améliorations

### Version 1.1 (à venir)
- [ ] Interface web d'upload (drag & drop)
- [ ] Validation en temps réel des fichiers Excel
- [ ] Preview avant import
- [ ] Export Excel depuis l'interface admin
- [ ] Templates Excel avec validation de données (dropdowns)
- [ ] Historique des imports
- [ ] Imports programmés (cron jobs)

### Version 1.2 (à venir)
- [ ] Support CSV en plus d'Excel
- [ ] Import depuis Google Sheets (API)
- [ ] Mappings personnalisés (colonnes différentes)
- [ ] Transformations de données (scripts Python custom)
- [ ] Rapport détaillé par email après import

---

## 📝 Changelog

### Version 1.0 (Janvier 2025)
- ✅ Documentation complète des schémas (23+ modèles)
- ✅ Script d'import CLI avec validation
- ✅ Générateur de templates Excel
- ✅ Guide utilisateur complet
- ✅ Support des modèles: User, Student, Parent, Teacher, AcademicYear, Level, Subject, ClassRoom, Enrollment
- ✅ Gestion des erreurs et transactions atomiques
- ✅ Logging détaillé et rapport de synthèse

---

## 📄 Licence

Ce module fait partie du projet eSchool.  
Voir LICENSE à la racine du projet.

---

**Date de création**: Janvier 2025  
**Dernière mise à jour**: Janvier 2025  
**Auteurs**: Équipe de développement eSchool
