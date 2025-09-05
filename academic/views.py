from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime

from .models import (
    AcademicYear, Level, Subject, ClassRoom, 
    TeacherAssignment, Enrollment, Grade, Attendance, Timetable
)
from accounts.models import Teacher, Student


@login_required
def classroom_list(request):
    """Liste des classes avec filtrage et recherche"""
    classrooms = ClassRoom.objects.select_related(
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
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        
        if action == 'add' and student_id:
            try:
                student = get_object_or_404(Student, id=student_id)
                
                # Vérifier si déjà inscrit
                existing = Enrollment.objects.filter(
                    student=student,
                    academic_year=classroom.academic_year,
                    is_active=True
                ).exists()
                
                if existing:
                    messages.error(request, f'{student.user.get_full_name()} est déjà inscrit cette année.')
                elif classroom.is_full:
                    messages.error(request, 'La classe a atteint sa capacité maximale.')
                else:
                    Enrollment.objects.create(
                        student=student,
                        classroom=classroom,
                        academic_year=classroom.academic_year
                    )
                    messages.success(request, f'{student.user.get_full_name()} a été inscrit dans la classe.')
                    
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'inscription : {str(e)}')
        
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
                
                messages.success(request, 'L\'élève a été retiré de la classe.')
                
            except Exception as e:
                messages.error(request, f'Erreur lors du retrait : {str(e)}')
        
        return redirect('academic:enrollment_manage', classroom_id=classroom.id)
    
    # Étudiants inscrits
    enrollments = Enrollment.objects.filter(
        classroom=classroom, 
        is_active=True
    ).select_related('student__user')
    
    # Étudiants disponibles pour inscription
    enrolled_student_ids = enrollments.values_list('student_id', flat=True)
    available_students = Student.objects.select_related('user').exclude(
        id__in=enrolled_student_ids
    ).exclude(
        enrollments__academic_year=classroom.academic_year,
        enrollments__is_active=True
    ).filter(user__is_active=True)
    
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

def classroom_timetable(request, classroom_id):
    return HttpResponse(f"Emploi du temps de la classe {classroom_id} - En cours de développement")

def timetable_list(request):
    return HttpResponse("Liste des emplois du temps - En cours de développement")

def timetable_create(request):
    return HttpResponse("Créer un emploi du temps - En cours de développement")

def attendance_list(request):
    return HttpResponse("Liste des présences - En cours de développement")

def attendance_take(request):
    return HttpResponse("Faire l'appel - En cours de développement")

def attendance_class(request, classroom_id):
    return HttpResponse(f"Présences de la classe {classroom_id} - En cours de développement")

def grade_list(request):
    return HttpResponse("Liste des notes - En cours de développement")

def grade_add(request):
    return HttpResponse("Ajouter une note - En cours de développement")

def student_grades(request, student_id):
    return HttpResponse(f"Notes de l'élève {student_id} - En cours de développement")

def class_grades(request, classroom_id):
    return HttpResponse(f"Notes de la classe {classroom_id} - En cours de développement")

def student_bulletin(request, student_id):
    return HttpResponse(f"Bulletin de l'élève {student_id} - En cours de développement")

def class_report(request, classroom_id):
    return HttpResponse(f"Rapport de la classe {classroom_id} - En cours de développement")
