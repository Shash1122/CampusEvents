#events/views.py
from django.db.models import Count, Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # swap to IsAuthenticated if you enable JWT
from rest_framework.response import Response
from rest_framework import status

from .models import College, Student, Event, Registration, Attendance, Feedback
from .serializers import (
    RegistrationCreateSerializer, CheckinSerializer, FeedbackSerializer,
    EventReportSerializer, StudentParticipationSerializer
)

@api_view(["POST"])
@permission_classes([AllowAny])
def register_student(request):
    """
    POST { student_id, event_id } -> create Registration (idempotent)
    """
    ser = RegistrationCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    reg = ser.save()
    return Response({"registration_id": str(reg.id)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def checkin(request):
    """
    POST { registration_id } OR { student_id, event_id } -> mark Attendance.present=True
    """
    ser = CheckinSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    att = ser.save()
    return Response({"attendance_id": str(att.id), "present": att.present}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_feedback(request):
    """
    POST { registration_id | (student_id,event_id), rating (1-5), comment? }
    """
    ser = FeedbackSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    fb = ser.save()
    return Response({"feedback_id": str(fb.id), "rating": fb.rating}, status=status.HTTP_201_CREATED)


# ---------- Reports ----------

@api_view(["GET"])
@permission_classes([AllowAny])
def event_popularity_report(request):
    """
    GET /api/reports/popularity?college=<college_id>
    Returns events sorted by registrations desc.
    """
    college_id = request.GET.get("college")
    qs = Event.objects.all()
    if college_id:
        qs = qs.filter(college_id=college_id)

    qs = qs.annotate(
        registrations=Count("registrations", distinct=True),
        attendance=Count("registrations__attendance", distinct=True),
        avg_rating=Avg("registrations__feedback__rating"),
    )

    # compute attendance_pct safely
    data = []
    for e in qs.order_by("-registrations"):
        total = e.registrations or 0
        present = e.attendance or 0
        pct = (present * 100.0 / total) if total else 0.0
        data.append({
            "id": e.id, "title": e.title, "code": e.code,
            "registrations": total, "attendance": present,
            "attendance_pct": round(pct, 2),
            "avg_rating": round(e.avg_rating or 0.0, 2),
        })
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def student_participation_report(request):
    """
    GET /api/reports/student-participation?college=<college_id>
    -> list students with count of attended events
    Or GET /api/reports/student-participation?student=<student_id> -> one student
    """
    college_id = request.GET.get("college")
    student_id = request.GET.get("student")

    qs = Student.objects.all()
    if student_id:
        qs = qs.filter(id=student_id)
    if college_id:
        qs = qs.filter(college_id=college_id)

    qs = qs.annotate(
        attended_events=Count(
            "registrations__attendance",
            filter=Q(registrations__attendance__present=True),
            distinct=True,
        )
    ).order_by("-attended_events")

    data = StudentParticipationSerializer(qs, many=True).data
    return Response(data)
