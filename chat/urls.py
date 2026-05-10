from django.urls import path

from .views import (
    chatbot,
    delete_recording,
    home,
    subject_page,
    upload_note,
    upload_recording,
    upload_test,
)

urlpatterns = [
    path('', home, name='home'),
    path('subjects/<slug:subject_slug>/', subject_page, name='subject_page'),
    path('chat/', chatbot, name='chatbot'),
    path('notes/upload/', upload_note, name='upload_note'),
    path('tests/upload/', upload_test, name='upload_test'),
    path('recordings/upload/', upload_recording, name='upload_recording'),
    path('recordings/<int:recording_id>/delete/', delete_recording, name='delete_recording'),
]
