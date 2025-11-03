# Permissions du Gestionnaire Financier (FINANCE_MANAGER)

## 📋 Résumé

Ce document décrit les permissions accordées au rôle **FINANCE_MANAGER** et les modifications apportées au système pour permettre la gestion complète des finances.

## 🔑 Compte de Test

**Email:** `finance@eschool.cd`  
**Mot de passe:** `password123`  
**Nom:** Marie Finances  
**Rôle:** FINANCE (Personnel financier)

> ⚠️ **Important:** Le rôle dans le modèle User s'appelle `FINANCE`, pas `FINANCE_MANAGER`.

## ✅ Permissions Accordées

Le rôle FINANCE_MANAGER a maintenant accès à toutes les fonctionnalités financières :

### 1. Gestion des Factures
- ✅ **Consulter** toutes les factures (`/finance/invoices/`)
- ✅ **Créer** de nouvelles factures (`/finance/invoices/create/`)
- ✅ **Modifier** les factures existantes (`/finance/invoices/<id>/edit/`)
- ✅ **Générer** des factures automatiquement (`/finance/invoices/generate/`)
- ✅ **Télécharger** les factures en PDF (`/finance/invoices/<id>/pdf/`)

### 2. Gestion des Paiements
- ✅ **Consulter** tous les paiements (`/finance/payments/`)
- ✅ **Créer** des paiements (`/finance/payments/create/`)
- ✅ **Confirmer** ou rejeter les paiements en attente (`/finance/payments/<id>/confirm/`)
- ✅ **Voir** les paiements en attente (`/finance/payments/pending/`)

### 3. Gestion des Types de Frais
- ✅ **Consulter** les types de frais (`/finance/fee-types/`)
- ✅ **Créer** de nouveaux types de frais (`/finance/fee-types/create/`)
- ✅ **Gérer** les structures tarifaires (`/finance/fee-structures/`)

### 4. Rapports Financiers
- ✅ **Consulter** le rapport financier journalier (`/finance/reports/daily/`)
- ✅ **Générer** des rapports pour des dates spécifiques (`/finance/reports/daily/generate/`)
- ✅ **Exporter** les rapports en PDF (`/finance/reports/daily/<date>/pdf/`)
- ✅ **Exporter** les rapports en Excel (`/finance/reports/daily/<date>/excel/`)

### 5. Accès au Dashboard
- ✅ Accès au dashboard administratif avec statistiques
- ✅ Visualisation des KPIs financiers

## 🔧 Modifications Techniques

### 1. Décorateur `@finance_required`

Le décorateur `@finance_required` a été créé dans `core/decorators/permissions.py` :

```python
def finance_required(view_func):
    """
    Décorateur pour les vues réservées au personnel financier
    """
    return role_required(['FINANCE', 'ADMIN', 'SUPER_ADMIN'])(view_func)
```

Ce décorateur autorise l'accès aux rôles :
- `FINANCE` (Personnel financier)
- `ADMIN`
- `SUPER_ADMIN`

### 2. Décorateur `@finance_or_family_required`

Un nouveau décorateur a été créé pour les vues de consultation accessibles par plusieurs rôles :

```python
def finance_or_family_required(view_func):
    """
    Décorateur pour les vues financières accessibles aux gestionnaires financiers,
    parents, étudiants ET administrateurs
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        allowed_roles = ['PARENT', 'STUDENT', 'FINANCE_MANAGER', 'ADMIN', 'SUPER_ADMIN']
        if request.user.role not in allowed_roles:
            raise PermissionDenied(
                "Accès réservé au personnel financier, parents, étudiants et administrateurs"
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper
```

Ce décorateur autorise :
- `FINANCE_MANAGER` - Peut voir toutes les factures/paiements
- `PARENT` - Peut voir ses propres factures
- `STUDENT` - Peut voir ses propres factures
- `ADMIN` et `SUPER_ADMIN` - Accès complet

### 2. Décorateur `@finance_or_family_required`

Un nouveau décorateur a été créé pour les vues de consultation accessibles par plusieurs rôles :

```python
def finance_or_family_required(view_func):
    """
    Décorateur pour les vues financières accessibles aux gestionnaires financiers,
    parents, étudiants ET administrateurs
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        allowed_roles = ['PARENT', 'STUDENT', 'FINANCE_MANAGER', 'ADMIN', 'SUPER_ADMIN']
        if request.user.role not in allowed_roles:
            raise PermissionDenied(
                "Accès réservé au personnel financier, parents, étudiants et administrateurs"
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper
```

Ce décorateur autorise :
- `FINANCE_MANAGER` - Peut voir toutes les factures/paiements
- `PARENT` - Peut voir ses propres factures
- `STUDENT` - Peut voir ses propres factures
- `ADMIN` et `SUPER_ADMIN` - Accès complet

### 3. Vues Modifiées

### 3. Vues Modifiées

Les vues suivantes ont été mises à jour :

**Vues avec `@finance_required` (gestion - finance uniquement) :**
- `invoice_create()` - Ligne 287
- `invoice_edit()` - Ligne 544
- `invoice_generate()` - Ligne 851
- `payment_confirm()` - Ligne 478
- `pending_payments()` - Ligne 527
- `daily_financial_report()` - Ligne 998
- `daily_financial_report_generate()` - Ligne 1110
- `daily_financial_report_export_pdf()` - Ligne 1158
- `daily_financial_report_export_excel()` - Ligne 1180

**Vues avec `@finance_or_family_required` (consultation - finance + familles) :**
- `invoice_list()` - Ligne 157 (changé de `@parent_or_student_required`)
- `invoice_detail()` - Ligne 372 (changé de `@parent_or_student_required`)
- `invoice_pay()` - Ligne 399 (changé de `@parent_or_student_required`)
- `invoice_pdf()` - Ligne 746 (changé de `@parent_or_student_required`)
- `payment_list()` - Ligne 752 (changé de `@parent_or_student_required`)
- `payment_detail()` - Ligne 796 (changé de `@parent_or_student_required`)

### 4. Dashboard

### 4. Dashboard

La vue `dashboard()` dans `accounts/views.py` a été mise à jour pour rediriger les utilisateurs FINANCE_MANAGER vers le dashboard administratif :

```python
# Dashboard administrateur et gestionnaire financier
if request.user.role in ['ADMIN', 'SUPER_ADMIN', 'FINANCE_MANAGER'] or request.user.is_staff:
    return admin_dashboard(request)
```

### 5. Script de Génération de Données

Le script `scripts/reset_and_populate.py` a été mis à jour pour créer automatiquement un compte FINANCE_MANAGER lors de la génération des données de test :

**Nouvelle étape 2B :**
```python
# Créer un gestionnaire financier
finance_user = User.objects.create_user(
    email='finance@eschool.cd',
    password='password123',
    first_name='Marie',
    last_name='Finances',
    role='FINANCE_MANAGER',
    gender='F',
    is_active=True,
    is_staff=True,
    date_of_birth=date(1985, 5, 15)
)
```

## 📊 Comparaison des Rôles

| Fonctionnalité | ADMIN | FINANCE_MANAGER | TEACHER | PARENT | STUDENT |
|----------------|-------|-----------------|---------|--------|---------|
| Gestion des factures | ✅ | ✅ | ❌ | ❌ | ❌ |
| Gestion des paiements | ✅ | ✅ | ❌ | ❌ | ❌ |
| Confirmation paiements | ✅ | ✅ | ❌ | ❌ | ❌ |
| Rapports financiers | ✅ | ✅ | ❌ | ❌ | ❌ |
| Gestion utilisateurs | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gestion académique | ✅ | ❌ | Partiel | ❌ | ❌ |
| Voir ses factures | ✅ | ✅ | ❌ | ✅ | ✅ |

## 🧪 Tests

Pour tester les permissions du FINANCE_MANAGER :

1. **Se connecter** avec le compte `finance@eschool.cd`
2. **Accéder au dashboard** - devrait afficher les statistiques
3. **Naviguer vers** `/finance/invoices/` - devrait afficher toutes les factures
4. **Créer une facture** - `/finance/invoices/create/`
5. **Consulter les paiements** - `/finance/payments/`
6. **Confirmer un paiement** - `/finance/payments/pending/`
7. **Voir le rapport journalier** - `/finance/reports/daily/`

## 🔐 Sécurité

- Le rôle FINANCE_MANAGER **NE PEUT PAS** :
  - Créer ou modifier des utilisateurs
  - Accéder aux données académiques (notes, présences)
  - Gérer les classes et emplois du temps
  - Modifier les paramètres système

- Le rôle FINANCE_MANAGER **PEUT** :
  - Gérer toutes les finances (factures, paiements, bourses)
  - Consulter et générer des rapports financiers
  - Confirmer ou rejeter des paiements
  - Exporter des données financières

## 📝 Notes Importantes

1. **Compatibilité** : Les vues utilisent toujours le décorateur `@staff_required` pour certaines fonctions basiques (types de frais, structures). Ce décorateur inclut déjà FINANCE_MANAGER.

2. **Dashboard** : Le FINANCE_MANAGER voit le même dashboard que l'ADMIN mais n'a pas accès aux fonctions administratives (gestion des utilisateurs, etc.).

3. **RBAC** : Les models Invoice et Payment utilisent des managers avec méthode `for_role()` pour filtrer les données selon le rôle. Le FINANCE_MANAGER peut voir toutes les factures et paiements.

4. **Menu de navigation** : Le template du dashboard devrait être mis à jour pour afficher/masquer les liens selon le rôle (à implémenter si nécessaire).

## 🚀 Prochaines Étapes

1. ✅ Permissions accordées
2. ✅ Compte de test créé
3. ✅ Dashboard configuré
4. 🔲 Tester toutes les fonctionnalités avec le compte finance
5. 🔲 Créer des comptes FINANCE_MANAGER réels pour la production
6. 🔲 Documenter les procédures financières

---

**Date de création:** 19 octobre 2025  
**Dernière mise à jour:** 19 octobre 2025  
**Version:** 1.0
