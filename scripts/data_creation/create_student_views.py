#!/usr/bin/env python3
"""
Amélioration de l'interface Élève - Nouvelles vues
"""

import os
import sys
import django

# Configuration de Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta

from accounts.models import Student
from academic.models import Grade, Subject, Attendance, ClassRoom
from finance.models import Invoice, Payment

def create_student_views():
    """Créer les nouvelles vues pour les élèves"""
    
    student_views_code = '''
# Nouvelles vues spéciales pour les élèves

@login_required
def student_grades_detail(request):
    """Vue détaillée des notes par matière pour l'élève"""
    if request.user.role != 'STUDENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Profil étudiant non trouvé.')
        return redirect('accounts:dashboard')
    
    # Récupération des notes par matière
    grades_by_subject = {}
    subjects = Subject.objects.filter(grades__student=student).distinct()
    
    for subject in subjects:
        subject_grades = Grade.objects.filter(
            student=student, 
            subject=subject
        ).order_by('-created_at')
        
        # Calculs statistiques
        avg_score = subject_grades.aggregate(avg=Avg('score'))['avg'] or 0
        best_score = subject_grades.order_by('-score').first()
        recent_trend = subject_grades[:3]
        
        grades_by_subject[subject] = {
            'grades': subject_grades,
            'average': round(avg_score, 2),
            'percentage': round((avg_score / 20) * 100, 1),
            'best_score': best_score.score if best_score else 0,
            'total_evaluations': subject_grades.count(),
            'recent_trend': recent_trend,
            'improvement': calculate_improvement(recent_trend) if len(recent_trend) >= 2 else 0
        }
    
    # Moyenne générale
    all_grades = Grade.objects.filter(student=student)
    general_average = all_grades.aggregate(avg=Avg('score'))['avg'] or 0
    
    context = {
        'student': student,
        'grades_by_subject': grades_by_subject,
        'general_average': round(general_average, 2),
        'general_percentage': round((general_average / 20) * 100, 1),
        'total_subjects': subjects.count(),
        'total_evaluations': all_grades.count(),
    }
    
    return render(request, 'accounts/student_grades_detail.html', context)


@login_required  
def student_attendance_detail(request):
    """Vue détaillée des présences pour l'élève"""
    if request.user.role != 'STUDENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Profil étudiant non trouvé.')
        return redirect('accounts:dashboard')
    
    # Filtrage par période
    period = request.GET.get('period', 'month')
    today = date.today()
    
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'semester':
        start_date = today - timedelta(days=120)
    else:
        start_date = today - timedelta(days=30)
    
    # Récupération des présences
    attendances = Attendance.objects.filter(
        student=student,
        date__gte=start_date
    ).order_by('-date')
    
    # Statistiques
    total_days = attendances.count()
    present_days = attendances.filter(status='PRESENT').count()
    absent_days = attendances.filter(status='ABSENT').count()
    late_days = attendances.filter(status='LATE').count()
    
    attendance_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0
    
    # Présences par matière
    attendance_by_subject = {}
    subjects = Subject.objects.filter(attendances__student=student).distinct()
    
    for subject in subjects:
        subject_attendances = attendances.filter(subject=subject)
        subject_present = subject_attendances.filter(status='PRESENT').count()
        subject_total = subject_attendances.count()
        subject_rate = round((subject_present / subject_total * 100), 1) if subject_total > 0 else 0
        
        attendance_by_subject[subject] = {
            'total': subject_total,
            'present': subject_present,
            'absent': subject_attendances.filter(status='ABSENT').count(),
            'late': subject_attendances.filter(status='LATE').count(),
            'rate': subject_rate
        }
    
    # Tendance hebdomadaire
    weekly_trend = []
    for i in range(7):
        day_date = today - timedelta(days=i)
        day_attendance = attendances.filter(date=day_date).first()
        weekly_trend.append({
            'date': day_date,
            'status': day_attendance.status if day_attendance else 'NO_CLASS',
            'subject': day_attendance.subject.name if day_attendance else None
        })
    
    context = {
        'student': student,
        'attendances': attendances[:20],  # 20 dernières
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'attendance_rate': attendance_rate,
        'attendance_by_subject': attendance_by_subject,
        'weekly_trend': reversed(weekly_trend),
        'period': period,
        'start_date': start_date,
    }
    
    return render(request, 'accounts/student_attendance_detail.html', context)


@login_required
def student_finance_detail(request):
    """Vue détaillée des finances pour l'élève"""
    if request.user.role != 'STUDENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Profil étudiant non trouvé.')
        return redirect('accounts:dashboard')
    
    # Factures par statut
    pending_invoices = Invoice.objects.filter(
        student=student,
        status__in=['DRAFT', 'SENT']
    ).order_by('-due_date')
    
    paid_invoices = Invoice.objects.filter(
        student=student,
        status='PAID'
    ).order_by('-issue_date')
    
    overdue_invoices = Invoice.objects.filter(
        student=student,
        status='OVERDUE'
    ).order_by('-due_date')
    
    # Statistiques financières
    total_pending = pending_invoices.aggregate(total=models.Sum('total_amount'))['total'] or 0
    total_paid = paid_invoices.aggregate(total=models.Sum('total_amount'))['total'] or 0
    total_overdue = overdue_invoices.aggregate(total=models.Sum('total_amount'))['total'] or 0
    
    # Historique des paiements
    recent_payments = Payment.objects.filter(
        invoice__student=student,
        status='COMPLETED'
    ).select_related('invoice').order_by('-payment_date')[:10]
    
    # Prochaines échéances
    upcoming_due = pending_invoices.filter(
        due_date__lte=date.today() + timedelta(days=30)
    ).order_by('due_date')[:5]
    
    context = {
        'student': student,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices[:10],  # 10 dernières
        'overdue_invoices': overdue_invoices,
        'total_pending': total_pending,
        'total_paid': total_paid,
        'total_overdue': total_overdue,
        'recent_payments': recent_payments,
        'upcoming_due': upcoming_due,
        'balance_status': 'danger' if total_overdue > 0 else 'warning' if total_pending > 0 else 'success'
    }
    
    return render(request, 'accounts/student_finance_detail.html', context)


@login_required
def student_academic_calendar(request):
    """Calendrier académique pour l'élève avec devoirs et examens"""
    if request.user.role != 'STUDENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Profil étudiant non trouvé.')
        return redirect('accounts:dashboard')
    
    # Simulation d'événements (à remplacer par vrai modèle Assignment/Exam)
    today = date.today()
    events = []
    
    # Événements simulés pour les 30 prochains jours
    for i in range(30):
        event_date = today + timedelta(days=i)
        
        # Simulation aléatoire d'événements
        if i % 7 == 1:  # Examens le lundi
            events.append({
                'date': event_date,
                'type': 'exam',
                'title': f'Examen Mathématiques',
                'description': 'Examen trimestriel',
                'subject': 'Mathématiques',
                'time': '08:00',
                'duration': 120,
                'importance': 'high'
            })
        
        if i % 5 == 3:  # Devoirs le jeudi
            events.append({
                'date': event_date,
                'type': 'assignment',
                'title': f'Devoir Français',
                'description': 'Rédaction à rendre',
                'subject': 'Français',
                'time': '14:00',
                'duration': 60,
                'importance': 'medium'
            })
    
    # Grouper par date
    events_by_date = {}
    for event in events:
        date_str = event['date'].strftime('%Y-%m-%d')
        if date_str not in events_by_date:
            events_by_date[date_str] = []
        events_by_date[date_str].append(event)
    
    context = {
        'student': student,
        'events': events,
        'events_by_date': events_by_date,
        'current_month': today.strftime('%B %Y'),
        'today': today,
    }
    
    return render(request, 'accounts/student_calendar.html', context)


def calculate_improvement(grades_list):
    """Calcule l'amélioration entre les notes récentes"""
    if len(grades_list) < 2:
        return 0
    
    latest = grades_list[0].score
    previous = grades_list[1].score
    return latest - previous
'''
    
    return student_views_code

if __name__ == '__main__':
    print("🚀 Génération des nouvelles vues élève...")
    views_code = create_student_views()
    print("✅ Code généré pour les vues élève spécialisées")
    print("📝 À ajouter dans accounts/views.py")
    print("🔗 URLs à créer pour ces vues")
    print("🎨 Templates à créer pour chaque vue")
