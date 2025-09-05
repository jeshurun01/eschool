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
from academic.models import ClassRoom, Subject, Grade, Attendance, Enrollment
from finance.models import Invoice, Payment
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
    return redirect('account_login')


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
        
        # Ajouter le pourcentage pour chaque note
        for grade in recent_grades:
            grade.percentage = (grade.score / grade.max_score * 100) if grade.max_score > 0 else 0
        
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
        classroom__in=assigned_classes,
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
            'date': grade.created_at,
            'color': 'blue'
        })
    
    # Ajout des présences récentes
    recent_attendance = Attendance.objects.filter(
        classroom__in=assigned_classes,
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
            'description': f'{attendance.student.user.first_name} {attendance.student.user.last_name} - {attendance.get_status_display()}',
            'date': attendance.date,
            'color': status_colors.get(attendance.status, 'gray')
        })
    
    # Tri par date décroissante
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Classes avec le plus d'absences cette semaine
    classes_with_absences = []
    for class_obj in assigned_classes:
        week_absences = Attendance.objects.filter(
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
    
    if request.headers.get('HX-Request'):
        return JsonResponse({
            'success': True,
            'is_active': user_obj.is_active,
            'message': f'Utilisateur {status}'
        })
    
    return redirect('accounts:user_detail', user_id=user_obj.pk)


# Vues spécifiques par rôle

@user_passes_test(is_admin)
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

def student_detail(request, student_id):
    return HttpResponse(f"Détails de l'élève {student_id} - En cours de développement")

def student_edit(request, student_id):
    return HttpResponse(f"Modifier l'élève {student_id} - En cours de développement")

def parent_list(request):
    return HttpResponse("Liste des parents - En cours de développement")

def parent_create(request):
    return HttpResponse("Créer un parent - En cours de développement")

def parent_detail(request, parent_id):
    return HttpResponse(f"Détails du parent {parent_id} - En cours de développement")

def parent_edit(request, parent_id):
    return HttpResponse(f"Modifier le parent {parent_id} - En cours de développement")

def teacher_list(request):
    return HttpResponse("Liste des enseignants - En cours de développement")

def teacher_create(request):
    return HttpResponse("Créer un enseignant - En cours de développement")

def teacher_detail(request, teacher_id):
    return HttpResponse(f"Détails de l'enseignant {teacher_id} - En cours de développement")

def teacher_edit(request, teacher_id):
    return HttpResponse(f"Modifier l'enseignant {teacher_id} - En cours de développement")
