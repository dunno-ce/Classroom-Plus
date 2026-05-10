from typing import Optional

from django.conf import settings
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from groq import Groq

from .models import ClassRecording, SubjectTest, TeacherNote


SUBJECTS = {
    "general": {
        "title": "Classroom Hub",
        "hero_title": "Classroom Plus",
        "eyebrow": "Digital classroom workspace",
        "description": "A shared classroom workspace for updates, notes, recorded lectures, tests, and AI help.",
        "badge": "Core classroom view",
    },
    "engineering-maths": {
        "title": "Engineering Maths",
        "hero_title": "Engineering Maths",
        "eyebrow": "Subject workspace",
        "description": "Upload notes, post lecture recordings, and publish maths tests for the class.",
        "badge": "Subject page",
    },
    "electrical-and-electronics": {
        "title": "Electrical and Electronics",
        "hero_title": "Electrical and Electronics",
        "eyebrow": "Subject workspace",
        "description": "Keep circuit theory notes, lecture captures, and assessment files in one place.",
        "badge": "Subject page",
    },
    "cti": {
        "title": "CTI",
        "hero_title": "CTI",
        "eyebrow": "Subject workspace",
        "description": "Manage CTI notes, explainers, lecture recordings, and quick tests from the same dashboard.",
        "badge": "Subject page",
    },
}


SUBJECT_ANNOUNCEMENTS = {
    "general": [
        {
            "title": "Week 4 module unlocked",
            "body": "Review this week's class materials and upload any recap recording after the session.",
            "tag": "Coursework",
        }
    ]
}


def _current_ai_status() -> dict:
    groq_key = (settings.GROQ_API_KEY or "").strip()

    if groq_key:
        return {
            "provider": "Groq",
            "configured": True,
            "model": "llama-3.1-8b-instant",
        }
    return {
        "provider": "Unavailable",
        "configured": False,
        "model": "",
    }


def _normalize_subject(subject_slug: Optional[str]) -> str:
    subject=(subject_slug or "general").strip().lower()
    return subject if subject in SUBJECTS else "general"


def _build_subject_context(subject_slug: str) -> dict:
    subject=_normalize_subject(subject_slug)
    return {
        "current_subject_slug":subject,
        "current_subject":SUBJECTS[subject],
        "ai_status":_current_ai_status(),
        "subject_links":[
            {"slug":slug,**config} for slug,config in SUBJECTS.items()
        ],
        "announcements":SUBJECT_ANNOUNCEMENTS.get(subject,[]),
        "notes":TeacherNote.objects.filter(subject=subject)[:8],
        "recordings":ClassRecording.objects.filter(subject=subject)[:8],
        "tests":SubjectTest.objects.filter(subject=subject)[:8],
    }


def _subject_redirect(subject_slug: str):
    subject=_normalize_subject(subject_slug)
    if subject=="general":
        return redirect("home")
    return redirect("subject_page",subject_slug=subject)


def _groq_response(prompt,subject_slug):
    api_key=(settings.GROQ_API_KEY or "").strip()
    if not api_key:
        raise ValueError("Groq API key is not configured.")

    client=Groq(api_key=api_key)

    subject_title=SUBJECTS[_normalize_subject(subject_slug)]["title"]

    chat=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role":"system",
                "content":f"You are a classroom assistant for the subject '{subject_title}'. Answer clearly and concisely for a student or teacher."
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return chat.choices[0].message.content.strip()


def _chatbot_response(prompt,subject):
    if (settings.GROQ_API_KEY or "").strip():
        return _groq_response(prompt,subject),"groq"
    raise ValueError("Groq API key is not configured.")


@ensure_csrf_cookie
@xframe_options_exempt
def home(request):
    return render(request,"index.html",_build_subject_context("general"))


@ensure_csrf_cookie
@xframe_options_exempt
def subject_page(request,subject_slug):
    subject=_normalize_subject(subject_slug)
    if subject=="general":
        raise Http404("General subject page does not use this route.")
    return render(request,"index.html",_build_subject_context(subject))


@require_POST
def upload_note(request):
    subject=_normalize_subject(request.POST.get("subject"))
    title=(request.POST.get("title") or "").strip()
    description=(request.POST.get("description") or "").strip()
    uploaded_by=(request.POST.get("uploaded_by") or "Teacher").strip() or "Teacher"
    attachment=request.FILES.get("attachment")

    if not title or not attachment:
        return _subject_redirect(subject)

    TeacherNote.objects.create(
        subject=subject,
        title=title,
        description=description,
        uploaded_by=uploaded_by,
        attachment=attachment,
    )
    return _subject_redirect(subject)


@require_POST
def upload_test(request):
    subject=_normalize_subject(request.POST.get("subject"))
    title=(request.POST.get("title") or "").strip()
    description=(request.POST.get("description") or "").strip()
    uploaded_by=(request.POST.get("uploaded_by") or "Teacher").strip() or "Teacher"
    attachment=request.FILES.get("attachment")

    if not title or not attachment:
        return _subject_redirect(subject)

    SubjectTest.objects.create(
        subject=subject,
        title=title,
        description=description,
        uploaded_by=uploaded_by,
        attachment=attachment,
    )
    return _subject_redirect(subject)


@require_POST
def upload_recording(request):
    subject=_normalize_subject(request.POST.get("subject"))
    video=request.FILES.get("video")
    recorded_by=(request.POST.get("recorded_by") or "Teacher").strip() or "Teacher"
    title=(request.POST.get("title") or "").strip()

    if not video:
        return JsonResponse({"error":"Missing video file."},status=400)

    if not title:
        title="Class Recording"

    recording=ClassRecording.objects.create(
        subject=subject,
        title=title,
        recorded_by=recorded_by,
        video=video,
    )

    return JsonResponse({
        "message":"Recording uploaded successfully.",
        "recording":{
            "id":recording.id,
            "title":recording.title,
            "recorded_by":recording.recorded_by,
            "video_url":recording.video.url,
        }
    },status=201)


@require_POST
def delete_recording(request,recording_id):
    recording=get_object_or_404(ClassRecording,pk=recording_id)
    recording.video.delete(save=False)
    recording.delete()
    return JsonResponse({"message":"Recording deleted successfully."},status=200)


def chatbot(request):
    if request.method!="POST":
        return HttpResponseNotAllowed(["POST"])

    user_input=(request.POST.get("message") or "").strip()
    subject=_normalize_subject(request.POST.get("subject"))

    if not user_input:
        return JsonResponse({"error":"Missing 'message' field."},status=400)

    try:
        response_text,provider=_chatbot_response(user_input,subject)
    except Exception as e:
        return JsonResponse({"error":str(e)},status=502)

    return JsonResponse({"response":response_text,"provider":provider},status=200)
