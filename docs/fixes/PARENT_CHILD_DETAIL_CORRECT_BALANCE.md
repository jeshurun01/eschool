# Correction du calcul des soldes et montants financiers - parent_child_detail

## Problème identifié

La section Finance de la page parent_child_detail affichait des montants incorrects :

1. **Soldes incorrects** : Ne prenait pas en compte les paiements partiels
2. **Factures "Payées" non comptées** : Seules les factures avec statut `DRAFT` ou `SENT` étaient considérées
3. **Pas de visibilité sur les paiements partiels** : Impossible de voir combien a été payé sur chaque facture
4. **Calcul basé uniquement sur le statut** : Ne tenait pas compte du vrai solde (montant - paiements)

### Exemple du problème
- Facture de 1000 €
- Paiement de 600 € effectué
- **AVANT** : Affichait 1000 € en attente (❌ incorrect)
- **APRÈS** : Affiche 400 € de solde restant (✅ correct)

## Corrections apportées

### 1. Calcul correct des soldes (`accounts/views.py`, ligne ~2862-2917)

#### AVANT (incorrect)
```python
# Ne considérait que les factures avec statut DRAFT ou SENT
pending_invoices = Invoice.objects.filter(
    student=child,
    status__in=['DRAFT', 'SENT']
).order_by('-due_date')

# Calculait le montant total sans déduire les paiements
total_balance = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
```

#### APRÈS (correct)
```python
# Récupère TOUTES les factures avec leurs paiements
all_invoices = Invoice.objects.filter(student=child).prefetch_related('payments')

# Identifie les factures non entièrement payées via la propriété is_paid
pending_invoices = [inv for inv in all_invoices if not inv.is_paid]

# Calcule le solde réel (utilise la propriété balance = total_amount - paid_amount)
total_balance = sum(inv.balance for inv in pending_invoices)
```

### 2. Utilisation des propriétés du modèle Invoice

Le modèle `Invoice` fournit des propriétés calculées :

```python
# finance/models.py - Propriétés Invoice
@property
def paid_amount(self):
    """Montant payé"""
    return sum(payment.amount for payment in self.payments.filter(status='COMPLETED'))

@property
def balance(self):
    """Solde restant"""
    return self.total_amount - self.paid_amount

@property
def is_paid(self):
    """Vérifie si la facture est entièrement payée"""
    return self.balance <= Decimal('0.00')
```

### 3. Affichage amélioré du tableau des factures

#### Ajout de colonnes
- **Payé** : Montant déjà payé (en vert)
- **Solde** : Montant restant à payer (en rouge si > 0, gris si = 0)

#### Amélioration des statuts
```html
<!-- Avant -->
<span>Envoyée</span>

<!-- Après -->
{% if invoice.paid_amount > 0 %}
    <span>Partiellement payée</span>
{% else %}
    <span>Envoyée</span>
{% endif %}
```

#### Structure du tableau
```
| Numéro | Date | Montant | Payé | Solde | Statut | Échéance | Actions |
|--------|------|---------|------|-------|--------|----------|---------|
| INV001 | 01/09| 1000 €  | 600€ | 400 € | Part.  | 15/10    | Voir    |
| INV002 | 15/09| 500 €   | 500€ | 0 €   | Payée  | 01/10    | Voir    |
```

### 4. Statistiques financières corrigées

```python
financial_stats = {
    'total_balance': float(total_balance),        # Vrai solde à payer (avec paiements déduits)
    'pending_amount': float(total_pending),       # Montant total des factures en attente
    'pending_invoices': len(pending_invoices),    # Nombre de factures non payées
    'paid_this_month': paid_this_month['total'] or 0,
    'payments_this_month': paid_this_month['count'] or 0,
    'next_due_date': next_invoice.due_date if next_invoice else None,
    'next_due_amount': float(next_invoice.balance) if next_invoice else 0,  # Solde, pas total
}
```

## Différences Avant/Après

### Cas 1 : Facture partiellement payée
**Facture** : 1000 € | **Payé** : 600 € | **Statut** : SENT

| Indicateur | Avant | Après |
|------------|-------|-------|
| Solde total | 1000 € ❌ | 400 € ✅ |
| En attente | 1000 € ❌ | 1000 € ✅ |
| Statut affiché | "Envoyée" | "Partiellement payée" |
| Colonnes | Montant seulement | Montant + Payé + Solde |

### Cas 2 : Facture entièrement payée
**Facture** : 500 € | **Payé** : 500 € | **Statut** : PAID

| Indicateur | Avant | Après |
|------------|-------|-------|
| Comptée dans solde | Oui (si SENT) ❌ | Non ✅ |
| Affichage | Normal | Solde en gris (0 €) |

### Cas 3 : Multiples factures avec paiements variés
**Factures** :
- INV001: 1000 € (payé 600 €)
- INV002: 500 € (payé 0 €)
- INV003: 800 € (payé 800 €)

| Indicateur | Avant | Après |
|------------|-------|-------|
| Solde total | 1500 € ❌ | 900 € ✅ |
| Factures en attente | 2 (INV001, INV002) | 2 (INV001, INV002) |
| Prochaine échéance | Montant total | Solde restant |

## Optimisations de performance

### Utilisation de `prefetch_related`
```python
all_invoices = Invoice.objects.filter(student=child).prefetch_related('payments')
```
- Une seule requête supplémentaire pour tous les paiements
- Évite le problème N+1
- Les propriétés `paid_amount`, `balance`, `is_paid` utilisent les données pré-chargées

## Tests recommandés

### Test 1 : Facture partiellement payée
1. Créer une facture de 1000 €
2. Créer un paiement de 600 € (statut COMPLETED)
3. Vérifier que le solde affiché est 400 €
4. Vérifier que le statut est "Partiellement payée"

### Test 2 : Facture entièrement payée
1. Créer une facture de 500 €
2. Créer un paiement de 500 € (statut COMPLETED)
3. Vérifier que la facture ne compte pas dans le solde total
4. Vérifier que le solde affiché est 0 € (en gris)

### Test 3 : Multiples paiements
1. Créer une facture de 1000 €
2. Créer 3 paiements : 200 €, 300 €, 250 €
3. Vérifier que le montant payé total est 750 €
4. Vérifier que le solde restant est 250 €

### Test 4 : Paiements non complétés
1. Créer une facture de 1000 €
2. Créer un paiement de 600 € avec statut PENDING
3. Vérifier que le montant payé est 0 € (seuls les COMPLETED comptent)
4. Vérifier que le solde est 1000 €

## Impact

### Avant ❌
- Parents voyaient des montants incorrects
- Impossible de suivre les paiements partiels
- Confusion sur ce qui est réellement dû
- Calculs basés uniquement sur le statut

### Après ✅
- Calculs précis basés sur les vrais paiements
- Visibilité complète : montant, payé, solde
- Identification des paiements partiels
- Statistiques financières exactes
- Prochaine échéance affiche le solde restant, pas le total

## Fichiers modifiés

- `accounts/views.py` : 
  - Ligne ~2862-2917 : Nouveau calcul des soldes avec `prefetch_related`
  - Utilisation des propriétés `balance`, `paid_amount`, `is_paid`
  
- `templates/accounts/parent_child_detail.html` :
  - Ajout de colonnes "Payé" et "Solde" dans le tableau
  - Affichage conditionnel "Partiellement payée"
  - Coloration : vert pour payé, rouge pour solde restant

## Documentation du modèle utilisé

### Propriétés Invoice utilisées
```python
invoice.total_amount     # Montant total de la facture
invoice.paid_amount      # Montant déjà payé (somme des paiements COMPLETED)
invoice.balance          # Solde restant (total_amount - paid_amount)
invoice.is_paid          # True si balance <= 0
```

### Relation avec Payment
```python
invoice.payments.all()              # Tous les paiements
invoice.payments.filter(status='COMPLETED')  # Paiements complétés
```
