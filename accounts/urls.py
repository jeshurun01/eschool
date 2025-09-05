from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    
    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Gestion des utilisateurs (admin)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Gestion des élèves
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    
    # Gestion des parents
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/create/', views.parent_create, name='parent_create'),
    path('parents/<int:parent_id>/', views.parent_detail, name='parent_detail'),
    path('parents/<int:parent_id>/edit/', views.parent_edit, name='parent_edit'),
    
    # Gestion des enseignants
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:teacher_id>/edit/', views.teacher_edit, name='teacher_edit'),
]
