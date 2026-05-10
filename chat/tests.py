from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from unittest.mock import MagicMock, patch

from .models import ClassRecording, SubjectTest, TeacherNote


class ClassroomViewTests(TestCase):
    def test_home_page_renders_dashboard(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classroom Hub')
        self.assertContains(response, 'Engineering Maths')
        self.assertContains(response, 'Electrical and Electronics')
        self.assertContains(response, 'CTI')

    def test_subject_page_filters_materials(self):
        TeacherNote.objects.create(
            subject='engineering-maths',
            title='Matrices',
            description='Unit 1',
            uploaded_by='Teacher Rao',
            attachment=SimpleUploadedFile('matrices.txt', b'content'),
        )
        TeacherNote.objects.create(
            subject='cti',
            title='Networking',
            description='Unit 2',
            uploaded_by='Teacher Sen',
            attachment=SimpleUploadedFile('networking.txt', b'content'),
        )

        response = self.client.get(reverse('subject_page', args=['engineering-maths']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matrices')
        self.assertNotContains(response, 'Networking')

    def test_note_upload_creates_teacher_note(self):
        response = self.client.post(
            reverse('upload_note'),
            {
                'subject': 'engineering-maths',
                'title': 'Week 1 Handout',
                'description': 'Foundations module',
                'uploaded_by': 'Teacher Rao',
                'attachment': SimpleUploadedFile('handout.txt', b'content'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TeacherNote.objects.count(), 1)
        self.assertEqual(TeacherNote.objects.get().subject, 'engineering-maths')
        self.assertEqual(TeacherNote.objects.get().uploaded_by, 'Teacher Rao')

    def test_test_upload_creates_subject_test(self):
        response = self.client.post(
            reverse('upload_test'),
            {
                'subject': 'electrical-and-electronics',
                'title': 'Quiz 1',
                'description': 'DC circuits',
                'uploaded_by': 'Teacher Rao',
                'attachment': SimpleUploadedFile('quiz.pdf', b'content'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SubjectTest.objects.count(), 1)
        self.assertEqual(SubjectTest.objects.get().subject, 'electrical-and-electronics')

    def test_recording_upload_creates_recording(self):
        response = self.client.post(
            reverse('upload_recording'),
            {
                'subject': 'cti',
                'title': 'Session Recap',
                'recorded_by': 'Teacher Rao',
                'video': SimpleUploadedFile('recap.webm', b'video-bytes', content_type='video/webm'),
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ClassRecording.objects.count(), 1)
        self.assertEqual(ClassRecording.objects.get().subject, 'cti')
        self.assertEqual(ClassRecording.objects.get().title, 'Session Recap')

    def test_recording_delete_removes_recording(self):
        recording = ClassRecording.objects.create(
            subject='cti',
            title='Session Recap',
            recorded_by='Teacher Rao',
            video=SimpleUploadedFile('recap.webm', b'video-bytes', content_type='video/webm'),
        )

        response = self.client.post(reverse('delete_recording', args=[recording.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ClassRecording.objects.count(), 0)

    @patch('chat.views.Groq')
    @patch('chat.views.settings.GROQ_API_KEY', 'test-key')
    def test_chatbot_returns_groq_response(self, mocked_groq):
        mocked_client = MagicMock()
        mocked_completion = MagicMock()
        mocked_completion.choices = [MagicMock(message=MagicMock(content='Matrices are arrays of numbers.'))]
        mocked_client.chat.completions.create.return_value = mocked_completion
        mocked_groq.return_value = mocked_client

        response = self.client.post(
            reverse('chatbot'),
            {'message': 'Explain matrices', 'subject': 'engineering-maths'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['provider'], 'groq')
        self.assertEqual(response.json()['response'], 'Matrices are arrays of numbers.')

    @patch('chat.views.settings.GROQ_API_KEY', '')
    def test_chatbot_returns_error_when_key_missing(self):
        response = self.client.post(
            reverse('chatbot'),
            {'message': 'Explain matrices', 'subject': 'engineering-maths'},
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()['error'], 'Groq API key is not configured.')
