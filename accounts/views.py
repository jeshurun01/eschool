from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import date, timedelta
from .models import User, Student, Parent, Teacher
from academic.models import ClassRoom, Subject, Attendance, Enrollment, Level, Grade
from finance.models import Invoice, Payment, FeeStructure
from communication.models import Announcement, Message
from .forms import (
    UserRegistrationForm, CustomLoginForm, ProfileEditForm,
    StudentProfileForm, TeacherProfileForm, ParentProfileForm,
    AdminUserCreateForm, PasswordChangeForm
)


# Fonctions utilitaires pour les permissions
def is_admin_or_staff(user):
    """Vérifie si l'utilisateur est admin ou staff"""
    return user.is_authenticated and (user.role in ['ADMIN', 'SUPER_ADMIN'] or user.is_staff)


def admin_required(view_func):
    """Décorateur pour les vues nécessitant des droits admin"""
    return user_passes_test(is_admin_or_staff)(view_func)


# Vues d'authentification

@csrf_protect
@login_required
@admin_required
def register_view(request):
    """Vue d'inscription des utilisateurs - Réservée au staff"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Compte créé avec succès pour {user.first_name} {user.last_name}.')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Erreur lors de la création du compte. Vérifiez les informations.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/user_create.html', {'form': form})


@csrf_protect
def login_view(request):
    """Vue de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Use the backend that was used during authentication
            login(request, user, backend=getattr(user, 'backend', 'django.contrib.auth.backends.ModelBackend'))
            
            # Session persistante si demandée
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            # Redirection selon le rôle
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            return redirect('accounts:dashboard')
    else:
        form = CustomLoginForm()
    
    return render(request, 'account/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accounts:login')


# Vues principales

@login_required
def dashboard(request):
    """Dashboard principal basé sur le rôle de l'utilisateur"""
    context = {
        'user': request.user,
    }
    
    # Dashboard administrateur
    if request.user.role in ['ADMIN', 'SUPER_ADMIN'] or request.user.is_staff:
        return admin_dashboard(request)
    
    # Dashboard élève
    elif request.user.role == 'STUDENT':
        return student_dashboard(request)
    
    # Dashboard enseignant
    elif request.user.role == 'TEACHER':
        return teacher_dashboard(request)
    
    # Dashboard parent
    elif request.user.role == 'PARENT':
        return parent_dashboard(request)
    
    # Dashboard par défaut
    return render(request, 'accounts/dashboard.html', context)


@admin_required
def admin_dashboard(request):
    """Dashboard spécialisé pour les administrateurs"""
    today = date.today()
    now = timezone.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Statistiques principales
    stats = {
        # Utilisateurs
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_parents': Parent.objects.count(),
        'total_users': User.objects.filter(is_active=True).count(),
        
        # Académique
        'total_classes': ClassRoom.objects.count(),
        'total_subjects': Subject.objects.count(),
        'active_enrollments': Enrollment.objects.filter(
            withdrawal_date__isnull=True
        ).count(),
        
        # Présences du jour
        'today_attendances': Attendance.objects.filter(date=today).count(),
        'today_absences': Attendance.objects.filter(
            date=today, 
            status='ABSENT'
        ).count(),
        
        # Financier
        'total_invoices': Invoice.objects.count(),
        'pending_invoices': Invoice.objects.filter(status='PENDING').count(),
        'total_revenue': Payment.objects.filter(
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'month_revenue': Payment.objects.filter(
            status='COMPLETED',
            payment_date__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Activité récente
    recent_activity = {
        'new_students': Student.objects.filter(
            user__date_joined__gte=week_ago
        ).order_by('-user__date_joined')[:5],
        
        'recent_payments': Payment.objects.filter(
            status='COMPLETED',
            payment_date__gte=week_ago
        ).order_by('-payment_date')[:5],
        
        'pending_invoices': Invoice.objects.filter(
            status='PENDING'
        ).order_by('-due_date')[:5],
    }
    
    # Moyennes et statistiques académiques
    academic_stats = {
        'avg_class_size': ClassRoom.objects.annotate(
            student_count=Count('enrollments')
        ).aggregate(avg=Avg('student_count'))['avg'] or 0,
        
        'attendance_rate': 0,  # À calculer plus tard si besoin
    }
    
    # Graphiques données (pour futurs charts)
    chart_data = {
        'student_growth': [],  # Évolution des inscriptions
        'revenue_trend': [],   # Évolution des revenus
        'attendance_trend': [],  # Évolution des présences
    }
    
    context = {
        'user': request.user,
        'stats': stats,
        'recent_activity': recent_activity,
        'academic_stats': academic_stats,
        'chart_data': chart_data,
        'today': today,
        'now': now,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def student_dashboard(request):
    """Dashboard spécialisé pour les étudiants"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Profil étudiant non trouvé.')
        return redirect('accounts:profile')
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Informations de base
    context = {
        'student': student,
        'current_class': student.current_class,
        'today': timezone.now(),
    }
    
    # Initialisation par défaut
    recent_grades = Grade.objects.none()
    
    # Statistiques académiques
    if student.current_class:
        # Notes récentes avec calcul du pourcentage
        recent_grades = Grade.objects.filter(
            student=student
        ).select_related('subject', 'teacher').order_by('-created_at')[:5]
        
        # Le pourcentage est calculé automatiquement par la propriété @percentage du modèle Grade
        
        # Moyenne générale
        student_grades = Grade.objects.filter(student=student)
        if student_grades.exists():
            avg_grade = student_grades.aggregate(avg=Avg('score'))['avg']
            context['average_grade'] = round(avg_grade, 2) if avg_grade else None
            context['average_percentage'] = round((avg_grade / 20) * 100, 1) if avg_grade else 0
        
        # Présences du mois
        monthly_attendances = Attendance.objects.filter(
            student=student,
            date__gte=month_ago
        )
        present_count = monthly_attendances.filter(status='PRESENT').count()
        total_days = monthly_attendances.count()
        attendance_rate = round((present_count / total_days * 100), 1) if total_days > 0 else 0
        
        context.update({
            'recent_grades': recent_grades,
            'attendance_rate': attendance_rate,
            'monthly_attendances': {
                'present': present_count,
                'absent': monthly_attendances.filter(status='ABSENT').count(),
                'late': monthly_attendances.filter(status='LATE').count(),
                'total': total_days,
                'attendance_rate': attendance_rate
            }
        })
        
        # Prochains cours (emploi du temps)
        from academic.models import Timetable
        next_classes_query = Timetable.objects.filter(
            classroom=student.current_class
        ).select_related('subject', 'teacher').order_by('weekday', 'start_time')[:5]
        
        # Transformer les données pour le template
        next_classes = []
        for timetable in next_classes_query:
            class_data = {
                'subject': timetable.subject.name,
                'teacher': timetable.teacher.user.get_full_name(),
                'room': timetable.classroom.room_number if hasattr(timetable.classroom, 'room_number') else '--',
                'time': timezone.now().replace(hour=timetable.start_time.hour, minute=timetable.start_time.minute),
                'duration': 60,  # Durée par défaut
            }
            next_classes.append(class_data)
        
        context['next_classes'] = next_classes
    
    # Devoirs et assignements à venir (simulation)
    context['pending_assignments'] = 3  # Valeur simulée
    
    # Messages non lus (simulation)
    context['unread_messages'] = 2  # Valeur simulée
    
    # Informations financières
    pending_invoices = Invoice.objects.filter(
        student=student,
        status__in=['PENDING', 'SENT']
    ).order_by('-due_date')[:3]
    
    recent_payments = Payment.objects.filter(
        invoice__student=student,
        status='COMPLETED'
    ).select_related('invoice').order_by('-payment_date')[:3]
    
    context.update({
        'pending_invoices': pending_invoices,
        'recent_payments': recent_payments,
        'total_pending_amount': pending_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
    })
    
    # Annonces récentes (simulation)
    from communication.models import Announcement
    try:
        recent_announcements = Announcement.objects.filter(
            target_classes=student.current_class
        ).order_by('-created_at')[:3]
    except:
        recent_announcements = []
    
    context['recent_announcements'] = recent_announcements
    
    # Activités récentes
    recent_activities = []
    
    # Ajout des notes récentes
    for grade in recent_grades:
        recent_activities.append({
            'type': 'grade',
            'icon': 'academic-cap',
            'title': f'Note en {grade.subject.name}',
            'description': f'{grade.score}/20 - {grade.evaluation_type}',
            'date': grade.created_at,
            'color': 'green' if grade.score >= 12 else 'yellow' if grade.score >= 10 else 'red'
        })
    
    # Ajout des paiements récents
    for payment in recent_payments:
        recent_activities.append({
            'type': 'payment',
            'icon': 'credit-card',
            'title': 'Paiement effectué',
            'description': f'{payment.amount} FCFA - {payment.invoice.invoice_number}',
            'date': payment.payment_date,
            'color': 'green'
        })
    
    # Tri par date décroissante
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    context['recent_activities'] = recent_activities[:10]
    
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Dashboard spécialisé pour les enseignants"""
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        messages.error(request, 'Profil enseignant non trouvé.')
        return redirect('accounts:profile')
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Classes assignées à l'enseignant
    assigned_classes = teacher.assigned_classes.all()
    total_students = 0
    for class_obj in assigned_classes:
        total_students += class_obj.students.count()
    
    # Matières enseignées
    subjects = teacher.subjects.all()
    
    # Cours de l'enseignant (TeacherAssignment) avec année courante
    from academic.models import TeacherAssignment, AcademicYear
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    teacher_courses = TeacherAssignment.objects.filter(
        teacher=teacher,
        academic_year=current_year if current_year else AcademicYear.objects.first()
    ).select_related('classroom', 'subject', 'academic_year').order_by('classroom__name', 'subject__name')
    
    # Notes récentes données par l'enseignant
    recent_grades = Grade.objects.filter(
        teacher=teacher
    ).select_related('student__user', 'subject').order_by('-created_at')[:10]
    
    # Statistiques des notes
    grades_this_month = Grade.objects.filter(
        teacher=teacher,
        created_at__gte=month_ago
    )
    
    average_grade = grades_this_month.aggregate(avg=Avg('score'))['avg'] or 0
    total_grades_given = grades_this_month.count()
    
    # Présences du jour pour les classes de l'enseignant
    today_attendance = Attendance.objects.filter(
        teacher=teacher,
        date=today
    ).select_related('student__user', 'classroom')
    
    attendance_stats = {
        'present': today_attendance.filter(status='PRESENT').count(),
        'absent': today_attendance.filter(status='ABSENT').count(),
        'late': today_attendance.filter(status='LATE').count(),
        'excused': today_attendance.filter(status='EXCUSED').count(),
    }
    attendance_stats['total'] = sum(attendance_stats.values())
    attendance_stats['attendance_rate'] = int(
        (attendance_stats['present'] / attendance_stats['total'] * 100) 
        if attendance_stats['total'] > 0 else 0
    )
    
    # Emploi du temps de la semaine (simulé pour le moment)
    from django.utils import timezone
    import calendar
    
    # Obtenir le début de la semaine (lundi)
    today_weekday = today.weekday()
    week_start = today - timedelta(days=today_weekday)
    
    # Créer un emploi du temps basique (à remplacer par un vrai modèle Schedule plus tard)
    weekly_schedule = []
    weekdays = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    
    for i, day_name in enumerate(weekdays):
        day_date = week_start + timedelta(days=i)
        day_classes = []
        
        # Simulation de cours (à remplacer par de vraies données)
        for j, class_obj in enumerate(assigned_classes[:3]):  # Limite à 3 classes par jour
            if j < len(subjects):
                start_time = f"{8 + j*2}:00"
                end_time = f"{10 + j*2}:00"
                day_classes.append({
                    'subject': subjects[j % len(subjects)],
                    'class_room': class_obj,
                    'start_time': start_time,
                    'end_time': end_time,
                    'room': f"Salle {j+1}",
                })
        
        weekly_schedule.append({
            'day': day_name,
            'date': day_date,
            'classes': day_classes,
            'is_today': day_date == today
        })
    
    # Activités récentes
    recent_activities = []
    
    # Ajout des notes récentes
    for grade in recent_grades[:5]:
        recent_activities.append({
            'type': 'grade',
            'icon': 'academic-cap',
            'title': f'Note attribuée en {grade.subject.name}',
            'description': f'{grade.student.user.first_name} {grade.student.user.last_name} - {grade.score}/20',
            'date': grade.created_at.date() if hasattr(grade.created_at, 'date') else grade.created_at,
            'color': 'blue'
        })
    
    # Ajout des présences récentes
    recent_attendance = Attendance.objects.filter(
        teacher=teacher,
        date__gte=week_ago
    ).select_related('student__user', 'classroom').order_by('-date')[:5]
    
    for attendance in recent_attendance:
        status_colors = {
            'PRESENT': 'green',
            'ABSENT': 'red',
            'LATE': 'yellow',
            'EXCUSED': 'blue'
        }
        recent_activities.append({
            'type': 'attendance',
            'icon': 'user-check',
            'title': f'Présence enregistrée',
            'description': f'{attendance.student.user.first_name} {attendance.student.user.last_name} - {attendance.status}',
            'date': attendance.date,
            'color': status_colors.get(attendance.status, 'gray')
        })
    
    # Tri par date décroissante
    def get_date(activity):
        date_value = activity['date']
        # Convertir en date si c'est un datetime
        if hasattr(date_value, 'date'):
            return date_value.date()
        return date_value
    
    recent_activities.sort(key=get_date, reverse=True)
    
    # Classes avec le plus d'absences cette semaine (pour cet enseignant)
    classes_with_absences = []
    for class_obj in assigned_classes:
        week_absences = Attendance.objects.filter(
            teacher=teacher,
            classroom=class_obj,
            date__gte=week_ago,
            status='ABSENT'
        ).count()
        
        if week_absences > 0:
            classes_with_absences.append({
                'class': class_obj,
                'absences': week_absences
            })
    
    classes_with_absences.sort(key=lambda x: x['absences'], reverse=True)
    
    context = {
        'teacher': teacher,
        'assigned_classes': assigned_classes,
        'subjects': subjects,
        'teacher_courses': teacher_courses,
        'total_students': total_students,
        'recent_grades': recent_grades[:5],
        'attendance_stats': attendance_stats,
        'weekly_schedule': weekly_schedule,
        'recent_activities': recent_activities[:10],
        'classes_with_absences': classes_with_absences[:5],
        'stats': {
            'total_classes': assigned_classes.count(),
            'total_subjects': subjects.count(),
            'total_students': total_students,
            'average_grade': round(average_grade, 1),
            'total_grades_given': total_grades_given,
            'attendance_rate': round(attendance_stats['attendance_rate'], 1)
        },
        'today': today,
    }
    
    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
def parent_dashboard(request):
    """Dashboard spécialisé pour les parents"""
    try:
        parent = request.user.parent_profile
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('accounts:profile')
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Enfants du parent
    children = parent.children.all()
    
    if not children.exists():
        # Si aucun enfant n'est associé, afficher un message
        context = {
            'parent': parent,
            'children': children,
            'no_children': True,
            'today': today,
        }
        return render(request, 'accounts/parent_dashboard.html', context)
    
    # Statistiques générales
    total_children = children.count()
    
    # Collecte des données pour tous les enfants
    children_data = []
    overall_stats = {
        'total_grades': 0,
        'total_average': 0,
        'total_absences': 0,
        'total_pending_amount': 0,
    }
    
    for child in children:
        # Notes récentes de l'enfant
        recent_grades = Grade.objects.filter(
            student=child
        ).select_related('subject', 'teacher').order_by('-created_at')[:5]
        
        # Moyenne générale de l'enfant
        all_grades = Grade.objects.filter(student=child)
        average_grade = all_grades.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Présences de l'enfant cette semaine
        week_attendance = Attendance.objects.filter(
            student=child,
            date__gte=week_ago
        )
        
        attendance_stats = {
            'present': week_attendance.filter(status='PRESENT').count(),
            'absent': week_attendance.filter(status='ABSENT').count(),
            'late': week_attendance.filter(status='LATE').count(),
            'excused': week_attendance.filter(status='EXCUSED').count(),
        }
        attendance_stats['total'] = sum(attendance_stats.values())
        attendance_stats['attendance_rate'] = int(
            (attendance_stats['present'] / attendance_stats['total'] * 100) 
            if attendance_stats['total'] > 0 else 100
        )
        
        # Absences non justifiées
        recent_absences = Attendance.objects.filter(
            student=child,
            status='ABSENT',
            date__gte=week_ago,
            justification__isnull=True
        ).order_by('-date')[:3]
        
        # Informations financières de l'enfant
        pending_invoices = Invoice.objects.filter(
            student=child,
            status__in=['PENDING', 'SENT']
        ).order_by('-due_date')
        
        total_pending = pending_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        recent_payments = Payment.objects.filter(
            invoice__student=child,
            status='COMPLETED'
        ).select_related('invoice').order_by('-payment_date')[:3]
        
        # Prochains cours (simulé)
        next_classes = []
        if child.current_class:
            # Simulation de cours à venir
            for i in range(3):
                next_classes.append({
                    'subject': f'Matière {i+1}',
                    'time': f'{8+i*2}:00',
                    'teacher': f'Enseignant {i+1}',
                    'room': f'Salle {i+1}'
                })
        
        child_data = {
            'student': child,
            'recent_grades': recent_grades,
            'average_grade': round(average_grade, 2),
            'attendance_stats': attendance_stats,
            'recent_absences': recent_absences,
            'pending_invoices': pending_invoices,
            'total_pending': total_pending,
            'recent_payments': recent_payments,
            'next_classes': next_classes,
            'grade_trend': 'up' if average_grade >= 12 else 'down',  # Simulation
        }
        
        children_data.append(child_data)
        
        # Mise à jour des statistiques globales
        overall_stats['total_grades'] += all_grades.count()
        overall_stats['total_average'] += average_grade
        overall_stats['total_absences'] += attendance_stats['absent']
        overall_stats['total_pending_amount'] += total_pending
    
    # Calcul des moyennes globales
    if total_children > 0:
        overall_stats['average_grade'] = round(overall_stats['total_average'] / total_children, 2)
        overall_stats['average_absences'] = round(overall_stats['total_absences'] / total_children, 1)
    else:
        overall_stats['average_grade'] = 0
        overall_stats['average_absences'] = 0
    
    # Activités récentes de tous les enfants
    recent_activities = []
    
    # Ajout des notes récentes
    for child_data in children_data:
        for grade in child_data['recent_grades']:
            recent_activities.append({
                'type': 'grade',
                'icon': 'academic-cap',
                'title': f'Nouvelle note - {child_data["student"].user.first_name}',
                'description': f'{grade.subject.name}: {grade.score}/20',
                'date': grade.created_at,
                'color': 'green' if grade.score >= 12 else 'yellow' if grade.score >= 10 else 'red',
                'child': child_data['student']
            })
    
    # Ajout des absences récentes
    for child_data in children_data:
        for absence in child_data['recent_absences']:
            recent_activities.append({
                'type': 'absence',
                'icon': 'exclamation-triangle',
                'title': f'Absence - {child_data["student"].user.first_name}',
                'description': f'Absent le {absence.date.strftime("%d/%m/%Y")}',
                'date': absence.date,
                'color': 'red',
                'child': child_data['student']
            })
    
    # Ajout des paiements récents
    for child_data in children_data:
        for payment in child_data['recent_payments']:
            recent_activities.append({
                'type': 'payment',
                'icon': 'credit-card',
                'title': f'Paiement effectué - {child_data["student"].user.first_name}',
                'description': f'{payment.amount} FCFA - {payment.invoice.invoice_number}',
                'date': payment.payment_date,
                'color': 'green',
                'child': child_data['student']
            })
    
    # Tri par date décroissante
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Événements à venir (simulés)
    upcoming_events = [
        {
            'title': 'Réunion parents-enseignants',
            'date': today + timedelta(days=7),
            'time': '14:00',
            'type': 'meeting'
        },
        {
            'title': 'Remise des bulletins',
            'date': today + timedelta(days=14),
            'time': '10:00',
            'type': 'academic'
        },
        {
            'title': 'Journée portes ouvertes',
            'date': today + timedelta(days=21),
            'time': '09:00',
            'type': 'event'
        }
    ]
    
    context = {
        'parent': parent,
        'children': children,
        'children_data': children_data,
        'total_children': total_children,
        'overall_stats': overall_stats,
        'recent_activities': recent_activities[:15],
        'upcoming_events': upcoming_events,
        'stats': {
            'total_children': total_children,
            'average_grade': overall_stats['average_grade'],
            'total_pending_amount': overall_stats['total_pending_amount'],
            'total_absences': overall_stats['total_absences']
        },
        'today': today,
    }
    
    return render(request, 'accounts/parent_dashboard.html', context)


@login_required
def profile_view(request):
    """Afficher le profil de l'utilisateur"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    """Modifier le profil de l'utilisateur"""
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile')
    else:
        profile_form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'profile_form': profile_form})


@login_required
def change_password(request):
    """Changer le mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mot de passe changé avec succès.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


# Vues de gestion des utilisateurs (Admin)

def is_admin(user):
    """Vérifier si l'utilisateur est administrateur"""
    return user.is_authenticated and user.role in ['ADMIN', 'SUPER_ADMIN']


@user_passes_test(is_admin)
def user_list(request):
    """Liste des utilisateurs"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Ordre pour la pagination
    users = users.order_by('last_name', 'first_name')
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': User.ROLE_CHOICES,
    }
    
    return render(request, 'accounts/user_list.html', context)


@user_passes_test(is_admin)
def user_create(request):
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Créer le profil spécifique selon le rôle
            if user.role == 'STUDENT':
                Student.objects.create(user=user)
            elif user.role == 'TEACHER':
                Teacher.objects.create(user=user)
            elif user.role == 'PARENT':
                Parent.objects.create(user=user)
            
            messages.success(request, f'Utilisateur {user.full_name} créé avec succès.')
            return redirect('accounts:user_detail', user_id=user.pk)
    else:
        form = AdminUserCreateForm()
    
    return render(request, 'accounts/user_create.html', {'form': form})


@user_passes_test(is_admin)
def user_detail(request, user_id):
    """Détails d'un utilisateur"""
    user_obj = get_object_or_404(User, id=user_id)
    context = {'user_obj': user_obj}
    return render(request, 'accounts/user_detail.html', context)


@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Modifier un utilisateur"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Utilisateur {user_obj.full_name} modifié avec succès.')
            return redirect('accounts:user_detail', user_id=user_obj.pk)
    else:
        form = ProfileEditForm(instance=user_obj)
    
    return render(request, 'accounts/user_edit.html', {'form': form, 'user_obj': user_obj})


@user_passes_test(is_admin)
@require_http_methods(["POST"])
def user_toggle_active(request, user_id):
    """Activer/désactiver un utilisateur"""
    user_obj = get_object_or_404(User, id=user_id)
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    
    status = "activé" if user_obj.is_active else "désactivé"
    messages.success(request, f'Utilisateur {user_obj.full_name} {status}.')
    
    # Retourner JSON pour les requêtes AJAX (fetch ou HTMX)
    if request.headers.get('HX-Request') or request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'success': True,
            'is_active': user_obj.is_active,
            'message': f'Utilisateur {status}'
        })
    
    return redirect('accounts:user_detail', user_id=user_obj.pk)


# Vues spécifiques par rôle

@user_passes_test(is_admin_or_staff)
def student_list(request):
    """Liste des élèves"""
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class', '')
    
    students = Student.objects.select_related('user', 'current_class').all()
    
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(matricule__icontains=search_query)
        )
    
    if class_filter:
        students = students.filter(current_class_id=class_filter)
    
    # Ordre pour la pagination
    students = students.order_by('user__last_name', 'user__first_name')
    
    # Pagination
    paginator = Paginator(students, 20)
    page = request.GET.get('page')
    students = paginator.get_page(page)
    
    # Import ici pour éviter les imports circulaires
    from academic.models import ClassRoom
    classes = ClassRoom.objects.all()
    
    context = {
        'students': students,
        'search_query': search_query,
        'class_filter': class_filter,
        'classes': classes,
    }
    
    return render(request, 'accounts/student_list.html', context)


# Vues placeholder pour le développement futur
def student_create(request):
    return HttpResponse("Créer un élève - En cours de développement")

@user_passes_test(is_admin_or_staff)
def student_detail(request, student_id):
    """Détail d'un élève"""
    student = get_object_or_404(Student, id=student_id)
    
    context = {
        'student': student,
    }
    return render(request, 'accounts/student_detail.html', context)

@user_passes_test(is_admin_or_staff)
def student_edit(request, student_id):
    """Modifier un élève"""
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    
    if request.method == 'POST':
        # Données utilisateur de base
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.date_of_birth = request.POST.get('date_of_birth') or user.date_of_birth
        user.gender = request.POST.get('gender', user.gender)
        
        # Données spécifiques à l'élève
        student.matricule = request.POST.get('matricule', student.matricule)
        
        # Assignation de classe si fournie
        class_id = request.POST.get('current_class')
        if class_id:
            from academic.models import ClassRoom
            try:
                classroom = ClassRoom.objects.get(id=class_id)
                student.current_class = classroom
            except ClassRoom.DoesNotExist:
                pass
        
        try:
            user.save()
            student.save()
            messages.success(request, f'Élève {user.full_name} modifié avec succès.')
            return redirect('accounts:student_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    # Import ici pour éviter les imports circulaires
    from academic.models import ClassRoom
    classes = ClassRoom.objects.all()
    
    context = {
        'student': student,
        'user': user,
        'classes': classes,
    }
    return render(request, 'accounts/student_edit.html', context)

@login_required
@admin_required
def parent_list(request):
    """Liste des parents avec recherche et filtres"""
    from django.core.paginator import Paginator
    
    # Récupérer tous les parents
    parents = Parent.objects.select_related('user').prefetch_related('children__user')
    
    # Filtres de recherche
    search_query = request.GET.get('search', '')
    relationship_filter = request.GET.get('relationship', '')
    has_children = request.GET.get('has_children', '')
    
    # Appliquer les filtres
    if search_query:
        parents = parents.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(profession__icontains=search_query) |
            Q(workplace__icontains=search_query)
        )
    
    if relationship_filter:
        parents = parents.filter(relationship=relationship_filter)
    
    if has_children == 'with_children':
        parents = parents.filter(children__isnull=False).distinct()
    elif has_children == 'without_children':
        parents = parents.filter(children__isnull=True)
    
    # Trier les résultats
    sort_by = request.GET.get('sort', 'user__last_name')
    if sort_by in ['user__last_name', '-user__last_name', 'user__first_name', '-user__first_name', 
                   'relationship', '-relationship', 'created_at', '-created_at']:
        parents = parents.order_by(sort_by)
    else:
        parents = parents.order_by('user__last_name')
    
    # Pagination
    paginator = Paginator(parents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_parents = Parent.objects.count()
    active_parents = Parent.objects.filter(user__is_active=True).count()
    parents_with_children = Parent.objects.filter(children__isnull=False).distinct().count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'relationship_filter': relationship_filter,
        'has_children': has_children,
        'sort_by': sort_by,
        'total_parents': total_parents,
        'active_parents': active_parents,
        'parents_with_children': parents_with_children,
        'relationship_choices': Parent._meta.get_field('relationship').choices,
    }
    
    return render(request, 'accounts/parent_list.html', context)


@login_required
@admin_required
def parent_create(request):
    """Créer un nouveau parent"""
    if request.method == 'POST':
        user_form = AdminUserCreateForm(request.POST)
        parent_form = ParentProfileForm(request.POST)
        
        if user_form.is_valid() and parent_form.is_valid():
            # Créer l'utilisateur
            user = user_form.save(commit=False)
            user.role = 'PARENT'
            user.save()
            
            # Créer le profil parent
            parent = parent_form.save(commit=False)
            parent.user = user
            parent.save()
            
            messages.success(request, f'Parent {user.get_full_name()} créé avec succès.')
            return redirect('accounts:parent_detail', parent_id=parent.id)
        else:
            # Afficher les erreurs de débogage
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Erreur dans {field}: {error}')
            
            if not parent_form.is_valid():
                for field, errors in parent_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Erreur dans {field}: {error}')
            
            messages.error(request, 'Erreur lors de la création du parent. Vérifiez les informations.')
    else:
        user_form = AdminUserCreateForm(initial={'role': 'PARENT'})
        parent_form = ParentProfileForm()
    
    context = {
        'user_form': user_form,
        'parent_form': parent_form,
    }
    
    return render(request, 'accounts/parent_create.html', context)


@login_required
@admin_required
def parent_detail(request, parent_id):
    """Détails d'un parent"""
    parent = get_object_or_404(Parent, id=parent_id)
    
    # Statistiques des enfants
    children = parent.children.all()
    children_data = []
    
    for child in children:
        # Récupérer les informations académiques
        enrollments = Enrollment.objects.filter(student=child).select_related('classroom', 'classroom__level')
        current_enrollment = enrollments.filter(
            classroom__academic_year__is_current=True
        ).first() if enrollments.exists() else None
        
        # Récupérer les factures récentes
        recent_invoices = Invoice.objects.filter(
            student=child
        ).order_by('-created_at')[:3]
        
        # Récupérer les présences récentes
        recent_attendance = Attendance.objects.filter(
            student=child
        ).order_by('-date')[:5]
        
        children_data.append({
            'student': child,
            'current_enrollment': current_enrollment,
            'recent_invoices': recent_invoices,
            'recent_attendance': recent_attendance,
        })
    
    # Statistiques financières
    total_invoices = Invoice.objects.filter(student__in=children).count()
    total_amount = Invoice.objects.filter(student__in=children).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    paid_amount = Payment.objects.filter(
        invoice__student__in=children
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'parent': parent,
        'children_data': children_data,
        'total_invoices': total_invoices,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'balance': total_amount - paid_amount,
    }
    
    return render(request, 'accounts/parent_detail.html', context)


@login_required
@admin_required
def admin_children_overview(request):
    """Vue d'ensemble de tous les enfants pour les administrateurs"""
    # Filtres
    parent_id = request.GET.get('parent')
    class_id = request.GET.get('class')
    search = request.GET.get('search', '').strip()
    
    # Base queryset
    students = Student.objects.select_related('user', 'current_class').all()
    
    # Applique les filtres
    if parent_id:
        students = students.filter(parents__id=parent_id)
    
    if class_id:
        students = students.filter(current_class_id=class_id)
    
        if search:
            students = students.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(matricule__icontains=search)
            )    # Pagination
    paginator = Paginator(students, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Préparer les données détaillées pour chaque enfant
    children_data = []
    today = date.today()
    start_of_month = today.replace(day=1)
    
    for student in page_obj:
        # Informations académiques récentes
        recent_grades = Grade.objects.filter(
            student=student,
            created_at__gte=start_of_month
        ).select_related('subject')
        
        average_grade = recent_grades.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Présences du mois
        monthly_attendance = Attendance.objects.filter(
            student=student,
            date__gte=start_of_month
        )
        
        attendance_rate = 0
        if monthly_attendance.exists():
            present_count = monthly_attendance.filter(status='PRESENT').count()
            attendance_rate = round((present_count / monthly_attendance.count()) * 100, 1)
        
        # Situation financière
        pending_invoices = Invoice.objects.filter(
            student=student,
            status__in=['DRAFT', 'SENT']
        )
        
        overdue_invoices = Invoice.objects.filter(
            student=student,
            status='OVERDUE'
        )
        
        total_pending = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_overdue = overdue_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Parents
        parents = student.parents.all()
        
        # Inscription actuelle
        current_enrollment = Enrollment.objects.filter(
            student=student,
            is_active=True
        ).select_related('classroom', 'classroom__level').first()
        
        children_data.append({
            'student': student,
            'current_enrollment': current_enrollment,
            'parents': parents,
            'recent_grades_count': recent_grades.count(),
            'average_grade': round(average_grade, 2),
            'attendance_rate': attendance_rate,
            'total_pending': total_pending,
            'total_overdue': total_overdue,
            'financial_status': 'danger' if total_overdue > 0 else 'warning' if total_pending > 0 else 'success',
            'academic_status': 'excellent' if average_grade >= 16 else 'good' if average_grade >= 12 else 'needs_improvement' if average_grade >= 8 else 'poor'
        })
    
    # Statistiques globales
    total_students = students.count()
    total_with_parents = students.filter(parents__isnull=False).distinct().count()
    total_without_parents = total_students - total_with_parents
    
    # Données pour les filtres
    all_parents = Parent.objects.select_related('user').all()
    all_classes = ClassRoom.objects.select_related('level').all()
    
    context = {
        'page_obj': page_obj,
        'children_data': children_data,
        'total_students': total_students,
        'total_with_parents': total_with_parents,
        'total_without_parents': total_without_parents,
        'all_parents': all_parents,
        'all_classes': all_classes,
        'current_parent': parent_id,
        'current_class': class_id,
        'search_query': search,
        'start_of_month': start_of_month,
    }
    
    return render(request, 'accounts/admin_children_overview.html', context)


@login_required
@admin_required
def parent_edit(request, parent_id):
    """Modifier un parent"""
    parent = get_object_or_404(Parent, id=parent_id)
    
    if request.method == 'POST':
        user_form = ProfileEditForm(request.POST, request.FILES, instance=parent.user)
        parent_form = ParentProfileForm(request.POST, instance=parent)
        
        if user_form.is_valid() and parent_form.is_valid():
            user_form.save()
            parent_form.save()
            
            messages.success(request, f'Profil de {parent.user.full_name} mis à jour avec succès.')
            return redirect('accounts:parent_detail', parent_id=parent.id)
        else:
            messages.error(request, 'Erreur lors de la mise à jour. Vérifiez les informations.')
    else:
        user_form = ProfileEditForm(instance=parent.user)
        parent_form = ParentProfileForm(instance=parent)
    
    context = {
        'parent': parent,
        'user_form': user_form,
        'parent_form': parent_form,
    }
    
    return render(request, 'accounts/parent_edit.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def parent_delete(request, parent_id):
    """Supprimer un parent"""
    parent = get_object_or_404(Parent, id=parent_id)
    
    # Vérifier si le parent a des enfants
    if parent.children.exists():
        messages.error(request, f'Impossible de supprimer {parent.user.full_name}. Ce parent a des enfants associés.')
        return redirect('accounts:parent_detail', parent_id=parent.id)
    
    parent_name = parent.user.full_name
    user = parent.user
    
    # Supprimer le parent et l'utilisateur
    parent.delete()
    user.delete()
    
    messages.success(request, f'Parent {parent_name} supprimé avec succès.')
    return redirect('accounts:parent_list')


@login_required
@admin_required
def parent_assign_children(request, parent_id):
    """Assigner des enfants à un parent"""
    parent = get_object_or_404(Parent, id=parent_id)
    
    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        action = request.POST.get('action')
        
        if action == 'add':
            # Ajouter des enfants
            students = Student.objects.filter(id__in=student_ids)
            for student in students:
                parent.children.add(student)
            messages.success(request, f'{len(students)} enfant(s) ajouté(s) à {parent.user.full_name}.')
        
        elif action == 'remove':
            # Retirer des enfants
            students = Student.objects.filter(id__in=student_ids)
            for student in students:
                parent.children.remove(student)
            messages.success(request, f'{len(students)} enfant(s) retiré(s) de {parent.user.full_name}.')
        
        return redirect('accounts:parent_detail', parent_id=parent.id)
    
    # Obtenir les enfants actuels et les enfants disponibles
    current_children = parent.children.all()
    available_students = Student.objects.exclude(
        id__in=current_children.values_list('id', flat=True)
    ).select_related('user')
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        available_students = available_students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(matricule__icontains=search_query)
        )
    
    context = {
        'parent': parent,
        'current_children': current_children,
        'available_students': available_students,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/parent_assign_children.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def parent_toggle_active(request, parent_id):
    """Activer/désactiver un parent"""
    parent = get_object_or_404(Parent, id=parent_id)
    
    parent.user.is_active = not parent.user.is_active
    parent.user.save()
    
    status = "activé" if parent.user.is_active else "désactivé"
    messages.success(request, f'Parent {parent.user.full_name} {status} avec succès.')
    
    return redirect('accounts:parent_detail', parent_id=parent.id)


@login_required
@admin_required
def parent_bulk_import(request):
    """Import en masse de parents via CSV"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, 'Veuillez sélectionner un fichier CSV.')
            return render(request, 'accounts/parent_bulk_import.html')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV.')
            return render(request, 'accounts/parent_bulk_import.html')
        
        try:
            import csv
            import io
            
            # Lire le fichier CSV
            file_data = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(file_data))
            
            created_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_data, start=2):  # Start at 2 because row 1 is header
                try:
                    # Validation des données requises
                    required_fields = ['first_name', 'last_name', 'email', 'relationship']
                    missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
                    
                    if missing_fields:
                        errors.append(f"Ligne {row_num}: Champs manquants: {', '.join(missing_fields)}")
                        error_count += 1
                        continue
                    
                    # Vérifier si l'email existe déjà
                    if User.objects.filter(email=row['email'].strip()).exists():
                        errors.append(f"Ligne {row_num}: L'email {row['email'].strip()} existe déjà")
                        error_count += 1
                        continue
                    
                    # Créer l'utilisateur
                    user = User.objects.create_user(
                        email=row['email'].strip(),
                        password=row.get('password', 'password123').strip() or 'password123',
                        first_name=row['first_name'].strip(),
                        last_name=row['last_name'].strip(),
                        phone=row.get('phone', '').strip(),
                        role='PARENT',
                        is_active=True
                    )
                    
                    # Créer le profil parent
                    parent = Parent.objects.create(
                        user=user,
                        relationship=row['relationship'].strip().upper(),
                        profession=row.get('profession', '').strip(),
                        workplace=row.get('workplace', '').strip()
                    )
                    
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Ligne {row_num}: Erreur - {str(e)}")
                    error_count += 1
            
            # Messages de résultat
            if created_count > 0:
                messages.success(request, f'{created_count} parent(s) créé(s) avec succès.')
            
            if error_count > 0:
                messages.warning(request, f'{error_count} erreur(s) détectée(s). Voir les détails ci-dessous.')
                for error in errors[:10]:  # Afficher seulement les 10 premières erreurs
                    messages.error(request, error)
                
                if len(errors) > 10:
                    messages.info(request, f'... et {len(errors) - 10} autres erreurs.')
            
            if created_count > 0:
                return redirect('accounts:parent_list')
                
        except Exception as e:
            messages.error(request, f'Erreur lors de la lecture du fichier CSV: {str(e)}')
    
    return render(request, 'accounts/parent_bulk_import.html')


@login_required
@admin_required  
def parent_export_csv(request):
    """Export des parents en format CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="parents_export.csv"'
    
    writer = csv.writer(response)
    
    # En-têtes
    writer.writerow([
        'ID', 'Prénom', 'Nom', 'Email', 'Téléphone', 'Relation',
        'Profession', 'Lieu de travail', 'Nombre d\'enfants', 'Actif',
        'Date création'
    ])
    
    # Données
    parents = Parent.objects.select_related('user').prefetch_related('children')
    
    for parent in parents:
        writer.writerow([
            parent.id,
            parent.user.first_name,
            parent.user.last_name,
            parent.user.email,
            parent.user.phone or '',
            parent.get_relationship_display(),
            parent.profession or '',
            parent.workplace or '',
            parent.children.count(),
            'Oui' if parent.user.is_active else 'Non',
            parent.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


@user_passes_test(is_admin_or_staff)
def teacher_list(request):
    """Liste des enseignants avec recherche et filtres"""
    from django.core.paginator import Paginator
    from .models import Teacher
    
    # Récupérer tous les enseignants
    teachers = Teacher.objects.select_related('user').prefetch_related('subjects')
    
    # Filtres de recherche
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    subject_filter = request.GET.get('subject', '')
    
    # Appliquer les filtres
    if search_query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    if status_filter == 'active':
        teachers = teachers.filter(user__is_active=True, is_active_employee=True)
    elif status_filter == 'inactive':
        teachers = teachers.filter(
            Q(user__is_active=False) | Q(is_active_employee=False)
        )
    
    if subject_filter:
        teachers = teachers.filter(subjects__id=subject_filter)
    
    # Tri
    sort_by = request.GET.get('sort', 'user__last_name')
    if sort_by in ['user__last_name', 'user__first_name', 'hire_date', 'employee_id']:
        teachers = teachers.order_by(sort_by)
    else:
        teachers = teachers.order_by('user__last_name')
    
    # Pagination
    paginator = Paginator(teachers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupérer les matières pour le filtre
    from academic.models import Subject
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'teachers': page_obj,
        'subjects': subjects,
        'search_query': search_query,
        'status_filter': status_filter,
        'subject_filter': subject_filter,
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    
    return render(request, 'accounts/teacher_list.html', context)

@user_passes_test(is_admin)
def teacher_create(request):
    """Créer un nouvel enseignant"""
    if request.method == 'POST':
        # Créer l'utilisateur
        user = User.objects.create_user(
            email=request.POST.get('email'),
            password='temp123456',  # Mot de passe temporaire
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            role='TEACHER',
            phone=request.POST.get('phone', ''),
            date_of_birth=request.POST.get('date_of_birth') or None,
            gender=request.POST.get('gender', ''),
            address=request.POST.get('address', ''),
        )
        
        # Créer le profil enseignant
        teacher = Teacher.objects.create(
            user=user,
            employee_id=request.POST.get('employee_id'),
            hire_date=request.POST.get('hire_date') or timezone.now().date(),
            education_level=request.POST.get('education_level', ''),
            certifications=request.POST.get('certifications', ''),
            is_head_teacher=request.POST.get('is_head_teacher') == 'on'
        )
        
        # Assigner les matières
        subject_ids = request.POST.getlist('subjects')
        if subject_ids:
            teacher.subjects.set(subject_ids)
        
        messages.success(request, f'L\'enseignant {user.full_name} a été créé avec succès. Mot de passe temporaire: temp123456')
        return redirect('accounts:teacher_detail', teacher_id=teacher.pk)
    
    # Récupérer toutes les matières pour le formulaire
    from academic.models import Subject
    subjects = Subject.objects.all().order_by('name')
    
    # Générer un ID employé unique
    import random
    from datetime import date
    employee_id = f"EMP{random.randint(1000, 9999)}"
    while Teacher.objects.filter(employee_id=employee_id).exists():
        employee_id = f"EMP{random.randint(1000, 9999)}"
    
    context = {
        'subjects': subjects,
        'suggested_employee_id': employee_id,
        'today': date.today(),
        'is_popup': request.GET.get('popup', False)
    }
    return render(request, 'accounts/teacher_create.html', context)

@user_passes_test(is_admin_or_staff)
def teacher_detail(request, teacher_id):
    """Détail d'un enseignant"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    context = {
        'teacher': teacher,
    }
    return render(request, 'accounts/teacher_detail.html', context)

@user_passes_test(is_admin_or_staff)
def teacher_edit(request, teacher_id):
    """Modifier un enseignant"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    user = teacher.user
    
    if request.method == 'POST':
        # Mise à jour des informations utilisateur
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.date_of_birth = request.POST.get('date_of_birth') or user.date_of_birth
        user.gender = request.POST.get('gender', user.gender)
        user.address = request.POST.get('address', user.address)
        user.save()
        
        # Mise à jour des informations enseignant
        teacher.education_level = request.POST.get('education_level', teacher.education_level)
        teacher.certifications = request.POST.get('certifications', teacher.certifications)
        teacher.is_head_teacher = request.POST.get('is_head_teacher') == 'on'
        teacher.save()
        
        # Mise à jour des matières
        subject_ids = request.POST.getlist('subjects')
        if subject_ids:
            teacher.subjects.set(subject_ids)
        
        messages.success(request, f'Les informations de {user.full_name} ont été mises à jour.')
        return redirect('accounts:teacher_detail', teacher_id=teacher.id)
    
    # Récupérer toutes les matières pour le formulaire
    from academic.models import Subject
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'teacher': teacher,
        'user': user,
        'subjects': subjects,
    }
    return render(request, 'accounts/teacher_edit.html', context)


# ===== NOUVELLES VUES SPÉCIALISÉES POUR LES ÉLÈVES =====

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
    subjects = Subject.objects.filter(attendance__student=student).distinct()
    
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
            'subject': day_attendance.subject.name if day_attendance and day_attendance.subject else None
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
    total_pending = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = paid_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_overdue = overdue_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    
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


# ===== NOUVELLES VUES SPÉCIALISÉES POUR LES PARENTS =====

@login_required
def parent_children_overview(request):
    """Vue d'ensemble détaillée de tous les enfants pour le parent"""
    if request.user.role != 'PARENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        parent = request.user.parent_profile
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('accounts:dashboard')
    
    children = parent.children.all()
    
    if not children.exists():
        messages.info(request, 'Aucun enfant associé à votre compte.')
        return redirect('accounts:dashboard')
    
    # Période de comparaison
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
    
    children_detailed = []
    
    for child in children:
        # Statistiques académiques
        recent_grades = Grade.objects.filter(
            student=child,
            created_at__gte=start_date
        ).select_related('subject')
        
        average_grade = recent_grades.aggregate(avg=Avg('score'))['avg'] or 0
        best_grade = recent_grades.order_by('-score').first()
        worst_grade = recent_grades.order_by('score').first()
        
        # Statistiques de présence
        attendances = Attendance.objects.filter(
            student=child,
            date__gte=start_date
        )
        
        attendance_rate = 0
        if attendances.exists():
            present_count = attendances.filter(status='PRESENT').count()
            attendance_rate = round((present_count / attendances.count()) * 100, 1)
        
        # Situation financière
        pending_invoices = Invoice.objects.filter(
            student=child,
            status__in=['DRAFT', 'SENT']
        )
        overdue_invoices = Invoice.objects.filter(
            student=child,
            status='OVERDUE'
        )
        
        total_pending = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_overdue = overdue_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Performance par matière
        subjects_performance = []
        subjects = Subject.objects.filter(grades__student=child).distinct()
        
        for subject in subjects:
            subject_grades = recent_grades.filter(subject=subject)
            if subject_grades.exists():
                subject_avg = subject_grades.aggregate(avg=Avg('score'))['avg']
                subjects_performance.append({
                    'subject': subject,
                    'average': round(subject_avg, 2),
                    'grades_count': subject_grades.count(),
                    'best_score': subject_grades.order_by('-score').first().score,
                    'trend': 'up' if subject_avg >= 12 else 'down'
                })
        
        child_data = {
            'student': child,
            'period_grades': recent_grades.count(),
            'average_grade': round(average_grade, 2),
            'best_grade': best_grade.score if best_grade else 0,
            'worst_grade': worst_grade.score if worst_grade else 0,
            'attendance_rate': attendance_rate,
            'total_pending': total_pending,
            'total_overdue': total_overdue,
            'subjects_performance': subjects_performance,
            'financial_status': 'danger' if total_overdue > 0 else 'warning' if total_pending > 0 else 'success'
        }
        
        children_detailed.append(child_data)
    
    # Calcul des statistiques globales
    total_pending_amount = sum(child['total_pending'] for child in children_detailed)
    total_overdue_amount = sum(child['total_overdue'] for child in children_detailed)
    
    # Calcul de la moyenne globale avec protection contre division par zéro
    children_with_grades = [child for child in children_detailed if child['average_grade'] > 0]
    if children_with_grades:
        average_grade_global = sum(child['average_grade'] for child in children_with_grades) / len(children_with_grades)
    else:
        average_grade_global = 0
    
    # Calcul du taux de présence moyen avec protection contre division par zéro
    if children_detailed:
        average_attendance_global = sum(child['attendance_rate'] for child in children_detailed) / len(children_detailed)
    else:
        average_attendance_global = 0
    
    context = {
        'parent': parent,
        'children_detailed': children_detailed,
        'period': period,
        'start_date': start_date,
        'total_children': children.count(),
        'total_pending_amount': total_pending_amount,
        'total_overdue_amount': total_overdue_amount,
        'average_grade_global': round(average_grade_global, 1),
        'average_attendance_global': round(average_attendance_global, 1),
    }
    
    return render(request, 'accounts/parent_children_overview.html', context)


@login_required
def parent_child_detail(request, child_id):
    """Vue détaillée d'un enfant spécifique pour le parent"""
    if request.user.role != 'PARENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        parent = request.user.parent_profile
        child = get_object_or_404(Student, id=child_id, parents=parent)
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('accounts:dashboard')
    
    # Section sélectionnée (notes, présences, finances)
    section = request.GET.get('section', 'overview')
    
    # Données de base
    today = date.today()
    month_ago = today - timedelta(days=30)
    
    # Données académiques
    recent_grades = Grade.objects.filter(
        student=child
    ).select_related('subject', 'teacher').order_by('-created_at')[:10]
    
    average_grade = Grade.objects.filter(student=child).aggregate(avg=Avg('score'))['avg'] or 0
    
    # Données de présence
    all_recent_attendances = Attendance.objects.filter(
        student=child,
        date__gte=month_ago
    ).order_by('-date')
    
    # Calculer les stats avant le slicing
    attendance_stats = {
        'present': all_recent_attendances.filter(status='PRESENT').count(),
        'absent': all_recent_attendances.filter(status='ABSENT').count(),
        'late': all_recent_attendances.filter(status='LATE').count(),
    }
    
    total_days = all_recent_attendances.count()
    attendance_rate = round((attendance_stats['present'] / total_days * 100), 1) if total_days > 0 else 0
    
    # Limiter à 15 pour l'affichage
    recent_attendances = all_recent_attendances[:15]
    
    # Données financières
    pending_invoices = Invoice.objects.filter(
        student=child,
        status__in=['DRAFT', 'SENT']
    ).order_by('-due_date')
    
    paid_invoices = Invoice.objects.filter(
        student=child,
        status='PAID'
    ).order_by('-issue_date')[:5]
    
    total_pending = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Prochains événements (simulation)
    upcoming_events = [
        {
            'type': 'exam',
            'title': 'Examen de Mathématiques',
            'date': today + timedelta(days=3),
            'time': '08:00',
            'importance': 'high'
        },
        {
            'type': 'assignment',
            'title': 'Devoir de Français',
            'date': today + timedelta(days=7),
            'time': '14:00',
            'importance': 'medium'
        }
    ]
    
    context = {
        'parent': parent,
        'child': child,
        'section': section,
        'recent_grades': recent_grades,
        'average_grade': round(average_grade, 2),
        'recent_attendances': recent_attendances,
        'attendance_stats': attendance_stats,
        'attendance_rate': attendance_rate,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices,
        'total_pending': total_pending,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'accounts/parent_child_detail.html', context)


@login_required
def parent_communication_center(request):
    """Centre de communication pour les parents"""
    if request.user.role != 'PARENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    
    try:
        parent = request.user.parent_profile
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('accounts:dashboard')
    
    children = parent.children.all()
    
    # Messages récents par enfant (simulation)
    messages_by_child = {}
    for child in children:
        messages_by_child[child] = [
            {
                'from': 'M. Dupont (Mathématiques)',
                'subject': f'Progression de {child.user.first_name}',
                'preview': 'Votre enfant fait de beaux progrès en mathématiques...',
                'date': timezone.now() - timedelta(days=2),
                'read': False,
                'type': 'teacher'
            },
            {
                'from': 'Administration',
                'subject': 'Rappel: Réunion parents-professeurs',
                'preview': 'La réunion aura lieu le vendredi 15 septembre...',
                'date': timezone.now() - timedelta(days=5),
                'read': True,
                'type': 'admin'
            }
        ]
    
    # Notifications importantes
    notifications = [
        {
            'type': 'warning',
            'title': 'Paiement en attente',
            'message': 'Une facture est en attente de paiement',
            'action': 'Voir les factures',
            'link': '#'
        },
        {
            'type': 'info',
            'title': 'Nouvelle note disponible',
            'message': 'Une nouvelle note a été ajoutée',
            'action': 'Voir les notes',
            'link': '#'
        }
    ]
    
    context = {
        'parent': parent,
        'children': children,
        'messages_by_child': messages_by_child,
        'notifications': notifications,
    }
    
    return render(request, 'accounts/parent_communication_center.html', context)
