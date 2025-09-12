#!/usr/bin/env python
"""
Script pour créer des données de test pour le module finance
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Student, Parent
from finance.models import Invoice, InvoiceItem, FeeType, PaymentMethod, Payment
from academic.models import AcademicYear, Level

def create_finance_test_data():
    """Créer des données de test pour le module finance"""
    
    print("🏗️  Création des données de test pour le module finance...")
    
    # Vérifier s'il y a déjà des factures
    existing_invoices = Invoice.objects.count()
    if existing_invoices > 0:
        print(f"⚠️  {existing_invoices} factures existent déjà. Nettoyage en cours...")
        Invoice.objects.all().delete()
        Payment.objects.all().delete()
        print("✅ Nettoyage terminé")
    
    # Récupérer l'année scolaire actuelle
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        print("❌ Aucune année scolaire actuelle trouvée")
        return
    
    # Créer des types de frais s'ils n'existent pas
    fee_types_data = [
        {'name': 'Frais de scolarité', 'description': 'Frais de scolarité mensuelle', 'is_recurring': True, 'is_mandatory': True},
        {'name': 'Frais d\'inscription', 'description': 'Frais d\'inscription annuelle', 'is_recurring': False, 'is_mandatory': True},
        {'name': 'Frais de cantine', 'description': 'Frais de restauration scolaire', 'is_recurring': True, 'is_mandatory': False},
        {'name': 'Frais de transport', 'description': 'Frais de transport scolaire', 'is_recurring': True, 'is_mandatory': False},
        {'name': 'Matériel scolaire', 'description': 'Fournitures et manuels scolaires', 'is_recurring': False, 'is_mandatory': True},
    ]
    
    fee_types = []
    for data in fee_types_data:
        fee_type, created = FeeType.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        fee_types.append(fee_type)
        if created:
            print(f"✅ Type de frais créé: {fee_type.name}")
    
    # Créer des méthodes de paiement s'elles n'existent pas
    payment_methods_data = [
        {'name': 'Virement bancaire', 'code': 'TRANSFER', 'description': 'Paiement par virement bancaire', 'is_active': True},
        {'name': 'Chèque', 'code': 'CHECK', 'description': 'Paiement par chèque', 'is_active': True},
        {'name': 'Espèces', 'code': 'CASH', 'description': 'Paiement en espèces', 'is_active': True},
        {'name': 'Carte bancaire', 'code': 'CARD', 'description': 'Paiement par carte bancaire', 'is_active': True},
    ]
    
    payment_methods = []
    for data in payment_methods_data:
        method, created = PaymentMethod.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        payment_methods.append(method)
        if created:
            print(f"✅ Méthode de paiement créée: {method.name}")
    
    # Récupérer quelques étudiants
    students = Student.objects.select_related('user').all()[:10]
    if not students:
        print("❌ Aucun étudiant trouvé dans la base de données")
        return
    
    print(f"📚 {len(students)} étudiants trouvés")
    
    # Créer des factures pour chaque étudiant
    invoice_counter = 1
    for i, student in enumerate(students):
        # Créer 2-4 factures par étudiant
        num_invoices = min(3, i % 4 + 1)
        
        for j in range(num_invoices):
            # Générer un numéro de facture unique
            invoice_number = f"FAC-{current_year.start_date.year}-{invoice_counter:04d}"
            
            # Calculer les dates
            issue_date = date.today() - timedelta(days=30*j + i*5)
            due_date = issue_date + timedelta(days=30)
            
            # Déterminer le statut
            if j == 0:  # Première facture
                status = 'PAID'
            elif j == 1:  # Deuxième facture
                status = 'SENT' if due_date > date.today() else 'OVERDUE'
            else:  # Autres factures
                status = 'DRAFT'
            
            # Créer la facture
            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                student=student,
                parent=student.parents.first() if student.parents.exists() else None,
                issue_date=issue_date,
                due_date=due_date,
                status=status,
                notes=f"Facture {j+1} pour {student.user.get_full_name()}"
            )
            
            # Ajouter des items à la facture
            total_amount = Decimal('0.00')
            
            # Frais de scolarité (toujours présent)
            scolarite_amount = Decimal('250.00') + Decimal(str(i * 10))  # Variation par étudiant
            InvoiceItem.objects.create(
                invoice=invoice,
                fee_type=fee_types[0],  # Frais de scolarité
                description=f"Frais de scolarité - {issue_date.strftime('%B %Y')}",
                quantity=1,
                unit_price=scolarite_amount,
            )
            total_amount += scolarite_amount
            
            # Ajouter d'autres frais aléatoirement
            if j == 0:  # Première facture: inscription
                inscription_amount = Decimal('150.00')
                InvoiceItem.objects.create(
                    invoice=invoice,
                    fee_type=fee_types[1],  # Frais d'inscription
                    description="Frais d'inscription annuelle",
                    quantity=1,
                    unit_price=inscription_amount,
                )
                total_amount += inscription_amount
            
            if i % 3 == 0:  # Certains étudiants ont la cantine
                cantine_amount = Decimal('80.00')
                InvoiceItem.objects.create(
                    invoice=invoice,
                    fee_type=fee_types[2],  # Frais de cantine
                    description=f"Frais de cantine - {issue_date.strftime('%B %Y')}",
                    quantity=1,
                    unit_price=cantine_amount,
                )
                total_amount += cantine_amount
            
            if i % 4 == 0:  # Certains étudiants ont le transport
                transport_amount = Decimal('45.00')
                InvoiceItem.objects.create(
                    invoice=invoice,
                    fee_type=fee_types[3],  # Frais de transport
                    description=f"Frais de transport - {issue_date.strftime('%B %Y')}",
                    quantity=1,
                    unit_price=transport_amount,
                )
                total_amount += transport_amount
            
            # Mettre à jour le total de la facture
            invoice.subtotal = total_amount
            invoice.total_amount = total_amount
            invoice.save()
            
            # Créer un paiement si la facture est payée
            if status == 'PAID':
                Payment.objects.create(
                    invoice=invoice,
                    payment_method=payment_methods[i % len(payment_methods)],
                    amount=total_amount,
                    payment_date=issue_date + timedelta(days=5),
                    status='COMPLETED',
                    notes=f"Paiement de la facture {invoice_number}"
                )
            
            print(f"✅ Facture créée: {invoice_number} - {student.user.get_full_name()} - {total_amount}€ ({status})")
            invoice_counter += 1
    
    print(f"\n🎉 {Invoice.objects.count()} factures créées au total")
    print(f"💰 {Payment.objects.count()} paiements créés au total")
    
    # Afficher un résumé des statistiques
    from django.db.models import Sum, Count
    stats = Invoice.objects.aggregate(
        total_amount=Sum('total_amount'),
        total_count=Count('id')
    )
    
    status_stats = {}
    for status_code, status_label in Invoice.STATUS_CHOICES:
        count = Invoice.objects.filter(status=status_code).count()
        status_stats[status_label] = count
    
    print(f"\n📊 Statistiques générées:")
    print(f"   💵 Montant total: {stats['total_amount']}€")
    print(f"   📄 Nombre total de factures: {stats['total_count']}")
    for status_label, count in status_stats.items():
        if count > 0:
            print(f"   📋 {status_label}: {count}")

if __name__ == "__main__":
    create_finance_test_data()

# Exécuter la fonction quand le script est importé via exec()
create_finance_test_data()
