from django.urls import path, include
from . import views
from .views import student_views, teacher_views, parent_views, admin_views

app_name = 'academic'

urlpatterns = [
    # Gestion des années scolaires
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/create/', views.academic_year_create, name='academic_year_create'),
    
    # Gestion des niveaux
    path('levels/', views.level_list, name='level_list'),
    path('levels/create/', views.level_create, name='level_create'),
    path('levels/<int:level_id>/', views.level_detail, name='level_detail'),
    path('levels/<int:level_id>/edit/', views.level_edit, name='level_edit'),
    
    # Gestion des matières
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    
    # Gestion des classes
    path('classes/', views.classroom_list, name='classroom_list'),
    path('classes/create/', views.classroom_create, name='classroom_create'),
    path('classes/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),
    path('classes/<int:classroom_id>/edit/', views.classroom_edit, name='classroom_edit'),
    path('classes/<int:classroom_id>/enrollments/', views.enrollment_manage, name='enrollment_manage'),
    path('classes/<int:classroom_id>/students/', views.classroom_students, name='classroom_students'),
    path('classes/<int:classroom_id>/timetable/', views.classroom_timetable, name='classroom_timetable'),
    
    # Gestion des cours (TeacherAssignment)
    path('courses/<int:assignment_id>/', views.course_detail, name='course_detail'),
    
    # Gestion des emplois du temps
    path('timetables/', views.timetable_list, name='timetable_list'),
    path('timetables/create/', views.timetable_create, name='timetable_create'),
    
    # Gestion des présences
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/take/', views.attendance_take, name='attendance_take'),
    path('attendance/class/<int:classroom_id>/', views.attendance_class, name='attendance_class'),
    path('api/classroom/<int:classroom_id>/students/', views.get_classroom_students, name='get_classroom_students'),
    
    # Gestion des notes
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/add/', views.grade_add, name='grade_add'),
    path('grades/student/<int:student_id>/', views.student_grades, name='student_grades'),
    path('grades/class/<int:classroom_id>/', views.class_grades, name='class_grades'),
    
    # Gestion des documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/add/', views.document_add, name='document_add'),
    path('documents/<int:document_id>/', views.document_detail, name='document_detail'),
    path('documents/<int:document_id>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:document_id>/view/', views.document_view, name='document_view'),
    path('documents/subject/<int:subject_id>/', views.document_subject_list, name='document_subject_list'),
    
    # Bulletins
    path('reports/bulletin/<int:student_id>/', views.student_bulletin, name='student_bulletin'),
    path('reports/class/<int:classroom_id>/', views.class_report, name='class_report'),
    
    # === NOUVELLES URLS SPÉCIALISÉES PAR RÔLE ===
    
    # URLs pour les étudiants
    path('student/sessions/', student_views.student_sessions_view, name='student_sessions'),
    path('student/session/<int:session_id>/', student_views.student_session_detail, name='student_session_detail'),
    path('student/attendance/', student_views.student_attendance_overview, name='student_attendance'),
    path('student/timetable/', student_views.student_timetable_view, name='student_timetable'),
    path('student/documents/', student_views.student_documents_view, name='student_documents'),
    path('student/assignments/', student_views.student_assignments_view, name='student_assignments'),
    path('student/grades/', student_views.student_grades_view, name='student_grades'),
    
    # URLs pour les enseignants
    path('teacher/sessions/', teacher_views.teacher_sessions_view, name='teacher_sessions'),
    path('teacher/sessions/create/', teacher_views.teacher_session_create, name='session_create'),
    path('teacher/session/<int:session_id>/', teacher_views.teacher_session_detail, name='teacher_session_detail'),
    path('teacher/session/<int:session_id>/edit/', teacher_views.teacher_session_edit, name='teacher_session_edit'),
    path('teacher/session/<int:session_id>/attendance/', teacher_views.teacher_attendance_view, name='teacher_attendance'),
    path('teacher/session/<int:session_id>/document/add/', teacher_views.teacher_session_document_add, name='teacher_session_document_add'),
    path('teacher/session/<int:session_id>/assignment/add/', teacher_views.teacher_session_assignment_add, name='teacher_session_assignment_add'),
    path('teacher/timetable/', teacher_views.teacher_timetable_view, name='teacher_timetable'),
    path('teacher/timetable/create/', teacher_views.teacher_timetable_create, name='teacher_timetable_create'),
    path('teacher/timetable/<int:timetable_id>/', teacher_views.teacher_timetable_detail, name='teacher_timetable_detail'),
    path('teacher/timetable/<int:timetable_id>/delete/', teacher_views.teacher_timetable_delete, name='teacher_timetable_delete'),
    path('teacher/documents/', teacher_views.teacher_documents_view, name='teacher_documents'),
    path('teacher/assignments/', teacher_views.teacher_assignments_view, name='teacher_assignments'),
    path('teacher/students/', teacher_views.teacher_students_overview, name='teacher_students'),
    path('teacher/class/<int:class_id>/', teacher_views.teacher_class_detail, name='teacher_class_detail'),
    
    # URLs pour les parents
    path('parent/children/', parent_views.parent_children_overview, name='parent_children'),
    path('parent/child/<int:child_id>/', parent_views.parent_child_detail, name='parent_child_detail'),
    path('parent/child/<int:child_id>/timetable/', parent_views.parent_child_timetable, name='parent_child_timetable'),
    path('parent/communications/', parent_views.parent_communications_view, name='parent_communications'),
    # URLs AJAX pour parents
    path('parent/api/child/<int:child_id>/sessions/', parent_views.parent_child_sessions_ajax, name='parent_child_sessions_ajax'),
    path('parent/api/summary/', parent_views.parent_dashboard_summary, name='parent_dashboard_summary'),
    
    # URLs pour l'administration
    path('admin/dashboard/', admin_views.admin_dashboard_overview, name='admin_dashboard'),
    path('admin/sessions/', admin_views.admin_sessions_management, name='admin_sessions'),
    path('admin/attendance/reports/', admin_views.admin_attendance_reports, name='admin_attendance_reports'),
    path('admin/teachers/', admin_views.admin_teachers_overview, name='admin_teachers'),
    path('admin/students/', admin_views.admin_students_overview, name='admin_students'),
    path('admin/system/stats/', admin_views.admin_system_stats, name='admin_system_stats'),
    # Export pour admin
    path('admin/export/attendance/csv/', admin_views.admin_export_attendance_csv, name='admin_export_attendance_csv'),
]
