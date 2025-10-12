# Correction des Calculs Financiers dans les Dashboards

**Date:** 12 octobre 2025  
**Fichier modifié:** `accounts/views.py`  
**Commit:** En cours

## Problème Identifié

Les dashboards `parent_dashboard()` et `student_dashboard()` utilisaient une méthode incorrecte pour calculer les montants en attente, ignorant les paiements partiels.

### Code Incorrect

```python
# Ancien code dans parent_dashboard() et student_dashboard()
pending_invoices = Invoice.objects.filter(
    student=student,
    status__in=['PENDING', 'SENT']
).order_by('-due_date')

total_pending = pending_invoices.aggregate(
    total=Sum('total_amount')
)['total'] or 0
```

**Problèmes :**
1. Utilise le `total_amount` complet de la facture
2. Ignore les paiements partiels déjà effectués
3. Affiche des montants incorrects (trop élevés)

**Exemple :**
- Facture de 1000€ avec 600€ déjà payés
- Ancien code affiche : 1000€ en attente ❌
- Devrait afficher : 400€ en attente ✅

## Solution Implémentée

Utilisation des propriétés calculées du modèle `Invoice` :
- `invoice.balance` : Retourne `total_amount - paid_amount`
- `invoice.is_paid` : Retourne `True` si `balance <= 0`

### parent_dashboard() (Lignes 834-881)

```python
# Nouveau code - calcule le solde réel avec paiements partiels
all_child_invoices = Invoice.objects.filter(student=child).prefetch_related('payments')
pending_invoices_list = [inv for inv in all_child_invoices if not inv.is_paid]
total_pending = sum(inv.balance for inv in pending_invoices_list)

child_data = {
    'pending_invoices': pending_invoices_list,
    'total_pending': float(total_pending),
}

# Accumulation dans les statistiques globales
overall_stats['total_pending_amount'] += float(total_pending)
```

**Changements :**
1. Récupération de toutes les factures avec `prefetch_related('payments')` (optimisation)
2. Filtrage par `invoice.is_paid` au lieu de `status`
3. Calcul avec `invoice.balance` au lieu de `total_amount`
4. Conversion `float()` pour éviter les erreurs de type Decimal
5. Initialisation de `total_pending_amount` à `0.0` (float) au lieu de `0` (int)

### student_dashboard() (Lignes 461-476)

```python
# Nouveau code - calcul avec balance réelle (inclut les paiements partiels)
all_student_invoices = Invoice.objects.filter(student=student).prefetch_related('payments')
pending_invoices_list = [inv for inv in all_student_invoices if not inv.is_paid]
pending_invoices = sorted(pending_invoices_list, key=lambda x: x.due_date, reverse=True)[:3]
total_pending = sum(inv.balance for inv in pending_invoices_list)

context.update({
    'pending_invoices': pending_invoices,
    'recent_payments': recent_payments,
    'total_pending_amount': float(total_pending)
})
```

**Changements :**
1. Même logique que parent_dashboard
2. Tri manuel par `due_date` pour les 3 factures les plus récentes
3. Calcul du total sur toutes les factures non payées (pas seulement les 3 affichées)

## Optimisations de Performance

**Requête optimisée :**
```python
Invoice.objects.filter(student=student).prefetch_related('payments')
```

**Avantages :**
- Évite les requêtes N+1 lors de l'accès à `invoice.balance`
- `balance` utilise `invoice.paid_amount` qui fait `Sum` des paiements
- Avec `prefetch_related`, tous les paiements sont chargés en 2 requêtes au lieu de N+1

## Cohérence avec les Autres Vues

Cette correction aligne les dashboards avec les corrections déjà apportées :
- ✅ `parent_child_detail()` (lignes 2741-2970)
- ✅ `parent_children_overview()` (lignes 2598-2740)
- ✅ `parent_dashboard()` (lignes 766-950)
- ✅ `student_dashboard()` (lignes 421-550)

Tous utilisent maintenant la même logique :
```python
all_invoices = Invoice.objects.filter(...).prefetch_related('payments')
pending = [inv for inv in all_invoices if not inv.is_paid]
total = sum(inv.balance for inv in pending)
```

## Tests de Vérification

Pour vérifier la correction :

1. **Créer des factures avec paiements partiels :**
```python
# Dans Django shell
from finance.models import Invoice, Payment
from accounts.models import Student

student = Student.objects.first()
invoice = Invoice.objects.create(student=student, total_amount=1000, status='SENT')
Payment.objects.create(invoice=invoice, amount=600, status='COMPLETED')

# Vérifier
print(f"Total: {invoice.total_amount}€")  # 1000€
print(f"Payé: {invoice.paid_amount}€")    # 600€
print(f"Solde: {invoice.balance}€")       # 400€
print(f"Est payée: {invoice.is_paid}")    # False
```

2. **Vérifier dans les dashboards :**
- Dashboard parent : Doit afficher 400€ en attente
- Dashboard étudiant : Doit afficher 400€ en attente
- Page parent_child_detail : Doit afficher 400€ dans colonne "Solde"
- Page parent_children_overview : Doit afficher 400€ total

## Corrections de Type

**Problème initial :**
```python
overall_stats = {
    'total_pending_amount': 0,  # int
}
overall_stats['total_pending_amount'] += float(total_pending)  # Erreur de type
```

**Solution :**
```python
overall_stats = {
    'total_pending_amount': 0.0,  # float
}
overall_stats['total_pending_amount'] += float(total_pending)  # OK
```

## Impact

- ✅ Les montants en attente affichent maintenant le solde réel
- ✅ Les paiements partiels sont correctement déduits
- ✅ Cohérence entre toutes les vues parent et étudiant
- ✅ Performance optimisée avec `prefetch_related`
- ✅ Code plus maintenable (utilise les propriétés du modèle)

## Prochaines Étapes

- [ ] Tester avec des données réelles (paiements partiels)
- [ ] Vérifier le dashboard administrateur
- [ ] Vérifier le dashboard enseignant (pas de finances)
- [ ] Commit des modifications
- [ ] Documentation utilisateur mise à jour
