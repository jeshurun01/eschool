"""
Vues spécialisées pour les enseignants
Module Academic - Teacher Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, Prefetch
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from datetime import datetime, timedelta
import json

from core.decorators.permissions import teacher_required
from accounts.models import Teacher, Student
from academic.models import (
    Session, SessionAttendance, SessionDocument, 
    SessionAssignment, DailyAttendanceSummary,
    Timetable, Subject, ClassRoom, Document,
    Period, AcademicYear, Enrollment, TeacherAssignment
)


@teacher_required
def teacher_sessions_view(request):
    """
    Vue pour afficher les sessions de l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Récupérer les filtres
    search = request.GET.get('search', '')
    classroom_id = request.GET.get('classroom', '')
    subject_id = request.GET.get('subject', '')
    status = request.GET.get('status', '')
    period = request.GET.get('period', 'all')
    
    today = timezone.now().date()
    
    # Gérer les périodes
    if period == 'current_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'current_month':
        start_date = today.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    elif period == 'next_week':
        start_date = today + timedelta(days=7 - today.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # all
        start_date = None
        end_date = None
    
    # Récupérer les sessions de l'enseignant
    sessions_query = Session.objects.filter(
        timetable__teacher=teacher
    ).select_related(
        'timetable__subject', 
        'timetable__classroom',
        'period'
    ).prefetch_related(
        'documents__document',
        'assignments',
        'attendances'
    )
    
    # Appliquer les filtres
    if start_date and end_date:
        sessions_query = sessions_query.filter(date__range=[start_date, end_date])
    
    if search:
        from django.db.models import Q
        sessions_query = sessions_query.filter(
            Q(timetable__subject__name__icontains=search) |
            Q(timetable__classroom__name__icontains=search) |
            Q(description__icontains=search) |
            Q(teacher_notes__icontains=search)
        )
    
    if classroom_id:
        sessions_query = sessions_query.filter(timetable__classroom_id=classroom_id)
    
    if subject_id:
        sessions_query = sessions_query.filter(timetable__subject_id=subject_id)
    
    if status:
        if status == 'upcoming':
            sessions_query = sessions_query.filter(date__gte=today, status='SCHEDULED')
        elif status == 'in_progress':
            sessions_query = sessions_query.filter(status='IN_PROGRESS')
        elif status == 'completed':
            sessions_query = sessions_query.filter(status='COMPLETED')
        elif status == 'cancelled':
            sessions_query = sessions_query.filter(status='CANCELLED')
    
    sessions = sessions_query.order_by('-date', 'timetable__start_time')
    
    # Récupérer les classes et matières de l'enseignant pour les filtres
    teacher_assignments = TeacherAssignment.objects.filter(
        teacher=teacher,
        academic_year__is_current=True
    ).select_related('classroom', 'subject')
    
    classrooms = ClassRoom.objects.filter(
        id__in=teacher_assignments.values_list('classroom_id', flat=True)
    ).distinct().order_by('name')
    
    subjects = Subject.objects.filter(
        id__in=teacher_assignments.values_list('subject_id', flat=True)
    ).distinct().order_by('name')
    
    # Pagination
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques rapides
    all_sessions = Session.objects.filter(timetable__teacher=teacher)
    stats = {
        'total_sessions': all_sessions.count(),
        'today_sessions': all_sessions.filter(date=today).count(),
        'upcoming_sessions': all_sessions.filter(date__gte=today, status='SCHEDULED').count(),
        'completed_sessions': all_sessions.filter(status='COMPLETED').count(),
        'avg_attendance': 85,  # À calculer dynamiquement
        'pending_attendance': all_sessions.filter(status='COMPLETED', attendance_taken=False).count(),
    }
    
    context = {
        'teacher': teacher,
        'page_obj': page_obj,
        'sessions': page_obj.object_list,
        'stats': stats,
        'classrooms': classrooms,
        'subjects': subjects,
        'period': period,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'academic/teacher/sessions_list.html', context)


@teacher_required
def teacher_session_detail(request, session_id):
    """
    Vue détaillée d'une session pour l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    session = get_object_or_404(
        Session.objects.select_related(
            'timetable__subject',
            'timetable__classroom',
            'period'
        ).prefetch_related(
            'documents__document',
            'assignments',
            'attendances__student__user'
        ),
        id=session_id,
        timetable__teacher=teacher
    )
    
    # Statistiques de présence
    attendance_stats = {
        'total_students': session.timetable.classroom.students.count(),
        'present': session.attendances.filter(status='PRESENT').count(),
        'absent': session.attendances.filter(status='ABSENT').count(),
        'late': session.attendances.filter(status='LATE').count(),
        'excused': session.attendances.filter(status='EXCUSED').count(),
    }
    
    # Calculer les pourcentages
    if attendance_stats['total_students'] > 0:
        attendance_stats['present_rate'] = round(
            (attendance_stats['present'] + attendance_stats['late']) / attendance_stats['total_students'] * 100, 1
        )
    else:
        attendance_stats['present_rate'] = 0
    
    # Documents de la session
    documents = session.documents.select_related('document').order_by('-shared_at')
    
    # Devoirs de la session
    assignments = session.assignments.order_by('due_date')
    
    context = {
        'teacher': teacher,
        'session': session,
        'attendance_stats': attendance_stats,
        'documents': documents,
        'assignments': assignments,
    }
    
    return render(request, 'academic/teacher/session_detail.html', context)


@teacher_required
def teacher_session_edit(request, session_id):
    """
    Vue pour modifier une session
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    session = get_object_or_404(
        Session,
        id=session_id,
        timetable__teacher=teacher
    )
    
    if request.method == 'POST':
        # Mettre à jour les informations de la session
        session.lesson_title = request.POST.get('lesson_title', '')
        session.lesson_objectives = request.POST.get('lesson_objectives', '')
        session.lesson_content = request.POST.get('lesson_content', '')
        session.lesson_summary = request.POST.get('lesson_summary', '')
        session.teacher_notes = request.POST.get('teacher_notes', '')
        session.homework_given = request.POST.get('homework_given', '')
        session.next_lesson_preparation = request.POST.get('next_lesson_preparation', '')
        session.status = request.POST.get('status', session.status)
        
        # Mettre à jour les heures réelles si fournies
        actual_start_time = request.POST.get('actual_start_time')
        actual_end_time = request.POST.get('actual_end_time')
        
        if actual_start_time:
            session.actual_start_time = actual_start_time
        if actual_end_time:
            session.actual_end_time = actual_end_time
            
        session.save()
        
        messages.success(request, "Session mise à jour avec succès.")
        return redirect('academic:teacher_session_detail', session_id=session.pk)
    
    context = {
        'teacher': teacher,
        'session': session,
    }
    
    return render(request, 'academic/teacher/session_edit.html', context)


@teacher_required
def teacher_attendance_view(request, session_id):
    """
    Vue pour prendre les présences d'une session
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    session = get_object_or_404(
        Session.objects.select_related(
            'timetable__subject',
            'timetable__classroom'
        ),
        id=session_id,
        timetable__teacher=teacher
    )
    
    # Récupérer tous les étudiants de la classe
    students = Student.objects.filter(
        current_class=session.timetable.classroom
    ).select_related('user').order_by('user__last_name', 'user__first_name')
    
    # Récupérer les présences existantes
    existing_attendances = {
        att.student.id: att for att in SessionAttendance.objects.filter(
            session=session
        ).select_related('student__user')
    }
    
    # Préparer les données pour le template
    student_attendances = []
    for student in students:
        attendance = existing_attendances.get(student.pk)
        student_attendances.append({
            'student': student,
            'attendance': attendance,
            'status': attendance.status if attendance else 'ABSENT',
            'arrival_time': attendance.arrival_time if attendance else None,
            'notes': attendance.notes if attendance else '',
        })
    
    if request.method == 'POST':
        # Traitement de la soumission des présences
        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'ABSENT')
            arrival_time = request.POST.get(f'arrival_time_{student.pk}') or None
            notes = request.POST.get(f'notes_{student.pk}', '')
            
            # Créer ou mettre à jour l'enregistrement de présence
            attendance, created = SessionAttendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={
                    'status': status,
                    'arrival_time': arrival_time,
                    'notes': notes,
                    'recorded_by': request.user,
                    'recorded_at': timezone.now(),
                }
            )
        
        # Marquer l'appel comme effectué
        session.attendance_taken = True
        session.attendance_taken_at = timezone.now()
        session.save()
        
        messages.success(request, "Présences enregistrées avec succès.")
        return redirect('academic:teacher_session_detail', session_id=session.pk)
    
    context = {
        'teacher': teacher,
        'session': session,
        'student_attendances': student_attendances,
    }
    
    return render(request, 'academic/teacher/attendance_form.html', context)


@teacher_required
def teacher_timetable_view(request):
    """
    Vue de l'emploi du temps de l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Gestion de la semaine courante
    week_param = request.GET.get('week')
    if week_param:
        try:
            current_week = datetime.strptime(week_param, '%Y-%m-%d').date()
        except ValueError:
            current_week = timezone.now().date()
    else:
        current_week = timezone.now().date()
    
    # Calculer le début de la semaine (lundi)
    days_since_monday = current_week.weekday()
    week_start = current_week - timedelta(days=days_since_monday)
    
    # Navigation semaines
    previous_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    # Créer les jours de la semaine
    week_days = []
    today = timezone.now().date()
    
    for i in range(5):  # Lundi à Vendredi
        day_date = week_start + timedelta(days=i)
        week_days.append({
            'weekday': i + 1,
            'name': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'][i],
            'date': day_date,
            'is_today': day_date == today
        })
    
    # Récupérer l'emploi du temps de l'enseignant
    timetables = Timetable.objects.filter(
        teacher=teacher
    ).select_related(
        'subject',
        'classroom'
    ).order_by('weekday', 'start_time')
    
    # Créer les créneaux horaires uniques
    time_slots = []
    times_seen = set()
    
    for timetable in timetables:
        time_key = f"{timetable.start_time}_{timetable.end_time}"
        if time_key not in times_seen:
            time_slots.append({
                'start_time': timetable.start_time,
                'end_time': timetable.end_time,
                'time_key': time_key
            })
            times_seen.add(time_key)
    
    # Trier les créneaux par heure de début
    time_slots.sort(key=lambda x: x['start_time'])
    
    # Organiser les créneaux dans une grille
    timetable_grid = {}
    for day in week_days:
        timetable_grid[day['weekday']] = {}
        for time_slot in time_slots:
            timetable_grid[day['weekday']][time_slot['time_key']] = None
    
    # Remplir la grille avec les créneaux
    for timetable in timetables:
        weekday = timetable.weekday
        time_key = f"{timetable.start_time}_{timetable.end_time}"
        if weekday in timetable_grid and time_key in timetable_grid[weekday]:
            timetable_grid[weekday][time_key] = timetable
    
    # Récupérer les sessions de la semaine
    sessions = Session.objects.filter(
        timetable__teacher=teacher,
        date__range=[week_start, week_start + timedelta(days=6)]
    ).select_related('timetable')
    
    # Organiser les sessions par timetable
    sessions_by_timetable = {}
    for session in sessions:
        sessions_by_timetable[session.timetable.pk] = session
    
    # Statistiques de la semaine
    weekly_stats = {
        'total_hours': sum(
            ((datetime.combine(timezone.now().date(), t.end_time) - 
              datetime.combine(timezone.now().date(), t.start_time)).seconds / 3600)
            for t in timetables
        ),
        'different_classes': timetables.values('classroom').distinct().count(),
        'different_subjects': timetables.values('subject').distinct().count(),
        'total_sessions': sessions.count(),
    }
    
    context = {
        'teacher': teacher,
        'current_week': week_start,
        'previous_week': previous_week,
        'next_week': next_week,
        'week_days': week_days,
        'time_slots': time_slots,
        'timetable_grid': timetable_grid,
        'sessions_by_timetable': sessions_by_timetable,
        'weekly_stats': weekly_stats,
        'today': today,
    }
    
    return render(request, 'academic/teacher/timetable.html', context)


@teacher_required
def teacher_documents_view(request):
    """
    Vue pour gérer les documents de l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Filtres
    subject_id = request.GET.get('subject')
    document_type = request.GET.get('type')
    search = request.GET.get('search')
    
    # Documents de l'enseignant
    documents = Document.objects.filter(
        teacher=teacher
    ).select_related('subject').order_by('-created_at')
    
    # Appliquer les filtres
    if subject_id:
        documents = documents.filter(subject_id=subject_id)
    
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Options pour les filtres
    subjects = Subject.objects.filter(
        teachers=teacher
    ).distinct().order_by('name')
    
    document_types = Document.DOCUMENT_TYPE_CHOICES
    
    # Statistiques
    stats = {
        'total_documents': documents.count(),
        'total_downloads': documents.aggregate(Sum('download_count'))['download_count__sum'] or 0,
        'total_views': documents.aggregate(Sum('view_count'))['view_count__sum'] or 0,
    }
    
    context = {
        'teacher': teacher,
        'page_obj': page_obj,
        'documents': page_obj.object_list,
        'subjects': subjects,
        'document_types': document_types,
        'current_subject': subject_id,
        'current_type': document_type,
        'search': search,
        'stats': stats,
    }
    
    return render(request, 'academic/teacher/documents.html', context)


@teacher_required
def teacher_assignments_view(request):
    """
    Vue pour gérer les devoirs de l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Filtres
    status = request.GET.get('status', 'all')
    subject_id = request.GET.get('subject')
    
    # Devoirs de l'enseignant
    assignments = SessionAssignment.objects.filter(
        created_by=request.user
    ).select_related(
        'session__timetable__subject',
        'session__timetable__classroom'
    ).order_by('-created_at')
    
    today = timezone.now().date()
    
    # Appliquer les filtres de statut
    if status == 'pending':
        assignments = assignments.filter(due_date__gte=today)
    elif status == 'overdue':
        assignments = assignments.filter(due_date__lt=today)
    elif status == 'unpublished':
        assignments = assignments.filter(is_published=False)
    
    # Filtre par matière
    if subject_id:
        assignments = assignments.filter(session__timetable__subject_id=subject_id)
    
    # Pagination
    paginator = Paginator(assignments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Options pour les filtres
    subjects = Subject.objects.filter(
        teachers=teacher
    ).distinct().order_by('name')
    
    # Statistiques
    stats = {
        'total': assignments.count(),
        'pending': assignments.filter(due_date__gte=today).count(),
        'overdue': assignments.filter(due_date__lt=today).count(),
        'unpublished': assignments.filter(is_published=False).count(),
    }
    
    context = {
        'teacher': teacher,
        'page_obj': page_obj,
        'assignments': page_obj.object_list,
        'subjects': subjects,
        'current_subject': subject_id,
        'current_status': status,
        'stats': stats,
        'today': today,
    }
    
    return render(request, 'academic/teacher/assignments.html', context)


@teacher_required
def teacher_students_overview(request):
    """
    Vue d'ensemble des étudiants de l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Récupérer les classes enseignées
    taught_classes = ClassRoom.objects.filter(
        timetables__teacher=teacher
    ).distinct().prefetch_related(
        'enrollments__student__user',
        'timetables__subject'
    )
    
    # Statistiques par classe
    class_stats = []
    for classroom in taught_classes:
        # Récupérer les étudiants via les inscriptions actives
        active_enrollments = classroom.enrollments.filter(is_active=True)
        students_count = active_enrollments.count()
        
        # Calcul des statistiques de présence pour cette classe
        recent_sessions = Session.objects.filter(
            timetable__classroom=classroom,
            timetable__teacher=teacher,
            date__gte=timezone.now().date() - timedelta(days=30)
        )
        
        attendance_data = DailyAttendanceSummary.objects.filter(
            student__enrollments__classroom=classroom,
            student__enrollments__is_active=True,
            date__gte=timezone.now().date() - timedelta(days=30)
        ).aggregate(
            avg_attendance=Avg('attendance_rate'),
            total_sessions=Sum('total_sessions'),
            total_attended=Sum('present_sessions')
        )
        
        class_stats.append({
            'classroom': classroom,
            'student_count': students_count,
            'recent_sessions': recent_sessions.count(),
            'avg_attendance_rate': round(attendance_data['avg_attendance'] or 0, 1),
            'subjects': Subject.objects.filter(
                timetable__classroom=classroom,
                timetable__teacher=teacher
            ).distinct()
        })
    
    context = {
        'teacher': teacher,
        'class_stats': class_stats,
    }
    
    return render(request, 'academic/teacher/students_overview.html', context)


@teacher_required
def teacher_class_detail(request, class_id):
    """
    Vue détaillée d'une classe pour l'enseignant
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    classroom = get_object_or_404(
        ClassRoom.objects.prefetch_related(
            'enrollments__student__user',
            'timetables__subject'
        ).filter(
            id=class_id,
            timetables__teacher=teacher
        ).distinct()
    )
    
    # Étudiants de la classe via les inscriptions actives
    students = [enrollment.student for enrollment in 
               classroom.enrollments.filter(is_active=True)
               .select_related('student__user')
               .order_by('student__user__last_name', 'student__user__first_name')]
    
    # Matières enseignées dans cette classe par cet enseignant
    subjects = Subject.objects.filter(
        timetable__classroom=classroom,
        timetable__teacher=teacher
    ).distinct()
    
    # Sessions récentes
    recent_sessions = Session.objects.filter(
        timetable__classroom=classroom,
        timetable__teacher=teacher,
        date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-date', '-timetable__start_time')[:10]
    
    # Sessions récentes
    recent_sessions = Session.objects.filter(
        timetable__classroom=classroom,
        timetable__teacher=teacher
    ).select_related(
        'timetable__subject'
    ).order_by('-date')[:10]
    
    # Statistiques de présence par étudiant (30 derniers jours)
    student_stats = []
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    for student in students:
        stats = DailyAttendanceSummary.objects.filter(
            student=student,
            date__gte=thirty_days_ago
        ).aggregate(
            total_days=Count('id'),
            attendance_rate=Avg('attendance_rate'),
            total_sessions=Sum('total_sessions'),
            present_sessions=Sum('present_sessions')
        )
        
        student_stats.append({
            'student': student,
            'attendance_rate': round(stats['attendance_rate'] or 0, 1),
            'total_days': stats['total_days'] or 0,
            'total_sessions': stats['total_sessions'] or 0,
            'attended_sessions': stats['present_sessions'] or 0,
        })
    
    context = {
        'teacher': teacher,
        'classroom': classroom,
        'students': students,
        'subjects': subjects,
        'recent_sessions': recent_sessions,
        'student_stats': student_stats,
    }
    
    return render(request, 'academic/teacher/class_detail.html', context)


@teacher_required
def teacher_session_create(request):
    """
    Vue pour créer une nouvelle session
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        timetable_id = request.POST.get('timetable_id')
        date = request.POST.get('date')
        teacher_notes = request.POST.get('notes', '')  # Renommer pour éviter confusion
        
        try:
            # Valider que le créneau appartient bien à l'enseignant
            timetable = get_object_or_404(
                Timetable,
                id=timetable_id,
                teacher=teacher
            )
            
            # Récupérer la période courante (ou créer une logique pour la déterminer)
            from django.utils import timezone
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                messages.error(request, 'Aucune année académique courante définie')
                return redirect('academic:teacher_sessions')
            
            # Obtenir la période appropriée (par défaut la première de l'année courante)
            period = Period.objects.filter(academic_year=current_year).first()
            if not period:
                messages.error(request, 'Aucune période définie pour l\'année courante')
                return redirect('academic:teacher_sessions')
            
            # Créer la session
            session = Session.objects.create(
                timetable=timetable,
                period=period,
                date=date,
                status='SCHEDULED',  # Utiliser la constante correcte
                teacher_notes=teacher_notes  # Utiliser teacher_notes au lieu de notes
            )
            
            messages.success(request, f'Session créée avec succès pour {timetable.subject.name}')
            return redirect('academic:teacher_sessions')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de la session: {str(e)}')
    
    # Récupérer les créneaux d'emploi du temps de l'enseignant
    timetables = Timetable.objects.filter(teacher=teacher).select_related(
        'subject', 'classroom'
    ).order_by('weekday', 'start_time')
    
    context = {
        'teacher': teacher,
        'timetables': timetables,
    }
    
    return render(request, 'academic/teacher/session_create.html', context)


@teacher_required
def teacher_timetable_create(request):
    """
    Vue pour créer un nouveau créneau d'emploi du temps
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        subject_id = request.POST.get('subject_id')
        classroom_id = request.POST.get('classroom_id')
        weekday = request.POST.get('weekday')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room', '')
        
        try:
            # Valider les données
            subject = get_object_or_404(Subject, id=subject_id)
            classroom = get_object_or_404(ClassRoom, id=classroom_id)
            
            # Vérifier que l'enseignant a une assignation pour cette matière et cette classe
            current_year = AcademicYear.objects.filter(is_current=True).first()
            
            if not TeacherAssignment.objects.filter(
                teacher=teacher,
                subject=subject,
                classroom=classroom,
                academic_year=current_year
            ).exists():
                messages.error(request, 'Vous n\'êtes pas assigné à cette matière dans cette classe.')
                return redirect('academic:teacher_timetable_create')
            
            # Vérifier qu'il n'y a pas de conflit d'horaire
            conflicts = Timetable.objects.filter(
                teacher=teacher,
                weekday=weekday,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if conflicts.exists():
                messages.error(request, f'Conflit d\'horaire détecté avec un autre créneau le {dict(Timetable.WEEKDAY_CHOICES)[int(weekday)]}.')
                return redirect('academic:teacher_timetable_create')
            
            # Créer le créneau
            timetable = Timetable.objects.create(
                teacher=teacher,
                subject=subject,
                classroom=classroom,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                room=room
            )
            
            messages.success(request, f'Créneau créé avec succès : {subject.name} - {classroom.name} le {timetable.get_weekday_display()}')
            return redirect('academic:teacher_timetable')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du créneau: {str(e)}')
    
    # Récupérer les assignations de l'enseignant pour l'année courante
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if current_year:
        assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=current_year
        ).select_related('subject', 'classroom')
    else:
        assignments = []
    
    # Récupérer les matières et classes disponibles
    subjects = Subject.objects.filter(
        teacherassignment__teacher=teacher,
        teacherassignment__academic_year=current_year
    ).distinct() if current_year else []
    
    classrooms = ClassRoom.objects.filter(
        teacherassignment__teacher=teacher,
        teacherassignment__academic_year=current_year
    ).distinct() if current_year else []
    
    context = {
        'teacher': teacher,
        'assignments': assignments,
        'subjects': subjects,
        'classrooms': classrooms,
        'weekday_choices': Timetable.WEEKDAY_CHOICES,
    }
    
    return render(request, 'academic/teacher/timetable_create.html', context)


@teacher_required
def teacher_timetable_detail(request, timetable_id):
    """
    Vue pour afficher les détails d'un créneau d'emploi du temps
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Récupérer le créneau (vérifier qu'il appartient bien à l'enseignant)
    timetable = get_object_or_404(
        Timetable.objects.select_related(
            'subject', 'classroom', 'classroom__level'
        ),
        id=timetable_id,
        teacher=teacher
    )
    
    # Récupérer les sessions associées à ce créneau
    sessions = Session.objects.filter(
        timetable=timetable
    ).select_related('period').order_by('-date')[:20]
    
    # Statistiques du créneau
    total_sessions = Session.objects.filter(timetable=timetable).count()
    completed_sessions = Session.objects.filter(
        timetable=timetable, 
        status='COMPLETED'
    ).count()
    upcoming_sessions = Session.objects.filter(
        timetable=timetable,
        date__gte=timezone.now().date(),
        status='SCHEDULED'
    ).count()
    
    # Étudiants de la classe
    students_count = Enrollment.objects.filter(
        classroom=timetable.classroom,
        is_active=True
    ).count()
    
    context = {
        'teacher': teacher,
        'timetable': timetable,
        'sessions': sessions,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'upcoming_sessions': upcoming_sessions,
        'students_count': students_count,
    }
    
    return render(request, 'academic/teacher/timetable_detail.html', context)


@teacher_required
def teacher_timetable_delete(request, timetable_id):
    """
    Vue pour supprimer un créneau d'emploi du temps
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    timetable = get_object_or_404(Timetable, id=timetable_id, teacher=teacher)
    
    if request.method == 'POST':
        # Vérifier s'il y a des sessions associées
        sessions_count = Session.objects.filter(timetable=timetable).count()
        
        if sessions_count > 0:
            messages.warning(
                request, 
                f'Ce créneau a {sessions_count} session(s) associée(s). '
                'Toutes les sessions seront également supprimées.'
            )
        
        timetable_info = f'{timetable.subject.name} - {timetable.classroom.name} le {timetable.get_weekday_display()}'
        timetable.delete()
        
        messages.success(request, f'Créneau "{timetable_info}" supprimé avec succès.')
        return redirect('academic:teacher_timetable')
    
    return redirect('academic:teacher_timetable_detail', timetable_id=timetable_id)


@teacher_required
def teacher_session_document_add(request, session_id):
    """
    Vue pour ajouter un document à une session
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    session = get_object_or_404(Session, id=session_id, timetable__teacher=teacher)
    
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        purpose = request.POST.get('purpose', '')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        deadline = request.POST.get('deadline')
        
        if document_id:
            try:
                document = Document.objects.get(id=document_id)
                
                # Vérifier si le document n'est pas déjà lié à cette session
                if SessionDocument.objects.filter(session=session, document=document).exists():
                    messages.warning(request, 'Ce document est déjà lié à cette session.')
                else:
                    # Créer le lien SessionDocument
                    session_doc = SessionDocument.objects.create(
                        session=session,
                        document=document,
                        shared_by=request.user,
                        purpose=purpose,
                        is_mandatory=is_mandatory,
                        deadline=deadline if deadline else None
                    )
                    messages.success(request, f'Document "{document.title}" ajouté à la session avec succès.')
            except Document.DoesNotExist:
                messages.error(request, 'Document introuvable.')
        else:
            messages.error(request, 'Veuillez sélectionner un document.')
        
        return redirect('academic:teacher_session_detail', session_id=session_id)
    
    # GET request - afficher le formulaire
    # Récupérer tous les documents de l'enseignant ou de la matière
    available_documents = Document.objects.filter(
        Q(teacher=teacher) |
        Q(subject=session.timetable.subject)
    ).distinct()
    
    # Exclure les documents déjà liés
    linked_document_ids = session.documents.values_list('document_id', flat=True)
    available_documents = available_documents.exclude(id__in=linked_document_ids)
    
    context = {
        'teacher': teacher,
        'session': session,
        'available_documents': available_documents,
    }
    
    return render(request, 'academic/teacher/session_document_add.html', context)


@teacher_required
def teacher_session_assignment_add(request, session_id):
    """
    Vue pour ajouter un devoir à une session
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    session = get_object_or_404(Session, id=session_id, timetable__teacher=teacher)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assignment_type = request.POST.get('assignment_type', 'HOMEWORK')
        priority = request.POST.get('priority', 'MEDIUM')
        due_date = request.POST.get('due_date')
        estimated_duration = request.POST.get('estimated_duration')
        will_be_graded = request.POST.get('will_be_graded') == 'on'
        max_score = request.POST.get('max_score') if will_be_graded else None
        coefficient = request.POST.get('coefficient', '1.0')
        instructions = request.POST.get('instructions', '')
        resources_needed = request.POST.get('resources_needed', '')
        submission_format = request.POST.get('submission_format', '')
        
        if title and description and due_date and estimated_duration:
            try:
                # Créer le devoir
                assignment = SessionAssignment.objects.create(
                    session=session,
                    title=title,
                    description=description,
                    assignment_type=assignment_type,
                    priority=priority,
                    due_date=due_date,
                    estimated_duration=int(estimated_duration),
                    will_be_graded=will_be_graded,
                    max_score=max_score if max_score else None,
                    coefficient=coefficient,
                    instructions=instructions,
                    resources_needed=resources_needed,
                    submission_format=submission_format,
                    created_by=request.user,
                    published_at=timezone.now()
                )
                messages.success(request, f'Devoir "{title}" créé avec succès.')
                return redirect('academic:teacher_session_detail', session_id=session_id)
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du devoir: {str(e)}')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    # GET request - afficher le formulaire
    context = {
        'teacher': teacher,
        'session': session,
        'assignment_types': SessionAssignment.ASSIGNMENT_TYPE_CHOICES,
        'priorities': SessionAssignment.PRIORITY_CHOICES,
    }
    
    return render(request, 'academic/teacher/session_assignment_add.html', context)