from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, Student, Parent, Teacher


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'gender', 'date_of_birth', 'address')}),
        (_('Rôle et permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined', 'email_verified')}),
        (_('Préférences'), {'fields': ('preferred_language',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined', 'gender')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'emergency_contact_name', 'emergency_contact_phone', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'emergency_contact_name')
    list_filter = ('created_at',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'user', 'current_class', 'enrollment_date', 'is_graduated')
    list_filter = ('is_graduated', 'enrollment_date', 'current_class__level')
    search_fields = ('matricule', 'user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('parents',)
    readonly_fields = ('matricule',)  # Auto-généré


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'relationship', 'profession', 'workplace')
    list_filter = ('relationship',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'profession')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'hire_date', 'is_head_teacher', 'is_active_employee')
    list_filter = ('is_head_teacher', 'is_active_employee', 'hire_date')
    search_fields = ('employee_id', 'user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('subjects',)
    readonly_fields = ('employee_id',)  # Auto-généré
