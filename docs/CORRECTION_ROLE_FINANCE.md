# Correction du Rôle Financier

## 🐛 Problème Identifié

Le compte financier ne pouvait pas accéder aux pages `/finance/invoices/` malgré les corrections des décorateurs.

### Cause Racine

**Confusion entre deux noms de rôle :**
- Nom utilisé dans le code : `FINANCE_MANAGER`
- Nom défini dans le modèle User : `FINANCE`

### Erreur

```python
# Dans la base de données
finance.role = 'FINANCE_MANAGER'  # ❌ Ce rôle n'existe pas!

# Dans User.ROLE_CHOICES
('FINANCE', 'Personnel financier')  # ✅ Le vrai rôle
```

## ✅ Corrections Appliquées

### 1. Base de Données

```python
# Correction du rôle dans la DB
finance = User.objects.get(email='finance@eschool.cd')
finance.role = 'FINANCE'  # Changé de 'FINANCE_MANAGER' à 'FINANCE'
finance.save()
```

### 2. Décorateur `finance_or_family_required`

**Fichier:** `core/decorators/permissions.py`

```python
# AVANT (❌ Incorrect)
allowed_roles = ['PARENT', 'STUDENT', 'FINANCE_MANAGER', 'ADMIN', 'SUPER_ADMIN']

# APRÈS (✅ Correct)
allowed_roles = ['PARENT', 'STUDENT', 'FINANCE', 'ADMIN', 'SUPER_ADMIN']
```

### 3. Dashboard

**Fichier:** `accounts/views.py`

```python
# AVANT (❌)
if request.user.role in ['ADMIN', 'SUPER_ADMIN', 'FINANCE_MANAGER']:

# APRÈS (✅)
if request.user.role in ['ADMIN', 'SUPER_ADMIN', 'FINANCE']:
```

### 4. Script de Génération

**Fichier:** `scripts/reset_and_populate.py`

```python
# AVANT (❌)
finance_user = User.objects.create_user(
    role='FINANCE_MANAGER',  # Mauvais rôle!
    ...
)

# APRÈS (✅)
finance_user = User.objects.create_user(
    role='FINANCE',  # Rôle correct!
    ...
)
```

## 📋 Rôles Disponibles dans User.ROLE_CHOICES

| Code | Libellé | Utilisation |
|------|---------|-------------|
| `STUDENT` | Élève | Comptes étudiants |
| `PARENT` | Parent | Comptes parents |
| `TEACHER` | Enseignant | Comptes enseignants |
| `ADMIN` | Administrateur | Administrateurs |
| `FINANCE` | Personnel financier | **Gestionnaires financiers** ✅ |
| `SUPER_ADMIN` | Super administrateur | Super admin |

## 🔐 Permissions Correctes

### @finance_required
Autorise : `['FINANCE', 'ADMIN', 'SUPER_ADMIN']`

### @finance_or_family_required
Autorise : `['PARENT', 'STUDENT', 'FINANCE', 'ADMIN', 'SUPER_ADMIN']`

### @staff_required
Autorise : `['TEACHER', 'ADMIN', 'SUPER_ADMIN', 'FINANCE']`

## 🧪 Vérification

```python
# Test du compte
finance = User.objects.get(email='finance@eschool.cd')
print(finance.role)  # Doit afficher: FINANCE
print(finance.get_role_display())  # Doit afficher: Personnel financier

# Test des permissions
'FINANCE' in ['FINANCE', 'ADMIN', 'SUPER_ADMIN']  # ✅ True
'FINANCE' in ['PARENT', 'STUDENT', 'FINANCE', 'ADMIN', 'SUPER_ADMIN']  # ✅ True
```

## ✅ Solution Finale

**Le rôle correct à utiliser partout est : `FINANCE`**

- ✅ Base de données : `role='FINANCE'`
- ✅ Décorateurs : `'FINANCE'` dans les listes de rôles autorisés
- ✅ Conditions : `request.user.role == 'FINANCE'`
- ✅ Script de création : `role='FINANCE'`

## 🚀 Actions pour Tester

1. **Déconnectez-vous** de l'application
2. **Reconnectez-vous** avec :
   - Email : `finance@eschool.cd`
   - Mot de passe : `password123`
3. **Accédez à** : http://localhost:8000/finance/invoices/
4. **Résultat attendu** : ✅ Liste des factures affichée

---

**Date de correction :** 19 octobre 2025  
**Fichiers modifiés :**
- `core/decorators/permissions.py`
- `accounts/views.py`
- `scripts/reset_and_populate.py`
- Base de données (compte finance@eschool.cd)
