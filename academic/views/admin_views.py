"""
Vues spécialisées pour l'administration
Module Academic - Admin Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import json
import csv

from core.decorators.permissions import admin_required
from accounts.models import Student, Teacher, Parent
from academic.models import (
    Session, SessionAttendance, SessionDocument, 
    SessionAssignment, DailyAttendanceSummary,
    Timetable, Subject, ClassRoom, Document,
    Period, AcademicYear, Level
)

User = get_user_model()


@admin_required
def admin_dashboard_overview(request):
    """
    Vue d'ensemble du tableau de bord administrateur
    """
    # Période pour les statistiques
    period_days = int(request.GET.get('period', 30))
    start_date = timezone.now().date() - timedelta(days=period_days)
    today = timezone.now().date()
    
    # Statistiques globales
    global_stats = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_parents': Parent.objects.count(),
        'total_classes': ClassRoom.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_sessions': Session.objects.count(),
    }
    
    # Statistiques de la période
    period_stats = {
        'recent_sessions': Session.objects.filter(date__gte=start_date).count(),
        'completed_sessions': Session.objects.filter(
            date__gte=start_date, 
            status='COMPLETED'
        ).count(),
        'cancelled_sessions': Session.objects.filter(
            date__gte=start_date, 
            status='CANCELLED'
        ).count(),
    }
    
    # Statistiques de présence
    attendance_stats = DailyAttendanceSummary.objects.filter(
        date__gte=start_date
    ).aggregate(
        avg_attendance_rate=Avg('attendance_rate'),
        total_student_days=Count('id'),
        total_present=Count('id', filter=Q(daily_status='PRESENT')),
        total_absent=Count('id', filter=Q(daily_status='ABSENT')),
        total_late=Count('id', filter=Q(daily_status='LATE'))
    )
    
    # Sessions d'aujourd'hui
    today_sessions = Session.objects.filter(date=today).select_related(
        'timetable__subject',
        'timetable__classroom',
        'timetable__teacher__user'
    ).order_by('timetable__start_time')
    
    # Classes avec le plus d'absences récentes
    problematic_classes = ClassRoom.objects.annotate(
        avg_absence_rate=Avg(
            'students__daily_summaries__attendance_rate',
            filter=Q(students__daily_summaries__date__gte=start_date)
        )
    ).filter(avg_absence_rate__lt=80).order_by('avg_absence_rate')[:5]
    
    # Enseignants les plus actifs
    active_teachers = Teacher.objects.annotate(
        recent_sessions=Count(
            'timetable__sessions',
            filter=Q(timetable__sessions__date__gte=start_date)
        )
    ).order_by('-recent_sessions')[:5]
    
    # Documents récemment partagés
    recent_documents = SessionDocument.objects.filter(
        shared_at__gte=start_date
    ).select_related(
        'document',
        'session__timetable__subject',
        'shared_by'
    ).order_by('-shared_at')[:10]
    
    # Devoirs avec dates limites proches
    upcoming_deadlines = SessionAssignment.objects.filter(
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timedelta(days=7),
        is_published=True
    ).select_related(
        'session__timetable__subject',
        'session__timetable__classroom'
    ).order_by('due_date')[:10]
    
    context = {
        'global_stats': global_stats,
        'period_stats': period_stats,
        'attendance_stats': attendance_stats,
        'today_sessions': today_sessions,
        'problematic_classes': problematic_classes,
        'active_teachers': active_teachers,
        'recent_documents': recent_documents,
        'upcoming_deadlines': upcoming_deadlines,
        'period_days': period_days,
        'start_date': start_date,
        'today': today,
    }
    
    return render(request, 'academic/admin/dashboard.html', context)


@admin_required
def admin_sessions_management(request):
    """
    Gestion des sessions pour l'administration
    """
    # Filtres
    date_filter = request.GET.get('date', 'all')
    status_filter = request.GET.get('status', 'all')
    teacher_filter = request.GET.get('teacher')
    class_filter = request.GET.get('class')
    subject_filter = request.GET.get('subject')
    
    # Base queryset
    sessions = Session.objects.select_related(
        'timetable__subject',
        'timetable__classroom',
        'timetable__teacher__user',
        'period'
    ).prefetch_related(
        'attendances',
        'documents',
        'assignments'
    )
    
    today = timezone.now().date()
    
    # Appliquer les filtres de date
    if date_filter == 'today':
        sessions = sessions.filter(date=today)
    elif date_filter == 'this_week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        sessions = sessions.filter(date__range=[week_start, week_end])
    elif date_filter == 'this_month':
        month_start = today.replace(day=1)
        next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
        month_end = next_month - timedelta(days=1)
        sessions = sessions.filter(date__range=[month_start, month_end])
    
    # Autres filtres
    if status_filter != 'all':
        sessions = sessions.filter(status=status_filter)
    if teacher_filter:
        sessions = sessions.filter(timetable__teacher_id=teacher_filter)
    if class_filter:
        sessions = sessions.filter(timetable__classroom_id=class_filter)
    if subject_filter:
        sessions = sessions.filter(timetable__subject_id=subject_filter)
    
    sessions = sessions.order_by('-date', 'timetable__start_time')
    
    # Pagination
    paginator = Paginator(sessions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Options pour les filtres
    teachers = Teacher.objects.select_related('user').order_by('user__last_name')
    classes = ClassRoom.objects.order_by('level__order', 'name')
    subjects = Subject.objects.order_by('name')
    
    # Statistiques
    stats = {
        'total_sessions': sessions.count(),
        'completed': sessions.filter(status='COMPLETED').count(),
        'scheduled': sessions.filter(status='SCHEDULED').count(),
        'cancelled': sessions.filter(status='CANCELLED').count(),
        'in_progress': sessions.filter(status='IN_PROGRESS').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'sessions': page_obj.object_list,
        'teachers': teachers,
        'classes': classes,
        'subjects': subjects,
        'stats': stats,
        'date_filter': date_filter,
        'status_filter': status_filter,
        'teacher_filter': teacher_filter,
        'class_filter': class_filter,
        'subject_filter': subject_filter,
    }
    
    return render(request, 'academic/admin/sessions_management.html', context)


@admin_required
def admin_attendance_reports(request):
    """
    Rapports de présence pour l'administration
    """
    # Période pour le rapport
    period = request.GET.get('period', 'current_month')
    class_filter = request.GET.get('class')
    
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
    elif period == 'last_year':
        start_date = today.replace(year=today.year-1, month=1, day=1)
        end_date = today.replace(year=today.year-1, month=12, day=31)
    else:
        start_date = today - timedelta(days=30)
        end_date = today
    
    # Statistiques globales de présence
    global_attendance = DailyAttendanceSummary.objects.filter(
        date__range=[start_date, end_date]
    )
    
    if class_filter:
        global_attendance = global_attendance.filter(student__current_class_id=class_filter)
    
    global_stats = global_attendance.aggregate(
        avg_attendance_rate=Avg('attendance_rate'),
        total_student_days=Count('id'),
        total_present=Count('id', filter=Q(status='PRESENT')),
        total_absent=Count('id', filter=Q(status='ABSENT')),
        total_late=Count('id', filter=Q(status='LATE')),
        total_excused=Count('id', filter=Q(status='EXCUSED'))
    )
    
    # Statistiques par classe
    class_stats = ClassRoom.objects.annotate(
        avg_attendance_rate=Avg(
            'students__daily_summaries__attendance_rate',
            filter=Q(students__daily_summaries__date__range=[start_date, end_date])
        ),
        total_students=Count('students', distinct=True),
        total_sessions=Count(
            'timetables__sessions',
            filter=Q(timetables__sessions__date__range=[start_date, end_date])
        )
    ).filter(avg_attendance_rate__isnull=False).order_by('-avg_attendance_rate')
    
    if class_filter:
        class_stats = class_stats.filter(id=class_filter)
    
    # Statistiques par matière
    subject_stats = Subject.objects.annotate(
        avg_attendance_rate=Avg(
            'timetable__sessions__attendances__student__daily_summaries__attendance_rate',
            filter=Q(
                timetable__sessions__attendances__student__daily_summaries__date__range=[start_date, end_date]
            )
        ),
        total_sessions=Count(
            'timetable__sessions',
            filter=Q(timetable__sessions__date__range=[start_date, end_date])
        )
    ).filter(avg_attendance_rate__isnull=False).order_by('-avg_attendance_rate')
    
    # Étudiants avec le plus d'absences
    problematic_students = Student.objects.annotate(
        avg_attendance_rate=Avg(
            'daily_summaries__attendance_rate',
            filter=Q(daily_summaries__date__range=[start_date, end_date])
        ),
        total_absences=Count(
            'daily_summaries',
            filter=Q(
                daily_summaries__date__range=[start_date, end_date],
                daily_summaries__status='ABSENT'
            )
        )
    ).filter(
        avg_attendance_rate__lt=75,
        total_absences__gt=0
    ).select_related('user', 'current_class').order_by('avg_attendance_rate')[:20]
    
    # Options pour les filtres
    classes = ClassRoom.objects.order_by('level__order', 'name')
    
    context = {
        'global_stats': global_stats,
        'class_stats': class_stats,
        'subject_stats': subject_stats,
        'problematic_students': problematic_students,
        'classes': classes,
        'period': period,
        'class_filter': class_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'academic/admin/attendance_reports.html', context)


@admin_required
def admin_teachers_overview(request):
    """
    Vue d'ensemble des enseignants pour l'administration
    """
    # Statistiques de performance des enseignants
    teachers = Teacher.objects.select_related('user').prefetch_related(
        'subjects',
        'timetable_set__classroom'
    ).annotate(
        total_sessions=Count('timetable__sessions'),
        completed_sessions=Count(
            'timetable__sessions',
            filter=Q(timetable__sessions__status='COMPLETED')
        ),
        total_classes=Count('timetable__classroom', distinct=True),
        total_subjects=Count('subjects', distinct=True)
    ).order_by('user__last_name', 'user__first_name')
    
    # Enseignants les plus actifs (30 derniers jours)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    active_teachers = teachers.annotate(
        recent_sessions=Count(
            'timetable__sessions',
            filter=Q(timetable__sessions__date__gte=thirty_days_ago)
        )
    ).order_by('-recent_sessions')[:10]
    
    # Enseignants avec le plus de documents partagés
    document_sharers = teachers.annotate(
        shared_documents=Count('user__sessiondocument')
    ).order_by('-shared_documents')[:10]
    
    # Statistiques globales
    global_teacher_stats = {
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active_employee=True).count(),
        'head_teachers': teachers.filter(is_head_teacher=True).count(),
        'avg_sessions_per_teacher': teachers.aggregate(
            avg=Avg('total_sessions')
        )['avg'] or 0,
    }
    
    context = {
        'teachers': teachers,
        'active_teachers': active_teachers,
        'document_sharers': document_sharers,
        'global_teacher_stats': global_teacher_stats,
    }
    
    return render(request, 'academic/admin/teachers_overview.html', context)


@admin_required
def admin_students_overview(request):
    """
    Vue d'ensemble des étudiants pour l'administration
    """
    # Filtres
    class_filter = request.GET.get('class')
    status_filter = request.GET.get('status', 'all')
    search = request.GET.get('search')
    
    # Base queryset
    students = Student.objects.select_related(
        'user', 'current_class__level'
    ).prefetch_related('parents')
    
    # Appliquer les filtres
    if class_filter:
        students = students.filter(current_class_id=class_filter)
    
    if status_filter == 'graduated':
        students = students.filter(is_graduated=True)
    elif status_filter == 'active':
        students = students.filter(is_graduated=False, current_class__isnull=False)
    elif status_filter == 'unassigned':
        students = students.filter(current_class__isnull=True, is_graduated=False)
    
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(matricule__icontains=search)
        )
    
    students = students.order_by('user__last_name', 'user__first_name')
    
    # Pagination
    paginator = Paginator(students, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Ajouter les statistiques de présence pour chaque étudiant
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    for student in page_obj.object_list:
        attendance_stats = DailyAttendanceSummary.objects.filter(
            student=student,
            date__gte=thirty_days_ago
        ).aggregate(
            avg_rate=Avg('attendance_rate'),
            total_days=Count('id')
        )
        student.recent_attendance_rate = round(attendance_stats['avg_rate'] or 0, 1)
        student.recent_days_count = attendance_stats['total_days'] or 0
    
    # Options pour les filtres
    classes = ClassRoom.objects.order_by('level__order', 'name')
    
    # Statistiques globales
    global_student_stats = {
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(
            is_graduated=False, 
            current_class__isnull=False
        ).count(),
        'graduated_students': Student.objects.filter(is_graduated=True).count(),
        'unassigned_students': Student.objects.filter(
            current_class__isnull=True, 
            is_graduated=False
        ).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'students': page_obj.object_list,
        'classes': classes,
        'global_student_stats': global_student_stats,
        'class_filter': class_filter,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'academic/admin/students_overview.html', context)


@admin_required
def admin_export_attendance_csv(request):
    """
    Export des données de présence en CSV
    """
    # Paramètres d'export
    period = request.GET.get('period', 'current_month')
    class_filter = request.GET.get('class')
    
    today = timezone.now().date()
    
    if period == 'current_month':
        start_date = today.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    elif period == 'last_month':
        end_date = today.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)
    else:
        start_date = today - timedelta(days=30)
        end_date = today
    
    # Récupérer les données
    summaries = DailyAttendanceSummary.objects.filter(
        date__range=[start_date, end_date]
    ).select_related(
        'student__user',
        'student__current_class'
    ).order_by('date', 'student__user__last_name')
    
    if class_filter:
        summaries = summaries.filter(student__current_class_id=class_filter)
    
    # Créer la réponse CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="presences_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Nom', 'Prénom', 'Matricule', 'Classe', 
        'Statut', 'Taux de présence', 'Sessions totales', 'Sessions assistées'
    ])
    
    for summary in summaries:
        writer.writerow([
            summary.date.strftime('%Y-%m-%d'),
            summary.student.user.last_name,
            summary.student.user.first_name,
            summary.student.matricule,
            summary.student.current_class.name if summary.student.current_class else '',
            summary.get_daily_status_display(),
            f"{summary.attendance_rate:.1f}%",
            summary.total_sessions,
            summary.present_sessions,
        ])
    
    return response


@admin_required
def admin_system_stats(request):
    """
    Statistiques système pour l'administration
    """
    # Statistiques générales
    stats = {
        'users': {
            'total': User.objects.count(),
            'students': Student.objects.count(),
            'teachers': Teacher.objects.count(),
            'parents': Parent.objects.count(),
            'admins': User.objects.filter(role__in=['ADMIN', 'SUPER_ADMIN']).count(),
        },
        'academic': {
            'levels': Level.objects.count(),
            'classes': ClassRoom.objects.count(),
            'subjects': Subject.objects.count(),
            'timetables': Timetable.objects.count(),
            'sessions': Session.objects.count(),
            'documents': Document.objects.count(),
            'assignments': SessionAssignment.objects.count(),
        },
        'activity': {
            'sessions_this_month': Session.objects.filter(
                date__gte=timezone.now().date().replace(day=1)
            ).count(),
            'documents_this_month': SessionDocument.objects.filter(
                shared_at__gte=timezone.now().replace(day=1)
            ).count(),
            'assignments_this_month': SessionAssignment.objects.filter(
                created_at__gte=timezone.now().replace(day=1)
            ).count(),
        }
    }
    
    # Évolution mensuelle (6 derniers mois)
    monthly_evolution = []
    for i in range(6):
        month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        
        monthly_stats = {
            'month': month_start.strftime('%B %Y'),
            'sessions': Session.objects.filter(date__range=[month_start, month_end]).count(),
            'documents': SessionDocument.objects.filter(
                shared_at__date__range=[month_start, month_end]
            ).count(),
            'assignments': SessionAssignment.objects.filter(
                created_at__date__range=[month_start, month_end]
            ).count(),
        }
        monthly_evolution.append(monthly_stats)
    
    monthly_evolution.reverse()
    
    context = {
        'stats': stats,
        'monthly_evolution': monthly_evolution,
    }
    
    return render(request, 'academic/admin/system_stats.html', context)