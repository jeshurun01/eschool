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
def register_view(request):
    """Vue d'inscription des utilisateurs"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Compte créé avec succès! Bienvenue {user.first_name}.')
            
            # Solution directe : Définir explicitement le backend sur l'utilisateur
            # avant de l'utiliser avec login()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'account/signup.html', {'form': form})


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
        try:
            teacher = request.user.teacher_profile
            context.update({
                'teacher': teacher,
                'assigned_classes': teacher.assigned_classes.all()[:5],  # 5 dernières classes
                'subjects': teacher.subjects.all(),
            })
        except Teacher.DoesNotExist:
            pass
        return render(request, 'accounts/dashboard.html', context)
    
    # Dashboard parent
    elif request.user.role == 'PARENT':
        try:
            parent = request.user.parent_profile
            context.update({
                'parent': parent,
                'children': parent.children.all(),
            })
        except Parent.DoesNotExist:
            pass
        return render(request, 'accounts/dashboard.html', context)
    
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
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Informations de base
    context = {
        'student': student,
        'current_class': student.current_class,
    }
    
    # Initialisation par défaut
    recent_grades = Grade.objects.none()
    
    # Statistiques académiques
    if student.current_class:
        # Notes récentes
        recent_grades = Grade.objects.filter(
            student=student
        ).select_related('subject', 'teacher').order_by('-created_at')[:5]
        
        # Moyenne générale
        student_grades = Grade.objects.filter(student=student)
        if student_grades.exists():
            avg_grade = student_grades.aggregate(avg=Avg('score'))['avg']
            context['average_grade'] = round(avg_grade, 2) if avg_grade else None
        
        # Présences du mois
        monthly_attendances = Attendance.objects.filter(
            student=student,
            date__gte=month_ago
        )
        present_count = monthly_attendances.filter(status='PRESENT').count()
        total_days = monthly_attendances.count()
        
        context.update({
            'recent_grades': recent_grades,
            'monthly_attendances': {
                'present': present_count,
                'absent': monthly_attendances.filter(status='ABSENT').count(),
                'late': monthly_attendances.filter(status='LATE').count(),
                'total': total_days,
                'attendance_rate': round((present_count / total_days * 100), 1) if total_days > 0 else 0
            }
        })
        
        # Prochains cours (emploi du temps)
        from academic.models import Timetable
        next_classes = Timetable.objects.filter(
            classroom=student.current_class
        ).select_related('subject', 'teacher').order_by('weekday', 'start_time')[:5]
        
        context['next_classes'] = next_classes
    
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
