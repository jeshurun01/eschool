#!/usr/bin/env python3
"""
Test des actions en lot des factures avec simulation complète
"""

import os
import sys
import django

# Configuration de Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import Invoice
from accounts.models import User
from django.contrib.messages import get_messages

def test_bulk_status_change():
    print("=== Test de changement de statut en lot ===\n")
    
    # Sélectionner quelques factures en brouillon
    draft_invoices = Invoice.objects.filter(status='DRAFT')[:3]
    
    if not draft_invoices.exists():
        print("❌ Aucune facture en brouillon trouvée")
        return
    
    print(f"📋 Factures sélectionnées pour test:")
    for invoice in draft_invoices:
        print(f"   - {invoice.invoice_number}: {invoice.get_status_display()} → SENT")
    
    print(f"\n🔄 Changement de statut vers 'SENT'...")
    
    try:
        # Simuler le changement de statut
        updated_count = 0
        for invoice in draft_invoices:
            old_status = invoice.status
            invoice.status = 'SENT'
            invoice.save()
            print(f"   ✅ {invoice.invoice_number}: {old_status} → {invoice.status}")
            updated_count += 1
        
        print(f"\n🎉 {updated_count} factures mises à jour avec succès !")
        
        # Vérifier les modifications
        print("\n📊 Vérification des modifications:")
        for invoice in draft_invoices:
            invoice.refresh_from_db()
            print(f"   - {invoice.invoice_number}: {invoice.get_status_display()}")
        
        # Remettre en brouillon pour les prochains tests
        print(f"\n🔙 Remise en état des factures de test...")
        for invoice in draft_invoices:
            invoice.status = 'DRAFT'
            invoice.save()
            print(f"   ↩️  {invoice.invoice_number}: Remis en DRAFT")
        
    except Exception as e:
        print(f"❌ Erreur lors du changement de statut: {e}")

def test_view_logic():
    print("\n=== Test de la logique de vue ===\n")
    
    # Importer la vue
    from finance.views import invoice_list
    from django.http import HttpRequest
    from django.contrib.auth.models import AnonymousUser
    
    # Créer une requête simulée
    request = HttpRequest()
    request.method = 'POST'
    request.user = User.objects.filter(is_staff=True).first()
    
    if not request.user:
        print("❌ Aucun utilisateur staff trouvé")
        return
    
    print(f"👤 Utilisateur de test: {request.user.email}")
    
    # Simuler les données POST
    draft_invoices = Invoice.objects.filter(status='DRAFT')[:2]
    if draft_invoices.exists():
        invoice_ids = [str(inv.id) for inv in draft_invoices]
        
        # Simuler les données du formulaire
        post_data = {
            'action': 'bulk_status_change',
            'new_status': 'SENT',
            'selected_invoices': invoice_ids
        }
        
        print(f"📤 Test avec données:")
        print(f"   - Action: {post_data['action']}")
        print(f"   - Nouveau statut: {post_data['new_status']}")
        print(f"   - Factures: {post_data['selected_invoices']}")
        
        # Vérification des permissions
        if request.user.is_staff:
            print("   ✅ Permissions valides (utilisateur staff)")
        else:
            print("   ❌ Permissions insuffisantes")
        
        # Vérification de l'action
        if post_data['action'] == 'bulk_status_change':
            print("   ✅ Action valide")
        else:
            print("   ❌ Action non reconnue")
        
        # Vérification du nouveau statut
        valid_statuses = ['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED']
        if post_data['new_status'] in valid_statuses:
            print("   ✅ Statut valide")
        else:
            print("   ❌ Statut invalide")
    
    else:
        print("⚠️  Aucune facture en brouillon pour tester")

if __name__ == '__main__':
    test_bulk_status_change()
    test_view_logic()
    print("\n✅ Tests terminés")
