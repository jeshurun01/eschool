# 🛠️ Scripts eSchool

Collection de scripts utilitaires pour le développement, test et maintenance du système eSchool.

## � Structure des dossiers

### 🧪 `testing/` - Scripts de test
Scripts pour tester différentes fonctionnalités du système.

**Tests d'authentification et RBAC :**
- `test_login_*.py` - Tests de connexion et authentification
- `test_rbac_phase*.py` - Tests du système de permissions RBAC

**Tests des modules académiques :**
- `test_attendance_*.py` - Tests du système de présences
- `test_grade_*.py` - Tests du système de notes
- `test_course_*.py` - Tests des cours et détails

**Tests des interfaces utilisateur :**
- `test_parent_student_interfaces.py` - Tests des interfaces parent/élève
- `test_final_all_interfaces.py` - Tests complets de toutes les interfaces
- `test_teacher_*.py` - Tests spécifiques aux enseignants

**Tests financiers :**
- `test_bulk_*.py` - Tests des actions en lot
- `test_decimal_conversion.py` - Tests de conversion décimale

**Autres tests :**
- `test_pagination_fix.py` - Tests de pagination
- `test_dashboard_differences.py` - Tests des tableaux de bord
- `test_guide.py` - Tests du guide utilisateur

### 💾 `data_creation/` - Création de données
Scripts pour créer des données de test et d'exemple.

**Données principales :**
- `populate_data.py` - Script principal de population (🔥 **IMPORTANT**)
- `create_grades.py` - Création de notes d'exemple

**Données par module :**
- `create_attendance_data.py` - Données de présences
- `create_finance_test_data.py` - Données financières de test
- `create_payment_test_data.py` - Données de paiements

**Données de communication :**
- `create_communication_test_data.py` - Messages et communications
- `create_forum_test_data.py` - Posts et sujets de forum

**Données académiques :**
- `create_realistic_assignments.py` - Devoirs réalistes
- `create_teacher_assignments.py` - Assignations enseignants
- `create_student_views.py` - Vues étudiants

**Données financières avancées :**
- `create_test_fee_structures.py` - Structures de frais
- `create_test_invoices.py` - Factures de test

### 🐛 `debugging/` - Scripts de débogage
Scripts pour identifier et corriger les problèmes.

**Corrections de timezone :**
- `fix_naive_datetimes.py` - Correction des datetimes naïves
- `fix_timezone_warnings.py` - Correction des alertes timezone

**Débogage système :**
- `debug_login_issue.py` - Débogage des problèmes de connexion
- `debug_timezone_issues.py` - Débogage des problèmes de timezone

### ✅ `validation/` - Scripts de validation
Scripts pour vérifier l'intégrité et la cohérence des données.

**Validation des données :**
- `validate_timezones.py` - Validation des timezones
- `detect_duplicate_ids.py` - Détection des IDs dupliqués

**Audit et vérification :**
- `audit_parent_student.py` - Audit des relations parent-élève
- `verify_teacher_filtering.py` - Vérification du filtrage enseignants

**Contrôles système :**
- `check_classroom_permissions.py` - Vérification permissions classes
- `check_fee_data.py` - Vérification des données de frais
- `check_homepage_*.py` - Vérifications page d'accueil
- `check_login_ids.py` - Vérification des IDs de connexion

### 🔧 `utilities/` - Scripts utilitaires
Scripts d'aide et d'information.

- `get_teacher_info.py` - Récupération d'informations enseignants

## 🚀 Scripts principaux à connaître

### Pour débuter avec des données
```bash
# Créer toutes les données de base
uv run python scripts/data_creation/populate_data.py
```

### Pour tester le système
```bash
# Tests complets de toutes les interfaces
uv run python scripts/testing/test_final_all_interfaces.py

# Tests spécifiques des interfaces parent/élève
uv run python scripts/testing/test_parent_student_interfaces.py
```

### Pour valider l'intégrité
```bash
# Audit complet parent-élève
uv run python scripts/validation/audit_parent_student.py

# Validation des timezones
uv run python scripts/validation/validate_timezones.py
```

## 📝 Notes d'utilisation

1. **Ordre recommandé** : Toujours commencer par `populate_data.py` pour avoir des données de base
2. **Tests** : Les scripts de test sont autonomes et peuvent être exécutés indépendamment
3. **Debugging** : Utiliser les scripts de debug en cas de problème spécifique
4. **Validation** : Exécuter régulièrement les scripts de validation pour s'assurer de l'intégrité

## ⚠️ Attention

- Certains scripts peuvent modifier la base de données
- Toujours tester sur une copie avant d'utiliser en production
- Les scripts vides sont des placeholders pour développement futur

---

*Organisé le 12 septembre 2025 - Voir [docs/INDEX_ORGANISATION.md](../docs/INDEX_ORGANISATION.md) pour la documentation complète*
