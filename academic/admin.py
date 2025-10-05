from django.contrib import admin
from .models import (
    AcademicYear, Level, Subject, ClassRoom, TeacherAssignment, 
    Enrollment, Timetable, Attendance, Grade, Period, Document, DocumentAccess,
    Session, SessionAttendance, DailyAttendanceSummary, SessionDocument, 
    SessionAssignment, SessionNote
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('name',)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'created_at')
    list_editable = ('order',)
    ordering = ('order',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'coefficient', 'color')
    list_filter = ('levels',)
    search_fields = ('name', 'code')
    filter_horizontal = ('levels',)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'academic_year', 'head_teacher', 'current_enrollment', 'capacity')
    list_filter = ('level', 'academic_year')
    search_fields = ('name', 'room_number')
    # Removed filter_horizontal for teachers since it uses a through model


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'classroom', 'subject', 'academic_year', 'hours_per_week')
    list_filter = ('academic_year', 'subject', 'classroom__level')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'subject__name', 'classroom__name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'academic_year', 'enrollment_date', 'is_active')
    list_filter = ('academic_year', 'classroom__level', 'is_active')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricule')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'subject', 'teacher', 'weekday', 'start_time', 'end_time', 'room')
    list_filter = ('weekday', 'classroom__level', 'subject')
    search_fields = ('classroom__name', 'subject__name', 'teacher__user__first_name', 'teacher__user__last_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin temporaire pour l'ancien modèle Attendance"""
    list_display = ('student', 'date', 'status', 'subject', 'teacher')
    list_filter = ('status', 'date', 'subject', 'classroom__level')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricule')
    date_hierarchy = 'date'


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('timetable', 'date', 'status', 'lesson_title', 'attendance_taken')
    list_filter = ('status', 'date', 'timetable__subject', 'timetable__classroom__level')
    search_fields = ('lesson_title', 'timetable__classroom__name', 'timetable__subject__name')
    date_hierarchy = 'date'
    readonly_fields = ('attendance_rate', 'students_count', 'present_students_count')


@admin.register(SessionAttendance)
class SessionAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'arrival_time', 'recorded_by')
    list_filter = ('status', 'session__date', 'session__timetable__subject')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricule')
    date_hierarchy = 'session__date'


@admin.register(DailyAttendanceSummary)
class DailyAttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'daily_status', 'attendance_rate', 'total_sessions', 'present_sessions')
    list_filter = ('daily_status', 'date', 'student__current_class__level')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    date_hierarchy = 'date'
    readonly_fields = ('total_sessions', 'present_sessions', 'absent_sessions', 'late_sessions', 'attendance_rate')


@admin.register(SessionDocument)
class SessionDocumentAdmin(admin.ModelAdmin):
    list_display = ('document', 'session', 'shared_by', 'is_mandatory', 'shared_at')
    list_filter = ('is_mandatory', 'shared_at', 'session__timetable__subject')
    search_fields = ('document__title', 'session__lesson_title')


@admin.register(SessionAssignment)
class SessionAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'session', 'assignment_type', 'due_date', 'priority', 'will_be_graded')
    list_filter = ('assignment_type', 'priority', 'will_be_graded', 'due_date')
    search_fields = ('title', 'description', 'session__lesson_title')
    date_hierarchy = 'due_date'


@admin.register(SessionNote)
class SessionNoteAdmin(admin.ModelAdmin):
    list_display = ('session', 'author', 'note_type', 'title', 'is_private', 'created_at')
    list_filter = ('note_type', 'is_private', 'visible_to_students', 'visible_to_parents')
    search_fields = ('title', 'content', 'session__lesson_title')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'evaluation_name', 'score', 'max_score', 'percentage', 'date')
    list_filter = ('evaluation_type', 'subject', 'date', 'classroom__level')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'evaluation_name')
    date_hierarchy = 'date'


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'is_current')
    list_filter = ('academic_year', 'is_current')
    search_fields = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'document_type', 'classroom', 'file_size_mb', 'is_public', 'is_accessible', 'created_at')
    list_filter = ('document_type', 'subject', 'is_public', 'is_downloadable', 'created_at')
    search_fields = ('title', 'description', 'teacher__user__first_name', 'teacher__user__last_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('file_size', 'file_type', 'view_count', 'download_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'document_type', 'file')
        }),
        ('Attribution', {
            'fields': ('subject', 'teacher', 'classroom')
        }),
        ('Accès et visibilité', {
            'fields': ('is_public', 'is_downloadable', 'access_date', 'expiry_date')
        }),
        ('Métadonnées', {
            'fields': ('file_size', 'file_type', 'view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'access_type', 'accessed_at', 'ip_address')
    list_filter = ('access_type', 'accessed_at', 'document__subject')
    search_fields = ('document__title', 'user__first_name', 'user__last_name')
    date_hierarchy = 'accessed_at'
    readonly_fields = ('accessed_at',)
