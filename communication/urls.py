from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Gestion des annonces
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:announcement_id>/mark-read/', views.announcement_mark_read, name='announcement_mark_read'),
    
    # Messagerie
    path('messages/', views.message_list, name='message_list'),
    path('messages/compose/', views.message_compose, name='message_compose'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/reply/', views.message_reply, name='message_reply'),
    
    # Messages de groupe
    path('group-messages/', views.group_message_list, name='group_message_list'),
    path('group-messages/compose/', views.group_message_compose, name='group_message_compose'),
    path('group-messages/<int:message_id>/', views.group_message_detail, name='group_message_detail'),
    
    # Ressources
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/upload/', views.resource_upload, name='resource_upload'),
    path('resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('resources/<int:resource_id>/download/', views.resource_download, name='resource_download'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    
    # Forum
    path('forum/', views.forum_index, name='forum_index'),
    path('forum/classroom/<int:classroom_id>/', views.forum_classroom, name='forum_classroom'),
    path('forum/topic/<int:topic_id>/', views.forum_topic_detail, name='forum_topic_detail'),
    path('forum/classroom/<int:classroom_id>/topic/create/', views.forum_topic_create, name='forum_topic_create'),
    path('forum/topic/<int:topic_id>/post/', views.forum_post_create, name='forum_post_create'),
]
