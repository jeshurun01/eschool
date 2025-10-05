"""
Vues spécialisées pour les étudiants
Module Academic - Student Views
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

from core.decorators.permissions import student_required
from accounts.models import Student
from academic.models import (
    Session, SessionAttendance, SessionDocument, 
    SessionAssignment, DailyAttendanceSummary,
    Timetable, Subject, ClassRoom, Document
)


@student_required
def student_sessions_view(request):
    """
    Vue pour afficher les sessions de l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    # Récupérer la classe via l'inscription active
    active_enrollment = student.enrollments.filter(is_active=True).first()
    current_class = active_enrollment.classroom if active_enrollment else None
    
    if not current_class:
        messages.warning(request, "Vous n'êtes inscrit dans aucune classe active.")
        return redirect('accounts:dashboard')
    
    # Filtrer par période si spécifiée
    period = request.GET.get('period', 'current_week')
    
    today = timezone.now().date()
    
    if period == 'current_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'current_month':
        start_date = today.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    elif period == 'last_week':
        end_date = today - timedelta(days=today.weekday() + 1)
        start_date = end_date - timedelta(days=6)
    else:  # all
        start_date = None
        end_date = None
    
    # Récupérer les matières de la classe de l'étudiant
    subjects = Subject.objects.filter(
        teacherassignment__classroom=current_class
    ).distinct().order_by('name')
    
    # Récupérer les sessions de la classe de l'étudiant
    sessions_query = Session.objects.filter(
        timetable__classroom=current_class
    ).select_related(
        'timetable__subject', 
        'timetable__teacher__user',
        'timetable__classroom',
        'period'
    ).prefetch_related('documents', 'assignments')
    
    if start_date and end_date:
        sessions_query = sessions_query.filter(date__range=[start_date, end_date])
    
    # Filtres de recherche
    search_query = request.GET.get('search', '')
    subject_filter = request.GET.get('subject', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        sessions_query = sessions_query.filter(
            Q(timetable__subject__name__icontains=search_query) |
            Q(timetable__teacher__user__first_name__icontains=search_query) |
            Q(timetable__teacher__user__last_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if subject_filter:
        sessions_query = sessions_query.filter(timetable__subject_id=subject_filter)
    
    if status_filter:
        if status_filter == 'upcoming':
            sessions_query = sessions_query.filter(date__gte=today, status='SCHEDULED')
        elif status_filter == 'completed':
            sessions_query = sessions_query.filter(status='COMPLETED')
        elif status_filter == 'in_progress':
            sessions_query = sessions_query.filter(status='IN_PROGRESS')
    
    sessions = sessions_query.order_by('-date', 'timetable__start_time')
    
    # Pagination
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prochaine session
    next_session = sessions_query.filter(
        date__gte=today, 
        status='SCHEDULED'
    ).order_by('date', 'timetable__start_time').first()
    
    # Statistiques rapides
    stats = {
        'total_sessions': sessions.count(),
        'completed_sessions': sessions.filter(status='COMPLETED').count(),
        'upcoming_sessions': sessions.filter(date__gte=today, status='SCHEDULED').count(),
        'sessions_this_week': sessions.filter(
            date__gte=today - timedelta(days=today.weekday()),
            date__lte=today + timedelta(days=6-today.weekday())
        ).count(),
        'attendance_rate': 85,  # TODO: Calculer le vrai taux
        'pending_assignments': 0,  # TODO: Calculer les vrais devoirs
    }
    
    context = {
        'student': student,
        'current_class': current_class,
        'page_obj': page_obj,
        'sessions': page_obj.object_list,
        'subjects': subjects,
        'stats': stats,
        'next_session': next_session,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
    }
    
    return render(request, 'academic/student/sessions_list.html', context)


@student_required
def student_session_detail(request, session_id):
    """
    Vue détaillée d'une session pour l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    session = get_object_or_404(
        Session.objects.select_related(
            'timetable__subject',
            'timetable__teacher__user',
            'timetable__classroom',
            'period'
        ).prefetch_related(
            'documents',
            'assignments',
            'attendances'
        ),
        id=session_id,
        timetable__classroom=student.current_class
    )
    
    # Récupérer la présence de l'étudiant pour cette session
    try:
        attendance = SessionAttendance.objects.get(
            session=session,
            student=student
        )
    except SessionAttendance.DoesNotExist:
        attendance = None
    
    # Documents de la session
    documents = session.documents.select_related('document').filter(
        document__access_level__in=['ALL', 'STUDENTS']
    ).order_by('-shared_at')
    
    # Devoirs de la session
    assignments = session.assignments.filter(
        is_published=True
    ).order_by('due_date')
    
    context = {
        'student': student,
        'session': session,
        'attendance': attendance,
        'documents': documents,
        'assignments': assignments,
    }
    
    return render(request, 'academic/student/session_detail.html', context)


@student_required
def student_attendance_overview(request):
    """
    Vue d'ensemble des présences de l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    # Période sélectionnée
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
    else:  # all
        start_date = None
        end_date = None
    
    # Récupérer les résumés de présence
    summaries_query = DailyAttendanceSummary.objects.filter(
        student=student
    ).select_related('student__user')
    
    if start_date and end_date:
        summaries_query = summaries_query.filter(date__range=[start_date, end_date])
    
    summaries = summaries_query.order_by('-date')
    
    # Calcul des statistiques
    stats = summaries.aggregate(
        total_days=Count('id'),
        fully_present_days=Count('id', filter=Q(daily_status='FULLY_PRESENT')),
        partially_present_days=Count('id', filter=Q(daily_status='PARTIALLY_PRESENT')),
        mostly_absent_days=Count('id', filter=Q(daily_status='MOSTLY_ABSENT')),
        fully_absent_days=Count('id', filter=Q(daily_status='FULLY_ABSENT')),
        total_sessions=Sum('total_sessions'),
        present_sessions=Sum('present_sessions'),
        absent_sessions=Sum('absent_sessions'),
        late_sessions=Sum('late_sessions'),
    )
    
    # Calcul des pourcentages
    if stats['total_sessions'] and stats['total_sessions'] > 0:
        effective_present = (stats['present_sessions'] or 0) + (stats['late_sessions'] or 0)
        stats['attendance_rate'] = round(effective_present / stats['total_sessions'] * 100, 1)
        stats['absence_rate'] = round((stats['absent_sessions'] or 0) / stats['total_sessions'] * 100, 1)
    else:
        stats['attendance_rate'] = 0
        stats['absence_rate'] = 0
    
    # Présences par matière
    subject_attendance = SessionAttendance.objects.filter(
        student=student
    ).values(
        'session__timetable__subject__name'
    ).annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT')),
        late=Count('id', filter=Q(status='LATE')),
        absent=Count('id', filter=Q(status='ABSENT'))
    ).order_by('session__timetable__subject__name')
    
    if start_date and end_date:
        subject_attendance = subject_attendance.filter(
            session__date__range=[start_date, end_date]
        )
    
    # Pagination des résumés
    paginator = Paginator(summaries, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student': student,
        'page_obj': page_obj,
        'summaries': page_obj.object_list,
        'stats': stats,
        'subject_attendance': subject_attendance,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
    }
    
    return render(request, 'academic/student/attendance_overview.html', context)


@student_required
def student_timetable_view(request):
    """
    Vue de l'emploi du temps de l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    if not student.current_class:
        messages.warning(request, "Vous n'êtes affecté à aucune classe actuellement.")
        return redirect('accounts:student_dashboard')
    
    # Récupérer l'emploi du temps de la classe
    timetables = Timetable.objects.filter(
        classroom=student.current_class
    ).select_related(
        'subject',
        'teacher__user',
        'classroom'
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
    
    # Statistiques
    stats = {
        'total_subjects': timetables.values('subject').distinct().count(),
        'total_hours_per_week': sum(
            ((datetime.combine(timezone.now().date(), t.end_time) - 
              datetime.combine(timezone.now().date(), t.start_time)).seconds / 3600)
            for t in timetables
        ),
        'total_teachers': timetables.values('teacher').distinct().count(),
    }
    
    context = {
        'student': student,
        'days_schedule': days_schedule,
        'day_names': day_names,
        'stats': stats,
        'today': timezone.now().date(),
    }
    
    return render(request, 'academic/student/timetable.html', context)


@student_required
def student_documents_view(request):
    """
    Vue des documents accessibles à l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    # Filtres
    subject_id = request.GET.get('subject')
    document_type = request.GET.get('type')
    search = request.GET.get('search')
    
    # Documents des sessions de la classe de l'étudiant
    documents = SessionDocument.objects.filter(
        session__timetable__classroom=student.current_class,
        document__is_public=True
    ).select_related(
        'document',
        'session__timetable__subject',
        'session__timetable__teacher__user',
        'shared_by'
    ).order_by('-shared_at')
    
    # Appliquer les filtres
    if subject_id:
        documents = documents.filter(session__timetable__subject_id=subject_id)
    
    if document_type:
        documents = documents.filter(document__document_type=document_type)
    
    if search:
        documents = documents.filter(
            Q(document__title__icontains=search) |
            Q(document__description__icontains=search) |
            Q(session__lesson_title__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Options pour les filtres
    subjects = Subject.objects.filter(
        timetable__classroom=student.current_class
    ).distinct().order_by('name')
    
    document_types = Document.DOCUMENT_TYPE_CHOICES
    
    context = {
        'student': student,
        'page_obj': page_obj,
        'documents': page_obj.object_list,
        'subjects': subjects,
        'document_types': document_types,
        'current_subject': subject_id,
        'current_type': document_type,
        'search': search,
    }
    
    return render(request, 'academic/student/documents.html', context)


@student_required  
def student_assignments_view(request):
    """
    Vue des devoirs de l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    # Récupérer la classe via l'inscription active
    active_enrollment = student.enrollments.filter(is_active=True).first()
    current_class = active_enrollment.classroom if active_enrollment else None
    
    if not current_class:
        messages.warning(request, "Vous n'êtes inscrit dans aucune classe active.")
        return redirect('accounts:dashboard')
    
    # Filtres
    status = request.GET.get('status', 'all')
    subject_id = request.GET.get('subject')
    search_query = request.GET.get('search', '')
    
    # Devoirs des sessions de la classe de l'étudiant
    assignments = SessionAssignment.objects.filter(
        session__timetable__classroom=current_class,
        is_published=True
    ).select_related(
        'session__timetable__subject',
        'session__timetable__teacher__user',
        'created_by'
    ).order_by('due_date', '-created_at')
    
    today = timezone.now().date()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Appliquer la recherche
    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(session__timetable__subject__name__icontains=search_query)
        )
    
    # Appliquer les filtres de statut
    if status == 'pending':
        assignments = assignments.filter(due_date__gte=today_start)
    elif status == 'overdue':
        assignments = assignments.filter(due_date__lt=today_start)
    elif status == 'this_week':
        week_end_date = today + timedelta(days=7)
        week_end = timezone.datetime.combine(week_end_date, timezone.datetime.max.time())
        week_end_datetime = timezone.make_aware(week_end) if timezone.is_naive(week_end) else week_end
        assignments = assignments.filter(due_date__range=[today_start, week_end_datetime])
    
    # Filtre par matière
    if subject_id:
        assignments = assignments.filter(session__timetable__subject_id=subject_id)
    
    # Pagination
    paginator = Paginator(assignments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculer les statuts des devoirs
    for assignment in page_obj.object_list:
        assignment_due_date = assignment.due_date.date() if hasattr(assignment.due_date, 'date') else assignment.due_date
        
        if assignment_due_date < today:
            assignment.status_class = 'overdue'
            assignment.status_text = 'En retard'
        elif assignment_due_date == today:
            assignment.status_class = 'due-today'
            assignment.status_text = 'Aujourd\'hui'
        elif assignment_due_date <= today + timedelta(days=3):
            assignment.status_class = 'due-soon'
            assignment.status_text = 'Bientôt'
        else:
            assignment.status_class = 'normal'
            assignment.status_text = 'À venir'
    
    # Options pour les filtres
    subjects = Subject.objects.filter(
        teacherassignment__classroom=current_class
    ).distinct().order_by('name')
    
    # Statistiques - convertir due_date en date pour comparaison
    from django.db.models import F
    from django.db.models.functions import Cast, TruncDate
    
    stats = {
        'total': assignments.count(),
        'pending': sum(1 for a in assignments if (a.due_date.date() if hasattr(a.due_date, 'date') else a.due_date) >= today),
        'overdue': sum(1 for a in assignments if (a.due_date.date() if hasattr(a.due_date, 'date') else a.due_date) < today),
        'this_week': sum(1 for a in assignments if today <= (a.due_date.date() if hasattr(a.due_date, 'date') else a.due_date) <= today + timedelta(days=7)),
    }
    
    context = {
        'student': student,
        'current_class': current_class,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'assignments': page_obj.object_list,
        'subjects': subjects,
        'current_subject': subject_id,
        'current_status': status,
        'stats': stats,
        'today': today,
    }
    
    return render(request, 'academic/student/assignments.html', context)


@student_required
def student_grades_view(request):
    """
    Vue des notes de l'étudiant
    """
    student = get_object_or_404(Student, user=request.user)
    
    # Cette vue sera étendue quand le système de notation sera implémenté
    # Pour l'instant, on affiche les informations de base
    
    context = {
        'student': student,
        'message': 'Le système de notation sera bientôt disponible.',
    }
    
    return render(request, 'academic/student/grades.html', context)