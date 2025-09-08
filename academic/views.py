from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, F, FloatField
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator

# Import RBAC
from core.decorators.permissions import (
    teacher_required, student_required, parent_required, 
    admin_required, teacher_or_student_required
)

from .models import (
    AcademicYear, Level, Subject, ClassRoom, 
    TeacherAssignment, Enrollment, Grade, Attendance, Timetable
)
from accounts.models import Teacher, Student


@admin_required  # Seuls les admins peuvent voir toutes les classes
def classroom_list(request):
    """Liste des classes avec filtrage et recherche"""
    # Utiliser le manager RBAC pour filtrer selon le rôle
    classrooms = ClassRoom.objects.for_role(request.user).select_related(
        'level', 'academic_year', 'head_teacher__user'
    ).annotate(
        student_count=Count('enrollments', filter=Q(enrollments__is_active=True))
    )
    
    # Filtrage par année académique
    academic_year = request.GET.get('academic_year')
    if academic_year and academic_year != 'None' and academic_year.strip():
        try:
            classrooms = classrooms.filter(academic_year_id=int(academic_year))
        except (ValueError, TypeError):
            pass  # Ignorer les valeurs invalides
    else:
        # Par défaut, année courante
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            classrooms = classrooms.filter(academic_year=current_year)
    
    # Filtrage par niveau
    level = request.GET.get('level')
    if level and level != 'None' and level.strip():
        try:
            classrooms = classrooms.filter(level_id=int(level))
        except (ValueError, TypeError):
            pass  # Ignorer les valeurs invalides
    
    # Recherche
    search = request.GET.get('search')
    if search and search != 'None' and search.strip():
        classrooms = classrooms.filter(
            Q(name__icontains=search) |
            Q(level__name__icontains=search) |
            Q(head_teacher__user__first_name__icontains=search) |
            Q(head_teacher__user__last_name__icontains=search)
        )
    
    # Ordre pour la pagination
    classrooms = classrooms.order_by('level__name', 'name')
    
    # Pagination
    paginator = Paginator(classrooms, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Données pour les filtres
    academic_years = AcademicYear.objects.all()
    levels = Level.objects.all()
    
    context = {
        'classrooms': page_obj,
        'academic_years': academic_years,
        'levels': levels,
        'current_academic_year': academic_year,
        'current_level': level,
        'search': search,
        'total_classrooms': classrooms.count(),
    }
    
    return render(request, 'academic/classroom_list.html', context)


@login_required
def classroom_detail(request, classroom_id):
    """Détails d'une classe"""
    classroom = get_object_or_404(
        ClassRoom.objects.select_related(
            'level', 'academic_year', 'head_teacher__user'
        ),
        id=classroom_id
    )
    
    # Étudiants inscrits
    enrollments = Enrollment.objects.filter(
        classroom=classroom, 
        is_active=True
    ).select_related('student__user').order_by('student__user__last_name')
    
    # Enseignants assignés
    assignments = TeacherAssignment.objects.filter(
        classroom=classroom,
        academic_year=classroom.academic_year
    ).select_related('teacher__user', 'subject')
    
    # Statistiques
    stats = {
        'total_students': enrollments.count(),
        'capacity_usage': round((enrollments.count() / classroom.capacity) * 100, 1) if classroom.capacity > 0 else 0,
        'total_teachers': assignments.count(),
        'total_subjects': assignments.values('subject').distinct().count(),
    }
    
    # Notes récentes (si l'utilisateur est enseignant)
    recent_grades = []
    if hasattr(request.user, 'teacher'):
        recent_grades = Grade.objects.filter(
            classroom=classroom,
            subject__in=assignments.filter(teacher=request.user.teacher).values('subject')
        ).select_related('student__user', 'subject').order_by('-created_at')[:10]
    
    context = {
        'classroom': classroom,
        'enrollments': enrollments,
        'assignments': assignments,
        'stats': stats,
        'recent_grades': recent_grades,
    }
    
    return render(request, 'academic/classroom_detail.html', context)


@login_required
def classroom_create(request):
    """Créer une nouvelle classe"""
    if request.method == 'POST':
        name = request.POST.get('name')
        level_id = request.POST.get('level')
        academic_year_id = request.POST.get('academic_year')
        head_teacher_id = request.POST.get('head_teacher')
        capacity = request.POST.get('capacity', 30)
        room_number = request.POST.get('room_number')
        
        # Validation
        if not all([name, level_id, academic_year_id]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('academic:classroom_create')
        
        try:
            level = get_object_or_404(Level, id=level_id)
            academic_year = get_object_or_404(AcademicYear, id=academic_year_id)
            head_teacher = None
            if head_teacher_id:
                head_teacher = get_object_or_404(Teacher, id=head_teacher_id)
            
            # Vérifier l'unicité
            if ClassRoom.objects.filter(name=name, level=level, academic_year=academic_year).exists():
                messages.error(request, 'Une classe avec ce nom existe déjà pour ce niveau et cette année.')
                return redirect('academic:classroom_create')
            
            classroom = ClassRoom.objects.create(
                name=name,
                level=level,
                academic_year=academic_year,
                head_teacher=head_teacher,
                capacity=int(capacity),
                room_number=room_number
            )
            
            messages.success(request, f'La classe {classroom.name} a été créée avec succès.')
            return redirect('academic:classroom_detail', classroom_id=classroom.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Données pour le formulaire
    levels = Level.objects.all()
    academic_years = AcademicYear.objects.all()
    teachers = Teacher.objects.select_related('user').filter(user__is_active=True)
    
    context = {
        'levels': levels,
        'academic_years': academic_years,
        'teachers': teachers,
    }
    
    return render(request, 'academic/classroom_create.html', context)


@login_required
def classroom_edit(request, classroom_id):
    """Modifier une classe"""
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    
    if request.method == 'POST':
        classroom.name = request.POST.get('name', classroom.name)
        classroom.capacity = int(request.POST.get('capacity', classroom.capacity))
        classroom.room_number = request.POST.get('room_number', classroom.room_number)
        
        level_id = request.POST.get('level')
        if level_id:
            classroom.level = get_object_or_404(Level, id=level_id)
        
        head_teacher_id = request.POST.get('head_teacher')
        if head_teacher_id:
            classroom.head_teacher = get_object_or_404(Teacher, id=head_teacher_id)
        else:
            classroom.head_teacher = None
        
        try:
            classroom.save()
            messages.success(request, 'La classe a été modifiée avec succès.')
            return redirect('academic:classroom_detail', classroom_id=classroom.id)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    # Données pour le formulaire
    levels = Level.objects.all()
    teachers = Teacher.objects.select_related('user').filter(user__is_active=True)
    
    context = {
        'classroom': classroom,
        'levels': levels,
        'teachers': teachers,
    }
    
    return render(request, 'academic/classroom_edit.html', context)


@login_required
def enrollment_manage(request, classroom_id):
    """Gérer les inscriptions d'une classe"""
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    
    # Vérifier les permissions - seuls les admins peuvent gérer les inscriptions
    if not request.user.is_admin:
        messages.error(request, 'Vous n\'avez pas les permissions pour gérer les inscriptions.')
        return redirect('academic:classroom_detail', classroom_id=classroom_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        
        if action == 'add' and student_id:
            try:
                student = get_object_or_404(Student, id=student_id)
                
                # Vérifier s'il y a une inscription active cette année
                active_enrollment = Enrollment.objects.filter(
                    student=student,
                    academic_year=classroom.academic_year,
                    is_active=True
                ).first()
                
                if active_enrollment:
                    messages.error(request, f'{student.user.get_full_name()} est déjà inscrit dans la classe {active_enrollment.classroom.name} cette année.')
                elif classroom.is_full:
                    messages.error(request, f'La classe a atteint sa capacité maximale ({classroom.capacity} élèves).')
                else:
                    # Vérifier s'il y a une inscription inactive dans cette classe
                    inactive_enrollment = Enrollment.objects.filter(
                        student=student,
                        classroom=classroom,
                        academic_year=classroom.academic_year,
                        is_active=False
                    ).first()
                    
                    if inactive_enrollment:
                        # Réactiver l'inscription existante
                        inactive_enrollment.is_active = True
                        inactive_enrollment.withdrawal_date = None
                        inactive_enrollment.enrollment_date = timezone.now().date()
                        inactive_enrollment.save()
                        messages.success(request, f'✅ {student.user.get_full_name()} a été réinscrit dans la classe {classroom.name}.')
                    else:
                        # Créer une nouvelle inscription
                        Enrollment.objects.create(
                            student=student,
                            classroom=classroom,
                            academic_year=classroom.academic_year
                        )
                        messages.success(request, f'✅ {student.user.get_full_name()} a été inscrit dans la classe {classroom.name}.')
                    
            except Exception as e:
                messages.error(request, f'❌ Erreur lors de l\'inscription : {str(e)}')
        
        elif action == 'remove' and student_id:
            try:
                enrollment = get_object_or_404(
                    Enrollment,
                    student_id=student_id,
                    classroom=classroom,
                    is_active=True
                )
                enrollment.is_active = False
                enrollment.withdrawal_date = timezone.now().date()
                enrollment.save()
                
                student_name = enrollment.student.user.get_full_name()
                messages.success(request, f'✅ {student_name} a été retiré de la classe {classroom.name}.')
                
            except Exception as e:
                messages.error(request, f'❌ Erreur lors du retrait : {str(e)}')
        
        return redirect('academic:enrollment_manage', classroom_id=classroom.id)
    
    # Étudiants inscrits dans cette classe
    enrollments = Enrollment.objects.filter(
        classroom=classroom, 
        is_active=True
    ).select_related('student__user').order_by('student__user__last_name', 'student__user__first_name')
    
    # Étudiants disponibles pour inscription (pas déjà inscrits cette année)
    enrolled_student_ids = Enrollment.objects.filter(
        academic_year=classroom.academic_year,
        is_active=True
    ).values_list('student_id', flat=True)
    
    available_students = Student.objects.select_related('user').exclude(
        id__in=enrolled_student_ids
    ).filter(
        user__is_active=True
    ).order_by('user__last_name', 'user__first_name')
    
    # Statistiques
    context = {
        'classroom': classroom,
        'enrollments': enrollments,
        'available_students': available_students,
        'capacity_usage': round((enrollments.count() / classroom.capacity) * 100, 1) if classroom.capacity > 0 else 0,
    }
    
    return render(request, 'academic/enrollment_manage.html', context)


# Vues temporaires (placeholder) - À implémenter plus tard

def academic_year_list(request):
    return HttpResponse("Liste des années scolaires - En cours de développement")

def academic_year_create(request):
    return HttpResponse("Créer une année scolaire - En cours de développement")

def level_list(request):
    return HttpResponse("Liste des niveaux - En cours de développement")

def level_create(request):
    return HttpResponse("Créer un niveau - En cours de développement")

def subject_list(request):
    return HttpResponse("Liste des matières - En cours de développement")

def subject_create(request):
    return HttpResponse("Créer une matière - En cours de développement")

def classroom_students(request, classroom_id):
    return HttpResponse(f"Élèves de la classe {classroom_id} - En cours de développement")

@login_required
def classroom_timetable(request, classroom_id):
    """Emploi du temps d'une classe"""
    classroom = get_object_or_404(
        ClassRoom.objects.select_related('level', 'academic_year', 'head_teacher__user'),
        id=classroom_id
    )
    
    # Récupérer tous les cours de l'emploi du temps pour cette classe
    timetables = Timetable.objects.filter(
        classroom=classroom
    ).select_related('subject', 'teacher__user').order_by('weekday', 'start_time')
    
    # Organiser les cours par jour de la semaine
    weekly_schedule = {}
    days = [
        (1, 'Lundi'),
        (2, 'Mardi'), 
        (3, 'Mercredi'),
        (4, 'Jeudi'),
        (5, 'Vendredi'),
        (6, 'Samedi'),
        (7, 'Dimanche')
    ]
    
    for day_num, day_name in days:
        day_courses = timetables.filter(weekday=day_num)
        weekly_schedule[day_name] = {
            'courses': day_courses,
            'total_hours': sum([
                (course.end_time.hour - course.start_time.hour) + 
                ((course.end_time.minute - course.start_time.minute) / 60)
                for course in day_courses
            ])
        }
    
    # Statistiques sur l'emploi du temps
    stats = {
        'total_courses': timetables.count(),
        'total_subjects': timetables.values('subject').distinct().count(),
        'total_teachers': timetables.values('teacher').distinct().count(),
        'total_weekly_hours': sum([day_data['total_hours'] for day_data in weekly_schedule.values()]),
    }
    
    # Enseignants assignés avec leurs matières
    assignments = TeacherAssignment.objects.filter(
        classroom=classroom,
        academic_year=classroom.academic_year
    ).select_related('teacher__user', 'subject')
    
    context = {
        'classroom': classroom,
        'weekly_schedule': weekly_schedule,
        'timetables': timetables,
        'stats': stats,
        'assignments': assignments,
        'days': days,
    }
    
    return render(request, 'academic/classroom_timetable.html', context)

def timetable_list(request):
    return HttpResponse("Liste des emplois du temps - En cours de développement")

def timetable_create(request):
    return HttpResponse("Créer un emploi du temps - En cours de développement")

def attendance_list(request):
    """Liste des présences avec filtres"""
    from django.db.models import Q, Count
    from datetime import datetime, timedelta
    
    # Récupérer les présences
    attendances = Attendance.objects.select_related(
        'student__user', 'classroom', 'subject', 'teacher__user'
    )
    
    # Filtres
    classroom_id = request.GET.get('classroom')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    subject_id = request.GET.get('subject')
    
    # Filtrage par classe
    if classroom_id and classroom_id != 'None':
        try:
            attendances = attendances.filter(classroom_id=int(classroom_id))
        except (ValueError, TypeError):
            pass
    
    # Filtrage par dates
    if date_from:
        try:
            attendances = attendances.filter(date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    
    if date_to:
        try:
            attendances = attendances.filter(date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass
    else:
        # Par défaut, dernière semaine
        one_week_ago = datetime.now().date() - timedelta(days=7)
        attendances = attendances.filter(date__gte=one_week_ago)
    
    # Filtrage par statut
    if status and status != 'None':
        attendances = attendances.filter(status=status)
    
    # Filtrage par matière
    if subject_id and subject_id != 'None':
        try:
            attendances = attendances.filter(subject_id=int(subject_id))
        except (ValueError, TypeError):
            pass
    
    # Ordre pour la pagination
    attendances = attendances.order_by('-date', 'classroom__name', 'student__user__last_name')
    
    # Pagination
    paginator = Paginator(attendances, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Données pour les filtres
    classrooms = ClassRoom.objects.filter(
        academic_year__is_current=True
    ).order_by('level__name', 'name')
    
    subjects = Subject.objects.all().order_by('name')
    
    # Statistiques
    total_attendances = attendances.count()
    present_count = attendances.filter(status='PRESENT').count()
    absent_count = attendances.filter(status='ABSENT').count()
    late_count = attendances.filter(status='LATE').count()
    excused_count = attendances.filter(status='EXCUSED').count()
    
    context = {
        'attendances': page_obj,
        'classrooms': classrooms,
        'subjects': subjects,
        'status_choices': Attendance.STATUS_CHOICES,
        'filters': {
            'classroom': classroom_id,
            'date_from': date_from,
            'date_to': date_to,
            'status': status,
            'subject': subject_id,
        },
        'stats': {
            'total': total_attendances,
            'present': present_count,
            'absent': absent_count,
            'late': late_count,
            'excused': excused_count,
        }
    }
    
    return render(request, 'academic/attendance_list.html', context)

def attendance_take(request):
    """Interface pour faire l'appel"""
    from datetime import datetime
    
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        date_str = request.POST.get('date')
        
        try:
            classroom = get_object_or_404(ClassRoom, id=classroom_id)
            subject = get_object_or_404(Subject, id=subject_id) if subject_id else None
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Vérifier que l'utilisateur peut faire l'appel pour cette classe
            if not request.user.is_superuser and hasattr(request.user, 'teacher'):
                # Vérifier si l'enseignant enseigne dans cette classe
                if not TeacherAssignment.objects.filter(
                    teacher=request.user.teacher,
                    classroom=classroom,
                    subject=subject
                ).exists():
                    messages.error(request, "Vous n'êtes pas autorisé à faire l'appel pour cette classe/matière.")
                    return redirect('academic:attendance_take')
            
            # Récupérer les étudiants de la classe
            students = Student.objects.filter(
                enrollments__classroom=classroom,
                enrollments__is_active=True
            ).select_related('user').order_by('user__last_name', 'user__first_name')
            
            # Traiter les présences
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                justification = request.POST.get(f'justification_{student.id}', '')
                
                if status:
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        classroom=classroom,
                        subject=subject,
                        date=date,
                        defaults={
                            'teacher': request.user.teacher if hasattr(request.user, 'teacher') else None,
                            'status': status,
                            'justification': justification,
                        }
                    )
                    
                    if not created:
                        attendance.status = status
                        attendance.justification = justification
                        attendance.save()
            
            messages.success(request, f"Appel effectué avec succès pour la classe {classroom.name} le {date}.")
            return redirect('academic:attendance_list')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")
    
    # GET request - afficher le formulaire
    classrooms = ClassRoom.objects.filter(
        academic_year__is_current=True
    ).order_by('level__name', 'name')
    
    subjects = Subject.objects.all().order_by('name')
    
    # Si l'utilisateur est enseignant, filtrer les classes/matières
    if hasattr(request.user, 'teacher') and not request.user.is_superuser:
        assignments = TeacherAssignment.objects.filter(
            teacher=request.user.teacher,
            academic_year__is_current=True
        ).select_related('classroom', 'subject')
        
        classroom_ids = assignments.values_list('classroom_id', flat=True).distinct()
        subject_ids = assignments.values_list('subject_id', flat=True).distinct()
        
        classrooms = classrooms.filter(id__in=classroom_ids)
        subjects = subjects.filter(id__in=subject_ids)
    
    context = {
        'classrooms': classrooms,
        'subjects': subjects,
        'today': datetime.now().date(),
        'status_choices': Attendance.STATUS_CHOICES,
    }
    
    return render(request, 'academic/attendance_take.html', context)

def attendance_class(request, classroom_id):
    """Présences d'une classe avec vue calendrier"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    
    # Paramètres de date
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        try:
            current_date = datetime(int(year), int(month), 1).date()
        except ValueError:
            current_date = datetime.now().date().replace(day=1)
    else:
        current_date = datetime.now().date().replace(day=1)
    
    # Dates du mois
    start_date = current_date
    if current_date.month == 12:
        end_date = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
    
    # Récupérer les présences du mois
    attendances = Attendance.objects.filter(
        classroom=classroom,
        date__range=[start_date, end_date]
    ).select_related('student__user', 'subject').order_by('date', 'student__user__last_name')
    
    # Étudiants de la classe
    students = Student.objects.filter(
        enrollments__classroom=classroom,
        enrollments__is_active=True
    ).select_related('user').order_by('user__last_name', 'user__first_name')
    
    # Organiser les données par date et étudiant
    attendance_data = {}
    dates_in_month = []
    
    current = start_date
    while current <= end_date:
        dates_in_month.append(current)
        attendance_data[current] = {}
        current += timedelta(days=1)
    
    # Remplir les données d'assiduité
    for attendance in attendances:
        if attendance.date not in attendance_data:
            attendance_data[attendance.date] = {}
        
        student_id = attendance.student.pk
        if student_id not in attendance_data[attendance.date]:
            attendance_data[attendance.date][student_id] = []
        
        attendance_data[attendance.date][student_id].append(attendance)
    
    # Statistiques pour chaque étudiant
    student_stats = {}
    for student in students:
        student_attendances = attendances.filter(student=student)
        student_stats[student.pk] = {
            'total': student_attendances.count(),
            'present': student_attendances.filter(status='PRESENT').count(),
            'absent': student_attendances.filter(status='ABSENT').count(),
            'late': student_attendances.filter(status='LATE').count(),
            'excused': student_attendances.filter(status='EXCUSED').count(),
        }
        
        if student_stats[student.pk]['total'] > 0:
            student_stats[student.pk]['presence_rate'] = round(
                (student_stats[student.pk]['present'] / student_stats[student.pk]['total']) * 100, 1
            )
        else:
            student_stats[student.pk]['presence_rate'] = 0
    
    # Navigation mois précédent/suivant
    prev_month = start_date - timedelta(days=1)
    next_month = end_date + timedelta(days=1)
    
    context = {
        'classroom': classroom,
        'students': students,
        'current_date': current_date,
        'dates_in_month': dates_in_month,
        'attendance_data': attendance_data,
        'student_stats': student_stats,
        'prev_month': prev_month,
        'next_month': next_month,
        'status_choices': dict(Attendance.STATUS_CHOICES),
    }
    
    return render(request, 'academic/attendance_class.html', context)

@teacher_or_student_required  # Enseignants et élèves peuvent voir les notes
def grade_list(request):
    """Liste des notes avec filtres"""
    from django.db.models import Avg, Count
    
    # Récupérer les notes avec filtrage RBAC automatique
    grades = Grade.objects.for_role(request.user).select_related(
        'student__user', 'subject', 'teacher__user', 'classroom'
    )
    
    # Filtres
    classroom_id = request.GET.get('classroom')
    subject_id = request.GET.get('subject')
    student_id = request.GET.get('student')
    evaluation_type = request.GET.get('evaluation_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Filtrage par classe
    if classroom_id and classroom_id != 'None':
        try:
            grades = grades.filter(classroom_id=int(classroom_id))
        except (ValueError, TypeError):
            pass
    
    # Filtrage par matière
    if subject_id and subject_id != 'None':
        try:
            grades = grades.filter(subject_id=int(subject_id))
        except (ValueError, TypeError):
            pass
    
    # Filtrage par étudiant
    if student_id and student_id != 'None':
        try:
            grades = grades.filter(student_id=int(student_id))
        except (ValueError, TypeError):
            pass
    
    # Filtrage par type d'évaluation
    if evaluation_type and evaluation_type != 'None':
        grades = grades.filter(evaluation_type=evaluation_type)
    
    # Filtrage par dates
    if date_from:
        try:
            grades = grades.filter(date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    
    if date_to:
        try:
            grades = grades.filter(date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass
    
    # Si l'utilisateur est enseignant, filtrer ses notes
    if hasattr(request.user, 'teacher') and not request.user.is_superuser:
        grades = grades.filter(teacher=request.user.teacher)
    
    # Ordre pour la pagination
    grades = grades.order_by('-date', 'classroom__name', 'subject__name', 'student__user__last_name')
    
    # Pagination
    paginator = Paginator(grades, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Données pour les filtres
    classrooms = ClassRoom.objects.filter(
        academic_year__is_current=True
    ).order_by('level__name', 'name')
    
    subjects = Subject.objects.all().order_by('name')
    
    students = Student.objects.filter(
        enrollments__is_active=True
    ).select_related('user').order_by('user__last_name', 'user__first_name')
    
    # Statistiques
    total_grades = grades.count()
    if total_grades > 0:
        avg_score = grades.aggregate(avg=Avg('score'))['avg'] or 0
        # Calcul simple de la moyenne des pourcentages
        all_grades = grades.values('score', 'max_score')
        percentages = [(g['score'] / g['max_score']) * 100 for g in all_grades if g['max_score'] > 0]
        avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    else:
        avg_score = 0
        avg_percentage = 0
    
    context = {
        'grades': page_obj,
        'classrooms': classrooms,
        'subjects': subjects,
        'students': students,
        'evaluation_types': Grade.EVALUATION_TYPE_CHOICES,
        'filters': {
            'classroom': classroom_id,
            'subject': subject_id,
            'student': student_id,
            'evaluation_type': evaluation_type,
            'date_from': date_from,
            'date_to': date_to,
        },
        'stats': {
            'total': total_grades,
            'avg_score': round(avg_score, 2) if avg_score else 0,
            'avg_percentage': round(avg_percentage, 2) if avg_percentage else 0,
        }
    }
    
    return render(request, 'academic/grade_list.html', context)

@teacher_required  # Seuls les enseignants peuvent ajouter des notes
def grade_add(request):
    """Ajouter une nouvelle note"""
    if request.method == 'POST':
        # Récupération des données du formulaire
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        evaluation_name = request.POST.get('evaluation_name')
        evaluation_type = request.POST.get('evaluation_type')
        score = request.POST.get('score')
        max_score = request.POST.get('max_score')
        coefficient = request.POST.get('coefficient', 1)
        comments = request.POST.get('comments', '')
        date_given = request.POST.get('date_given')
        
        try:
            # Validation et création de la note
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            teacher = request.user.teacher_profile if hasattr(request.user, 'teacher_profile') else None
            
            # Cette vérification n'est plus nécessaire grâce au décorateur @teacher_required
            # L'enseignant est garanti d'exister grâce au décorateur
            
            grade = Grade.objects.create(
                student=student,
                teacher=teacher,
                subject=subject,
                classroom=student.current_class,
                evaluation_name=evaluation_name,
                evaluation_type=evaluation_type,
                score=float(score),
                max_score=float(max_score),
                coefficient=float(coefficient),
                comments=comments,
                date=datetime.strptime(date_given, '%Y-%m-%d').date() if date_given else timezone.now().date()
            )
            
            messages.success(request, f"Note ajoutée avec succès pour {student.user.get_full_name()}")
            return redirect('academic:grade_list')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout de la note: {str(e)}")
    
    # Données pour le formulaire
    subjects = Subject.objects.all()
    classrooms = ClassRoom.objects.all()
    students = Student.objects.select_related('user', 'current_class').all()
    
    context = {
        'subjects': subjects,
        'classrooms': classrooms,
        'students': students,
        'evaluation_types': Grade.EVALUATION_TYPE_CHOICES,
    }
    
    return render(request, 'academic/grade_add.html', context)


@login_required
def student_grades(request, student_id):
    """Afficher toutes les notes d'un étudiant"""
    student = get_object_or_404(Student, id=student_id)
    
    # Filtrage par matière et période
    subject_filter = request.GET.get('subject')
    period_filter = request.GET.get('period')
    
    grades = Grade.objects.filter(student=student).select_related(
        'teacher__user', 'subject'
    ).order_by('-date')
    
    if subject_filter:
        grades = grades.filter(subject_id=subject_filter)
    
    if period_filter:
        current_year = timezone.now().year
        if period_filter == 'trimester1':
            grades = grades.filter(date__year=current_year, date__month__lte=4)
        elif period_filter == 'trimester2':
            grades = grades.filter(date__year=current_year, date__month__gte=5, date__month__lte=8)
        elif period_filter == 'trimester3':
            grades = grades.filter(date__year=current_year, date__month__gte=9)
    
    # Statistiques par matière
    subjects_stats = {}
    for grade in grades:
        subject = grade.subject
        if subject.name not in subjects_stats:
            subjects_stats[subject.name] = {
                'grades': [],
                'average': 0,
                'count': 0
            }
        subjects_stats[subject.name]['grades'].append(grade.percentage)
        subjects_stats[subject.name]['count'] += 1
    
    # Calcul des moyennes
    for subject_name, stats in subjects_stats.items():
        if stats['grades']:
            stats['average'] = sum(stats['grades']) / len(stats['grades'])
    
    # Moyenne générale
    all_percentages = [grade.percentage for grade in grades]
    general_average = sum(all_percentages) / len(all_percentages) if all_percentages else 0
    
    context = {
        'student': student,
        'grades': grades,
        'subjects': Subject.objects.all(),
        'subjects_stats': subjects_stats,
        'general_average': general_average,
        'total_grades': grades.count(),
    }
    
    return render(request, 'academic/student_grades.html', context)


@login_required  
def class_grades(request, classroom_id):
    """Afficher les notes d'une classe"""
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    students = Student.objects.filter(current_class=classroom).select_related('user')
    
    # Filtrage
    subject_filter = request.GET.get('subject')
    evaluation_type_filter = request.GET.get('evaluation_type')
    
    grades = Grade.objects.filter(
        student__current_class=classroom
    ).select_related('student__user', 'teacher__user', 'subject')
    
    if subject_filter:
        grades = grades.filter(subject_id=subject_filter)
    
    if evaluation_type_filter:
        grades = grades.filter(evaluation_type=evaluation_type_filter)
    
    # Statistiques de la classe
    class_stats = {}
    for student in students:
        student_grades = grades.filter(student=student)
        if student_grades.exists():
            avg_percentage = sum([g.percentage for g in student_grades]) / student_grades.count()
            class_stats[student.id] = {
                'student': student,
                'average': avg_percentage,
                'grades_count': student_grades.count(),
                'recent_grades': student_grades.order_by('-date')[:3]
            }
    
    # Moyenne de classe
    if class_stats:
        class_average = sum([s['average'] for s in class_stats.values()]) / len(class_stats)
    else:
        class_average = 0
    
    context = {
        'classroom': classroom,
        'students': students,
        'grades': grades.order_by('-date'),
        'subjects': Subject.objects.all(),
        'class_stats': class_stats,
        'class_average': class_average,
        'evaluation_types': Grade.EVALUATION_TYPE_CHOICES,
    }
    
    return render(request, 'academic/class_grades.html', context)

def student_bulletin(request, student_id):
    return HttpResponse(f"Bulletin de l'élève {student_id} - En cours de développement")

def class_report(request, classroom_id):
    return HttpResponse(f"Rapport de la classe {classroom_id} - En cours de développement")
