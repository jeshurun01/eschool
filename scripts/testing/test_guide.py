#!/usr/bin/env python3
"""
Guide de test pour les actions en lot des factures
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

def show_test_guide():
    print("🔧 Guide de test pour les actions en lot des factures")
    print("=" * 60)
    
    # État actuel de la base
    print("\n📊 État actuel de la base de données:")
    statuses = ['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED']
    for status in statuses:
        count = Invoice.objects.filter(status=status).count()
        print(f"   {status}: {count} factures")
    
    # Utilisateurs staff
    staff_users = User.objects.filter(is_staff=True)
    print(f"\n👥 Utilisateurs staff disponibles: {staff_users.count()}")
    for user in staff_users[:3]:
        print(f"   - {user.email}")
    
    # Instructions de test
    print(f"\n🧪 Instructions de test manuelles:")
    print(f"1. Aller à: http://localhost:8000/finance/invoices/")
    print(f"2. Se connecter avec un utilisateur staff")
    print(f"3. Vérifier la présence de la section 'Actions en lot' en haut")
    print(f"4. Cocher quelques factures avec les checkboxes")
    print(f"5. Sélectionner un nouveau statut dans la liste déroulante")
    print(f"6. Cliquer sur le bouton 'Modifier'")
    print(f"7. Confirmer dans la popup")
    print(f"8. Vérifier que les statuts ont changé")
    
    # Factures de test recommandées
    draft_invoices = Invoice.objects.filter(status='DRAFT')[:5]
    if draft_invoices.exists():
        print(f"\n📝 Factures recommandées pour le test (status DRAFT):")
        for inv in draft_invoices:
            print(f"   - {inv.invoice_number} (ID: {inv.id}) - {inv.student.user.get_full_name()}")
    
    # Éléments à vérifier dans le navigateur
    print(f"\n🔍 Éléments à vérifier dans les outils de développement:")
    print(f"   - Console JavaScript: Pas d'erreurs")
    print(f"   - Réseau: Requête POST vers /finance/invoices/ après clic")
    print(f"   - Formulaire: Données envoyées incluent action, new_status, selected_invoices")
    
    # Messages d'debug attendus
    print(f"\n📋 Messages de debug attendus dans la console JS:")
    print(f"   - 'submitBulkAction appelée: bulk_status_change Sélectionnées: X'")
    print(f"   - 'Soumission du formulaire...'")
    
    print(f"\n📋 Messages de debug attendus dans les logs Django:")
    print(f"   - 'DEBUG: Début de la vue invoice_list'")
    print(f"   - 'DEBUG: Requête POST reçue'")
    print(f"   - 'DEBUG: Action: bulk_status_change'")
    print(f"   - 'SUCCESS: X factures mises à jour'")

def check_javascript_elements():
    """Vérifier que tous les éléments JavaScript sont présents dans le template"""
    template_path = '/home/jeshurun-nasser/dev/py/django-app/eschool/templates/finance/invoice_list.html'
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    js_elements = [
        'select-all',
        'bulk-update-btn',
        'status-select',
        'invoice-checkbox',
        'submitBulkAction',
        'bulk_status_change',
        'getCookie',
        'csrfmiddlewaretoken'
    ]
    
    print(f"\n🔧 Vérification des éléments JavaScript:")
    for element in js_elements:
        if element in content:
            print(f"   ✅ {element}")
        else:
            print(f"   ❌ {element} manquant")

if __name__ == '__main__':
    show_test_guide()
    check_javascript_elements()
    print(f"\n🚀 Serveur déjà en cours sur: http://localhost:8000")
    print(f"💡 Conseil: Ouvrir les outils de développement avant de tester")
