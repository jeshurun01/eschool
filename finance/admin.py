from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    FeeType, FeeStructure, Invoice, InvoiceItem, PaymentMethod, 
    Payment, Scholarship, ScholarshipApplication, Expense, Payroll,
    DailyFinancialReport
)


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_recurring', 'is_mandatory', 'created_at')
    list_filter = ('is_recurring', 'is_mandatory')
    search_fields = ('name',)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('fee_type', 'level', 'academic_year', 'amount', 'due_date')
    list_filter = ('fee_type', 'level', 'academic_year')
    search_fields = ('fee_type__name', 'level__name')


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student', 'issue_date', 'due_date', 'total_amount', 'status', 'balance')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'student__user__first_name', 'student__user__last_name')
    readonly_fields = ('invoice_number', 'subtotal', 'total_amount', 'paid_amount', 'balance')
    inlines = [InvoiceItemInline]
    date_hierarchy = 'issue_date'
    
    def save_model(self, request, obj, form, change):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user
        super().delete_model(request, obj)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'requires_reference')
    list_filter = ('is_active', 'requires_reference')
    search_fields = ('name', 'code')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'invoice', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('payment_reference', 'transaction_id', 'invoice__invoice_number')
    readonly_fields = ('payment_reference',)
    date_hierarchy = 'payment_date'
    
    def save_model(self, request, obj, form, change):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user
        super().delete_model(request, obj)


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'academic_year', 'is_active', 'start_date', 'end_date')
    list_filter = ('type', 'academic_year', 'is_active')
    search_fields = ('name',)
    filter_horizontal = ('eligible_levels',)


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'scholarship', 'application_date', 'status', 'approved_by')
    list_filter = ('status', 'application_date', 'scholarship')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'scholarship__name')
    date_hierarchy = 'application_date'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'category', 'amount', 'expense_date', 'is_approved', 'recorded_by')
    list_filter = ('category', 'is_approved', 'expense_date')
    search_fields = ('description',)
    date_hierarchy = 'expense_date'


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period_start', 'period_end', 'base_salary', 'net_salary', 'status')
    list_filter = ('status', 'period_start')
    search_fields = ('employee__user__first_name', 'employee__user__last_name')
    date_hierarchy = 'period_start'


@admin.register(DailyFinancialReport)
class DailyFinancialReportAdmin(admin.ModelAdmin):
    list_display = (
        'report_date', 
        'payments_display', 
        'invoices_status_display',
        'overdue_display',
        'trend_display',
        'email_status',
        'generated_at'
    )
    list_filter = ('report_date', 'email_sent', 'generated_at')
    search_fields = ('notes',)
    readonly_fields = (
        'report_date', 'generated_at', 'generated_by', 'email_sent_at',
        'payments_count', 'payments_total', 'payments_cash', 'payments_check',
        'payments_transfer', 'payments_card', 'payments_mobile',
        'invoices_created_count', 'invoices_created_total',
        'invoices_pending_count', 'invoices_pending_total',
        'invoices_paid_count', 'invoices_paid_total',
        'invoices_overdue_count', 'invoices_overdue_total',
        'invoices_partial_count', 'invoices_partial_total',
        'payments_diff_previous_day', 'payments_diff_previous_day_percent',
        'payments_diff_previous_week', 'payments_diff_previous_week_percent',
        'monthly_average_payments', 'total_receivables', 'collection_rate',
        'expenses_count', 'expenses_total', 'net_balance', 'additional_data'
    )
    date_hierarchy = 'report_date'
    ordering = ('-report_date',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('report_date', 'generated_at', 'generated_by', 'notes')
        }),
        ('Paiements reçus', {
            'fields': (
                'payments_count', 'payments_total',
                ('payments_cash', 'payments_check'),
                ('payments_transfer', 'payments_card'),
                'payments_mobile',
            )
        }),
        ('Factures', {
            'fields': (
                ('invoices_created_count', 'invoices_created_total'),
                ('invoices_pending_count', 'invoices_pending_total'),
                ('invoices_paid_count', 'invoices_paid_total'),
                ('invoices_overdue_count', 'invoices_overdue_total'),
                ('invoices_partial_count', 'invoices_partial_total'),
            )
        }),
        ('Comparaisons', {
            'fields': (
                ('payments_diff_previous_day', 'payments_diff_previous_day_percent'),
                ('payments_diff_previous_week', 'payments_diff_previous_week_percent'),
                'monthly_average_payments',
            )
        }),
        ('Trésorerie', {
            'fields': (
                'total_receivables',
                'collection_rate',
                ('expenses_count', 'expenses_total'),
                'net_balance',
            )
        }),
        ('Email', {
            'fields': ('email_sent', 'email_sent_at')
        }),
        ('Données supplémentaires', {
            'classes': ('collapse',),
            'fields': ('additional_data',)
        }),
    )
    
    def payments_display(self, obj):
        """Affichage formaté des paiements"""
        return format_html(
            '<strong>{}</strong> paiements<br>{:,.0f} FCFA',
            obj.payments_count,
            obj.payments_total
        )
    payments_display.short_description = 'Paiements'
    
    def invoices_status_display(self, obj):
        """Affichage des statuts de factures"""
        return format_html(
            '✅ {} payées<br>⏳ {} en attente',
            obj.invoices_paid_count,
            obj.invoices_pending_count
        )
    invoices_status_display.short_description = 'Factures'
    
    def overdue_display(self, obj):
        """Affichage des factures en retard"""
        if obj.invoices_overdue_count > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {} en retard<br>{:,.0f} FCFA</span>',
                obj.invoices_overdue_count,
                obj.invoices_overdue_total
            )
        return format_html('<span style="color: green;">✓ Aucune</span>')
    overdue_display.short_description = 'En retard'
    
    def trend_display(self, obj):
        """Affichage de la tendance"""
        if obj.payments_diff_previous_day > 0:
            return format_html(
                '<span style="color: green;">📈 +{:,.0f} FCFA<br>(+{:.1f}%)</span>',
                obj.payments_diff_previous_day,
                obj.payments_diff_previous_day_percent
            )
        elif obj.payments_diff_previous_day < 0:
            return format_html(
                '<span style="color: orange;">📉 {:,.0f} FCFA<br>({:.1f}%)</span>',
                obj.payments_diff_previous_day,
                obj.payments_diff_previous_day_percent
            )
        return format_html('<span style="color: gray;">➡️ Stable</span>')
    trend_display.short_description = 'Tendance'
    
    def email_status(self, obj):
        """Statut de l'envoi d'email"""
        if obj.email_sent:
            return format_html(
                '<span style="color: green;">✓ Envoyé<br>{}</span>',
                obj.email_sent_at.strftime('%d/%m/%Y %H:%M') if obj.email_sent_at else ''
            )
        return format_html('<span style="color: gray;">✗ Non envoyé</span>')
    email_status.short_description = 'Email'
    
    def has_add_permission(self, request):
        """Empêcher la création manuelle (utiliser la commande)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Autoriser la suppression uniquement pour les superusers"""
        return request.user.is_superuser
    
    actions = ['mark_as_sent', 'regenerate_report']
    
    def mark_as_sent(self, request, queryset):
        """Action pour marquer comme envoyé"""
        count = 0
        for report in queryset:
            if not report.email_sent:
                report.mark_as_sent()
                count += 1
        self.message_user(request, f'{count} rapport(s) marqué(s) comme envoyé.')
    mark_as_sent.short_description = 'Marquer comme envoyé par email'
    
    def regenerate_report(self, request, queryset):
        """Action pour régénérer les rapports sélectionnés"""
        from django.core.management import call_command
        count = 0
        for report in queryset:
            try:
                call_command('generate_daily_financial_report', date=str(report.report_date), force=True)
                count += 1
            except Exception as e:
                self.message_user(request, f'Erreur pour {report.report_date}: {str(e)}', level='error')
        if count > 0:
            self.message_user(request, f'{count} rapport(s) régénéré(s) avec succès.')
    regenerate_report.short_description = 'Régénérer les rapports sélectionnés'
