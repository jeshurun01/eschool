from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification 
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),  # Réactivé - fonctionne bien
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Gestion des utilisateurs (admin)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/reset-password/', views.reset_password, name='reset_password'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Gestion des élèves
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    
    # Gestion des parents
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/create/', views.parent_create, name='parent_create'),
    path('parents/bulk-import/', views.parent_bulk_import, name='parent_bulk_import'),
    path('parents/export-csv/', views.parent_export_csv, name='parent_export_csv'),
    path('parents/<int:parent_id>/', views.parent_detail, name='parent_detail'),
    path('parents/<int:parent_id>/edit/', views.parent_edit, name='parent_edit'),
    path('parents/<int:parent_id>/delete/', views.parent_delete, name='parent_delete'),
    path('parents/<int:parent_id>/assign-children/', views.parent_assign_children, name='parent_assign_children'),
    path('parents/<int:parent_id>/toggle-active/', views.parent_toggle_active, name='parent_toggle_active'),
    
    # Gestion des enseignants
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:teacher_id>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/assignments/', views.teacher_assignments_management, name='teacher_assignments_management'),
    
    # === VUE D'ENSEMBLE POUR ADMIN ===
    path('children-overview/', views.admin_children_overview, name='admin_children_overview'),
    
    # === NOUVELLES VUES SPÉCIALISÉES ÉLÈVE ===
    path('student/grades/', views.student_grades_detail, name='student_grades_detail'),
    path('student/report-card/', views.student_report_card, name='student_report_card'),
    path('student/attendance/', views.student_attendance_detail, name='student_attendance_detail'),
    path('student/finance/', views.student_finance_detail, name='student_finance_detail'),
    path('student/calendar/', views.student_academic_calendar, name='student_academic_calendar'),
    
    # === NOUVELLES VUES SPÉCIALISÉES PARENT ===
    path('parent/children/', views.parent_children_overview, name='parent_children_overview'),
    path('parent/child/<int:child_id>/', views.parent_child_detail, name='parent_child_detail'),
    path('parent/communication/', views.parent_communication_center, name='parent_communication_center'),
]
