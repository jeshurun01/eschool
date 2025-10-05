"""
Vues spécialisées pour les parents
Module Academic - Parent Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from core.decorators.permissions import parent_required
from accounts.models import Parent, Student
from academic.models import (
    Session, SessionAttendance, SessionDocument, 
    SessionAssignment, DailyAttendanceSummary,
    Timetable, Subject, ClassRoom, Document
)


@parent_required
def parent_children_overview(request):
    """
    Vue d'ensemble des enfants pour le parent
    """
    parent = get_object_or_404(Parent, user=request.user)
    
    # Récupérer tous les enfants du parent
    children = parent.children.select_related(
        'user', 'current_class__level'
    ).order_by('user__first_name')
    
    # Période pour les statistiques
    period_days = int(request.GET.get('period', 30))
    start_date = timezone.now().date() - timedelta(days=period_days)
    
    # Préparer les données pour chaque enfant
    children_data = []
    for child in children:
        # Statistiques de présence
        attendance_summary = DailyAttendanceSummary.objects.filter(
            student=child,
            date__gte=start_date
        ).aggregate(
            total_days=Count('id'),
            avg_attendance=Avg('attendance_rate'),
            total_sessions=Sum('total_sessions'),
            attended_sessions=Sum('attended_sessions')
        )
        
        # Sessions récentes
        recent_sessions = Session.objects.filter(
            timetable__classroom=child.current_class,
            date__gte=start_date
        ).count() if child.current_class else 0
        
        # Devoirs en cours
        pending_assignments = SessionAssignment.objects.filter(
            session__timetable__classroom=child.current_class,
            is_published=True,
            due_date__gte=timezone.now()
        ).count() if child.current_class else 0
        
        # Devoirs en retard
        overdue_assignments = SessionAssignment.objects.filter(
            session__timetable__classroom=child.current_class,
            is_published=True,
            due_date__lt=timezone.now()
        ).count() if child.current_class else 0
        
        children_data.append({
            'child': child,
            'attendance_rate': round(attendance_summary['avg_attendance'] or 0, 1),
            'total_days': attendance_summary['total_days'] or 0,
            'recent_sessions': recent_sessions,
            'pending_assignments': pending_assignments,
            'overdue_assignments': overdue_assignments,
            'total_sessions': attendance_summary['total_sessions'] or 0,
            'attended_sessions': attendance_summary['attended_sessions'] or 0,
        })
    
    context = {
        'parent': parent,
        'children_data': children_data,
        'period_days': period_days,
        'start_date': start_date,
    }
    
    return render(request, 'academic/parent/children_overview.html', context)


@parent_required
def parent_child_detail(request, child_id):
    """
    Vue détaillée d'un enfant pour le parent
    """
    parent = get_object_or_404(Parent, user=request.user)
    
    # Vérifier que l'enfant appartient bien au parent
    child = get_object_or_404(
        Student.objects.select_related('user', 'current_class__level'),
        pk=child_id,
        parents=parent
    )
    
    # Onglet actif
    tab = request.GET.get('tab', 'attendance')
    
    # Période pour les données
    period = request.GET.get('period', 'current_month')
    today = timezone.now().date()
    
    if period == 'current_month':
        start_date = today.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    elif period == 'last_month':
        end_date = today.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif period == 'current_year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        start_date = today - timedelta(days=30)
        end_date = today
    
    context = {
        'parent': parent,
        'child': child,
        'tab': tab,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if tab == 'attendance':
        # Données de présence
        attendance_summaries = DailyAttendanceSummary.objects.filter(
            student=child,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        # Statistiques de présence
        attendance_stats = attendance_summaries.aggregate(
            total_days=Count('id'),
            avg_attendance=Avg('attendance_rate'),
            present_days=Count('id', filter=Q(status='PRESENT')),
            absent_days=Count('id', filter=Q(status='ABSENT')),
            late_days=Count('id', filter=Q(status='LATE')),
            excused_days=Count('id', filter=Q(status='EXCUSED'))
        )
        
        # Présences par matière
        if child.current_class:
            subject_attendance = SessionAttendance.objects.filter(
                student=child,
                session__date__range=[start_date, end_date]
            ).values(
                'session__timetable__subject__name',
                'session__timetable__subject__color'
            ).annotate(
                total=Count('id'),
                present=Count('id', filter=Q(status='PRESENT')),
                late=Count('id', filter=Q(status='LATE')),
                absent=Count('id', filter=Q(status='ABSENT'))
            ).order_by('session__timetable__subject__name')
        else:
            subject_attendance = []
        
        context.update({
            'attendance_summaries': attendance_summaries[:15],  # Limiter pour l'affichage
            'attendance_stats': attendance_stats,
            'subject_attendance': subject_attendance,
        })
    
    elif tab == 'sessions':
        # Sessions de l'enfant
        if child.current_class:
            sessions = Session.objects.filter(
                timetable__classroom=child.current_class,
                date__range=[start_date, end_date]
            ).select_related(
                'timetable__subject',
                'timetable__teacher__user'
            ).order_by('-date', 'timetable__start_time')
            
            # Ajouter les informations de présence
            session_data = []
            for session in sessions[:20]:  # Limiter pour l'affichage
                try:
                    attendance = SessionAttendance.objects.get(
                        session=session,
                        student=child
                    )
                except SessionAttendance.DoesNotExist:
                    attendance = None
                
                session_data.append({
                    'session': session,
                    'attendance': attendance
                })
        else:
            session_data = []
        
        context.update({
            'session_data': session_data,
        })
    
    elif tab == 'assignments':
        # Devoirs de l'enfant
        if child.current_class:
            assignments = SessionAssignment.objects.filter(
                session__timetable__classroom=child.current_class,
                is_published=True,
                created_at__date__range=[start_date, end_date]
            ).select_related(
                'session__timetable__subject',
                'session__timetable__teacher__user'
            ).order_by('-due_date')
            
            # Séparer par statut
            pending_assignments = assignments.filter(due_date__gte=timezone.now())
            overdue_assignments = assignments.filter(due_date__lt=timezone.now())
        else:
            pending_assignments = []
            overdue_assignments = []
        
        context.update({
            'pending_assignments': pending_assignments[:10],
            'overdue_assignments': overdue_assignments[:10],
        })
    
    elif tab == 'documents':
        # Documents accessibles
        if child.current_class:
            documents = SessionDocument.objects.filter(
                session__timetable__classroom=child.current_class,
                document__is_public=True,
                shared_at__date__range=[start_date, end_date]
            ).select_related(
                'document',
                'session__timetable__subject'
            ).order_by('-shared_at')
        else:
            documents = []
        
        context.update({
            'documents': documents[:15],
        })
    
    return render(request, 'academic/parent/child_detail.html', context)


@parent_required
def parent_child_timetable(request, child_id):
    """
    Vue de l'emploi du temps d'un enfant
    """
    parent = get_object_or_404(Parent, user=request.user)
    
    # Vérifier que l'enfant appartient bien au parent
    child = get_object_or_404(
        Student.objects.select_related('user', 'current_class'),
        pk=child_id,
        parents=parent
    )
    
    if not child.current_class:
        messages.warning(request, f"{child.user.first_name} n'est affecté à aucune classe actuellement.")
        return redirect('academic:parent_children_overview')
    
    # Récupérer l'emploi du temps de la classe
    timetables = Timetable.objects.filter(
        classroom=child.current_class
    ).select_related(
        'subject',
        'teacher__user'
    ).order_by('weekday', 'start_time')
    
    # Organiser par jour de la semaine
    days_schedule = {
        1: [],  # Lundi
        2: [],  # Mardi
        3: [],  # Mercredi
        4: [],  # Jeudi
        5: [],  # Vendredi
        6: [],  # Samedi
        7: [],  # Dimanche
    }
    
    for timetable in timetables:
        days_schedule[timetable.weekday].append(timetable)
    
    # Noms des jours
    day_names = {
        1: 'Lundi',
        2: 'Mardi', 
        3: 'Mercredi',
        4: 'Jeudi',
        5: 'Vendredi',
        6: 'Samedi',
        7: 'Dimanche'
    }
    
    # Sessions d'aujourd'hui
    today = timezone.now().date()
    today_sessions = Session.objects.filter(
        timetable__classroom=child.current_class,
        date=today
    ).select_related(
        'timetable__subject',
        'timetable__teacher__user'
    ).order_by('timetable__start_time')
    
    # Ajouter les informations de présence pour les sessions d'aujourd'hui
    today_session_data = []
    for session in today_sessions:
        try:
            attendance = SessionAttendance.objects.get(
                session=session,
                student=child
            )
        except SessionAttendance.DoesNotExist:
            attendance = None
        
        today_session_data.append({
            'session': session,
            'attendance': attendance
        })
    
    context = {
        'parent': parent,
        'child': child,
        'days_schedule': days_schedule,
        'day_names': day_names,
        'today_session_data': today_session_data,
        'today': today,
    }
    
    return render(request, 'academic/parent/child_timetable.html', context)


@parent_required
def parent_communications_view(request):
    """
    Vue des communications pour le parent
    """
    parent = get_object_or_404(Parent, user=request.user)
    
    # Cette vue sera étendue quand le système de communication sera implémenté
    # Pour l'instant, on affiche les informations de base
    
    # Messages récents (placeholder)
    messages_data = []
    
    # Notifications importantes
    notifications = []
    
    # Événements à venir
    upcoming_events = []
    
    context = {
        'parent': parent,
        'messages_data': messages_data,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
        'message': 'Le système de communication sera bientôt disponible.',
    }
    
    return render(request, 'academic/parent/communications.html', context)


@parent_required
def parent_child_sessions_ajax(request, child_id):
    """
    Vue AJAX pour récupérer les sessions d'un enfant
    """
    parent = get_object_or_404(Parent, user=request.user)
    
    # Vérifier que l'enfant appartient bien au parent
    child = get_object_or_404(
        Student,
        pk=child_id,
        parents=parent
    )
    
    if not child.current_class:
        return JsonResponse({'error': 'Enfant non affecté à une classe'}, status=400)
    
    # Paramètres de date
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Format de date invalide'}, status=400)
    else:
        date = timezone.now().date()
    
    # Récupérer les sessions du jour
    sessions = Session.objects.filter(
        timetable__classroom=child.current_class,
        date=date
    ).select_related(
        'timetable__subject',
        'timetable__teacher__user'
    ).order_by('timetable__start_time')
    
    # Préparer les données
    sessions_data = []
    for session in sessions:
        try:
            attendance = SessionAttendance.objects.get(
                session=session,
                student=child
            )
            attendance_data = {
                'status': attendance.status,
                'status_display': attendance.get_status_display(),
                'arrival_time': attendance.arrival_time.strftime('%H:%M') if attendance.arrival_time else None,
                'notes': attendance.notes
            }
        except SessionAttendance.DoesNotExist:
            attendance_data = None
        
        sessions_data.append({
            'id': session.pk,
            'subject': session.timetable.subject.name,
            'teacher': session.timetable.teacher.user.get_full_name(),
            'start_time': session.timetable.start_time.strftime('%H:%M'),
            'end_time': session.timetable.end_time.strftime('%H:%M'),
            'room': session.timetable.room or '',
            'status': session.status,
            'status_display': session.get_status_display(),
            'lesson_title': session.lesson_title or '',
            'attendance': attendance_data,
        })
    
    return JsonResponse({
        'sessions': sessions_data,
        'child_name': child.user.get_full_name(),
        'date': date.strftime('%d/%m/%Y')
    })


@parent_required
def parent_dashboard_summary(request):
    """
    Vue résumé du tableau de bord parent (pour inclusion AJAX)
    """
    parent = get_object_or_404(Parent, user=request.user)
    
    # Résumé pour tous les enfants
    children = parent.children.select_related('user', 'current_class')
    
    summary_data = {
        'total_children': children.count(),
        'children_with_classes': children.filter(current_class__isnull=False).count(),
        'total_pending_assignments': 0,
        'total_overdue_assignments': 0,
        'children_summaries': []
    }
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    for child in children:
        if child.current_class:
            # Devoirs en cours et en retard
            pending = SessionAssignment.objects.filter(
                session__timetable__classroom=child.current_class,
                is_published=True,
                due_date__gte=timezone.now()
            ).count()
            
            overdue = SessionAssignment.objects.filter(
                session__timetable__classroom=child.current_class,
                is_published=True,
                due_date__lt=timezone.now()
            ).count()
            
            # Présence de cette semaine
            week_attendance = DailyAttendanceSummary.objects.filter(
                student=child,
                date__gte=week_start
            ).aggregate(
                avg_rate=Avg('attendance_rate')
            )
            
            summary_data['total_pending_assignments'] += pending
            summary_data['total_overdue_assignments'] += overdue
            
            summary_data['children_summaries'].append({
                'child': {
                    'id': child.pk,
                    'name': child.user.get_full_name(),
                    'class': child.current_class.name if child.current_class else None,
                },
                'pending_assignments': pending,
                'overdue_assignments': overdue,
                'week_attendance_rate': round(week_attendance['avg_rate'] or 0, 1),
            })
        else:
            summary_data['children_summaries'].append({
                'child': {
                    'id': child.pk,
                    'name': child.user.get_full_name(),
                    'class': None,
                },
                'pending_assignments': 0,
                'overdue_assignments': 0,
                'week_attendance_rate': 0,
            })
    
    return JsonResponse(summary_data)