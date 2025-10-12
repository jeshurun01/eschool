# Correction des sections Finance et Communication - parent_child_detail

## Problèmes identifiés

### Section Finance
1. **Variables manquantes** : Le template utilisait `financial_stats` et `recent_invoices` non fournis par la vue
2. **Attribut incorrect** : Le template utilisait `invoice.amount` au lieu de `invoice.total_amount`
3. **Statuts incorrects** : Le template utilisait `PENDING` au lieu de `SENT` pour le statut "Envoyée"
4. **Lien non fonctionnel** : Le lien "Voir" pointait vers `#` au lieu de l'URL de détail de la facture

### Section Communication
1. **Variable manquante** : Le template utilisait `recent_messages` non fourni par la vue
2. **Attribut incorrect** : Le template utilisait `message.sent_at` au lieu de `message.sent_date`
3. **Nom complet** : Utilisation de `sender.first_name` et `sender.last_name` au lieu de `sender.full_name`

## Corrections apportées

### 1. Statistiques financières complètes (`accounts/views.py`, ligne ~2861-2897)

**Ajouté** :
```python
# Toutes les factures récentes
recent_invoices = Invoice.objects.filter(
    student=child
).order_by('-issue_date')[:10]

# Paiements ce mois
month_start = today.replace(day=1)
paid_this_month = Invoice.objects.filter(
    student=child,
    status='PAID',
    payment_date__gte=month_start
).aggregate(
    total=Sum('total_amount'),
    count=Count('id')
)

# Prochaine échéance
next_invoice = pending_invoices.order_by('due_date').first()

# Statistiques financières
financial_stats = {
    'total_balance': total_balance,           # Solde total à payer
    'pending_amount': total_pending,          # Montant en attente
    'pending_invoices': pending_invoices.count(),  # Nombre de factures en attente
    'paid_this_month': paid_this_month['total'] or 0,  # Payé ce mois
    'payments_this_month': paid_this_month['count'] or 0,  # Nombre de paiements
    'next_due_date': next_invoice.due_date if next_invoice else None,
    'next_due_amount': next_invoice.total_amount if next_invoice else 0,
}
```

### 2. Template Finance corrigé

#### Statistiques financières
```html
<!-- AVANT -->
{{ financial_stats.total_balance|floatformat:0 }} €
{{ financial_stats.pending_amount|floatformat:0 }} €

<!-- APRÈS (maintenant fourni par la vue) -->
✓ Solde total calculé
✓ Montant en attente calculé
✓ Paiements du mois calculés
✓ Prochaine échéance identifiée
```

#### Tableau des factures
```html
<!-- AVANT -->
{{ invoice.amount|floatformat:2 }} €
{% if invoice.status == 'PENDING' %}

<!-- APRÈS -->
{{ invoice.total_amount|floatformat:2 }} €
{% if invoice.status == 'SENT' %}
{% elif invoice.status == 'DRAFT' %}
{% elif invoice.status == 'CANCELLED' %}
```

#### Lien de détail
```html
<!-- AVANT -->
<a href="#" class="text-blue-600">Voir</a>

<!-- APRÈS -->
<a href="{% url 'finance:invoice_detail' invoice.id %}" class="text-blue-600">Voir</a>
```

### 3. Messages récents de communication (`accounts/views.py`, ligne ~2942-2945)

**Ajouté** :
```python
from communication.models import Message
recent_messages = Message.objects.filter(
    recipient=request.user
).select_related('sender').order_by('-sent_date')[:5]
```

### 4. Template Communication corrigé

```html
<!-- AVANT -->
{{ message.sender.first_name }} {{ message.sender.last_name }}
{{ message.sent_at|timesince }}

<!-- APRÈS -->
{{ message.sender.full_name }}
{{ message.sent_date|timesince }}
```

## Variables ajoutées au contexte

```python
context = {
    # ... (variables existantes)
    'recent_invoices': recent_invoices,      # Liste des 10 dernières factures
    'financial_stats': financial_stats,      # Dict avec toutes les stats financières
    'recent_messages': recent_messages,      # Liste des 5 derniers messages
}
```

## Statuts de factures supportés

Le template affiche maintenant correctement tous les statuts :
- ✅ **PAID** (Payée) - Badge vert
- ✅ **SENT** (Envoyée) - Badge jaune
- ✅ **DRAFT** (Brouillon) - Badge gris
- ✅ **OVERDUE** (En retard) - Badge rouge
- ✅ **CANCELLED** (Annulée) - Badge rouge

## Impact

### Avant
- ❌ Section Finance vide ou avec erreurs
- ❌ Aucune statistique financière affichée
- ❌ Section Communication vide
- ❌ Liens vers factures non fonctionnels

### Après
- ✅ Statistiques financières complètes :
  - Solde total à payer
  - Montant en attente
  - Paiements du mois en cours
  - Prochaine échéance identifiée
- ✅ Liste des 10 dernières factures avec tous les détails
- ✅ Liens fonctionnels vers le détail des factures
- ✅ Messages récents (5 derniers) affichés
- ✅ Tous les statuts de factures correctement affichés

## Tests recommandés

1. **Section Finance** :
   - Vérifier l'affichage des statistiques (solde, en attente, payé ce mois)
   - Vérifier le tableau des factures avec différents statuts
   - Tester le lien vers le détail d'une facture
   - Vérifier l'affichage de la prochaine échéance

2. **Section Communication** :
   - Vérifier l'affichage des messages récents
   - Vérifier que le nom complet de l'expéditeur s'affiche
   - Vérifier la date relative (timesince)
   - Tester avec 0 messages

3. **Test avec données manquantes** :
   - Élève sans factures : vérifier le message "Aucune facture disponible"
   - Parent sans messages : vérifier le message "Aucun message récent"
   - Factures sans échéance : vérifier l'affichage "-"

## Fichiers modifiés

- `accounts/views.py` : Fonction `parent_child_detail` - ajout de `financial_stats`, `recent_invoices`, `recent_messages`
- `templates/accounts/parent_child_detail.html` : Corrections des variables et ajout de tous les statuts de factures
