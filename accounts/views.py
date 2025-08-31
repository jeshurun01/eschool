from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import User, Student, Parent, Teacher

@login_required
def dashboard(request):
    """Dashboard principal basé sur le rôle de l'utilisateur"""
    context = {
        'user': request.user,
    }
    
    if request.user.role == 'STUDENT':
        # Dashboard élève
        try:
            student = request.user.student_profile
            context.update({
                'student': student,
                'current_class': student.current_class,
                'recent_grades': student.grades.order_by('-created_at')[:5],
                'recent_attendance': student.attendances.order_by('-date')[:5],
            })
        except:
            pass
            
    elif request.user.role == 'PARENT':
        # Dashboard parent
        try:
            parent = request.user.parent_profile
            context.update({
                'parent': parent,
                'children': parent.children.all(),
            })
        except:
            pass
            
    elif request.user.role == 'TEACHER':
        # Dashboard enseignant
        try:
            teacher = request.user.teacher_profile
            context.update({
                'teacher': teacher,
                'assigned_classes': teacher.assigned_classes.all(),
                'subjects': teacher.subjects.all(),
            })
        except:
            pass
            
    elif request.user.role in ['ADMIN', 'SUPER_ADMIN']:
        # Dashboard administrateur
        context.update({
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_parents': Parent.objects.count(),
        })
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    """Afficher le profil de l'utilisateur"""
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    """Modifier le profil de l'utilisateur"""
    if request.method == 'POST':
        # TODO: Implémenter la logique de modification du profil
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile_edit.html', {'user': request.user})

# Vues temporaires (placeholder)
def user_list(request):
    return HttpResponse("Liste des utilisateurs - En cours de développement")

def user_create(request):
    return HttpResponse("Créer un utilisateur - En cours de développement")

def user_detail(request, user_id):
    return HttpResponse(f"Détails de l'utilisateur {user_id} - En cours de développement")

def user_edit(request, user_id):
    return HttpResponse(f"Modifier l'utilisateur {user_id} - En cours de développement")

def student_list(request):
    return HttpResponse("Liste des élèves - En cours de développement")

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
