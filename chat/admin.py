from django.contrib import admin

from .models import ClassRecording, SubjectTest, TeacherNote


@admin.register(TeacherNote)
class TeacherNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_by', 'created_at')
    search_fields = ('title', 'subject', 'uploaded_by')


@admin.register(ClassRecording)
class ClassRecordingAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'recorded_by', 'created_at')
    search_fields = ('title', 'subject', 'recorded_by')


@admin.register(SubjectTest)
class SubjectTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_by', 'created_at')
    search_fields = ('title', 'subject', 'uploaded_by')
