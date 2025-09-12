#!/usr/bin/env python3
"""
Script pour tester la modification en lot des factures
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from finance.models import Invoice

def test_bulk_status_change():
    """Tester la modification en lot via une requête POST simulée"""
    
    print("=== Test de modification en lot des statuts ===\n")
    
    # Créer un client de test
    client = Client()
    
    # Récupérer un utilisateur staff
    User = get_user_model()
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            print("❌ Aucun utilisateur staff trouvé")
            return
        
        print(f"✅ Utilisateur trouvé: {admin_user.username}")
        
        # Se connecter
        client.force_login(admin_user)
        print("✅ Connexion réussie")
        
        # Récupérer quelques factures
        invoices = Invoice.objects.all()[:3]
        if not invoices:
            print("❌ Aucune facture trouvée")
            return
        
        print(f"📄 {len(invoices)} factures trouvées pour le test")
        
        # Afficher l'état initial
        print("\n📊 État initial des factures:")
        for invoice in invoices:
            print(f"  {invoice.invoice_number}: {invoice.status}")
        
        # Préparer les données POST
        invoice_ids = [str(invoice.pk) for invoice in invoices]
        post_data = {
            'action': 'bulk_status_change',
            'new_status': 'SENT',
            'selected_invoices': invoice_ids
        }
        
        print(f"\n🔄 Tentative de modification vers 'SENT'")
        print(f"   IDs: {invoice_ids}")
        
        # Envoyer la requête POST
        response = client.post('/finance/invoices/', post_data)
        
        print(f"📡 Réponse HTTP: {response.status_code}")
        
        if response.status_code == 302:  # Redirection après succès
            print("✅ Redirection détectée (succès attendu)")
            
            # Vérifier les changements
            print("\n📊 État après modification:")
            for invoice in Invoice.objects.filter(pk__in=[inv.pk for inv in invoices]):
                print(f"  {invoice.invoice_number}: {invoice.status}")
                
        else:
            print(f"❌ Réponse inattendue: {response.status_code}")
            print(f"Contenu: {response.content[:500]}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_view_get():
    """Tester l'accès GET à la vue"""
    
    print("\n=== Test d'accès GET ===\n")
    
    client = Client()
    User = get_user_model()
    
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            client.force_login(admin_user)
        
        response = client.get('/finance/invoices/')
        print(f"📡 Réponse GET: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page accessible")
            
            # Vérifier la présence du formulaire
            content = response.content.decode('utf-8')
            if 'bulk-actions-form' in content:
                print("✅ Formulaire d'actions en lot trouvé")
            else:
                print("❌ Formulaire d'actions en lot non trouvé")
                
            if 'selected_invoices' in content:
                print("✅ Cases à cocher trouvées")
            else:
                print("❌ Cases à cocher non trouvées")
        else:
            print(f"❌ Erreur d'accès: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_view_get()
    test_bulk_status_change()
