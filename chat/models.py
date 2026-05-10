from django.db import models


class TeacherNote(models.Model):
    subject = models.CharField(max_length=64, default="general", db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_by = models.CharField(max_length=120, default="Teacher")
    attachment = models.FileField(upload_to="notes/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class ClassRecording(models.Model):
    subject = models.CharField(max_length=64, default="general", db_index=True)
    title = models.CharField(max_length=200)
    recorded_by = models.CharField(max_length=120, default="Teacher")
    video = models.FileField(upload_to="recordings/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class SubjectTest(models.Model):
    subject = models.CharField(max_length=64, default="general", db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_by = models.CharField(max_length=120, default="Teacher")
    attachment = models.FileField(upload_to="tests/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
