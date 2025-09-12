#!/usr/bin/env python3
"""
Script pour créer des factures de test avec différents statuts
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import Invoice, InvoiceItem, FeeType
from accounts.models import Student
from decimal import Decimal
from datetime import date, timedelta
import random

def create_test_invoices():
    """Créer des factures de test avec différents statuts"""
    
    print("=== Création de factures de test ===\n")
    
    # Obtenir des étudiants et types de frais
    students = list(Student.objects.all()[:10])  # Les 10 premiers étudiants
    fee_types = list(FeeType.objects.all()[:3])  # Les 3 premiers types de frais
    
    if not students:
        print("❌ Aucun étudiant trouvé. Veuillez d'abord créer des étudiants.")
        return
    
    if not fee_types:
        print("❌ Aucun type de frais trouvé. Veuillez d'abord créer des types de frais.")
        return
    
    print(f"📚 {len(students)} étudiants trouvés")
    print(f"💰 {len(fee_types)} types de frais trouvés")
    
    # Statuts à tester
    statuses = [
        ('DRAFT', 'Brouillon'),
        ('SENT', 'Envoyée'),
        ('PAID', 'Payée'),
        ('OVERDUE', 'En retard'),
        ('CANCELLED', 'Annulée')
    ]
    
    created_invoices = []
    
    # Créer 15 factures avec différents statuts
    for i in range(15):
        try:
            student = random.choice(students)
            status, status_label = random.choice(statuses)
            
            # Créer la facture
            invoice = Invoice.objects.create(
                student=student,
                issue_date=date.today() - timedelta(days=random.randint(0, 30)),
                due_date=date.today() + timedelta(days=random.randint(7, 60)),
                status=status,
                notes=f"Facture de test #{i+1} - Statut: {status_label}",
                subtotal=Decimal('0.00'),
                discount=Decimal('0.00'),
                total_amount=Decimal('0.00')
            )
            
            # Ajouter 1-3 éléments de facture
            num_items = random.randint(1, min(3, len(fee_types)))
            selected_fee_types = random.sample(fee_types, num_items)
            
            total_amount = Decimal('0.00')
            
            for fee_type in selected_fee_types:
                quantity = Decimal(str(random.randint(1, 2)))
                unit_price = Decimal(str(random.randint(10000, 50000)))
                
                item = InvoiceItem.objects.create(
                    invoice=invoice,
                    fee_type=fee_type,
                    description=f"{fee_type.name} - {student.user.get_full_name()}",
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                total_amount += item.total
            
            # Mettre à jour les totaux de la facture
            invoice.subtotal = total_amount
            invoice.total_amount = total_amount
            invoice.save()
            
            created_invoices.append(invoice)
            
            print(f"✅ Facture créée: {invoice.invoice_number} - {student.user.get_full_name()} - {status_label} ({invoice.total_amount} FCFA)")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la facture {i+1}: {e}")
    
    print(f"\n🎉 {len(created_invoices)} factures de test créées avec succès!")
    
    # Statistiques par statut
    print("\n📊 Répartition par statut:")
    for status_code, status_label in statuses:
        count = len([inv for inv in created_invoices if inv.status == status_code])
        if count > 0:
            print(f"  {status_label}: {count} facture(s)")
    
    print("\n💡 Vous pouvez maintenant tester le système de modification en lot sur:")
    print("   http://localhost:8000/finance/invoices/")
    print("\n🔧 Scénarios à tester:")
    print("   1. Sélectionner plusieurs factures 'Brouillon' → les passer à 'Envoyée'")
    print("   2. Sélectionner des factures 'En retard' → les passer à 'Payée'")
    print("   3. Utiliser 'Tout sélectionner' pour une action globale")

if __name__ == "__main__":
    create_test_invoices()
