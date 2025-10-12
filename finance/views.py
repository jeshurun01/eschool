from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation

# Import RBAC
from core.decorators.permissions import (
    staff_required, parent_required, student_required, 
    admin_required, parent_or_student_required
)

from .models import Payment, Invoice, PaymentMethod, FeeType, FeeStructure, InvoiceItem
from academic.models import Level, AcademicYear, Enrollment
from accounts.models import Student

# Vues temporaires (placeholder) - À implémenter plus tard

@staff_required  # Seul le personnel financier/admin peut gérer les types de frais
def fee_type_list(request):
    """Liste des types de frais et structures de frais"""
    fee_types = FeeType.objects.all().order_by('name')
    
    # Organiser les structures par type de frais et compter
    for fee_type in fee_types:
        fee_type.fee_structures_list = FeeStructure.objects.filter(
            fee_type=fee_type
        ).select_related('level', 'academic_year').order_by('level__name')
        fee_type.structures_count = fee_type.fee_structures_list.count()
    
    # Statistiques pour les filtres
    total_mandatory = sum(1 for ft in fee_types if ft.is_mandatory)
    total_recurring = sum(1 for ft in fee_types if ft.is_recurring)
    
    context = {
        'fee_types': fee_types,
        'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
        'total_mandatory': total_mandatory,
        'total_recurring': total_recurring,
    }
    
    return render(request, 'finance/fee_type_list.html', context)

@staff_required
def fee_type_create(request):
    """Créer un nouveau type de frais"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_recurring = request.POST.get('is_recurring') == 'on'
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        
        if name:
            try:
                fee_type = FeeType.objects.create(
                    name=name,
                    description=description,
                    is_recurring=is_recurring,
                    is_mandatory=is_mandatory
                )
                messages.success(request, f'Type de frais "{fee_type.name}" créé avec succès.')
                return redirect('finance:fee_type_list')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
        else:
            messages.error(request, 'Le nom du type de frais est obligatoire.')
    
    return render(request, 'finance/fee_type_create.html')

@staff_required
def fee_structure_list(request):
    """Liste des structures tarifaires"""
    fee_structures = FeeStructure.objects.select_related(
        'fee_type', 'level', 'academic_year'
    ).order_by('fee_type__name', 'academic_year__name', 'level__name')
    
    context = {
        'fee_structures': fee_structures,
        'fee_types': FeeType.objects.all().order_by('name'),
        'levels': Level.objects.all().order_by('name'),
        'academic_years': AcademicYear.objects.all().order_by('-is_current', 'name'),
    }
    
    return render(request, 'finance/fee_structure_list.html', context)

@staff_required
def fee_structure_create(request, fee_type_id=None):
    """Créer une nouvelle structure tarifaire"""
    if request.method == 'POST':
        fee_type_id = request.POST.get('fee_type')
        level_id = request.POST.get('level')
        academic_year_id = request.POST.get('academic_year')
        amount = request.POST.get('amount')
        due_date_str = request.POST.get('due_date')
        
        try:
            # Validation
            fee_type = FeeType.objects.get(id=fee_type_id)
            level = Level.objects.get(id=level_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
            
            # Vérifier si une structure similaire existe déjà
            existing = FeeStructure.objects.filter(
                fee_type=fee_type,
                level=level,
                academic_year=academic_year
            ).first()
            
            if existing:
                messages.error(request, f'Une structure tarifaire existe déjà pour {fee_type.name} - {level.name} ({academic_year.name})')
                return redirect('finance:fee_structure_create')
            
            # Date d'échéance optionnelle
            due_date = None
            if due_date_str:
                from datetime import datetime
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            # Créer la structure
            fee_structure = FeeStructure.objects.create(
                fee_type=fee_type,
                level=level,
                academic_year=academic_year,
                amount=amount,
                due_date=due_date
            )
            
            messages.success(request, f'Structure tarifaire créée: {fee_structure}')
            return redirect('finance:fee_type_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
    
    # Pré-sélectionner le type de frais si fourni
    selected_fee_type = None
    if fee_type_id:
        try:
            selected_fee_type = FeeType.objects.get(id=fee_type_id)
        except FeeType.DoesNotExist:
            pass
    
    context = {
        'fee_types': FeeType.objects.all().order_by('name'),
        'levels': Level.objects.all().order_by('name'),
        'academic_years': AcademicYear.objects.all().order_by('-is_current', 'name'),
        'selected_fee_type': selected_fee_type,
        'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
    }
    
    return render(request, 'finance/fee_structure_create.html', context)

@parent_or_student_required  # Parents et élèves peuvent voir leurs factures
def invoice_list(request):
    """Liste des factures avec filtres et pagination"""
    # Gestion de la modification en lot
    if request.method == 'POST' and request.user.is_staff:
        print(f"[DEBUG] POST request reçu par {request.user}")  # Debug
        print(f"[DEBUG] POST data: {request.POST}")  # Debug
        
        action = request.POST.get('action')
        selected_invoices = request.POST.getlist('selected_invoices')
        
        print(f"[DEBUG] Action: {action}")  # Debug
        print(f"[DEBUG] Selected invoices: {selected_invoices}")  # Debug
        
        if action == 'bulk_status_change' and selected_invoices:
            new_status = request.POST.get('new_status')
            print(f"[DEBUG] New status: {new_status}")  # Debug
            
            if new_status and new_status in dict(Invoice.STATUS_CHOICES):
                try:
                    # Filtrer les factures selon les permissions RBAC
                    invoices_to_update = Invoice.objects.filter(
                        id__in=selected_invoices
                    )
                    print(f"[DEBUG] Factures trouvées: {invoices_to_update.count()}")  # Debug
                    
                    updated_count = invoices_to_update.update(status=new_status)
                    print(f"[DEBUG] Factures mises à jour: {updated_count}")  # Debug
                    
                    status_display = dict(Invoice.STATUS_CHOICES)[new_status]
                    messages.success(
                        request, 
                        f'{updated_count} facture(s) ont été modifiée(s) au statut "{status_display}".'
                    )
                    print(f"[DEBUG] Message de succès ajouté")  # Debug
                except Exception as e:
                    print(f"[DEBUG] Erreur: {e}")  # Debug
                    messages.error(request, f'Erreur lors de la modification: {str(e)}')
            else:
                print(f"[DEBUG] Statut invalide: {new_status}")  # Debug
                messages.error(request, 'Statut invalide sélectionné.')
        elif action == 'bulk_delete' and selected_invoices and request.user.is_superuser:
            try:
                invoices_to_delete = Invoice.objects.filter(
                    id__in=selected_invoices
                )
                deleted_count = invoices_to_delete.count()
                invoices_to_delete.delete()
                
                messages.success(request, f'{deleted_count} facture(s) ont été supprimée(s).')
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')
        else:
            print(f"[DEBUG] Aucune action effectuée - Action: {action}, Selected: {len(selected_invoices) if selected_invoices else 0}")  # Debug
        
        print(f"[DEBUG] Redirection vers invoice_list")  # Debug
        return redirect('finance:invoice_list')
    
    # Utiliser le manager RBAC pour filtrer selon le rôle
    invoices = Invoice.objects.for_role(request.user).select_related(
        'student__user', 'parent__user'
    ).prefetch_related('items__fee_type')
    
    # Filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    student_filter = request.GET.get('student', '')
    
    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    if student_filter and (hasattr(request.user, 'teacher_profile') or request.user.is_staff):
        invoices = invoices.filter(student_id=student_filter)
    
    # Statistiques pour le dashboard (exclure les brouillons)
    # Filtrer les factures non-brouillon pour les statistiques
    non_draft_invoices = invoices.exclude(status='DRAFT')
    
    total_invoices = non_draft_invoices.count()
    paid_invoices = non_draft_invoices.filter(status='PAID').count()
    pending_invoices = non_draft_invoices.filter(status='SENT').count()
    overdue_invoices = non_draft_invoices.filter(status='OVERDUE').count()
    
    # Montants (exclure les brouillons du calcul)
    from django.db.models import Sum
    total_amount = non_draft_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    paid_amount = non_draft_invoices.filter(status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_amount = non_draft_invoices.filter(status__in=['SENT', 'OVERDUE']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Pagination
    paginator = Paginator(invoices.order_by('-issue_date'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Pour les enseignants/staff : liste des étudiants pour le filtre
    students = None
    if hasattr(request.user, 'teacher_profile') or request.user.is_staff:
        from accounts.models import Student
        students = Student.objects.filter(
            invoices__isnull=False
        ).distinct().select_related('user').order_by('user__first_name')
    
    context = {
        'page_obj': page_obj,
        'invoices': page_obj.object_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'student_filter': student_filter,
        'students': students,
        'stats': {
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'pending_invoices': pending_invoices,
            'overdue_invoices': overdue_invoices,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': pending_amount,
        },
        'status_choices': Invoice.STATUS_CHOICES,
    }
    
    return render(request, 'finance/invoice_list.html', context)

@staff_required  # Seul le personnel financier peut créer des factures
@admin_required
def invoice_create(request):
    """Créer une nouvelle facture"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        student_id = request.POST.get('student')
        due_date_str = request.POST.get('due_date')
        discount_str = request.POST.get('discount', '0')
        notes = request.POST.get('notes', '')
        
        # Données des éléments de facture
        fee_types = request.POST.getlist('fee_type')
        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        
        try:
            # Validation des données
            if not student_id:
                messages.error(request, 'Veuillez sélectionner un élève.')
                return redirect('finance:invoice_create')
            
            student = Student.objects.get(id=student_id)
            
            # Date d'échéance
            if due_date_str:
                from datetime import datetime
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            else:
                due_date = (timezone.now() + timedelta(days=30)).date()
            
            # Récupérer le parent responsable
            parent = student.parents.first()
            
            # Créer la facture
            invoice = Invoice.objects.create(
                student=student,
                parent=parent,
                due_date=due_date,
                discount=Decimal(discount_str) if discount_str else Decimal('0.00'),
                notes=notes,
                status='DRAFT'
            )
            
            # Créer les éléments de facture
            subtotal = Decimal('0.00')
            for i in range(len(fee_types)):
                if fee_types[i] and descriptions[i] and quantities[i] and unit_prices[i]:
                    try:
                        fee_type = FeeType.objects.get(id=int(fee_types[i]))
                        quantity = Decimal(quantities[i])
                        unit_price = Decimal(unit_prices[i])
                        
                        item = InvoiceItem.objects.create(
                            invoice=invoice,
                            fee_type=fee_type,
                            description=descriptions[i],
                            quantity=quantity,
                            unit_price=unit_price
                        )
                        subtotal += item.total
                    except (ValueError, FeeType.DoesNotExist):
                        pass
            
            # Mettre à jour les totaux de la facture
            invoice.subtotal = subtotal
            invoice.total_amount = subtotal - invoice.discount
            invoice.save()
            
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('finance:invoice_detail', invoice_id=invoice.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
    
    # GET request - afficher le formulaire
    context = {
        'students': Student.objects.select_related('user').all(),
        'fee_types': FeeType.objects.all(),
        'default_due_date': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
    }
    
    return render(request, 'finance/invoice_create.html', context)

@parent_or_student_required
@login_required
def invoice_detail(request, invoice_id):
    """Détails d'une facture avec RBAC"""
    # Récupérer la facture avec filtrage RBAC
    invoice = get_object_or_404(
        Invoice.objects.for_role(request.user).select_related(
            'student__user', 'parent__user'
        ).prefetch_related('items__fee_type'),
        id=invoice_id
    )
    
    # Récupérer les paiements liés à cette facture
    payments = invoice.payments.select_related('payment_method').all()
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'can_edit': request.user.role in ['ADMIN', 'SUPER_ADMIN'],
        'can_view_payments': True,  # Tous les utilisateurs autorisés peuvent voir les paiements
        'total_paid': sum(payment.amount for payment in payments),
        'remaining_amount': invoice.total_amount - sum(payment.amount for payment in payments),
    }
    
    return render(request, 'finance/invoice_detail.html', context)


@parent_or_student_required
@login_required
def invoice_pay(request, invoice_id):
    """Traiter le paiement d'une facture"""
    # Récupérer la facture avec filtrage RBAC
    invoice = get_object_or_404(
        Invoice.objects.for_role(request.user).select_related(
            'student__user', 'parent__user'
        ),
        id=invoice_id
    )
    
    # Vérifier que la facture peut être payée
    if invoice.status not in ['SENT', 'OVERDUE']:
        messages.error(request, 'Cette facture ne peut pas être payée.')
        return redirect('finance:invoice_detail', invoice_id=invoice.id)
    
    # Calculer le montant restant
    total_paid = sum(payment.amount for payment in invoice.payments.filter(status='COMPLETED'))
    remaining_amount = invoice.total_amount - total_paid
    
    if remaining_amount <= 0:
        messages.info(request, 'Cette facture est déjà entièrement payée.')
        return redirect('finance:invoice_detail', invoice_id=invoice.id)
    
    # Récupérer les méthodes de paiement actives
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        amount_str = request.POST.get('amount')
        transaction_id = request.POST.get('transaction_id', '')
        notes = request.POST.get('notes', '')
        
        try:
            # Validation du montant
            amount = Decimal(amount_str)
            if amount <= 0:
                messages.error(request, 'Le montant doit être positif.')
                raise ValueError('Montant invalide')
            
            if amount > remaining_amount:
                messages.error(request, f'Le montant ne peut pas dépasser le montant restant ({remaining_amount}€).')
                raise ValueError('Montant trop élevé')
            
            # Validation de la méthode de paiement
            payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, is_active=True)
            
            # Créer le paiement (en attente de confirmation admin)
            payment = Payment.objects.create(
                invoice=invoice,
                payment_method=payment_method,
                amount=amount,
                transaction_id=transaction_id,
                notes=notes,
                status='PENDING'  # En attente de confirmation par un admin
            )
            
            # Ne pas mettre à jour automatiquement le statut de la facture
            # Les admins devront confirmer le paiement d'abord
            messages.success(request, f'Demande de paiement de {amount}€ soumise avec succès. En attente de confirmation par l\'administration.')
            
            return redirect('finance:invoice_detail', invoice_id=invoice.id)
            
        except (ValueError, InvalidOperation):
            messages.error(request, 'Montant invalide.')
        except Exception as e:
            messages.error(request, f'Erreur lors du traitement du paiement: {str(e)}')
    
    context = {
        'invoice': invoice,
        'remaining_amount': remaining_amount,
        'total_paid': total_paid,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'finance/invoice_pay.html', context)


@admin_required
@login_required
def payment_confirm(request, payment_id):
    """Confirmer ou rejeter un paiement (admin seulement)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'confirm':
            # Confirmer le paiement
            payment.status = 'COMPLETED'
            payment.processed_date = timezone.now()
            if admin_notes:
                payment.notes = f"{payment.notes}\n[Admin] {admin_notes}" if payment.notes else f"[Admin] {admin_notes}"
            payment.save()
            
            # Vérifier si la facture est maintenant entièrement payée
            invoice = payment.invoice
            total_paid = sum(p.amount for p in invoice.payments.filter(status='COMPLETED'))
            
            if total_paid >= invoice.total_amount:
                invoice.status = 'PAID'
                invoice.save()
                messages.success(request, f'Paiement confirmé et facture marquée comme payée.')
            else:
                remaining = invoice.total_amount - total_paid
                messages.success(request, f'Paiement de {payment.amount}€ confirmé. Montant restant: {remaining}€')
                
        elif action == 'reject':
            # Rejeter le paiement
            payment.status = 'FAILED'
            payment.processed_date = timezone.now()
            if admin_notes:
                payment.notes = f"{payment.notes}\n[Admin - Rejet] {admin_notes}" if payment.notes else f"[Admin - Rejet] {admin_notes}"
            payment.save()
            messages.warning(request, f'Paiement de {payment.amount}€ rejeté.')
        
        return redirect('finance:payment_detail', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'invoice': payment.invoice,
    }
    
    return render(request, 'finance/payment_confirm.html', context)


@admin_required
@login_required  
def pending_payments(request):
    """Liste des paiements en attente de confirmation (admin seulement)"""
    pending_payments = Payment.objects.filter(status='PENDING').select_related(
        'invoice', 'invoice__student__user', 'payment_method'
    ).order_by('-payment_date')
    
    context = {
        'pending_payments': pending_payments,
        'pending_count': pending_payments.count(),
    }
    
    return render(request, 'finance/pending_payments.html', context)


@admin_required
def invoice_edit(request, invoice_id):
    """Modifier une facture avec RBAC"""
    # Récupérer la facture avec filtrage RBAC
    invoice = get_object_or_404(
        Invoice.objects.for_role(request.user).select_related(
            'student__user', 'parent__user'
        ).prefetch_related('items__fee_type'),
        id=invoice_id
    )
    
    if request.method == 'POST':
        # Traitement du formulaire
        status = request.POST.get('status')
        due_date_str = request.POST.get('due_date')
        discount_str = request.POST.get('discount', '0')
        notes = request.POST.get('notes', '')
        
        try:
            # Validation et mise à jour
            if status and status in dict(Invoice.STATUS_CHOICES):
                invoice.status = status
            
            if due_date_str:
                from datetime import datetime
                try:
                    invoice.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Format de date invalide. Utilisez le format YYYY-MM-DD.')
                    return render(request, 'finance/invoice_edit.html', {
                        'invoice': invoice,
                        'status_choices': Invoice.STATUS_CHOICES,
                        'fee_types': FeeType.objects.all(),
                    })
            
            if discount_str and discount_str.strip():
                try:
                    # Fonction de nettoyage avancée pour les valeurs numériques
                    def clean_numeric_string(value):
                        """Nettoie une chaîne pour la conversion en Decimal"""
                        if not value or not str(value).strip():
                            return "0"
                        
                        # Convertir en string et nettoyer
                        clean = str(value).strip()
                        
                        # Supprimer les caractères non numériques sauf point, virgule et tiret
                        import re
                        clean = re.sub(r'[^\d.,\-]', '', clean)
                        
                        # Gérer les séparateurs de milliers (ex: 1,234.56 ou 1.234,56)
                        if ',' in clean and '.' in clean:
                            # Détecter le format (US: 1,234.56 vs EU: 1.234,56)
                            last_comma = clean.rfind(',')
                            last_dot = clean.rfind('.')
                            if last_dot > last_comma:
                                # Format US: 1,234.56
                                clean = clean.replace(',', '')
                            else:
                                # Format EU: 1.234,56
                                clean = clean.replace('.', '').replace(',', '.')
                        elif ',' in clean:
                            # Détecter si c'est un séparateur décimal ou de milliers
                            parts = clean.split(',')
                            if len(parts) == 2 and len(parts[1]) <= 2:
                                # Probablement décimal: 100,50
                                clean = clean.replace(',', '.')
                            else:
                                # Probablement milliers: 1,234
                                clean = clean.replace(',', '')
                        
                        # Valider qu'il ne reste qu'un seul point décimal
                        if clean.count('.') > 1:
                            raise ValueError("Format numérique invalide")
                        
                        return clean
                    
                    discount_str_clean = clean_numeric_string(discount_str)
                    discount = Decimal(discount_str_clean)
                    
                    if discount >= 0 and discount <= invoice.subtotal:
                        invoice.discount = discount
                        invoice.total_amount = invoice.subtotal - discount
                    else:
                        messages.error(request, f'La remise doit être entre 0 et {invoice.subtotal}.')
                        return render(request, 'finance/invoice_edit.html', {
                            'invoice': invoice,
                            'status_choices': Invoice.STATUS_CHOICES,
                            'fee_types': FeeType.objects.all(),
                        })
                except (ValueError, InvalidOperation) as e:
                    messages.error(request, f'Valeur de remise invalide: "{discount_str}". Utilisez un nombre valide (ex: 100.50).')
                    return render(request, 'finance/invoice_edit.html', {
                        'invoice': invoice,
                        'status_choices': Invoice.STATUS_CHOICES,
                        'fee_types': FeeType.objects.all(),
                    })
            
            invoice.notes = notes
            invoice.save()
            
            # Traitement des éléments de facture
            item_ids = request.POST.getlist('item_id')
            item_descriptions = request.POST.getlist('item_description')
            item_quantities = request.POST.getlist('item_quantity')
            item_unit_prices = request.POST.getlist('item_unit_price')
            
            # Mise à jour des éléments existants
            for i, item_id in enumerate(item_ids):
                if item_id and item_id != 'new':
                    try:
                        item = InvoiceItem.objects.get(id=int(item_id), invoice=invoice)
                        if i < len(item_descriptions):
                            item.description = item_descriptions[i]
                        if i < len(item_quantities):
                            try:
                                def clean_numeric_string(value):
                                    """Nettoie une chaîne pour la conversion en Decimal"""
                                    if not value or not str(value).strip():
                                        return "0"
                                    
                                    import re
                                    clean = str(value).strip()
                                    clean = re.sub(r'[^\d.,\-]', '', clean)
                                    
                                    if ',' in clean and '.' in clean:
                                        last_comma = clean.rfind(',')
                                        last_dot = clean.rfind('.')
                                        if last_dot > last_comma:
                                            clean = clean.replace(',', '')
                                        else:
                                            clean = clean.replace('.', '').replace(',', '.')
                                    elif ',' in clean:
                                        parts = clean.split(',')
                                        if len(parts) == 2 and len(parts[1]) <= 2:
                                            clean = clean.replace(',', '.')
                                        else:
                                            clean = clean.replace(',', '')
                                    
                                    if clean.count('.') > 1:
                                        raise ValueError("Format numérique invalide")
                                    
                                    return clean
                                
                                quantity_str = clean_numeric_string(item_quantities[i])
                                item.quantity = Decimal(quantity_str)
                            except (ValueError, InvalidOperation):
                                messages.error(request, f'Quantité invalide pour l\'élément {item.description}: "{item_quantities[i]}". Utilisez un nombre valide.')
                                continue
                        if i < len(item_unit_prices):
                            try:
                                def clean_numeric_string(value):
                                    """Nettoie une chaîne pour la conversion en Decimal"""
                                    if not value or not str(value).strip():
                                        return "0"
                                    
                                    import re
                                    clean = str(value).strip()
                                    clean = re.sub(r'[^\d.,\-]', '', clean)
                                    
                                    if ',' in clean and '.' in clean:
                                        last_comma = clean.rfind(',')
                                        last_dot = clean.rfind('.')
                                        if last_dot > last_comma:
                                            clean = clean.replace(',', '')
                                        else:
                                            clean = clean.replace('.', '').replace(',', '.')
                                    elif ',' in clean:
                                        parts = clean.split(',')
                                        if len(parts) == 2 and len(parts[1]) <= 2:
                                            clean = clean.replace(',', '.')
                                        else:
                                            clean = clean.replace(',', '')
                                    
                                    if clean.count('.') > 1:
                                        raise ValueError("Format numérique invalide")
                                    
                                    return clean
                                
                                price_str = clean_numeric_string(item_unit_prices[i])
                                item.unit_price = Decimal(price_str)
                            except (ValueError, InvalidOperation):
                                messages.error(request, f'Prix unitaire invalide pour l\'élément {item.description}: "{item_unit_prices[i]}". Utilisez un nombre valide.')
                                continue
                        item.save()  # Le total sera calculé automatiquement
                    except (ValueError, InvoiceItem.DoesNotExist):
                        pass
            
            # Recalculer les totaux
            invoice.subtotal = sum(item.total for item in invoice.items.all())
            invoice.total_amount = invoice.subtotal - invoice.discount
            invoice.save()
            
            messages.success(request, 'Facture mise à jour avec succès.')
            return redirect('finance:invoice_detail', invoice_id=invoice.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour: {str(e)}')
    
    context = {
        'invoice': invoice,
        'status_choices': Invoice.STATUS_CHOICES,
        'fee_types': FeeType.objects.all(),
    }
    
    return render(request, 'finance/invoice_edit.html', context)

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
    
    # Statistiques pour le contexte - filtrées selon le rôle de l'utilisateur
    base_payments = Payment.objects.for_role(request.user)
    total_payments = base_payments.count()
    completed_payments = base_payments.filter(status='COMPLETED').count()
    pending_payments = base_payments.filter(status='PENDING').count()
    
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

@admin_required
def invoice_generate(request):
    """Générer des factures automatiquement"""
    from django.db.models import Q
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    if request.method == 'POST':
        # Récupérer les paramètres du formulaire
        fee_type_id = request.POST.get('fee_type')
        level_id = request.POST.get('level')
        academic_year_id = request.POST.get('academic_year')
        due_date_str = request.POST.get('due_date')
        
        # Validation
        if not fee_type_id or not academic_year_id:
            messages.error(request, 'Le type de frais et l\'année académique sont obligatoires.')
            return redirect('finance:invoice_generate')
        
        try:
            fee_type = FeeType.objects.get(id=fee_type_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
            
            # Date d'échéance
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            else:
                due_date = (timezone.now() + timedelta(days=30)).date()
            
            # Construire la requête pour les élèves
            students_query = Student.objects.select_related('user').filter(
                enrollments__academic_year=academic_year,
                enrollments__is_active=True
            )
            
            # Filtrer par niveau si spécifié
            if level_id:
                level = Level.objects.get(id=level_id)
                students_query = students_query.filter(
                    enrollments__classroom__level=level
                )
            
            students = students_query.distinct()
            
            if not students.exists():
                messages.warning(request, 'Aucun élève trouvé avec les critères spécifiés.')
                return redirect('finance:invoice_generate')
            
            # Compter les factures créées
            created_count = 0
            errors = []
            
            for student in students:
                try:
                    # Récupérer la structure de frais pour le niveau de l'élève
                    enrollment = student.enrollments.filter(
                        academic_year=academic_year,
                        is_active=True
                    ).first()
                    
                    if not enrollment:
                        errors.append(f"Pas d'inscription active pour {student.user.get_full_name()}")
                        continue
                    
                    fee_structure = FeeStructure.objects.filter(
                        fee_type=fee_type,
                        level=enrollment.classroom.level,
                        academic_year=academic_year
                    ).first()
                    
                    if not fee_structure:
                        errors.append(f"Pas de structure de frais pour {fee_type.name} - {enrollment.classroom.level.name}")
                        continue
                    
                    # Vérifier si une facture similaire existe déjà
                    existing_invoice = Invoice.objects.filter(
                        student=student,
                        items__fee_type=fee_type,
                        status__in=['DRAFT', 'PENDING']
                    ).first()
                    
                    if existing_invoice:
                        errors.append(f"Facture en cours déjà existante pour {student.user.get_full_name()}")
                        continue
                    
                    # Récupérer le parent responsable (premier parent)
                    parent = student.parents.first()
                    
                    # Créer la facture
                    invoice = Invoice.objects.create(
                        student=student,
                        parent=parent,
                        due_date=due_date,
                        status='DRAFT'
                    )
                    
                    # Créer l'élément de facture
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        fee_type=fee_type,
                        description=f"{fee_type.name} - {enrollment.classroom.level.name}",
                        quantity=1,
                        unit_price=fee_structure.amount
                    )
                    
                    # Mettre à jour les totaux de la facture
                    invoice.subtotal = fee_structure.amount
                    invoice.total_amount = fee_structure.amount
                    invoice.save()
                    
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Erreur pour {student.user.get_full_name()}: {str(e)}")
            
            # Messages de résultat
            if created_count > 0:
                messages.success(request, f'{created_count} facture(s) créée(s) avec succès.')
            
            if errors:
                for error in errors[:5]:  # Limiter à 5 erreurs affichées
                    messages.warning(request, error)
                if len(errors) > 5:
                    messages.info(request, f"... et {len(errors) - 5} autres erreurs.")
            
            return redirect('finance:invoice_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération: {str(e)}')
            return redirect('finance:invoice_generate')
    
    # GET request - afficher le formulaire
    context = {
        'fee_types': FeeType.objects.all(),
        'levels': Level.objects.all(),
        'academic_years': AcademicYear.objects.all(),
        'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
        'default_due_date': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
    }
    
    return render(request, 'finance/invoice_generate.html', context)


# ===========================
# RAPPORTS FINANCIERS
# ===========================

@staff_required  # Seuls admin et personnel financier
def daily_financial_report(request):
    """
    Affiche le rapport financier journalier avec tous les KPIs
    Permet de filtrer par date et de visualiser les tendances
    """
    from .models import DailyFinancialReport
    from django.http import JsonResponse
    import json
    
    # Date sélectionnée (par défaut: aujourd'hui)
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            from datetime import datetime
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Récupérer le rapport pour la date sélectionnée
    report = DailyFinancialReport.objects.filter(report_date=selected_date).first()
    
    # Si le rapport n'existe pas, proposer de le générer
    if not report:
        # Vérifier si c'est une date future (on ne peut pas générer)
        if selected_date > timezone.now().date():
            messages.warning(
                request, 
                'Impossible de générer un rapport pour une date future.'
            )
        else:
            messages.info(
                request, 
                f'Aucun rapport trouvé pour le {selected_date.strftime("%d/%m/%Y")}. '
                f'Utilisez la commande: python manage.py generate_daily_financial_report --date {selected_date}'
            )
    
    # Récupérer les derniers rapports pour l'historique
    recent_reports = DailyFinancialReport.objects.all().order_by('-report_date')[:30]
    
    # Préparer les données pour les graphiques
    chart_data = None
    if report:
        chart_data = {
            # Données pour le graphique des paiements par méthode
            'payment_methods': {
                'labels': [],
                'data': [],
                'colors': [
                    '#10b981',  # Vert pour espèces
                    '#3b82f6',  # Bleu pour chèques
                    '#8b5cf6',  # Violet pour virements
                    '#f59e0b',  # Orange pour cartes
                    '#ec4899',  # Rose pour mobile
                ]
            },
            # Données pour le graphique des factures par statut
            'invoice_status': {
                'labels': ['En attente', 'Payées', 'En retard', 'Partielles'],
                'data': [
                    report.invoices_pending_count,
                    report.invoices_paid_count,
                    report.invoices_overdue_count,
                    report.invoices_partial_count,
                ],
                'colors': ['#fbbf24', '#10b981', '#ef4444', '#f97316']
            },
            # Données pour l'historique des paiements (7 derniers jours)
            'payments_trend': {
                'labels': [],
                'data': []
            }
        }
        
        # Remplir les données de paiements par méthode
        payment_dist = report.payment_methods_distribution
        for method, data in payment_dist.items():
            if data['amount'] > 0:
                chart_data['payment_methods']['labels'].append(method)
                chart_data['payment_methods']['data'].append(data['amount'])
        
        # Historique des 7 derniers jours
        for i in range(6, -1, -1):
            date = selected_date - timedelta(days=i)
            day_report = DailyFinancialReport.objects.filter(report_date=date).first()
            chart_data['payments_trend']['labels'].append(date.strftime('%d/%m'))
            chart_data['payments_trend']['data'].append(
                float(day_report.payments_total) if day_report else 0
            )
    
    # Statistiques globales (tous les rapports)
    all_reports = DailyFinancialReport.objects.all()
    global_stats = {
        'total_reports': all_reports.count(),
        'total_payments': sum(r.payments_total for r in all_reports),
        'average_daily': (sum(r.payments_total for r in all_reports) / all_reports.count()) if all_reports.count() > 0 else 0,
    }
    
    context = {
        'report': report,
        'selected_date': selected_date,
        'recent_reports': recent_reports,
        'chart_data': json.dumps(chart_data) if chart_data else None,
        'global_stats': global_stats,
        'today': timezone.now().date(),
    }
    
    return render(request, 'finance/daily_financial_report.html', context)


@staff_required
def daily_financial_report_generate(request):
    """
    Génère (ou régénère) le rapport pour une date donnée via l'interface web
    """
    if request.method == 'POST':
        date_str = request.POST.get('date')
        force = request.POST.get('force') == 'true'
        
        try:
            from datetime import datetime
            from django.core.management import call_command
            from io import StringIO
            
            report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Vérifier si c'est une date future
            if report_date > timezone.now().date():
                messages.error(request, 'Impossible de générer un rapport pour une date future.')
                return redirect('finance:daily_financial_report')
            
            # Capturer la sortie de la commande
            out = StringIO()
            
            # Appeler la commande de génération
            call_command(
                'generate_daily_financial_report',
                date=date_str,
                force=force,
                stdout=out
            )
            
            messages.success(
                request, 
                f'Rapport généré avec succès pour le {report_date.strftime("%d/%m/%Y")}.'
            )
            
            # Rediriger vers le rapport généré
            return redirect(f"{request.path.replace('/generate/', '/')}?date={date_str}")
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération: {str(e)}')
            return redirect('finance:daily_financial_report')
    
    # GET: rediriger vers la vue principale
    return redirect('finance:daily_financial_report')


@staff_required
def daily_financial_report_export_pdf(request, date):
    """
    Exporte le rapport en PDF
    TODO: Implémenter avec WeasyPrint
    """
    from .models import DailyFinancialReport
    from datetime import datetime
    
    try:
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        report = get_object_or_404(DailyFinancialReport, report_date=report_date)
        
        # Pour l'instant, retourner un message
        messages.info(request, 'Export PDF en cours de développement.')
        return redirect('finance:daily_financial_report')
        
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('finance:daily_financial_report')


@staff_required
def daily_financial_report_export_excel(request, date):
    """
    Exporte le rapport en Excel
    TODO: Implémenter avec openpyxl
    """
    from .models import DailyFinancialReport
    from datetime import datetime
    
    try:
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        report = get_object_or_404(DailyFinancialReport, report_date=report_date)
        
        # Pour l'instant, retourner un message
        messages.info(request, 'Export Excel en cours de développement.')
        return redirect('finance:daily_financial_report')
        
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('finance:daily_financial_report')
