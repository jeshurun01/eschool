# Correction de la page Vue d'ensemble des enfants (parent_children_overview)

## URL
`/accounts/parent/children/`

## Problèmes identifiés

### 1. Calculs financiers incorrects
- **Problème** : Utilisait `status__in=['DRAFT', 'SENT']` sans considérer les paiements partiels
- **Conséquence** : Un parent voyait 1000 € de dette même si 600 € avaient été payés

### 2. Factures en retard mal calculées
- **Problème** : Utilisait `status='OVERDUE'` au lieu de vérifier la date d'échéance
- **Conséquence** : Dépendait du statut manuel au lieu de calculer automatiquement

### 3. Variables template incorrectes
- **Problème** : Utilisait `{{ average_grade }}` au lieu de `{{ average_grade_global }}`
- **Problème** : Utilisait `{{ average_attendance }}` au lieu de `{{ average_attendance_global }}`
- **Problème** : Symbole monétaire `$` au lieu de `€`

## Corrections apportées

### 1. Calcul financier correct (`accounts/views.py`, ligne ~2668-2684)

#### AVANT (incorrect)
```python
# Ne considérait que le statut sans les paiements
pending_invoices = Invoice.objects.filter(
    student=child,
    status__in=['DRAFT', 'SENT']
)
overdue_invoices = Invoice.objects.filter(
    student=child,
    status='OVERDUE'
)

total_pending = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
total_overdue = overdue_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
```

#### APRÈS (correct)
```python
# Récupère toutes les factures avec paiements
all_child_invoices = Invoice.objects.filter(student=child).prefetch_related('payments')

# Identifie les factures non entièrement payées
pending_invoices_list = [inv for inv in all_child_invoices if not inv.is_paid]

# Identifie les factures en retard (échéance passée + non payées)
overdue_invoices_list = [
    inv for inv in pending_invoices_list 
    if inv.due_date and inv.due_date < today
]

# Calcule le vrai solde (montant - paiements)
total_pending = sum(inv.balance for inv in pending_invoices_list)
total_overdue = sum(inv.balance for inv in overdue_invoices_list)
```

### 2. Corrections template (`parent_children_overview.html`)

#### Variables globales
```html
<!-- AVANT -->
Moyenne: {{ average_grade|floatformat:1 }}/20
{{ average_attendance|floatformat:1 }}%
${{ total_pending_amount|floatformat:0 }}

<!-- APRÈS -->
Moyenne: {{ average_grade_global|floatformat:1 }}/20
{{ average_attendance_global|floatformat:1 }}%
{{ total_pending_amount|floatformat:0 }} €
```

#### Libellés
```html
<!-- AVANT -->
<p class="text-sm text-gray-600">Factures</p>

<!-- APRÈS -->
<p class="text-sm text-gray-600">Solde à payer</p>
```

## Données affichées (vérification)

### Pour chaque enfant
✅ **Notes** :
- Moyenne générale sur la période
- Meilleure note
- Pire note
- Performance par matière

✅ **Présences** :
- Taux de présence calculé depuis `DailyAttendanceSummary`
- Basé sur `present_sessions + late_sessions / total_sessions`

✅ **Finances** :
- **Solde à payer** : Somme des `invoice.balance` (vrai solde après paiements)
- **En retard** : Somme des soldes des factures dont `due_date < today`
- **Statut** : 
  - 🔴 "En retard" si `total_overdue > 0`
  - 🟡 "En attente" si `total_pending > 0`
  - 🟢 "À jour" si tout est payé

### Statistiques globales
✅ **Total enfants** : Nombre d'enfants associés au parent
✅ **Moyenne générale** : Moyenne des moyennes de tous les enfants
✅ **Taux présence global** : Moyenne des taux de présence
✅ **Solde total** : Somme de tous les soldes à payer
✅ **En retard** : Somme de tous les montants en retard

## Exemple concret

### Situation
**Enfant 1** :
- Facture INV001: 1000 € (payé 600 €, reste 400 €, échéance 01/10)
- Facture INV002: 500 € (payé 0 €, reste 500 €, échéance 15/11)
- Aujourd'hui : 12/10/2025

**Enfant 2** :
- Facture INV003: 800 € (payé 800 €, reste 0 €)

### AVANT (incorrect)
```
Enfant 1:
  Solde: 1500 € ❌ (ne déduisait pas les 600 € payés)
  En retard: 0 € ❌ (ne détectait pas l'échéance passée)
  Statut: En attente 🟡

Enfant 2:
  Solde: 0 € ✅
  Statut: À jour 🟢

Total: 1500 € ❌
```

### APRÈS (correct)
```
Enfant 1:
  Solde: 900 € ✅ (400 € + 500 €)
  En retard: 400 € ✅ (échéance 01/10 passée)
  Statut: En retard 🔴

Enfant 2:
  Solde: 0 € ✅
  Statut: À jour 🟢

Total: 900 € ✅
En retard: 400 € ✅
```

## Optimisations

### Performance
```python
# Une seule requête supplémentaire pour tous les paiements
all_child_invoices = Invoice.objects.filter(student=child).prefetch_related('payments')
```
- Évite N+1 queries
- Les propriétés `balance`, `paid_amount`, `is_paid` utilisent les données pré-chargées

### Calcul automatique des retards
```python
# Ne dépend plus du statut manuel, vérifie la date
if inv.due_date and inv.due_date < today
```

## Tests recommandés

### Test 1 : Enfant avec paiement partiel
1. Créer facture 1000 €
2. Créer paiement 600 €
3. ✅ Vérifier affichage : "900 € Solde à payer"

### Test 2 : Facture en retard
1. Créer facture échéance 01/10/2025
2. Payer partiellement 300 € sur 1000 €
3. ✅ Vérifier : "700 € en retard"

### Test 3 : Plusieurs enfants
1. Enfant 1 : 400 € de solde
2. Enfant 2 : 0 € (tout payé)
3. ✅ Vérifier total global : "400 €"

### Test 4 : Périodes différentes
1. Tester filtre "7 jours", "30 jours", "Semestre"
2. ✅ Vérifier que les notes et présences changent
3. ✅ Vérifier que les finances restent correctes

## Impact

### Avant ❌
- Soldes incorrects (montants totaux au lieu de soldes restants)
- Factures en retard non détectées automatiquement
- Variables template manquantes ou incorrectes
- Symbole $ au lieu de €

### Après ✅
- Calculs financiers exacts avec paiements partiels
- Détection automatique des retards via date d'échéance
- Libellé clair : "Solde à payer" au lieu de "Factures"
- Toutes les données sont réelles et synchronisées
- Symbole € correct

## Fichiers modifiés

- `accounts/views.py` : 
  - Ligne ~2668-2684 : Calcul financier corrigé avec `prefetch_related`
  
- `templates/accounts/parent_children_overview.html` :
  - Ligne ~47, 55 : Variables `average_grade_global` et `average_attendance_global`
  - Ligne ~63, 68 : Symbole `€` au lieu de `$`
  - Ligne ~63, 155 : Libellé "Solde à payer" au lieu de "Factures"
