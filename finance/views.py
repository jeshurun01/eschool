from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

# Import RBAC
from core.decorators.permissions import (
    staff_required, parent_required, student_required, 
    admin_required, parent_or_student_required
)

from .models import Payment, Invoice, PaymentMethod

# Vues temporaires (placeholder) - À implémenter plus tard

@staff_required  # Seul le personnel financier/admin peut gérer les types de frais
def fee_type_list(request):
    return HttpResponse("Liste des types de frais - En cours de développement")

@staff_required
def fee_type_create(request):
    return HttpResponse("Créer un type de frais - En cours de développement")

@parent_or_student_required  # Parents et élèves peuvent voir leurs factures
def invoice_list(request):
    return HttpResponse("Liste des factures - En cours de développement")

@staff_required  # Seul le personnel financier peut créer des factures
def invoice_create(request):
    return HttpResponse("Créer une facture - En cours de développement")

@parent_or_student_required
def invoice_detail(request, invoice_id):
    return HttpResponse(f"Détails de la facture {invoice_id} - En cours de développement")

@staff_required
def invoice_edit(request, invoice_id):
    return HttpResponse(f"Modifier la facture {invoice_id} - En cours de développement")

@parent_or_student_required
def invoice_pdf(request, invoice_id):
    return HttpResponse(f"PDF de la facture {invoice_id} - En cours de développement")

@parent_or_student_required  # Parents et élèves peuvent voir leurs paiements
def payment_list(request):
    """Liste des paiements avec filtres et pagination"""
    # Utiliser le manager RBAC pour filtrer selon le rôle
    payments = Payment.objects.for_role(request.user).select_related('invoice', 'payment_method').all()
    
    # Filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        payments = payments.filter(
            Q(payment_reference__icontains=search_query) |
            Q(invoice__invoice_number__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(payments, 25)  # 25 paiements par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques pour le contexte
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status='COMPLETED').count()
    pending_payments = Payment.objects.filter(status='PENDING').count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_status_choices': Payment.STATUS_CHOICES,
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'finance/payment_list.html', context)

def payment_create(request):
    return HttpResponse("Créer un paiement - En cours de développement")

@parent_or_student_required  # Parents et élèves peuvent voir leurs paiements
def payment_detail(request, payment_id):
    """Détails d'un paiement"""
    # Utiliser le manager RBAC pour s'assurer que l'utilisateur peut voir ce paiement
    payment = get_object_or_404(
        Payment.objects.for_role(request.user), 
        id=payment_id
    )
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'finance/payment_detail.html', context)

def scholarship_list(request):
    return HttpResponse("Liste des bourses - En cours de développement")

def scholarship_create(request):
    return HttpResponse("Créer une bourse - En cours de développement")

def scholarship_application_list(request):
    return HttpResponse("Liste des demandes de bourse - En cours de développement")

def expense_list(request):
    return HttpResponse("Liste des dépenses - En cours de développement")

def expense_create(request):
    return HttpResponse("Créer une dépense - En cours de développement")

def expense_detail(request, expense_id):
    return HttpResponse(f"Détails de la dépense {expense_id} - En cours de développement")

def payroll_list(request):
    return HttpResponse("Liste des paies - En cours de développement")

def payroll_create(request):
    return HttpResponse("Créer une paie - En cours de développement")

def payroll_detail(request, payroll_id):
    return HttpResponse(f"Détails de la paie {payroll_id} - En cours de développement")

def financial_reports(request):
    return HttpResponse("Rapports financiers - En cours de développement")

def revenue_report(request):
    return HttpResponse("Rapport des revenus - En cours de développement")

def expense_report(request):
    return HttpResponse("Rapport des dépenses - En cours de développement")

def report_list(request):
    return HttpResponse("Liste des rapports - En cours de développement")

def invoice_generate(request):
    return HttpResponse("Générer des factures - En cours de développement")
