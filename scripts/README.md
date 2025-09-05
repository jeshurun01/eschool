# 🛠️ Scripts de test et validation eSchool

## 📋 Scripts de validation

### 🏠 Page d'accueil
- **`check_homepage_simple.py`** - Validation complète de la page d'accueil (19/19 tests)
- **`check_homepage_improvements.py`** - Vérification des améliorations avec requests

### 🔐 Authentification
- **`check_login_ids.py`** - Validation des IDs de la page de login
- **`test_login.py`** - Tests d'authentification

### 🐛 Corrections de bugs
- **`test_grade_fix_simple.py`** - Validation de la correction Grade.percentage (3/3 tests)
- **`test_grade_fix.py`** - Test complet avec Django setup

### 🧪 Tests généraux
- **`test_views.py`** - Tests des vues Django

## 🚀 Utilisation

### Validation complète du système
```bash
# Test de la page d'accueil
uv run python scripts/check_homepage_simple.py

# Test de la correction de bug
uv run python scripts/test_grade_fix_simple.py
```

### Résultats attendus
- ✅ **Homepage** : 19/19 éléments validés (100%)
- ✅ **Bug fix** : 3/3 tests réussis (100%)
- ✅ **Login** : Accessibilité parfaite

---

**📅 Dernière mise à jour** : 5 septembre 2025  
**🎯 Statut** : ✅ Tous les tests passent
