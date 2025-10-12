from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Gestion des types de frais
    path('fee-types/', views.fee_type_list, name='fee_type_list'),
    path('fee-types/create/', views.fee_type_create, name='fee_type_create'),
    path('fee-structures/', views.fee_structure_list, name='fee_structure_list'),
    path('fee-structures/create/', views.fee_structure_create, name='fee_structure_create'),
    path('fee-structures/create/<int:fee_type_id>/', views.fee_structure_create, name='fee_structure_create_for_type'),
    
    # Gestion des factures
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:invoice_id>/pay/', views.invoice_pay, name='invoice_pay'),
    path('invoices/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    
    # Gestion des paiements
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/pending/', views.pending_payments, name='pending_payments'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:payment_id>/confirm/', views.payment_confirm, name='payment_confirm'),
    
    # Gestion des bourses
    path('scholarships/', views.scholarship_list, name='scholarship_list'),
    path('scholarships/create/', views.scholarship_create, name='scholarship_create'),
    path('scholarships/applications/', views.scholarship_application_list, name='scholarship_application_list'),
    
    # Gestion des dépenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/', views.expense_detail, name='expense_detail'),
    
    # Gestion de la paie
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/create/', views.payroll_create, name='payroll_create'),
    path('payroll/<int:payroll_id>/', views.payroll_detail, name='payroll_detail'),
    
    # Rapports financiers
    path('reports/', views.financial_reports, name='financial_reports'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    path('reports/expenses/', views.expense_report, name='expense_report'),
    path('reports/list/', views.report_list, name='report_list'),
    
    # Rapports financiers journaliers
    path('reports/daily/', views.daily_financial_report, name='daily_financial_report'),
    path('reports/daily/generate/', views.daily_financial_report_generate, name='daily_financial_report_generate'),
    path('reports/daily/<str:date>/pdf/', views.daily_financial_report_export_pdf, name='daily_financial_report_export_pdf'),
    path('reports/daily/<str:date>/excel/', views.daily_financial_report_export_excel, name='daily_financial_report_export_excel'),
    
    # URLs pour les dashboards
    path('invoices/generate/', views.invoice_generate, name='invoice_generate'),
]
