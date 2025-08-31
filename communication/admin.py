from django.contrib import admin
from .models import (
    Announcement, AnnouncementRead, Message, GroupMessage, 
    GroupMessageRead, Resource, ResourceAccess, Notification, 
    EmailTemplate, EmailLog
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'audience', 'author', 'is_published', 'publish_date', 'priority')
    list_filter = ('type', 'audience', 'is_published', 'priority', 'publish_date')
    search_fields = ('title', 'content')
    filter_horizontal = ('target_classes', 'target_levels')
    date_hierarchy = 'publish_date'


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'read_date')
    list_filter = ('read_date', 'announcement__type')
    search_fields = ('announcement__title', 'user__first_name', 'user__last_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'is_read', 'sent_date')
    list_filter = ('is_read', 'sent_date')
    search_fields = ('subject', 'sender__first_name', 'sender__last_name', 'recipient__first_name', 'recipient__last_name')
    date_hierarchy = 'sent_date'


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'sent_date')
    list_filter = ('sent_date',)
    search_fields = ('subject', 'sender__first_name', 'sender__last_name')
    filter_horizontal = ('target_classes', 'target_levels', 'target_users')
    date_hierarchy = 'sent_date'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'uploaded_by', 'subject', 'is_public', 'download_count', 'created_at')
    list_filter = ('resource_type', 'is_public', 'subject', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('accessible_classes', 'accessible_levels')


@admin.register(ResourceAccess)
class ResourceAccessAdmin(admin.ModelAdmin):
    list_display = ('resource', 'user', 'action', 'access_date')
    list_filter = ('action', 'access_date')
    search_fields = ('resource__title', 'user__first_name', 'user__last_name')
    date_hierarchy = 'access_date'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'subject')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'subject', 'status', 'sent_date')
    list_filter = ('status', 'sent_date')
    search_fields = ('recipient_email', 'subject')
    date_hierarchy = 'sent_date'
