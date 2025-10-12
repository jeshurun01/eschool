from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

# Import des managers RBAC
from .managers import PaymentManager, InvoiceManager

User = get_user_model()

# Helper functions for default values
def get_current_date():
    """Retourne la date actuelle (sans heure)"""
    return timezone.now().date()

def get_current_datetime():
    """Retourne la date et heure actuelles avec timezone"""
    return timezone.now()


class FeeType(models.Model):
    """Type de frais (Scolarité, Inscription, Transport, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nom du type de frais')
    description = models.TextField(blank=True, verbose_name='Description')
    is_recurring = models.BooleanField(default=False, verbose_name='Frais récurrent')
    is_mandatory = models.BooleanField(default=True, verbose_name='Frais obligatoire')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Type de frais'
        verbose_name_plural = 'Types de frais'
        ordering = ['name']

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """Structure des frais par niveau et année scolaire"""
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, related_name='structures', verbose_name='Type de frais')
    level = models.ForeignKey('academic.Level', on_delete=models.CASCADE, related_name='fee_structures', verbose_name='Niveau')
    academic_year = models.ForeignKey('academic.AcademicYear', on_delete=models.CASCADE, related_name='fee_structures', verbose_name='Année scolaire')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Montant')
    due_date = models.DateField(blank=True, null=True, verbose_name='Date d\'échéance')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Structure de frais'
        verbose_name_plural = 'Structures de frais'
        unique_together = ['fee_type', 'level', 'academic_year']

    def __str__(self):
        return f"{self.fee_type.name} - {self.level.name} ({self.academic_year.name}): {self.amount}"


class Invoice(models.Model):
    """Facture"""
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('SENT', 'Envoyée'),
        ('PAID', 'Payée'),
        ('OVERDUE', 'En retard'),
        ('CANCELLED', 'Annulée'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True, verbose_name='Numéro de facture')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='invoices', verbose_name='Élève')
    parent = models.ForeignKey('accounts.Parent', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name='Parent responsable')
    
    issue_date = models.DateField(default=get_current_date, verbose_name='Date d\'émission')
    due_date = models.DateField(verbose_name='Date d\'échéance')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Sous-total')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Remise')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Montant total')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager RBAC
    objects = InvoiceManager()

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-issue_date']

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.student.user.full_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Générer un numéro de facture automatiquement
            current_year = timezone.now().year
            current_month = timezone.now().month
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"INV{current_year}{current_month:02d}"
            ).order_by('invoice_number').last()
            
            if last_invoice:
                last_number = int(last_invoice.invoice_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.invoice_number = f"INV{current_year}{current_month:02d}{new_number:04d}"
        
        super().save(*args, **kwargs)

    @property
    def paid_amount(self):
        """Montant payé"""
        return sum(payment.amount for payment in self.payments.filter(status='COMPLETED'))

    @property
    def balance(self):
        """Solde restant"""
        return self.total_amount - self.paid_amount

    @property
    def is_paid(self):
        """Vérifie si la facture est entièrement payée"""
        return self.balance <= Decimal('0.00')

    def update_total(self):
        """Met à jour le total de la facture"""
        self.subtotal = sum(item.total for item in self.items.all())
        self.total_amount = self.subtotal - self.discount
        self.save()


class InvoiceItem(models.Model):
    """Ligne de facture"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name='Facture')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, verbose_name='Type de frais')
    description = models.CharField(max_length=200, verbose_name='Description')
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'), verbose_name='Quantité')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Prix unitaire')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ligne de facture'
        verbose_name_plural = 'Lignes de facture'

    def __str__(self):
        return f"{self.description} - {self.total}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """Méthode de paiement"""
    name = models.CharField(max_length=50, verbose_name='Nom')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    description = models.TextField(blank=True, verbose_name='Description')
    
    # Configuration pour les passerelles de paiement
    requires_reference = models.BooleanField(default=False, verbose_name='Nécessite une référence')
    webhook_url = models.URLField(blank=True, verbose_name='URL de webhook')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Méthode de paiement'
        verbose_name_plural = 'Méthodes de paiement'

    def __str__(self):
        return self.name


class Payment(models.Model):
    """Paiement"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('FAILED', 'Échoué'),
        ('CANCELLED', 'Annulé'),
        ('REFUNDED', 'Remboursé'),
    ]

    payment_reference = models.CharField(max_length=50, unique=True, verbose_name='Référence de paiement')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name='Facture')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='Méthode de paiement')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Montant')
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name='ID de transaction')
    
    payment_date = models.DateTimeField(default=get_current_datetime, verbose_name='Date de paiement')
    processed_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de traitement')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    # Informations de la passerelle de paiement
    gateway_response = models.JSONField(blank=True, null=True, verbose_name='Réponse de la passerelle')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager RBAC
    objects = PaymentManager()

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Paiement {self.payment_reference} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            # Générer une référence de paiement automatiquement
            current_year = timezone.now().year
            current_month = timezone.now().month
            last_payment = Payment.objects.filter(
                payment_reference__startswith=f"PAY{current_year}{current_month:02d}"
            ).order_by('payment_reference').last()
            
            if last_payment:
                last_number = int(last_payment.payment_reference[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.payment_reference = f"PAY{current_year}{current_month:02d}{new_number:04d}"
        
        super().save(*args, **kwargs)


class Scholarship(models.Model):
    """Bourse d'études"""
    TYPE_CHOICES = [
        ('PERCENTAGE', 'Pourcentage'),
        ('FIXED_AMOUNT', 'Montant fixe'),
        ('FULL', 'Gratuit total'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nom de la bourse')
    description = models.TextField(blank=True, verbose_name='Description')
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name='Type de bourse')
    
    # Valeur de la bourse
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, 
                                   validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Pourcentage')
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                     validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Montant fixe')
    
    # Critères d'éligibilité
    academic_year = models.ForeignKey('academic.AcademicYear', on_delete=models.CASCADE, verbose_name='Année scolaire')
    eligible_levels = models.ManyToManyField('academic.Level', verbose_name='Niveaux éligibles')
    
    is_active = models.BooleanField(default=True, verbose_name='Active')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bourse'
        verbose_name_plural = 'Bourses'

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class ScholarshipApplication(models.Model):
    """Demande de bourse"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvée'),
        ('REJECTED', 'Rejetée'),
        ('SUSPENDED', 'Suspendue'),
    ]

    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications', verbose_name='Bourse')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='scholarship_applications', verbose_name='Élève')
    
    application_date = models.DateField(default=get_current_date, verbose_name='Date de demande')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Statut')
    
    # Justification
    justification = models.TextField(verbose_name='Justification')
    supporting_documents = models.FileField(upload_to='scholarships/', blank=True, null=True, verbose_name='Documents justificatifs')
    
    # Décision
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_scholarships', verbose_name='Approuvé par')
    decision_date = models.DateField(blank=True, null=True, verbose_name='Date de décision')
    decision_notes = models.TextField(blank=True, verbose_name='Notes de décision')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Demande de bourse'
        verbose_name_plural = 'Demandes de bourse'
        unique_together = ['scholarship', 'student']

    def __str__(self):
        return f"{self.student.user.full_name} - {self.scholarship.name}"


class Expense(models.Model):
    """Dépense de l'école"""
    CATEGORY_CHOICES = [
        ('SALARIES', 'Salaires'),
        ('UTILITIES', 'Services publics'),
        ('SUPPLIES', 'Fournitures'),
        ('MAINTENANCE', 'Maintenance'),
        ('EQUIPMENT', 'Équipement'),
        ('TRANSPORTATION', 'Transport'),
        ('FOOD', 'Alimentation'),
        ('OTHER', 'Autre'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Catégorie')
    description = models.CharField(max_length=200, verbose_name='Description')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Montant')
    
    expense_date = models.DateField(default=get_current_date, verbose_name='Date de dépense')
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_expenses', verbose_name='Enregistré par')
    
    # Documents justificatifs
    receipt = models.FileField(upload_to='expenses/', blank=True, null=True, verbose_name='Reçu/Facture')
    
    # Approbation
    is_approved = models.BooleanField(default=False, verbose_name='Approuvé')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses', verbose_name='Approuvé par')
    approval_date = models.DateField(blank=True, null=True, verbose_name='Date d\'approbation')
    
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.description} - {self.amount} ({self.expense_date})"


class Payroll(models.Model):
    """Paie du personnel"""
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('CALCULATED', 'Calculée'),
        ('APPROVED', 'Approuvée'),
        ('PAID', 'Payée'),
    ]

    employee = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, related_name='payrolls', verbose_name='Employé')
    period_start = models.DateField(verbose_name='Début de période')
    period_end = models.DateField(verbose_name='Fin de période')
    
    # Salaire de base et avantages
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salaire de base')
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Indemnités')
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Heures supplémentaires')
    
    # Déductions
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Impôts')
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Sécurité sociale')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Autres déductions')
    
    # Totaux
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salaire brut')
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salaire net')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT', verbose_name='Statut')
    
    # Approbation et paiement
    calculated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calculated_payrolls', verbose_name='Calculé par')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payrolls', verbose_name='Approuvé par')
    paid_date = models.DateField(blank=True, null=True, verbose_name='Date de paiement')
    
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paie'
        verbose_name_plural = 'Paies'
        unique_together = ['employee', 'period_start', 'period_end']
        ordering = ['-period_start']

    def __str__(self):
        return f"Paie {self.employee.user.full_name} - {self.period_start} à {self.period_end}"

    def calculate_totals(self):
        """Calcule les totaux brut et net"""
        self.gross_salary = self.base_salary + self.allowances + self.overtime_amount
        total_deductions = self.tax_deduction + self.social_security + self.other_deductions
        self.net_salary = self.gross_salary - total_deductions


class DailyFinancialReport(models.Model):
    """
    Rapport financier journalier automatisé
    
    Stocke les statistiques financières quotidiennes pour :
    - Suivi des paiements reçus
    - État des factures
    - Encaissements par méthode de paiement
    - Comparaisons historiques
    - KPIs financiers
    """
    
    # Date du rapport
    report_date = models.DateField(unique=True, verbose_name='Date du rapport', db_index=True)
    
    # === PAIEMENTS REÇUS ===
    payments_count = models.IntegerField(default=0, verbose_name='Nombre de paiements')
    payments_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Total encaissé'
    )
    
    # Paiements par méthode
    payments_cash = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Espèces'
    )
    payments_check = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Chèques'
    )
    payments_transfer = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Virements'
    )
    payments_card = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Cartes bancaires'
    )
    payments_mobile = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Paiements mobiles'
    )
    
    # === FACTURES ===
    # Factures créées
    invoices_created_count = models.IntegerField(default=0, verbose_name='Factures créées')
    invoices_created_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Montant facturé'
    )
    
    # Factures en attente (à cette date)
    invoices_pending_count = models.IntegerField(default=0, verbose_name='Factures en attente')
    invoices_pending_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Montant en attente'
    )
    
    # Factures payées
    invoices_paid_count = models.IntegerField(default=0, verbose_name='Factures payées')
    invoices_paid_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Montant payé'
    )
    
    # Factures en retard (à cette date)
    invoices_overdue_count = models.IntegerField(default=0, verbose_name='Factures en retard')
    invoices_overdue_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Montant en retard'
    )
    
    # Factures partiellement payées
    invoices_partial_count = models.IntegerField(default=0, verbose_name='Factures partielles')
    invoices_partial_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Solde partiel'
    )
    
    # === COMPARAISONS ===
    # Comparaison avec le jour précédent
    payments_diff_previous_day = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Différence jour précédent',
        help_text='Différence de paiements vs jour précédent'
    )
    payments_diff_previous_day_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='% jour précédent'
    )
    
    # Comparaison avec la semaine précédente (même jour)
    payments_diff_previous_week = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Différence semaine précédente'
    )
    payments_diff_previous_week_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='% semaine précédente'
    )
    
    # Moyenne mobile du mois
    monthly_average_payments = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Moyenne mensuelle'
    )
    
    # === TRÉSORERIE & PRÉVISIONS ===
    total_receivables = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Créances totales',
        help_text='Montant total à recevoir'
    )
    
    collection_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Taux de recouvrement (%)',
        help_text='Pourcentage de paiements reçus vs facturé'
    )
    
    # === DÉPENSES (si applicable) ===
    expenses_count = models.IntegerField(default=0, verbose_name='Nombre de dépenses')
    expenses_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Total dépenses'
    )
    
    # Balance nette du jour
    net_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Balance nette',
        help_text='Encaissements - Dépenses'
    )
    
    # === MÉTADONNÉES ===
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='Généré le')
    generated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='generated_reports',
        verbose_name='Généré par'
    )
    
    # Flag pour savoir si le rapport a été envoyé
    email_sent = models.BooleanField(default=False, verbose_name='Email envoyé')
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Email envoyé le')
    
    # Notes supplémentaires
    notes = models.TextField(blank=True, verbose_name='Notes et observations')
    
    # JSON pour données supplémentaires (graphiques, détails, etc.)
    additional_data = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name='Données supplémentaires',
        help_text='Stockage de données complexes pour graphiques et analyses'
    )

    class Meta:
        verbose_name = 'Rapport financier journalier'
        verbose_name_plural = 'Rapports financiers journaliers'
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['-report_date']),
            models.Index(fields=['generated_at']),
        ]

    def __str__(self):
        return f"Rapport financier du {self.report_date.strftime('%d/%m/%Y')}"

    @property
    def has_payments(self):
        """Vérifie si des paiements ont été reçus"""
        return self.payments_count > 0

    @property
    def average_payment_amount(self):
        """Calcule le montant moyen par paiement"""
        if self.payments_count > 0:
            return self.payments_total / self.payments_count
        return Decimal('0.00')

    @property
    def payment_methods_distribution(self):
        """Retourne la distribution des paiements par méthode"""
        if self.payments_total == 0:
            return {}
        
        return {
            'Espèces': {
                'amount': float(self.payments_cash),
                'percent': float((self.payments_cash / self.payments_total) * 100)
            },
            'Chèques': {
                'amount': float(self.payments_check),
                'percent': float((self.payments_check / self.payments_total) * 100)
            },
            'Virements': {
                'amount': float(self.payments_transfer),
                'percent': float((self.payments_transfer / self.payments_total) * 100)
            },
            'Cartes': {
                'amount': float(self.payments_card),
                'percent': float((self.payments_card / self.payments_total) * 100)
            },
            'Mobile': {
                'amount': float(self.payments_mobile),
                'percent': float((self.payments_mobile / self.payments_total) * 100)
            },
        }

    @property
    def invoices_status_distribution(self):
        """Retourne la distribution des factures par statut"""
        total = (self.invoices_pending_count + self.invoices_paid_count + 
                 self.invoices_overdue_count + self.invoices_partial_count)
        
        if total == 0:
            return {}
        
        return {
            'En attente': {
                'count': self.invoices_pending_count,
                'percent': (self.invoices_pending_count / total) * 100
            },
            'Payées': {
                'count': self.invoices_paid_count,
                'percent': (self.invoices_paid_count / total) * 100
            },
            'En retard': {
                'count': self.invoices_overdue_count,
                'percent': (self.invoices_overdue_count / total) * 100
            },
            'Partielles': {
                'count': self.invoices_partial_count,
                'percent': (self.invoices_partial_count / total) * 100
            },
        }

    @property
    def trend_indicator(self):
        """Indicateur de tendance (hausse/baisse)"""
        if self.payments_diff_previous_day > 0:
            return 'up'
        elif self.payments_diff_previous_day < 0:
            return 'down'
        return 'stable'

    def mark_as_sent(self):
        """Marque le rapport comme envoyé par email"""
        self.email_sent = True
        self.email_sent_at = timezone.now()
        self.save(update_fields=['email_sent', 'email_sent_at'])
