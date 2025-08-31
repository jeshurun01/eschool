from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    # Gestion des années scolaires
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/create/', views.academic_year_create, name='academic_year_create'),
    
    # Gestion des niveaux
    path('levels/', views.level_list, name='level_list'),
    path('levels/create/', views.level_create, name='level_create'),
    
    # Gestion des matières
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    
    # Gestion des classes
    path('classes/', views.classroom_list, name='classroom_list'),
    path('classes/create/', views.classroom_create, name='classroom_create'),
    path('classes/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),
    path('classes/<int:classroom_id>/students/', views.classroom_students, name='classroom_students'),
    path('classes/<int:classroom_id>/timetable/', views.classroom_timetable, name='classroom_timetable'),
    
    # Gestion des emplois du temps
    path('timetables/', views.timetable_list, name='timetable_list'),
    path('timetables/create/', views.timetable_create, name='timetable_create'),
    
    # Gestion des présences
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/take/', views.attendance_take, name='attendance_take'),
    path('attendance/class/<int:classroom_id>/', views.attendance_class, name='attendance_class'),
    
    # Gestion des notes
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/add/', views.grade_add, name='grade_add'),
    path('grades/student/<int:student_id>/', views.student_grades, name='student_grades'),
    path('grades/class/<int:classroom_id>/', views.class_grades, name='class_grades'),
    
    # Bulletins
    path('reports/bulletin/<int:student_id>/', views.student_bulletin, name='student_bulletin'),
    path('reports/class/<int:classroom_id>/', views.class_report, name='class_report'),
]
