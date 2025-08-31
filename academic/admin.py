from django.contrib import admin
from .models import (
    AcademicYear, Level, Subject, ClassRoom, TeacherAssignment, 
    Enrollment, Timetable, Attendance, Grade, Period
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
    list_display = ('student', 'date', 'status', 'subject', 'teacher')
    list_filter = ('status', 'date', 'subject', 'classroom__level')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricule')
    date_hierarchy = 'date'


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
