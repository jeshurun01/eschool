from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .models import User, Student, Parent, Teacher
from .forms import (
    UserRegistrationForm, CustomLoginForm, ProfileEditForm,
    StudentProfileForm, TeacherProfileForm, ParentProfileForm,
    AdminUserCreateForm, PasswordChangeForm
)


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
            login(request, user)
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
            login(request, user)
            
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
    return render(request, 'accounts/dashboard.html', context)


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


# Placeholder views for development
def is_admin(user):
    return user.is_authenticated and user.is_staff

def user_list(request):
    return HttpResponse("User list - En cours de développement")

def user_create(request):
    return HttpResponse("Create user - En cours de développement")

def user_detail(request, user_id):
    return HttpResponse(f"User detail {user_id} - En cours de développement")

def user_edit(request, user_id):
    return HttpResponse(f"Edit user {user_id} - En cours de développement")

def user_toggle_active(request, user_id):
    return HttpResponse(f"Toggle user {user_id} - En cours de développement")

def student_list(request):
    return HttpResponse("Student list - En cours de développement")

def student_create(request):
    return HttpResponse("Create student - En cours de développement")

def student_detail(request, student_id):
    return HttpResponse(f"Student detail {student_id} - En cours de développement")

def student_edit(request, student_id):
    return HttpResponse(f"Edit student {student_id} - En cours de développement")

def parent_list(request):
    return HttpResponse("Parent list - En cours de développement")

def parent_create(request):
    return HttpResponse("Create parent - En cours de développement")

def parent_detail(request, parent_id):
    return HttpResponse(f"Parent detail {parent_id} - En cours de développement")

def parent_edit(request, parent_id):
    return HttpResponse(f"Edit parent {parent_id} - En cours de développement")

def teacher_list(request):
    return HttpResponse("Teacher list - En cours de développement")

def teacher_create(request):
    return HttpResponse("Create teacher - En cours de développement")

def teacher_detail(request, teacher_id):
    return HttpResponse(f"Teacher detail {teacher_id} - En cours de développement")

def teacher_edit(request, teacher_id):
    return HttpResponse(f"Edit teacher {teacher_id} - En cours de développement")
