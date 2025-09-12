#!/usr/bin/env python3
"""
Script de test pour les actions en lot des factures
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
from django.test import Client
from django.contrib.auth import authenticate

def test_bulk_actions():
    print("=== Test des actions en lot des factures ===\n")
    
    # Compter les factures
    total_invoices = Invoice.objects.count()
    print(f"📊 Total factures dans la base: {total_invoices}")
    
    # Afficher la répartition par statut
    statuses = Invoice.objects.values_list('status', flat=True).distinct()
    for status in statuses:
        count = Invoice.objects.filter(status=status).count()
        print(f"   - {status}: {count} factures")
    
    print()
    
    # Tester l'accès avec un utilisateur staff
    print("🔑 Test d'accès utilisateur staff...")
    try:
        # Trouver un utilisateur staff
        staff_user = User.objects.filter(is_staff=True).first()
        if not staff_user:
            print("❌ Aucun utilisateur staff trouvé")
            return
        
        print(f"   ✅ Utilisateur staff trouvé: {staff_user.email}")
        
        # Test avec le client de test Django
        client = Client()
        client.force_login(staff_user)
        
        # Accéder à la page des factures
        response = client.get('/finance/invoices/')
        print(f"   📄 Page factures: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Page accessible")
            
            # Vérifier la présence des éléments de bulk actions
            content = response.content.decode()
            
            checks = [
                ('select-all', 'Checkbox "Tout sélectionner"'),
                ('bulk-update-btn', 'Bouton "Modifier"'),
                ('status-select', 'Sélecteur de statut'),
                ('invoice-checkbox', 'Checkboxes des factures'),
                ('submitBulkAction', 'Fonction JavaScript')
            ]
            
            for element_id, description in checks:
                if element_id in content:
                    print(f"   ✅ {description} présent")
                else:
                    print(f"   ❌ {description} manquant")
        
        # Test d'une action en lot simulée
        print("\n🧪 Test d'action en lot simulée...")
        
        # Sélectionner 3 factures en brouillon
        draft_invoices = Invoice.objects.filter(status='DRAFT')[:3]
        if draft_invoices.exists():
            invoice_ids = [str(inv.id) for inv in draft_invoices]
            
            # Simuler une requête POST
            test_data = {
                'action': 'bulk_status_change',
                'new_status': 'SENT',
                'selected_invoices': invoice_ids
            }
            
            print(f"   📤 Test avec {len(invoice_ids)} factures:")
            for inv in draft_invoices:
                print(f"      - Facture {inv.invoice_number} (ID: {inv.id})")
            
            # Pour des raisons de sécurité, on ne fait que simuler
            print("   ⚠️  Simulation seulement (pas de modification réelle)")
            
        else:
            print("   ⚠️  Aucune facture en brouillon pour tester")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n✅ Test terminé")

if __name__ == '__main__':
    test_bulk_actions()
