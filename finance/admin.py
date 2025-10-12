from django.contrib import admin
from .models import (
    FeeType, FeeStructure, Invoice, InvoiceItem, PaymentMethod, 
    Payment, Scholarship, ScholarshipApplication, Expense, Payroll
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
