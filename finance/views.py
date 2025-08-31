from django.shortcuts import render
from django.http import HttpResponse

# Vues temporaires (placeholder) - À implémenter plus tard

def fee_type_list(request):
    return HttpResponse("Liste des types de frais - En cours de développement")

def fee_type_create(request):
    return HttpResponse("Créer un type de frais - En cours de développement")

def invoice_list(request):
    return HttpResponse("Liste des factures - En cours de développement")

def invoice_create(request):
    return HttpResponse("Créer une facture - En cours de développement")

def invoice_detail(request, invoice_id):
    return HttpResponse(f"Détails de la facture {invoice_id} - En cours de développement")

def invoice_edit(request, invoice_id):
    return HttpResponse(f"Modifier la facture {invoice_id} - En cours de développement")

def invoice_pdf(request, invoice_id):
    return HttpResponse(f"PDF de la facture {invoice_id} - En cours de développement")

def payment_list(request):
    return HttpResponse("Liste des paiements - En cours de développement")

def payment_create(request):
    return HttpResponse("Créer un paiement - En cours de développement")

def payment_detail(request, payment_id):
    return HttpResponse(f"Détails du paiement {payment_id} - En cours de développement")

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
