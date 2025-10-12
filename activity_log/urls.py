"""
URLs pour le système de suivi d'activité
"""
from django.urls import path
from activity_log import views

app_name = 'activity_log'

urlpatterns = [
    # Liste des activités
    path('', views.activity_log_list, name='list'),
    
    # Détails d'une activité
    path('<int:log_id>/', views.activity_log_detail, name='detail'),
    
    # Activités d'un utilisateur spécifique
    path('user/<int:user_id>/', views.user_activity_log, name='user_log'),
]
