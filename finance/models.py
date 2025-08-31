from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


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
    
    issue_date = models.DateField(default=timezone.now, verbose_name='Date d\'émission')
    due_date = models.DateField(verbose_name='Date d\'échéance')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Sous-total')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Remise')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Montant total')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
    payment_date = models.DateTimeField(default=timezone.now, verbose_name='Date de paiement')
    processed_date = models.DateTimeField(blank=True, null=True, verbose_name='Date de traitement')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    # Informations de la passerelle de paiement
    gateway_response = models.JSONField(blank=True, null=True, verbose_name='Réponse de la passerelle')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
    application_date = models.DateField(default=timezone.now, verbose_name='Date de demande')
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
    
    expense_date = models.DateField(default=timezone.now, verbose_name='Date de dépense')
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
