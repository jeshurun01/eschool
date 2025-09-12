#!/usr/bin/env python
"""
Script pour créer des données de test pour le module Finance - Paiements
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import Student
from academic.models import Level, AcademicYear
from finance.models import FeeType, Invoice, PaymentMethod, Payment

User = get_user_model()

def create_finance_test_data():
    print("🏦 Création des données de test pour Finance - Paiements...")
    
    # 1. Créer des méthodes de paiement si elles n'existent pas
    payment_methods = [
        {'name': 'Espèces', 'code': 'CASH', 'requires_reference': False},
        {'name': 'Chèque', 'code': 'CHECK', 'requires_reference': True},
        {'name': 'Virement bancaire', 'code': 'BANK_TRANSFER', 'requires_reference': True},
        {'name': 'Carte bancaire', 'code': 'CARD', 'requires_reference': False},
        {'name': 'Mobile Money', 'code': 'MOBILE_MONEY', 'requires_reference': False},
    ]
    
    created_methods = []
    for method_data in payment_methods:
        method, created = PaymentMethod.objects.get_or_create(
            code=method_data['code'],
            defaults=method_data
        )
        created_methods.append(method)
        if created:
            print(f"✅ Méthode de paiement créée: {method.name}")
    
    # 2. Créer des types de frais si ils n'existent pas
    fee_types_data = [
        {'name': 'Frais de scolarité', 'is_recurring': True, 'is_mandatory': True},
        {'name': 'Frais d\'inscription', 'is_recurring': False, 'is_mandatory': True},
        {'name': 'Frais de transport', 'is_recurring': True, 'is_mandatory': False},
        {'name': 'Frais de cantine', 'is_recurring': True, 'is_mandatory': False},
        {'name': 'Frais d\'examen', 'is_recurring': False, 'is_mandatory': True},
    ]
    
    created_fee_types = []
    for fee_data in fee_types_data:
        fee_type, created = FeeType.objects.get_or_create(
            name=fee_data['name'],
            defaults=fee_data
        )
        created_fee_types.append(fee_type)
        if created:
            print(f"✅ Type de frais créé: {fee_type.name}")
    
    # 3. Récupérer quelques étudiants existants
    students = Student.objects.all()[:10]
    if not students:
        print("❌ Aucun étudiant trouvé. Veuillez d'abord créer des étudiants.")
        return
    
    # 4. Récupérer l'année académique courante
    try:
        academic_year = AcademicYear.objects.filter(is_current=True).first()
        if not academic_year:
            academic_year = AcademicYear.objects.first()
    except:
        print("❌ Aucune année académique trouvée.")
        return
    
    # 5. Créer des factures et des paiements de test
    print("\n📄 Création des factures et paiements de test...")
    
    payment_count = 0
    for i, student in enumerate(students):
        try:
            # Créer 1-3 factures par étudiant
            for j in range(1, 4):
                # Créer une facture
                invoice = Invoice.objects.create(
                    invoice_number=f"INV-{academic_year.name if academic_year else '2025'}-{student.matricule}-{j:02d}",
                    student=student,
                    due_date=timezone.now().date() + timedelta(days=30),
                    subtotal=Decimal(str(50000 + (j * 25000))),  # 50k, 75k, 100k
                    total_amount=Decimal(str(50000 + (j * 25000))),
                    status='SENT' if j == 1 else 'PAID',
                    notes=f"Facture test - {student.user.get_full_name()}"
                )
                
                # Créer 1-2 paiements par facture (sauf pour la première qui reste impayée)
                if j > 1:  # Ne pas créer de paiement pour la première facture
                    num_payments = 1 if j == 2 else 2  # 1 paiement complet ou 2 paiements partiels
                    
                    for k in range(num_payments):
                        payment_amount = invoice.total_amount / num_payments
                        payment_status = 'COMPLETED' if k == 0 or j == 2 else ['PENDING', 'PROCESSING', 'COMPLETED'][k % 3]
                        
                        payment = Payment.objects.create(
                            payment_reference=f"PAY-{invoice.invoice_number}-{k+1:02d}",
                            invoice=invoice,
                            payment_method=created_methods[k % len(created_methods)],
                            amount=payment_amount,
                            transaction_id=f"TXN{timezone.now().strftime('%Y%m%d')}{payment_count:04d}",
                            payment_date=timezone.now() - timedelta(days=(j*10 + k*5)),
                            status=payment_status,
                            notes=f"Paiement {'partiel' if num_payments > 1 else 'complet'} - {payment_status}"
                        )
                        
                        if payment_status == 'COMPLETED':
                            payment.processed_date = payment.payment_date + timedelta(hours=2)
                            payment.save()
                        
                        payment_count += 1
                        print(f"✅ Paiement créé: {payment.payment_reference} - {payment.amount}€ ({payment.status})")
        
        except Exception as e:
            print(f"❌ Erreur lors de la création des données pour {student}: {e}")
            continue
    
    print(f"\n🎉 Données de test créées avec succès!")
    print(f"📊 Statistiques:")
    print(f"   - Méthodes de paiement: {PaymentMethod.objects.count()}")
    print(f"   - Types de frais: {FeeType.objects.count()}")
    print(f"   - Factures: {Invoice.objects.count()}")
    print(f"   - Paiements: {Payment.objects.count()}")
    print(f"   - Paiements terminés: {Payment.objects.filter(status='COMPLETED').count()}")
    print(f"   - Paiements en attente: {Payment.objects.filter(status='PENDING').count()}")

if __name__ == '__main__':
    create_finance_test_data()
