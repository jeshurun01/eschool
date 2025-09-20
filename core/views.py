from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from accounts.models import User, Student, Teacher, Parent
from academic.models import ClassRoom, Subject, Enrollment
from communication.models import Message, Announcement


def home_view(request):
    """Vue d'accueil avec vraies statistiques"""
    context = {}
    
    if request.user.is_authenticated:
        # Statistiques générales
        context.update({
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(), 
            'total_parents': Parent.objects.count(),
            'total_classes': ClassRoom.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
            'total_messages': Message.objects.count(),
            'total_announcements': Announcement.objects.count(),
        })
        
        # Statistiques spécifiques selon le rôle
        if hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            context.update({
                'user_role': 'student',
                'current_class': student.current_class,
                'enrollment_date': student.enrollment_date,
            })
        elif hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            context.update({
                'user_role': 'teacher',
                'subjects_taught': teacher.subjects.count(),
                'hire_date': teacher.hire_date,
            })
        elif hasattr(request.user, 'parent_profile'):
            parent = request.user.parent_profile
            context.update({
                'user_role': 'parent',
                'children_count': parent.children.count(),
            })
        elif request.user.is_admin:
            context.update({
                'user_role': 'admin',
                'recent_enrollments': Enrollment.objects.filter(is_active=True).order_by('-enrollment_date')[:5],
            })
    
    return render(request, 'home.html', context)