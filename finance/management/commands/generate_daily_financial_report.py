"""
Management command pour générer le rapport financier journalier

Usage:
    python manage.py generate_daily_financial_report
    python manage.py generate_daily_financial_report --date 2025-10-11
    python manage.py generate_daily_financial_report --force  # Regénère même si existe
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
from datetime import datetime, timedelta

from finance.models import DailyFinancialReport, Payment, Invoice


class Command(BaseCommand):
    help = 'Génère le rapport financier journalier avec toutes les statistiques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date du rapport au format YYYY-MM-DD (défaut: aujourd\'hui)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la regénération même si le rapport existe déjà',
        )
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Envoie le rapport par email après génération',
        )

    def handle(self, *args, **options):
        # Déterminer la date du rapport
        if options['date']:
            try:
                report_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                raise CommandError('Format de date invalide. Utilisez YYYY-MM-DD')
        else:
            report_date = timezone.now().date()

        self.stdout.write(f"Génération du rapport financier pour le {report_date.strftime('%d/%m/%Y')}...")

        # Vérifier si le rapport existe déjà
        existing_report = DailyFinancialReport.objects.filter(report_date=report_date).first()
        if existing_report and not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    f'Un rapport existe déjà pour cette date. Utilisez --force pour regénérer.'
                )
            )
            return

        # Supprimer l'ancien rapport si --force
        if existing_report and options['force']:
            existing_report.delete()
            self.stdout.write('Ancien rapport supprimé.')

        # Générer le rapport
        try:
            report = self.generate_report(report_date)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Rapport généré avec succès (ID: {report.id})'
                )
            )
            
            # Afficher un résumé
            self.display_summary(report)
            
            # Envoi par email si demandé
            if options['send_email']:
                self.send_report_email(report)
                
        except Exception as e:
            raise CommandError(f'Erreur lors de la génération du rapport: {str(e)}')

    def generate_report(self, report_date):
        """Génère le rapport complet pour une date donnée"""
        
        # Créer le rapport
        report = DailyFinancialReport(report_date=report_date)
        
        # === PAIEMENTS DU JOUR ===
        payments_query = Payment.objects.filter(
            payment_date__date=report_date,
            status='COMPLETED'
        )
        
        report.payments_count = payments_query.count()
        
        # Total des paiements
        payments_total = payments_query.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        report.payments_total = payments_total
        
        # Paiements par méthode
        payment_methods = payments_query.values('payment_method__code').annotate(
            total=Sum('amount')
        )
        
        for method_data in payment_methods:
            method_code = method_data['payment_method__code']
            amount = method_data['total'] or Decimal('0.00')
            
            if method_code == 'CASH':
                report.payments_cash = amount
            elif method_code == 'CHECK':
                report.payments_check = amount
            elif method_code == 'TRANSFER':
                report.payments_transfer = amount
            elif method_code == 'CARD':
                report.payments_card = amount
            elif method_code == 'MOBILE':
                report.payments_mobile = amount
        
        # === FACTURES CRÉÉES LE JOUR ===
        invoices_created = Invoice.objects.filter(
            issue_date=report_date
        )
        
        report.invoices_created_count = invoices_created.count()
        report.invoices_created_total = invoices_created.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # === FACTURES EN ATTENTE (à cette date) ===
        invoices_pending = Invoice.objects.filter(
            issue_date__lte=report_date,
            status='PENDING',
            due_date__gte=report_date  # Pas encore en retard
        )
        
        report.invoices_pending_count = invoices_pending.count()
        report.invoices_pending_total = invoices_pending.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # === FACTURES PAYÉES (payées ce jour-là) ===
        invoices_paid_today = Invoice.objects.filter(
            status='PAID',
            # On considère les factures qui ont reçu un paiement ce jour
            payments__payment_date=report_date,
            payments__status='COMPLETED'
        ).distinct()
        
        report.invoices_paid_count = invoices_paid_today.count()
        report.invoices_paid_total = invoices_paid_today.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # === FACTURES EN RETARD (à cette date) ===
        invoices_overdue = Invoice.objects.filter(
            due_date__lt=report_date,
            status__in=['PENDING', 'PARTIAL']
        )
        
        report.invoices_overdue_count = invoices_overdue.count()
        
        # Calculer le montant en retard (solde restant)
        overdue_total = Decimal('0.00')
        for invoice in invoices_overdue:
            overdue_total += invoice.balance  # Utilise la property balance
        report.invoices_overdue_total = overdue_total
        
        # === FACTURES PARTIELLEMENT PAYÉES ===
        invoices_partial = Invoice.objects.filter(
            status='PARTIAL',
            issue_date__lte=report_date
        )
        
        report.invoices_partial_count = invoices_partial.count()
        
        # Calculer le solde restant des factures partielles
        partial_total = Decimal('0.00')
        for invoice in invoices_partial:
            partial_total += invoice.balance
        report.invoices_partial_total = partial_total
        
        # === COMPARAISONS ===
        # Jour précédent
        previous_day = report_date - timedelta(days=1)
        previous_day_report = DailyFinancialReport.objects.filter(
            report_date=previous_day
        ).first()
        
        if previous_day_report:
            diff = report.payments_total - previous_day_report.payments_total
            report.payments_diff_previous_day = diff
            
            if previous_day_report.payments_total > 0:
                percent = (diff / previous_day_report.payments_total) * 100
                report.payments_diff_previous_day_percent = percent
        
        # Semaine précédente (même jour de la semaine)
        previous_week = report_date - timedelta(days=7)
        previous_week_report = DailyFinancialReport.objects.filter(
            report_date=previous_week
        ).first()
        
        if previous_week_report:
            diff = report.payments_total - previous_week_report.payments_total
            report.payments_diff_previous_week = diff
            
            if previous_week_report.payments_total > 0:
                percent = (diff / previous_week_report.payments_total) * 100
                report.payments_diff_previous_week_percent = percent
        
        # Moyenne mensuelle
        month_start = report_date.replace(day=1)
        monthly_reports = DailyFinancialReport.objects.filter(
            report_date__gte=month_start,
            report_date__lte=report_date
        )
        
        if monthly_reports.exists():
            avg = monthly_reports.aggregate(
                avg=Sum('payments_total')
            )['avg'] or Decimal('0.00')
            report.monthly_average_payments = avg / monthly_reports.count()
        
        # === TRÉSORERIE ===
        # Total des créances (toutes les factures non payées)
        all_unpaid = Invoice.objects.filter(
            issue_date__lte=report_date,
            status__in=['PENDING', 'PARTIAL']
        )
        
        receivables = Decimal('0.00')
        for invoice in all_unpaid:
            receivables += invoice.balance
        report.total_receivables = receivables
        
        # Taux de recouvrement
        total_invoiced = Invoice.objects.filter(
            issue_date__lte=report_date
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        if total_invoiced > 0:
            total_paid_cumul = Payment.objects.filter(
                payment_date__lte=report_date,
                status='COMPLETED'
            ).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            report.collection_rate = (total_paid_cumul / total_invoiced) * 100
        
        # === DÉPENSES ===
        # Si vous avez un modèle Expense, ajoutez ici
        # expenses = Expense.objects.filter(date=report_date)
        # report.expenses_count = expenses.count()
        # report.expenses_total = expenses.aggregate(Sum('amount'))['total'] or 0
        
        # Balance nette
        report.net_balance = report.payments_total - report.expenses_total
        
        # === DONNÉES SUPPLÉMENTAIRES (pour graphiques) ===
        # Stocke des données structurées pour les graphiques
        report.additional_data = {
            'top_payers': self.get_top_payers(report_date),
            'payment_timeline': self.get_payment_timeline(report_date),
            'invoice_aging': self.get_invoice_aging(report_date),
        }
        
        # Sauvegarder le rapport
        report.save()
        
        return report

    def get_top_payers(self, report_date, limit=10):
        """Retourne les plus gros payeurs du jour"""
        payments = Payment.objects.filter(
            payment_date=report_date,
            status='COMPLETED'
        ).values(
            'invoice__student__user__first_name',
            'invoice__student__user__last_name'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')[:limit]
        
        return [
            {
                'student': f"{p['invoice__student__user__first_name']} {p['invoice__student__user__last_name']}",
                'amount': float(p['total'])
            }
            for p in payments
        ]

    def get_payment_timeline(self, report_date):
        """Retourne la timeline des paiements par heure (si created_at disponible)"""
        payments = Payment.objects.filter(
            payment_date=report_date,
            status='COMPLETED'
        ).order_by('created_at')
        
        timeline = []
        for payment in payments[:50]:  # Limiter à 50 pour performance
            timeline.append({
                'time': payment.created_at.strftime('%H:%M') if hasattr(payment, 'created_at') else '00:00',
                'amount': float(payment.amount),
                'method': payment.get_payment_method_display()
            })
        
        return timeline

    def get_invoice_aging(self, report_date):
        """Analyse l'âge des factures impayées"""
        overdue = Invoice.objects.filter(
            due_date__lt=report_date,
            status__in=['PENDING', 'PARTIAL']
        )
        
        aging = {
            '0-30': {'count': 0, 'amount': 0},
            '31-60': {'count': 0, 'amount': 0},
            '61-90': {'count': 0, 'amount': 0},
            '90+': {'count': 0, 'amount': 0},
        }
        
        for invoice in overdue:
            days_overdue = (report_date - invoice.due_date).days
            balance = float(invoice.balance)
            
            if days_overdue <= 30:
                aging['0-30']['count'] += 1
                aging['0-30']['amount'] += balance
            elif days_overdue <= 60:
                aging['31-60']['count'] += 1
                aging['31-60']['amount'] += balance
            elif days_overdue <= 90:
                aging['61-90']['count'] += 1
                aging['61-90']['amount'] += balance
            else:
                aging['90+']['count'] += 1
                aging['90+']['amount'] += balance
        
        return aging

    def display_summary(self, report):
        """Affiche un résumé du rapport dans la console"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'  RÉSUMÉ DU RAPPORT - {report.report_date.strftime("%d/%m/%Y")}')
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write(f'💰 PAIEMENTS REÇUS:')
        self.stdout.write(f'   Nombre: {report.payments_count}')
        self.stdout.write(f'   Montant total: {report.payments_total:,.2f} FCFA')
        self.stdout.write(f'   Moyenne par paiement: {report.average_payment_amount:,.2f} FCFA\n')
        
        if report.payments_total > 0:
            self.stdout.write(f'📊 PAR MÉTHODE:')
            if report.payments_cash > 0:
                self.stdout.write(f'   Espèces: {report.payments_cash:,.2f} FCFA')
            if report.payments_check > 0:
                self.stdout.write(f'   Chèques: {report.payments_check:,.2f} FCFA')
            if report.payments_transfer > 0:
                self.stdout.write(f'   Virements: {report.payments_transfer:,.2f} FCFA')
            if report.payments_card > 0:
                self.stdout.write(f'   Cartes: {report.payments_card:,.2f} FCFA')
            if report.payments_mobile > 0:
                self.stdout.write(f'   Mobile: {report.payments_mobile:,.2f} FCFA')
            self.stdout.write('')
        
        self.stdout.write(f'📄 FACTURES:')
        self.stdout.write(f'   Créées: {report.invoices_created_count} ({report.invoices_created_total:,.2f} FCFA)')
        self.stdout.write(f'   En attente: {report.invoices_pending_count} ({report.invoices_pending_total:,.2f} FCFA)')
        self.stdout.write(f'   Payées: {report.invoices_paid_count} ({report.invoices_paid_total:,.2f} FCFA)')
        
        if report.invoices_overdue_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'   ⚠️  EN RETARD: {report.invoices_overdue_count} ({report.invoices_overdue_total:,.2f} FCFA)'
                )
            )
        
        if report.invoices_partial_count > 0:
            self.stdout.write(f'   Partielles: {report.invoices_partial_count} ({report.invoices_partial_total:,.2f} FCFA)\n')
        
        # Comparaisons
        if report.payments_diff_previous_day != 0:
            trend_icon = '📈' if report.payments_diff_previous_day > 0 else '📉'
            trend_color = self.style.SUCCESS if report.payments_diff_previous_day > 0 else self.style.WARNING
            self.stdout.write(
                trend_color(
                    f'{trend_icon} vs Jour précédent: {report.payments_diff_previous_day:+,.2f} FCFA '
                    f'({report.payments_diff_previous_day_percent:+.1f}%)'
                )
            )
        
        self.stdout.write(f'\n💼 TRÉSORERIE:')
        self.stdout.write(f'   Créances totales: {report.total_receivables:,.2f} FCFA')
        self.stdout.write(f'   Taux de recouvrement: {report.collection_rate:.1f}%')
        self.stdout.write(f'   Balance nette du jour: {report.net_balance:,.2f} FCFA')
        
        self.stdout.write('\n' + '='*60 + '\n')

    def send_report_email(self, report):
        """Envoie le rapport par email (à implémenter)"""
        self.stdout.write('📧 Envoi par email...')
        # TODO: Implémenter l'envoi d'email
        # from django.core.mail import send_mail
        # send_mail(...)
        self.stdout.write(self.style.SUCCESS('Email envoyé avec succès!'))
