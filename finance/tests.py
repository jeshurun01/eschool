from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from accounts.models import Teacher, Student, Parent
from academic.models import AcademicYear, Grade, ClassRoom
from .models import FeeType, FeeStructure, Invoice, Payment

User = get_user_model()


class FinanceModelsTest(TestCase):
    """Tests pour les modèles du module finance"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Année académique
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        # Niveau
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
            
        )
        
        # Classe
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            
        )
        
        # Utilisateurs
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Alexandre",
            last_name="Girard",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Brigitte",
            last_name="Andre",
            role="PARENT"
        )
        
        # Profils
        self.student = Student.objects.create(
            user=self.student_user,
            matricule="STU20250001"
        )
        
        self.parent = Parent.objects.create(
            user=self.parent_user,
            profession="Ingénieur"
        )
        
        # Associer parent et enfant
        self.student.parents.add(self.parent)

    def test_fee_type_model(self):
        """Test du modèle FeeType"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            description="Frais annuels de scolarité",
            is_mandatory=True
        )
        
        self.assertEqual(str(fee_type), "Frais de scolarité")
        self.assertTrue(fee_type.is_mandatory)
        self.assertTrue(fee_type.is_active)

    def test_fee_structure_model(self):
        """Test du modèle FeeStructure"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        self.assertEqual(fee_structure.fee_type, fee_type)
        self.assertEqual(fee_structure.amount, Decimal('500.00'))
        self.assertEqual(str(fee_structure), f"Frais de scolarité - 6ème - 2024-2025")

    def test_invoice_model(self):
        """Test du modèle Invoice"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15),
            status="PENDING"
        )
        
        self.assertEqual(invoice.student, self.student)
        self.assertEqual(invoice.total_amount, Decimal('500.00'))
        self.assertEqual(invoice.status, "PENDING")
        self.assertIsNotNone(invoice.invoice_number)

    def test_invoice_auto_number_generation(self):
        """Test de génération automatique du numéro de facture"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice1 = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice2 = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=300.00,
            due_date=date(2025, 2, 15)
        )
        
        # Les numéros devraient être différents
        self.assertNotEqual(invoice1.invoice_number, invoice2.invoice_number)
        self.assertTrue(invoice1.invoice_number.startswith("INV2025"))
        self.assertTrue(invoice2.invoice_number.startswith("INV2025"))

    def test_payment_model(self):
        """Test du modèle Payment"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        payment = Payment.objects.create(
            invoice=invoice,
            amount=250.00,
            payment_method="BANK_TRANSFER",
            payment_date=date.today(),
            reference_number="PAY123456"
        )
        
        self.assertEqual(payment.invoice, invoice)
        self.assertEqual(payment.amount, Decimal('250.00'))
        self.assertEqual(payment.payment_method, "BANK_TRANSFER")
        self.assertEqual(str(payment), f"Paiement {payment.reference_number} - 250.00€")

    def test_payment_auto_reference_generation(self):
        """Test de génération automatique de la référence de paiement"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        payment = Payment.objects.create(
            invoice=invoice,
            amount=250.00,
            payment_method="CASH",
            payment_date=date.today()
        )
        
        # La référence devrait être générée automatiquement
        self.assertIsNotNone(payment.reference_number)
        self.assertTrue(payment.reference_number.startswith("PAY2025"))

    def test_invoice_balance_calculation(self):
        """Test du calcul du solde de facture"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        # Initialement, le solde devrait être égal au montant total
        self.assertEqual(invoice.balance, Decimal('500.00'))
        
        # Ajouter un paiement partiel
        Payment.objects.create(
            invoice=invoice,
            amount=200.00,
            payment_method="CASH",
            payment_date=date.today()
        )
        
        # Le solde devrait être mis à jour
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('300.00'))
        
        # Ajouter un autre paiement
        Payment.objects.create(
            invoice=invoice,
            amount=300.00,
            payment_method="BANK_TRANSFER",
            payment_date=date.today()
        )
        
        # Le solde devrait être zéro
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('0.00'))
        self.assertEqual(invoice.status, "PAID")

    def test_invoice_overdue_status(self):
        """Test du statut en retard de facture"""
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date.today() - timedelta(days=10)  # Échéance passée
        )
        
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date.today() - timedelta(days=10),
            status="PENDING"
        )
        
        # La facture devrait être considérée comme en retard
        self.assertTrue(invoice.is_overdue)


class FinanceViewsTest(TestCase):
    """Tests pour les vues du module finance"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Données de base
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
            
        )
        
        self.classroom = ClassRoom.objects.create(
            name="6ème A",
            level=self.level,
            
        )
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True,
            is_superuser=True
        )
        
        self.finance_user = User.objects.create_user(
            email="finance@test.com",
            password="testpass123",
            first_name="Finance",
            last_name="User",
            role="FINANCE",
            is_staff=True
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )
        
        # Profils
        self.student = Student.objects.create(
            user=self.student_user,
            matricule="STU20250001"
        )
        
        self.parent = Parent.objects.create(
            user=self.parent_user,
            profession="Ingénieur"
        )
        
        # Type de frais
        self.fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        # Structure de frais
        self.fee_structure = FeeStructure.objects.create(
            fee_type=self.fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )

    def test_fee_type_list_view_admin(self):
        """Test de la vue liste des types de frais pour admin"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('finance:fee_type_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frais de scolarité")

    def test_fee_type_list_view_finance(self):
        """Test de la vue liste des types de frais pour personnel finance"""
        self.client.force_login(self.finance_user)
        response = self.client.get(reverse('finance:fee_type_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frais de scolarité")

    def test_fee_structure_create_view_get(self):
        """Test de la vue création de structure de frais (GET)"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('finance:fee_structure_create'))
        
        self.assertEqual(response.status_code, 200)

    def test_fee_structure_create_view_post(self):
        """Test de la vue création de structure de frais (POST)"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('finance:fee_structure_create'), {
            'fee_type': self.fee_type.pk,
            'grade': self.grade.pk,
            'academic_year': self.academic_year.pk,
            'amount': '750.00',
            'due_date': '2025-02-15',
            'description': 'Nouveaux frais'
        })
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérifier la création
        new_structure = FeeStructure.objects.filter(amount=Decimal('750.00')).first()
        self.assertIsNotNone(new_structure)
        self.assertEqual(new_structure.fee_type, self.fee_type)

    def test_invoice_list_view_admin(self):
        """Test de la vue liste des factures pour admin"""
        # Créer une facture
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('finance:invoice_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)

    def test_invoice_detail_view(self):
        """Test de la vue détail de facture"""
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('finance:invoice_detail', kwargs={'pk': invoice.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)
        self.assertContains(response, "500.00")

    def test_invoice_generate_view_get(self):
        """Test de la vue génération de factures (GET)"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('finance:invoice_generate'))
        
        self.assertEqual(response.status_code, 200)

    def test_invoice_generate_view_post(self):
        """Test de la vue génération de factures (POST)"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('finance:invoice_generate'), {
            'fee_structure': self.fee_structure.pk,
            'students': [self.student.pk]
        })
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérifier la création de la facture
        invoice = Invoice.objects.filter(
            student=self.student,
            fee_structure=self.fee_structure
        ).first()
        
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.total_amount, Decimal('500.00'))

    def test_payment_create_view_get(self):
        """Test de la vue création de paiement (GET)"""
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('finance:payment_create', kwargs={'invoice_pk': invoice.pk})
        )
        
        self.assertEqual(response.status_code, 200)

    def test_payment_create_view_post(self):
        """Test de la vue création de paiement (POST)"""
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse('finance:payment_create', kwargs={'invoice_pk': invoice.pk}),
            {
                'amount': '250.00',
                'payment_method': 'CASH',
                'payment_date': date.today().strftime('%Y-%m-%d'),
                'notes': 'Paiement partiel'
            }
        )
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérifier la création du paiement
        payment = Payment.objects.filter(invoice=invoice).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, Decimal('250.00'))
        
        # Vérifier la mise à jour du solde
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('250.00'))

    def test_bulk_invoice_actions_view(self):
        """Test de la vue actions en lot sur factures"""
        # Créer plusieurs factures
        invoices = []
        for i in range(3):
            invoice = Invoice.objects.create(
                student=self.student,
                fee_structure=self.fee_structure,
                total_amount=500.00,
                due_date=date(2025, 1, 15)
            )
            invoices.append(invoice)
        
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('finance:bulk_invoice_actions'), {
            'action': 'mark_overdue',
            'invoice_ids': [invoice.pk for invoice in invoices]
        })
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que les factures ont été mises à jour
        for invoice in invoices:
            invoice.refresh_from_db()
            self.assertEqual(invoice.status, 'OVERDUE')

    def test_unauthorized_access_student(self):
        """Test d'accès non autorisé pour un étudiant"""
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('finance:fee_type_list'))
        
        # L'étudiant ne devrait pas voir la liste des types de frais
        self.assertEqual(response.status_code, 403)

    def test_parent_invoice_view(self):
        """Test de vue des factures pour un parent"""
        # Associer l'enfant au parent
        self.student.parents.add(self.parent)
        
        # Créer une facture pour l'enfant
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        self.client.force_login(self.parent_user)
        response = self.client.get(reverse('finance:parent_invoices'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)


class FinanceCalculationsTest(TestCase):
    """Tests pour les calculs financiers"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
            
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            matricule="STU20250001"
        )
        
        self.fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        self.fee_structure = FeeStructure.objects.create(
            fee_type=self.fee_type,
            level=self.level,
            ,
            amount=1000.00,
            due_date=date(2025, 1, 15)
        )

    def test_invoice_balance_with_multiple_payments(self):
        """Test du calcul de solde avec plusieurs paiements"""
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=1000.00,
            due_date=date(2025, 1, 15)
        )
        
        # Paiement 1: 300€
        Payment.objects.create(
            invoice=invoice,
            amount=300.00,
            payment_method="CASH",
            payment_date=date.today()
        )
        
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('700.00'))
        
        # Paiement 2: 200€
        Payment.objects.create(
            invoice=invoice,
            amount=200.00,
            payment_method="BANK_TRANSFER",
            payment_date=date.today()
        )
        
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('500.00'))
        
        # Paiement final: 500€
        Payment.objects.create(
            invoice=invoice,
            amount=500.00,
            payment_method="CHEQUE",
            payment_date=date.today()
        )
        
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('0.00'))
        self.assertEqual(invoice.status, "PAID")

    def test_overpayment_handling(self):
        """Test de gestion des trop-perçus"""
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        # Paiement supérieur au montant dû
        Payment.objects.create(
            invoice=invoice,
            amount=600.00,
            payment_method="BANK_TRANSFER",
            payment_date=date.today()
        )
        
        invoice.refresh_from_db()
        
        # Le solde devrait être négatif (crédit)
        self.assertEqual(invoice.balance, Decimal('-100.00'))
        self.assertEqual(invoice.status, "OVERPAID")

    def test_financial_statistics(self):
        """Test des statistiques financières"""
        # Créer plusieurs factures avec différents statuts
        invoices = []
        
        # Facture payée
        invoice1 = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15),
            status="PAID"
        )
        Payment.objects.create(
            invoice=invoice1,
            amount=500.00,
            payment_method="CASH",
            payment_date=date.today()
        )
        
        # Facture en attente
        invoice2 = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=300.00,
            due_date=date(2025, 2, 15),
            status="PENDING"
        )
        
        # Facture en retard
        invoice3 = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=200.00,
            due_date=date.today() - timedelta(days=30),
            status="OVERDUE"
        )
        
        # Calculer les statistiques
        total_invoiced = Invoice.objects.aggregate(
            total=models.Sum('total_amount')
        )['total']
        
        total_paid = Payment.objects.aggregate(
            total=models.Sum('amount')
        )['total']
        
        total_pending = Invoice.objects.filter(
            status='PENDING'
        ).aggregate(
            total=models.Sum('total_amount')
        )['total']
        
        self.assertEqual(total_invoiced, Decimal('1000.00'))
        self.assertEqual(total_paid, Decimal('500.00'))
        self.assertEqual(total_pending, Decimal('300.00'))

    def test_discount_application(self):
        """Test d'application de remises"""
        # Créer une facture avec remise
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            total_amount=500.00,
            discount_amount=50.00,  # 10% de remise
            due_date=date(2025, 1, 15)
        )
        
        # Le montant final devrait tenir compte de la remise
        final_amount = invoice.total_amount - invoice.discount_amount
        self.assertEqual(final_amount, Decimal('450.00'))
        
        # Paiement du montant avec remise
        Payment.objects.create(
            invoice=invoice,
            amount=450.00,
            payment_method="BANK_TRANSFER",
            payment_date=date.today()
        )
        
        invoice.refresh_from_db()
        # Le solde devrait être calculé avec la remise
        expected_balance = (invoice.total_amount - invoice.discount_amount) - Decimal('450.00')
        self.assertEqual(invoice.balance, expected_balance)


class FinanceIntegrationTest(TestCase):
    """Tests d'intégration pour le module finance"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Configuration complète
        self.academic_year = AcademicYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            is_current=True
        )
        
        self.level = Level.objects.create(
            name="6ème",
            description="Classe de 6ème",
            order=6
            
        )
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_staff=True,
            is_superuser=True
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            role="STUDENT"
        )
        
        self.parent_user = User.objects.create_user(
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
            role="PARENT"
        )
        
        # Profils
        self.student = Student.objects.create(
            user=self.student_user,
            matricule="STU20250001"
        )
        
        self.parent = Parent.objects.create(
            user=self.parent_user,
            profession="Ingénieur"
        )
        
        # Associer parent et enfant
        self.student.parents.add(self.parent)

    def test_complete_billing_workflow(self):
        """Test du workflow complet de facturation"""
        self.client.force_login(self.admin_user)
        
        # 1. Créer un type de frais
        response = self.client.post(reverse('finance:fee_type_create'), {
            'name': 'Frais de cantine',
            'description': 'Frais mensuels de cantine',
            'is_mandatory': True
        })
        self.assertEqual(response.status_code, 302)
        
        fee_type = FeeType.objects.filter(name='Frais de cantine').first()
        self.assertIsNotNone(fee_type)
        
        # 2. Créer une structure de frais
        response = self.client.post(reverse('finance:fee_structure_create'), {
            'fee_type': fee_type.pk,
            'grade': self.grade.pk,
            'academic_year': self.academic_year.pk,
            'amount': '100.00',
            'due_date': '2025-01-31'
        })
        self.assertEqual(response.status_code, 302)
        
        fee_structure = FeeStructure.objects.filter(fee_type=fee_type).first()
        self.assertIsNotNone(fee_structure)
        
        # 3. Générer une facture
        response = self.client.post(reverse('finance:invoice_generate'), {
            'fee_structure': fee_structure.pk,
            'students': [self.student.pk]
        })
        self.assertEqual(response.status_code, 302)
        
        invoice = Invoice.objects.filter(
            student=self.student,
            fee_structure=fee_structure
        ).first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.total_amount, Decimal('100.00'))
        
        # 4. Enregistrer un paiement
        response = self.client.post(
            reverse('finance:payment_create', kwargs={'invoice_pk': invoice.pk}),
            {
                'amount': '100.00',
                'payment_method': 'BANK_TRANSFER',
                'payment_date': date.today().strftime('%Y-%m-%d'),
                'notes': 'Paiement complet'
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # 5. Vérifier que tout est cohérent
        payment = Payment.objects.filter(invoice=invoice).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, Decimal('100.00'))
        
        invoice.refresh_from_db()
        self.assertEqual(invoice.balance, Decimal('0.00'))
        self.assertEqual(invoice.status, 'PAID')

    def test_parent_payment_workflow(self):
        """Test du workflow de paiement pour un parent"""
        # Créer une facture pour l'enfant
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        invoice = Invoice.objects.create(
            student=self.student,
            fee_structure=fee_structure,
            total_amount=500.00,
            due_date=date(2025, 1, 15)
        )
        
        # Le parent se connecte et voit la facture
        self.client.force_login(self.parent_user)
        response = self.client.get(reverse('finance:parent_invoices'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)
        
        # Le parent peut voir les détails
        response = self.client.get(
            reverse('finance:parent_invoice_detail', kwargs={'pk': invoice.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "500.00")

    def test_bulk_operations_workflow(self):
        """Test du workflow d'opérations en lot"""
        self.client.force_login(self.admin_user)
        
        # Créer plusieurs factures
        fee_type = FeeType.objects.create(
            name="Frais de scolarité",
            is_mandatory=True
        )
        
        fee_structure = FeeStructure.objects.create(
            fee_type=fee_type,
            level=self.level,
            ,
            amount=500.00,
            due_date=date.today() - timedelta(days=30)  # Échéance passée
        )
        
        invoices = []
        for i in range(5):
            invoice = Invoice.objects.create(
                student=self.student,
                fee_structure=fee_structure,
                total_amount=500.00,
                due_date=date.today() - timedelta(days=30),
                status="PENDING"
            )
            invoices.append(invoice)
        
        # Marquer toutes les factures comme en retard
        response = self.client.post(reverse('finance:bulk_invoice_actions'), {
            'action': 'mark_overdue',
            'invoice_ids': [invoice.pk for invoice in invoices]
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que toutes les factures sont marquées comme en retard
        for invoice in invoices:
            invoice.refresh_from_db()
            self.assertEqual(invoice.status, 'OVERDUE')
